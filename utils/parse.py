import utils.scrape
import sqlite3

class Dataset:
    def __init__(self, league):
        self._db = sqlite3.connect('data/soccer_data.db')
        self._league_name = league
        self._create_table(league)
    
    @property
    def table_headers(self):
        cursor = self._db.cursor()
        cursor.execute(f"PRAGMA table_info({self._league_name});")
        data = cursor.fetchall()
        return data

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
                away_clearances INTEGER,
                home_formation TEXT,
                away_formation TEXT)
        ''')
        # The prevented goals stat is calculated by subtracting the number of goals a keeper has conceded from the number of goals a keeper would be expected to concede based on the quality of shots he faced.
        self._db.commit()

    def _add_row(self, values):
        if len(values) != 46:
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
            away_clearances, 
            home_formation, 
            away_formation) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", values)
        self._db.commit()
    
    def _add_match_data(self, id_file, scraper, chunk_size, current_chunk):
        with open(id_file, "r") as f:
            ids = f.readline().split(",")
        
        filelength = len(ids)
        n_chunks = (filelength // chunk_size) + 1
        starting_id = current_chunk * n_chunks
        ending_id = starting_id + chunk_size
        ids = ids[starting_id : min(ending_id, filelength)]
        
        cursor = self._db.cursor()

        for id in ids:
            cursor.execute(f"SELECT * FROM {self._league_name} WHERE match_id = {id}")
            existing_match = cursor.fetchall()
            if not existing_match:
                self._add_row(scraper.get_match_data(int(id)))

    def pull_league_data(self, chunk_size, curr):
        self._create_table(self._league_name)
        scr = utils.scrape.Scraper()
        self.add_match_data("data/mls_match_ids.txt", scr, chunk_size, curr, self._league_name)

    def all_but_last_n_matches(self, agg_depth: int) -> list: # all matches but the last 10
        cursor = self._db.cursor()
        cursor.execute(f"SELECT * from {self._league_name} ORDER BY epoch_date")
        data = cursor.fetchall()
        return data[:-agg_depth]
    
    def _get_last_n_matches_of_team(self, team_name, rowid, agg_depth):
        cursor = self._db.cursor()

        cursor.execute(f"SELECT rowid, * from {self._league_name} WHERE home_team = {team_name} OR away_team = {team_name}")
        team_matches = cursor.fetchall()

        rowid = int(rowid)
        matches = []
        for match in team_matches:
            if int(match[0]) in range(rowid + 1, rowid + agg_depth):
                matches.append(match)
        
        return matches
    
    def _sum_column(self, to_sum, teamname, key):
        agg = 0
        column = key.split("_")[-1]

        for match in to_sum:
            prefix = "home_" if match[2] == teamname else "away_" # 2: home, 4: away
            agg += match[prefix + column]
        
        return agg

    def _aggregate_match_data(self, match: dict, agg_depth: int):
        rowid = match[0]

        home_matches = self._get_last_n_matches_of_team(self, self._leauge_name, match["home_team"], rowid, agg_depth)
        away_matches = self._get_last_n_matches_of_team(self, self._league_name, match["away_team"], rowid, agg_depth)
        
        for col in match:
            if str(match[col]).isnumeric():
                if "home" in col:
                    match[col] += self._sum_column(home_matches, match["home"], col)
                elif "away" in col:
                    match[col] += self._sum_column(away_matches, match["away"], col)
        
        return match
    
    def aggregate_data(self, aggregate_depth):
        aggregated_data, headers = [], self.table_headers()
        for match in self.all_but_last_n_matches(aggregate_depth):
            match_dict = dict(zip(headers, match))
            aggregate = self._aggregate_match_data(match_dict, aggregate_depth)
            # ^INSIDE -> aggregate_team_stats(team, )
            aggregated_data.append(aggregate)
        
        return aggregated_data

    def normalize(self):
        return self.aggregate_data(10)

    def peek(self):
        cursor = self._db.cursor()
        cursor.execute(f"SELECT * FROM {self._league_name}")
        data = cursor.fetchall()
        return data
    
    def close_db(self):
        self._db.close()

