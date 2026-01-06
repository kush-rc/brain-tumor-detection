"""
Database utilities for patient history and predictions
Uses CSV files for data storage
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import uuid
import os

# Data files
DATA_DIR = Path("data")
PATIENTS_FILE = DATA_DIR / "patients.csv"
PREDICTIONS_FILE = DATA_DIR / "predictions_history.csv"

def init_database():
    """Initialize database CSV files if they don't exist"""
    try:
        # Create data directory
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Initialize patients file
        if not PATIENTS_FILE.exists():
            patients_df = pd.DataFrame(columns=[
                'patient_id', 'name', 'age', 'gender', 'contact', 
                'medical_history', 'created_at', 'updated_at', 'total_scans', 'last_scan'
            ])
            patients_df.to_csv(PATIENTS_FILE, index=False)
        
        # Initialize predictions file
        if not PREDICTIONS_FILE.exists():
            predictions_df = pd.DataFrame(columns=[
                'prediction_id', 'patient_id', 'patient_name', 'date', 'time',
                'predicted_class', 'confidence', 'glioma_prob', 'meningioma_prob',
                'no_tumor_prob', 'pituitary_prob', 'image_path', 'notes', 'user'
            ])
            predictions_df.to_csv(PREDICTIONS_FILE, index=False)
        
        return True
    
    except Exception as e:
        st.error(f"Error initializing database: {e}")
        return False

def load_patients():
    """
    Load all patients from CSV
    
    Returns:
        Dictionary of patients {patient_id: patient_data}
    """
    try:
        init_database()
        
        df = pd.read_csv(PATIENTS_FILE)
        
        if df.empty:
            return {}
        
        # Convert DataFrame to dictionary
        patients = {}
        for _, row in df.iterrows():
            patient_id = row['patient_id']
            patients[patient_id] = {
                'name': row['name'],
                'age': row['age'],
                'gender': row['gender'],
                'contact': row.get('contact', ''),
                'medical_history': row.get('medical_history', ''),
                'created_at': row.get('created_at', ''),
                'updated_at': row.get('updated_at', ''),
                'total_scans': int(row.get('total_scans', 0)),
                'last_scan': row.get('last_scan', 'Never')
            }
        
        return patients
    
    except Exception as e:
        st.error(f"Error loading patients: {e}")
        return {}

def save_patients_df(df):
    """
    Save patients DataFrame to CSV
    
    Args:
        df: Patients DataFrame
    """
    try:
        df.to_csv(PATIENTS_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving patients: {e}")
        return False

def add_patient(patient_id, name, age, gender, contact="", medical_history=""):
    """
    Add a new patient to database
    
    Args:
        patient_id: Unique patient ID
        name: Patient name
        age: Patient age
        gender: Patient gender
        contact: Contact information
        medical_history: Medical history notes
    
    Returns:
        Boolean indicating success
    """
    try:
        df = pd.read_csv(PATIENTS_FILE)
        
        # Check if patient already exists
        if patient_id in df['patient_id'].values:
            st.error("❌ Patient ID already exists!")
            return False
        
        # Create new patient record
        new_patient = pd.DataFrame([{
            'patient_id': patient_id,
            'name': name,
            'age': age,
            'gender': gender,
            'contact': contact,
            'medical_history': medical_history,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'total_scans': 0,
            'last_scan': 'Never'
        }])
        
        # Append to CSV
        df = pd.concat([df, new_patient], ignore_index=True)
        df.to_csv(PATIENTS_FILE, index=False)
        
        return True
    
    except Exception as e:
        st.error(f"Error adding patient: {e}")
        return False

def update_patient(patient_id, **kwargs):
    """
    Update patient information
    
    Args:
        patient_id: Patient ID
        **kwargs: Fields to update (name, age, gender, contact, medical_history)
    
    Returns:
        Boolean indicating success
    """
    try:
        df = pd.read_csv(PATIENTS_FILE)
        
        # Find patient
        mask = df['patient_id'] == patient_id
        
        if not mask.any():
            st.error("❌ Patient not found!")
            return False
        
        # Update fields
        for key, value in kwargs.items():
            if key in df.columns and key != 'patient_id':
                df.loc[mask, key] = value
        
        # Update timestamp
        df.loc[mask, 'updated_at'] = datetime.now().isoformat()
        
        # Save
        df.to_csv(PATIENTS_FILE, index=False)
        
        return True
    
    except Exception as e:
        st.error(f"Error updating patient: {e}")
        return False

def get_patient(patient_id):
    """
    Get patient information
    
    Args:
        patient_id: Patient ID
    
    Returns:
        Patient dictionary or None
    """
    try:
        df = pd.read_csv(PATIENTS_FILE)
        
        patient_row = df[df['patient_id'] == patient_id]
        
        if patient_row.empty:
            return None
        
        # Convert to dictionary
        patient = patient_row.iloc[0].to_dict()
        
        # Handle NaN values
        for key, value in patient.items():
            if pd.isna(value):
                patient[key] = '' if key in ['contact', 'medical_history'] else 0
        
        return patient
    
    except Exception as e:
        st.error(f"Error getting patient: {e}")
        return None

def save_prediction(patient_id, patient_name, predicted_class, confidence, 
                   all_probabilities, image_path=None, notes="", user="system"):
    """
    Save a prediction to history
    
    Args:
        patient_id: Patient ID
        patient_name: Patient name
        predicted_class: Predicted tumor class
        confidence: Confidence score
        all_probabilities: Dictionary of all class probabilities
        image_path: Path to saved image
        notes: Additional notes
        user: Username who made the prediction
    
    Returns:
        Prediction ID
    """
    try:
        init_database()
        
        # Generate unique prediction ID
        prediction_id = str(uuid.uuid4())[:8]
        
        # Current timestamp
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        
        # Create prediction record
        new_prediction = pd.DataFrame([{
            'prediction_id': prediction_id,
            'patient_id': patient_id,
            'patient_name': patient_name,
            'date': date_str,
            'time': time_str,
            'predicted_class': predicted_class,
            'confidence': confidence,
            'glioma_prob': all_probabilities.get('Glioma', 0),
            'meningioma_prob': all_probabilities.get('Meningioma', 0),
            'no_tumor_prob': all_probabilities.get('No Tumor', 0),
            'pituitary_prob': all_probabilities.get('Pituitary', 0),
            'image_path': image_path or "",
            'notes': notes,
            'user': user
        }])
        
        # Append to CSV
        df = pd.read_csv(PREDICTIONS_FILE)
        df = pd.concat([df, new_prediction], ignore_index=True)
        df.to_csv(PREDICTIONS_FILE, index=False)
        
        # Update patient scan count
        patients_df = pd.read_csv(PATIENTS_FILE)
        mask = patients_df['patient_id'] == patient_id
        
        if mask.any():
            patients_df.loc[mask, 'total_scans'] = patients_df.loc[mask, 'total_scans'].fillna(0) + 1
            patients_df.loc[mask, 'last_scan'] = date_str
            patients_df.to_csv(PATIENTS_FILE, index=False)
        
        return prediction_id
    
    except Exception as e:
        st.error(f"Error saving prediction: {e}")
        return None

def get_patient_predictions(patient_id):
    """
    Get all predictions for a patient
    
    Args:
        patient_id: Patient ID
    
    Returns:
        DataFrame of predictions
    """
    try:
        init_database()
        
        df = pd.read_csv(PREDICTIONS_FILE)
        
        patient_predictions = df[df['patient_id'] == patient_id]
        
        return patient_predictions.sort_values('date', ascending=False)
    
    except Exception as e:
        st.error(f"Error getting predictions: {e}")
        return pd.DataFrame()

def get_all_predictions():
    """
    Get all predictions
    
    Returns:
        DataFrame of all predictions
    """
    try:
        init_database()
        
        df = pd.read_csv(PREDICTIONS_FILE)
        
        return df.sort_values('date', ascending=False)
    
    except Exception as e:
        st.error(f"Error getting predictions: {e}")
        return pd.DataFrame()

def delete_patient(patient_id):
    """
    Delete a patient and all their predictions
    
    Args:
        patient_id: Patient ID
    
    Returns:
        Boolean indicating success
    """
    try:
        # Delete from patients
        patients_df = pd.read_csv(PATIENTS_FILE)
        patients_df = patients_df[patients_df['patient_id'] != patient_id]
        patients_df.to_csv(PATIENTS_FILE, index=False)
        
        # Delete predictions
        predictions_df = pd.read_csv(PREDICTIONS_FILE)
        predictions_df = predictions_df[predictions_df['patient_id'] != patient_id]
        predictions_df.to_csv(PREDICTIONS_FILE, index=False)
        
        return True
    
    except Exception as e:
        st.error(f"Error deleting patient: {e}")
        return False

def get_statistics():
    """
    Get overall system statistics
    
    Returns:
        Dictionary with statistics
    """
    try:
        init_database()
        
        patients_df = pd.read_csv(PATIENTS_FILE)
        predictions_df = pd.read_csv(PREDICTIONS_FILE)
        
        # Today's date
        today = datetime.now().strftime("%Y-%m-%d")
        
        stats = {
            'total_patients': len(patients_df),
            'total_predictions': len(predictions_df),
            'predictions_today': len(predictions_df[predictions_df['date'] == today]),
            'class_distribution': predictions_df['predicted_class'].value_counts().to_dict() if not predictions_df.empty else {},
            'average_confidence': predictions_df['confidence'].mean() if not predictions_df.empty and 'confidence' in predictions_df.columns else 0
        }
        
        return stats
    
    except Exception as e:
        st.error(f"Error getting statistics: {e}")
        return {
            'total_patients': 0,
            'total_predictions': 0,
            'predictions_today': 0,
            'class_distribution': {},
            'average_confidence': 0
        }

def export_all_data():
    """
    Export all data as a dictionary of DataFrames
    
    Returns:
        Dictionary with 'patients' and 'predictions' DataFrames
    """
    try:
        return {
            'patients': pd.read_csv(PATIENTS_FILE),
            'predictions': pd.read_csv(PREDICTIONS_FILE)
        }
    except Exception as e:
        st.error(f"Error exporting data: {e}")
        return None

def list_people():
    """
    List all patient names
    
    Returns:
        List of patient IDs
    """
    try:
        df = pd.read_csv(PATIENTS_FILE)
        return df['patient_id'].tolist()
    except Exception as e:
        st.error(f"Error listing people: {e}")
        return []
