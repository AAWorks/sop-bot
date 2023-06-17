# helper script to make footapi more readable
import requests


HEADERS = {
    "X-RapidAPI-Key": "0b59cdea82msh8c62aa043ee53dcp1d2033jsn82befb9a89bc",
    "X-RapidAPI-Host": "footapi7.p.rapidapi.com"
}


def clean_input(inputstr):
    return inputstr.lower().strip().replace(" ", "-")

def general_request(details):
    #stuff to get api data
    details = map(clean_input, details)
    country, league, year = details
    category_id = get_category_id(country)
    #...
    #return (category_id, tournament_id, season_id)
    return details

def get_category_id(country): #category = country (i.e. US)
    request_url = f"https://footapi7.p.rapidapi.com/api/tournament/categories"
    response = requests.get(request_url, headers=HEADERS).json()
    for row in response["categories"]:
        if row["slug"] == country:
            return row["id"]
    return None

def get_tournament_id(category_id, league): #tournament = league (i.e. MLS)
    pass

def get_season_id(tournament_id, year): #season = season (i.e. MLS 2023 season)
    pass

if __name__ == "__main__":
    details = input("Details: ").replace(" ", "").split(",")
    ids = general_request(details)
    print(ids)