import streamlit as st
import numpy as np
from PIL import Image
import tempfile
import os
from datetime import datetime

# Set page config
st.set_page_config(page_title="Pothole Detection AI", page_icon="🕳️", layout="wide")

# Title and description
st.title("🕳️ Pothole Detection AI")
st.write("Upload an image to detect potholes and generate a professional analysis report")

# Mock analysis function (replace with your actual model later)
def analyze_image(image_path):
    """Mock analysis - replace with your actual YOLO model code"""
    # This is where you would normally run model.predict()
    # For now, returning mock data
    return {
        "total_potholes": 7,
        "risk_level": "EXTREME",
        "total_area": 11942,
        "confidence": 64.1,
        "potholes": [
            {"confidence": 92.24, "width": 102, "height": 24, "area": 2448, "severity": 30},
            {"confidence": 89.98, "width": 74, "height": 29, "area": 2146, "severity": 30},
            # Add more mock pothole data as needed
        ]
    }

# PDF generation function
def generate_pdf_report(analysis_results):
    from fpdf import FPDF
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 24)
    pdf.cell(0, 20, "Pothole Analysis Report", 0, 1, 'C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
    pdf.ln(20)
    
    # Add analysis results to PDF
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Executive Summary", 0, 1)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, f"Total Potholes Detected: {analysis_results['total_potholes']}\nRisk Level: {analysis_results['risk_level']}\nTotal Area: {analysis_results['total_area']} pixels²\nConfidence: {analysis_results['confidence']}%")
    
    pdf_output = "analysis_report.pdf"
    pdf.output(pdf_output)
    return pdf_output

# Main app
uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    # Display uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image', use_container_width=True)
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
        image.save(tmp.name)
        img_path = tmp.name
    
    # Analyze image
    with st.spinner('Analyzing image for potholes...'):
        results = analyze_image(img_path)
        
        # Generate PDF report
        pdf_path = generate_pdf_report(results)
        
        st.success("✅ Analysis completed!")
        st.write(f"**Total Potholes Detected:** {results['total_potholes']}")
        st.write(f"**Risk Level:** {results['risk_level']}")
        st.write(f"**Confidence:** {results['confidence']}%")
        
        # Download button for PDF
        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="📄 Download Full Analysis Report PDF",
                data=pdf_file,
                file_name="pothole_analysis_report.pdf",
                mime="application/pdf"
            )
    
    # Clean up
    os.unlink(img_path)
    if os.path.exists(pdf_path):
        os.unlink(pdf_path)

