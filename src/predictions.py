import pandas as pd
import numpy as np
import pickle as pkl
from dataclasses import dataclass
import streamlit as st


# @dataclass
# class UserInputs:
#     beds: int
#     baths: float
#     sqft: int
#     fitness_center: bool
#     air_conditioning: bool
#     in_unit_washer_dryer: bool
#     laundry_facilities: bool
#     roof: bool
#     concierge: bool
#     garage: bool
#     pets_allowed: bool


def load_model(location: str):
    # Load the xbg and rf models
    with open(f"./models/{location}_rent_prediction.pickle", "rb") as handle:
        xgb = pkl.load(handle)
    return xgb


class Prediction:
    def __init__(self, beds: int, baths: int, sqft: int, amenities: list):
        self.beds = beds
        self.baths = baths
        self.sqft = sqft
        self.fitness_center = 1 if "Fitness Center" in amenities else 0
        self.air_conditioning = 1 if "Air Conditioning" in amenities else 0
        self.in_unit_washer_dryer = 1 if "Washer/Dryer" in amenities else 0
        self.laundry_facilities = 1 if "Laundry Facilities" in amenities else 0
        self.roof = 1 if "Rooftop" in amenities else 0
        self.concierge = 1 if "Concierge" in amenities else 0
        self.garage = 1 if "Parking Garage" in amenities else 0
        self.pets_allowed = 1 if "Pets Allowed" in amenities else 0

    def get_predictions(self, model, locations):

        column_order = [
            "beds",
            "baths",
            "sqft",
            "fitness_center",
            "air_conditioning",
            "in_unit_washer_dryer",
            "laundry_facilities",
            "roof",
            "concierge",
            "garage",
            "dist_seattle",
            "dist_transit",
            "pets_allowed",
            "cluster_id_0.0",
            "cluster_id_1.0",
            "cluster_id_2.0",
            "cluster_id_3.0",
            "cluster_id_4.0",
            "cluster_id_5.0",
        ]
        prediction_locations = locations.assign(**vars(self))
        X = prediction_locations[column_order]
        predictions = np.exp(model.predict(X)).astype(int)

        return predictions

