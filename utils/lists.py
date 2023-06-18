from api_parser import FootAPIParser
import requests

class Scraper(FootAPIParser):
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