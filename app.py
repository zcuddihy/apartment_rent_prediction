#%%
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import json
import pickle as pkl
from xgboost import XGBRegressor

st.title("Uber pickups in NYC")


@st.cache
def load_prediction_locations(location: str):
    data_location = f"./data/processed/{location.lower()}_prediction_location.csv"
    locations = pd.read_csv(data_location)
    return locations


@st.cache
def load_geojson(location: str):
    with open(f"./data/geojson_files/{location}-neighborhoods.geojson") as f:
        geojson = json.load(f)
    return geojson


def load_model(location: str):
    # Load the xbg and rf models
    with open(f"./models/{location}_rent_prediction.pickle", "rb") as handle:
        xgb = pkl.load(handle)
    return xgb


def make_predictions(model, locations):
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

    X = locations[column_order]
    predictions = np.exp(model.predict(X)).astype(int)

    return predictions


def plot_results(locations, geojson):
    # Get median for each neighborhood
    dist_limit = 0.2
    nhood_rent = (
        locations[locations.dist_transit < dist_limit]
        .groupby(["neighborhood"], as_index=False)["Rent"]
        .median()
    )
    nhood_rent.Rent = nhood_rent.Rent.astype(int)
    nhood_rent = nhood_rent[nhood_rent["neighborhood"].str.strip().astype(bool)]
    nhood_rent.head()

    # Set map center
    downtown_seattle = {"lat": 47.604013, "lon": -122.335167}

    fig = px.choropleth_mapbox(
        nhood_rent,
        geojson=geojson,
        locations="neighborhood",
        featureidkey="properties.S_HOOD",
        color="Rent",
        mapbox_style="carto-positron",
        zoom=10.8,
        center={"lat": downtown_seattle["lat"], "lon": downtown_seattle["lon"]},
        opacity=0.7,
        hover_name="neighborhood",
    )

    title_settings = {
        "text": "Predicted Rent ($): 1 Bed, 1 Bath, 584sqft",
        "font_size": 25,
        "y": 0.975,
        "x": 0.5,
        "xanchor": "center",
        "yanchor": "top",
    }

    fig.update_layout(height=1000, width=1000)
    fig.update_layout(title=title_settings)
    st.plotly_chart(fig)


if __name__ == "__main__":
    locations = load_prediction_locations("seattle")
    geojson = load_geojson("seattle")
    model = load_model("seattle")

    user_inputs = {
        "beds": 1.0,
        "baths": 1,
        "sqft": np.log(584),
        "fitness_center": 0.0,
        "air_conditioning": 0.0,
        "in_unit_washer_dryer": 1.0,
        "laundry_facilities": 0.0,
        "roof": 0.0,
        "concierge": 0.0,
        "garage": 1.0,
        "pets_allowed": 1.0,
    }

    locations = locations.assign(**user_inputs)
    locations["Rent"] = make_predictions(model, locations)

    plot_results(locations, geojson)
