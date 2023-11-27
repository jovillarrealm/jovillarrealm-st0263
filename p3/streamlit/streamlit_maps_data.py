import streamlit as st
import json
import matplotlib.pyplot as plt
import datetime
import googlemaps


api_key = None
with open("secret.json") as mapi:
    api_key = json.load(mapi)["MAPS_API_KEY"]
    
gmaps = googlemaps.Client(key=api_key)

def get_traffic_data(origin, destination):
    now = datetime.datetime.utcnow()
    directions_result = gmaps.directions(origin, destination, mode="driving", departure_time=now, traffic_model="best_guess")
    print(directions_result)
    traffic_data = directions_result[0]["legs"][0]["duration_in_traffic"]
    return traffic_data


def visualize_traffic_data(traffic_data):
    # Extract traffic data
    traffic_density = [segment["traffic_density"] for segment in traffic_data]
    distance = [segment["distance"] for segment in traffic_data["segments"]]

    # Create a visualization
    plt.figure(figsize=(10, 6))
    plt.plot(distance, traffic_density)
    plt.xlabel("Distance (m)")
    plt.ylabel("Traffic Density")
    plt.title("Traffic Density along Route")
    plt.show()

st.title("Real-time Traffic Visualization")

#origin = st.text_input("Origin:", placeholder="Los Angeles, CA")
#destination = st.text_input("Destination:", placeholder="San Francisco, CA")
origin = "Los Angeles, CA"
destination = "San Francisco, CA"

if st.button("Get Traffic Data"):
    if origin and destination:
        traffic_data = get_traffic_data(origin, destination)
        visualize_traffic_data(traffic_data)
