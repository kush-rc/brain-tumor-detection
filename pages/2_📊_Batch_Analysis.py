"""
Batch MRI Analysis Page
Upload and analyze multiple MRI scans at once
"""

import streamlit as st
import sys
from pathlib import Path
from PIL import Image
import pandas as pd
import time
import zipfile
import io
import tempfile
from utils.theme_switcher import theme_toggle_button, apply_custom_css, init_theme


# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.model_utils import load_brain_tumor_model, predict_tumor
from utils.visualization import plot_prediction_bars
from utils.auth import require_login, get_current_user
from utils.database import init_database, save_prediction

# Page config
st.set_page_config(page_title="Batch Analysis", page_icon="📊", layout="wide")
init_theme()
apply_custom_css()

def main():
    """Main function for batch analysis page"""
    
    st.title("📊 Batch MRI Analysis")
    st.markdown("Upload and analyze multiple MRI scans simultaneously for efficient processing")
    
    # Check login
    if not require_login():
        return
    
    current_user = get_current_user()
    
    st.markdown("---")
    
    # Initialize
    init_database()
    model = load_brain_tumor_model()
    
    if model is None:
        st.error("❌ Failed to load model")
        return
    
    # File uploader for multiple files
    st.subheader("📤 Upload Multiple MRI Scans")
    
    uploaded_files = st.file_uploader(
        "Choose MRI images (JPG, JPEG, PNG)",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        help="Select multiple MRI scans to analyze in batch"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} images uploaded")
        
        # Options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            save_results = st.checkbox("💾 Save Results to History", value=False)
        with col2:
            export_csv = st.checkbox("📥 Export Results to CSV", value=True)
        with col3:
            show_images = st.checkbox("🖼️ Show All Images", value=False)
        
        patient_id = None
        if save_results:
            patient_id = st.text_input("Patient ID (for saving)", placeholder="e.g., P001")
        
        # Analyze button
        if st.button("🔍 Analyze All Scans", type="primary", use_container_width=True):
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results_list = []
            
            # Process each image
            for idx, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Processing {idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")
                
                try:
                    # Load image
                    image = Image.open(uploaded_file).convert("RGB")
                    
                    # Predict
                    results = predict_tumor(model, image)
                    
                    if results:
                        results['filename'] = uploaded_file.name
                        results['image'] = image
                        results_list.append(results)
                        
                        # Save to history if requested
                        if save_results and patient_id:
                            save_prediction(
                                patient_id=patient_id,
                                patient_name=patient_id,
                                predicted_class=results['predicted_class'],
                                confidence=results['confidence'],
                                all_probabilities=results['all_probabilities'],
                                notes=f"Batch analysis: {uploaded_file.name}",
                                user=current_user['username']
                            )
                    
                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {e}")
                
                # Update progress
                progress_bar.progress((idx + 1) / len(uploaded_files))
            
            status_text.text("✅ Analysis complete!")
            time.sleep(1)
            status_text.empty()
            progress_bar.empty()
            
            # Display results
            st.markdown("---")
            st.subheader("📊 Batch Analysis Results")
            
            if results_list:
                # Summary statistics
                st.markdown("### 📈 Summary Statistics")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Scans", len(results_list))
                
                with col2:
                    avg_confidence = sum(r['confidence'] for r in results_list) / len(results_list)
                    st.metric("Avg Confidence", f"{avg_confidence*100:.1f}%")
                
                with col3:
                    tumor_count = sum(1 for r in results_list if r['predicted_class'] != 'No Tumor')
                    st.metric("Tumors Detected", tumor_count)
                
                with col4:
                    no_tumor_count = sum(1 for r in results_list if r['predicted_class'] == 'No Tumor')
                    st.metric("No Tumor", no_tumor_count)
                
                # Class distribution
                st.markdown("### 🎯 Class Distribution")
                
                class_counts = {}
                for result in results_list:
                    pred_class = result['predicted_class']
                    class_counts[pred_class] = class_counts.get(pred_class, 0) + 1
                
                # Create bar chart
                import plotly.express as px
                
                df_dist = pd.DataFrame({
                    'Class': list(class_counts.keys()),
                    'Count': list(class_counts.values())
                })
                
                fig = px.bar(df_dist, x='Class', y='Count', 
                            title='Distribution of Predicted Classes',
                            color='Class',
                            color_discrete_map={
                                'Glioma': '#e74c3c',
                                'Meningioma': '#e67e22',
                                'Pituitary': '#f39c12',
                                'No Tumor': '#27ae60'
                            })
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Detailed results table
                st.markdown("### 📋 Detailed Results")
                
                # Create DataFrame
                df_results = pd.DataFrame([
                    {
                        'Filename': r['filename'],
                        'Predicted Class': r['predicted_class'],
                        'Confidence': f"{r['confidence']*100:.2f}%",
                        'Glioma': f"{r['all_probabilities']['Glioma']*100:.1f}%",
                        'Meningioma': f"{r['all_probabilities']['Meningioma']*100:.1f}%",
                        'No Tumor': f"{r['all_probabilities']['No Tumor']*100:.1f}%",
                        'Pituitary': f"{r['all_probabilities']['Pituitary']*100:.1f}%",
                    }
                    for r in results_list
                ])
                
                st.dataframe(df_results, use_container_width=True, hide_index=True)
                
                # Export to CSV
                if export_csv:
                    csv = df_results.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Results as CSV",
                        data=csv,
                        file_name=f"batch_analysis_results_{int(time.time())}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                # Show images if requested
                if show_images:
                    st.markdown("---")
                    st.markdown("### 🖼️ Image Gallery with Predictions")
                    
                    # Display in grid
                    cols_per_row = 3
                    rows = [results_list[i:i+cols_per_row] for i in range(0, len(results_list), cols_per_row)]
                    
                    for row in rows:
                        cols = st.columns(cols_per_row)
                        for col, result in zip(cols, row):
                            with col:
                                st.image(result['image'], use_container_width=True)
                                
                                # Color code based on confidence
                                confidence = result['confidence']
                                if confidence >= 0.9:
                                    color = "🟢"
                                elif confidence >= 0.75:
                                    color = "🟡"
                                else:
                                    color = "🔴"
                                
                                st.caption(f"{color} **{result['predicted_class']}**")
                                st.caption(f"Confidence: {confidence*100:.1f}%")
                                st.caption(f"File: {result['filename']}")
            
            else:
                st.warning("⚠️ No results to display")
    
    else:
        st.info("👆 Upload multiple MRI scans to begin batch analysis")
        
        # Instructions
        st.markdown("### 📖 How to Use Batch Analysis")
        st.markdown("""
        1. **Select Multiple Files**: Click the upload button and select multiple MRI scans
        2. **Configure Options**: Choose whether to save results and export to CSV
        3. **Start Analysis**: Click 'Analyze All Scans' to process all images
        4. **Review Results**: View summary statistics, class distribution, and detailed results
        5. **Export Data**: Download results as CSV for further analysis
        
        **Benefits:**
        - ⚡ Process multiple scans efficiently
        - 📊 Get aggregate statistics and insights
        - 📥 Export results for documentation
        - 💾 Optionally save to patient history
        """)
    
    # Sidebar
    with st.sidebar:
        # Theme toggle
        theme_toggle_button()
    
        st.markdown("---")
        st.markdown("### 💡 Batch Analysis Tips")
        st.info("""
        - Upload up to 50 images at once
        - All images should be MRI brain scans
        - Supported formats: JPG, JPEG, PNG
        - Results can be exported to CSV
        - Use for screening multiple patients
        """)
        
        st.markdown("---")
        st.markdown("### ⚡ Performance")
        st.write("**Processing Speed:** ~1-2 seconds per image")
        st.write("**Recommended Batch Size:** 10-20 images")

if __name__ == "__main__":
    main()
