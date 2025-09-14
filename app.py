import streamlit as st
from PIL import Image
from datetime import datetime

# Set page config
st.set_page_config(page_title="Pothole Detection AI", page_icon="🕳️", layout="wide")

# Title and description
st.title("🕳️ Pothole Detection AI")
st.write("Upload an image to detect potholes and generate a professional analysis report")

# Mock analysis function
def analyze_image(image):
    """Mock analysis - returns sample data"""
    return {
        "total_potholes": 7,
        "risk_level": "EXTREME", 
        "total_area": 11942,
        "confidence": 64.1
    }

# Simple text report generation (no PDF for now)
def create_text_report(results):
    """Create a simple text report"""
    report = f"""
    POTHOLEDETECTION AI - ANALYSIS REPORT
    =====================================
    Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    EXECUTIVE SUMMARY:
    -----------------
    Total Potholes Detected: {results['total_potholes']}
    Risk Level: {results['risk_level']}
    Total Damage Area: {results['total_area']} pixels²
    AI Confidence: {results['confidence']}%
    
    DETAILED ANALYSIS:
    -----------------
    The AI model has detected multiple potholes requiring attention.
    Immediate maintenance is recommended for optimal road safety.
    
    © 2025 Pothole Detection AI System
    """
    return report

# Main app
uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    # Display uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image', use_container_width=True)
    
    # Analyze image
    with st.spinner('Analyzing image for potholes...'):
        results = analyze_image(image)
        
        # Generate text report
        text_report = create_text_report(results)
        
        st.success("✅ Analysis completed!")
        st.write(f"**Total Potholes Detected:** {results['total_potholes']}")
        st.write(f"**Risk Level:** {results['risk_level']}")
        st.write(f"**Confidence:** {results['confidence']}%")
        
        # Show full report
        st.text_area("Full Analysis Report", text_report, height=300)
        
        # Download button for text report
        st.download_button(
            label="📄 Download Analysis Report (TXT)",
            data=text_report,
            file_name="pothole_analysis_report.txt",
            mime="text/plain"
        )
