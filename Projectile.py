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
    
    # Bearing 1 calculation
    bearing_1 = math.atan2(dz, dx) * (180 / math.pi)
    bearing_1 -= 90
    if bearing_1 < 0:
        bearing_1 += 360
    
    # Bearing 2 calculation (opposite bearing)
    bearing_2 = (bearing_1 + 180) % 360
    
    return bearing_1, bearing_2

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
        term = (velocity**4) - GRAVITY * (GRAVITY * horizontal_range**2 + 2 * dy * velocity**2)

        # Check if the term is negative (no real solution possible)
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
    
    return results

# Function to calculate mortar settings
def mortar_calculator(mortar_coords, target_coords):
    bearing_1, bearing_2 = calculate_bearing(mortar_coords, target_coords)
    charge_results = calculate_elevations_and_time_of_flight(mortar_coords, target_coords)
    return bearing_1, bearing_2, charge_results

# Streamlit app interface
st.title("Mortar Calculator")

# Single-line input for coordinates
st.sidebar.header("Launch Point (x0, y0, z0)")
launch_coords = st.sidebar.text_input("Enter launch coordinates as x0, y0, z0:", "0, 0, 0")
x0, y0, z0 = map(float, launch_coords.split(','))

st.sidebar.header("Target Point (xt, yt, zt)")
target_coords = st.sidebar.text_input("Enter target coordinates as xt, yt, zt:", "0, 0, 0")
xt, yt, zt = map(float, target_coords.split(','))

# Perform calculation when the button is clicked
if st.button("Calculate"):
    mortar_coords = (x0, y0, z0)
    target_coords = (xt, yt, zt)
    bearing_1, bearing_2, charge_results = mortar_calculator(mortar_coords, target_coords)
    distance = calculate_horizontal_range(mortar_coords, target_coords)

    # Display results
    st.subheader("Results")
    st.write(f"Bearing 1: **{bearing_1:.2f} degrees**")
    st.write(f"Bearing 2 (Opposite): **{bearing_2:.2f} degrees**")
    st.write(f"Distance: **{distance:.2f} studs**")
    
    for angle, time_of_flight, charge_mode in charge_results:
        if angle is not None:
            st.write(f"**Elevation Angle for C{charge_mode}:** {angle:.2f} degrees")
            st.write(f"**Time of Flight for C{charge_mode}:** {time_of_flight:.2f} seconds")
        else:
            st.write(f"No feasible solution for C{charge_mode} within angle limits.")
