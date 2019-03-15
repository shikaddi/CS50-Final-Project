import datetime
from time import strptime, strftime
import requests
from bs4 import BeautifulSoup as Soup
import pickle
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
import os
import pandas as pd
import matplotlib.pyplot as plt

engine = create_engine('SQL_Database', echo=True)
database = scoped_session(sessionmaker(bind=engine))
database.execute('CREATE TABLE IF NOT EXISTS ALBUMS (AlbumId VARCHAR UNIQUE PRIMARY KEY, ArtistName VARCHAR NOT NULL, AlbumName VARCHAR NOT NULL);')
database.commit()

class Data():

    def gatherInfo(queries):
        if queries['Album'] == "" and queries['Artist'] == "":
            extra = ""
        elif queries['Album'] != "" and queries['Artist'] == "":
            extra = " AND AlbumName = %(album)s"
        elif queries['Album'] == "" and queries['Artist'] != "":
            extra = " AND ArtistName = %(artist)s"
        else:
            Data.albumCheck(queries['Album'], queries['Artist'])
            extra = " AND AlbumName = %(album)s AND ArtistName = %(artist)s"
        try:
            queries["limitAmount"] = int(queries["limitAmount"])
        except:
            queries["limitAmount"] = 100
        info = (queries['beginWeek'][4:],queries['beginYear'][4:],queries['endWeek'][4:],queries['endYear'][4:])
        if queries["albumSales"] == "":
            queries['albumSales'] = 0
        elif not (queries["albumSales"].replace(",","").isnumeric()):
            queries['albumSales'] = 0
        if queries['method'] == "Cumulative":
            return Data.getCumulativeSales (queries, info, extra)
        elif queries['method'] == 'Highest':
            return Data.getHighestSales(queries, info, extra)
        elif queries['method'] == 'Byweek':
            return Data.getAllSales(queries, info, extra)
        else:
            raise Exception('This is weird, But no valid method was detected?')

    def albumCheck(album, artist):
        hasAnyAlbums = database.execute('SELECT AlbumName FROM ALBUMS WHERE ArtistName = :Artist AND AlbumName = :Album', {'Artist' : artist, 'Album' : album}).fetchone()
        if hasAnyAlbums is None:
            raise Exception('''This Artist doesn't have this Album''')

    def getAllSales(queries, timeTuple, extra):
        begin = getSunday(timeTuple[0], timeTuple[1])
        end = getSunday(timeTuple[2], timeTuple[3])
        frame = pd.read_sql_query(f'Select * from AllAlbums WHERE SalesWeek >= %(begin)s AND SalesWeek <= %(end)s AND albumSales >= %(sales)s{extra} order by albumSales desc LIMIT %(limit)s;',
                                                        con=engine, params={'album': queries['Album'], 'artist' : queries['Artist'], 'begin' : begin, 'end' : end, 'sales': queries['albumSales'], 'limit': queries['limitAmount']})
        if len(frame) == 0:
            raise Exception('''No albums found, either this artist doesn't exist, this album doesn't exist or the chosen artist doesn't have the chosen album''')
        return frame

    def getCumulativeSales(queries, timeTuple, extra):
        begin = getSunday(timeTuple[0], timeTuple[1])
        end = getSunday(timeTuple[2], timeTuple[3])
        frame = pd.read_sql_query(f'Select artistName, albumName, SUM(AlbumSales) from AllAlbums WHERE SalesWeek >= %(begin)s AND SalesWeek <= %(end)s{extra} GROUP BY artistname,albumName order by sum(albumSales) desc LIMIT %(limit)s;',
                                                        con=engine, params={'album': queries['Album'], 'artist' : queries['Artist'], 'begin' : begin, 'end' : end, 'limit': queries['limitAmount']})
        frame['salesweek'] = 'Total Sales'
        frame.rename(inplace=True, columns={'sum':'albumsales'})
        minimum = frame['albumsales'] >= queries["albumSales"]
        if len(frame) == 0:
            raise Exception('''No albums found, either this artist doesn't exist, this album doesn't exist or the chosen artist doesn't have the chosen album''')
        return frame[minimum]

    def getHighestSales(queries, timeTuple, extra):
        begin = getSunday(timeTuple[0], timeTuple[1])
        end = getSunday(timeTuple[2], timeTuple[3])
        frame = pd.read_sql_query(f'''select * from AllAlbums WHERE (artistname, albumname, albumsales) in (Select artistName, albumName, MAX(AlbumSales) from AllAlbums
                                        WHERE SalesWeek >= %(begin)s AND SalesWeek <= %(end)s AND albumSales >= %(sales)s{extra} GROUP BY artistname,albumName ) order by albumSales desc LIMIT %(limit)s;''',
                                        con=engine, params={'album': queries['Album'], 'artist' : queries['Artist'], 'begin' : begin, 'end' : end, 'sales': queries['albumSales'], 'limit': queries['limitAmount']})
        frame.rename(inplace=True, columns={'max':'albumsales'})
        if len(frame) == 0:
            raise Exception('''No albums found, either this artist doesn't exist, this album doesn't exist or the chosen artist doesn't have the chosen album''')
        return frame

    def howManyToShow(limit, length):
        if limit == "":
            if length > 250:
                return range(250)
            else:
                return range(length)
        elif int(limit) > length:
            return range(length)
        else:
            return range(limit)

class barPreparation():

    def coloringList(info):
        listOfBools = []
        multipleArtists = {}
        maxColoring = 0
        for artist in info:
            if artist in multipleArtists:
                if maxColoring != 15:
                    if multipleArtists[artist] == 1:
                        maxColoring += 1
                    multipleArtists[artist] += 1
            else:
                multipleArtists[artist] = 1
        for artist in info:
            if multipleArtists.get(artist) != 1:
                listOfBools.append(True)
                print(artist, True)
            else:
                listOfBools.append(False)
                print(artist, False)
        return listOfBools

    def addColorToFrame(info, query):
        defaultColor = 'grey'
        otherColors = ['yellow', 'black', 'red','orange','teal','brown','blue','pink','cyan','green','purple','navy','crimson','lime','khaki']
        colorsAssignedToArtist = {}
        colorList = []
        for artist,bool in zip(info[query],info['bools']):
            if bool == False:
                colorList.append(defaultColor)
            else:
                for color in otherColors:
                    if not color in colorsAssignedToArtist.values():
                        if not artist in colorsAssignedToArtist.keys():
                            colorsAssignedToArtist[artist.strip()] = color
                            break
                try:
                    colorList.append(colorsAssignedToArtist[artist])
                except:
                    colorList.append(defaultColor)
        return colorList

    def mergeAlbumAndArtist(info):
        artistAndAlbum = []
        for artist, album in zip(info['artistname'], info['albumname']):
            artistAndAlbum.append(f'{artist} | {album}')
        return artistAndAlbum

    def createPlot(info, size, width):
        plt.clf()
        albumsSoldAxis = info['albumsales'].iloc[::-1].plot(kind='barh', figsize=(10,size + 2), fontsize=12, color=info['colors'].iloc[::-1], edgecolor = 'black', tick_label=info['merger'].iloc[::-1])
        albumsSoldAxis.set_title("Artists who sell a lot", fontsize=18)
        albumsSoldAxis.set_xlabel("Albums sold in one week", fontsize=18)
        albumsSoldAxis.set_xticks(range(0,width,width // 8))
        ylabel = []
        for patch, artistAndAlbum, number in zip(albumsSoldAxis.patches, info['merger'].iloc[::-1], range(len(info['merger']),0,-1)):
            x, y = patch.get_width(), patch.get_y()
            albumsSoldAxis.text(x + 10000, y, format(x,',d'))
            ylabel.append(f'{artistAndAlbum} - {number}')
        albumsSoldAxis.set_yticks(range(len(ylabel)))
        albumsSoldAxis.set_yticklabels(ylabel)
        plt.setp(albumsSoldAxis.get_xticklabels(), fontsize=10)
        figure = albumsSoldAxis.get_figure()
        figure.tight_layout()
        if os.path.exists("static/test.jpg"):
            os.remove("static/test.jpg")
        figure.savefig(f'static/test.jpg')
        return f'static/test.jpg'

def getSunday(_weekNo, _Year):
    janOne = strptime('%s-01-01' % _Year, '%Y-%m-%d')
    dayOfFirstWeek = ((7-int((strftime("%u",janOne)))+ 2 % 7))
    dateOfFirstWeek = strptime('%s-01-%s' % (_Year, dayOfFirstWeek), '%Y-%m-%d')
    dayOne = datetime.datetime( dateOfFirstWeek.tm_year, dateOfFirstWeek.tm_mon, dateOfFirstWeek.tm_mday )
    daysToGo = 7*(int(_weekNo)-1)
    lastDay = daysToGo+6
    dayY = dayOne + datetime.timedelta(days = lastDay - 7)
    resultDateY = strptime('%s-%s-%s' % (dayY.year, dayY.month, dayY.day), '%Y-%m-%d')
    stringedmonth = str(resultDateY[1])
    stringedday = str(resultDateY[2])
    if len(stringedmonth) == 1:
        stringedmonth = "0" + stringedmonth
    if len(stringedday) == 1:
        stringedday = "0" + stringedday
    theDaysIWant = str(resultDateY[0]) + stringedmonth + stringedday
    return int(theDaysIWant)
