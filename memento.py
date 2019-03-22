import datetime
import requests
from bs4 import BeautifulSoup as Soup
from helper import database, getSunday

def getNewDayOfData(date):
    link = 'http://hitsdailydouble.com/sales_plus_streaming'
    response = Soup(requests.get(link).text, features="lxml")
    print(response)
    table = response.find('div', {'class' : 's101_main_column'})
    rows = table.find_all('tr', {'class': 'hits_album_chart_header_full_alt1'})
    rows += table.find_all('tr', {'class': 'hits_album_chart_header_full_alt2'})
    for row in rows:
        boolean = True
        boolean = addToDictV1(row, date)
        if (boolean == False):
            addToDictV2(row, date)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def filterName(name):
    name = name.strip().title().replace('&Amp;','&').replace('The ','').replace('&Gt;','>')
    filterbrackets = (name.find('('), name.find(')'))
    if filterbrackets[0] > -1:
        first = name[0:filterbrackets[0]]
        second = name[filterbrackets[1] + 1:]
        name = first + second
    if 'Lady Gaga' in name:
        name = 'Lady Gaga'
    if 'Black Panther' in name:
        name = 'Kendrick Lamer'
    name = name.replace("'T","'t").replace('Xxxt','XXXT').replace('Bohemian Rhapsody Bohemian Rhapsody (Origina','Bohemian Rhapsody').strip()
    return name

def addToDict(artist, album, sales, date):
    #database.execute("INSERT INTO AllAlbums (ArtistName,AlbumName,SalesWeek,AlbumSales) VALUES (:artist, :album, :date, :sales)",{"artist": artist, "album": album, "date": date, "sales": sales})
    print(artist, album, sales, date)
def addToDictV1(row, date):
    artist_span = str(row.find('span', {'class' : 'hits_album_chart_item_details_full_artist'}))
    begin, middle, end = artist_span.find('artist">') + 8, artist_span.find('|'), artist_span.find('</span')
    artist, album = filterName(artist_span[begin:middle-1]), filterName(artist_span[middle+1:end])
    albumsSold_td = str(row.find('td', {'class' : 'col_sales'}))
    begin, end= albumsSold_td.find('">') +2 , albumsSold_td.find('</td>')
    albumsSold = albumsSold_td[begin:end]
    boolean = is_number(albumsSold.replace(",",""))
    if (boolean == True):
        addToDict(artist, album, albumsSold, date)
    else:
        return boolean

def addToDictV2(row, date):
    artist_span = str(row.find('span', {'class' : 'hits_album_chart_item_top_full_details_artist'}))
    if (artist_span == 'None'):
        artist_span = str(row.find('span', {'class' : 'hits_album_chart_item_details_full_artist'}))
    begin, end = artist_span.find('artist">') + 8, artist_span.find('</span>')
    artist = filterName(artist_span[begin:end])
    album_span = str(row.find('span',{'class' : 'hits_album_chart_item_top_dull_details_release'}))
    if (album_span == 'None'):
        album_span = str(row.find('span',{'class' : 'hits_album_chart_item_details_release'}))
    begin, end = album_span.find('release"') + 9, album_span.find('</span>')
    album = filterName(album_span[begin:end])
    albumsSold_td = str(row.find('td', {'class':'hits_album_chart_item_top_details_full_sales'}))
    begin, end = albumsSold_td.find('sales">') + 7, albumsSold_td.find('</td>')
    albumsSold = albumsSold_td[begin:end]
    boolean = is_number(albumsSold.replace(",",""))
    if boolean:
        addToDict(artist, album, albumsSold, date)
    else:
        return boolean

def isSunday():
    now = datetime.datetime.now()
    a = str(now.day - 1)
    b = str(now.month) if len(str(now.month)) == 2 else "0" + str(now.month)
    c = str(now.year)
    d = c + b + a
    for sundays in range(0,52):
        if d == str(getSunday(sundays, 2019)):
            getNewDayOfData(d)
    print(d)


if __name__ == '__main__':
    isSunday()

