# See this in action here: https://www.reddit.com/r/raspberry_pi/comments/swcii5/raspberry_pi_4_and_29_epaper_showing_me_the/
#

import json 
import time
import urllib.request
import urllib.parse
from lib import epd4in2_V2# Get the waveshare module for your display (epd2inbc is the black/red one, epd2in9 is the black/white one) and put them in a subfolder called "lib"
from PIL import Image,ImageDraw,ImageFont # Needed for the e-ink display.
import textwrap # This is so your text can wrap if it gets too long.
import datetime # To get time of last update.
# import locale
# locale.setlocale(locale.LC_ALL, 'de_DE.utf8') # Used this to set Germany as a region.

meteocons = ImageFont.truetype('/home/metar/Desktop/Weather-on-Waveshare/meteocons.ttf', 32) # Get here: https://www.alessioatzeni.com/meteocons/ and put .ttf file in the same directory
meteoconssmall = ImageFont.truetype('/home/metar/Desktop/Weather-on-Waveshare/meteocons.ttf', 20) # This is the same for a smaller text size, in case you want smaller symbols.
glyphter = ImageFont.truetype('/home/metar/Desktop/Weather-on-Waveshare/glyphter.ttf', 20) # This is for humidity icon. Font is here: https://freebiesbug.com/psd-freebies/80-stroke-icons-psd-ai-webfont/
font40 = ImageFont.truetype('/home/metar/Desktop/Weather-on-Waveshare/Font.ttf', 40) # Various font sizes to choose from.
font22 = ImageFont.truetype('/home/metar/Desktop/Weather-on-Waveshare/Font.ttf', 30) # Various font sizes to choose from.
font20 = ImageFont.truetype('/home/metar/Desktop/Weather-on-Waveshare/Font.ttf', 25)
font18 = ImageFont.truetype('/home/metar/Desktop/Weather-on-Waveshare/Font.ttf', 18)
font16 = ImageFont.truetype('/home/metar/Desktop/Weather-on-Waveshare/Font.ttf', 16)
font14 = ImageFont.truetype('/home/metar/Desktop/Weather-on-Waveshare/Font.ttf', 14)
width = 400 # width and height
height = 300

APIKEY = "" # Get a free api key from the Open Weather Map: https://openweathermap.org/api

WETTER_API_URL = "http://api.openweathermap.org/data/2.5/weather" # This is the weather API. They have other APIs like the "One Call" one that has other info like forecast or moonrise. Pick your poison.

epd = epd4in2_V2.EPD() # Adjust according to your display.

def ausgabe(y, LOCATION):
	
	
	epd.init()
	epd.Clear()
	#image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
	image = Image.new('1', (width, height), 255)

	draw = ImageDraw.Draw(image)


	draw.rectangle((0, 0, epd.height, epd.width), fill = 255)
	today = datetime.datetime.today()
	drawblack = ImageDraw.Draw(image)

	
	message = "\' " #Meteocon symbol for the thermometer
	drawblack.text((2,5), message, font = meteoconssmall, fill = 0) # It's red. Adjust this for black/white displays.
	message = "   " + str(y["main"]["temp"]) + "ºC" # Getting the data from the API.
	drawblack.text((3,2), message, font = font22, fill = 0)
	message = str(y["weather"][0]["description"])
	drawblack.text((23,30), message, font = font22, fill = 0) # Getting description from API (e.g. "partly cloudy")
	
	#Wind speed
	message = "F"  # Meteocon symbol for wind
	drawblack.text((95,95), message, font = meteoconssmall, fill = 0)
	wind_ms = (y["wind"]["speed"])
	wind_kmh = wind_ms * 3.6 # This calculates the metres/second into kilometers/hour
	formatted_wind_kmh = "{:.2f}".format(wind_kmh) # This reduces the output to two numbers behind the comma
	message = str(y["wind"]["speed"]) + " m/s = "  + str(formatted_wind_kmh) + " km/h"
	drawblack.text((120,95), message, font = font20, fill = 0)

	message = "W" #glyphter font: This is the humidity drop.
	drawblack.text((6,95), message, font = glyphter, fill = 0)
	message = ": " + str(y["main"]["humidity"]) + "%" 
	drawblack.text((22,95), message, font = font20, fill = 0)
		
	message = "B " # Sunrise icon
	drawblack.text((10,135), message, font = meteocons, fill = 0)
	message = "   " + time.strftime('%H:%M', time.localtime(y["sys"]["sunrise"]))
	drawblack.text((20,140), message, font = font22, fill = 0)
	message = "Sunrise"
	drawblack.text((50,165), message, font = font18, fill = 0)

	message = "A " # Sunset icon
	drawblack.text((135,135), message, font = meteocons, fill = 0)
	message = "   " + time.strftime('%H:%M', time.localtime(y["sys"]["sunset"]))
	drawblack.text((140,140), message, font = font22, fill = 0)
	message = "Sunset"
	drawblack.text((175,165), message, font = font18, fill = 0)

#	DATE AND TIME
	drawblack.text((250,140), 'Last update:', font = font16, fill = 0) #
	drawblack.text((250, 155), '{:%a, %d.%m. (%H:%M)}'.format(today), font = font16, fill = 0)
	drawblack.line((245, 140, 245, 175), fill = 0, width = 2)
# SHOW LOCATION
	message = 'Location: ' + LOCATION
	drawblack.text((10,230), message, font = font22, fill = 0 )
	
	epd.display(epd.getbuffer(image))
	epd.sleep()

def get_weather_eink(location):
	LOCATION = "Berlin,DE" # Choose your city.
	LOCATION = location
	# Set up where we'll be fetching data from
	params = {"q": LOCATION, "appid": APIKEY, "units":"metric" } # options are standard, metric, imperial
	data_source = WETTER_API_URL + "?" + urllib.parse.urlencode(params) +"&lang=en" # change "&lang=en" to "&lang=de" for German, etc.
	weather_refresh = None
	
	response = urllib.request.urlopen(data_source) 
	if response.getcode() == 200: 
		value = response.read() 
		y = json.loads(value)
		print(y)
		print("draw")
		ausgabe(y, location)


