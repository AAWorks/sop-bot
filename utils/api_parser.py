# helper script to make footapi more readable

def general_request(api_link, key, details):
    #stuff to get api data
    #country, league, year = details
    #category_id = get_category_id(country)
    #...
    #return (category_id, tournament_id, season_id)
    pass

def get_category_id(country): #category = country (i.e. US)
    pass

def get_tournament_id(category_id, league): #tournament = league (i.e. MLS)
    pass

def get_season_id(tournament_id, year): #season = season (i.e. MLS 2023 season)
    pass

if __name__ == "__main__":
    api = ""
    api_key = ""
    details = input().replace(" ", "").split(",")
    ids = general_request(api, api_key, details)
    print(ids)