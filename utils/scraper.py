from api_search import FootAPISearch
import regex as re
import sqlite3, requests


class Scraper:
    def __init__(self):
        self._footapi = FootAPISearch()

    def _get_page_match_ids(self, league_id, season_id, ids, page_num):
        url = f"https://footapi7.p.rapidapi.com/api/tournament/{league_id}/season/{season_id}/matches/last/{page_num}"
        response = requests.get(url, headers=self._footapi._headers).json()
        for row in response["events"]:
            ids.append(str(row["id"]))
        
        if response["hasNextPage"]:
            return page_num + 1
        return -1

    def _get_season_match_ids(self, league_id, season_id, ids):
        next_page = 0
        
        while next_page != -1:
            next_page = self._get_page_match_ids(league_id, season_id, ids, next_page)

    def get_league_match_ids(self, league_id, num_seasons=10): #get all the mls leagues match ids
        ids = []
        url = f"https://footapi7.p.rapidapi.com/api/tournament/{league_id}/seasons"
        response = requests.get(url, headers=self._footapi._headers).json()["seasons"]

        for i in range(num_seasons):
            season_id = response[i]["id"]
            self._get_season_match_ids(league_id, season_id, ids)
        
        with open("data/mls_matches.txt", "w") as f:
            f.write(",".join(ids))

    def _clean_data(self, data):
        if "%" in data:
            seq = re.compile(r"\b(?<!\.)(?!0+(?:\.0+)?%)(?:\d|[1-9]\d|100)(?:(?<!100)\.\d+)?%")
            match = seq.search(data)
            data = match.group()[:-1]
        return int(data)

    def get_match_data(self, match_id): #get all the relevant stats from a match and put them into a list
        match_data = []
        url = f"https://footapi7.p.rapidapi.com/api/match/{match_id}"
        response = requests.get(url, headers=self._footapi._headers).json()["event"]
        match_data.append(match_id)
        match_data.append(int(response["startTimestamp"]))
        match_data.append(response["homeTeam"]["name"])
        match_data.append(int(response["homeScore"]["current"]))
        match_data.append(response["awayTeam"]["name"])
        match_data.append(int(response["awayScore"]["current"]))
        match_data.append(((int(response["referee"]["redCards"]) * 2) + int(response["referee"]["yellowCards"]) + int(response["referee"]["yellowRedCards"])) / (int(response["referee"]["games"])))
        url = f"https://footapi7.p.rapidapi.com/api/match/{match_id}/statistics"
        response = requests.get(url, headers=self._footapi._headers).json()["statistics"][0]["groups"]
        match_data.append(int(response[1]["statisticsItems"][0]["home"].replace("%","")))
        match_data.append(int(response[1]["statisticsItems"][0]["away"].replace("%","")))
        for row in response[2]["statisticsItems"]:
            match_data.append(int(row["home"]))
            match_data.append(int(row["away"]))
        try:
            match_data.append(int(response[3]["statisticsItems"][4]["home"]))
            match_data.append(int(response[3]["statisticsItems"][4]["away"]))
        except:
            match_data.append(0)
            match_data.append(0)
        for row in response[4]["statisticsItems"]:
            if "." in row["home"]:
                match_data.append(float(row["home"]))
                match_data.append(float(row["away"]))
            else:
                match_data.append(row["home"])
                match_data.append(row["away"])
        
        for typ in ("home", "away"):
            for i in (3, 5, 6):
                for j in range(4):
                    match_data.append(self._clean_data(response[i]["statisticsItems"][j][typ]))

        for row in response[7]["statisticsItems"]:
            match_data.append(int(row["home"]))
            match_data.append(int(row["away"]))

        url = f"https://footapi7.p.rapidapi.com/api/match/{match_id}/lineups"
        response = requests.get(url, headers=self._footapi._headers).json()
        match_data.append(response["home"]["formation"])
        match_data.append(response["away"]["formation"])

        return tuple(match_data)
