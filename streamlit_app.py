import streamlit as st
import numpy as np
import plotly.express as px

# 1. Set up the UI layout
st.title("UHI Spatial Variables Simulator")
st.sidebar.header("Urban Parameters")

# 2. Create the interactive sliders
veg_cover = st.sidebar.slider("Vegetation Cover (%)", 0, 100, 50)
build_density = st.sidebar.slider("Building Density", 1, 10, 5)
albedo = st.sidebar.slider("Surface Albedo (0=Dark, 1=Light)", 0.0, 1.0, 0.2)

# 3. The Math Engine: Calculate base temperature
# High vegetation lowers temp, high density raises it, high albedo (reflective) lowers it.
base_temp = 30.0 
simulated_temp = base_temp - (veg_cover * 0.05) + (build_density * 0.8) - (albedo * 5.0)

# 4. Generate the Spatial Data (Simulating a raster)
# Create a 50x50 pixel grid with some random spatial noise for realism
grid_size = 50
noise = np.random.normal(0, 0.5, (grid_size, grid_size))
heat_map_data = np.full((grid_size, grid_size), simulated_temp) + noise

# 5. Render the Visuals
fig = px.imshow(heat_map_data, color_continuous_scale='RdBu_r', 
                title=f"Simulated City Block (Avg Temp: {simulated_temp:.2f}°C)")
st.plotly_chart(fig)
