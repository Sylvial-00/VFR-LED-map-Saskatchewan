import requests
import RPi.GPIO as GPIO
import neopixel
import board
import re
import time
import threading
import sys
import multiprocessing
import math
import random

from pathlib import Path
from metar import Metar
from datetime import datetime, timedelta
from adafruit_led_animation.animation.blink import Blink
from adafruit_led_animation.helper import PixelSubset
from adafruit_led_animation.color import RED, BLUE, GREEN
from adafruit_led_animation.helper import PixelMap#
from adafruit_led_animation.group import AnimationGroup

sys.path.append(str(Path(__file__).parent / "Weather-on-Waveshare/"))

from utf8_weather_epaper import get_weather_eink

#Define the airport icao CODEs
airport_icaos = ["CYEN", "CYMJ", "CYQR", "CYYN", "CYKY", "CYXE",
                "CYQW", "CYPA", "CYBU", "CYLJ", "CYVC", "CYVT",
                "CYKJ", "CYSF", "CYQV"]
#airport_icaos = ["CYVT","CYKJ", "CYSF", "CYQV"]
airport_icaos_LED = {"CYEN": 1, "CYMJ": 3, "CYQR":4, "CYYN":6, "CYKY":7, "CYXE":9,
                "CYQW":10, "CYPA":12, "CYBU":13, "CYLJ":16, "CYVC":18, "CYVT":20,
                "CYKJ":22, "CYSF":24, "CYQV":35

}

yxe2 = 28 # the second, zoomed in circle of saskatoon 
legend_LED = {"VFR" : 44, 
            "MVFR" : 43,
            "IFR" : 42,
            "LIFR" : 41,
            "WINDY" : 40,
            "FROZEN" : 39,
            "THUNDER" : 38}

#no city API call for Key lake
cities = ["Saskatoon,CA", "Estevan,CA", "Moose Jaw,CA", "Regina,CA", "Swift Current,CA",
        "Kinsersley,CA", "North Battlefoard,CA", "Prince Albert,CA", "Nipawin,CA", "Meadow Lake,CA",
        "La Ronge,CA", "Buffalo Narrows,CA", "Stony Rapids,CA", "Yorkton,CA"]
#airport_icao = "CYXE"
def get_metar_data(airport, hours):
    """
    Gets LATEST metar data from aviationweather.gov api in json format given the airpor code
    airport: the ICAO code of the airport
    hours: past hours to grab data from (past 24 or 48 or 36 or 12 ...etc hours)
    """
    print("DEBUGGING AIRPORT")
    print(airport)
    url = f"https://aviationweather.gov/api/data/metar?ids={airport}&hours={hours}&format=json"

    
    response = requests.get(url)
    response.raise_for_status()
    metar_data = response.json()
    
    print(metar_data[0])
    if metar_data:
        print(f"METAR for {airport}: {metar_data[0]}") #Get the latest metar take
        print(type(metar_data[0]))
        return metar_data[0]
    else:
        print(airport)
        print("we got a rpblem")
def get_ceiling(cloud_string):
    '''
    cloud_string: string from metar.metar.sky_conditions()
    return lowest layer of clouds (BROKEN OR OVERCAST ONLY COUNTS) (int)
    '''
    layers = re.findall(r'(overcast|broken) clouds at (\d+)', cloud_string, flags=re.IGNORECASE)
    if layers:
        lowest = min(layers, key=lambda x: int(x[1]))
        #print("WE HAVE CLOUDS")
        #print(lowest[1])
        return int(lowest[1]) #return the lowest ceiling based on overcast or broken clouds
    else:
        return 4000 #no ceilings, clear skies basically
def get_visibility(vis_data, raw_vis):
    vis_data = vis_data.replace(" miles", "")
    parts = vis_data.split()
    try:
        if len(parts) ==1:
            return float(vis_data)
        return float(raw_vis)
    except ValueError as e:
        return float(raw_vis)
def get_weather(weather, raw_weather, wind, raw_wind):
    '''
    Returns weather of interest (if frozen percipitation, thunferstorm or high windspeed)
    
    '''
    print(weather)
    print(raw_weather)
    if weather == "" and raw_weather is None:
        if len(wind) > 1:
            wind_knots = re.findall(r'-?\d+\.?\d*', wind)
            if (len(wind_knots) < 1):
                wind_knots = float(raw_wind)
            else:
                wind_knots = float(wind_knots[0])
            print(wind_knots)
            if wind_knots >= 15 or float(raw_wind) >= 15:
                return 'WIND'
        return 0
    else:
        if "thunderstorm" in weather or'TS' in raw_weather:
            return "THUNDER"
        elif ("snow" in weather or "freezing rain" in weather or "ice pellets" in weather or "hail" in weather or "freezing drizzle" in weather):
            return "FROZEN"
        elif len(raw_weather) > 0:
            for i in ['SN', 'PL', 'GR', 'FZRA', 'FZDZ', 'GS']:
                if i in raw_weather:
                    return "FROZEN"
        elif len(wind) > 1:
            try: #try to get the actual wind speed out of the parsed metar
                wind_knots = float(re.findall(r'-?\d+\.?\d*', wind)[0])
            except Exception as e:
                if wind == "calm" or wind == "missing": #if parser set wind to calm
                    wind_knots = 0.0
            if wind_knots >= 15 or float(raw_wind) >= 15:
                return 'WIND'


    
def metar_categories(clouds, vis, raw_vis,weather, raw_weather, wind, raw_wind):
    """
    Determines what caegory of metar data it is based on cieling, visibility.
    determines active weather phenomena  from determined set
    frozen percipitation:
        wxstring = SN, PL, FZRA, FZDZ, GR, GS
    Thunderstorm
        wxstring = TS in string and not TSNO
    wind knots
        windspeed over or equal to 15 knots 'wspd'
    Weather phenomena report OVER METAR category, if no weather phenomena above, report METAR category
    
    metar_data: json of the data i.e dictionary of the data. automatically pased via requests package .json function
    """
    weather = get_weather(weather,raw_weather, wind, raw_wind)
    ceiling = int(get_ceiling(clouds))
    visibility = float(get_visibility(vis, raw_vis))
    print(weather)
    print("HELLO")
    if (weather == "THUNDER"):
        return "THUNDER"
    elif (weather == "FROZEN"):
        return "FROZEN"
    elif (weather == "WIND"):
        return "WIND"
    elif weather == 0:
        pass
    
    #VFR: cieling: >= 3000ft & visib ility > 5
    if (ceiling  >= 3000 and visibility > 5):
        return 'VFR'
    #MVFR: ceiling:  1000 - 3000 OR 3-5SM
    elif ((ceiling >= 1000 and ceiling  <= 3000) or (visibility <= 5 and visibility >= 3)):
        
        return "MVFR"
    #LIFR ceiling: <500  visibility: < 1
    elif (ceiling  < 500 or visibility < 1):
        return 'LIFR'
    #IFR ceiling: <1000 OR visibility <3SM
    elif (ceiling  < 1000 or visibility < 3):
        return 'IFR'
    
def flash_all(pixels, color=(255, 255,255), times = 3, delay=0.8):
    '''
    Flash all leds in the strip activated 
    '''
    for _ in range(times):
        pixels.fill(color)
        pixels.show()
        time.sleep(delay)
        
        pixels.fill((0,0,0))
        pixels.show()
        time.sleep(delay)
def dimming(pixels,index, smoothness, colour=(216, 0, 230)):
    COLOR = colour #(0,0,0)
    step = 0
    direction = 1
    while True:
        brightness = (math.sin(step)+ 1 / 2)
        
        r = int(colour[0]*brightness)
        g = int(colour[1] * brightness)
        b = int(colour[2]*brightness)
        
        for i in index:
            pixels[i] = (r,g,b)
        pixels.show()
        step +=0.05
        time.sleep(5)
def update_category(pixels, airport_icaos):
    """
    Updates what light colour the led will be based on the wind and sky and visbility
    
    """
        #sets the legend for the other categories like MVFR or whatever else
    pixels[legend_LED['VFR']] = (155, 0,0) #greeen
    pixels[legend_LED['MVFR']] = (0, 0,255) #blue
    pixels[legend_LED['IFR']] = (0, 255,0) #red
    pixels[legend_LED['LIFR']] = (0, 120,120) #purple
    global animations, thunder_subset, frozen_subset, wind_subset
    for airport in airport_icaos:
        noData = False
        try:
            json_metar = get_metar_data(airport, 96)
            obs = Metar.Metar(json_metar['rawOb'])
        except:
            noData = True
        print(obs.string())
        print("weather: " + str(obs.present_weather()))
        print(obs.sky_conditions())
        #print(obs.visibility())
        print("sky conditioons above")
        #print(get_visibility(obs.visibility()))
        sky = obs.sky_conditions()
        vis = obs.visibility()
        weather = obs.present_weather()
        wind = obs.wind()
        try:
            raw_weather = json_metar['wxString']
        except (KeyError):
            raw_weather = ""
        #print(airport_icaos_LED[airpowxrt])
        #print(metar_categories(sky, vis, json_metar['visib'], weather, json_metar['wxString'], wind, json_metar['wspd']))
        #print(get_ceiling(sky))
        if (noData):
            category = "noData"
        else:
            category =metar_categories(sky, vis, json_metar['visib'], weather, raw_weather, wind, json_metar['wspd'])

        if (category == "WIND"):
            #dimming(pixels, airport_icaos_LED[airport], 20, (0,0,255))
            wind_subset.append(airport_icaos_LED[airport])
            if airport == "CYXE":
                all_weather.append((yxe2, (216, 0, 230)))
            all_weather.append((airport_icaos_LED[airport], (216, 0, 230)))
        elif (category == "THUNDER"):
            #dimming(pixels, airport_icaos_LED[airport], 20, (237,237,4))
            thunder_subset.append(airport_icaos_LED[airport])
            if airport == "CYXE":
                all_weather.append((yxe2, (237,237,4)))
            all_weather.append((airport_icaos_LED[airport], (237,237,4)))
        elif (category == "FROZEN"):
            #dimming(pixels, airport_icaos_LED[airport], 20, (216,173,230))
            frozen_subset.append(airport_icaos_LED[airport])
            if airport == "CYXE":
                all_weather.append((yxe2, (216,173,230)))
            all_weather.append((airport_icaos_LED[airport], (216,173,230)))
        
        #For some reason the second sasaktoon light cant be its own if statemtn if i grab the colour after the if statement of setting the colours, it returns [0,0,0]
        elif (category== 'VFR'):
            pixels[airport_icaos_LED[airport]] = (155, 0,0) #greeen
            #for second saskatoon light
            if airport == "CYXE":
                pixels[yxe2] =(155, 0,0) #greeen
        elif (category  == 'MVFR'):
            pixels[airport_icaos_LED[airport]] = (0, 0,255) #blue
            #for second saskatoon light
            if airport == "CYXE":
                pixels[yxe2] = (0, 0,255) #blue
        elif (category== 'IFR'):
            pixels[airport_icaos_LED[airport]] = (0, 255,0) #red
            #for second saskatoon light
            if airport == "CYXE":
                pixels[yxe2] =(0, 255,0) #red
        elif (category == 'LIFR'):
            pixels[airport_icaos_LED[airport]] = (0, 120,120) #purple
            #for second saskatoon light
            if airport == "CYXE":
                pixels[yxe2] = (0, 120,120) #purple
        if (category == "noData"):
            pixels[airport_icaos_LED[airport]] = (0,0,0)
            
def special_weather(pixels, indices, colour):
    for i in indices:
        pixels[i] = (0,0,0)
    pixels.show()
    time.sleep(0.15)
    
    for i in indices:
        pixels[i] = colour
    pixels.show()
    time.sleep(0.2)
    
    for i in indices:
        pixels[i] = (0,0,0)
    pixels.show()
    time.sleep(0.15)
        
    for i in indices:
        pixels[i] = colour
    pixels.show()
    time.sleep(0.15)
    
    for i in indices:
        pixels[i] = colour
    pixels.show()
    time.sleep(0.15)
def special_weather_all(pixels, indices):
    for i, colour in indices:
        pixels[i] = (0,0,0)
    pixels.show()
    time.sleep(1.0)
    
    for i, colour in indices:
        pixels[i] = colour
    pixels.show()
    time.sleep(1.0)
    
    for i, colour in indices:
        pixels[i] = (0,0,0)
    pixels.show()
    time.sleep(1.0)
        
    for i, colour in indices:
        pixels[i] = colour
    pixels.show()
    time.sleep(1.0)
    
NUM_AIRPORTS = 45 #number of lights we need to send data throgh
PIXEL_ORDER = neopixel.GRB
####NUMBER OF AIRPORTS PLUS 7 BECAUSE THE LEGEND IS 7 PIXELS
pixels = neopixel.NeoPixel(board.D18, NUM_AIRPORTS, brightness = 0.25, auto_write = False)
pixels.fill((0,0,0))
pixels.show()

all_weather = []

thunder_subset = []
frozen_subset = []
wind_subset = []
animations = []

time_to_refresh = 1800 #in SECONDS, refresh evert 30 minutes
end_time = datetime.now() + timedelta(seconds =time_to_refresh)
weather_end_time = datetime.now() + timedelta(seconds =time_to_refresh/2)
last_run_weather = datetime.now()
city_index = random.randrange(len(cities))
get_weather_eink(cities[city_index])
while True:
    all_weather = [] #the weather pixels like thunderstorm or icy or whatever
    #sets the legend for weather
    all_weather.append((legend_LED['THUNDER'],(237,237,4)))
    all_weather.append((legend_LED['FROZEN'],(216,173,230)))
    all_weather.append((legend_LED['WINDY'],(216, 0, 230)))

    flash_all(pixels)
    update_category(pixels, airport_icaos)
    #print(weather_end_time)
    #print(end_time)
    while datetime.now() < end_time:
        current_time = datetime.now()
        if current_time - last_run_weather >= timedelta(minutes=37): #update weather every 3 mins
            try: #Close the process if it exists so i dont blow up the cpu
                screen_thread.terminate()
                screen_thread.close()
            except: 
                pass
            city_index+=1
            last_run_weather = current_time
            if city_index == len(cities)-1:
                city_index = 0
            screen_thread = multiprocessing.Process(target=get_weather_eink, args = (cities[city_index],))
            screen_thread.daemon = True
            screen_thread.start()
        pixels.show()
        #smoothness = 5
        #for i in range(smoothness):
            #for w in wind_subset:
                #brightness = i/smoothness
                
                #gamma_corrected = tuple(int(c * (brightness**2.8)) for c in (0,0,255))
                #pixels[w] = gamma_corrected
                #pixels.show()
                #time.sleep(0.2)
        #Thunderstorm pixels
        #special_weather(pixels, thunder_subset, (237, 237, 4))
        #special_weather(pixels, wind_subset, (216, 0, 230))
        #special_weather(pixels, frozen_subset, (255, 255, 255))
        special_weather_all(pixels, all_weather)
    end_time = datetime.now() + timedelta(seconds = time_to_refresh)
    #animation_group = AnimationGroup(*animations)
    #animation_group.animate()
    
    #blink = Blink(pixels, speed=2.0, color=(255,0,0))
    #blink.animate()
    #pixels.show()

    #animations = []
    #thunder_subset = []
    #frozen_subset = []
    #wind_subset = []


        

#GPIO.setwarnings(False)
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(23, GPIO.IN,
           #pull_up_down=GPIO.PUD_UP)

##try:
#    while True:
#        if GPIO.input(23) == GPIO.HIGH:
#            print("button Pressed")
#            while GPIO.input(23) == GPIO.HIGH:
#                time.sleep(0.1)
#            time.sleep(0.1)
#except KeyboardInterrupt:
#    print("Program Stropped")
#finally:
    #GPIO.cleanup()
