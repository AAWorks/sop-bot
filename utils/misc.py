import scrape, parse

def count_file_data(filename):
    with open(filename, "r") as f:
        print(len(f.readline().split(",")))

def get_ids(scr):
    scr.get_league_match_ids(242)

def process_match_data(par, scr, filename):
    par.add_match_data(filename, scr)

def peek():
    print(parse.Parser().peek())