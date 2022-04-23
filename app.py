#%%
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import json
from src.predictions import load_model, Prediction
from src.settings import location_centroid

st.set_page_config(layout="wide")
st.title("Apartment Rental Price Estimation")


@st.cache
def load_prediction_points(location: str):
    data_location = f"./{location.lower().replace(' ','_')}/models/{location.lower().replace(' ','_')}_prediction_location.csv"
    locations = pd.read_csv(data_location)
    return locations


def load_geojson(location: str):
    with open(
        f"./{location.lower().replace(' ','_')}/data/external/neighborhood_boundaries.geojson"
    ) as f:
        geojson = json.load(f)
    return geojson


def plot_results(df, geojson, max_dist_transit, location):
    # Get median for each neighborhood
    nhood_rent = (
        df[df.dist_transit < max_dist_transit]
        .groupby(["neighborhood"], as_index=False)["Rent"]
        .median()
    )
    nhood_rent.Rent = nhood_rent.Rent.astype(int)

    # Set map center
    map_center = location_centroid[location]

    featureidkey_location = {
        "Seattle": "properties.S_HOOD",
        "New York City": "properties.ntaname",
    }

    fig = px.choropleth_mapbox(
        nhood_rent,
        geojson=geojson,
        locations="neighborhood",
        featureidkey=featureidkey_location[location],
        color="Rent",
        mapbox_style="carto-positron",
        zoom=10.8,
        center={"lat": map_center["lat"], "lon": map_center["lon"]},
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
                    "Elevator",
                    "Dishwasher",
                    "Parking Garage",
                    "Pets Allowed",
                ],
            )
            submit = st.form_submit_button("Get Estimated Values")

    # Setup data for model
    prediction_points = load_prediction_points(location)
    geojson = load_geojson(location)
    model = load_model(location)

    # Get predictions
    predictor = Prediction(
        beds=beds, baths=baths, sqft=np.log(sqft), amenities=amenities
    )
    predictions = predictor.get_predictions(model, prediction_points, location)
    results = pd.DataFrame(
        {
            "neighborhood": prediction_points.neighborhood,
            "Rent": predictions,
            "dist_transit": prediction_points.loc[:, "dist_transit"],
        }
    )
    # Plot results
    plot_results(results, geojson, transit_distance, location)


if __name__ == "__main__":
    main()
