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

hnl_sr_ss = sr_ss("Honolulu", 21.315603, -157.858093)
hnl_dawn = hnl_sr_ss[0]
hnl_sr   = hnl_sr_ss[1]
hnl_ss   = hnl_sr_ss[2]
hnl_dusk = hnl_sr_ss[3]

#**************************************** OAHU *******************************************************
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

# Kaneohe Observations
phng_observation = observations('PHNG')[0:6]
phng_date = phng_observation[0]
phng_time = phng_observation[1]
phng_wind = phng_observation[2]
phng_weather = phng_observation[3]
phng_temp = phng_observation[4]
phng_heat_index = phng_observation[5]

# Wahiawa Observations
phhi_observation = observations('PHHI')[0:6]
phhi_date = phhi_observation[0]
phhi_time = phhi_observation[1]
phhi_wind = phhi_observation[2]
phhi_weather = phhi_observation[3]
phhi_temp = phhi_observation[4]
phhi_heat_index = phhi_observation[5]

# Honolulu Observations
phnl_observation = observations('PHNL')[0:6]
phnl_date = phnl_observation[0]
phnl_time = phnl_observation[1]
phnl_wind = phnl_observation[2]
phnl_weather = phnl_observation[3]
phnl_temp = phnl_observation[4]
phnl_heat_index = phnl_observation[5]

# Kalaeloa Observations
phjr_observation = observations('PHJR')[0:6]
phjr_date = phjr_observation[0]
phjr_time = phjr_observation[1]
phjr_wind = phjr_observation[2]
phjr_weather = phjr_observation[3]
phjr_temp = phjr_observation[4]
phjr_heat_index = phjr_observation[5]


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
    oahu_index_start = description1_list.index('Oahu')
    oahu_index_end = description1_list.index('Molokai')
    oahu_section = (description1_list[oahu_index_start:oahu_index_end])
    return(oahu_section)

oahu_section1 = pull_request(day_one_obs)
oahu_section2 = pull_request(day_two_obs)

def rain_stations(day_num_obs):
    if day_num_obs == day_one_obs:
        oahu_section = oahu_section1
    elif day_num_obs == day_two_obs:
        oahu_section = oahu_section2

    def day_sections(num):
        ##OAHU
        ##Windward/Mauka Sites
        KAHH1 = oahu_section[oahu_section.index('KAHH1') + num-1]
        KTAH1 = oahu_section[oahu_section.index('KTAH1') + num+1]
        KFWH1 = oahu_section[oahu_section.index('KFWH1') + num-1]
        PUNH1 = oahu_section[oahu_section.index('PUNH1') + num+1]
        PNSH1 = oahu_section[oahu_section.index('PNSH1') + num+1]
        KNRH1 = oahu_section[oahu_section.index('KNRH1') + num]
        HAKH1 = oahu_section[oahu_section.index('HAKH1') + num+1]
        WPPH1 = oahu_section[oahu_section.index('WPPH1') + num+1]
        WHSH1 = oahu_section[oahu_section.index('WHSH1') + num]
        OFRH1 = oahu_section[oahu_section.index('OFRH1') + num+2]
        AHUH1 = oahu_section[oahu_section.index('AHUH1') + num+1]#
        #HNG = oahu_section[oahu_section.index('HNG') + 5]########
        LULH1 = oahu_section[oahu_section.index('LULH1') + num]#
        NUUH1 = oahu_section[oahu_section.index('NUUH1') + num+1]
        MNLH1 = oahu_section[oahu_section.index('MNLH1') + num+2]
        STVH1 = oahu_section[oahu_section.index('STVH1') + num+1]
        MAUH1 = oahu_section[oahu_section.index('MAUH1') + num]
        OFSH1 = oahu_section[oahu_section.index('OFSH1') + num+1]
        WMLH1 = oahu_section[oahu_section.index('WMLH1') + num]
        BELH1 = oahu_section[oahu_section.index('BELH1') + num]
        KMHH1 = oahu_section[oahu_section.index('KMHH1') + num]
        HAJH1 = oahu_section[oahu_section.index('HAJH1') + num+3]

        ##Leeward/Central Sites
        NIUH1 = oahu_section[oahu_section.index('NIUH1') + num+1]
        PFSH1 = oahu_section[oahu_section.index('PFSH1') + num+2]
        ALOH1 = oahu_section[oahu_section.index('ALOH1') + num+1]
        HNL   = oahu_section[oahu_section.index('HNL') + num]
        MOAH1 = oahu_section[oahu_section.index('MOAH1') + num]
        MOGH1 = oahu_section[oahu_section.index('MOGH1') + num+1]
        TNLH1 = oahu_section[oahu_section.index('TNLH1') + num+1]
        PACH1 = oahu_section[oahu_section.index('PACH1') + num]
        WAWH1 = oahu_section[oahu_section.index('WAWH1') + num+1]
        MITH1 = oahu_section[oahu_section.index('MITH1') + num]
        SCBH1 = oahu_section[oahu_section.index('SCBH1') + num]
        SCEH1 = oahu_section[oahu_section.index('SCEH1') + num]
        WAFH1 = oahu_section[oahu_section.index('WAFH1') + num]
        POAH1 = oahu_section[oahu_section.index('POAH1') + num]
        #KWLH1 = oahu_section[oahu_section.index('KWLH1') + num-1]
        KMRH1 = oahu_section[oahu_section.index('KMRH1') + num+1]
        PPRH1 = oahu_section[oahu_section.index('PPRH1') + num+1]
        PMHH1 = oahu_section[oahu_section.index('PMHH1') + num+2]
        DLGH1 = oahu_section[oahu_section.index('DLGH1') + num-1]
        PECH1 = oahu_section[oahu_section.index('PECH1') + num]
        KUNH1 = oahu_section[oahu_section.index('KUNH1') + num+1]
        WWFH1 = oahu_section[oahu_section.index('WWFH1') + num-1]
        HOFH1 = oahu_section[oahu_section.index('HOFH1') + num-1]
        PTWH1 = oahu_section[oahu_section.index('PTWH1') + num+3]
        HJR   = oahu_section[oahu_section.index('HJR') + num]
        PLHH1 = oahu_section[oahu_section.index('PLHH1') + num-1]
        LUAH1 = oahu_section[oahu_section.index('LUAH1') + num]
        WNVH1 = oahu_section[oahu_section.index('WNVH1') + num]
        WBHH1 = oahu_section[oahu_section.index('WBHH1') + num+1]
        WAIH1 = oahu_section[oahu_section.index('WAIH1') + num]
        MKHH1 = oahu_section[oahu_section.index('MKHH1') + num+1]
        MKRH1 = oahu_section[oahu_section.index('MKRH1') + num]
        MKGH1 = oahu_section[oahu_section.index('MKGH1') + num]
        MAPH1 = oahu_section[oahu_section.index('MAPH1') + num]
        KKRH1 = oahu_section[oahu_section.index('KKRH1') + num-1]
        END_oahu = oahu_section[oahu_section.index(':Island') - 2]

        return(
                KAHH1, KTAH1, KFWH1, PUNH1, PNSH1, KNRH1, HAKH1, WPPH1,
                WHSH1, OFRH1, AHUH1, LULH1, NUUH1, MNLH1, STVH1,
                MAUH1, OFSH1, WMLH1, BELH1, KMHH1, HAJH1,

                NIUH1, PFSH1, ALOH1,
                HNL, MOAH1, MOGH1, TNLH1, PACH1, WAWH1, MITH1, SCBH1,
                SCEH1, WAFH1, POAH1, KMRH1, PPRH1, PMHH1, DLGH1,
                PECH1, KUNH1, WWFH1, HOFH1, PTWH1, HJR, PLHH1,
                LUAH1, WNVH1, WBHH1, WAIH1, MKHH1, MKRH1, MKGH1, MAPH1, KKRH1

                )

    # num = 5
    all_03 = day_sections(5)
    all_06 = day_sections(7)
    all_12 = day_sections(9)
    all_24 = day_sections(11)

    return(all_03, all_06, all_12, all_24)

all_obs1 = rain_stations(day_one_obs)
all_obs2 = rain_stations(day_two_obs)

all_obs1_03 = (list(all_obs1[0])[0:59])
all_obs1_06 = (list(all_obs1[1])[0:59])
all_obs1_12 = (list(all_obs1[2])[0:59])
all_obs1_24 = (list(all_obs1[3])[0:59])

all_obs2_03 = (list(all_obs2[0])[0:59])
all_obs2_06 = (list(all_obs2[1])[0:59])
all_obs2_12 = (list(all_obs2[2])[0:59])
all_obs2_24 = (list(all_obs2[3])[0:59])
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

#OAHU
KAHH1 = (sort_locations(0))
KTAH1 = (sort_locations(1))
KFWH1 = (sort_locations(2))
PUNH1 = (sort_locations(3))
PNSH1 = (sort_locations(4))

KNRH1 = (sort_locations(5))
HAKH1 = (sort_locations(6))
WPPH1 = (sort_locations(7))
WHSH1 = (sort_locations(8))
OFRH1 = (sort_locations(9))

AHUH1 = (sort_locations(10))
#HNG   = (sort_locations(37))
LULH1 = (sort_locations(11))
NUUH1 = (sort_locations(12))
MNLH1 = (sort_locations(13))

STVH1 = (sort_locations(14))
MAUH1 = (sort_locations(15))
OFSH1 = (sort_locations(16))
WMLH1 = (sort_locations(17))
BELH1 = (sort_locations(18))

KMHH1 = (sort_locations(19))
HAJH1 = (sort_locations(20))
##Leeward/Central Sites
NIUH1 = (sort_locations(21))
PFSH1 = (sort_locations(22))
ALOH1 = (sort_locations(23))

HNL   = (sort_locations(24))
MOAH1 = (sort_locations(25))
MOGH1 = (sort_locations(26))
TNLH1 = (sort_locations(27))
PACH1 = (sort_locations(28))

WAWH1 = (sort_locations(29))
MITH1 = (sort_locations(30))
SCBH1 = (sort_locations(31))
SCEH1 = (sort_locations(32))
WAFH1 = (sort_locations(33))

POAH1 = (sort_locations(34))
#KWLH1 = (sort_locations(35))
KMRH1 = (sort_locations(35))
PPRH1 = (sort_locations(36))
PMHH1 = (sort_locations(37))

DLGH1 = (sort_locations(38))
PECH1 = (sort_locations(39))
KUNH1 = (sort_locations(40))
WWFH1 = (sort_locations(41))
HOFH1 = (sort_locations(42))

PTWH1 = (sort_locations(43))
HJR   = (sort_locations(44))
PLHH1 = (sort_locations(45))
LUAH1 = (sort_locations(46))
WNVH1 = (sort_locations(47))

WBHH1 = (sort_locations(48))
WAIH1 = (sort_locations(49))
MKHH1 = (sort_locations(50))
MKRH1 = (sort_locations(51))
MKGH1 = (sort_locations(52))

MAPH1 = (sort_locations(53))
KKRH1 = (sort_locations(54))


def rain_calc():
    laie_total = float( PUNH1 + PNSH1 + (KTAH1) / 2 )
    punaluu_total = float( (PUNH1 + PNSH1 + KNRH1) / 3 )
    kahana_total = float( KNRH1 )
    kualoa_total = float( (KNRH1 + HAKH1) / 2)
    waiahole_total = float( (HAKH1 + WPPH1 + WHSH1 + AHUH1) / 4 )
    kaneohe_total = float( (LULH1 + TNLH1) / 2 )
    olomana_total = float( (OFSH1 + WMLH1 + BELH1) / 3 )
    maunawili_total = float( MAUH1 + .05 )
    likeke_total = float( (LULH1 + NUUH1 + MAUH1) / 3 )
    waipuhia_total = float( (LULH1 + NUUH1) / 2 )
    manana_waimano_ridge_total = float( PACH1 / 2)
    manana_waimano_falls_total = float( (WAWH1 + PACH1) / 2)
    poamoho_total = ( (POAH1 + PMHH1 + SCEH1) / 3 )
    manoa_total = float( MNLH1 )
    palolo_total = float( PFSH1 )
    kuliouou_total = float( NIUH1 )
    jackass_lulumahu_total = float( NUUH1 )
    kapena_total = float( (STVH1 + ALOH1) / 2 )
    pupukea_total = float( (KMRH1 + PPRH1) / 3 )
    haleiwa_total = float( (KMRH1 + PMHH1) / 3 )
    makapuu_total = float( HAJH1 + (KMHH1 * .25))
    #kaena_total = float( ( DLGH1 + MKRH1 + MKGH1 + MAPH1) / 4)
    kaena_total = float( KKRH1 )
    makaha_total = float( (WNVH1 + WBHH1 + WAIH1 + MKHH1
                            + MKRH1 + MKGH1 + MAPH1) / 7)
    nanakuli_total = float( (PLHH1 + WNVH1 + WBHH1 + WAIH1 + HOFH1 ) / 5)
    makakilo_total = float( (PLHH1 + LUAH1 + HJR + HOFH1) / 4)
    kolekole_total = float( (SCBH1 + WAFH1) / 3 )
    diamond_head_total = float( (NIUH1 + PFSH1 * .5) / 3 )
    koko_total = float( (HAJH1 + NIUH1 + KMHH1 - .15) / 3 )
    moanalua_total = float( (MOAH1 + MOGH1) / 2 )
    aiea_total = float( (TNLH1 + MOAH1 + MOGH1) / 3 )

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
            mud = ("Muddy")
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
            mud = ("Very Muddy")
            falls = ("Light-Moderate")
            falls_dry = ("Weak-Light")
            falls_wet = ("Moderate")
        if rain_total >= 1.5 and rain_total < 2:
            mud = ("Very Muddy")
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

    laie_mud = (conditions(laie_total))[0]
    laie_falls1 = (conditions(laie_total))[1]
    laie_falls2 = (conditions(laie_total))[2]
    laie_falls3 = (conditions(laie_total))[3]

    punaluu_mud = (conditions(punaluu_total))[0]
    punaluu_falls1 = (conditions(punaluu_total))[1]
    punaluu_falls2 = (conditions(punaluu_total))[2]
    punaluu_falls3 = (conditions(punaluu_total))[3]

    kahana_mud = (conditions(kahana_total))[0]
    kahana_falls1 = (conditions(kahana_total))[1]
    kahana_falls2 = (conditions(kahana_total))[2]
    kahana_falls3 = (conditions(kahana_total))[3]

    kualoa_mud = (conditions(kualoa_total))[0]
    kualoa_falls1 = (conditions(kualoa_total))[1]
    kualoa_falls2 = (conditions(kualoa_total))[2]
    kualoa_falls3 = (conditions(kualoa_total))[3]

    waiahole_mud = (conditions(waiahole_total))[0]
    waiahole_falls1 = (conditions(waiahole_total))[1]
    waiahole_falls2 = (conditions(waiahole_total))[2]
    waiahole_falls3 = (conditions(waiahole_total))[3]

    olomana_mud = (conditions(olomana_total))[0]
    olomana_falls1 = (conditions(olomana_total))[1]
    olomana_falls2 = (conditions(olomana_total))[2]
    olomana_falls3 = (conditions(olomana_total))[3]

    maunawili_mud = (conditions(maunawili_total))[0]
    maunawili_falls1 = (conditions(maunawili_total))[1]
    maunawili_falls2 = (conditions(maunawili_total))[2]
    maunawili_falls3 = (conditions(maunawili_total))[3]

    likeke_mud = (conditions(likeke_total))[0]
    likeke_falls1 = (conditions(likeke_total))[1]
    likeke_falls2 = (conditions(likeke_total))[2]
    likeke_falls3 = (conditions(likeke_total))[3]

    waipuhia_mud = (conditions(waipuhia_total))[0]
    waipuhia_falls1 = (conditions(waipuhia_total))[1]
    waipuhia_falls2 = (conditions(waipuhia_total))[2]
    waipuhia_falls3 = (conditions(waipuhia_total))[3]

    manana_waimano_ridge_mud = (conditions(manana_waimano_ridge_total))[0]
    manana_waimano_ridge_falls1 = (conditions(manana_waimano_ridge_total))[1]
    #manana_waimano_ridge_falls2 = (conditions(manana_waimano_ridge_total))[2]
    #manana_waimano_ridge_falls3 = (conditions(manana_waimano_ridge_total))[3]

    manana_waimano_falls_mud = (conditions(manana_waimano_falls_total))[0]
    manana_waimano_falls1 = (conditions(manana_waimano_falls_total))[1]
    manana_waimano_falls2 = (conditions(manana_waimano_falls_total))[2]
    manana_waimano_falls3 = (conditions(manana_waimano_falls_total))[3]

    poamoho_mud = (conditions(poamoho_total))[0]
    poamoho_falls1 = (conditions(poamoho_total))[1]
    poamoho_falls2 = (conditions(poamoho_total))[2]
    poamoho_falls3 = (conditions(poamoho_total))[3]

    manoa_mud = (conditions(manoa_total))[0]
    manoa_falls1 = (conditions(manoa_total))[1]
    manoa_falls2 = (conditions(manoa_total))[2]
    manoa_falls3 = (conditions(manoa_total))[3]

    palolo_mud = (conditions(palolo_total))[0]
    palolo_falls1 = (conditions(palolo_total))[1]
    palolo_falls2 = (conditions(palolo_total))[2]
    palolo_falls3 = (conditions(palolo_total))[3]

    kuliouou_mud = (conditions(kuliouou_total))[0]
    kuliouou_falls1 = (conditions(kuliouou_total))[1]
    kuliouou_falls2 = (conditions(kuliouou_total))[2]
    kuliouou_falls3 = (conditions(kuliouou_total))[3]

    jackass_lulumahu_mud = (conditions(jackass_lulumahu_total))[0]
    jackass_lulumahu_falls1 = (conditions(jackass_lulumahu_total))[1]
    jackass_lulumahu_falls2 = (conditions(jackass_lulumahu_total))[2]
    jackass_lulumahu_falls3 = (conditions(jackass_lulumahu_total))[3]

    kapena_mud = (conditions(kapena_total))[0]
    kapena_falls1 = (conditions(kapena_total))[1]
    kapena_falls2 = (conditions(kapena_total))[2]
    kapena_falls3 = (conditions(kapena_total))[3]

    pupukea_mud = (conditions(pupukea_total))[0]
    pupukea_falls1 = (conditions(pupukea_total))[1]
    pupukea_falls2 = (conditions(pupukea_total))[2]
    pupukea_falls3 = (conditions(pupukea_total))[3]

    haleiwa_mud = (conditions(haleiwa_total))[0]
    haleiwa_falls1 = (conditions(haleiwa_total))[1]
    haleiwa_falls2 = (conditions(haleiwa_total))[2]
    haleiwa_falls3 = (conditions(haleiwa_total))[3]

    makapuu_mud = (conditions(makapuu_total))[0]
    makapuu_falls1 = (conditions(makapuu_total))[1]
    makapuu_falls2 = (conditions(makapuu_total))[2]
    makapuu_falls3 = (conditions(makapuu_total))[3]

    kaena_mud = (conditions(kaena_total))[0]
    kaena_falls1 = (conditions(kaena_total))[1]
    kaena_falls2 = (conditions(kaena_total))[2]
    kaena_falls3 = (conditions(kaena_total))[3]

    makaha_mud = (conditions(makaha_total))[0]
    makaha_falls1 = (conditions(makaha_total))[1]
    makaha_falls2 = (conditions(makaha_total))[2]
    makaha_falls3 = (conditions(makaha_total))[3]

    nanakuli_mud = (conditions(nanakuli_total))[0]
    nanakuli_falls1 = (conditions(nanakuli_total))[1]
    nanakuli_falls2 = (conditions(nanakuli_total))[2]
    nanakuli_falls3 = (conditions(nanakuli_total))[3]

    makakilo_mud = (conditions(makakilo_total))[0]
    makakilo_falls1 = (conditions(makakilo_total))[1]
    makakilo_falls2 = (conditions(makakilo_total))[2]
    makakilo_falls3 = (conditions(makakilo_total))[3]

    kolekole_mud = (conditions(kolekole_total))[0]
    kolekole_falls1 = (conditions(kolekole_total))[1]
    kolekole_falls2 = (conditions(kolekole_total))[2]
    kolekole_falls3 = (conditions(kolekole_total))[3]

    diamond_head_mud = (conditions(diamond_head_total))[0]
    diamond_head_falls1 = (conditions(diamond_head_total))[1]
    diamond_head_falls2 = (conditions(diamond_head_total))[2]
    diamond_head_falls3 = (conditions(diamond_head_total))[3]

    koko_mud = (conditions(koko_total))[0]
    koko_falls1 = (conditions(koko_total))[1]
    koko_falls2 = (conditions(koko_total))[2]
    koko_falls3 = (conditions(koko_total))[3]

    moanalua_mud = (conditions(moanalua_total))[0]
    moanalua_falls1 = (conditions(moanalua_total))[1]
    moanalua_falls2 = (conditions(moanalua_total))[2]
    moanalua_falls3 = (conditions(moanalua_total))[3]

    aiea_mud = (conditions(aiea_total))[0]
    aiea_falls1 = (conditions(aiea_total))[1]
    aiea_falls2 = (conditions(aiea_total))[2]
    aiea_falls3 = (conditions(aiea_total))[3]

    kaneohe_mud = (conditions(kaneohe_total))[0]
    kaneohe_falls1 = (conditions(kaneohe_total))[1]
    kaneohe_falls2 = (conditions(kaneohe_total))[2]
    kaneohe_falls3 = (conditions(kaneohe_total))[3]


    return(laie_mud, laie_falls3,
           waiahole_mud, waiahole_falls3,
           olomana_mud, olomana_falls1,
           maunawili_mud, maunawili_falls3,
           waipuhia_mud, waipuhia_falls1,
           manana_waimano_ridge_mud, manana_waimano_ridge_falls1,
           waipuhia_mud, waipuhia_falls1,
           manana_waimano_falls_mud, manana_waimano_falls1,
           manoa_mud, manoa_falls3,
           kuliouou_mud, kuliouou_falls3,
           jackass_lulumahu_mud, jackass_lulumahu_falls1,
           kapena_mud, kapena_falls1,
           pupukea_mud, pupukea_falls3,
           makapuu_mud, makapuu_falls1,
           makaha_mud, makaha_falls1,
           kolekole_mud, kolekole_falls1,
           diamond_head_mud, diamond_head_falls1,
           kualoa_mud, kualoa_falls1,
           likeke_mud, likeke_falls3,
           palolo_mud, palolo_falls1,
           nanakuli_mud, nanakuli_falls1,
           makakilo_mud, makakilo_falls1,
           kaena_mud, kaena_falls1,
           poamoho_mud, poamoho_falls1,
           haleiwa_mud, haleiwa_falls1,
           koko_mud, koko_falls1,
           moanalua_mud, moanalua_falls1,
           kaneohe_mud, kaneohe_falls2,
           aiea_mud, aiea_falls1,
           punaluu_mud, punaluu_falls3,
           kahana_mud, kahana_falls3,
           kualoa_mud, kualoa_falls3)



conditions = (rain_calc())[0:70]
laie_mud = conditions[0]
laie_falls = conditions[1]
waiahole_mud = conditions[2]
waiahole_falls = conditions[3]
olomana_mud = conditions[4]
olomana_falls = conditions[5]
maunawili_mud = conditions[6]
maunawili_falls = conditions[7]
waipuhia_mud = conditions[8]
waipuhia_falls = conditions[9]
manana_waimano_ridge_mud = conditions[10]
manana_waimano_ridge_falls = conditions[11]
waipuhia_mud = conditions[12]
waipuhia_falls = conditions[13]
manana_waimano_falls_mud = conditions[14]
manana_waimano_falls = conditions[15]
manoa_mud = conditions[16]
manoa_falls = conditions[17]
kuliouou_mud = conditions[18]
kuliouou_falls = conditions[19]
jackass_lulumahu_mud = conditions[20]
jackass_lulumahu_falls = conditions[21]
kapena_mud = conditions[22]
kapena_falls = conditions[23]
pupukea_mud = conditions[24]
pupukea_falls = conditions[25]
makapuu_mud = conditions[26]
makapuu_falls = conditions[27]
makaha_mud = conditions[28]
makaha_falls = conditions[29]
kolekole_mud = conditions[30]
kolekole_falls = conditions[31]
diamond_head_mud = conditions[32]
diamond_head_falls = conditions[33]
kualoa_mud = conditions[34]
kualoa_falls = conditions[35]
likeke_mud = conditions[36]
likeke_falls = conditions[37]
palolo_mud = conditions[38]
palolo_falls = conditions[39]
nanakuli_mud = conditions[40]
nanakuli_falls = conditions[41]
makakilo_mud = conditions[42]
makakilo_falls = conditions[43]
kaena_mud = conditions[44]
kaena_falls = conditions[45]
poamoho_mud = conditions[46]
poamoho_falls = conditions[47]
haleiwa_mud = conditions[48]
haleiwa_falls = conditions[49]
koko_mud = conditions[50]
koko_falls = conditions[51]
moanalua_mud = conditions[52]
moanalua_falls = conditions[53]
kaneohe_mud = conditions[54]
kaneohe_falls = conditions[55]
aiea_mud = conditions[56]
aiea_falls = conditions[57]
punaluu_mud = conditions[58]
punaluu_falls = conditions[59]
kahana_mud = conditions[60]
kahana_falls = conditions[61]
kualoa_mud = conditions[62]
kualoa_falls = conditions[63]


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

# Koolau Forecast Variables parsed
koolau_fcst = (zoneforecast('HIZ035'))[0:10]
koolau_vt1 = koolau_fcst[0]
koolau_wx1 = koolau_fcst[1]
koolau_vt2 = koolau_fcst[2]
koolau_wx2 = koolau_fcst[3]
koolau_vt3 = koolau_fcst[4]
koolau_wx3 = koolau_fcst[5]
koolau_vt4 = koolau_fcst[6]
koolau_wx4 = koolau_fcst[7]
koolau_vt5 = koolau_fcst[8]
koolau_wx5 = koolau_fcst[9]

# Koolau Forecasts by day string value
koolau_fcst1 = (koolau_vt1 + ': ' + koolau_wx1)
koolau_fcst2 = (koolau_vt2 + ': ' + koolau_wx2)
koolau_fcst3 = (koolau_vt3 + ': ' + koolau_wx3)
koolau_fcst4 = (koolau_vt4 + ': ' + koolau_wx4)
koolau_fcst5 = (koolau_vt5 + ': ' + koolau_wx5)


# Waianae Forecast Variables parsed
waianae_fcst = (zoneforecast('HIZ011'))[0:10]
waianae_vt1 = waianae_fcst[0]
waianae_wx1 = waianae_fcst[1]
waianae_vt2 = waianae_fcst[2]
waianae_wx2 = waianae_fcst[3]
waianae_vt3 = waianae_fcst[4]
waianae_wx3 = waianae_fcst[5]
waianae_vt4 = waianae_fcst[6]
waianae_wx4 = waianae_fcst[7]
waianae_vt5 = waianae_fcst[8]
waianae_wx5 = waianae_fcst[9]

# Waianae Forecasts by day string value
waianae_fcst1 = (waianae_vt1 + ': ' + waianae_wx1)
waianae_fcst2 = (waianae_vt2 + ': ' + waianae_wx2)
waianae_fcst3 = (waianae_vt3 + ': ' + waianae_wx3)
waianae_fcst4 = (waianae_vt4 + ': ' + waianae_wx4)
waianae_fcst5 = (waianae_vt5 + ': ' + waianae_wx5)


# South Oahu (Dimanond Head / Koko Head) Forecast Variables parsed
south_oahu_fcst = (zoneforecast('HIZ033'))[0:10]
south_oahu_vt1 = south_oahu_fcst[0]
south_oahu_wx1 = south_oahu_fcst[1]
south_oahu_vt2 = south_oahu_fcst[2]
south_oahu_wx2 = south_oahu_fcst[3]
south_oahu_vt3 = south_oahu_fcst[4]
south_oahu_wx3 = south_oahu_fcst[5]
south_oahu_vt4 = south_oahu_fcst[6]
south_oahu_wx4 = south_oahu_fcst[7]
south_oahu_vt5 = south_oahu_fcst[8]
south_oahu_wx5 = south_oahu_fcst[9]

# South Oahu (Dimanond Head / Koko Head) Forecasts by day string value
south_oahu_fcst1 = (south_oahu_vt1 + ': ' + south_oahu_wx1)
south_oahu_fcst2 = (south_oahu_vt2 + ': ' + south_oahu_wx2)
south_oahu_fcst3 = (south_oahu_vt3 + ': ' + south_oahu_wx3)
south_oahu_fcst4 = (south_oahu_vt4 + ': ' + south_oahu_wx4)
south_oahu_fcst5 = (south_oahu_vt5 + ': ' + south_oahu_wx5)

# Webpage Variables
oahu = Blueprint('oahu', __name__)

@oahu.route('/oahu')
def oahuinfo():
    info = "Hikeit Hawaii"
    summary = "Hawaii's Hiking Weather...Trail Conditions...and Waterfalls"
    island = "Oahu"

    dawn = hnl_dawn
    sunrise = hnl_sr
    sunset = hnl_ss
    dusk = hnl_dusk
    moon_phase = moon

    # Koolau's
    zone1 = "Ko'olau Windward"

    windward_ob_wx = phng_weather
    windward_ob_temp = phng_temp+"℉"
    windward_ob_wind = "Wind: "+phng_wind

    zone1_fcst1 = koolau_fcst1
    zone1_fcst2 = koolau_fcst2
    zone1_fcst3 = koolau_fcst3
    zone1_fcst4 = koolau_fcst4
    zone1_fcst5 = koolau_fcst5

    laie = "Ko'olauloa (Laie)"
    laie_hikes = "Laie Falls/Summit - Malaekahana Falls - Wailele Falls  - Koloa Gulch"
    laie_mud1 = "Conditions: " + laie_mud
    laie_falls1 = "Waterfalls Flowing: " + laie_falls

    punaluu = "Ko'olauloa (Hau'ula / Punalu'u)"
    punaluu_hikes = "Hau'ula Loop/Ridge - Seven Falls (Ma'akua Gulch) - Sacred Falls(Closed)"
    punaluu_mud1 = "Conditions: " + punaluu_mud
    punaluu_falls1 = "Waterfalls Flowing: " + punaluu_falls

    kahana = "Ko'olauloa (Kahana)"
    kahana_hikes = "Kahana"
    kahana_mud1 = "Conditions: " + kahana_mud
    kahana_falls1 = "Waterfalls Flowing: " + kahana_falls

    kualoa = "Ko'olauloa (Ka'a'awa)"
    kualoa_hikes1 = "Crouching Lion - Makaua Falls - Kualoa"
    kualoa_mud1 = "Conditions: " + kualoa_mud
    kualoa_falls1 = "Waterfalls Flowing: " + kualoa_falls

    waiahole = "Ko'olaupoko (Kaneohe Area)"
    waiahole_hikes = "Hamama Falls - Puu Maelieli"
    waiahole_mud1 = "Conditions: " + waiahole_mud
    waiahole_falls1 = "Waterfalls Flowing: " + waiahole_falls

    kaneohe_hikes1 = "Haiku Stairs (Stairway to Heaven) - 1000 Falls (Haiku)"
    kaneohe_mud1 = "Conditions: " + kaneohe_mud
    kaneohe_falls1 = "Waterfalls Flowing: " + kaneohe_falls

    #olomana = "Olomana"
    olomana_hikes1 = "Likeke Falls"
    olomana_mud1 = "Conditions: " + likeke_mud
    olomana_falls1 = "Waterfalls Flowing: " + likeke_falls

    olomana_hikes2 = "Old Pali Rd.(Paved) - Pali Puka/Lookout"
    olomana_mud2 = "Conditions: " + likeke_mud

    olomana_hikes3 = "Waipuhia"
    olomana_mud3 = "Conditions: " + waipuhia_mud
    olomana_falls3 = "Waterfalls Flowing: " + waipuhia_falls

    olomana_hikes4 = "Maunawili"
    olomana_mud4 = "Conditions: " + maunawili_mud
    olomana_falls4 = "Waterfalls Flowing: " + maunawili_falls

    olomana_hikes5 = "Kailua Pillbox"
    olomana_mud5 = "Conditions: " + olomana_mud

    makapuu = "Makapu'u Lighthouse - Tom Tom Trail"
    makapuu_mud1 = "Conditions: " + makapuu_mud


    zone2 = "Ko'olau Leeward/Central-North"

    central_ob_wx = phhi_weather
    central_ob_temp = phhi_temp+"℉"
    central_ob_wind = "Wind: "+phhi_wind

    zone2_fcst1 = koolau_fcst1 # Need to change by adding Central Zone Forecast
    zone2_fcst2 = koolau_fcst2
    zone2_fcst3 = koolau_fcst3
    zone2_fcst4 = koolau_fcst4
    zone2_fcst5 = koolau_fcst5

    koolau_central_hikes1 = "Poamoho Ridge - Wahiawa Hills - Schofield Waikane"
    koolau_central_mud1 = "Conditions: " + poamoho_mud
    koolau_central_falls1 = "Waterfalls Flowing: " + poamoho_falls

    koolau_central_hikes2 = "Wahiawa Botanical Garden - Kukaniloko Birthstones"
    koolau_central_mud2 = "Conditions: " + kolekole_mud
    koolau_central_falls2 = "Waterfalls Flowing: " + kolekole_falls

    koolau_central_hikes3 = "Manana Ridge - Waimano Loop"
    koolau_central_mud3 = "Conditions: " + manana_waimano_ridge_mud
    koolau_central_falls3 = "Waterfalls Flowing: " + manana_waimano_ridge_falls

    koolau_central_hikes4 = "Waimano Falls"
    koolau_central_mud4 = "Conditions: " + manana_waimano_falls_mud
    koolau_central_falls4 = "Waterfalls Flowing: " + manana_waimano_falls

    koolau_north_hikes1 = "Ehukai Pillbox/Secret/Jungle Trails"
    koolau_north_mud1 = "Conditions: " + pupukea_mud
    koolau_north_falls1 = "Waterfalls Flowing: " + pupukea_falls

    koolau_north_hikes2 = "Waimea Falls(Paved) - Pupukea-Paumalu Trail - Kaunala Trail  - Pupukea Summit"
    koolau_north_mud2 = "Conditions: " + pupukea_mud
    koolau_north_falls2 = "Waterfalls Flowing: " + pupukea_falls

    koolau_north_hikes3 = "Kawailoa - Kawai'iki"
    koolau_north_mud3 = "Conditions: " + haleiwa_mud
    koolau_north_falls3 = "Waterfalls Flowing: " + haleiwa_falls


    zone3 = "Ko'olau Leeward/South"

    south_ob_wx = phnl_weather
    south_ob_temp = phnl_temp+"℉"
    south_ob_wind = "Wind: "+phnl_wind

    zone3_fcst1 = koolau_fcst1
    zone3_fcst2 = koolau_fcst2
    zone3_fcst3 = koolau_fcst3
    zone3_fcst4 = koolau_fcst4
    zone3_fcst5 = koolau_fcst5

    koolau_south_hikes1 = "Manoa Falls"
    koolau_south_mud1 = "Conditions: " + manoa_mud
    koolau_south_falls1 = "Waterfalls Flowing: " + manoa_falls

    koolau_south_hikes2 = "Ka'au Crater"
    koolau_south_mud2 = "Conditions: " + palolo_mud
    koolau_south_falls2 = "Waterfalls Flowing: " + palolo_falls

    koolau_south_hikes3 = "Kuliouou Ridge/Valley - Wiliwilinui Ridge"
    koolau_south_mud3 = "Conditions: " + kuliouou_mud
    koolau_south_falls3 = "Waterfalls Flowing: " + kuliouou_falls

    koolau_south_hikes4 = "Judd Trail(Ginger Pool) - Lulumahu Falls"
    koolau_south_mud4 = "Conditions: " + jackass_lulumahu_mud
    koolau_south_falls4 = "Waterfalls Flowing: " + jackass_lulumahu_falls

    koolau_south_hikes5 = "Kapena Falls"
    koolau_south_mud5 = "Conditions: " + kapena_mud
    koolau_south_falls5 = "Waterfalls Flowing: " + kapena_falls

    koolau_south_hikes6 = "Moanalua Ridge/Valley - Tripler Ridge - Bowman Trail"
    koolau_south_mud6 = "Conditions: " + moanalua_mud
    koolau_south_falls6 = "Waterfalls Flowing: " + moanalua_falls

    koolau_south_hikes7 = "Aiea Loop"
    koolau_south_mud7 = "Conditions: " + aiea_mud
    koolau_south_falls7 = "Waterfalls Flowing: " + aiea_falls




    # South Oahu Popular Hikes
    zone4 = "Diamond Head / Koko Head"

    south_ob_wx = phnl_weather
    south_ob_temp = phnl_temp+"℉"
    south_ob_wind = "Wind: "+phnl_wind

    zone4_fcst1 = south_oahu_fcst1
    zone4_fcst2 = south_oahu_fcst2
    zone4_fcst3 = south_oahu_fcst3
    zone4_fcst4 = south_oahu_fcst4
    zone4_fcst5 = south_oahu_fcst5

    dh_mud1 = "Conditions: " + diamond_head_mud
    kh_mud1 = "Conditions: " + koko_mud

    # Waianae Range
    zone5 = "Waianae Range"

    leeward_ob_wx = phjr_weather
    leeward_ob_temp = phjr_temp+"℉"
    leeward_ob_wind = "Wind: "+phjr_wind

    zone5_fcst1 = waianae_fcst1
    zone5_fcst2 = waianae_fcst2
    zone5_fcst3 = waianae_fcst3
    zone5_fcst4 = waianae_fcst4
    zone5_fcst5 = waianae_fcst5

    waianae_hikes1 = "Ka'ena Pt - Kuaokala Trail"
    waianae_mud1 = "Conditions: " + kaena_mud

    waianae_hikes2 = "Makua Kea'au - Pu'u Kea'au - Kamaileunu Ridge - Ohikilolo Ridge - Ka'ala Trail"
    waianae_mud2 = "Conditions: " + makaha_mud

    waianae_hikes3 = "Pu'u O Hulu (Maili/Pink Pillboxes)"
    waianae_mud3 = "Conditions: " + nanakuli_mud

    waianae_hikes4 = "Makakilo Gulch - Camp Palehua"
    waianae_mud4 = "Conditions: " + makakilo_mud

    kolekole_hikes = "Kolekole Pass - Pu'u Haupapa"
    kolekole_mud1 = "Conditions: " + kolekole_mud

    return render_template('oahuv2.html',**locals())
