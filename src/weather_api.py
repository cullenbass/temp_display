import urequests
import ujson

headers= {'User-Agent' : 'Desktop Temp Display'}

def get_weather_station_gov(weather_lat, weather_long):
    req = urequests.get(f'https://api.weather.gov/points/{weather_lat},{weather_long}', headers = headers)
    if req.status_code != 200:
        print(f'Status code: {req.status_code}')
        print(req.text)
        return None
    req = urequests.get(ujson.load(req.raw)['properties']['observationStations'], headers=headers)
    if req.status_code != 200:
        print(f'Status code: {req.status_code}')
        print(req.text)
        return None
    return ujson.load(req.raw)['features'][0]['properties']['stationIdentifier']


def get_current_temp_gov(station_id):
    req = urequests.get(f'https://api.weather.gov/stations/{station_id}/observations', headers=headers)
    if req.status_code != 200:
        print(f'Status code: {req.status_code}')
        print(req.text)
        return None
    print(ujson.load(req.raw)['features'][0]['temperature'])

def get_current_temp(lat, long):
    req = urequests.get(f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&current=temperature_2m&temperature_unit=fahrenheit')
    if req.status_code != 200:
        print(f'Status code: {req.status_code}')
        print(req.text)
        return None
    return ujson.load(req.raw)['current']['temperature_2m']
