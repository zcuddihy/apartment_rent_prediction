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


@st.cache
def load_prediction_locations(location: str):
    data_location = f"./{location}/models/{location.lower().replace(' ','_')}_prediction_location.csv"
    locations = pd.read_csv(data_location)
    return locations


@st.cache
def load_geojson(location: str):
    with open(f"./data/geojson_files/{location}-neighborhoods.geojson") as f:
        geojson = json.load(f)
    return geojson


def plot_results(df, geojson, max_dist_transit):
    # Get median for each neighborhood
    nhood_rent = (
        df[df.dist_transit < max_dist_transit]
        .groupby(["neighborhood"], as_index=False)["Rent"]
        .median()
    )
    nhood_rent.Rent = nhood_rent.Rent.astype(int)
    nhood_rent = nhood_rent[nhood_rent["neighborhood"].str.strip().astype(bool)]

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


def main():
    # Setup sidebar for user inputs
    with st.form(key="Form1"):
        with st.sidebar:
            location = st.selectbox(
                "Select the location",
                ("Seattle", "Bay Area", "Chicago", "New York City"),
            )
            beds = st.number_input("Beds", 0, 3, 1)
            baths = st.number_input("Baths", 0, 3, 1)
            sqft = st.slider("Square Feet", 200, 1500, 500, 10)
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
                    "Dishwasher",
                    "Rooftop",
                    "Concierge",
                    "Pool",
                    "Parking Garage",
                    "Pets Allowed",
                ],
            )
            submit = st.form_submit_button("Get Predictions")

    # Setup data for model
    location = load_prediction_locations("seattle")
    geojson = load_geojson("seattle")
    model = load_model("seattle")

    # Get predictions
    predictor = Prediction(
        beds=beds, baths=baths, sqft=np.log(sqft), amenities=amenities
    )
    predictions = predictor.get_predictions(model, location)
    results = pd.DataFrame(
        {
            "neighborhood": location.neighborhood,
            "Rent": predictions,
            "dist_transit": location.loc[:, "dist_transit"],
        }
    )
    # Plot results
    plot_results(results, geojson, transit_distance)


if __name__ == "__main__":
    main()
