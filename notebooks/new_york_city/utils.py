import numpy as np
import sqlite3
from sqlite3 import Error


def create_connection(database):
    """Creates a connection to the specified database"""

    conn = None
    try:
        conn = sqlite3.connect(database)
    except Error as e:
        print(e)

    return conn


def calculate_bearing(startLat, startLon, destLat, destLon):

    startLon, startLat, destLon, destLat = map(
        np.radians, [startLon, startLat, destLon, destLat]
    )

    dlon = destLon - startLon
    x = np.cos(destLat) * np.sin(dlon)
    y = np.cos(startLat) * np.sin(destLat) - np.sin(startLat) * np.cos(
        destLat
    ) * np.cos(dlon)

    brng = np.arctan2(x, y)
    return (np.degrees(brng) + 360) % 360


def calculate_distance(startLat, startLon, destLat, destLon):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    startLon, startLat, destLon, destLat = map(
        np.radians, [startLon, startLat, destLon, destLat]
    )

    dlon = destLon - startLon
    dlat = destLat - startLat

    a = (
        np.sin(dlat / 2.0) ** 2
        + np.cos(startLat) * np.cos(destLat) * np.sin(dlon / 2.0) ** 2
    )

    c = 2 * np.arcsin(np.sqrt(a))
    miles = 3958.756 * c
    return miles


def find_string_index(list_of_strings, substring):
    """Returns the index in a list if the substring is in the string from the list"""
    try:
        return next(
            stringIndex
            for stringIndex, string in enumerate(list_of_strings)
            if substring in string
        )
    except:
        return None


# def google_distance_matrix(
#     origin_lat, origin_lng, destination_lat, destination_lng, mode
# ) -> int:

#     # Control the request rate
#     time.sleep(1)

#     # Defaults for the request
#     API_KEY = "AIzaSyAzCVQrg9R2aGgW9yKCz5t06xWrz9E6Gyg"
#     units = "imperial"

#     # Converting the lat/long pairs
#     origins = (origin_lat, origin_lng)
#     destinations = (destination_lat, destination_lng)

#     # Create a departure_time of 8:00AM on the next Monday
#     today = datetime.date.today()
#     next_monday = today + datetime.timedelta(days=-today.weekday(), weeks=1)
#     next_monday = datetime.datetime(
#         next_monday.year, next_monday.month, next_monday.day, 8, 0, 0
#     )

#     # Connect to the Google Maps API
#     gmaps = googlemaps.Client(key=API_KEY)
#     result = gmaps.distance_matrix(
#         origins=origins,
#         destinations=destinations,
#         units=units,
#         mode=mode,
#         departure_time=next_monday,
#     )

#     # Get duration of trip from result JSON
#     commute_time = result["rows"][0]["elements"][0]["duration"]["text"]
#     commute_time = int(re.sub("[^\d\.]", "", commute_time))

#     return commute_time
