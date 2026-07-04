import requests
from datetime import datetime, timedelta
import streamlit as st
import folium
from streamlit_folium import st_folium
import streamlit_searchbox

st.set_page_config(layout="wide", page_title="Singapore Carbon Tracker")

@st.cache_data(ttl=timedelta(days=2))
def fetch_api_token():
    auth_url = "https://www.onemap.gov.sg/api/auth/post/getToken"
    payload = {
        "email": st.secrets["ONEMAP_EMAIL"],
        "password": st.secrets["ONEMAP_PASSWORD"]
    }
    try:
        response = requests.post(auth_url, json=payload).json()
        if "access_token" in response:
            return response["access_token"]
        else:
            st.error("❌ Authentication failed. Check your Streamlit Secrets.")
            return None
    except Exception as e:
        st.error(f"❌ API Connection Error: {e}")
        return None

api_token = fetch_api_token()

if "origin_coords" not in st.session_state:
    st.session_state.origin_coords = None
if "dest_coords" not in st.session_state:
    st.session_state.dest_coords = None
if "last_processed_click" not in st.session_state:
    st.session_state.last_processed_click = None
if "route_results" not in st.session_state:
    st.session_state.route_results = None
if "route_results_car" not in st.session_state:
    st.session_state.route_results_car = None
if "form_version" not in st.session_state:
    st.session_state.form_version = 0
if "prev_orig_text" not in st.session_state:
    st.session_state.prev_orig_text = None
if "prev_dest_text" not in st.session_state:
    st.session_state.prev_dest_text = None

Coordinates_URL = "https://www.onemap.gov.sg/api/common/elastic/search"
Distance_URl = "https://www.onemap.gov.sg/api/public/routingsvc/route"

Now = datetime.now()
Date = Now.strftime("%m-%d-%Y")
Time = Now.strftime("%H:%M:%S")

Bus_Emission_Factor = 0.0737
Train_Emission_Factor = 0.0148
Ice_Car_Emission_Factor = 0.1732
Hybrid_Car_emission_factor = 0.1343
Battery_Electric_Car_Emission_Factor = 0.0618

MODE_SETTINGS = {
    "BUS": {"icon": "🚌", "label": "Bus Line"},
    "SUBWAY": {"icon": "🚇", "label": "MRT Subway"},
    "WALK": {"icon": "🚶", "label": "Walk Journey"}
}

def lookup_address(address_str):
    if not address_str:
        return None
    headers = {"Authorization": api_token}
    params = {"searchVal": address_str, "returnGeom": "Y", "getAddrDetails": "N"}
    try:
        res = requests.get(headers=headers, url=Coordinates_URL, params=params).json()
        if "results" in res and res["results"]:
            return [float(res["results"][0]["LATITUDE"]), float(res["results"][0]["LONGITUDE"])]
    except:
        pass
    return None

def search(searchterm: str) -> list:
    if not searchterm or len(searchterm.strip()) < 2:
        return []
    try:
        headers = {"Authorization": api_token}
        params = {"searchVal": searchterm, "returnGeom": "N", "getAddrDetails": "N"}
        response = requests.get(url=Coordinates_URL, headers=headers, params=params).json()
        if "results" in response and response["results"]:
            return [item["SEARCHVAL"] for item in response["results"] if "SEARCHVAL" in item]
    except:
        pass
    return []

def display_premium_route(response):
    if not response or "plan" not in response or "itineraries" not in response["plan"]:
        st.error("❌ No routing paths found for these positions. Please verify inputs.")
        return

    distance_list = response["plan"]["itineraries"]
    st.markdown("## 🧭 Recommended Transits")

    for idx, leg in enumerate(distance_list):
        Total_Distance = 0
        Total_Carbon_Emmissions = 0

        with st.container(border=True):
            st.markdown(f"### 🗺️ Route Option #{idx + 1}")

            for segment in leg["legs"]:
                mode = segment["mode"].upper().strip()
                distance = float(segment["distance"])
                destination = segment["to"]["name"]
                bus_route = segment.get("route", "")

                segment_duration = float(segment.get("duration", 0))
                segment_time = max(1, round(segment_duration / 60))

                segment_emissions = 0
                if mode == "BUS":
                    segment_emissions = (distance / 1000) * Bus_Emission_Factor
                elif mode == "SUBWAY":
                    segment_emissions = (distance / 1000) * Train_Emission_Factor

                Total_Carbon_Emmissions += segment_emissions
                Total_Distance += distance / 1000

                setting = MODE_SETTINGS.get(mode, {"icon": "📍", "label": mode.title()})
                route_badge = f"• `{bus_route}` " if bus_route else ""

                st.markdown(
                    f"{setting['icon']} **{setting['label']}** {route_badge}"
                    f"→ *{destination.title()}* ({round(distance, 1):,}m | ⏱️ {segment_time} min | 🌱 {round(segment_emissions, 2)} kg CO₂)"
                )

            travel_time = round(leg["duration"] / 60)
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="📏 Total Distance", value=f"{round(Total_Distance, 2)} km")
            with col2:
                st.metric(label="⏱️ Travel Time", value=f"{travel_time} min")
            with col3:
                st.metric(label="🌱 Carbon Footprint", value=f"{round(Total_Carbon_Emmissions, 2)} kg CO₂")

@st.fragment
def map_section():
    st.title("Singapore Eco-Transit Footprint Router")
    st.markdown("Use the search boxes below, or activate a map tool to drop pins directly onto the map.")

    text_column, marker_column = st.columns([7, 3])
    with text_column:
        orig_val = streamlit_searchbox.st_searchbox(
            search,
            label="🛫 Origin Position (Name of place / Postal Code):",
            key=f"orig_search_{st.session_state.form_version}"
        )

        dest_val = streamlit_searchbox.st_searchbox(
            search,
            label="🛬 Destination Position (Name of place / Postal Code):",
            key=f"dest_search_{st.session_state.form_version}"
        )

        if orig_val != st.session_state.prev_orig_text:
            st.session_state.prev_orig_text = orig_val
            if orig_val:
                st.session_state.origin_coords = lookup_address(orig_val)
                st.session_state.route_results = None
                st.session_state.route_results_car = None
            st.rerun()

        if dest_val != st.session_state.prev_dest_text:
            st.session_state.prev_dest_text = dest_val
            if dest_val:
                st.session_state.dest_coords = lookup_address(dest_val)
                st.session_state.route_results = None
                st.session_state.route_results_car = None
            st.rerun()

    with marker_column:
        map_tool = st.radio(
            "📍 Map Interaction Tool:",
            options=["❌ Disabled", "🟢 Set Origin Marker", "🔴 Set Destination Marker"],
            horizontal=True
        )

    calculate_clicked = st.button(label="🚀 Calculate Carbon Emissions", use_container_width=True)
    st.write("")

    singapore_map = folium.Map(
        location=[1.3521, 103.8198],
        zoom_start=11,
        min_zoom=11, max_zoom=18,
        min_lat=1.15, max_lat=1.50, min_lon=103.55, max_lon=104.35,
        max_bounds=True,
        tiles="https://www.onemap.gov.sg/maps/tiles/Default_HD/{z}/{x}/{y}.png",
        attr='<img src="https://www.onemap.gov.sg/web-assets/images/logo/om_logo.png" style="height:20px;width:20px;"/>&nbsp;<a href="https://www.onemap.gov.sg/" target="_blank" rel="noopener noreferrer">OneMap</a>&nbsp;&copy;&nbsp;contributors&nbsp;&#124;&nbsp;<a href="https://www.sla.gov.sg/" target="_blank" rel="noopener noreferrer">Singapore Land Authority</a>',
    )

    marker_layer = folium.FeatureGroup(name="Dynamic Markers")

    if st.session_state.origin_coords is not None:
        folium.Marker(
            location=st.session_state.origin_coords,
            popup="Origin", tooltip="Origin Point",
            icon=folium.Icon(color="green", icon="play")
        ).add_to(marker_layer)

    if st.session_state.dest_coords is not None:
        folium.Marker(
            location=st.session_state.dest_coords,
            popup="Destination", tooltip="Destination Target",
            icon=folium.Icon(color="red", icon="stop")
        ).add_to(marker_layer)

    singapore_map_data: dict = st_folium(
        singapore_map,
        feature_group_to_add=marker_layer,
        width=910, height=450,
        returned_objects=["last_clicked"],
        key="singapore_seamless_map"
    )

    if singapore_map_data and singapore_map_data.get("last_clicked"):
        click_info = singapore_map_data["last_clicked"]
        click_coords = [click_info["lat"], click_info["lng"]]

        if st.session_state.last_processed_click != click_coords:
            st.session_state.last_processed_click = click_coords
            st.session_state.route_results = None
            st.session_state.route_results_car = None

            if map_tool == "🟢 Set Origin Marker":
                st.session_state.origin_coords = click_coords
                st.rerun()
            elif map_tool == "🔴 Set Destination Marker":
                st.session_state.dest_coords = click_coords
                st.rerun()

    if calculate_clicked:
        if st.session_state.origin_coords and st.session_state.dest_coords and api_token:
            with st.spinner("Analyzing Transit Networks..."):
                start_str = f"{st.session_state.origin_coords[0]},{st.session_state.origin_coords[1]}"
                end_str = f"{st.session_state.dest_coords[0]},{st.session_state.dest_coords[1]}"

                Distance_headers = {"Authorization": api_token}

                Distance_params = {
                    "start": start_str, "end": end_str,
                    "routeType": "pt", "date": Date, "time": Time, "mode": "transit"
                }

                Car_params = {
                    "start": start_str, "end": end_str,
                    "routeType": "drive", "date": Date, "time": Time
                }

                pt_response = requests.get(url=Distance_URl, headers=Distance_headers, params=Distance_params)
                car_response = requests.get(url=Distance_URl, headers=Distance_headers, params=Car_params)

                if pt_response.status_code == 429 or car_response.status_code == 429:
                    st.error(
                        "🚦 Whoa there! The routing servers are experiencing extremely high traffic right now. Please wait about 60 seconds and try again.")
                elif pt_response.status_code == 200 and car_response.status_code == 200:
                    st.session_state.route_results = pt_response.json()
                    st.session_state.route_results_car = car_response.json()

                    st.session_state.origin_coords = None
                    st.session_state.dest_coords = None

                    st.rerun()
                else:
                    st.error(
                        "❌ An unexpected error occurred while contacting the routing servers. Please try again later.")

        elif not api_token:
            st.error("Authentication Error. Check API credentials.")
        else:
            st.warning("⚠️ Please ensure BOTH an Origin and a Destination marker are placed.")

    if st.session_state.route_results is not None or st.session_state.route_results_car is not None:
        st.markdown("---")

        tab1, tab2 = st.tabs(["🚌 Public Transport Results", "🚗 Private Car Results"])

        with tab1:
            if st.session_state.route_results:
                display_premium_route(st.session_state.route_results)
            else:
                st.info("No public transit data available for this route.")

        with tab2:
            if st.session_state.route_results_car and "route_summary" in st.session_state.route_results_car:
                summary = st.session_state.route_results_car["route_summary"]
                Car_Total_Distance = summary["total_distance"] / 1000
                Car_Total_Time = round(summary["total_time"] / 60)

                Ice_Car_Emission = Car_Total_Distance * Ice_Car_Emission_Factor
                Hybrid_Car_Emission = Car_Total_Distance * Hybrid_Car_emission_factor
                Battery_Electric_Car_Emission = Car_Total_Distance * Battery_Electric_Car_Emission_Factor

                st.markdown("## 🚗 Private Vehicle Driving Analysis")

                with st.container(border=True):
                    st.markdown("### ⚡ Option #1: Battery Electric Vehicle (BEV)")
                    st.write(
                        "Zero tailpipe exhaust. Emissions reflect the carbon cost of producing electricity on Singapore's power grid.")
                    st.markdown("---")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(label="📏 Route Distance", value=f"{round(Car_Total_Distance, 2)} km")
                    with col2:
                        st.metric(label="⏱️ Driving Time", value=f"{Car_Total_Time} min")
                    with col3:
                        st.metric(label="🌱 Carbon Footprint", value=f"{round(Battery_Electric_Car_Emission, 2)} kg CO₂")

                with st.container(border=True):
                    st.markdown("### 🔋 Option #2: Hybrid Vehicle (HEV)")
                    st.write(
                        "Combines a smaller petrol engine with automated energy recovery brakes to reduce city fuel consumption.")
                    st.markdown("---")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(label="📏 Route Distance", value=f"{round(Car_Total_Distance, 2)} km")
                    with col2:
                        st.metric(label="⏱️ Driving Time", value=f"{Car_Total_Time} min")
                    with col3:
                        st.metric(label="🌱 Carbon Footprint", value=f"{round(Hybrid_Car_Emission, 2)} kg CO₂")

                with st.container(border=True):
                    st.markdown("### ⛽ Option #3: Petrol/Diesel Car (ICE)")
                    st.write("Traditional internal combustion engines rely entirely on petroleum fuel burning.")
                    st.markdown("---")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(label="📏 Route Distance", value=f"{round(Car_Total_Distance, 2)} km")
                    with col2:
                        st.metric(label="⏱️ Driving Time", value=f"{Car_Total_Time} min")
                    with col3:
                        st.metric(label="🌱 Carbon Footprint", value=f"{round(Ice_Car_Emission, 2)} kg CO₂")
            else:
                st.error("❌ No valid driving route could be calculated between these points.")

map_section()
st.markdown("---")
st.caption("""
**Disclaimer:** This tool is an independent project and is not officially affiliated with, endorsed by, or representing the Land Transport Authority (LTA) or the Singapore Land Authority (SLA).

Carbon footprint calculations are standardized estimates based on general emission factors for public transit. Actual emissions may vary based on vehicle model, passenger load, and live traffic conditions. This tool is designed for educational and awareness purposes only.
""")