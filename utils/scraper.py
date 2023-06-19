from api_search import FootAPISearch
import sqlite3, requests


class Parser:
    pass

class Scraper:
    def __init__(self):
        self._footapi = FootAPISearch()
    
    def get_premier_league_ids(self): #gets the league ids for all the divisions
        pass

    def get_league_matches(self, league_id):
        pass

    def get_match_data(self, match_id):
        pass

class Stats(FootAPIParser):
    def get_country_list(self):
        country_list = []
        request_url = "https://footapi7.p.rapidapi.com/api/tournament/categories"
        response = requests.get(request_url, headers=self._headers).json()
        with open("static/country_list.txt", "a") as f:
            for row in response["categories"]:
                f.write(row["slug"], "\n")

    def get_league_list(country_id):
        pass

    def get_team_list(league_id):
        pass
Scraper = Scraper()
Scraper.get_country_list()