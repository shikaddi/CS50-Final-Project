import datetime
from time import strptime, strftime
import requests
from bs4 import BeautifulSoup as Soup
import pickle

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

def getMemento(dates):
    dictOfArtists = pickle.load(open('newDicts.p','rb'))
    missedDates = []
    length = len(dates)
    thisone = 0

    for date in dates:
        date = "20190310"
        thisone += 1
        print(f'{thisone}/{length}', date)
        if 1==1 :
            #link = 'https://web.archive.org/web/20180825161931/http://hitsdailydouble.com/sales_plus_streaming'
            link = 'http://hitsdailydouble.com/sales_plus_streaming'
            response = Soup(requests.get(link).text, features="lxml")
            if not "Status: Final" in str(response) and "status:" in str(response):
                missedDates.append(date)
            table = response.find('div', {'class' : 's101_main_column'})
            rows = table.find_all('tr', {'class': 'hits_album_chart_header_full_alt1'})
            rows += table.find_all('tr', {'class': 'hits_album_chart_header_full_alt2'})
            for row in rows:
                boolean = True
                boolean = addToDictV1(row, date, dictOfArtists)
                if (boolean == False):
                    addToDictV2(row, date, dictOfArtists)
        else:
            missedDates.append(date)
            print('missed this: ', date)
    return dictOfArtists

def allSundaysFromDateTillYear(lastSunday, stopYear):
    if int(stopYear) < 2013 or int(stopYear) > 2018:
        return []
    sundays = [lastSunday]
    year, month, day = int(lastSunday[0:4]), int(lastSunday[4:6]), int(lastSunday[6:])
    lastDate = datetime.date(year, month, day)
    i = 0
    while (str((sundays)[i])[0:4] != stopYear):
        lastDate = lastDate - datetime.timedelta(days = 7)
        sundays.append(str(lastDate).replace("-",""))
        i += 1
    return sundays

def initiateDates():
    dates = allSundaysFromDateTillYear("20190310", '2014')
    return dates

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

def addToDict(artist, album, sales, date, dictOfArtists):
    if not artist in dictOfArtists:
                dictOfArtists[artist] = {album : []}
                dictOfArtists[artist][album].append({date : sales})
    elif not album in dictOfArtists[artist]:
                dictOfArtists[artist][album] = []
                dictOfArtists[artist][album].append({date : sales})
    else:
                dictOfArtists[artist][album].append({date : sales})

def addToDictV1(row, date , dictOfArtists):
    artist_span = str(row.find('span', {'class' : 'hits_album_chart_item_details_full_artist'}))
    begin, middle, end = artist_span.find('artist">') + 8, artist_span.find('|'), artist_span.find('</span')
    artist, album = filterName(artist_span[begin:middle-1]), filterName(artist_span[middle+1:end])
    albumsSold_td = str(row.find('td', {'class' : 'col_sales'}))
    begin, end= albumsSold_td.find('">') +2 , albumsSold_td.find('</td>')
    albumsSold = albumsSold_td[begin:end]
    boolean = is_number(albumsSold.replace(",",""))
    if (boolean == True):
        addToDict(artist, album, albumsSold, date, dictOfArtists)
    else:
        return boolean

def addToDictV2(row, date, dictOfArtists):
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
        addToDict(artist, album, albumsSold, date, dictOfArtists)
    else:
        return boolean

def identifyDuplicates():
    dictOfArtists = pickle.load(open('newerDicts.p','rb'))
    #del dictOfArtists["Panic! At Disco"]["Death Of A Bachelor"][31]
    dup = []
    for arname, artist in dictOfArtists.items():
        for alname, album in artist.items():
            i = 0
            for list in album:
                for week, sales in list.items():
                    i += 1
                    if (week == '20160724') and alname == "Death Of A Bachelor":
                        dup.append((arname, alname, i-1))
                        print(arname, alname , dictOfArtists[arname][alname][i-1], i)
                #break
            #break
        #break
    #duplicates = []
    #for i in range(len(dup)-1):
    #    if (dup[i][0], dup[i][1], dictOfArtists[dup[i][0]][dup[i][1]][dup[i][2]]) == (dup[i+1][0], dup[i+1][1], dictOfArtists[dup[i+1][0]][dup[i+1][1]][dup[i+1][2]]):
    #        duplicates.append(([dup[i][0]],[dup[i][1]],[dup[i][2]]))
    #for list in range(len(duplicates)):
    #     i,j,k = duplicates[list]
    #    i,j,k= i[0], j[0],k[0]
    #    del (dictOfArtists[i][j][k])
    #pickle.dump(dictOfArtists, open('newerDicts.p', 'wb'))

dictOfArtists = {}
if __name__ == '__main__':
    pass
    #identifyDuplicates()
    #dates = initiateDates()
    #dictOfArtists = getMemento(dates)
    #pickle.dump(dictOfArtists, open('newDicts.p', 'wb'))
