import streamlit as st
from ultralytics import YOLO
import cv2
import numpy as np
import base64
from datetime import datetime
from PIL import Image

# Load YOLO model
model = YOLO("best.pt")

# Function to analyze pothole danger
def analyze_pothole_danger(area, confidence):
    if area > 15000:
        risk = "🚨 EXTREME RISK"
        impact = "• Vehicle damage guaranteed\n• Tire bursts likely\n• Suspension destruction\n• High accident risk\n• Immediate repair required"
        severity = "95%"
        repair_urgency = "IMMEDIATE (Within 24 hours)"
        cost_estimate = "₹15,000 - ₹50,000"
    elif area > 10000:
        risk = "🚨 HIGH RISK"
        impact = "• Significant vehicle damage\n• Tire damage probable\n• Suspension stress\n• Accident risk\n• Urgent repair needed"
        severity = "80%"
        repair_urgency = "URGENT (Within 48 hours)"
        cost_estimate = "₹8,000 - ₹20,000"
    elif area > 5000:
        risk = "⚠️ MEDIUM RISK"
        impact = "• Moderate vehicle wear\n• Wheel alignment issues\n• Uncomfortable ride\n• Repair recommended"
        severity = "60%"
        repair_urgency = "PRIORITY (Within 1 week)"
        cost_estimate = "₹3,000 - ₹10,000"
    else:
        risk = "✅ LOW RISK"
        impact = "• Minor vehicle wear\n• Reduced ride quality\n• Maintenance suggested"
        severity = "30%"
        repair_urgency = "SCHEDULED (Within 2 weeks)"
        cost_estimate = "₹1,000 - ₹5,000"

    if confidence < 0.6:
        risk += " (Low Confidence)"
        severity = "25%"

    return risk, impact, severity, repair_urgency, cost_estimate

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="Pothole Detection AI", layout="centered")

st.title("🕳️ Pothole Detection AI")
st.write("Upload an image to analyze potholes and assess road safety risks.")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Read image
    image = Image.open(uploaded_file).convert("RGB")
    img_array = np.array(image)

    # Run YOLO model
    results = model.predict(img_array, save=False, conf=0.5)
    result = results[0]

    # Annotated image
    annotated_img = result.plot()
    st.image(annotated_img, caption="Detected Potholes", use_column_width=True)

    # Analysis
    analysis_data = []
    for i, box in enumerate(result.boxes):
        conf = float(box.conf[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        width = x2 - x1
        height = y2 - y1
        area = width * height

        risk, impact, severity, repair_urgency, cost_estimate = analyze_pothole_danger(area, conf)

        analysis_data.append({
            'id': i + 1,
            'confidence': f"{conf:.2%}",
            'width': width,
            'height': height,
            'area': area,
            'risk_level': risk,
            'impact': impact,
            'severity': severity,
            'repair_urgency': repair_urgency,
            'cost_estimate': cost_estimate,
            'location': f"X:{x1}-{x2}, Y:{y1}-{y2}"
        })

    # Overall risk
    overall_risk = "🚨 EXTREME" if len(analysis_data) > 5 else \
                   "⚠️ HIGH" if len(analysis_data) > 2 else \
                   "🟡 MODERATE" if len(analysis_data) > 0 else "✅ CLEAR"

    st.subheader("📊 Analysis Report")
    st.write(f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.write(f"**Overall Road Risk:** {overall_risk}")

    for p in analysis_data:
        st.markdown(f"""
        ### 🕳️ Pothole ID {p['id']}
        - **Confidence:** {p['confidence']}
        - **Dimensions:** {p['width']}x{p['height']} (Area: {p['area']})
        - **Risk:** {p['risk_level']}
        - **Severity:** {p['severity']}
        - **Urgency:** {p['repair_urgency']}
        - **Cost:** {p['cost_estimate']}
        - **Location:** {p['location']}
        - **Impact:**  
          ```
          {p['impact']}
          ```
        """)

