# ✈︎ VFR-LED-map-Saskatchewan ✈︎
An LED-lit map of Saskatchewan designed for VFR (Visual Flight Rules) navigation. Think of it as a backlit sectional chart that helps pilots see airports, landmarks, and airspace boundaries at a glance. 
Powered by a Raspberry Pi Zero 2 WH with ws2811 lights for the LEDs, and a Waveshare e-ink display. LEDs show current flight conditions, and an e-ink display shows local weather for towns and cities.

This repository has: 
- The .img (disk image) of the raspberry pi
- The Python script used to parse the VFR data and display the data ( **AirportMetar.py** )
  - There are many already made code repo's for VFR data/maps, but I wanted to add categories for thunderstorms or high winds or frozen precipitation, a legend, and an e-ink display. So I wrote a lot of my own functions. Also allowed me to add more if I ever wanted to.
  - Legend idea/format of text came from: https://aerosavvy.com/metar-map/
- The edited python script for displaying weather and more on the e-ink display ( **utf8_weather_epaper.py** )

- The full image used of Saskatchewan used for the map. I created this map by taking multiple screenshots of Saskatchewan piece by piece through https://www.fltplan.com/ . I then stitched the images together through Photoshop.
  - Becasue Canda doesn't make sectionals of provinces easy to obtain digitally, I made it myself so I could ensure quality and edit it to whatever I desire.

<img src="https://raw.githubusercontent.com/Sylvial-00/VFR-LED-map-Saskatchewan/refs/heads/main/VFRMapImages/20260131_211743.jpg" width="300" hspace="100"><img src="https://raw.githubusercontent.com/Sylvial-00/VFR-LED-map-Saskatchewan/refs/heads/main/VFRMapImages/20260316_212902.jpg" width="300">
<p align="center">
  <img src="https://github.com/Sylvial-00/VFR-LED-map-Saskatchewan/blob/main/VFRMapImages/PXL_20251219_001834482.LS.gif?raw=true" width="300">
</p>

---
## What other repositories did I use?

I believe in "not re-inventing the wheel" when creating smething. I used
- https://github.com/python-metar/python-metar
  - Used to help parse more of the aviation gov data. I use it alongside my own rudimentary parsing to double check and to make category checking easier.
- https://github.com/MerlinLuchs/Weather-on-Waveshare
  - Used to control the e-ink display. I did change a bit of the code to add the location of the current displayed weather and to move around icons, change size of icons and text as well.

## What does this do

This is a physical wall map with LED-lit airports and an e-ink display. Every 30 minutes, it pulls live weather data from aviationweather.gov and updates the colors to show flight categories at 15 airports across Saskatchewan.

The e-ink display shows temperature, humidity, and weather for a town or city. It rotates to a different location every 36 minutes.

---

## Airports Included

| | | | |
|---|---|---|---|
| Stony Rapids | Meadow Lake | Kindersley | Saskatoon |
| Key Lake | Prince Albert | Yorkton | Regina |
| Buffalo Narrows | Nipawin | Swift Current | Estevan |
| La Ronge | North Battleford | Moose Jaw | |

Airports were chosen based on availability through aviationweather.gov. Not all Saskatchewan airports were listed there, nor did all have reliable data.

**_An API key for aviationweather.gov is necessary for the data to be retrieved._**

---

## LED Color Codes

| Color | Category | Conditions |
|-------|----------|------------|
| 🟢 Green | VFR | Ceiling ≥ 3,000 ft AND visibility ≥ 5 sm |
| 🔵 Dark Blue | MVFR | Ceiling 1,000-3,000 ft OR visibility 3-5 sm |
| 🔴 Red | IFR | Ceiling 500-<1,000 ft OR visibility 1-<3 sm |
| 🟣 Purple | LIFR | Ceiling <500 ft OR visibility <1 sm |

---

## Flashing Hazard Indicators

| Color | Hazard |
|-------|--------|
| ⚪ White Flashing | Frozen Precipitation (snow, freezing rain, ice pellets, freezing drizzle, hail) |
| 🟡 Yellow Flashing | Thunderstorm |
| 🔵 Light Blue Flashing | Strong Winds (≥ 15 knots sustained) |

**Note:** Weather takes precedence over flight categories. Priority order: Thunder > Precipitation > Wind.

---

### Update Schedule

- **Every 30 minutes:** Flight categories update, LEDs flash to indicate update
- **Every 36 minutes:** E-ink display changes to a different location (due to API rate limits)

---

### How It Runs

The script starts automatically on reboot using a crontab:
  crontab.log 2>&1 /home/metar/desktop/crontab.log

---
### Wiring

A figure of how stuff is connected to the raspberry pi is shown below.

<img src="https://github.com/Sylvial-00/VFR-LED-map-Saskatchewan/blob/main/VFRMapImages/Wiring1.png?raw=true" width="450">

### Images of it being worked on

This project was fun to make. The whole process was a bit frustrating at times but incredibly rewarding once it worked and once the recipient told me how awesome they thought it was! Some images below show the work in progress images I took.

<img src="https://github.com/Sylvial-00/VFR-LED-map-Saskatchewan/blob/main/VFRMapImages/metar-map-for-my-bfs-christmas-present-v0-udrg92vdsf4g1.webp?raw=true" width="250">
<img src="https://github.com/Sylvial-00/VFR-LED-map-Saskatchewan/blob/main/VFRMapImages/PXL_20251129_223112543.MP.jpg?raw=true" width="250">
<img src="https://github.com/Sylvial-00/VFR-LED-map-Saskatchewan/blob/main/VFRMapImages/PXL_20251129_044730150.MP.jpg?raw=true" width="250">
