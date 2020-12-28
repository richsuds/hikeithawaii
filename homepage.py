from flask import Flask, render_template, redirect, url_for, request, Blueprint
import bs4
import requests
from datetime import datetime
from astral import LocationInfo
from datetime import *
from astral.sun import sun
from astral import moon

### SUN/MOON Data #########
moon_phase = moon.phase(datetime.today())
def moonphase():
    if moon_phase >= 0 and moon_phase < 1.1:
        return('New Moon')
    if moon_phase >= 1.1 and moon_phase < 6.38:
        return('Waxing Crescent')
    if moon_phase >= 6.38 and moon_phase < 8.38:
        return('First Quarter')
    if moon_phase >= 8.38 and moon_phase < 13.76:
        return('Waxing Gibbous')
    if moon_phase >= 13.76 and moon_phase < 15.77:
        return('Full Moon')
    if moon_phase >= 15.77 and moon_phase < 21.14:
        return('Waning Gibbous')
    if moon_phase >= 21.14 and moon_phase < 23.14:
        return('Last Quarter')
    if moon_phase >= 23.14 and moon_phase < 28.53:
        return('Waning Crescent')
    if moon_phase >= 28.53 and moon_phase < 29.54:
        return('New Moon')

moon = (moonphase())
tday = datetime.today()

def sr_ss(city, lat, long):
    city = LocationInfo(city, "USA", "US/Hawaii", lat, long)

    s = sun(city.observer, date=tday, tzinfo=city.timezone)

    dawn = (f'{s["dawn"]}')
    sunrise = (f'{s["sunrise"]}')
    sunset = (f'{s["sunset"]}')
    dusk = (f'{s["dusk"]}')

    dawn_clean = dawn.split('.')[0].replace('-', '/')
    sunrise_clean = sunrise.split('.')[0].replace('-', '/')
    sunset_clean = sunset.split('.')[0].replace('-', '/')
    dusk_clean = dusk.split('.')[0].replace('-', '/')

    dawn = datetime.strptime(dawn_clean, "%Y/%m/%d %H:%M:%S")
    dawn_strf = dawn.strftime("%I:%M %p")

    sunrise = datetime.strptime(sunrise_clean, "%Y/%m/%d %H:%M:%S")
    sunrise_strf = sunrise.strftime("%I:%M %p")

    sunset = datetime.strptime(sunset_clean, "%Y/%m/%d %H:%M:%S")
    sunset_strf = sunset.strftime("%I:%M %p")

    dusk = datetime.strptime(dusk_clean, "%Y/%m/%d %H:%M:%S")
    dusk_strf = dusk.strftime("%I:%M %p")

    return(dawn_strf, sunrise_strf, sunset_strf, dusk_strf)

hnl_sr_ss = sr_ss("Honolulu", 21.315603, -157.858093)
hnl_dawn = hnl_sr_ss[0]
hnl_sr   = hnl_sr_ss[1]
hnl_ss   = hnl_sr_ss[2]
hnl_dusk = hnl_sr_ss[3]


now = datetime.now()
current_time = now.strftime("%H:%M:%S")

if int(now.strftime("%H")) >= 23 or int(now.strftime("%H")) < 2:
    curr_time = "11pm"
if int(now.strftime("%H")) >= 2 and int(now.strftime("%H")) < 5:
    curr_time = "2am"
if int(now.strftime("%H")) >= 5 and int(now.strftime("%H")) < 8:
    curr_time = "5am"
if int(now.strftime("%H")) >= 8 and int(now.strftime("%H")) < 11:
    curr_time = "8am"
if int(now.strftime("%H")) >= 11 and int(now.strftime("%H")) < 14:
    curr_time = "11am"
if int(now.strftime("%H")) >= 14 and int(now.strftime("%H")) < 17:
    curr_time = "2pm"
if int(now.strftime("%H")) >= 17 and int(now.strftime("%H")) < 20:
    curr_time = "5pm"
if int(now.strftime("%H")) >= 20 and int(now.strftime("%H")) < 23:
    curr_time = "8pm"

######################### UV Index
res = requests.get('https://forecast.weather.gov/product.php?site=CRH&product=UVI&issuedby=CAC')
res.raise_for_status()
bs4.BeautifulSoup(res.text, features='lxml')

soup = bs4.BeautifulSoup(res.text, features='lxml')
soup.find('#local > pre')

uvi1 = soup.select('#local > pre')

uvi2 = uvi1[0]
uvi3 = str(uvi2)
uvi4 = uvi3[0:-1]

uvi5 = uvi4.index('HONOLULU')
uvi6 = uvi4.index('SEATTLE')

uvi7 = int(uvi5)
uvi8 = int(uvi6)

city = uvi3[uvi7:uvi7 + 8]
indexnum = int(uvi3[uvi6 - 10:uvi6])
indexnumstring = (uvi3[uvi6 - 10:uvi6])

if indexnum in range(0, 3):
    explvl = "Low"
if indexnum in range(3, 6):
    explvl = "Moderate"
if indexnum in range(6, 8):
    explvl = "High"
if indexnum in range(8, 11):
    explvl = "Very High"
if indexnum > 10:
    explvl = "Extreme"

################ Synopsis ################
#
# res = requests.get('https://forecast.weather.gov/product.php?issuedby=HFO&product=AFD&site=hfo')
# res.raise_for_status()
# bs4.BeautifulSoup(res.text, features='lxml')
#
# soup = bs4.BeautifulSoup(res.text, features='lxml')
# soup.find('#localcontent > pre')
#
# syn1 = soup.select('#localcontent > pre')
#
# syn2 = syn1[0]
# syn3 = str(syn2)
# syn4 = syn3[0:-1]
#
# syn5 = syn4.index('SYNOPSIS')
# syn6 = syn4.index('DISCUSSION')
#
# syn7 = int(syn5 + 11)
# syn8 = int(syn6 - 14)
#
# syn = syn3[syn7:syn8]

################ WWA's ################

res = requests.get('https://www.weather.gov/wwamap/wwatxtget.php?cwa=hfo&wwa=all')
res.raise_for_status()
bs4.BeautifulSoup(res.text, features='lxml')

soup = bs4.BeautifulSoup(res.text, features='lxml')
headlines = soup.find_all('h3')
def sort_wwas():
    try:
        h0 = headlines[0].contents[0]
    except IndexError:
        h0 = "None"
    try:
        h1 = headlines[1].contents[0]
    except IndexError:
        h1 = ""
    try:
        h2 = headlines[2].contents[0]
    except IndexError:
        h2 = ""
    try:
        h3 = headlines[3].contents[0]
    except IndexError:
        h3 = ""
    try:
        h4 = headlines[4].contents[0]
    except IndexError:
        h4 = ""

    return(h0, h1, h2, h3, h4)

h0 = sort_wwas()[0]
h1 = sort_wwas()[1]
h2 = sort_wwas()[2]
h3 = sort_wwas()[3]
h4 = sort_wwas()[4]

#
# res = requests.get('https://alerts.weather.gov/cap/hi.php?x=1')
# res.raise_for_status()
# bs4.BeautifulSoup(res.text, features='lxml')
#
# soup = bs4.BeautifulSoup(res.text, features='lxml')
# soup.find('body')
#
# syn1 = soup.select('body')
#
# syn2 = syn1[0]
# syn3 = str(syn2)
# syn4 = syn3[0:-1]
#
# syn5 = syn4.index('<summary>')
# syn6 = syn4.index('</summary>')
#
# syn7 = int(syn5 + 9)
# syn8 = int(syn6)
#
# wwa = syn3[syn7:syn8]

 #Old code

#syn10 = syn4.index('HFO WATCHES/WARNINGS/ADVISORIES')
#syn11 = syn4.index('$$')

#syn12 = int(syn10 + 34)
#syn13 = int(syn11 - 13)

#wwa = syn3[syn12:syn13]

################ Hazards ################
#
# res = requests.get('https://forecast.weather.gov/product.php?site=NWS&issuedby=HFO&product=HWO')
# res.raise_for_status()
# bs4.BeautifulSoup(res.text, features='lxml')
#
# soup = bs4.BeautifulSoup(res.text, features='lxml')
# soup.find('#local > div:nth-child(3) > span')
#
# hzd_sel = soup.select('#local > div:nth-child(3) > span')
# hzds = str(hzd_sel[0].text).strip()

######################### All Island Forecast

res = requests.get('https://forecast.weather.gov/product.php?issuedby=HFO&product=SFP&site=hfo')
res.raise_for_status()
bs4.BeautifulSoup(res.text, features='lxml')

soup = bs4.BeautifulSoup(res.text, features='lxml')
soup.find('#localcontent > pre')

fcst1 = soup.select('#localcontent > pre')

fcst2 = fcst1[0]
fcst3 = str(fcst2)
fcst4 = fcst3[0:-1]

komml = fcst4.find('KAUAI-OAHU-MAUI-MOLOKAI-LANAI-')
big_i = fcst4.find('BIG ISLAND OF HAWAII-')
end = fcst4.find('$$')

komml_int = int(komml)
big_i_int = int(big_i)
end_int = int(end)

komml_sect = fcst3[komml_int:big_i_int].strip()
big_i_sect = fcst3[big_i_int:-1].strip()

sect1_index1 = komml_sect.index('TO')
sect1_index2 = komml_sect.index('MPH')

sect1_int1 = int(sect1_index1)
sect1_int2 = int(sect1_index2 + 4)

komml_fcst = komml_sect[sect1_int1:sect1_int2].title()

sect2_index1 = big_i_sect.index('TO')
sect2_index2 = big_i_sect.index('MPH')

sect2_int1 = int(sect2_index1)
sect2_int2 = int(sect2_index2 + 4)

big_i_fcst = big_i_sect[sect2_int1:sect2_int2].title()



#########################

home = Blueprint('home', __name__)

@home.route("/")
@home.route("/home")
def homeinfo():
    info = "Hikeit Hawaii"
    statement = "Hawaii Hiking Conditions"
    summary = "Hawaii's Hiking Weather...Trail Conditions...and Waterfalls"
    island = "Hawaiian Islands"
    general_title = "Forecast: Hawaiian Islands"

    dawn = hnl_dawn
    sunrise = hnl_sr
    sunset = hnl_ss
    dusk = hnl_dusk
    moon_phase = moon

    all_island_fcst = komml_fcst
    big_island_fcst = big_i_fcst

    # synopsistitle = "Synopsis"
    # synopsis = syn

    wwa_title = "NWS Hazards"
    #hazards = hzds
    wwa0 = h0
    wwa1 = h1
    wwa2 = h2
    wwa3 = h3
    wwa4 = h4

    time = curr_time

    uvexposure = "UV Exposure"
    uvi = 'UV Index:' + indexnumstring + ' | ' + explvl

    return render_template('homev2.html',**locals())
