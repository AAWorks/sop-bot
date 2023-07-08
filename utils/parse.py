import scrape
import sqlite3

class Parser:
    def __init__(self):
        self._db = sqlite3.connect('data/soccer_data.db')

    def _create_table(self, league):
        cursor = self._db.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {league}
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

    def _add_row(self, values, league):
        if len(values) != 46:
            return

        cursor = self._db.cursor()
        cursor.execute(f"SELECT * FROM {league} WHERE match_id = {values[0]}")
        existing_match = cursor.fetchall()
        if existing_match:
            return

        cursor.execute(f"""INSERT INTO {league} (
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
    
    def _add_match_data(self, id_file, scraper, chunk_size, current_chunk, league):
        with open(id_file, "r") as f:
            ids = f.readline().split(",")
        
        filelength = len(ids)
        n_chunks = (filelength // chunk_size) + 1
        starting_id = current_chunk * n_chunks
        ending_id = starting_id + chunk_size
        ids = ids[starting_id : min(ending_id, filelength)]

        for id in ids:
            self._add_row(scraper.get_match_data(int(id)), league)

    def table_headers(self, tablename):
        cursor = self._db.cursor()
        cursor.execute(f"PRAGMA table_info({tablename});")
        data = cursor.fetchall()
        return data

    def pull_league_data(self, chunk_size, curr, league="mls"):
        self._create_table(league)
        scr = scrape.Scraper()
        self.add_match_data("data/mls_match_ids.txt", scr, chunk_size, curr, league)

    def all_but_last_n_matches(self, league_name: str, agg_depth: int) -> list: # all matches but the last 10
        cursor = self._db.cursor()
        cursor.execute(f"SELECT * from {league_name} ORDER BY epoch_date")
        data = cursor.fetchall()
        return data[:-agg_depth]

    def aggregate_match_data(self, match: tuple, agg_depth: int):
        pass

    def peek(self):
        cursor = self._db.cursor()
        cursor.execute("SELECT * FROM mls")
        data = cursor.fetchall()
        return data
    
    def close_db(self):
        self._db.close()

