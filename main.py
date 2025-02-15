import os
import traci
import time
import json
from ultralytics import YOLO
import cv2

# Load YOLO model
model = YOLO("yolov8n.pt")

# Start SUMO simulation
sumo_binary = "sumo-gui"  # Use "sumo" if running without GUI
sumo_config_path = os.path.join("sumo_simulation", "config.sumocfg")
sumo_cmd = ["sumo-gui", "-c", "sumo_simulation/config.sumocfg"]

# Start SUMO with TraCI
time.sleep(2)  # Wait for SUMO to start
traci.start(sumo_cmd)
traci.start(sumo_cmd)
print("SUMO started successfully!")

def detect_vehicles(frame):
    """Detect vehicles and return density count."""
    results = model(frame)
    vehicle_count = {"car": 0, "motorcycle": 0, "bus": 0, "truck": 0}

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            label = model.names[cls]
            if label in vehicle_count:
                vehicle_count[label] += 1

    return vehicle_count

while traci.simulation.getMinExpectedNumber() > 0:
    frame = cv2.imread("traffic_cam.jpg")  # Replace with actual camera/video frame
    vehicle_density = detect_vehicles(frame)

    # Set traffic light timing based on density
    green_time = 30  # Default green light time
    if vehicle_density["car"] > 10 or vehicle_density["bus"] > 5:
        green_time = 50  # Increase green time if traffic is high
    elif sum(vehicle_density.values()) < 3:
        green_time = 10  # Reduce green time if traffic is low

    traci.trafficlight.setPhaseDuration("center", green_time)
    traci.simulationStep()

traci.close()
