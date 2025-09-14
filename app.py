import streamlit as st
import numpy as np
from PIL import Image
import torch
from ultralytics import YOLO
import cv2
from fpdf import FPDF
import tempfile
import os
from datetime import datetime

# Set page config
st.set_page_config(page_title="Pothole Detection AI", page_icon="🕳️", layout="wide")

# Title and description
st.title("🕳️ Pothole Detection AI")
st.write("Upload an image to detect potholes and generate a professional analysis report")

# Load model function
@st.cache_resource
def load_model():
    try:
        model = YOLO('best.pt')
        return model
    except:
        st.error("Model file 'best.pt' not found. Please ensure it's in the project root directory.")
        return None

# PDF generation function (from your Flask app)
def generate_pdf_report(results, image_path):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Page 1: Cover and Executive Summary
    pdf.add_page()
    pdf.set_font("Arial", 'B', 24)
    pdf.cell(0, 20, "Pothole Analysis Report", 0, 1, 'C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, "Comprehensive Road Infrastructure Assessment | " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 1, 'C')
    pdf.ln(20)
    
    # Add your existing PDF content generation logic here
    # Copy the exact code from your Flask app that creates the PDF
    
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
    
    # Load model and process
    model = load_model()
    if model:
        with st.spinner('Analyzing image for potholes...'):
            results = model(img_path)
            
            # Generate PDF report
            pdf_path = generate_pdf_report(results, img_path)
            
            st.success("✅ Analysis completed!")
            
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

