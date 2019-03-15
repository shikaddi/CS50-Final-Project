import pickle
from flask import Flask, render_template, jsonify, request
from helper import Data, barPreparation, database

def main():
    database.execute('CREATE TABLE IF NOT EXISTS AllAlbums (ArtistName VARCHAR NOT NULL, AlbumName VARCHAR NOT NULL, SalesWeek INT NOT NULL, AlbumSales INT NOT NULL , PRIMARY KEY (ArtistName, AlbumName, SalesWeek));')
    database.execute('DELETE FROM AllAlbums;')
    database.commit()
    dictOfArtist = pickle.load(open('newerDicts.p', "rb"))
    id = 0

    for name, music in dictOfArtist.items():
        for albumName, albumData in music.items():
            id += 1
            if albumName == 'Various Artists' or albumName == "Soundtrack":
                temp = albumName
                albumName = name
                name = temp
                if albumName == "Kendrick Lamer" or albumName == "Kendrick Lamar":
                    name = "Kendrick Lamar"
                    albumName = "Black Panther"
            #database.execute('INSERT INTO ALBUMS (AlbumId, ArtistName, AlbumName) VALUES (:Id, :Artist, :Album);', {"Id" : id,"Artist" : name, "Album" : albumName})
            for data in albumData:
                for week, sales in data.items():
                    if int(week) >= 20150201: #5th week
                        if name != "Various Artists" or albumName != 'Soundtrack':
                            database.execute('INSERT INTO AllAlbums (ArtistName,AlbumName,SalesWeek,AlbumSales) VALUES (:artist, :album, :week, :sales);',
                                                                { 'artist' : name, 'album': albumName, 'week' : week, 'sales' : int(sales.replace(",",""))})
    database.execute("INSERT INTO AllAlbums (ArtistName,AlbumName,SalesWeek,AlbumSales) VALUES ('Taylor Swift', 'Reputation', 20171126, 256000);")
    database.execute("INSERT INTO AllAlbums (ArtistName,AlbumName,SalesWeek,AlbumSales) VALUES ('Tim McGraw & Faith Hill', 'Rest Of Our Life', 20171126 , 104000);")
    database.execute("INSERT INTO AllAlbums (ArtistName,AlbumName,SalesWeek,AlbumSales) VALUES ('Sam Smith', 'Thrill Of It All', 20171126, 58000);")
    database.execute("INSERT INTO AllAlbums (ArtistName,AlbumName,SalesWeek,AlbumSales) VALUES ('Garth Brooks', 'Anthology Part I', 20171126, 53000);")
    database.execute("INSERT INTO AllAlbums (ArtistName,AlbumName,SalesWeek,AlbumSales) VALUES ('Pentatonix', 'A Pentatonic Christmas', 20171126, 47000);")
    database.execute("INSERT INTO AllAlbums (ArtistName,AlbumName,SalesWeek,AlbumSales) VALUES ('Pink', 'Beautiful Trauma', 20171126, 44000);")
    database.execute("INSERT INTO AllAlbums (ArtistName,AlbumName,SalesWeek,AlbumSales) VALUES ('Maroon 5', 'Red Pill Blues', 20171126, 43000);")
    database.execute("INSERT INTO AllAlbums (ArtistName,AlbumName,SalesWeek,AlbumSales) VALUES ('Ed Sheeran', 'Divide', 20171126, 41000);")
    database.execute("INSERT INTO AllAlbums (ArtistName,AlbumName,SalesWeek,AlbumSales) VALUES ('Post Malone', 'Stoney', 20171126, 39000);")
    database.execute("INSERT INTO AllAlbums (ArtistName,AlbumName,SalesWeek,AlbumSales) VALUES ('Lil Uzi Vert', 'Luv Is Rage 2', 20171126, 41000);")
    database.commit()

if __name__ == "__main__":
    main()

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 5

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/artistchecker/<string:artist>")
def artistChecker(artist):
    artist = '%' + artist + '%'
    sqlListOfPossibleArtist = database.execute(f"SELECT distinct ArtistName from ALBUMS WHERE ArtistName like :artist LIMIT 5;", {'artist' : artist.strip().title()}).fetchall()
    if len(sqlListOfPossibleArtist) == 0:
        sqlListOfPossibleArtist = database.execute(f"SELECT distinct ArtistName from ALBUMS WHERE ArtistName like :artist LIMIT 5;", {'artist': artist.strip()}).fetchall()
    listOfPossibleArtist = []
    for possibleArtist in sqlListOfPossibleArtist:
        listOfPossibleArtist.append(possibleArtist[0])
    database.close()
    return jsonify(listOfPossibleArtist)

@app.route("/albumchecker/<string:queries>")
def albumChecker(queries):
    query = queries.split('|')
    query[0] = '%' + query[0] + '%'
    query[1] = '%' + query[1] + '%'
    sqlListOfPossibleAlbums = database.execute(f"SELECT distinct AlbumName from ALBUMS WHERE ArtistName like :album AND AlbumName like :artist LIMIT 5;", {'album': query[1].strip().title(), 'artist': query[0].strip().title()}).fetchall()
    if len(sqlListOfPossibleAlbums) == 0:
        sqlListOfPossibleAlbums = database.execute(f"SELECT distinct AlbumName from ALBUMS WHERE ArtistName like :album AND AlbumName like :artist LIMIT 5;", {'album': query[1].strip(), 'artist': query[0].strip()}).fetchall()
    listOfPossibleAlbums = []
    for possibleAlbum in sqlListOfPossibleAlbums:
        listOfPossibleAlbums.append(possibleAlbum[0])
    database.close()
    return jsonify(listOfPossibleAlbums)

@app.route("/table", methods=['GET','POST'])
def table():
    if request.method == "POST":
        try:
            queries = {}
            thingsToQuery = ["Artist","Album","albumSales", "limitAmount",'method',"endWeek","endYear","beginWeek",'beginYear']
            for query in thingsToQuery:
                queries[query] = request.form.get(query).title()
            if queries['limitAmount'] == "":
                queries["limitAmount"] = 250
            frame = Data.gatherInfo(queries)
            numbers = Data.howManyToShow(queries['limitAmount'], len(frame['artistname']))
            return render_template('table.html', tuple = frame, numbers = numbers)
        except Exception as error:
            return render_template('error.html', errormessage = error, numbers = 0)
    return render_template('index.html')

@app.route("/barchart", methods=["GET","POST"])
def barchart():
    if request.method == "POST":
        try:
            queries = {}
            thingsToQuery = ["Artist","Album","albumSales", "limitAmount",'method',"endWeek","endYear","beginWeek",'beginYear']
            for query in thingsToQuery:
                queries[query] = request.form.get(query).strip().title()
            if queries['limitAmount'] == "":
                queries["limitAmount"] = 100
            frame = Data.gatherInfo(queries)
            if not queries['Artist'] == "":
                frame['bools'] = barPreparation.coloringList(frame['albumname'])
                frame['colors'] = barPreparation.addColorToFrame(frame, 'albumname')
            else:
                frame['bools'] = barPreparation.coloringList(frame['artistname'])
                frame['colors'] = barPreparation.addColorToFrame(frame, 'artistname')
            frame['merger'] = barPreparation.mergeAlbumAndArtist(frame)
            width = int(frame['albumsales'][0].item())
            url = barPreparation.createPlot(frame, len(frame['artistname'])/3, width)
            return render_template('barchart.html', numbers = 0)
        except Exception as error:
            return render_template('error.html', errormessage = error, numbers = 0)
    return render_template('index.html')

@app.route('/json', methods=['get','post'])
def json():
    if request.method == 'POST':
        try:
            queries = {}
            thingsToQuery = ["Artist","Album","albumSales", "limitAmount",'method',"endWeek","endYear","beginWeek",'beginYear']
            for query in thingsToQuery:
                queries[query] = request.form.get(query).title()
            if queries['limitAmount'] == "":
                queries["limitAmount"] = 25000
            frame = Data.gatherInfo(queries)
            return frame.transpose().to_json()
        except Exception as error:
            return render_template('error.html', errormessage = error, numbers = 0)
    return render_template('index.html')
