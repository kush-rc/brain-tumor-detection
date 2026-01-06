"""
Single MRI Prediction Page
Upload and analyze individual MRI scans with Grad-CAM visualization
"""

import streamlit as st
import sys
from pathlib import Path
import time
from PIL import Image
import tempfile

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.model_utils import load_brain_tumor_model, predict_tumor, get_class_description, get_confidence_color
from utils.visualization import generate_gradcam, overlay_heatmap, plot_prediction_bars
from utils.database import init_database, save_prediction, load_patients, add_patient
from utils.report_generator import download_report_button
from utils.auth import require_login, get_current_user
from utils.theme_switcher import theme_toggle_button, apply_custom_css, init_theme


# Page config
st.set_page_config(page_title="Single Prediction", page_icon="🔍", layout="wide")
init_theme()
apply_custom_css()

# Custom CSS
st.markdown("""
<style>
    .prediction-box {
        padding: 2rem;
        border-radius: 15px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    .confidence-high {
        background-color: #27ae60;
        padding: 0.5rem;
        border-radius: 5px;
        color: white;
        font-weight: bold;
    }
    .confidence-medium {
        background-color: #f39c12;
        padding: 0.5rem;
        border-radius: 5px;
        color: white;
        font-weight: bold;
    }
    .confidence-low {
        background-color: #e74c3c;
        padding: 0.5rem;
        border-radius: 5px;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main function for single prediction page"""
    
    st.title("🔍 Single MRI Scan Analysis")
    st.markdown("Upload an MRI scan for instant brain tumor classification with AI explainability")
    
    # Check login
    if not require_login():
        return
    
    current_user = get_current_user()
    
    st.markdown("---")
    
    # Initialize database
    init_database()
    
    # Load model
    model = load_brain_tumor_model()
    
    if model is None:
        st.error("❌ Failed to load model. Please check the model file.")
        return
    
    # Two column layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📤 Upload MRI Scan")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose an MRI image",
            type=["jpg", "jpeg", "png"],
            help="Upload a brain MRI scan in JPG, JPEG, or PNG format"
        )
        
        if uploaded_file is not None:
            # Display uploaded image
            image = Image.open(uploaded_file).convert("RGB")
            st.image(image, caption="Uploaded MRI Scan", use_container_width=True)
            
            # Image info
            st.info(f"📊 Image Size: {image.size[0]} x {image.size[1]} pixels")
    
    with col2:
        st.subheader("👤 Patient Information")
        
        # Patient selection/creation
        patients = load_patients()
        patient_list = list(patients.keys())
        
        patient_option = st.radio(
            "Select Option:",
            ["Existing Patient", "New Patient", "Anonymous"],
            horizontal=True
        )
        
        patient_id = None
        patient_name = "Anonymous"
        patient_info = {}
        
        if patient_option == "Existing Patient":
            if patient_list:
                selected_patient = st.selectbox(
                    "Select Patient:",
                    patient_list,
                    format_func=lambda x: f"{patients[x]['name']} ({x})"
                )
                patient_id = selected_patient
                patient_name = patients[selected_patient]['name']
                patient_info = patients[selected_patient]
                patient_info['id'] = patient_id
                
                # Display patient info
                with st.expander("📋 Patient Details"):
                    st.write(f"**Name:** {patient_info.get('name', 'N/A')}")
                    st.write(f"**Age:** {patient_info.get('age', 'N/A')}")
                    st.write(f"**Gender:** {patient_info.get('gender', 'N/A')}")
                    st.write(f"**Total Scans:** {patient_info.get('total_scans', 0)}")
            else:
                st.warning("⚠️ No patients in database. Please add a new patient.")
        
        elif patient_option == "New Patient":
            with st.form("new_patient_form"):
                st.markdown("##### Add New Patient")
                new_patient_id = st.text_input("Patient ID*", placeholder="e.g., P001")
                new_patient_name = st.text_input("Full Name*", placeholder="John Doe")
                new_patient_age = st.number_input("Age*", min_value=1, max_value=120, value=30)
                new_patient_gender = st.selectbox("Gender*", ["Male", "Female", "Other"])
                new_patient_contact = st.text_input("Contact", placeholder="Phone/Email")
                new_patient_history = st.text_area("Medical History", placeholder="Previous conditions, medications, etc.")
                
                submit_patient = st.form_submit_button("➕ Add Patient", use_container_width=True)
                
                if submit_patient:
                    if new_patient_id and new_patient_name:
                        if add_patient(
                            new_patient_id,
                            new_patient_name,
                            new_patient_age,
                            new_patient_gender,
                            new_patient_contact,
                            new_patient_history
                        ):
                            st.success(f"✅ Patient {new_patient_name} added successfully!")
                            patient_id = new_patient_id
                            patient_name = new_patient_name
                            patient_info = {
                                'id': new_patient_id,
                                'name': new_patient_name,
                                'age': new_patient_age,
                                'gender': new_patient_gender,
                                'contact': new_patient_contact
                            }
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.error("❌ Please fill in required fields (ID and Name)")
        
        else:  # Anonymous
            patient_id = f"ANON_{int(time.time())}"
            patient_name = "Anonymous Patient"
            patient_info = {'id': patient_id, 'name': patient_name, 'age': 'N/A', 'gender': 'N/A', 'contact': 'N/A'}
    
    # Analysis section
    st.markdown("---")
    
    if uploaded_file is not None:
        # Analysis options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            show_gradcam = st.checkbox("🔥 Generate Grad-CAM", value=True, help="Show attention heatmap")
        with col2:
            show_probabilities = st.checkbox("📊 Show All Probabilities", value=True)
        with col3:
            save_to_history = st.checkbox("💾 Save to History", value=True)
        
        # Additional notes
        notes = st.text_area("📝 Clinical Notes (Optional)", placeholder="Add any relevant observations or notes...")
        
        # Analyze button
        if st.button("🔍 Analyze MRI Scan", type="primary", use_container_width=True):
            
            with st.spinner("🧠 Analyzing MRI scan..."):
                # Make prediction
                results = predict_tumor(model, image)
                
                if results is None:
                    st.error("❌ Error during prediction")
                    return
                
                # Display results
                st.success("✅ Analysis Complete!")
                
                # Main prediction result
                st.markdown(f"""
                <div class="prediction-box">
                    <h2>Prediction: {results['predicted_class']}</h2>
                    <h3>Confidence: {results['confidence']*100:.2f}%</h3>
                    <p>Analysis completed in {results['prediction_time']:.3f} seconds</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Results layout
                result_col1, result_col2 = st.columns([1, 1])
                
                with result_col1:
                    st.subheader("📊 Detailed Results")
                    
                    # Confidence indicator
                    confidence = results['confidence']
                    if confidence >= 0.9:
                        conf_class = "confidence-high"
                        conf_label = "High Confidence"
                    elif confidence >= 0.75:
                        conf_class = "confidence-medium"
                        conf_label = "Medium Confidence"
                    else:
                        conf_class = "confidence-low"
                        conf_label = "Low Confidence"
                    
                    st.markdown(f'<div class="{conf_class}">{conf_label}: {confidence*100:.2f}%</div>', unsafe_allow_html=True)
                    
                    # Class description
                    st.markdown("#### 📖 About This Diagnosis")
                    st.info(get_class_description(results['predicted_class']))
                    
                    # Probability distribution
                    if show_probabilities:
                        st.markdown("#### 📈 Class Probabilities")
                        for class_name, prob in sorted(results['all_probabilities'].items(), key=lambda x: x[1], reverse=True):
                            st.progress(float(prob))
                            st.write(f"**{class_name}:** {prob*100:.2f}%")
                
                with result_col2:
                    st.subheader("🔥 Visual Explanation")
                    
                    if show_gradcam:
                        with st.spinner("Generating Grad-CAM heatmap..."):
                            # Preprocess image for Grad-CAM
                            from utils.model_utils import preprocess_image
                            img_array = preprocess_image(image)
                            
                            # Generate Grad-CAM
                            heatmap = generate_gradcam(
                                model,
                                img_array,
                                results['predicted_class_idx']
                            )
                            
                            if heatmap is not None:
                                # Overlay heatmap
                                overlaid_image = overlay_heatmap(image, heatmap)
                                
                                # Display
                                st.image(overlaid_image, caption="Grad-CAM Attention Map", use_container_width=True)
                                st.caption("🔥 Red areas show regions the AI focused on for classification")
                                
                                # Save heatmap for report
                                heatmap_path = tempfile.NamedTemporaryFile(delete=False, suffix='.png').name
                                overlaid_image.save(heatmap_path)
                            else:
                                st.warning("⚠️ Could not generate Grad-CAM heatmap")
                                heatmap_path = None
                    else:
                        st.image(image, caption="Original MRI Scan", use_container_width=True)
                        heatmap_path = None
                    
                    # Probability bar chart
                    if show_probabilities:
                        fig = plot_prediction_bars(results['all_probabilities'], list(results['all_probabilities'].keys()))
                        if fig:
                            st.pyplot(fig)
                
                # Save to history
                if save_to_history and patient_id:
                    # Save original image
                    image_path = tempfile.NamedTemporaryFile(delete=False, suffix='.png').name
                    image.save(image_path)
                    
                    prediction_id = save_prediction(
                        patient_id=patient_id,
                        patient_name=patient_name,
                        predicted_class=results['predicted_class'],
                        confidence=results['confidence'],
                        all_probabilities=results['all_probabilities'],
                        image_path=image_path,
                        notes=notes,
                        user=current_user['username']
                    )
                    
                    if prediction_id:
                        st.success(f"✅ Prediction saved to history (ID: {prediction_id})")
                
                # Generate PDF Report
                st.markdown("---")
                st.subheader("📄 Download Report")
                
                download_report_button(
                    patient_info=patient_info,
                    prediction_results=results,
                    image_path=image_path if save_to_history else None,
                    heatmap_path=heatmap_path if show_gradcam else None,
                    notes=notes
                )
    
    else:
        st.info("👆 Please upload an MRI scan to begin analysis")
    
    # Sidebar info
    with st.sidebar:
        # Theme toggle
        theme_toggle_button()
    
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        from utils.database import get_statistics
        stats = get_statistics()

        st.metric("Total Patients", stats.get('total_patients', 0))
        st.metric("Total Predictions", stats.get('total_predictions', 0))
        st.metric("Today's Predictions", stats.get('predictions_today', 0))
        
        st.markdown("---")
        st.markdown("### ℹ️ Tips")
        st.info("""
        - Use high-quality MRI scans for best results
        - Grad-CAM shows which areas the AI focused on
        - Save predictions to track patient history
        - Download PDF reports for documentation
        """)

if __name__ == "__main__":
    main()
