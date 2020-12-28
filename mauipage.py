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

kahu_sr_ss = sr_ss("Kahului", 20.888033, -156.46785)
kahu_dawn = kahu_sr_ss[0]
kahu_sr   = kahu_sr_ss[1]
kahu_ss   = kahu_sr_ss[2]
kahu_dusk = kahu_sr_ss[3]

#**************************************** MAUI *******************************************************
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

# Kahului Observations
phog_observation = observations('PHOG')[0:6]
phog_date = phog_observation[0]
phog_time = phog_observation[1]
phog_wind = phog_observation[2]
phog_weather = phog_observation[3]
phog_temp = phog_observation[4]
phog_heat_index = phog_observation[5]

# Lahaina Observations
phjh_observation = observations('PHJH')[0:6]
phjh_date = phjh_observation[0]
phjh_time = phjh_observation[1]
phjh_wind = phjh_observation[2]
phjh_weather = phjh_observation[3]
phjh_temp = phjh_observation[4]
phjh_heat_index = phjh_observation[5]

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
    maui_index_start = description1_list.index('Maui')
    maui_index_end = description1_list.index('UPLH1') - 1
    maui_section = (description1_list[maui_index_start:maui_index_end])
    return(maui_section)

maui_section1 = pull_request(day_one_obs)
maui_section2 = pull_request(day_two_obs)

def rain_stations(day_num_obs):
    if day_num_obs == day_one_obs:
        maui_section = maui_section1
    elif day_num_obs == day_two_obs:
        maui_section = maui_section2

    def day_sections(num):
        ##MAUI
        ##Windward/Mauka Sites
        HNAH1 = maui_section[maui_section.index('HNAH1') + num]
        WWKH1 = maui_section[maui_section.index('WWKH1') + num+1]
        AIKH1 = maui_section[maui_section.index('AIKH1') + num]
        HOG   = maui_section[maui_section.index('HOG') + num]
        WUKH1 = maui_section[maui_section.index('WUKH1') + num]
        KHKH1 = maui_section[maui_section.index('KHKH1') + num]
        PKKH1 = maui_section[maui_section.index('PKKH1') + num+1]
        ##Leeward/Upcountry Sites
        KPGH1 = maui_section[maui_section.index('KPGH1') + num]
        KPNH1 = maui_section[maui_section.index('KPNH1') + num]
        PUKH1 = maui_section[maui_section.index('PUKH1') + num]
        KBSH1 = maui_section[maui_section.index('KBSH1') + num+2]
        KLFH1 = maui_section[maui_section.index('KLFH1') + num]
        ULUH1 = maui_section[maui_section.index('ULUH1') + num]
        KHIH1 = maui_section[maui_section.index('KHIH1') + num+1]
        KPDH1 = maui_section[maui_section.index('KPDH1') + num+1]
        WCCH1 = maui_section[maui_section.index('WCCH1') + num+1]
        P36   = maui_section[maui_section.index('P36') + num]
        LAHH1 = maui_section[maui_section.index('LAHH1') + num]
        MABH1 = maui_section[maui_section.index('MABH1') + num]


        return(
                HNAH1, WWKH1, AIKH1, HOG, WUKH1, KHKH1, PKKH1, KPGH1,
                KPNH1, PUKH1, KBSH1, KLFH1, ULUH1, KHIH1, KPDH1, WCCH1,
                P36, LAHH1, MABH1,

                )
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

##MAUI
##Windward/Mauka Sites
HNAH1 = (sort_locations(0))
WWKH1 = (sort_locations(1))
AIKH1 = (sort_locations(2))
HOG   = (sort_locations(3))

WUKH1 = (sort_locations(4))
KHKH1 = (sort_locations(5))
PKKH1 = (sort_locations(6))
##Leeward/Upcountry Sites
KPGH1 = (sort_locations(7))

KPNH1 = (sort_locations(8))
PUKH1 = (sort_locations(9))
KBSH1 = (sort_locations(10))
KLFH1 = (sort_locations(11))
ULUH1 = (sort_locations(12))
KHIH1 = (sort_locations(13))

KPDH1 = (sort_locations(14))
WCCH1 = (sort_locations(15))
P36   = (sort_locations(16))
LAHH1 = (sort_locations(17))
MABH1 = (sort_locations(18))

def rain_calc():
    hana_total = float( HNAH1 )
    wailuaiki_total = float( WWKH1 )
    haiku_total = float( AIKH1 )
    kahului_total = float( HOG )
    wailuku_total = float( (WUKH1 + HOG + WCCH1 + KHKH1) / 4 )
    kahakuloa_total = float( KHKH1 )

    kaupo_gap_total = float( KPGH1 )
    kepuni_total = float( KPNH1 )
    pukalani_total = float( PUKH1 )
    kula_total = float( KBSH1 + KLFH1 )
    ulupalakua_total = float( ULUH1 )
    kihei_total = float( KHIH1 )
    maalaea_total = float( KPDH1 + P36 )
    waikapu_total = float( WCCH1 )
    lahaina_total = float( LAHH1 )

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

    hana_mud = (conditions(hana_total))[0]
    hana_falls = (conditions(hana_total))[1]

    wailuaiki_mud = (conditions(wailuaiki_total))[0]
    wailuaiki_falls = (conditions(wailuaiki_total))[1]

    haiku_mud = (conditions(haiku_total))[0]
    haiku_falls = (conditions(haiku_total))[1]

    kahului_mud = (conditions(kahului_total))[0]
    kahului_falls = (conditions(kahului_total))[1]

    wailuku_mud = (conditions(wailuku_total))[0]
    wailuku_falls = (conditions(wailuku_total))[1]

    kahakuloa_mud = (conditions(kahakuloa_total))[0]
    kahakuloa_falls = (conditions(kahakuloa_total))[1]

    kaupo_gap_mud = (conditions(kaupo_gap_total))[0]
    kaupo_gap_falls = (conditions(kaupo_gap_total))[1]

    kepuni_mud = (conditions(kepuni_total))[0]
    kepuni_falls = (conditions(kepuni_total))[1]

    pukalani_mud = (conditions(pukalani_total))[0]
    pukalani_falls = (conditions(pukalani_total))[1]

    kula_mud = (conditions(kula_total))[0]
    kula_falls = (conditions(kula_total))[1]

    ulupalakua_mud = (conditions(ulupalakua_total))[0]
    ulupalakua_falls = (conditions(ulupalakua_total))[1]

    kihei_mud = (conditions(kihei_total))[0]
    kihei_falls = (conditions(kihei_total))[1]

    maalaea_mud = (conditions(maalaea_total))[0]
    maalaea_falls = (conditions(maalaea_total))[1]

    waikapu_mud = (conditions(waikapu_total))[0]
    waikapu_falls = (conditions(waikapu_total))[1]

    lahaina_mud = (conditions(lahaina_total))[0]
    lahaina_falls = (conditions(lahaina_total))[1]

    return(hana_mud, hana_falls,
           wailuaiki_mud, wailuaiki_falls,
           haiku_mud, haiku_falls,
           kahului_mud, kahului_falls,
           wailuku_mud, wailuku_falls,
           kahakuloa_mud, kahakuloa_falls,
           kaupo_gap_mud, kaupo_gap_falls,
           kepuni_mud, kepuni_falls,
           pukalani_mud, pukalani_falls,
           kula_mud, kula_falls,
           ulupalakua_mud, ulupalakua_falls,
           kihei_mud, kihei_falls,
           maalaea_mud, maalaea_falls,
           waikapu_mud, waikapu_falls,
           lahaina_mud, lahaina_falls)

#all_conds = rain_calc()[0:31]
#return(all_conds)

conditions = (rain_calc())[0:37]
n_hana_mud = conditions[0]
n_hana_falls = conditions[1]
wailuaiki_mud = conditions[2]
wailuaiki_falls = conditions[3]
haiku_mud = conditions[4]
haiku_falls = conditions[5]
kahului_mud = conditions[6]
kahului_falls = conditions[7]
wailuku_mud = conditions[8]
wailuku_falls = conditions[9]
kahakuloa_mud = conditions[10]
kahakuloa_falls = conditions[11]
kaupo_gap_mud = conditions[12]
kaupo_gap_falls = conditions[13]
kepuni_mud = conditions[14]
kepuni_falls = conditions[15]
pukalani_mud = conditions[16]
pukalani_falls = conditions[17]
kula_mud = conditions[18]
kula_falls = conditions[19]
ulupalakua_mud = conditions[20]
ulupalakua_falls = conditions[21]
kihei_mud = conditions[22]
kihei_falls = conditions[23]
maalaea_mud = conditions[24]
maalaea_falls = conditions[25]
waikapu_mud = conditions[26]
waikapu_falls = conditions[27]
lahaina_mud = conditions[28]
lahaina_falls = conditions[29]


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

# Windward Haleakala  Forecast Variables parsed
windward_haleakala_fcst = (zoneforecast('HIZ020'))[0:10]
windward_haleakala_vt1 = windward_haleakala_fcst[0]
windward_haleakala_wx1 = windward_haleakala_fcst[1]
windward_haleakala_vt2 = windward_haleakala_fcst[2]
windward_haleakala_wx2 = windward_haleakala_fcst[3]
windward_haleakala_vt3 = windward_haleakala_fcst[4]
windward_haleakala_wx3 = windward_haleakala_fcst[5]
windward_haleakala_vt4 = windward_haleakala_fcst[6]
windward_haleakala_wx4 = windward_haleakala_fcst[7]
windward_haleakala_vt5 = windward_haleakala_fcst[8]
windward_haleakala_wx5 = windward_haleakala_fcst[9]

# Windward Haleakala Forecasts by day string value
windward_haleakala_fcst1 = (windward_haleakala_vt1 + ': ' + windward_haleakala_wx1)
windward_haleakala_fcst2 = (windward_haleakala_vt2 + ': ' + windward_haleakala_wx2)
windward_haleakala_fcst3 = (windward_haleakala_vt3 + ': ' + windward_haleakala_wx3)
windward_haleakala_fcst4 = (windward_haleakala_vt4 + ': ' + windward_haleakala_wx4)
windward_haleakala_fcst5 = (windward_haleakala_vt5 + ': ' + windward_haleakala_wx5)

# Haleakala Summit  Forecast Variables parsed
haleakala_summit_fcst = (zoneforecast('HIZ022'))[0:10]
haleakala_summit_vt1 = haleakala_summit_fcst[0]
haleakala_summit_wx1 = haleakala_summit_fcst[1]
haleakala_summit_vt2 = haleakala_summit_fcst[2]
haleakala_summit_wx2 = haleakala_summit_fcst[3]
haleakala_summit_vt3 = haleakala_summit_fcst[4]
haleakala_summit_wx3 = haleakala_summit_fcst[5]
haleakala_summit_vt4 = haleakala_summit_fcst[6]
haleakala_summit_wx4 = haleakala_summit_fcst[7]
haleakala_summit_vt5 = haleakala_summit_fcst[8]
haleakala_summit_wx5 = haleakala_summit_fcst[9]

# Haleakala Summit Forecasts by day string value
haleakala_summit_fcst1 = (haleakala_summit_vt1 + ': ' + haleakala_summit_wx1)
haleakala_summit_fcst2 = (haleakala_summit_vt2 + ': ' + haleakala_summit_wx2)
haleakala_summit_fcst3 = (haleakala_summit_vt3 + ': ' + haleakala_summit_wx3)
haleakala_summit_fcst4 = (haleakala_summit_vt4 + ': ' + haleakala_summit_wx4)
haleakala_summit_fcst5 = (haleakala_summit_vt5 + ': ' + haleakala_summit_wx5)

# Leeward Haleakala  Forecast Variables parsed
leeward_haleakala_fcst = (zoneforecast('HIZ021'))[0:10]
leeward_haleakala_vt1 = leeward_haleakala_fcst[0]
leeward_haleakala_wx1 = leeward_haleakala_fcst[1]
leeward_haleakala_vt2 = leeward_haleakala_fcst[2]
leeward_haleakala_wx2 = leeward_haleakala_fcst[3]
leeward_haleakala_vt3 = leeward_haleakala_fcst[4]
leeward_haleakala_wx3 = leeward_haleakala_fcst[5]
leeward_haleakala_vt4 = leeward_haleakala_fcst[6]
leeward_haleakala_wx4 = leeward_haleakala_fcst[7]
leeward_haleakala_vt5 = leeward_haleakala_fcst[8]
leeward_haleakala_wx5 = leeward_haleakala_fcst[9]

# Leeward Haleakala Forecasts by day string value
leeward_haleakala_fcst1 = (leeward_haleakala_vt1 + ': ' + leeward_haleakala_wx1)
leeward_haleakala_fcst2 = (leeward_haleakala_vt2 + ': ' + leeward_haleakala_wx2)
leeward_haleakala_fcst3 = (leeward_haleakala_vt3 + ': ' + leeward_haleakala_wx3)
leeward_haleakala_fcst4 = (leeward_haleakala_vt4 + ': ' + leeward_haleakala_wx4)
leeward_haleakala_fcst5 = (leeward_haleakala_vt5 + ': ' + leeward_haleakala_wx5)

# Windward West Maui  Forecast Variables parsed
windward_west_fcst = (zoneforecast('HIZ017'))[0:10]
windward_west_vt1 = windward_west_fcst[0]
windward_west_wx1 = windward_west_fcst[1]
windward_west_vt2 = windward_west_fcst[2]
windward_west_wx2 = windward_west_fcst[3]
windward_west_vt3 = windward_west_fcst[4]
windward_west_wx3 = windward_west_fcst[5]
windward_west_vt4 = windward_west_fcst[6]
windward_west_wx4 = windward_west_fcst[7]
windward_west_vt5 = windward_west_fcst[8]
windward_west_wx5 = windward_west_fcst[9]

# Windward West Maui Forecasts by day string value
windward_west_fcst1 = (windward_west_vt1 + ': ' + windward_west_wx1)
windward_west_fcst2 = (windward_west_vt2 + ': ' + windward_west_wx2)
windward_west_fcst3 = (windward_west_vt3 + ': ' + windward_west_wx3)
windward_west_fcst4 = (windward_west_vt4 + ': ' + windward_west_wx4)
windward_west_fcst5 = (windward_west_vt5 + ': ' + windward_west_wx5)

# Leeward West Maui  Forecast Variables parsed
leeward_west_fcst = (zoneforecast('HIZ018'))[0:10]
leeward_west_vt1 = leeward_west_fcst[0]
leeward_west_wx1 = leeward_west_fcst[1]
leeward_west_vt2 = leeward_west_fcst[2]
leeward_west_wx2 = leeward_west_fcst[3]
leeward_west_vt3 = leeward_west_fcst[4]
leeward_west_wx3 = leeward_west_fcst[5]
leeward_west_vt4 = leeward_west_fcst[6]
leeward_west_wx4 = leeward_west_fcst[7]
leeward_west_vt5 = leeward_west_fcst[8]
leeward_west_wx5 = leeward_west_fcst[9]

# Leeward West Maui Forecasts by day string value
leeward_west_fcst1 = (leeward_west_vt1 + ': ' + leeward_west_wx1)
leeward_west_fcst2 = (leeward_west_vt2 + ': ' + leeward_west_wx2)
leeward_west_fcst3 = (leeward_west_vt3 + ': ' + leeward_west_wx3)
leeward_west_fcst4 = (leeward_west_vt4 + ': ' + leeward_west_wx4)
leeward_west_fcst5 = (leeward_west_vt5 + ': ' + leeward_west_wx5)

#########################

maui = Blueprint('maui', __name__)

@maui.route('/maui')
def mauiinfo():
    info = "Hikeit Hawaii"
    summary = "Hawaii's Hiking Weather...Trail Conditions...and Waterfalls"
    island = "Maui"

    dawn = kahu_dawn
    sunrise = kahu_sr
    sunset = kahu_ss
    dusk = kahu_dusk
    moon_phase = moon

    zone1 = "Windward Haleakala"
    # Lookup Hana Airport observations
    windward_haleakala_wx = phog_weather
    windward_haleakala_temp = phog_temp+"℉"
    windward_haleakala_wind = "Wind: "+phog_wind

    zone1_fcst1 = windward_haleakala_fcst1
    zone1_fcst2 = windward_haleakala_fcst2
    zone1_fcst3 = windward_haleakala_fcst3
    zone1_fcst4 = windward_haleakala_fcst4
    zone1_fcst5 = windward_haleakala_fcst5

    hana = "Hana"
    hana_hikes1 = "Wailua - Paihi - Kanahuali'i - Waimoku - Pools at Ohe'o - Makahiku"
    hana_mud1 = "Conditions: " + wailuaiki_mud
    hana_falls1 = "Waterfalls Flowing: " + wailuaiki_falls

    hana_road = "Road to Hana"
    hana_hikes2 = "Twin Falls - Haipua'ena - Upper Waikani - Kopiliula - Pua'a Ka'a - Hanawi - Makapipi"
    hana_mud2 = "Conditions: " + n_hana_mud
    hana_falls2 = "Waterfalls Flowing: " + n_hana_falls

    haiku = "Haiku"
    haiku_hikes1 = "Alelele - Waiohiwi - Lower Puohokamoa"
    haiku_mud1 = "Conditions: " + haiku_mud
    haiku_falls1 = "Waterfalls Flowing: " + haiku_falls


    zone2 = "Haleakala Summit"
    zone2_fcst1 = haleakala_summit_fcst1
    zone2_fcst2 = haleakala_summit_fcst2
    zone2_fcst3 = haleakala_summit_fcst3
    zone2_fcst4 = haleakala_summit_fcst4
    zone2_fcst5 = haleakala_summit_fcst5


    zone3 = "Leeward Haleakala"
    zone3_fcst1 = leeward_haleakala_fcst1
    zone3_fcst2 = leeward_haleakala_fcst2
    zone3_fcst3 = leeward_haleakala_fcst3
    zone3_fcst4 = leeward_haleakala_fcst4
    zone3_fcst5 = leeward_haleakala_fcst5

    zone4 = "Windward West"

    windward_west_ob_wx = phog_weather
    windward_west_ob_temp = phog_temp+"℉"
    windward_west_ob_wind = "Wind: "+phog_wind

    zone4_fcst1 = windward_west_fcst1
    zone4_fcst2 = windward_west_fcst2
    zone4_fcst3 = windward_west_fcst3
    zone4_fcst4 = windward_west_fcst4
    zone4_fcst5 = windward_west_fcst5

    iao_valley = "Windward West"
    iao_hikes = "Secret Trail - Iao Needle - Kapilau - Honokohau - Makamaka'ole"
    iao_mud = "Conditions: " + wailuku_mud
    iao_falls = "Waterfalls Flowing: " + wailuku_falls


    zone5 = "Leeward West"

    leeward_west_ob_wx = phjh_weather
    leeward_west_ob_temp = phjh_temp+"℉"
    leeward_west_ob_wind = "Wind: "+phjh_wind

    zone5_fcst1 = leeward_west_fcst1
    zone5_fcst2 = leeward_west_fcst2
    zone5_fcst3 = leeward_west_fcst3
    zone5_fcst4 = leeward_west_fcst4
    zone5_fcst5 = leeward_west_fcst5

    lahaina = "Lahaina"
    lahaina_hikes = "Kahana"
    lahaina_mud1 = "Conditions: " + lahaina_mud
    lahaina_falls1 = "Waterfalls Flowing: " + lahaina_falls

    return render_template('mauiv2.html',**locals())
