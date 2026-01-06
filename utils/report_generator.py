"""
PDF report generator for brain tumor predictions
Creates professional medical-style reports
"""

import streamlit as st
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from pathlib import Path
import tempfile
from PIL import Image
import io

def generate_prediction_report(patient_info, prediction_results, image_path=None, 
                              heatmap_path=None, notes=""):
    """
    Generate a professional PDF report for brain tumor prediction
    
    Args:
        patient_info: Dictionary with patient information
        prediction_results: Dictionary with prediction results
        image_path: Path to original MRI image
        heatmap_path: Path to Grad-CAM heatmap
        notes: Additional notes
    
    Returns:
        BytesIO object containing PDF
    """
    try:
        # Create temporary file
        buffer = io.BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Header
        elements.append(Paragraph("🧠 Brain Tumor Detection Report", title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Report metadata
        report_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        elements.append(Paragraph(f"<b>Report Generated:</b> {report_date}", styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Patient Information Section
        elements.append(Paragraph("Patient Information", heading_style))
        
        patient_data = [
            ['Patient Name:', patient_info.get('name', 'N/A')],
            ['Patient ID:', patient_info.get('id', 'N/A')],
            ['Age:', str(patient_info.get('age', 'N/A'))],
            ['Gender:', patient_info.get('gender', 'N/A')],
            ['Contact:', patient_info.get('contact', 'N/A')],
        ]
        
        patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        elements.append(patient_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Prediction Results Section
        elements.append(Paragraph("Diagnosis Results", heading_style))
        
        predicted_class = prediction_results.get('predicted_class', 'Unknown')
        confidence = prediction_results.get('confidence', 0) * 100
        
        # Color code based on class
        class_colors = {
            'Glioma': colors.HexColor('#e74c3c'),
            'Meningioma': colors.HexColor('#e67e22'),
            'Pituitary': colors.HexColor('#f39c12'),
            'No Tumor': colors.HexColor('#27ae60')
        }
        
        diagnosis_color = class_colors.get(predicted_class, colors.grey)
        
        diagnosis_data = [
            ['Predicted Classification:', f"{predicted_class}"],
            ['Confidence Level:', f"{confidence:.2f}%"],
            ['Prediction Time:', f"{prediction_results.get('prediction_time', 0):.3f} seconds"],
        ]
        
        diagnosis_table = Table(diagnosis_data, colWidths=[2.5*inch, 3.5*inch])
        diagnosis_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('BACKGROUND', (1, 0), (1, 0), diagnosis_color),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('TEXTCOLOR', (1, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        elements.append(diagnosis_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Probability Distribution
        elements.append(Paragraph("Class Probability Distribution", heading_style))
        
        prob_data = [['Class', 'Probability']]
        all_probs = prediction_results.get('all_probabilities', {})
        
        for class_name, prob in sorted(all_probs.items(), key=lambda x: x[1], reverse=True):
            prob_data.append([class_name, f"{prob*100:.2f}%"])
        
        prob_table = Table(prob_data, colWidths=[3*inch, 3*inch])
        prob_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')])
        ]))
        
        elements.append(prob_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Images Section
        if image_path or heatmap_path:
            elements.append(PageBreak())
            elements.append(Paragraph("MRI Scan Analysis", heading_style))
            
            img_table_data = []
            img_row = []
            
            if image_path:
                try:
                    # Resize image
                    img = Image.open(image_path)
                    img.thumbnail((250, 250))
                    
                    # Save to temp file
                    temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                    img.save(temp_img.name)
                    
                    img_row.append(RLImage(temp_img.name, width=2.5*inch, height=2.5*inch))
                except Exception as e:
                    img_row.append(Paragraph("Original MRI\n[Image not available]", styles['Normal']))
            
            if heatmap_path:
                try:
                    # Resize heatmap
                    heatmap = Image.open(heatmap_path)
                    heatmap.thumbnail((250, 250))
                    
                    # Save to temp file
                    temp_heatmap = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                    heatmap.save(temp_heatmap.name)
                    
                    img_row.append(RLImage(temp_heatmap.name, width=2.5*inch, height=2.5*inch))
                except Exception as e:
                    img_row.append(Paragraph("Grad-CAM Heatmap\n[Image not available]", styles['Normal']))
            
            if img_row:
                img_table_data.append(img_row)
                img_labels = []
                if image_path:
                    img_labels.append(Paragraph("<b>Original MRI Scan</b>", styles['Normal']))
                if heatmap_path:
                    img_labels.append(Paragraph("<b>Grad-CAM Attention Map</b>", styles['Normal']))
                img_table_data.append(img_labels)
                
                img_table = Table(img_table_data)
                img_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                
                elements.append(img_table)
                elements.append(Spacer(1, 0.3*inch))
        
        # Clinical Notes
        if notes:
            elements.append(Paragraph("Clinical Notes", heading_style))
            elements.append(Paragraph(notes, styles['Normal']))
            elements.append(Spacer(1, 0.3*inch))
        
        # Disclaimer
        elements.append(Spacer(1, 0.5*inch))
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_LEFT
        )
        
        disclaimer_text = """
        <b>MEDICAL DISCLAIMER:</b> This report is generated by an AI-based system for research and 
        educational purposes only. The predictions should NOT be used as the sole basis for medical 
        diagnosis or treatment decisions. Always consult qualified healthcare professionals for 
        proper medical evaluation and diagnosis. The system has an accuracy of approximately 96% 
        on test data, but individual results may vary.
        """
        
        elements.append(Paragraph(disclaimer_text, disclaimer_style))
        
        # Footer
        elements.append(Spacer(1, 0.2*inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        
        elements.append(Paragraph("Brain Tumor Detection AI System | v1.0.0", footer_style))
        elements.append(Paragraph("© 2026 Medical AI Solutions | All Rights Reserved", footer_style))
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF bytes
        buffer.seek(0)
        return buffer
    
    except Exception as e:
        st.error(f"Error generating PDF report: {e}")
        return None

def download_report_button(patient_info, prediction_results, image_path=None, 
                          heatmap_path=None, notes=""):
    """
    Create a download button for the PDF report
    
    Args:
        patient_info: Patient information dict
        prediction_results: Prediction results dict
        image_path: Path to MRI image
        heatmap_path: Path to heatmap
        notes: Additional notes
    """
    try:
        pdf_buffer = generate_prediction_report(
            patient_info, prediction_results, 
            image_path, heatmap_path, notes
        )
        
        if pdf_buffer:
            filename = f"brain_tumor_report_{patient_info.get('id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_buffer,
                file_name=filename,
                mime="application/pdf",
                use_container_width=True
            )
    
    except Exception as e:
        st.error(f"Error creating download button: {e}")
