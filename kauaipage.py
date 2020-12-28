from flask import Flask, render_template, redirect, url_for, request, Blueprint
import bs4
import requests
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

lih_sr_ss = sr_ss("Lihue", 21.97472, -159.36555)
lih_dawn = lih_sr_ss[0]
lih_sr   = lih_sr_ss[1]
lih_ss   = lih_sr_ss[2]
lih_dusk = lih_sr_ss[3]

#**************************************** KAUAI *******************************************************
# OBSERVATIONS

def observations(icao):
    res = requests.get('https://w1.weather.gov/data/obhistory/'+icao+'.html')
    res.raise_for_status()
    bs4.BeautifulSoup(res.text, features='lxml')
    soup = bs4.BeautifulSoup(res.text, features='lxml')
    soup.find('body > table:nth-child(4)')
    all_obs = soup.select('td')

    date = str(all_obs[8].text).strip()
    time = str(all_obs[9].text).strip()
    wind = str(all_obs[10].text).strip()
    weather = str(all_obs[12].text).strip()
    temp = str(all_obs[14].text).strip()
    heat_index = str(all_obs[20].text).strip()

    #def rain():
    #rain1 = str(all_obs[25].text).strip()
    #rain2 = str(all_obs[43].text).strip()
    return date, time, wind, weather, temp, heat_index

# Lihue Observations
phli_observation = observations('PHLI')[0:6]
phli_date = phli_observation[0]
phli_time = phli_observation[1]
phli_wind = phli_observation[2]
phli_weather = phli_observation[3]
phli_temp = phli_observation[4]
phli_heat_index = phli_observation[5]

# Barking Sands Observations
phbk_observation = observations('PHBK')[0:6]
phbk_date = phbk_observation[0]
phbk_time = phbk_observation[1]
phbk_wind = phbk_observation[2]
phbk_weather = phbk_observation[3]
phbk_temp = phbk_observation[4]
phbk_heat_index = phbk_observation[5]

# Kona Observations
phko_observation = observations('PHKO')[0:6]
phko_date = phko_observation[0]
phko_time = phko_observation[1]
phko_wind = phko_observation[2]
phko_weather = phko_observation[3]
phko_temp = phko_observation[4]
phko_heat_index = phko_observation[5]

#24hr Rainfall totals
# 00-24hr obs
res1 = requests.get('https://forecast.weather.gov/product.php?issuedby=HFO&product=RRA&site=hfo')
res1.raise_for_status()
bs4.BeautifulSoup(res1.text, features='lxml')
soup1 = bs4.BeautifulSoup(res1.text, features='lxml')

soup1.find('#localcontent > pre')
page1 = soup1.select('#localcontent > pre')
day_one_obs = page1[0]


res2 = requests.get('https://forecast.weather.gov/product.php?site=HFO&issuedby=HFO&product=RRA&format=CI&version=50&glossary=0')
res2.raise_for_status()
bs4.BeautifulSoup(res2.text, features='lxml')
soup2 = bs4.BeautifulSoup(res2.text, features='lxml')

soup2.find('#localcontent > pre')
page2 = soup2.select('#localcontent > pre')
day_two_obs = page2[0]

def pull_request(day_num_obs):
    description1_list = list(day_num_obs.contents[0].string.split())
    kauai_index_start = description1_list.index('Kauai')
    kauai_index_end = description1_list.index('Oahu')
    kauai_section = (description1_list[kauai_index_start:kauai_index_end])
    return(kauai_section)

kauai_section1 = pull_request(day_one_obs)
kauai_section2 = pull_request(day_two_obs)

def rain_stations(day_num_obs):
    if day_num_obs == day_one_obs:
        kauai_section = kauai_section1
    elif day_num_obs == day_two_obs:
        kauai_section = kauai_section2

    def day_sections(num):
        ##KAUAI
        ##Windward/Mauka Sites
        MKAH1 = kauai_section[kauai_section.index('MKAH1') + num]
        PLRH1 = kauai_section[kauai_section.index('PLRH1') + num]
        WKRH1 = kauai_section[kauai_section.index('WKRH1') + num]
        KLOH1 = kauai_section[kauai_section.index('KLOH1') + num]
        MCRH1 = kauai_section[kauai_section.index('MCRH1') + num+1]
        WLGH1 = kauai_section[kauai_section.index('WLGH1') + num]
        WNHH1 = kauai_section[kauai_section.index('WNHH1') + num]
        HNIH1 = kauai_section[kauai_section.index('HNIH1') + num]
        WLLH1 = kauai_section[kauai_section.index('WLLH1') + num+1]
        PRIH1 = kauai_section[kauai_section.index('PRIH1') + num]
        MLDH1 = kauai_section[kauai_section.index('MLDH1') + num]
        ANHH1 = kauai_section[kauai_section.index('ANHH1') + num]
        KPIH1 = kauai_section[kauai_section.index('KPIH1') + num]
        WLDH1 = kauai_section[kauai_section.index('WLDH1') + num+2]
        WUHH1 = kauai_section[kauai_section.index('WUHH1') + num]
        LIHH1 = kauai_section[kauai_section.index('LIHH1') + num+2]
        HLI   = kauai_section[kauai_section.index('HLI') + num]
        ##Leeward Sites
        POIH1 = kauai_section[kauai_section.index('POIH1') + num-1]
        OMAH1 = kauai_section[kauai_section.index('OMAH1') + num]
        KHEH1 = kauai_section[kauai_section.index('KHEH1') + num]
        PAKH1 = kauai_section[kauai_section.index('PAKH1') + num]
        HNPH1 = kauai_section[kauai_section.index('HNPH1') + num]
        POPH1 = kauai_section[kauai_section.index('POPH1') + num]
        WHGH1 = kauai_section[kauai_section.index('WHGH1') + num]
        WMTH1 = kauai_section[kauai_section.index('WMTH1') + num+1]
        MNRH1 = kauai_section[kauai_section.index('MNRH1') + num-1]

        return(MKAH1, PLRH1, WKRH1, KLOH1, MCRH1, WLGH1, WNHH1, HNIH1,
                WLLH1, PRIH1, MLDH1, ANHH1, KPIH1, WLDH1, WUHH1, LIHH1,
                HLI, POIH1, OMAH1, KHEH1, PAKH1, HNPH1, POPH1, WHGH1,
                WMTH1, MNRH1)

    # num = 5
    all_03 = day_sections(5)
    all_06 = day_sections(7)
    all_12 = day_sections(9)
    all_24 = day_sections(11)

    return(all_03, all_06, all_12, all_24)

all_obs1 = rain_stations(day_one_obs)
all_obs2 = rain_stations(day_two_obs)

all_obs1_03 = (list(all_obs1[0])[0:150])
all_obs1_06 = (list(all_obs1[1])[0:150])
all_obs1_12 = (list(all_obs1[2])[0:150])
all_obs1_24 = (list(all_obs1[3])[0:150])

all_obs2_03 = (list(all_obs2[0])[0:150])
all_obs2_06 = (list(all_obs2[1])[0:150])
all_obs2_12 = (list(all_obs2[2])[0:150])
all_obs2_24 = (list(all_obs2[3])[0:150])
#print(all_obs2_24)

def sort_locations(loc_num):
    try:
        day1_03 = float(all_obs1_03[loc_num])
    except ValueError:
        day1_03 = float(0.00)

    try:
        day1_06 = float(all_obs1_06[loc_num])
    except ValueError:
        day1_06 = float(0.00)

    try:
        day1_12 = float(all_obs1_12[loc_num])
    except ValueError:
        day1_12 = float(0.00)

    try:
        day1_24 = float(all_obs1_24[loc_num])
    except ValueError:
        day1_24 = float(0.00)

    try:
        day2_03 = float(all_obs2_03[loc_num])
    except ValueError:
        day2_03 = float(0.00)

    try:
        day2_06 = float(all_obs2_06[loc_num])
    except ValueError:
        day2_06 = float(0.00)

    try:
        day2_12 = float(all_obs2_12[loc_num])
    except ValueError:
        day2_12 = float(0.00)

    try:
        day2_24 = float(all_obs2_24[loc_num])
    except ValueError:
        day2_24 = float(0.00)

    def rainfall_tf():
        day1_1 = float(day1_03 + day1_06)
        day1_2 = float(day1_12 + day1_24)
        day2_1 = float(day2_03 + day2_06)
        day2_2 = float(day2_12 + day2_24)

        # 12hr group
        if day1_24 >= float(0.25) and day1_24 < float(0.50):
            total = float(0.50 + ((day2_24) * 0.66))
        elif day1_24 >= float(0.50) and day1_24 < float(0.75):
            total = float(1.0 + ((day2_24) * 0.66))
        elif day1_24 >= float(0.75) and day1_24 < float(1.0):
            total = float(1.0 + ((day2_24) * 0.66))

        # 12hr group
        elif day1_12 >= float(0.25) and day1_12 < float(0.50):
            total = float(0.50 + day1_24 - day1_12 + ((day2_24) * 0.75))
        elif day1_12 >= float(0.50) and day1_12 < float(0.75):
            total = float(1.25 + day1_24 - day1_12 + ((day2_24) * 0.75))
        elif day1_12 >= float(0.75) and day1_12 < float(2.0):
            total = float(2.0 + day1_24 - day1_12 + ((day2_24) * 0.75))

        # 06hr group
        elif day1_06 >= float(0.15) and day1_06 < float(0.25):
            total = float(0.50 + day1_24 - day1_06 + ((day2_24) * 0.75))
        elif day1_06 >= float(0.25) and day1_06 < float(0.50):
            total = float(1.0 + day1_24 - day1_06 + ((day2_24) * 0.75))
        elif day1_06 >= float(0.50) and day1_06 < float(0.75):
            total = float(2.0 + day1_24 - day1_06 + ((day2_24) * 0.75))
        elif day1_06 >= float(0.75) and day1_06 < float(3.0):
            total = float(3.0 + day1_24 - day1_06 + ((day2_24) * 0.75))

        # 03hr group
        elif day1_03 >= float(0.05) and day1_03 < float(0.10):
            total = float(0.25 + day1_24 - day1_03 + ((day2_24) * 0.75))
        elif day1_03 >= float(0.10) and day1_03 < float(0.15):
            total = float(0.50 + day1_24 - day1_03 + ((day2_24) * 0.75))
        elif day1_03 >= float(0.15) and day1_03 < float(0.25):
            total = float(1.0 + day1_24 - day1_03 + ((day2_24) * 0.75))
        elif day1_03 >= float(0.25) and day1_03 < float(0.50):
            total = float(2.0 + day1_24 - day1_03 + ((day2_24) * 0.75))
        elif day1_03 >= float(0.50):
            total = float(3.5 + day1_24 - day1_03 + ((day2_24) * 0.75))

        else:
            total = float(day1_24 + ((day2_24) * 0.75))
        return(total)
    return(rainfall_tf())

#KAUAI
MKAH1 = (sort_locations(0))
PLRH1 = (sort_locations(1))
WKRH1 = (sort_locations(2))
KLOH1 = (sort_locations(3))
MCRH1 = (sort_locations(4))# Both N and NW Kauai
WLGH1 = (sort_locations(5))# Both N and NW Kauai

WNHH1 = (sort_locations(6))# N Kauai
HNIH1 = (sort_locations(7))
WLLH1 = (sort_locations(8))# Affects whole island(Mt Waialeale/Wettest place)
PRIH1 = (sort_locations(9))        # Wai Koa Loop, Kilauea Falls, Kauapea,
MLDH1 = (sort_locations(10))        # Na Aina Kai Botanical Gardens)

ANHH1 = (sort_locations(11))
KPIH1 = (sort_locations(12))
WLDH1 = (sort_locations(13))
WUHH1 = (sort_locations(14))
LIHH1 = (sort_locations(15))

HLI   = (sort_locations(16))
POIH1 = (sort_locations(17))# No trails
OMAH1 = (sort_locations(18))# No trails
KHEH1 = (sort_locations(19))
PAKH1 = (sort_locations(20))

HNPH1 = (sort_locations(21))
POPH1 = (sort_locations(22))
WHGH1 = (sort_locations(23))
WMTH1 = (sort_locations(24))
MNRH1 = (sort_locations(25))

def rain_calc():
    # NW Kauai/Kula/Kokee/NaPali Kona/Waimea Canyon (Waipoo, Waimea Canyon, Paaiki)
    nw_kauai_total = float( (WLLH1 + MKAH1 + PLRH1 + WKRH1 + MCRH1 + WLGH1) / 6 )
    # N Kauai/NaPali (NaPali Coast, Hoolea Falls, Hanakapai Falls, Limahuli Falls)
    n_kauai_total = float( (WLLH1 + KLOH1 + MCRH1 + WLGH1 + WNHH1 + HNIH1) / 6 )
    # Central (Mt Waialeale/Wettest place/ Hinalele, Puwainui, Waianuenue, Kahili, Hali'i, Manawaiopuna(Jurassic Park Falls)
    central_total = float( WLLH1 )
    # NE Kauai / Princeville area(Okolehao, Princeville Botanical Garden, Wai Koa Loop, Kilauea Falls, Kauapea, Na Aina Kai Botanical Gardens)
    ne_kauai_total = float( (WLLH1 + PRIH1 + MLDH1) / 3 )
    # Moloaa Forest / (Opae Falls)
    moloaa_total = float( (WLLH1 + ANHH1) / 2 )
    # Kapaa-Wailua / (WailuaSleeping Giant, Kaholalele, Hoopii, Makaleha, Kapakaiki)
    wailua_total = float( (WLLH1 + KPIH1 + WLDH1 + WUHH1 + LIHH1) / 5 )
    # SE Coast rain totals
    se_kauai_total = float( (WLLH1 + POIH1 + OMAH1) / 3 )
    # S Kauai (Ooiki, Kaukiuki, Waiolue)
    s_kauai_total = float( (WLLH1 + KHEH1) / 2  )
    # Port Allen-Waimea
    waimea_total = float( (WLLH1 + PAKH1 + HNPH1 + POPH1 + WHGH1 + WMTH1) / 6 )

    def conditions(rain_total):

        if rain_total < .02:
            mud = ("Mostly Dry")
            falls = ("Dry-Weak")
            falls_dry = ("Dry-Weak")
            falls_wet = "Weak-Light"
        if rain_total >= .02 and rain_total < .10:
            mud = ("Slightly Muddy")
            falls = ("Dry-Weak")
            falls_dry = ("Dry-Weak")
            falls_wet = ("Light")
        if rain_total >= .10 and rain_total < .5:
            mud = ("Slightly Muddy")
            falls = ("Weak-Light")
            falls_dry = ("Dry-Weak")
            falls_wet = ("Light")
        if rain_total >= .5 and rain_total < .75:
            mud = ("Muddy")
            falls = ("Weak-Light")
            falls_dry = ("Dry-Weak")
            falls_wet = ("Light-Moderate")
        if rain_total >= .75 and rain_total < 1:
            mud = ("Muddy")
            falls = ("Light")
            falls_dry = ("Dry-Weak")
            falls_wet = ("Light-Moderate")
        if rain_total >= 1 and rain_total < 1.5:
            mud = ("Muddy")
            falls = ("Light-Moderate")
            falls_dry = ("Weak-Light")
            falls_wet = ("Moderate")
        if rain_total >= 1.5 and rain_total < 2:
            mud = ("Muddy")
            falls = ("Moderate")
            falls_dry = ("Light")
            falls_wet = ("Moderate-Strong")
        if rain_total >= 2 and rain_total < 3.5:
            mud = ("Very Muddy")
            falls = ("Moderate-Strong")
            falls_dry = ("Light-Moderate")
            falls_wet = ("Strong")
        if rain_total >= 3.5:
            mud = ("Very Muddy")
            falls = ("Strong")
            falls_dry = ("Moderate")
            falls_wet = ("Strong")
        return(mud, falls, falls_dry, falls_wet)

    nw_kauai_mud = (conditions(nw_kauai_total))[0]
    nw_kauai_falls = (conditions(nw_kauai_total))[1]

    n_kauai_mud = (conditions(n_kauai_total))[0]
    n_kauai_falls = (conditions(n_kauai_total))[1]

    central_mud = (conditions(central_total))[0]
    central_falls = (conditions(central_total))[1]

    ne_kauai_mud = (conditions(ne_kauai_total))[0]
    ne_kauai_falls = (conditions(ne_kauai_total))[1]

    moloaa_mud = (conditions(moloaa_total))[0]
    moloaa_falls = (conditions(moloaa_total))[1]

    wailua_mud = (conditions(wailua_total))[0]
    wailua_falls = (conditions(wailua_total))[1]

    se_kauai_mud = (conditions(se_kauai_total))[0]
    se_kauai_falls = (conditions(se_kauai_total))[1]

    s_kauai_mud = (conditions(s_kauai_total))[0]
    s_kauai_falls = (conditions(s_kauai_total))[1]

    waimea_mud = (conditions(waimea_total))[0]
    waimea_falls = (conditions(waimea_total))[1]


    return(nw_kauai_mud, nw_kauai_falls,
           n_kauai_mud, n_kauai_falls,
           central_mud, central_falls,
           ne_kauai_mud, ne_kauai_falls,
           moloaa_mud, moloaa_falls,
           wailua_mud, wailua_falls,
           se_kauai_mud, se_kauai_falls,
           s_kauai_mud, s_kauai_falls,
           waimea_mud, waimea_falls )

#all_conds = rain_calc()[0:20]
#return(all_conds)

conditions = (rain_calc())[0:19]
nw_kauai_mud = conditions[0]
nw_kauai_falls = conditions[1]
n_kauai_mud = conditions[2]
n_kauai_falls = conditions[3]
central_mud = conditions[4]
central_falls = conditions[5]
ne_kauai_mud = conditions[6]
ne_kauai_falls = conditions[7]
moloaa_mud = conditions[8]
moloaa_falls = conditions[9]
wailua_mud = conditions[10]
wailua_falls = conditions[11]
se_kauai_mud = conditions[12]
se_kauai_falls = conditions[13]
s_kauai_mud = conditions[14]
s_kauai_falls = conditions[15]
waimea_mud = conditions[16]
waimea_falls = conditions[17]

# ZONE FORECASTS
def zoneforecast(zone):
    res = requests.get('https://forecast.weather.gov/MapClick.php?zoneid='+zone+'')
    res.raise_for_status()
    bs4.BeautifulSoup(res.text, features='lxml')
    soup = bs4.BeautifulSoup(res.text, features='lxml')
    soup.find('#detailed-forecast-body > div:nth-child(1) > div.col-sm-2.forecast-label')

    def day(num):
        time_frame_slot = soup.select('#detailed-forecast-body > div:nth-child('+str(num)+') > div.col-sm-2.forecast-label')
        time_frame = str(time_frame_slot[0].text).strip()
        return(time_frame)
    valid_time1 = (day(1))
    valid_time2 = (day(2))
    valid_time3 = (day(3))
    valid_time4 = (day(4))
    valid_time5 = (day(5))

    def wxfcst(num):
        wx_slot = soup.select('#detailed-forecast-body > div:nth-child('+str(num)+') > div.col-sm-10.forecast-text')
        wx = str(wx_slot[0].text).strip()
        return(wx)
    wx1 = (wxfcst(1))
    wx2 = (wxfcst(2))
    wx3 = (wxfcst(3))
    wx4 = (wxfcst(4))
    wx5 = (wxfcst(5))

    return valid_time1, wx1, valid_time2, wx2, valid_time3, wx3, valid_time4, wx4, valid_time5, wx5

# Windward  Forecast Variables parsed
windward_fcst = (zoneforecast('HIZ002'))[0:10]
windward_vt1 = windward_fcst[0]
windward_wx1 = windward_fcst[1]
windward_vt2 = windward_fcst[2]
windward_wx2 = windward_fcst[3]
windward_vt3 = windward_fcst[4]
windward_wx3 = windward_fcst[5]
windward_vt4 = windward_fcst[6]
windward_wx4 = windward_fcst[7]
windward_vt5 = windward_fcst[8]
windward_wx5 = windward_fcst[9]

# Windward Forecasts by day string value
windward_fcst1 = (windward_vt1 + ': ' + windward_wx1)
windward_fcst2 = (windward_vt2 + ': ' + windward_wx2)
windward_fcst3 = (windward_vt3 + ': ' + windward_wx3)
windward_fcst4 = (windward_vt4 + ': ' + windward_wx4)
windward_fcst5 = (windward_vt5 + ': ' + windward_wx5)


# Mountains  Forecast Variables parsed
mountains_fcst = (zoneforecast('HIZ004'))[0:10]
mountains_vt1 = mountains_fcst[0]
mountains_wx1 = mountains_fcst[1]
mountains_vt2 = mountains_fcst[2]
mountains_wx2 = mountains_fcst[3]
mountains_vt3 = mountains_fcst[4]
mountains_wx3 = mountains_fcst[5]
mountains_vt4 = mountains_fcst[6]
mountains_wx4 = mountains_fcst[7]
mountains_vt5 = mountains_fcst[8]
mountains_wx5 = mountains_fcst[9]

# Mountains Forecasts by day string value
mountains_fcst1 = (mountains_vt1 + ': ' + mountains_wx1)
mountains_fcst2 = (mountains_vt2 + ': ' + mountains_wx2)
mountains_fcst3 = (mountains_vt3 + ': ' + mountains_wx3)
mountains_fcst4 = (mountains_vt4 + ': ' + mountains_wx4)
mountains_fcst5 = (mountains_vt5 + ': ' + mountains_wx5)

# Leeward Forecast Variables parsed
leeward_fcst = (zoneforecast('HIZ003'))[0:10]
leeward_vt1 = leeward_fcst[0]
leeward_wx1 = leeward_fcst[1]
leeward_vt2 = leeward_fcst[2]
leeward_wx2 = leeward_fcst[3]
leeward_vt3 = leeward_fcst[4]
leeward_wx3 = leeward_fcst[5]
leeward_vt4 = leeward_fcst[6]
leeward_wx4 = leeward_fcst[7]
leeward_vt5 = leeward_fcst[8]
leeward_wx5 = leeward_fcst[9]

# Leeward Forecasts by day string value
leeward_fcst1 = (leeward_vt1 + ': ' + leeward_wx1)
leeward_fcst2 = (leeward_vt2 + ': ' + leeward_wx2)
leeward_fcst3 = (leeward_vt3 + ': ' + leeward_wx3)
leeward_fcst4 = (leeward_vt4 + ': ' + leeward_wx4)
leeward_fcst5 = (leeward_vt5 + ': ' + leeward_wx5)


#########################

kauai = Blueprint('kauai', __name__)

@kauai.route('/kauai')
def kauaiinfo():
    info = "Hikeit Hawaii"
    summary = "Hawaii's Hiking Weather...Trail Conditions...and Waterfalls"
    island = "Kauai"

    dawn = lih_dawn
    sunrise = lih_sr
    sunset = lih_ss
    dusk = lih_dusk
    moon_phase = moon

    zone1 = "Windward/North/NorthWest"

    windward_ob_wx = phli_weather
    windward_ob_temp = phli_temp+"℉"
    windward_ob_wind = "Wind: "+phli_wind

    zone1_fcst1 = windward_fcst1
    zone1_fcst2 = windward_fcst2
    zone1_fcst3 = windward_fcst3
    zone1_fcst4 = windward_fcst4
    zone1_fcst5 = windward_fcst5

    nw_kauai = "Koke'e / Na Pali Kona / Waimea Canyon"
    nw_kauai_hikes1 = "Awa'awapuhi Trail - Waipoo - Waimea Canyon - Paaiki"
    nw_kauai_mud1 = "Conditions: " + nw_kauai_mud
    nw_kauai_falls1 = "Waterfalls Flowing: " + nw_kauai_falls

    n_kauai = "Na Pali"
    n_kauai_hikes1 = "Na Pali Coast - Hoolea Falls - Hanakapai Falls - Limahuli Falls"
    n_kauai_mud1 = "Conditions: " + n_kauai_mud
    n_kauai_falls1 = "Waterfalls Flowing: " + n_kauai_falls

    ne_kauai = "Hanalei / Princeville"
    ne_kauai_hikes1 = "Okolehao - Princeville Botanical Garden - Wai Koa Loop - Kilauea Falls - Kauapea - Na Aina Kai Botanical Gardens"
    ne_kauai_mud1 = "Conditions: " + ne_kauai_mud
    ne_kauai_falls1 = "Waterfalls Flowing: " + ne_kauai_falls

    moloaa = "Moloaa"
    moloaa_hikes1 = "Opae Falls"
    moloaa_mud1 = "Conditions: " + moloaa_mud
    moloaa_falls1 = "Waterfalls Flowing: " + moloaa_falls

    wailua = "Wailua / Kapaa"
    wailua_hikes1 = "Wailua - Sleeping Giant - Kaholalele - Hoopii - Makaleha - Kapakaiki"
    wailua_mud1 = "Conditions: " + wailua_mud
    wailua_falls1 = "Waterfalls Flowing: " + wailua_falls

    s_kauai = "South Kauai"
    s_kauai_hikes1 = "Ooiki - Kaukiuki - Waiolue"
    s_kauai_mud1 = "Conditions: " + s_kauai_mud
    s_kauai_falls1 = "Waterfalls Flowing: " + s_kauai_falls

    zone2 = "Mountains (Central)"

    windward_ob_wx = phli_weather
    windward_ob_temp = phli_temp+"℉"
    windward_ob_wind = "Wind: "+phli_wind

    zone2_fcst1 = mountains_fcst1
    zone2_fcst2 = mountains_fcst2
    zone2_fcst3 = mountains_fcst3
    zone2_fcst4 = mountains_fcst4
    zone2_fcst5 = mountains_fcst5

    central_kauai = "Mt. Waialeale"
    central_hikes1 = "Hinalele - Puwainui - Waianuenue - Kahili, Hali'i - Manawaiopuna (Jurassic Park Falls)"
    central_mud1 = "Conditions: " + central_mud
    central_falls1 = "Waterfalls Flowing: " + central_falls

    zone3 = "Leeward"

    leeward_ob_wx = phbk_weather
    leeward_ob_temp = phbk_temp+"℉"
    leeward_ob_wind = "Wind: "+phbk_wind

    zone3_fcst1 = leeward_fcst1
    zone3_fcst2 = leeward_fcst2
    zone3_fcst3 = leeward_fcst3
    zone3_fcst4 = leeward_fcst4
    zone3_fcst5 = leeward_fcst5

    leeward_kauai = "Leeward"
    leeward_hikes1 = "Red Dirt Waterfall"
    leeward_mud1 = "Conditions: " + waimea_mud
    leeward_falls1 = "Waterfalls Flowing: " + waimea_falls

    return render_template('kauaiv2.html',**locals())
