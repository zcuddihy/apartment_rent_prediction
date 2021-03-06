import numpy as np
import pickle as pkl
import streamlit as st
from .settings import column_orders


def load_model(location: str):
    # Load the xbg and rf models
    with open(
        f"./{location.lower().replace(' ', '_')}/models/{location.lower().replace(' ', '_')}_rent_prediction.pickle",
        "rb",
    ) as handle:
        xgb = pkl.load(handle)
    return xgb


class Prediction:
    def __init__(self, beds: int, baths: int, sqft: int, amenities: list):
        self.beds_times_baths = beds * baths
        self.sqft = sqft
        self.fitness_center = 1 if "Fitness Center" in amenities else 0
        self.air_conditioning = 1 if "Air Conditioning" in amenities else 0
        self.in_unit_washer_dryer = 1 if "Washer/Dryer" in amenities else 0
        self.laundry_facilities = 1 if "Laundry Facilities" in amenities else 0
        self.roof = 1 if "Rooftop" in amenities else 0
        self.concierge = 1 if "Concierge" in amenities else 0
        self.garage = 1 if "Parking Garage" in amenities else 0
        self.pets_allowed = 1 if "Pets Allowed" in amenities else 0
        self.pool = 1 if "Pool" in amenities else 0
        self.elevator = 1 if "Elevator" in amenities else 0
        self.dishwasher = 1 if "Dishwasher" in amenities else 0

    def get_predictions(self, model, prediction_points, location):
        df = prediction_points.copy()

        column_order = column_orders[location]

        df = df.assign(**vars(self))
        X = df[column_order]
        predictions = np.exp(model.predict(X)).astype(int)

        return predictions

