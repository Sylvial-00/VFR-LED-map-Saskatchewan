# ✈︎ VFR-LED-map-Saskatchewan ✈︎
An LED-lit map of Saskatchewan designed for VFR (Visual Flight Rules) navigation. Think of it as a backlit sectional chart that helps pilots see airports, landmarks, and airspace boundaries at a glance. 
Powered by a Raspberry Pi Zero 2 WH with ws2811 lights for the LEDs, and a Waveshare e-ink display. LEDs show current flight conditions, and an e-ink display shows local weather for towns and cities.

This repository has: 
- The .img (disk image) of the raspberry pi
- The Python script used to parse the VFR data
- The edited python script from

- The full image used of Saskatchewan used for the map. I created this map by taking multiple screenshots of Saskatchewan piece by piece through https://www.fltplan.com/ . I then stitched the images together through Photoshop.
  - Becasue Canda doesn't make sectionals of provinces easy to obtain digitally, I made it myself so I could ensure quality and edit it to whatever I desire.

<img src="https://raw.githubusercontent.com/Sylvial-00/VFR-LED-map-Saskatchewan/refs/heads/main/VFRMapImages/20260131_211743.jpg" width="300" hspace="100"><img src="https://raw.githubusercontent.com/Sylvial-00/VFR-LED-map-Saskatchewan/refs/heads/main/VFRMapImages/20260316_212902.jpg" width="300">

---
## What other repositories did I use?

I believe in "not re-inventing the wheel" when creating something. I used
- https://github.com/aeharding/metar-taf-parser/blob/main/example/src/helpers/metarTaf.ts
  - Used to help parse more of the aviation gov data. I use it alongside my own rudimentary parsing to double check and to make category checking easier.
- https://github.com/MerlinLuchs/Weather-on-Waveshare
  - Used to control the e-ink display. I did change a bit of the code to add the location of the current displayed weather and to move around icons.

## What does this do

This is a physical wall map with LED-lit airports and an e-ink display. Every 30 minutes, it pulls live weather data from aviationweather.gov and updates the colors to show flight categories at 15 airports across Saskatchewan.

The e-ink display shows temperature, humidity, and weather for a town or city. It rotates to a different location every 36 minutes.

---

## Airports Included

| | | |
|---|---|---|
| Stony Rapids | Meadow Lake | Kindersley |
| Key Lake | Prince Albert | Yorkton |
| Buffalo Narrows | Nipawin | Swift Current |
| La Ronge | North Battleford | Moose Jaw |
| | Saskatoon | Regina |
| | | Estevan |

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
