from utils.search import FootAPISearch
import regex as re
import requests


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

    def _clean_data(self, data: str):
        if "0%" in data:
            return 0
        if "%" in data:
            seq = re.compile(r"(?<!\.)(?!0+(?:\.0+)?%)(?:\d|[1-9]\d|100)(?:(?<!100)\.\d+)?%")
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

        if not response["homeScore"] or not response["awayScore"]:
            return ()

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
            match_data.append(int(shot_stats["Shots on target"]["home"])) #home shots on target
            match_data.append(int(shot_stats["Shots on target"]["away"])) #away shots on target
            if "Total shots" in shot_stats:
                match_data.append(int(shot_stats['Total shots']["home"])) #home tot shots
                match_data.append(int(shot_stats['Total shots']["away"])) #away tot shots
            else:
                home_shots = [shot_stats[grp]["home"] for grp in ("Shots on target", "Shots off target", "Blocked shots") if grp in shot_stats]
                away_shots = [shot_stats[grp]["away"] for grp in ("Shots on target", "Shots off target", "Blocked shots") if grp in shot_stats]
                match_data.append(int(sum(home_shots))) #home tot shots
                match_data.append(int(sum(away_shots))) #away tot shots
        
        shots_extra_headers = ("Big chances", "Shots inside box", "Goalkeeper saves")
        shots_extra_stats = {row["name"]:row for row in response[stat_groups["Shots extra"]]["statisticsItems"] if row["name"] in shots_extra_headers}
        if len(shots_extra_stats) == 3:
            for row in shots_extra_stats.values():
                match_data.append(int(row["home"])) # home - big chances, shots in box, saves
                match_data.append(int(row["away"])) # away - big chances, shots in box, saves
        
        tvdata_headers = ("Corner kicks", "Offsides", "Fouls", "Yellow cards", "Red cards")
        tvdata_stats = {row["name"]:row for row in response[stat_groups["TVData"]]["statisticsItems"] if row["name"] in tvdata_headers}
        for grp in tvdata_headers:
            if grp in tvdata_stats:
                match_data.append(int(tvdata_stats[grp]["home"])) # home - corners, offsides, fouls, yellows, reds
                match_data.append(int(tvdata_stats[grp]["away"])) # away - corners, offsides, fouls, yellows, reds
            else:
                match_data.append(0)
                match_data.append(0)

        passes_headers = ("Passes", "Accurate passes", "Long balls", "Crosses")
        passes_stats = {row["name"]:row for row in response[stat_groups["Passes"]]["statisticsItems"] if row["name"] in passes_headers}
        if len(passes_stats) == 4:
            for row in passes_stats.values():
                match_data.append(self._clean_data(row["home"])) # home - passes, accurate, long balls, crosses
                match_data.append(self._clean_data(row["away"])) # away - passes, accurate, long balls, crosses
        
        for row in response[stat_groups["Duels"]]["statisticsItems"]:
            if row["name"] == "Dribbles":
                match_data.append(self._clean_data(row["home"]))
                match_data.append(self._clean_data(row["away"]))

        def_headers = ("Tackles", "Interceptions", "Clearances")
        def_stats = {row["name"]:row for row in response[stat_groups["Defending"]]["statisticsItems"] if row["name"] in def_headers}
        for grp in def_headers:
            if grp in def_stats:
                match_data.append(self._clean_data(def_stats[grp]["home"])) # home - tackles, intercepts, clears
                match_data.append(self._clean_data(def_stats[grp]["away"])) # away - tackles, intercepts, clears
            else:
                match_data.append(0)
                match_data.append(0)

        return tuple(match_data)

