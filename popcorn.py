import requests
import json
import sqlite3
import os

sqlite_file = './movie_tracker.sqlite'

def checkDB():
    data = requests.get('https://movies-v2.api-fetch.website/movies/1?sort=trending%15')
    rawdata = data.json()
    parsedData = {}

    for movie in rawdata:
        id = movie["imdb_id"]
        title = movie["title"]
        year = movie["year"]
        try:
            u1080 = movie["torrents"]["en"]["1080p"]["url"]
        except:
            u1080 = "none"
        try:
            u720 = movie["torrents"]["en"]["720p"]["url"]
        except:
            u720 = "none"
        parsedData[id] = {"title": title,"year": year,"u1080": u1080, "u720": u720}
    return parsedData

def createSQL():
    table_name = 'movies'
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE movies(id TEXT PRIMARY KEY, title TEXT, year TEXT, url TEXT)
    ''')

    conn.commit()
    conn.close



def addTorrent(title, year, url):
    uri = "http://localhost:8080/command/download"
    rename = "{0} ({1})".format(title,year)
    data = {'urls': url, 'category': 'movie', 'rename': rename}
    r = requests.post(uri, data)
    

def compareDB(newData):
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    for movie in newData:
        _id = movie
        title = newData[_id]["title"]
        year = newData[_id]["year"]
        if(newData[_id]["u1080"] != "none"):
            url = newData[_id]["u1080"]
        else:
            url = newData[_id]["u720"]
        data = (_id, title, year, url)
        try:
            sql = '''INSERT INTO movies(id, title, year, url)
                          VALUES(?,?,?,?)'''
            c.execute(sql,data)
            conn.commit()
            print("Added {} to DB".format(title))
            addTorrent(title, year, url)
        except sqlite3.IntegrityError:
            print('ERROR: {1} ({0}) already exists in database.'.format(_id, title))
    conn.close



if not os.path.isfile('./movie_tracker.sqlite'):
    createSQL()
    
while(True):
    newData = checkDB()
    compareDB(newData)
    print("\n\nUpdated... Sleeping for 12 Hours\n\n")
    sleep(43200)
    



        
