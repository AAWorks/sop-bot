from search import FootAPISearch
import regex as re
import sqlite3, requests


class Scraper:
    def __init__(self):
        self._footapi = FootAPISearch()
        self._ids = []

    def _get_page_match_ids(self, league_id, season_id, page_num):
        url = f"https://footapi7.p.rapidapi.com/api/tournament/{league_id}/season/{season_id}/matches/last/{page_num}"
        response = requests.get(url, headers=self._footapi._headers).json()
        for row in response["events"]:
            self._ids.append(str(row["id"]))
        
        if response["hasNextPage"]:
            return page_num + 1
        return -1

    def _get_season_match_ids(self, league_id, season_id):
        next_page = 0
        
        while next_page != -1:
            next_page = self._get_page_match_ids(league_id, season_id, next_page)

    def get_league_match_ids(self, league_id, num_seasons=10): #get all the mls leagues match ids
        self._ids = []
        url = f"https://footapi7.p.rapidapi.com/api/tournament/{league_id}/seasons"
        response = requests.get(url, headers=self._footapi._headers).json()["seasons"]

        for i in range(num_seasons):
            season_id = response[i]["id"]
            self._get_season_match_ids(league_id, season_id)
        
        with open("data/mls_match_ids.txt", "w") as f:
            f.write(",".join(self._ids))

    def _clean_data(self, data):
        if "%" in data:
            seq = re.compile(r"\b(?<!\.)(?!0+(?:\.0+)?%)(?:\d|[1-9]\d|100)(?:(?<!100)\.\d+)?%")
            match = seq.search(data)
            data = match.group()[:-1]
        return int(data)
    
    def _get_data_sects(self, response):
        all_stat_groups = {
            "Possession": -1,
            "Shots": -1,
            "TVData": -1,
            "Shots extra": -1,
            "Passes": -1,
            "Duels": -1,
            "Defending": -1
        }
        i = 0

        for sect in response:
            stat_group = sect["groupName"]
            if stat_group in all_stat_groups:
                all_stat_groups[stat_group] = i
            i += 1
        
        return all_stat_groups

    def get_match_data(self, match_id): #get all the relevant stats from a match and put them into a list
        match_data = []
        url = f"https://footapi7.p.rapidapi.com/api/match/{match_id}"
        response = requests.get(url, headers=self._footapi._headers).json()["event"]
        match_data.append(match_id) #matchid
        match_data.append(int(response["startTimestamp"])) #timestamp
        match_data.append(response["homeTeam"]["name"]) #homename
        match_data.append(int(response["homeScore"]["current"])) #homescore
        match_data.append(response["awayTeam"]["name"]) #awayname
        match_data.append(int(response["awayScore"]["current"])) #awayscore

        url = f"https://footapi7.p.rapidapi.com/api/match/{match_id}/statistics"
        response = requests.get(url, headers=self._footapi._headers).json()["statistics"][0]["groups"]

        stat_groups = self._get_data_sects(response)

        if -1 in stat_groups.values():
            return ()

        match_data.append(int(response[stat_groups["Possession"]]["statisticsItems"][0]["home"].replace("%",""))) #homepossession
        match_data.append(int(response[stat_groups["Possession"]]["statisticsItems"][0]["away"].replace("%",""))) #awaypossession

        shot_stats = {row["name"]:row for row in response[stat_groups["Shots"]]["statisticsItems"]}
        if "Shots on target" in shot_stats:
            match_data.append(int(row["home"])) #home shots on target
            match_data.append(int(row["away"])) #away shots on target
            if "Total shots" in shot_stats:
                match_data.append(int(shot_stats['Total shots']["home"])) #home tot shots
                match_data.append(int(shot_stats['Total shots']["away"])) #away tot shots
            else:
                home_shots = [shot_stats[grp]["home"] for grp in ("Shots on target", "Shots off target", "Blocked shots") if grp in shot_stats]
                away_shots = [shot_stats[grp]["away"] for grp in ("Shots on target", "Shots off target", "Blocked shots") if grp in shot_stats]
                match_data.append(int(sum(home_shots))) #home tot shots
                match_data.append(int(sum(away_shots))) #away tot shots

        try:
            match_data.append(int(response[stat_groups["TVData"]]["statisticsItems"][4]["home"]))
            match_data.append(int(response[stat_groups["TVData"]]["statisticsItems"][4]["away"]))
        except:
            match_data.append(0)
            match_data.append(0)
        
        shots_extra_stats = {row["name"]:row for row in response[stat_groups["Shots extra"]]["statisticsItems"] if row["name"] in ("Big chances", "Shots inside box", "Goalkeeper saves")}
        
        if len(shots_extra_stats) >= 2:
            for grp in shots_extra_stats:
                match_data.append(int(shots_extra_stats[grp]["home"]))
                match_data.append(int(shots_extra_stats[grp]["away"]))
        
        for typ in ("home", "away"):
            for i in (stat_groups["TVData"], stat_groups["Passes"], stat_groups["Duels"]):
                for j in range(4):
                    try:
                        match_data.append(self._clean_data(response[i]["statisticsItems"][j][typ]))
                    except:
                        match_data.append(0)
        
        for row in response[stat_groups["Defending"]]["statisticsItems"]:
            match_data.append(int(row["home"]))
            match_data.append(int(row["away"]))

        url = f"https://footapi7.p.rapidapi.com/api/match/{match_id}/lineups"
        response = requests.get(url, headers=self._footapi._headers).json()
        match_data.append(response["home"]["formation"])
        match_data.append(response["away"]["formation"])

        return tuple(match_data)
