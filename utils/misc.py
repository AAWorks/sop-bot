import scrape, parse
import sqlite3
def count_file_data(filename):
    with open(filename, "r") as f:
        print(len(f.readline().split(",")))

def get_ids(scr):
    scr.get_league_match_ids(242)

def process_match_data(par, scr, filename):
    par.add_match_data(filename, scr)

def peek():
    print(parse.Parser().peek())


def delete_duplicates(league_name):
    sqliteConnection = sqlite3.connect('data/soccer_data.db')
    cursor = sqliteConnection.cursor()
    match_ids = []
    
    cursor.execute(f"SELECT rowid, * FROM {league_name}")
    all_rows = cursor.fetchall()

    for row in all_rows:
        if row[1] in match_ids:
            rowid = row[0]
            cursor.execute(f"DELETE from {league_name} where rowid = {rowid}")
            sqliteConnection.commit()
        else:
            match_ids.append(row[1])


delete_duplicates("mls")
