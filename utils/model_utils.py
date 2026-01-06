"""
Model utilities for brain tumor detection
Handles model loading, prediction, and preprocessing
"""

import streamlit as st
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from PIL import Image, ImageOps
import time
from pathlib import Path

# Model configuration
IMG_SIZE = (150, 150)
CLASS_NAMES = ["Glioma", "Meningioma", "No Tumor", "Pituitary"]

@st.cache_resource(show_spinner=False)
def load_brain_tumor_model():
    """
    Load the pre-trained model with caching
    Returns: Loaded Keras model
    """
    try:
        model_path = Path("models/brain_tumor_detection_model_v1_96%_Kaggle.h5")
        
        if not model_path.exists():
            # Try alternate path for Streamlit Cloud
            model_path = Path("brain_tumor_detection_model_v1_96%_Kaggle.h5")
        
        if not model_path.exists():
            st.error("❌ Model file not found!")
            return None
        
        with st.spinner("🔄 Loading AI model..."):
            model = load_model(str(model_path))
            st.success("✅ Model loaded successfully!")
        
        return model
    
    except Exception as e:
        st.error(f"❌ Error loading model: {e}")
        return None

def preprocess_image(image, target_size=IMG_SIZE):
    """
    Preprocess image for model prediction
    
    Args:
        image: PIL Image object
        target_size: Target size tuple (width, height)
    
    Returns:
        Preprocessed numpy array
    """
    try:
        # Resize image
        image = ImageOps.fit(image, target_size, Image.Resampling.LANCZOS)
        
        # Convert to array and normalize
        img_array = np.asarray(image).astype("float32") / 255.0
        
        # Handle PNG with alpha channel
        if img_array.shape[-1] == 4:
            img_array = img_array[..., :3]
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    
    except Exception as e:
        st.error(f"Error preprocessing image: {e}")
        return None

def predict_tumor(model, image):
    """
    Make prediction on preprocessed image
    
    Args:
        model: Loaded Keras model
        image: PIL Image object
    
    Returns:
        dict with prediction results
    """
    try:
        start_time = time.time()
        
        # Preprocess
        img_array = preprocess_image(image)
        
        if img_array is None:
            return None
        
        # Predict
        predictions = model.predict(img_array, verbose=0)[0]
        
        # Get results
        predicted_class_idx = np.argmax(predictions)
        predicted_class = CLASS_NAMES[predicted_class_idx]
        confidence = float(predictions[predicted_class_idx])
        
        prediction_time = time.time() - start_time
        
        # Create detailed results
        results = {
            "predicted_class": predicted_class,
            "predicted_class_idx": int(predicted_class_idx),
            "confidence": confidence,
            "all_probabilities": {
                CLASS_NAMES[i]: float(predictions[i]) 
                for i in range(len(CLASS_NAMES))
            },
            "prediction_time": prediction_time
        }
        
        return results
    
    except Exception as e:
        st.error(f"Error making prediction: {e}")
        return None

def get_class_description(class_name):
    """
    Get medical description for each tumor class
    
    Args:
        class_name: Name of the tumor class
    
    Returns:
        Description string
    """
    descriptions = {
        "Glioma": """
        **Glioma** is a type of tumor that occurs in the brain and spinal cord. 
        Gliomas begin in the gluey supportive cells (glial cells) that surround 
        nerve cells. They are the most common type of malignant brain tumor.
        
        **Symptoms may include:**
        - Headaches
        - Seizures
        - Memory problems
        - Changes in personality or behavior
        """,
        
        "Meningioma": """
        **Meningioma** is a tumor that arises from the meninges — the membranes 
        that surround your brain and spinal cord. Most meningiomas are noncancerous 
        (benign), though rarely they can be cancerous (malignant).
        
        **Symptoms may include:**
        - Vision changes
        - Headaches that worsen over time
        - Hearing loss or ringing in ears
        - Memory loss
        """,
        
        "No Tumor": """
        **No Tumor** indicates that the MRI scan shows normal brain tissue 
        without any detectable tumors. This is a healthy brain scan.
        
        **Note:** A normal scan doesn't rule out all neurological conditions. 
        Consult with a healthcare professional for complete evaluation.
        """,
        
        "Pituitary": """
        **Pituitary Tumor** is an abnormal growth in the pituitary gland, 
        which is located at the base of your brain. Most pituitary tumors are 
        noncancerous (adenomas) and remain in your pituitary gland.
        
        **Symptoms may include:**
        - Vision problems
        - Headaches
        - Hormonal imbalances
        - Unexplained weight changes
        """
    }
    
    return descriptions.get(class_name, "No description available.")

def get_confidence_color(confidence):
    """
    Get color code based on confidence level
    
    Args:
        confidence: Confidence score (0-1)
    
    Returns:
        Color string for Streamlit
    """
    if confidence >= 0.9:
        return "green"
    elif confidence >= 0.75:
        return "blue"
    elif confidence >= 0.6:
        return "orange"
    else:
        return "red"
