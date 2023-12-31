# helper script to make footapi more readable
import requests


class FootAPISearch:
    _headers: dict

    def __init__(self):
        #with open("data/footapi_key.txt", "r") as keyfile:
        #    key = keyfile.readline().strip()

        self._headers = {
            "X-RapidAPI-Key": "41cb3ca06bmshe5c2195f078e2e2p1dc0acjsn58ee906dc98d",
            "X-RapidAPI-Host": "footapi7.p.rapidapi.com"
        }
    
    @property
    def headers(self):
        return self._headers

    def _clean_input(self, inputstr):
        return inputstr.lower().strip().replace(" ", "-")

    #def get_all_league_ids(self, inputstr):
    #    pass

    def get_category_id(self, country):
        #category = country (i.e. US)
        request_url = "https://footapi7.p.rapidapi.com/api/tournament/categories"
        response = requests.get(request_url, headers=self._headers).json()
        for row in response["categories"]:
            if row["slug"] == country:
                return row["id"]
        return None

    def get_tournament_id(self, category_id, league):
        #tournament = league (i.e. MLS)
        request_url = f"https://footapi7.p.rapidapi.com/api/tournament/all/\
            category/{category_id}"
        response = requests.get(request_url, headers=self._headers).json()
        for row in response["groups"][0]["uniqueTournaments"]:
            if row["slug"] == league:
                return row["id"]
        return None

    def get_season_id(self, tournament_id, year):
        #season = season (i.e. MLS 2023 season)
        request_url = f"https://footapi7.p.rapidapi.com/api/tournament/\
            {tournament_id}/seasons"
        response = requests.get(request_url, headers=self._headers).json()
        for row in response["seasons"]:
            if row["year"] == year:
                return row["id"]
        return None

    def general_request(self, details):
        details = tuple(map(self._clean_input, details))
        country, league, year = details

        category_id = self.get_category_id(country)
        tournament_id = self.get_tournament_id(category_id, league)
        season_id = self.get_season_id(tournament_id, year)

        return (category_id, tournament_id, season_id)

def test():
    details = ("usa", "mls", "2023")
    parser = FootAPISearch()
    ids = parser.general_request(details)
    print(f"Country: {ids[0]}, League: {ids[1]}, Season: {ids[2]}")
