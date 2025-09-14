from flask import Flask, request, render_template_string
from ultralytics import YOLO
import cv2
import numpy as np
from datetime import datetime
import base64

app = Flask(__name__)
model = YOLO('runs/detect/train5/weights/best.pt')

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

@app.route('/')
def home():
    return render_template_string(''' 
<!DOCTYPE html>
<html>
<head>
    <title>Pothole Detection AI</title>
    <style>
        body { font-family: 'Inter', sans-serif; background: linear-gradient(135deg, #0f172a, #1e293b); color: #e2e8f0; margin:0; padding:0; }
        .container { max-width: 500px; margin: 80px auto; background: rgba(15,23,42,0.95); padding: 40px; border-radius: 20px; text-align:center; }
        h1 { background: linear-gradient(135deg, #818cf8, #a5b4fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        input[type="file"] { margin: 20px 0; padding: 16px; width: 100%; border-radius: 12px; background: rgba(15,23,42,0.8); color: #e2e8f0; }
        input[type="submit"] { background: linear-gradient(135deg, #6366f1, #818cf8); color: white; padding: 15px 30px; border: none; border-radius: 12px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🕳️ Pothole Detection AI</h1>
        <form action="/predict" method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept="image/*" required>
            <input type="submit" value="🔍 Analyze Road Conditions">
        </form>
    </div>
</body>
</html>
    ''')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        file = request.files['file']
        img_bytes = file.read()
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        results = model.predict(img, save=False, conf=0.5)
        result = results[0]
        
        annotated_img = result.plot()
        _, buffer = cv2.imencode('.jpg', annotated_img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
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
        
        overall_risk = "🚨 EXTREME" if len(analysis_data) > 5 else \
                       "⚠️ HIGH" if len(analysis_data) > 2 else \
                       "🟡 MODERATE" if len(analysis_data) > 0 else "✅ CLEAR"
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return render_template_string(f''' 
<!DOCTYPE html>
<html>
<head>
    <title>Pothole Analysis Results</title>
    <style>
        body {{ font-family: 'Inter', sans-serif; background: linear-gradient(135deg,#0f172a,#1e293b); color:#e2e8f0; padding:20px; }}
        .container {{ max-width: 1000px; margin:auto; background: rgba(15,23,42,0.95); padding:40px; border-radius:20px; }}
        h1 {{ background: linear-gradient(135deg, #818cf8, #a5b4fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .pothole-item {{ margin:15px 0; padding:15px; border-radius:12px; background:rgba(30,41,59,0.8); }}
        img {{ max-width:100%; border-radius:12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🕳️ Analysis Results</h1>
        <p><b>Time:</b> {current_time}</p>
        <p><b>Overall Road Risk:</b> {overall_risk}</p>
        <img src="data:image/jpeg;base64,{img_base64}" alt="Annotated Image"/>
        
        <h2>Detected Potholes</h2>
        {''.join([f"""
        <div class='pothole-item'>
            <p><b>ID:</b> {p['id']}</p>
            <p><b>Confidence:</b> {p['confidence']}</p>
            <p><b>Dimensions:</b> {p['width']}x{p['height']} (Area: {p['area']})</p>
            <p><b>Risk:</b> {p['risk_level']}</p>
            <p><b>Severity:</b> {p['severity']}</p>
            <p><b>Urgency:</b> {p['repair_urgency']}</p>
            <p><b>Cost:</b> {p['cost_estimate']}</p>
            <p><b>Location:</b> {p['location']}</p>
            <pre>{p['impact']}</pre>
        </div>
        """ for p in analysis_data])}
    </div>
</body>
</html>
        ''')
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app.run(debug=True)
