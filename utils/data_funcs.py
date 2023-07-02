import scraper, parser

def count_file_data(filename):
    with open(filename, "r") as f:
        print(len(f.readline().split(",")))

def get_ids(scr):
    scr.get_league_match_ids(242)

def process_match_data(par, scr, filename):
    par.add_match_data(filename, scr)

def extract_data():
    scr = scraper.Scraper()
    par = parser.Parser()
    #scr.get_league_match_ids(242)
    par.add_match_data("data/mls_match_ids.txt", scr)
    par.close_db()

extract_data()