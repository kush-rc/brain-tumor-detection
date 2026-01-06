"""
Patient History Page
View and manage patient records and prediction history
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from utils.theme_switcher import theme_toggle_button, apply_custom_css, init_theme


# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))
init_theme()
apply_custom_css()

from utils.database import (
    init_database, load_patients, get_patient, 
    get_patient_predictions, get_all_predictions,
    update_patient, delete_patient
)
from utils.auth import require_login, get_current_user

# Page config
st.set_page_config(page_title="Patient History", page_icon="📋", layout="wide")

def main():
    """Main function for patient history page"""
    
    st.title("📋 Patient History & Records")
    st.markdown("View and manage patient information and prediction history")
    
    # Check login
    if not require_login():
        return
    
    current_user = get_current_user()
    
    st.markdown("---")
    
    # Initialize database
    init_database()
    
    # Load patients
    patients = load_patients()
    
    if not patients:
        st.warning("⚠️ No patients in database. Add patients from the Single Prediction page.")
        return
    
    # Patient selection
    patient_list = list(patients.keys())
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_patient = st.selectbox(
            "Select Patient:",
            patient_list,
            format_func=lambda x: f"{patients[x]['name']} - {x}",
            key="patient_selector"
        )
    
    with col2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    
    if selected_patient:
        patient_info = get_patient(selected_patient)
        
        if patient_info:
            # Patient information card
            st.markdown("### 👤 Patient Information")
            
            info_col1, info_col2, info_col3 = st.columns(3)
            
            with info_col1:
                st.markdown(f"""
                **Name:** {patient_info.get('name', 'N/A')}  
                **Patient ID:** {selected_patient}  
                **Age:** {patient_info.get('age', 'N/A')}  
                **Gender:** {patient_info.get('gender', 'N/A')}
                """)
            
            with info_col2:
                st.markdown(f"""
                **Contact:** {patient_info.get('contact', 'N/A')}  
                **Total Scans:** {patient_info.get('total_scans', 0)}  
                **Last Scan:** {patient_info.get('last_scan', 'Never')}  
                **Created:** {patient_info.get('created_at', 'N/A')[:10]}
                """)
            
            with info_col3:
                # Actions
                st.markdown("**Actions:**")
                if st.button("✏️ Edit Patient", use_container_width=True):
                    st.session_state.edit_mode = True
                
                if st.button("🗑️ Delete Patient", use_container_width=True, type="secondary"):
                    st.session_state.confirm_delete = True
            
            # Edit mode
            if st.session_state.get('edit_mode', False):
                with st.expander("✏️ Edit Patient Information", expanded=True):
                    with st.form("edit_patient_form"):
                        edit_name = st.text_input("Name", value=patient_info.get('name', ''))
                        edit_age = st.number_input("Age", value=int(patient_info.get('age', 0)), min_value=1, max_value=120)
                        edit_gender = st.selectbox("Gender", ["Male", "Female", "Other"], 
                                                  index=["Male", "Female", "Other"].index(patient_info.get('gender', 'Male')))
                        edit_contact = st.text_input("Contact", value=patient_info.get('contact', ''))
                        edit_history = st.text_area("Medical History", value=patient_info.get('medical_history', ''))
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            submit_edit = st.form_submit_button("💾 Save Changes", use_container_width=True)
                        with col2:
                            cancel_edit = st.form_submit_button("❌ Cancel", use_container_width=True)
                        
                        if submit_edit:
                            if update_patient(
                                selected_patient,
                                name=edit_name,
                                age=edit_age,
                                gender=edit_gender,
                                contact=edit_contact,
                                medical_history=edit_history
                            ):
                                st.success("✅ Patient information updated!")
                                st.session_state.edit_mode = False
                                time.sleep(1)
                                st.rerun()
                        
                        if cancel_edit:
                            st.session_state.edit_mode = False
                            st.rerun()
            
            # Delete confirmation
            if st.session_state.get('confirm_delete', False):
                st.error("⚠️ **Warning:** This will permanently delete the patient and all their records!")
                col1, col2, col3 = st.columns([1, 1, 2])
                
                with col1:
                    if st.button("✅ Confirm Delete", type="primary"):
                        if delete_patient(selected_patient):
                            st.success("✅ Patient deleted successfully")
                            st.session_state.confirm_delete = False
                            time.sleep(1)
                            st.rerun()
                
                with col2:
                    if st.button("❌ Cancel Delete"):
                        st.session_state.confirm_delete = False
                        st.rerun()
            
            # Medical history
            if patient_info.get('medical_history'):
                with st.expander("📄 Medical History"):
                    st.write(patient_info['medical_history'])
            
            st.markdown("---")
            
            # Prediction history
            st.markdown("### 📊 Prediction History")
            
            predictions_df = get_patient_predictions(selected_patient)
            
            if not predictions_df.empty:
                # Statistics
                stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
                
                with stat_col1:
                    st.metric("Total Predictions", len(predictions_df))
                
                with stat_col2:
                    avg_confidence = predictions_df['confidence'].mean() * 100
                    st.metric("Avg Confidence", f"{avg_confidence:.1f}%")
                
                with stat_col3:
                    tumor_count = len(predictions_df[predictions_df['predicted_class'] != 'No Tumor'])
                    st.metric("Tumors Detected", tumor_count)
                
                with stat_col4:
                    latest_date = predictions_df['date'].iloc[0]
                    st.metric("Latest Scan", latest_date)
                
                # Timeline chart
                st.markdown("#### 📈 Prediction Timeline")
                
                # Prepare data for timeline
                timeline_df = predictions_df.copy()
                timeline_df['datetime'] = pd.to_datetime(timeline_df['date'] + ' ' + timeline_df['time'])
                
                fig = px.scatter(timeline_df, x='datetime', y='confidence', 
                               color='predicted_class', size='confidence',
                               hover_data=['prediction_id', 'notes'],
                               title='Confidence Over Time',
                               color_discrete_map={
                                   'Glioma': '#e74c3c',
                                   'Meningioma': '#e67e22',
                                   'Pituitary': '#f39c12',
                                   'No Tumor': '#27ae60'
                               })
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Class distribution pie chart
                st.markdown("#### 🎯 Class Distribution")
                
                class_counts = predictions_df['predicted_class'].value_counts()
                
                fig_pie = px.pie(values=class_counts.values, names=class_counts.index,
                               title='Distribution of Predictions',
                               color=class_counts.index,
                               color_discrete_map={
                                   'Glioma': '#e74c3c',
                                   'Meningioma': '#e67e22',
                                   'Pituitary': '#f39c12',
                                   'No Tumor': '#27ae60'
                               })
                
                st.plotly_chart(fig_pie, use_container_width=True)
                
                # Detailed records table
                st.markdown("#### 📋 Detailed Records")
                
                # Format display columns
                display_df = predictions_df[[
                    'prediction_id', 'date', 'time', 'predicted_class', 
                    'confidence', 'notes', 'user'
                ]].copy()
                
                display_df['confidence'] = display_df['confidence'].apply(lambda x: f"{x*100:.2f}%")
                display_df.columns = ['ID', 'Date', 'Time', 'Prediction', 'Confidence', 'Notes', 'User']
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                # Export button
                csv = predictions_df.to_csv(index=False)
                st.download_button(
                    label="📥 Export History to CSV",
                    data=csv,
                    file_name=f"patient_{selected_patient}_history.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            else:
                st.info("📭 No prediction history for this patient yet.")
    
    # Sidebar - All patients overview
    with st.sidebar:
        # Theme toggle
        theme_toggle_button()
    
        st.markdown("---")
        
        st.markdown("### 📊 All Patients Overview")
        
        st.metric("Total Patients", len(patients))
        
        all_predictions = get_all_predictions()
        st.metric("Total Predictions", len(all_predictions))
        
        if not all_predictions.empty:
            st.metric("Today's Predictions", 
                     len(all_predictions[all_predictions['date'] == datetime.now().strftime("%Y-%m-%d")]))
        
        st.markdown("---")
        st.markdown("### 🔍 Quick Search")
        
        search_term = st.text_input("Search patients", placeholder="Enter name or ID")
        
        if search_term:
            matching_patients = [
                pid for pid, info in patients.items()
                if search_term.lower() in info['name'].lower() or search_term.lower() in pid.lower()
            ]
            
            if matching_patients:
                st.success(f"Found {len(matching_patients)} patients")
                for pid in matching_patients:
                    if st.button(f"{patients[pid]['name']} ({pid})", key=f"search_{pid}"):
                        st.session_state.patient_selector = pid
                        st.rerun()
            else:
                st.warning("No matching patients found")

if __name__ == "__main__":
    import time
    main()
