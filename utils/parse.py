import utils.scrape as scrape
import sqlite3
import pandas as pd
from sklearn.utils import shuffle
import time

class Dataset:
    def __init__(self, league):
        self._db = sqlite3.connect('data/soccer_data.db')
        self._league_name = league
        self._create_table()
        self._scr = scrape.Scraper()
    
    @property
    def league_name(self): return self._league_name
    
    @property
    def table_headers(self):
        cursor = self._db.cursor()
        cursor.execute(f"PRAGMA table_info({self._league_name});")
        headers = cursor.fetchall()
        res = []
        for header in headers:
            res.append(header[1])
        return res
    
    @property
    def team_names(self) -> tuple:
        cursor = self._db.cursor()
        cursor.execute("SELECT DISTINCT home_team FROM laligapremier ORDER BY home_team ASC;")
        names = cursor.fetchall()
        return tuple([name[0] for name in names])
    
    def _create_joint_table(self):
        cursor = self._db.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS laligapremier AS SELECT * FROM laliga")
        cursor.execute(f"INSERT INTO laligapremier SELECT * FROM premier_league EXCEPT SELECT * FROM laliga;")
        self._db.commit()

    def _create_table(self):
        cursor = self._db.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self._league_name}
                (match_id INTEGER,
                epoch_date INTEGER,
                home_team TEXT,
                home_score INTEGER,
                away_team TEXT,
                away_score INTEGER,
                home_possession INTEGER,
                away_possession INTEGER,
                home_shotsontarget INTEGER,
                away_shotsontarget INTEGER,
                home_totshots INTEGER,
                away_totshots INTEGER,
                home_bigchances INTEGER,
                away_bigchances INTEGER,
                home_shotsinsidebox INTEGER,
                away_shotsinsidebox INTEGER,
                home_goalkeepersaves INTEGER,
                away_goalkeepersaves INTEGER,
                home_cornerkicks INTEGER,
                away_cornerkicks INTEGER,
                home_offsides INTEGER,
                away_offsides INTEGER,
                home_fouls INTEGER,
                away_fouls INTEGER,
                home_yellowcards INTEGER,
                away_yellowcards INTEGER,
                home_redcards INTEGER,
                away_redcards INTEGER,
                home_passes INTEGER,
                away_passes INTEGER,
                home_accuratepasses INTEGER,
                away_accuratepasses INTEGER,
                home_longballs INTEGER,
                away_longballs INTEGER,
                home_crosses INTEGER,
                away_crosses INTEGER,
                home_dribbles INTEGER,
                away_dribbles INTEGER,
                home_tackles INTEGER,
                away_tackles INTEGER,
                home_interceptions INTEGER,
                away_interceptions INTEGER,
                home_clearances INTEGER,
                away_clearances INTEGER)
        ''')
        # The prevented goals stat is calculated by subtracting the number of goals a keeper has conceded from the number of goals a keeper would be expected to concede based on the quality of shots he faced.
        self._db.commit()

    def _add_row(self, values):
        if len(values) != 44:
            return

        cursor = self._db.cursor()

        cursor.execute(f"""INSERT INTO {self._league_name} (
            match_id, 
            epoch_date, 
            home_team, 
            home_score, 
            away_team, 
            away_score, 
            home_possession, 
            away_possession, 
            home_shotsontarget, 
            away_shotsontarget, 
            home_totshots, 
            away_totshots, 
            home_cornerkicks, 
            away_cornerkicks, 
            home_offsides, 
            away_offsides, 
            home_fouls, 
            away_fouls, 
            home_yellowcards, 
            away_yellowcards, 
            home_redcards, 
            away_redcards, 
            home_bigchances, 
            away_bigchances,
            home_shotsinsidebox, 
            away_shotsinsidebox, 
            home_goalkeepersaves, 
            away_goalkeepersaves, 
            home_passes, 
            away_passes, 
            home_accuratepasses, 
            away_accuratepasses, 
            home_longballs, 
            away_longballs, 
            home_crosses, 
            away_crosses, 
            home_dribbles, 
            away_dribbles,
            home_tackles, 
            away_tackles, 
            home_interceptions, 
            away_interceptions, 
            home_clearances, 
            away_clearances) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", values)
        self._db.commit()
    
    def _add_match_data(self, id_file, scraper, chunk_size, current_chunk):
        with open(id_file, "r") as f:
            ids = f.readline().split(",")
        
        filelength = len(ids)
        starting_id = current_chunk * chunk_size
        ending_id = starting_id + chunk_size
        ids = ids[starting_id : min(ending_id, filelength)]

        #raise Exception(f"filelength: {filelength} | n_chunks: {n_chunks} | starting_id: {starting_id} | ending_id: {ending_id} | ids: {ids}")
        
        cursor = self._db.cursor()

        for id in ids:
            cursor.execute(f"SELECT * FROM {self._league_name} WHERE match_id = {id}")
            existing_match = cursor.fetchall()
            if not existing_match:
                self._add_row(scraper.get_match_data(int(id)))

    def pull_league_data(self, chunk_size, curr):
        self._add_match_data("data/prem_match_ids.txt", self._scr, chunk_size, curr)
    
    def _parse_w_result(self, data):
        def get_result(home, away):
            if home > away: return "W"
            elif home < away: return "L"
            else: return "T"
        
        matches = []

        for row in data:
            match = dict(zip(["rowid"] + self.table_headers, row))
            match["result"] = get_result(int(match["home_score"]), int(match["away_score"]))
            matches.append(match)
        
        return matches

    def all_matches_w_results(self) -> list: # all matches in dict form
        cursor = self._db.cursor()
        cursor.execute(f"SELECT rowid, * from {self._league_name} ORDER BY epoch_date")
        data = cursor.fetchall()
        
        return self._parse_w_result(data)
    
    def _get_last_n_matches_of_team(self, team_name, epoch_date, agg_depth):
        cursor = self._db.cursor()
        epoch_date = int(epoch_date)

        cursor.execute(f"SELECT rowid, * from {self._league_name} WHERE home_team = '{team_name}' OR away_team = '{team_name}' AND epoch_date < {epoch_date} ORDER BY epoch_date")
        team_matches = cursor.fetchall()

        if len(team_matches) >= agg_depth:
            team_matches = team_matches[:agg_depth]
        else:
            return []
        
        return self._parse_w_result(team_matches)
    
    def _get_win_val(self, match, prefix):
        if prefix == "home":
            return 1 if match["result"] == "W" else 0
        return 1 if match["result"] == "L" else 0

    def _get_loss_val(self, match, prefix):
        if prefix == "home":
            return 1 if match["result"] == "L" else 0
        return 1 if match["result"] == "W" else 0
    
    def _sum_column(self, to_sum, teamname, key, mode=None):
        agg = 0
        column = key.split("_")[-1]

        for match in to_sum:
            prefix = "home" if match["home_team"] == teamname else "away" # 2: home, 4: away
            if key != "result":
                agg += match[f"{prefix}_{column}"]
            elif mode:
                if mode == "wins":
                    agg += self._get_win_val(match, prefix)
                elif mode == "losses":
                    agg += self._get_loss_val(match, prefix)
                else:
                    agg += 1 if match["result"] == "T" else 0
        
        return agg

    def _aggregate_match_data(self, match: dict, agg_depth: int):
        date = match["epoch_date"]
        home, away = match["home_team"], match["away_team"]

        home_matches = self._get_last_n_matches_of_team(home, date, agg_depth)
        away_matches = self._get_last_n_matches_of_team(away, date, agg_depth)

        if not home_matches or not away_matches:
            return []

        new_match = {}

        for col in match:
            # if col in ("match_id", "epoch_date"):
            #     new_match[col] = match[col]
            if str(match[col]).isnumeric() and not col in ("match_id", "epoch_date", "result"):
                if "home" in col:
                    new_match[col] = self._sum_column(home_matches, home, col)
                elif "away" in col:
                    new_match[col] = self._sum_column(away_matches, away, col)
            if col == "result":
                if match[col] != -1:
                    new_match[col] = {"W": 1, "L": 0, "T": 2}.get(match[col])
                for mode in ("wins", "ties","losses"):
                    new_match[f"home_{mode}"] = self._sum_column(home_matches, home, col, mode)
                    new_match[f"away_{mode}"] = self._sum_column(away_matches, away, col, mode)
        
        return new_match

    def _aggregate_potential_match_stats(self, home_team, away_team, agg_depth):
        match = dict(zip(self.table_headers, [0] * len(self.table_headers)))
        match["result"] = -1
        match["home_team"] = home_team
        match["away_team"] = away_team
        match["epoch_date"] = int(time.time())
        return self._aggregate_match_data(match, agg_depth)

    def aggregate_data(self, aggregate_depth, progress_bar=None):
        aggregated_data = []
        percent_complete = 0

        matches = self.all_matches_w_results()
        lenmatches = len(matches)
        inc = 1 / lenmatches

        for match in matches:
            aggregate = self._aggregate_match_data(match, aggregate_depth)
            if aggregate:
                aggregated_data.append(aggregate)
            if progress_bar:
                percent_complete = min(percent_complete + inc, 1.0)
                progress_bar.progress(percent_complete, text=f"Processing Match Data ({int(percent_complete * 100)}% Complete)")
        
        return aggregated_data
    
    def to_df(self, data):
        return pd.DataFrame.from_dict(data)

    def _normalize_column(self, series):
        return (series - series.min())/(series.max() - series.min())

    def normalize_aggregate(self, data=None, progress_bar=None):
        if not data:
            data = self.aggregate_data(10)
        
        df = pd.DataFrame.from_dict(data)
        cols = df.columns

        lencols, percent_complete = len(cols), 0
        inc = 1 / lencols

        for col in cols:
            if col != "result":
                df[col] = self._normalize_column(df[col])

            if progress_bar:
                percent_complete = min(percent_complete + inc, 1.0)
                progress_bar.progress(percent_complete, text=f"Normalizing Data ({int(percent_complete * 100)}% Complete)")

        if progress_bar:
            progress_bar.progress(1.0, text="Normalized Match Data")

        # df = df.drop("home_wins", axis=1).drop("away_wins", axis=1)
        # df["home_wins"] = df["result"]
        # df["away_wins"] = df["result"]

        # for i in range(100):
        #     df["away_wins" + str(i)] = df["result"]
        
        return df

    def _drop_columns(self, data, columns):
        columns = [f"home_{col}" for col in columns] + [f"away_{col}" for col in columns]

        data.drop(columns, axis=1, inplace=True)

        return data

    def potential_match_preprocessing(self, aggregated_data, home_team, away_team, agg_depth, columns_to_drop):
        agg_match = self._aggregate_potential_match_stats(home_team, away_team, agg_depth)
        to_norm = [agg_match] + aggregated_data
        normalized = self.normalize_aggregate(to_norm).head(1)
        return self._drop_columns(normalized, columns_to_drop)
    
    def _swap_home_away(self, records):
        new_records = pd.DataFrame()
        for column in records.columns:
            if column == "result": new_records[column] = [1 if res == 0 else 0 for res in records[column]]
            else:
                mode, column_type = tuple(column.split("_"))
                new_column = str("home_" if mode == "away" else "away_") + column_type

                new_records[new_column] = records[column]

        return new_records
    
    def dnn_preprocessing(self, records, columns_to_drop=None, include_ties=False):
        if columns_to_drop:
            records = self._drop_columns(records, columns_to_drop)

        # (wins, losses, ?ties)
        w, l, t = records.loc[records['result'] == 1], records.loc[records['result'] == 0], records.loc[records['result'] == 2]

        if not include_ties:
            # min_length = min([df.shape[0] for df in (w, l)])
            # w = w.head(min_length).reset_index(drop=True)
            # l = l.head(min_length).reset_index(drop=True)
            rev_w = self._swap_home_away(w)
            rev_l = self._swap_home_away(l)

            classes = (w, l, rev_w, rev_l)
        else:
            min_length = min(w.shape[0], (l.shape[0] + t.shape[0]))
            w = w.head(min_length).reset_index(drop=True)
            l_and_t = pd.concat([l, t]).sort_index(kind='merge')
            l_and_t = l_and_t.head(min_length).reset_index(drop=True)
            l_and_t.result.replace(2, 0, inplace=True)
            classes = (w, l_and_t)

        
        parsed_records = pd.concat(list(classes)).sort_index(kind='merge')
        # print(parsed_records)
        # parsed_records = parsed_records.drop("index", axis=1)

        parsed_records = shuffle(parsed_records)
        parsed_records.reset_index(inplace=True, drop=True)
        
        return parsed_records

    def peek(self):
        cursor = self._db.cursor()
        cursor.execute(f"SELECT * FROM {self._league_name}")
        data = cursor.fetchall()
        return [dict(zip(self.table_headers, row)) for row in data]
    
    def close_db(self):
        self._db.close()

def run_pull(league_name):
    data = Dataset(league_name)
    i = 0
    repeated_errors = 0
    while i < 11 and repeated_errors < 3:
        try:
            print(f"***DIAG: Pull {i} Initiated***")
            data.pull_league_data(300, i)
            print(f"***DIAG: Pull {i} Completed***")
            i += 1
            repeated_errors = 0
        except(KeyboardInterrupt):
            raise Exception("Process Terminated")
        except(Exception) as e:
            print(f"***DIAG: Threw Error - Pull #{i} Restarted***")
            print(f"***DIAG: Error Thrown - {e}***")
            repeated_errors += 1

    if repeated_errors == 3:
        print(f"***DIAG: Repeated Errors Exceeded Max Threshold***")

# data = Dataset("mls")
# data._create_joint_table()
