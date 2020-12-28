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

hilo_sr_ss = sr_ss("Hilo", 19.71924, -155.08185)
hilo_dawn = hilo_sr_ss[0]
hilo_sr   = hilo_sr_ss[1]
hilo_ss   = hilo_sr_ss[2]
hilo_dusk = hilo_sr_ss[3]

#print(sr_ss('Big Island Summits', 19.8236111, -155.4708333))

kona_sr_ss = sr_ss("Kailua-Kona", 19.639994, -155.996933)
kona_dawn = kona_sr_ss[0]
kona_sr   = kona_sr_ss[1]
kona_ss   = kona_sr_ss[2]
kona_dusk = kona_sr_ss[3]

#**************************************** BIG ISLAND *******************************************************
# OBSERVATIONS
#
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

# Hilo Observations
phto_observation = observations('PHTO')[0:6]
phto_date = phto_observation[0]
phto_time = phto_observation[1]
phto_wind = phto_observation[2]
phto_weather = phto_observation[3]
phto_temp = phto_observation[4]
phto_heat_index = phto_observation[5]

# Bradshaw Observations
phsf_observation = observations('PHSF')[0:6]
phsf_date = phsf_observation[0]
phsf_time = phsf_observation[1]
phsf_wind = phsf_observation[2]
phsf_weather = phsf_observation[3]
phsf_temp = phsf_observation[4]
phsf_heat_index = phsf_observation[5]

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
    hawaii_index_start = description1_list.index('UPLH1') - 1
    hawaii_index_end = description1_list.index('.END')
    hawaii_section = (description1_list[hawaii_index_start:hawaii_index_end])

    return(hawaii_section)

hawaii_section1 = pull_request(day_one_obs)
hawaii_section2 = pull_request(day_two_obs)

def rain_stations(day_num_obs):
    if day_num_obs == day_one_obs:
        hawaii_section = hawaii_section1
    elif day_num_obs == day_two_obs:
        hawaii_section = hawaii_section2

    def day_sections(num):
        ##BIG ISLAND
        ##Windward Sites
        UPLH1 = hawaii_section[hawaii_section.index('UPLH1') + num]
        KWSH1 = hawaii_section[hawaii_section.index('KWSH1') + num+1]
        KUUH1 = hawaii_section[hawaii_section.index('KUUH1') + num+1]
        KMUH1 = hawaii_section[hawaii_section.index('KMUH1') + num]
        HNKH1 = hawaii_section[hawaii_section.index('HNKH1') + num-1]
        PMLH1 = hawaii_section[hawaii_section.index('PMLH1') + num]
        LPHH1 = hawaii_section[hawaii_section.index('LPHH1') + num]
        HKUH1 = hawaii_section[hawaii_section.index('HKUH1') + num+1]
        PPWH1 = hawaii_section[hawaii_section.index('PPWH1') + num+1]
        SDQH1 = hawaii_section[hawaii_section.index('SDQH1') + num+1]
        PIIH1 = hawaii_section[hawaii_section.index('PIIH1') + num]
        WKAH1 = hawaii_section[hawaii_section.index('WKAH1') + num+1]
        WEXH1 = hawaii_section[hawaii_section.index('WEXH1') + num+1]
        HTO   = hawaii_section[hawaii_section.index('HTO') + num]
        PHAH1 = hawaii_section[hawaii_section.index('PHAH1') + num]
        MTVH1 = hawaii_section[hawaii_section.index('MTVH1') + num+1]
        GLNH1 = hawaii_section[hawaii_section.index('GLNH1') + num]
        KNWH1 = hawaii_section[hawaii_section.index('KNWH1') + num+1]

        ##Leeward Sites
        MOBH1 = hawaii_section[hawaii_section.index('MOBH1') + num+2]
        KKUH1 = hawaii_section[hawaii_section.index('KKUH1') + num-1]
        KMOH1 = hawaii_section[hawaii_section.index('KMOH1') + num-1]
        PLIH1 = hawaii_section[hawaii_section.index('PLIH1') + num]
        KPRH1 = hawaii_section[hawaii_section.index('KPRH1') + num]
        KAYH1 = hawaii_section[hawaii_section.index('KAYH1') + num+1]
        PPLH1 = hawaii_section[hawaii_section.index('PPLH1') + num]
        NENH1 = hawaii_section[hawaii_section.index('NENH1') + num]
        SOPH1 = hawaii_section[hawaii_section.index('SOPH1') + num]
        LKHH1 = hawaii_section[hawaii_section.index('LKHH1') + num]
        KRCH1 = hawaii_section[hawaii_section.index('KRCH1') + num]
        PHRH1 = hawaii_section[hawaii_section.index('PHRH1') + num]
        HAUH1 = hawaii_section[hawaii_section.index('HAUH1') + num]
        KLEH1 = hawaii_section[hawaii_section.index('KLEH1') + num]
        WIHH1 = hawaii_section[hawaii_section.index('WIHH1') + num]
        KHOH1 = hawaii_section[hawaii_section.index('KHOH1') + num-1]
        HKO   = hawaii_section[hawaii_section.index('HKO') + num+1]
        KIRH1 = hawaii_section[hawaii_section.index('KIRH1') + num+1]
        KPLH1 = hawaii_section[hawaii_section.index('KPLH1') + num-1]
        PULH1 = hawaii_section[hawaii_section.index('PULH1') + num-1]
        PWWH1 = hawaii_section[hawaii_section.index('PWWH1') + num]
        PKAH1 = hawaii_section[hawaii_section.index('PKAH1') + num+1]
        PKWH1 = hawaii_section[hawaii_section.index('PKWH1') + num]
        PKMH1 = hawaii_section[hawaii_section.index('PKMH1') + num]
        AHMH1 = hawaii_section[hawaii_section.index('AHMH1') + num-1]
        WHIH1 = hawaii_section[hawaii_section.index('WHIH1') + num]
        WKVH1 = hawaii_section[hawaii_section.index('WKVH1') + num-1]
        PERH1 = hawaii_section[hawaii_section.index('PERH1') + num]
        KHRH1 = hawaii_section[hawaii_section.index('KHRH1') + num]
        KASH1 = hawaii_section[hawaii_section.index('KASH1') + num+1]

        return(
                UPLH1, KWSH1, KUUH1, KMUH1, HNKH1, PMLH1, LPHH1, HKUH1,
                PPWH1, SDQH1, PIIH1, WKAH1, WEXH1, HTO, PHAH1, MTVH1,
                GLNH1, KNWH1,

                MOBH1, KKUH1, KMOH1, PLIH1, KPRH1, KAYH1, PPLH1, NENH1,
                SOPH1, LKHH1, KRCH1, PHRH1, HAUH1, KLEH1, WIHH1, KHOH1,
                HKO, KIRH1, KPLH1, PULH1, PWWH1, PKAH1, PKWH1, PKMH1,
                AHMH1, WHIH1, WKVH1, PERH1, KHRH1, KASH1

                )
    # num = 5
    all_03 = day_sections(5)
    all_06 = day_sections(7)
    all_12 = day_sections(9)
    all_24 = day_sections(11)

    return(all_03, all_06, all_12, all_24)

all_obs1 = rain_stations(day_one_obs)
all_obs2 = rain_stations(day_two_obs)

all_obs1_03 = (list(all_obs1[0])[0:50])
all_obs1_06 = (list(all_obs1[1])[0:50])
all_obs1_12 = (list(all_obs1[2])[0:50])
all_obs1_24 = (list(all_obs1[3])[0:50])

all_obs2_03 = (list(all_obs2[0])[0:50])
all_obs2_06 = (list(all_obs2[1])[0:50])
all_obs2_12 = (list(all_obs2[2])[0:50])
all_obs2_24 = (list(all_obs2[3])[0:50])
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

##BIG ISLAND
##Windward Sites
UPLH1 = (sort_locations(0))
KWSH1 = (sort_locations(1))
KUUH1 = (sort_locations(2))
KMUH1 = (sort_locations(3))
HNKH1 = (sort_locations(4))

PMLH1 = (sort_locations(5))
LPHH1 = (sort_locations(6))
HKUH1 = (sort_locations(7))
PPWH1 = (sort_locations(8))
SDQH1 = (sort_locations(9))

PIIH1 = (sort_locations(10))
WKAH1 = (sort_locations(11))
WEXH1 = (sort_locations(12))
HTO   = (sort_locations(13))
PHAH1 = (sort_locations(14))

MTVH1 = (sort_locations(15))
GLNH1 = (sort_locations(16))
KNWH1 = (sort_locations(17))
##Leeward Sites
MOBH1 = (sort_locations(18))
KKUH1 = (sort_locations(19))

KMOH1 = (sort_locations(20))
PLIH1 = (sort_locations(21))
KPRH1 = (sort_locations(22))
KAYH1 = (sort_locations(23))
PPLH1 = (sort_locations(24))

NENH1 = (sort_locations(25))
SOPH1 = (sort_locations(26))
LKHH1 = (sort_locations(27))
KRCH1 = (sort_locations(28))
PHRH1 = (sort_locations(29))

HAUH1 = (sort_locations(30))
KLEH1 = (sort_locations(31))
WIHH1 = (sort_locations(32))
KHOH1 = (sort_locations(33))
HKO   = (sort_locations(34))

KIRH1 = (sort_locations(35))
KPLH1 = (sort_locations(36))
PULH1 = (sort_locations(37))
PWWH1 = (sort_locations(38))
PKAH1 = (sort_locations(39))

PKWH1 = (sort_locations(40))
PKMH1 = (sort_locations(41))
AHMH1 = (sort_locations(42))
WHIH1 = (sort_locations(43))
WKVH1 = (sort_locations(44))
PERH1 = (sort_locations(45))
KHRH1 = (sort_locations(46))
KASH1 = (sort_locations(47))

def rain_calc():
    hawi_total = float( UPLH1 )
    waipio_total = float( KWSH1 )
    waimea_total = float( KUUH1 + KMUH1 / 2) # KMUH1
    honokaa_total = float( (HNKH1 + PMLH1) / 2 )
    laupahoehoe_total = float( LPHH1 )
    hakalau_total = float( HKUH1 )
    papaiku_total = float( PPWH1 )
    hilo_total = float((SDQH1 + PIIH1 + HTO ) / 3 )
    maunaloa_summit_total = float(( MOBH1 + WKAH1 + KKUH1 ) / 3 )
    s_hilo_total = float( WEXH1 )
    pahoa_total = float( PHAH1 )
    mtn_view_total = float( MTVH1 + GLNH1 )
    volcano_total = float( (LPHH1 + KMOH1 + PLIH1 + KPRH1 + KAYH1) / 5 )
    kau_total = float( (PPLH1 + NENH1) / 2 )
    s_big_isle_total = float( (SOPH1 + LKHH1 + KRCH1) / 3)
    kona_total = float((PHRH1 + HAUH1 + KLEH1 + WIHH1 + KHOH1 + HKO + KIRH1 + KPLH1) / 8 )
    n_kona_total = float((PULH1 + PWWH1) / 2 )
    pohakuloa_total = float((PKAH1 + PKWH1 + PKMH1) / 3 )
    leeward_maunakea_total = float((AHMH1 + WHIH1) / 2 )
    waikoloa_total = float((WKVH1 + PERH1) / 2 )
    kohala_total = float((KHRH1 + KUUH1 + KMUH1) / 3 ) #KMUH1

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

    hawi_mud = (conditions(hawi_total))[0]
    hawi_falls = (conditions(hawi_total))[1]

    waipio_mud = (conditions(waipio_total))[0]
    waipio_falls = (conditions(waipio_total))[1]

    waimea_mud = (conditions(waimea_total))[0]
    waimea_falls = (conditions(waimea_total))[1]

    honokaa_mud = (conditions(honokaa_total))[0]
    honokaa_falls = (conditions(honokaa_total))[1]

    laupahoehoe_mud = (conditions(laupahoehoe_total))[0]
    laupahoehoe_falls = (conditions(laupahoehoe_total))[1]

    hakalau_mud = (conditions(hakalau_total))[0]
    hakalau_falls = (conditions(hakalau_total))[1]

    papaiku_mud = (conditions(papaiku_total))[0]
    papaiku_falls = (conditions(papaiku_total))[1]

    hilo_mud = (conditions(hilo_total))[0]
    hilo_falls = (conditions(hilo_total))[1]

    maunaloa_summit_mud = (conditions(maunaloa_summit_total))[0]
    maunaloa_summit_falls = (conditions(maunaloa_summit_total))[1]

    s_hilo_mud = (conditions(s_hilo_total))[0]
    s_hilo_falls = (conditions(s_hilo_total))[1]

    pahoa_mud = (conditions(pahoa_total))[0]
    pahoa_falls = (conditions(pahoa_total))[1]

    mtn_view_mud = (conditions(mtn_view_total))[0]
    mtn_view_falls = (conditions(mtn_view_total))[1]

    volcano_mud = (conditions(volcano_total))[0]
    volcano_falls = (conditions(volcano_total))[1]

    kau_mud = (conditions(kau_total))[0]
    kau_falls = (conditions(kau_total))[1]

    s_big_isle_mud = (conditions(s_big_isle_total))[0]
    s_big_isle_falls = (conditions(s_big_isle_total))[1]

    kona_mud = (conditions(kona_total))[0]
    kona_falls = (conditions(kona_total))[1]

    n_kona_mud = (conditions(n_kona_total))[0]
    n_kona_falls = (conditions(n_kona_total))[1]

    pohakuloa_mud = (conditions(pohakuloa_total))[0]
    pohakuloa_falls = (conditions(pohakuloa_total))[1]

    leeward_maunakea_mud = (conditions(leeward_maunakea_total))[0]
    leeward_maunakea_falls = (conditions(leeward_maunakea_total))[1]

    waikoloa_mud = (conditions(waikoloa_total))[0]
    waikoloa_falls = (conditions(waikoloa_total))[1]

    kohala_mud = (conditions(kohala_total))[0]
    kohala_falls = (conditions(kohala_total))[1]


    return(hawi_mud, hawi_falls,
           waipio_mud, waipio_falls,
           waimea_mud, waimea_falls,
           honokaa_mud, honokaa_falls,
           laupahoehoe_mud, laupahoehoe_falls,
           hakalau_mud, hakalau_falls,
           papaiku_mud, papaiku_falls,
           hilo_mud, hilo_falls,
           maunaloa_summit_mud, maunaloa_summit_falls,
           s_hilo_mud, s_hilo_falls,
           pahoa_mud, pahoa_falls,
           mtn_view_mud, mtn_view_falls,
           volcano_mud, volcano_falls,
           kau_mud, kau_falls,
           s_big_isle_mud, s_big_isle_falls,
           kona_mud, kona_falls,
           n_kona_mud, n_kona_falls,
           pohakuloa_mud, pohakuloa_falls,
           leeward_maunakea_mud, leeward_maunakea_falls,
           waikoloa_mud, waikoloa_falls,
           kohala_mud, kohala_falls)

#all_conds = rain_calc()[0:43]
#return(all_conds)

conditions = (rain_calc())[0:44]
hawi_mud = conditions[0]
hawi_falls = conditions[1]
waipio_mud = conditions[2]
waipio_falls = conditions[3]
waimea_mud = conditions[4]
waimea_falls = conditions[5]
honokaa_mud = conditions[6]
honokaa_falls = conditions[7]
laupahoehoe_mud = conditions[8]
laupahoehoe_falls = conditions[9]
hakalau_mud = conditions[10]
hakalau_falls = conditions[11]
papaiku_mud = conditions[12]
papaiku_falls = conditions[13]
hilo_mud = conditions[14]
hilo_falls = conditions[15]
maunaloa_summit_mud = conditions[16]
maunaloa_summit_falls = conditions[17]
s_hilo_mud = conditions[18]
s_hilo_falls = conditions[19]
pahoa_mud = conditions[20]
pahoa_falls = conditions[21]
mtn_view_mud = conditions[22]
mtn_view_falls = conditions[23]
volcano_mud = conditions[24]
volcano_falls = conditions[25]
kau_mud = conditions[26]
kau_falls = conditions[27]
s_big_isle_mud = conditions[28]
s_big_isle_falls = conditions[29]
kona_mud = conditions[30]
kona_falls = conditions[31]
n_kona_mud = conditions[32]
n_kona_falls = conditions[33]
pohakuloa_mud = conditions[34]
pohakuloa_falls = conditions[35]
leeward_mauna_kea_mud = conditions[36]
leeward_mauna_kea_falls = conditions[37]
waikoloa_mud = conditions[38]
waikoloa_falls = conditions[39]
kohala_mud = conditions[40]
kohala_falls = conditions[41]

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

# Big Island North and East Forecast Variables parsed
north_east_fcst = (zoneforecast('HIZ025'))[0:10]
north_east_vt1 = north_east_fcst[0]
north_east_wx1 = north_east_fcst[1]
north_east_vt2 = north_east_fcst[2]
north_east_wx2 = north_east_fcst[3]
north_east_vt3 = north_east_fcst[4]
north_east_wx3 = north_east_fcst[5]
north_east_vt4 = north_east_fcst[6]
north_east_wx4 = north_east_fcst[7]
north_east_vt5 = north_east_fcst[8]
north_east_wx5 = north_east_fcst[9]


# Big Island North and East Forecasts by day string value
north_east_fcst1 = (north_east_vt1 + ': ' + north_east_wx1)
north_east_fcst2 = (north_east_vt2 + ': ' + north_east_wx2)
north_east_fcst3 = (north_east_vt3 + ': ' + north_east_wx3)
north_east_fcst4 = (north_east_vt4 + ': ' + north_east_wx4)
north_east_fcst5 = (north_east_vt5 + ': ' + north_east_wx5)

# Big Island South Forecast Variables parsed
south_fcst = (zoneforecast('HIZ024'))[0:10]
south_vt1 = south_fcst[0]
south_wx1 = south_fcst[1]
south_vt2 = south_fcst[2]
south_wx2 = south_fcst[3]
south_vt3 = south_fcst[4]
south_wx3 = south_fcst[5]
south_vt4 = south_fcst[6]
south_wx4 = south_fcst[7]
south_vt5 = south_fcst[8]
south_wx5 = south_fcst[9]

# Big Island South Forecasts by day string value
south_fcst1 = (south_vt1 + ': ' + south_wx1)
south_fcst2 = (south_vt2 + ': ' + south_wx2)
south_fcst3 = (south_vt3 + ': ' + south_wx3)
south_fcst4 = (south_vt4 + ': ' + south_wx4)
south_fcst5 = (south_vt5 + ': ' + south_wx5)


# Big Island Summits Forecasts Variables parsed
summits_fcst = (zoneforecast('HIZ028'))[0:10]
summits_vt1 = summits_fcst[0]
summits_wx1 = summits_fcst[1]
summits_vt2 = summits_fcst[2]
summits_wx2 = summits_fcst[3]
summits_vt3 = summits_fcst[4]
summits_wx3 = summits_fcst[5]
summits_vt4 = summits_fcst[6]
summits_wx4 = summits_fcst[7]
summits_vt5 = summits_fcst[8]
summits_wx5 = summits_fcst[9]

# Big Island Summits Forecasts by day string value
summits_fcst1 = (summits_vt1 + ': ' + summits_wx1)
summits_fcst2 = (summits_vt2 + ': ' + summits_wx2)
summits_fcst3 = (summits_vt3 + ': ' + summits_wx3)
summits_fcst4 = (summits_vt4 + ': ' + summits_wx4)
summits_fcst5 = (summits_vt5 + ': ' + summits_wx5)

# Big Island Kona Forecasts Variables parsed
kona_fcst = (zoneforecast('HIZ023'))[0:10]
kona_vt1 = summits_fcst[0]
kona_wx1 = summits_fcst[1]
kona_vt2 = summits_fcst[2]
kona_wx2 = summits_fcst[3]
kona_vt3 = summits_fcst[4]
kona_wx3 = summits_fcst[5]
kona_vt4 = summits_fcst[6]
kona_wx4 = summits_fcst[7]
kona_vt5 = summits_fcst[8]
kona_wx5 = summits_fcst[9]

# Big Island Kona Forecasts by day string value
kona_fcst1 = (kona_vt1 + ': ' + kona_wx1)
kona_fcst2 = (kona_vt2 + ': ' + kona_wx2)
kona_fcst3 = (kona_vt3 + ': ' + kona_wx3)
kona_fcst4 = (kona_vt4 + ': ' + kona_wx4)
kona_fcst5 = (kona_vt5 + ': ' + kona_wx5)

# Big Island Kohala Forecasts Variables parsed
kohala_fcst = (zoneforecast('HIZ026'))[0:10]
kohala_vt1 = kohala_fcst[0]
kohala_wx1 = kohala_fcst[1]
kohala_vt2 = kohala_fcst[2]
kohala_wx2 = kohala_fcst[3]
kohala_vt3 = kohala_fcst[4]
kohala_wx3 = kohala_fcst[5]
kohala_vt4 = kohala_fcst[6]
kohala_wx4 = kohala_fcst[7]
kohala_vt5 = kohala_fcst[8]
kohala_wx5 = kohala_fcst[9]

# Big Island Kohala Forecasts by day string value
kohala_fcst1 = (kohala_vt1 + ': ' + kohala_wx1)
kohala_fcst2 = (kohala_vt2 + ': ' + kohala_wx2)
kohala_fcst3 = (kohala_vt3 + ': ' + kohala_wx3)
kohala_fcst4 = (kohala_vt4 + ': ' + kohala_wx4)
kohala_fcst5 = (kohala_vt5 + ': ' + kohala_wx5)

# Webpage Variables
bigisland = Blueprint('bigisland', __name__)

@bigisland.route('/bigisland')
def bigislandinfo():
    info = "Hikeit Hawaii"
    summary = "Hawaii's Hiking Weather...Trail Conditions...and Waterfalls"
    island = "Big Island"

    dawn = hilo_dawn
    sunrise = hilo_sr
    sunset = hilo_ss
    dusk = hilo_dusk

    dawn1 = kona_dawn
    sunrise1 = kona_sr
    sunset1 = kona_ss
    dusk1 = kona_dusk

    moon_phase = moon

    zone1 = "Windward North-East"

    north_east_ob_wx = phto_weather
    north_east_ob_temp = phto_temp+"℉"
    north_east_ob_wind = "Wind: "+phto_wind

    zone1_fcst1 = north_east_fcst1
    zone1_fcst2 = north_east_fcst2
    zone1_fcst3 = north_east_fcst3
    zone1_fcst4 = north_east_fcst4
    zone1_fcst5 = north_east_fcst5

    waipio = "Waipio"
    waipio_hikes1 = "Hi'ilawe - Waiholoa - Lahomene - Wai'ilikahi - Waimanu"
    waipio_mud1 = "Conditions: " + waipio_mud
    waipio_falls1 = "Waterfalls Flowing: " + waipio_falls

    laupahoehoe = "Laupahoehoe"
    laupahoehoe_hikes1 = "Hikiau"
    laupahoehoe_mud1 = "Conditions: " + laupahoehoe_mud
    laupahoehoe_falls1 = "Waterfalls Flowing: " + laupahoehoe_falls

    hakalau = "Hakalau"
    hakalau_hikes1 = "Nanue - Kahuna - Akaka"
    hakalau_mud1 = "Conditions: " + hakalau_mud
    hakalau_falls1 = "Waterfalls Flowing: " + hakalau_falls

    papaiku = "Papaiku"
    papaiku_hikes1 = "Waiemi - Waialae"
    papaiku_mud1 = "Conditions: " + papaiku_mud
    papaiku_falls1 = "Waterfalls Flowing: " + papaiku_falls

    hilo = "Hilo"
    hilo_hikes1 = "Wahiloa - Lelekaae - Kulaniapia - Kauwehu - Waiale - Rainbow - Poakana - Peepee Falls - Narnia Falls"
    hilo_mud1 = "Conditions: " + hilo_mud
    hilo_falls1 = "Waterfalls Flowing: " + hilo_falls


    zone2 = "South (Kilauea Volcano)"

    north_east_ob_wx = phto_weather
    north_east_ob_temp = phto_temp+"℉"
    north_east_ob_wind = "Wind: "+phto_wind

    zone2_fcst1 = south_fcst1
    zone2_fcst2 = south_fcst2
    zone2_fcst3 = south_fcst3
    zone2_fcst4 = south_fcst4
    zone2_fcst5 = south_fcst5

    south = "South Big Island"
    south_hikes1 = "Hawaii Volcanoes National Park"
    south_mud1 = "Conditions: " + volcano_mud
    south_falls1 = "Waterfalls Flowing: " + volcano_falls


    zone3 = "Summits (Mauna Loa / Mauna Kea)"

    summits_ob_wx = phsf_weather
    summits_ob_temp = phsf_temp+"℉"
    summits_ob_wind = "Wind: "+phsf_wind

    zone3_fcst1 = summits_fcst1
    zone3_fcst2 = summits_fcst2
    zone3_fcst3 = summits_fcst3
    zone3_fcst4 = summits_fcst4
    zone3_fcst5 = summits_fcst5

    mauna_loa = "Mauna Loa"
    mauna_loa_hikes1 = "Mauna Loa Summit"
    mauna_loa_mud1 = "Conditions: " + maunaloa_summit_mud
    mauna_loa_falls1 = "Waterfalls Flowing: " + maunaloa_summit_falls

    mauna_kea = "Mauna Kea"
    mauna_kea_hikes1 = "Mauna Kea Summit"
    mauna_kea_mud1 = "Conditions: " + pohakuloa_mud
    mauna_kea_falls1 = "Waterfalls Flowing: " + pohakuloa_falls

    leeward_mauna_kea = "Waihilau (NW Slope Mauna Kea)"
    leeward_mauna_kea_hikes1 = "Waihilau Falls"
    leeward_mauna_kea_mud1 = "Conditions: " + leeward_mauna_kea_mud
    leeward_mauna_kea_falls1 = "Waterfalls Flowing: " + leeward_mauna_kea_falls

    pohakuloa = "Pohakuloa"
    pohakuloa_hikes1 = "Pu'u O'o Trail"
    pohakuloa_mud1 = "Conditions: " + pohakuloa_mud
    pohakuloa_falls1 = "Waterfalls Flowing: " + pohakuloa_falls

    zone4 = "Kona"

    kona = "Kona"
    kona_ob_wx = phko_weather
    kona_ob_temp = phko_temp+"℉"
    kona_ob_wind = "Wind: "+phko_wind

    zone4_fcst1 = kona_fcst1
    zone4_fcst2 = kona_fcst2
    zone4_fcst3 = kona_fcst3
    zone4_fcst4 = kona_fcst4
    zone4_fcst5 = kona_fcst5

    kona = "Kona"
    kona_hikes1 = "Kona Cloud Forest - Honua'ula"
    kona_mud1 = "Conditions: " + kona_mud
    kona_falls1 = "Waterfalls Flowing: " + kona_falls

    n_kona = "North Kona"
    n_kona_hikes1 = "Pu'u Wa'awa'a Cinder Cone"
    n_kona_mud1 = "Conditions: " + n_kona_mud
    n_kona_falls1 = "Waterfalls Flowing: " + n_kona_falls

    zone5 = "Kohala"

    kohala = "Kohala"
    kohala_ob_wx = phko_weather
    kohala_ob_temp = phko_temp+"℉"
    kohala_ob_wind = "Wind: "+phko_wind


    zone5_fcst1 = kohala_fcst1
    zone5_fcst2 = kohala_fcst2
    zone5_fcst3 = kohala_fcst3
    zone5_fcst4 = kohala_fcst4
    zone5_fcst5 = kohala_fcst5

    kohala = "Kohala"
    kohala_hikes1 = "Kemole - Waiokanalopaka - Keanapakulua"
    kohala_mud1 = "Conditions: " + kohala_mud
    kohala_falls1 = "Waterfalls Flowing: " + kohala_falls


    return render_template('bigislandv2.html',**locals())
