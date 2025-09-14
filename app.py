from flask import Flask, request, render_template_string
import os
import cv2
import numpy as np
from datetime import datetime
import base64
import traceback

app = Flask(__name__)

# Try to load ultralytics YOLO model if available and model file present.
MODEL_PATH = os.path.join("runs", "detect", "train5", "weights", "best.pt")
model = None
MODEL_AVAILABLE = False

try:
    from ultralytics import YOLO
    if os.path.isfile(MODEL_PATH):
        try:
            model = YOLO(MODEL_PATH)
            MODEL_AVAILABLE = True
            print(f"[INFO] Loaded YOLO model from {MODEL_PATH}")
        except Exception as e:
            print("[WARN] ultralytics installed but failed to load model:", e)
            MODEL_AVAILABLE = False
    else:
        print(f"[WARN] Model file not found at {MODEL_PATH}. Running in demo mode.")
except Exception as e:
    print("[WARN] ultralytics not available. Running in demo mode.", str(e))

def analyze_pothole_danger(area, confidence):
    """Analyze pothole danger level with detailed assessment"""
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

HOME_HTML = '''<!DOCTYPE html>
<html>
<head>
    <title>Pothole Detection AI</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, Helvetica, sans-serif; background:#0f172a; color:#e2e8f0; margin:0; padding:0; }
        .container { max-width:600px; margin:80px auto; background:rgba(15,23,42,0.95); padding:34px; border-radius:14px; text-align:center; }
        h1 { font-size:28px; margin-bottom:6px; color:#f8fafc; }
        p.sub { color:#94a3b8; margin-top:0; margin-bottom:18px; }
        input[type=file] { width:100%; padding:12px; border-radius:8px; background:rgba(15,23,42,0.85); color:#e2e8f0; border:1px solid rgba(255,255,255,0.06); }
        input[type=submit] { margin-top:16px; padding:12px 20px; border-radius:10px; border:none; cursor:pointer; background:linear-gradient(90deg,#6366f1,#818cf8); color:#fff; font-weight:600; }
        .note { color:#cbd5e1; font-size:13px; margin-top:16px; text-align:left; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🕳️ Pothole Detection AI</h1>
        <p class="sub">Upload a road image — model runs and returns annotated image + analysis.</p>
        <form action="/predict" method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept="image/*" required>
            <input type="submit" value="🔍 Analyze Road Conditions">
        </form>
        <div class="note">
            <p><b>Demo mode:</b> if model file is missing or ultralytics isn't installed, the app runs a visual demo so you can share a live link immediately.</p>
        </div>
    </div>
</body>
</html>
'''

RESULT_HTML = '''<!DOCTYPE html>
<html>
<head>
    <title>Pothole Analysis Results</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, Helvetica, sans-serif; background:#0f172a; color:#e2e8f0; padding:20px; }
        .container { max-width:1100px; margin:0 auto; background:rgba(15,23,42,0.95); padding:28px; border-radius:12px; }
        h1 { font-size:28px; margin-bottom:6px; color:#f8fafc; }
        .meta { color:#94a3b8; margin-bottom:16px; }
        .grid { display:flex; gap:20px; flex-wrap:wrap; }
        .left { flex:1 1 480px; }
        .right { flex:1 1 360px; max-width:360px; }
        img { max-width:100%; border-radius:10px; display:block; margin-bottom:12px; }
        .card { background:rgba(30,41,59,0.8); padding:14px; border-radius:10px; margin-bottom:12px; }
        .pothole-item pre { white-space:pre-wrap; color:#d1d5db; }
        a.btn { display:inline-block; margin-top:8px; padding:10px 14px; background:linear-gradient(90deg,#6366f1,#818cf8); color:white; text-decoration:none; border-radius:8px; font-weight:600; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🕳️ Analysis Results</h1>
        <div class="meta"><b>Time:</b> {{ current_time }} — <b>Overall Road Risk:</b> {{ overall_risk }}</div>
        <div class="grid">
            <div class="left">
                <div class="card">
                    <img src="data:image/jpeg;base64,{{ img_base64 }}" alt="Annotated Image">
                    <div><b>Detected potholes:</b> {{ analysis_count }}</div>
                </div>
                {% for p in analysis_data %}
                <div class="card pothole-item">
                    <div><b>ID:</b> {{ p.id }}  —  <b>Confidence:</b> {{ p.confidence }}</div>
                    <div><b>Dimensions:</b> {{ p.width }} x {{ p.height }} (Area: {{ p.area }})</div>
                    <div><b>Risk:</b> {{ p.risk_level }}</div>
                    <div><b>Severity:</b> {{ p.severity }}</div>
                    <div><b>Urgency:</b> {{ p.repair_urgency }}</div>
                    <div><b>Cost:</b> {{ p.cost_estimate }}</div>
                    <div><b>Location:</b> {{ p.location }}</div>
                    <pre>{{ p.impact }}</pre>
                </div>
                {% endfor %}
            </div>
            <div class="right">
                <div class="card">
                    <h3>Quick Notes</h3>
                    <ul>
                        <li>Model used: {{ model_used }}</li>
                        <li>Demo mode: {{ demo_mode }}</li>
                        <li>Keep server & tunnel open to keep public link alive.</li>
                    </ul>
                    <a href="/" class="btn">⬅ Back</a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

def encode_img_to_base64(img_bgr):
    _, buffer = cv2.imencode('.jpg', img_bgr)
    return base64.b64encode(buffer).decode('utf-8')

@app.route('/')
def home():
    return render_template_string(HOME_HTML)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        file = request.files.get('file')
        if not file:
            return "No file uploaded", 400

        img_bytes = file.read()
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return "Unable to decode image", 400

        analysis_data = []
        demo_mode = False
        model_used = "None"

        if MODEL_AVAILABLE and model is not None:
            model_used = MODEL_PATH
            # Using ultralytics model predict
            res = model.predict(img, save=False, conf=0.5)
            result = res[0]
            try:
                annotated = result.plot()
            except Exception:
                # fallback if plot() fails
                annotated = img.copy()

            for i, box in enumerate(result.boxes):
                try:
                    conf = float(box.conf[0])
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                except Exception:
                    # if structure different, skip
                    continue
                width = max(1, x2 - x1)
                height = max(1, y2 - y1)
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
            annotated_img = annotated
        else:
            # Demo fallback: draw a sample pothole box in the center
            demo_mode = True
            model_used = "demo (no model)"
            annotated_img = img.copy()
            h, w = annotated_img.shape[:2]
            box_w, box_h = max(50, w // 5), max(50, h // 8)
            x1 = w // 2 - box_w // 2
            y1 = h // 2 - box_h // 2
            x2 = x1 + box_w
            y2 = y1 + box_h
            cv2.rectangle(annotated_img, (x1, y1), (x2, y2), (0, 0, 255), 3)
            cv2.putText(annotated_img, "pothole (demo) 92%", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
            conf = 0.92
            width = box_w
            height = box_h
            area = width * height
            risk, impact, severity, repair_urgency, cost_estimate = analyze_pothole_danger(area, conf)
            analysis_data.append({
                'id': 1,
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

        img_base64 = encode_img_to_base64(annotated_img)
        overall_risk = "🚨 EXTREME" if len(analysis_data) > 5 else \
                       "⚠️ HIGH" if len(analysis_data) > 2 else \
                       "🟡 MODERATE" if len(analysis_data) > 0 else "✅ CLEAR"
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Convert list of dicts to objects for easier access in Jinja
        class P:
            def __init__(self, d): 
                self.__dict__.update(d)
        analysis_objs = [P(d) for d in analysis_data]

        return render_template_string(RESULT_HTML,
                                      img_base64=img_base64,
                                      analysis_data=analysis_objs,
                                      analysis_count=len(analysis_objs),
                                      overall_risk=overall_risk,
                                      current_time=current_time,
                                      demo_mode=str(demo_mode),
                                      model_used=model_used)
    except Exception as e:
        tb = traceback.format_exc()
        print("[ERROR]", tb)
        return f"Error processing image: {str(e)}\n\nTraceback:\n{tb}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # host 0.0.0.0 so ngrok / remote hosts can reach it
    app.run(host="0.0.0.0", port=port)
