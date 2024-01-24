#%%
import requests
from IPython import display
from dotenv import load_dotenv
import hashlib
import hmac
import os
import base64
import urllib.parse as urlparse

load_dotenv()

# Pull in API key and Secret key from .env

APIKEY = os.environ.get("API_KEY")
SECRET = os.environ.get("SECRET")

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
def gen_coordinates(start_lat, start_lon, lat_inc=0.00145, lon_inc=-0.00172, grid_size = 5):
    """
    Given a starting latitude and longitude, gathers images in a grid pattern conforming
    to Google API calls with parameters {scale=2, zoom=19, size=640x640}.
    Default lat and lon increments provide images next to each other but not overlapping.
    Args:
    start_lat, start_lon: starting coordinates of grid
    lat_inc, lon_inc: Distance of each image from starting position
    grid_size: Size of grid to collect images, default 5x5
    Returns: List of coordinates that cover inputted grid size
    """
    coord_pairs = []
    for i in range(grid_size):
        for j in range(grid_size):
            curr_lat = round(start_lat + (lat_inc * i), 8)
            curr_lon = round(start_lon + (lon_inc * j), 8)
            curr_coords = f"{curr_lat}, {curr_lon}"
            coord_pairs.append(curr_coords)
    return coord_pairs

# Update parameters of function to be the starting point
g = gen_coordinates(32.7439375, -117.0935763)


# %%
def check_data_dir():
    os.chdir(".")
    print(os.getcwd())
    if os.path.isdir("data"):
        pass
    else:
        os.mkdir("data")

# %%
def get_grid_images(coord_list):
    """
    Given coordinates list, calls Google API to get static images and saves them to data directory 
    """
    check_data_dir()
    for i in range(len(coord_list)):
        print(f"Collecting image {i+1} of {len(coord_list)}")
        curr_coords = coord_list[i]
        URL = f"https://maps.googleapis.com/maps/api/staticmap?center={curr_coords}&scale=2&zoom=19&size=640x640&maptype=satellite&key={APIKEY}"
        response = requests.get(URL)
        img_name = f"loc{curr_coords}"
        with open(f'data/{img_name}.jpg', 'wb') as file:
           file.write(response.content)


get_grid_images(g)


