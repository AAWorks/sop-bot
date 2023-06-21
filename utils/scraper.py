from api_search import FootAPISearch
import sqlite3, requests


class Parser:
    pass

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
        home_team = []
        away_team = []
        match_data = []
        url = f"https://footapi7.p.rapidapi.com/api/match/{match_id}"
        response = requests.get(url, headers=self._footapi._headers).json()
        away_team.append(response["event"]["awayTeam"]["name"])
        away_team.append(response["event"]["awayScore"]["current"])
        home_team.append(response["event"]["homeTeam"]["name"])
        home_team.append(response["event"]["homeScore"]["current"])
        match_data.append(response["event"]["tournament"]["uniqueTournament"]["name"])
        match_data.append(response["event"]["venue"]["stadium"]["name"])
        match_data.append(response["event"]["season"]["year"])
        return home_team, away_team, match_data


par = Scraper()
home_stats, away_stats, match_stats = par.get_match_data(10952277)
print(f"{home_stats[0]}: {home_stats[1]}, {away_stats[0]}: {away_stats[1]} | Tournament: {match_stats[0]} | Venue: {match_stats[1]} | Year: {match_stats[2]}")
