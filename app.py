#%%
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import json
import pickle as pkl
from xgboost import XGBRegressor
from src.predictions import load_model, Prediction

st.set_page_config(layout="wide")
st.title("Apartment Rental Price Prediction")


def load_prediction_locations(location: str):
    data_location = f"./data/processed/{location.lower()}_prediction_location.csv"
    locations = pd.read_csv(data_location)
    return locations


@st.cache
def load_geojson(location: str):
    with open(f"./data/geojson_files/{location}-neighborhoods.geojson") as f:
        geojson = json.load(f)
    return geojson


def plot_results(locations, geojson, dist_transit):
    # Get median for each neighborhood
    nhood_rent = (
        locations[locations.dist_transit < dist_transit]
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

    fig.update_layout(height=1000, width=1000)
    st.plotly_chart(fig, use_container_width=True)


# user_inputs = UserInputs(
#     beds=st.sidebar.number_input("Beds", 0, 4, 1),
#     baths=st.sidebar.number_input("Baths", 0, 4, 1),
#     sqft=st.sidebar.slider("Square Feet", 50, 2000, 500),
#     fitness_center=1,
#     air_conditioning=1,
#     in_unit_washer_dryer=1,
#     laundry_facilities=1,
#     roof=1,
#     concierge=1,
#     garage=1,
#     pets_allowed=1,
# )


# user_inputs = {
#     "beds": user_inputs.beds,
#     "baths": user_inputs.baths,
#     "sqft": np.log(user_inputs.sqft),
#     "fitness_center": 0.0,
#     "air_conditioning": 0.0,
#     "in_unit_washer_dryer": 1.0,
#     "laundry_facilities": 0.0,
#     "roof": 0.0,
#     "concierge": 0.0,
#     "garage": 1.0,
#     "pets_allowed": 1.0,
# }

# locations["Rent"] = make_predictions(model, locations)


def main():
    # Setup sidebar for user inputs
    with st.sidebar:
        beds = st.number_input("Beds", 0, 4, 1)
        baths = st.number_input("Baths", 0, 4, 1)
        sqft = st.slider("Square Feet", 50, 2000, 500)
        transit_distance = st.slider(
            "Max Distance to Transit (miles)", 0.00, 1.00, 0.50
        )
        amenities = st.multiselect(
            "Select additional amenities",
            [
                "Fitness Center",
                "Air Conditioning",
                "Washer/Dryer",
                "Laundry Facilities",
                "Rooftop",
                "Concierge",
                "Parking Garage",
                "Pets Allowed",
            ],
        )

    # Setup data for model
    locations = load_prediction_locations("seattle")
    geojson = load_geojson("seattle")
    model = load_model("seattle")

    # Get predictions
    rent = Prediction(beds=beds, baths=baths, sqft=sqft, amenities=amenities)
    locations["Rent"] = rent.get_predictions(model, locations)

    # Plot results
    plot_results(locations, geojson, transit_distance)


if __name__ == "__main__":
    main()
