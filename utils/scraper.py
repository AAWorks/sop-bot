from api_search import FootAPISearch
import sqlite3, requests


class Parser:
    pass

class Scraper:
    def __init__(self):
        self._footapi = FootAPISearch()
    
    def get_league_ids(self): #gets the league ids for all the mls divisions
        pass

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
        pass


par = Scraper()
ids = par.get_league_match_ids(47955)
print(ids)
