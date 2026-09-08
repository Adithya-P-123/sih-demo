import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
from collections import deque

st.set_page_config(page_title="SIH26037: AV Path Planner", layout="centered")
st.title("🚗 Chaotic Road Path Planner Demo")
st.write("Scan successful! Adjust the parameters below to test our local path planner's collision avoidance.")

# User controls for the phone screen
traffic_density = st.slider("Select Traffic Congestion Level", 1, 5, 2)
obstacle_type = st.selectbox("Select Obstacle to Inject", ["Static Pothole", "Erratic Auto-Rickshaw", "Wandering Animal"])

# Generate a 2D environment grid
grid_size = 20
grid = np.zeros((grid_size, grid_size), dtype=int)

# Define start and goal
start = (0, 10)
goal = (19, 10)

# Simulate traffic obstacles based on slider
np.random.seed(42)
for _ in range(traffic_density * 4):
    obs_x = np.random.randint(3, 17)
    obs_y = np.random.randint(2, 18)
    grid[obs_x, obs_y] = 1  # 1 represents an obstacle

# Inject the selected obstacle into the center lane.
grid[10, 10] = 1

# Keep manually placed obstacles across Streamlit reruns.
if "user_obstacles" not in st.session_state:
    st.session_state.user_obstacles = set()
if "execution_step" not in st.session_state:
    st.session_state.execution_step = 0

st.subheader("Place an obstacle")
st.caption("Choose any grid cell, including one currently used by the planned path.")
obstacle_col, obstacle_row, add_col = st.columns(3)
with obstacle_col:
    obstacle_x = st.number_input("Column (0-19)", min_value=0, max_value=grid_size - 1, value=10, step=1)
with obstacle_row:
    obstacle_y = st.number_input("Row (0-19)", min_value=0, max_value=grid_size - 1, value=10, step=1)
with add_col:
    st.write("")
    st.write("")
    if st.button("Add obstacle", use_container_width=True):
        st.session_state.user_obstacles.add((int(obstacle_x), int(obstacle_y)))
        st.session_state.execution_step = 0
    if st.button("Clear obstacles", use_container_width=True):
        st.session_state.user_obstacles.clear()
        st.session_state.execution_step = 0

for obstacle_x, obstacle_y in st.session_state.user_obstacles:
    grid[obstacle_x, obstacle_y] = 1

if st.session_state.user_obstacles:
    st.write("User obstacles:", ", ".join(f"({x}, {y})" for x, y in sorted(st.session_state.user_obstacles)))

# Find a complete route through every free cell instead of making local nudges.
planned_path = []
if grid[start] == 0 and grid[goal] == 0:
    previous = {start: None}
    cells_to_visit = deque([start])
    while cells_to_visit:
        current_x, current_y = cells_to_visit.popleft()
        if (current_x, current_y) == goal:
            break
        neighbors = (
            (current_x + 1, current_y),
            (current_x, current_y + 1),
            (current_x, current_y - 1),
            (current_x - 1, current_y),
        )
        for neighbor_x, neighbor_y in neighbors:
            neighbor = (neighbor_x, neighbor_y)
            if (0 <= neighbor_x < grid_size and 0 <= neighbor_y < grid_size
                    and grid[neighbor] == 0 and neighbor not in previous):
                previous[neighbor] = (current_x, current_y)
                cells_to_visit.append(neighbor)

    if goal in previous:
        current = goal
        while current is not None:
            planned_path.append(current)
            current = previous[current]
        planned_path.reverse()

if not planned_path:
    st.error("No clear route to the destination with the current obstacles.")
    planned_path = [start]

path_x = [position[0] for position in planned_path]
path_y = [position[1] for position in planned_path]

st.subheader("Path execution")
obstacle_markers = {
    "Static Pothole": "X",
    "Erratic Auto-Rickshaw": "s",
    "Wandering Animal": "^",
}

def render_path(execution_step, chart):
    vehicle_position = planned_path[execution_step]
    executed_x = path_x[: execution_step + 1]
    executed_y = path_y[: execution_step + 1]
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.imshow(grid.T, cmap="Blues", origin="lower")
    ax.plot(path_x, path_y, color="red", marker="o", markersize=4, label="Adaptive Trajectory")
    ax.plot(executed_x, executed_y, color="limegreen", linewidth=3, label="Executed Path")
    ax.scatter([vehicle_position[0]], [vehicle_position[1]], color="green", s=100, label="AV Position", zorder=5)
    ax.scatter([goal[0]], [goal[1]], color="gold", s=100, label="Destination", zorder=5)
    for obstacle_x, obstacle_y in st.session_state.user_obstacles:
        ax.scatter(
            [obstacle_x],
            [obstacle_y],
            color="darkred",
            marker=obstacle_markers[obstacle_type],
            s=55,
            edgecolors="white",
            linewidths=0.7,
            zorder=6,
        )
    ax.scatter(
        [10], [10], color="darkred", marker=obstacle_markers[obstacle_type],
        s=55, edgecolors="white", linewidths=0.7, label="Obstacle", zorder=6,
    )
    ax.legend(loc="upper left", fontsize=7)
    ax.axis("off")
    chart.pyplot(fig)
    plt.close(fig)

chart = st.empty()
can_execute = planned_path[-1] == goal
if st.button("Execute planned path", type="primary", use_container_width=True, disabled=not can_execute):
    for step in range(len(planned_path)):
        st.session_state.execution_step = step
        render_path(step, chart)
        time.sleep(0.3)

execution_step = min(st.session_state.execution_step, len(planned_path) - 1)
render_path(execution_step, chart)
vehicle_position = planned_path[execution_step]
if execution_step == len(planned_path) - 1 and vehicle_position == goal and can_execute:
    st.success("Planned path executed successfully.")
else:
    st.info(f"Vehicle is at ({vehicle_position[0]}, {vehicle_position[1]}). Click Execute planned path to run the route.")
