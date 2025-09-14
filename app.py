import streamlit as st
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image

# Load YOLO model
model = YOLO("best.pt")  # your trained pothole model

st.title("🕳️ Pothole Detection Portal")
st.write("Upload an image to detect potholes and calculate size, risk, and difficulty.")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Convert uploaded file to OpenCV image
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)

    st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), caption="Uploaded Image", use_column_width=True)

    # Run YOLO detection
    results = model(img)

    for result in results:
        boxes = result.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls = int(box.cls[0])

            # Draw bounding box
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Example size/risk/difficulty calculation (you already had this logic)
            width = x2 - x1
            height = y2 - y1
            area = width * height

            if area < 5000:
                risk = "Low"
                difficulty = "Easy"
            elif area < 15000:
                risk = "Moderate"
                difficulty = "Medium"
            else:
                risk = "High"
                difficulty = "Difficult"

            label = f"Pothole | Risk: {risk} | Difficulty: {difficulty}"
            cv2.putText(img, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Show result image
    st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), caption="Detection Result", use_column_width=True)


