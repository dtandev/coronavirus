import requests
from geopy import geocoders

geolocator = geocoders.Nominatim(user_agent = 'dtansci@gmail.com')

def locate_user_ip():
    """

    """
    ip_request = requests.get('https://get.geojs.io/v1/ip.json')
    my_ip = ip_request.json()['ip']
    georequest_url = 'https://get.geojs.io/v1/geo/'+my_ip+'.json'
    georequest = requests.get(georequest_url)
    geodata = georequest.json()
    return geodata['city']


def locate_user_address(address):
    """
    
    """
    return geolocator.geocode(address)[1]

