from api_search import FootAPISearch
import sqlite3, requests


class Parser:
    def __init__(self):
        self._db = sqlite3.connect('data/soccer_data.db')
        self._create_table()

    def _create_table(self):
        cursor = self._db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mls(
                match_id INTEGER,
                epoch_date INTEGER,
                home_team TEXT,
                home_score INTEGER,
                away_team TEXT,
                away_score INTEGER,
                stadium_name TEXT,
                ref_toughness INTEGER
                
            )
        ''')
        self._db.commit()

    def _close_db(self):
        self._db.close()

    def _add_row(self, values):
        cursor = self._db.cursor()
        cursor.execute("INSERT INTO mls(match_id, epoch_date, home_team, home_score, away_team, away_score, stadium_name, ref_toughness ...) VALUES(?, ?, ?, ...)", *values)
        self._db.commit()

class Scraper:
    def __init__(self):
        self._footapi = FootAPISearch()

    def get_league_match_ids(self, league_id): #get all the mls leagues match ids
        ids = []
        url = f"https://footapi7.p.rapidapi.com/api/tournament/242/season/{league_id}/matches/last/0"
        response = requests.get(url, headers=self._footapi._headers).json()
        for row in response["events"]:
            ids.append(row["id"])
        return ids
        
    def get_league_matches(self, league_id): #skip this for now
        pass

    def get_match_data(self, match_id): #get all the relevant stats from a match and put them into a list
        match_data = []
        url = f"https://footapi7.p.rapidapi.com/api/match/{match_id}"
        response = requests.get(url, headers=self._footapi._headers).json()["event"]
        match_data.append(match_id)
        match_data.append(response["startTimestamp"])
        match_data.append(response["homeTeam"]["name"])
        match_data.append(response["homeScore"]["current"])
        match_data.append(response["awayTeam"]["name"])
        match_data.append(response["awayScore"]["current"])
        match_data.append(((int(response["referee"]["redCards"]) * 2) + int(response["referee"]["yellowCards"]) + int(response["referee"]["yellowRedCards"])) / (int(response["referee"]["games"])))
        url = f"https://footapi7.p.rapidapi.com/api/match/{match_id}/statistics"
        response = requests.get(url, headers=self._footapi._headers).json()["statistics"][0]["groups"]
        return match_data


par = Scraper()
home_stats, away_stats, match_stats = par.get_match_data(10408291)
print(f"{home_stats[0]}: {home_stats[1]}, {away_stats[0]}: {away_stats[1]} | Tournament: {match_stats[0]} | Stadium: {match_stats[1]} | Year: {match_stats[2]}")
