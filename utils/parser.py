from api_search import FootAPISearch
import regex as re
import sqlite3, requests

class Parser:
    def __init__(self):
        self._db = sqlite3.connect('data/soccer_data.db')
        self._create_table()

    def _create_table(self):
        cursor = self._db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mls
                (match_id INTEGER,
                epoch_date INTEGER,
                home_team TEXT,
                home_score INTEGER,
                away_team TEXT,
                away_score INTEGER,
                home_possession INTEGER,
                away_possession INTEGER,
                home_totshots INTEGER,
                away_totshots INTEGER,
                home_shotsontarget INTEGER,
                away_shotsontarget INTEGER,
                home_shotsofftarget INTEGER,
                away_shotsofftarget INTEGER,
                home_blockedshots INTEGER,
                away_blockedshots INTEGER,
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
                home_bigchances INTEGER,
                away_bigchances INTEGER,
                home_bigchancesmissed INTEGER,
                away_bigchancesmissed INTEGER,
                home_hitwoodwork INTEGER,
                away_hitwoodwork INTEGER,
                home_counterattacks INTEGER,
                away_counterattacks INTEGER,
                home_counterattackshotsmissed INTEGER,
                away_counterattackshotsmissed INTEGER,
                home_shotsinsidebox INTEGER,
                away_shotsinsidebox INTEGER,
                home_shotsoutsidebox INTEGER,
                away_shotsoutsidebox INTEGER,
                home_goalkeepersaves INTEGER,
                away_goalkeepersaves INTEGER,
                home_goalsprevented FLOAT,
                away_goalsprevented FLOAT,
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
                home_possessionlost INTEGER,
                away_possessionlost INTEGER,
                home_duelswon INTEGER,
                away_duelswon INTEGER,
                home_aerialswon INTEGER,
                away_aerialswon INTEGER,
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

    def close_db(self):
        self._db.close()

    def _add_row(self, values):
        cursor = self._db.cursor()
        cursor.execute("""INSERT INTO mls (
            match_id, 
            epoch_date, 
            home_team, 
            home_score, 
            away_team, 
            away_score, 
            home_possession, 
            away_possession, 
            home_totshots, 
            away_totshots, 
            home_shotsontarget, 
            away_shotsontarget, 
            home_shotsofftarget, 
            away_shotsofftarget, 
            home_blockedshots, 
            away_blockedshots, 
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
            home_bigchancesmissed, 
            away_bigchancesmissed, 
            home_hitwoodwork, 
            away_hitwoodwork, 
            home_counterattacks, 
            away_counterattacks, 
            home_counterattackshotsmissed, 
            away_counterattackshotsmissed, 
            home_shotsinsidebox, 
            away_shotsinsidebox, 
            home_shotsoutsidebox, 
            away_shotsoutsidebox, 
            home_goalkeepersaves, 
            away_goalkeepersaves, 
            home_goalsprevented, 
            away_goalsprevented, 
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
            home_possessionlost, 
            away_possessionlost, 
            home_duelswon, 
            away_duelswon, 
            home_aerialswon, 
            away_aerialswon, 
            home_tackles, 
            away_tackles, 
            home_interceptions, 
            away_interceptions, 
            home_clearances, 
            away_clearances, 
            home_formation, 
            away_formation) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", values)
        self._db.commit()
    
    def add_match_data(self, id_file, scraper):
        with open(id_file, "r") as f:
            ids = f.readline().split(",")

        for id in ids:
            self._add_row(scraper.get_match_data(int(id)))
    
    def peek(self):
        cursor = self._db.cursor()
        cursor.execute("SELECT * FROM mls")
        data = cursor.fetchall()
        return data