import streamlit as st
from PIL import Image
from datetime import datetime
import io

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

# Simple PDF generation function
def create_pdf_report(results):
    """Create a simple text-based PDF"""
    from fpdf import FPDF
    
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", 'B', 24)
    pdf.cell(0, 20, "Pothole Analysis Report", 0, 1, 'C')
    
    # Date
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
    pdf.ln(10)
    
    # Results
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Executive Summary", 0, 1)
    pdf.set_font("Arial", '', 12)
    
    summary_text = f"""
    Total Potholes Detected: {results['total_potholes']}
    Risk Level: {results['risk_level']}
    Total Damage Area: {results['total_area']} pixels²
    AI Confidence: {results['confidence']}%
    """
    
    pdf.multi_cell(0, 10, summary_text)
    
    # Save to bytes
    return pdf.output(dest='S').encode('latin-1')

# Main app
uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    # Display uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image', use_container_width=True)
    
    # Analyze image
    with st.spinner('Analyzing image for potholes...'):
        results = analyze_image(image)
        
        # Generate PDF report
        try:
            pdf_bytes = create_pdf_report(results)
            
            st.success("✅ Analysis completed!")
            st.write(f"**Total Potholes Detected:** {results['total_potholes']}")
            st.write(f"**Risk Level:** {results['risk_level']}")
            st.write(f"**Confidence:** {results['confidence']}%")
            
            # Download button for PDF
            st.download_button(
                label="📄 Download Full Analysis Report PDF",
                data=pdf_bytes,
                file_name="pothole_analysis_report.pdf",
                mime="application/pdf"
            )
            
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")
            # Fallback: show results without PDF
            st.write("**Analysis Results:**")
            st.json(results)
