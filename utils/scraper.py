from api_search import FootAPISearch
import sqlite3, requests


class Parser:
    pass

class Scraper:
    def __init__(self):
        self._footapi = FootAPISearch()
    
    def get_mls_league_ids(self): #gets the league ids for all the mls divisions
        pass

    def get_mls_league_match_ids(self): #get all the mls leagues match ids
        pass

    def get_league_matches(self, league_id): #skip this for now
        pass

    def get_match_data(self, match_id): #get all the relevant stats from a match and put them into a list
        pass

