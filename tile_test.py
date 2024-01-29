#%%
import requests
from IPython import display
from dotenv import load_dotenv
import hashlib
import hmac
import os
import base64
import math
import urllib.parse as urlparse

load_dotenv()

# Pull in API key and Secret key from .env

APIKEY = os.environ.get("API_KEY")
SECRET = os.environ.get("SECRET")
#SESSION = "AJVsH2zcE4_jik59GS3waaWZYEoAt1XTsh5lIbi_rOizq1ubO2U1OAQeRCW2yp_4qq-vIhAM-QFYeh1t-KTMqmjzxQ"
TILE_SIZE = 256


#%%
# Google API documentation code for signing API requests
def sign_url(input_url=None, secret=None):
    """ Sign a request URL with a URL signing secret.
      Usage:
      from urlsigner import sign_url
      signed_url = sign_url(input_url=my_url, secret=SECRET)
      Args:
      input_url - The URL to sign
      secret    - Your URL signing secret
      Returns:
      The signed request URL
  """

    if not input_url or not secret:
        raise Exception("Both input_url and secret are required")

    url = urlparse.urlparse(input_url)

    # We only need to sign the path+query part of the string
    url_to_sign = url.path + "?" + url.query

    # Decode the private key into its binary format
    # We need to decode the URL-encoded private key
    decoded_key = base64.urlsafe_b64decode(secret)

    # Create a signature using the private key and the URL-encoded
    # string using HMAC SHA1. This signature will be binary.
    signature = hmac.new(decoded_key, str.encode(url_to_sign), hashlib.sha1)

    # Encode the binary signature into base64 for use within a URL
    encoded_signature = base64.urlsafe_b64encode(signature.digest())

    original_url = url.scheme + "://" + url.netloc + url.path + "?" + url.query

    # Return signed URL
    return original_url + "&signature=" + encoded_signature.decode()



#lon_increment of (0.00172 causes almost perfect no overlap stitch)
#lat_increment of (0.00145 causes almost perfect no overlap stitch)


# %%
def check_data_dir():
    os.chdir(".")
    print(os.getcwd())
    if os.path.isdir("data"):
        pass
    else:
        os.mkdir("data")

def fromLatLngToPoint(lat, lng):
    mercator = -math.log(math.tan((0.25 + lat / 360) * math.pi))
    return {
    "x": TILE_SIZE * (lng / 360 + 0.5),
    "y": TILE_SIZE / 2 * (1 +  mercator / math.pi)
  }

def fromLatLngToTileCoord(lat, lng, zoom):
    point = fromLatLngToPoint(lat, lng)
    scale = math.pow(2, zoom)

    return {
    "x": math.floor(point["x"] * scale / TILE_SIZE),
    "y": math.floor(point["y"] * scale / TILE_SIZE),
    "z": zoom
  }

##def fromTileCoordToLatLng(x_t, y_t, zoom):
##    scale = math.pow(2, zoom)
##    x_p = (x_t * TILE_SIZE) / scale
##    y_p = (y_t * TILE_SIZE) / scale
##    lng = 360*((x_p/TILE_SIZE) - 0.5)
##    to_exp = -math.pi*(y_p/128 - 1)
##    to_atan = math.pow(10, to_exp)
##    atan = math.atan(to_atan)
##    exp1 = ((atan / math.pi) - 0.25)
##    lat = 360*exp1
##    return (lat, lng)


# %%
def get_tile(x, y, zoom=19):
    """
    Given coordinates list, calls Google API to get static images and saves them to data directory 
    """
    SESSION = "AJVsH2ylSH6_zUX-SeYQvMEXXTYeyREIY3szAAKFZpVL0UIHwMSoVluxMzTiv3L-Ty2mgMPKdNS4U9UqjsJXoPUwEFsQqBmK"
    URL = f"https://tile.googleapis.com/v1/2dtiles/{zoom}/{x}/{y}?session={SESSION}&key={APIKEY}"
    #URL = f"https://tile.googleapis.com/tile/v1/viewport?session={SESSION}&key={APIKEY}&zoom=19&north=32.9&south=32.6&east=-117&west=-117.3"
    response = requests.get(URL)
    #with open('tile1.jpg', 'wb') as file:
    #    file.write(response.content)
    return response.content


def get_adjacent_tile_coord(curr_x, curr_y, direction="north"):
    """
    Given a tile coordinate and cardinal direction, retrievies the adjacent tile in specified direction.
    Returns (x, y) tuple of adjacent tile.
    """
    direction_map = {"north": -1, "south": 1, "east": 1, "west": -1}
    new_x, new_y = curr_x, curr_y
    if direction not in direction_map.keys():
        raise ValueError("Invalid Direction")
    if direction in ["north", "south"]:
        new_y = curr_y + direction_map[direction]
    if direction in ["east", "west"]:
        new_x = curr_x + direction_map[direction]
    return (new_x, new_y)

def display_tile(tile):
    return display.Image(tile)


# %%
class Tile:
    """
    Tile class that holds image data and tile coordinates in line with Google 2D tiles API
    """
    def __init__(self, x, y, zoom=18):
        self.x = x
        self.y = y
        self.zoom = zoom
        self.image = get_tile(self.x, self.y, zoom)

    def get_coords(self):
        return (self.x, self.y)
    
    def get_image(self):
        return self.image
    
    def create_adjacent_tile(self, direction):
        if direction not in ["north", "south", "east", "west"]:
            raise ValueError("Invalid Direction")
        adj_coords = get_adjacent_tile_coord(self.x, self.y, direction)
        adj_x, adj_y = adj_coords[0], adj_coords[1]
        new_tile = Tile(adj_x, adj_y, zoom=self.zoom)
        return new_tile


# %%
    
# Zoom level when fetching initial tile coords have to
# match zoom level when creating new Tile object
tile_coord = fromLatLngToTileCoord(32.7439375, -117.0935763, zoom=18)
test_tile = Tile(tile_coord["x"], tile_coord["y"], zoom=18)
display_tile(test_tile.get_image())



# %%
new_tile = test_tile.create_adjacent_tile("south")
display_tile(new_tile.get_image())
# %%
