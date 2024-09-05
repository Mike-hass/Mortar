import streamlit as st
import math

# Constants
GRAVITY = 196.2  # Studs/second^2
CHARGE_VELOCITIES = [720, 780, 840, 900, 960]  # Velocities for C0 to C4 in Studs/Second
MAX_ANGLE = 85.25  # Maximum angle of elevation in degrees
MIN_ANGLE = 44.25  # Minimum angle of elevation in degrees

# Function to calculate the bearing angle
def calculate_bearing(mortar_coords, target_coords):
    dx = target_coords[0] - mortar_coords[0]
    dz = target_coords[2] - mortar_coords[2]
    bearing = math.atan2(dz, dx) * (180 / math.pi)
    bearing -= 90
    if bearing < 0:
        bearing += 360
    return bearing

# Function to calculate the horizontal range
def calculate_horizontal_range(mortar_coords, target_coords):
    dx = target_coords[0] - mortar_coords[0]
    dz = target_coords[2] - mortar_coords[2]
    return math.sqrt(dx**2 + dz**2)

# Function to calculate elevation angles and time of flight
def calculate_elevations_and_time_of_flight(mortar_coords, target_coords):
    horizontal_range = calculate_horizontal_range(mortar_coords, target_coords)
    dy = target_coords[1] - mortar_coords[1]
    results = []

    for i, velocity in enumerate(CHARGE_VELOCITIES):
        try:
            term = (velocity**4) - GRAVITY * (GRAVITY * horizontal_range**2 + 2 * dy * velocity**2)
            if term < 0:
                results.append((None, None, i))
                continue
            sqrt_term = math.sqrt(term)
            angle_radians_1 = math.atan((velocity**2 + sqrt_term) / (GRAVITY * horizontal_range))
            angle_radians_2 = math.atan((velocity**2 - sqrt_term) / (GRAVITY * horizontal_range))
            angle_degrees_1 = math.degrees(angle_radians_1)
            angle_degrees_2 = math.degrees(angle_radians_2)

            valid_angle_1 = MIN_ANGLE <= angle_degrees_1 <= MAX_ANGLE
            valid_angle_2 = MIN_ANGLE <= angle_degrees_2 <= MAX_ANGLE

            time_of_flight_1 = (velocity * math.sin(angle_radians_1) + math.sqrt((velocity * math.sin(angle_radians_1))**2 + 2 * GRAVITY * dy)) / GRAVITY if valid_angle_1 else None
            time_of_flight_2 = (velocity * math.sin(angle_radians_2) + math.sqrt((velocity * math.sin(angle_radians_2))**2 + 2 * GRAVITY * dy)) / GRAVITY if valid_angle_2 else None

            if valid_angle_1:
                results.append((angle_degrees_1, time_of_flight_1, i))
            elif valid_angle_2:
                results.append((angle_degrees_2, time_of_flight_2, i))
            else:
                results.append((None, None, i))
        except ValueError:
            results.append((None, None, i))
    return results

# Function to calculate mortar settings
def mortar_calculator(mortar_coords, target_coords):
    bearing = calculate_bearing(mortar_coords, target_coords)
    charge_results = calculate_elevations_and_time_of_flight(mortar_coords, target_coords)
    return bearing, charge_results

# Streamlit app interface
st.title("Mortar Calculator")

# Input fields
st.sidebar.header("Launch Point (x0, y0, z0)")
x0 = st.sidebar.number_input("x0", value=0.0)
y0 = st.sidebar.number_input("y0", value=0.0)
z0 = st.sidebar.number_input("z0", value=0.0)

st.sidebar.header("Target Point (xt, yt, zt)")
xt = st.sidebar.number_input("xt", value=0.0)
yt = st.sidebar.number_input("yt", value=0.0)
zt = st.sidebar.number_input("zt", value=0.0)

# Perform calculation when the button is clicked
if st.button("Calculate"):
    mortar_coords = (x0, y0, z0)
    target_coords = (xt, yt, zt)
    bearing, charge_results = mortar_calculator(mortar_coords, target_coords)
    distance = calculate_horizontal_range(mortar_coords, target_coords)

    # Display results
    st.subheader("Results")
    st.write(f"Bearing: **{bearing:.2f} degrees**")
    st.write(f"Distance: **{distance:.2f} studs**")
    
    for angle, time_of_flight, charge_mode in charge_results:
        if angle is not None:
            st.write(f"**Elevation Angle for C{charge_mode}:** {angle:.2f} degrees")
            st.write(f"**Time of Flight for C{charge_mode}:** {time_of_flight:.2f} seconds")
        else:
            st.write(f"No feasible solution for C{charge_mode} within angle limits.")
