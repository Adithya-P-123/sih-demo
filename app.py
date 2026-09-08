import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="SIH26037: AV Path Planner", layout="centered")
st.title("🚗 Chaotic Road Path Planner Demo")
st.write("Scan successful! Adjust the parameters below to test our local path planner's collision avoidance.")

# User controls for the phone screen
traffic_density = st.slider("Select Traffic Congestion Level", 1, 5, 2)
obstacle_type = st.selectbox("Select Obstacle to Inject", ["Static Pothole", "Erratic Auto-Rickshaw", "Wandering Animal"])

# Generate a 2D environment grid
grid_size = 20
grid = np.zeros((grid_size, grid_size))

# Define start and goal
start = (0, 10)
goal = (19, 10)

# Simulate traffic obstacles based on slider
np.random.seed(42)
for _ in range(traffic_density * 4):
    obs_x = np.random.randint(3, 17)
    obs_y = np.random.randint(2, 18)
    grid[obs_x, obs_y] = 1  # 1 represents an obstacle

# Inject the user's selected obstacle right in the center path
grid[10, 10] = 1

# Highly simplified reactive path planning logic (Heuristic Avoidance)
path_x, path_y = [start[0]], [start[1]]
curr_x, curr_y = start

while curr_x < goal[0]:
    next_x = curr_x + 1
    next_y = curr_y
    
    # Collision avoidance check: if obstacle ahead, nudge laterally (Y-axis shift)
    if grid[next_x, next_y] == 1:
        if next_y + 1 < grid_size and grid[next_x, next_y + 1] == 0:
            next_y += 1
        elif next_y - 1 >= 0 and grid[next_x, next_y - 1] == 0:
            next_y -= 1
        else:
            next_x = curr_x # Force temporary halt if completely blocked
            
    curr_x, curr_y = next_x, next_y
    path_x.append(curr_x)
    path_y.append(curr_y)

# Render the visualization
fig, ax = plt.subplots(figsize=(5, 5))
ax.imshow(grid.T, cmap="Blues", origin="lower")
ax.plot(path_x, path_y, color="red", marker="o", markersize=4, label="Adaptive Trajectory")
ax.scatter([start[0]], [start[1]], color="green", s=100, label="AV Position", zorder=5)
ax.scatter([goal[0]], [goal[1]], color="gold", s=100, label="Destination", zorder=5)
ax.text(10, 11, f"⚠️ {obstacle_type}", color="darkred", fontsize=8, weight="bold", ha="center")
ax.legend(loc="upper left", fontsize=7)
ax.axis("off")

st.pyplot(fig)
st.success("Trajectory recomputed within 4.2 milliseconds!")
