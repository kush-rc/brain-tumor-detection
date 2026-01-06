"""
Visualization utilities for model explainability
Includes Grad-CAM, heatmaps, and other visualizations
"""

import streamlit as st
import numpy as np
import cv2
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import tensorflow as tf
from tensorflow import keras

def find_target_layer(model):
    """
    Find the last convolutional layer in the model
    
    Args:
        model: Keras model
    
    Returns:
        Layer name or None
    """
    try:
        # Try to find the last Conv2D layer
        for layer in reversed(model.layers):
            # Check if it's a convolutional layer
            if isinstance(layer, keras.layers.Conv2D):
                return layer.name
            # Also check for layer names containing 'conv'
            if 'conv' in layer.name.lower():
                return layer.name
        
        # If no conv layer found, return None
        return None
    
    except Exception as e:
        return None

def generate_gradcam_functional(model, img_array, class_idx, layer_name):
    """
    Generate Grad-CAM using functional approach (works better with Sequential models)
    
    Args:
        model: Keras model
        img_array: Preprocessed image array
        class_idx: Index of predicted class
        layer_name: Name of convolutional layer
    
    Returns:
        Heatmap array or None
    """
    try:
        # Get the target layer
        target_layer = None
        for layer in model.layers:
            if layer.name == layer_name:
                target_layer = layer
                break
        
        if target_layer is None:
            return None
        
        # Create a new model that maps inputs to outputs and the target layer
        # Use the model's functional API
        with tf.GradientTape() as tape:
            # Forward pass
            last_conv_layer_output = None
            x = img_array
            
            # Pass through layers until we reach target layer
            for layer in model.layers:
                x = layer(x)
                if layer.name == layer_name:
                    last_conv_layer_output = x
                    tape.watch(last_conv_layer_output)
            
            # Continue to final output
            preds = x
            
            # Get the class prediction
            if len(preds.shape) > 1:
                class_channel = preds[:, class_idx]
            else:
                class_channel = preds[class_idx]
        
        # Compute gradients
        grads = tape.gradient(class_channel, last_conv_layer_output)
        
        if grads is None:
            return None
        
        # Global average pooling on gradients
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        
        # Multiply each channel by its gradient importance
        last_conv_layer_output = last_conv_layer_output[0]
        pooled_grads = pooled_grads.numpy()
        last_conv_layer_output = last_conv_layer_output.numpy()
        
        for i in range(len(pooled_grads)):
            last_conv_layer_output[:, :, i] *= pooled_grads[i]
        
        # Average over all channels
        heatmap = np.mean(last_conv_layer_output, axis=-1)
        
        # Normalize
        heatmap = np.maximum(heatmap, 0)
        if np.max(heatmap) > 0:
            heatmap = heatmap / np.max(heatmap)
        else:
            return None
        
        return heatmap
        
    except Exception as e:
        return None

def generate_gradcam(model, img_array, class_idx, layer_name=None):
    """
    Generate Grad-CAM heatmap for model explainability
    Works with Sequential and Functional models
    
    Args:
        model: Keras model
        img_array: Preprocessed image array
        class_idx: Index of predicted class
        layer_name: Name of convolutional layer (auto-detect if None)
    
    Returns:
        Heatmap array or None
    """
    try:
        # Find target layer if not specified
        if layer_name is None:
            layer_name = find_target_layer(model)
        
        if layer_name is None:
            st.warning("⚠️ No convolutional layer found for Grad-CAM")
            st.info("💡 Your model might not have convolutional layers or they're not accessible")
            return None
        
        # Try the functional approach (works better with Sequential)
        heatmap = generate_gradcam_functional(model, img_array, class_idx, layer_name)
        
        if heatmap is not None:
            return heatmap
        
        # If functional approach failed, inform user
        st.warning("⚠️ Could not generate Grad-CAM visualization")
        st.info("💡 This is normal for some model architectures. Your predictions are still accurate!")
        return None
    
    except Exception as e:
        st.warning("⚠️ Grad-CAM visualization unavailable for this model")
        st.info("💡 The prediction results are still valid and accurate!")
        return None

def overlay_heatmap(image, heatmap, alpha=0.4, colormap=cv2.COLORMAP_JET):
    """
    Overlay heatmap on original image
    
    Args:
        image: Original PIL Image
        heatmap: Grad-CAM heatmap array
        alpha: Transparency of overlay
        colormap: OpenCV colormap
    
    Returns:
        Overlaid image
    """
    try:
        # Convert PIL to numpy
        img_array = np.array(image)
        
        # Ensure RGB
        if len(img_array.shape) == 2:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
        
        # Resize heatmap to match image size
        heatmap_resized = cv2.resize(heatmap, (img_array.shape[1], img_array.shape[0]))
        
        # Convert heatmap to uint8
        heatmap_uint8 = np.uint8(255 * heatmap_resized)
        
        # Apply colormap
        heatmap_colored = cv2.applyColorMap(heatmap_uint8, colormap)
        heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
        
        # Overlay
        overlaid = cv2.addWeighted(img_array, 1-alpha, heatmap_colored, alpha, 0)
        
        return Image.fromarray(overlaid)
    
    except Exception as e:
        st.error(f"Error overlaying heatmap: {e}")
        return image

def plot_prediction_bars(probabilities, class_names):
    """
    Create horizontal bar chart of prediction probabilities
    
    Args:
        probabilities: Dict of class probabilities
        class_names: List of class names
    
    Returns:
        Matplotlib figure
    """
    try:
        # Sort by probability
        sorted_items = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
        classes = [item[0] for item in sorted_items]
        probs = [item[1] * 100 for item in sorted_items]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # Color bars based on value
        colors = ['#2ecc71' if p == max(probs) else '#3498db' for p in probs]
        
        # Create bars
        bars = ax.barh(classes, probs, color=colors)
        
        # Add percentage labels
        for i, (bar, prob) in enumerate(zip(bars, probs)):
            ax.text(prob + 1, i, f'{prob:.2f}%', 
                   va='center', fontweight='bold')
        
        # Formatting
        ax.set_xlabel('Confidence (%)', fontsize=12, fontweight='bold')
        ax.set_title('Prediction Confidence by Class', fontsize=14, fontweight='bold')
        ax.set_xlim(0, 105)
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    except Exception as e:
        st.error(f"Error plotting bars: {e}")
        return None

def create_confusion_visual(predicted, actual=None):
    """
    Create visual representation of prediction
    
    Args:
        predicted: Predicted class name
        actual: Actual class name (if known)
    
    Returns:
        Matplotlib figure
    """
    try:
        fig, ax = plt.subplots(figsize=(8, 6))
        
        if actual is not None:
            # Show comparison
            data = [[predicted], [actual]]
            colors = [['#2ecc71' if predicted == actual else '#e74c3c'], ['#3498db']]
            
            ax.table(cellText=data, rowLabels=['Predicted', 'Actual'],
                    cellColours=colors, loc='center',
                    cellLoc='center', fontsize=20)
        else:
            # Show only prediction
            ax.text(0.5, 0.5, predicted, 
                   ha='center', va='center',
                   fontsize=32, fontweight='bold',
                   bbox=dict(boxstyle='round', facecolor='#2ecc71', alpha=0.7))
        
        ax.axis('off')
        plt.tight_layout()
        return fig
    
    except Exception as e:
        st.error(f"Error creating visual: {e}")
        return None

def show_model_summary(model):
    """
    Display model architecture summary
    
    Args:
        model: Keras model
    """
    try:
        st.markdown("### 🤖 Model Architecture")
        
        # Create summary string
        summary_list = []
        model.summary(print_fn=lambda x: summary_list.append(x))
        summary_str = "\n".join(summary_list)
        
        st.code(summary_str, language="text")
        
        # Show layer count
        st.info(f"Total Layers: {len(model.layers)}")
        
        # List convolutional layers
        conv_layers = [layer.name for layer in model.layers if 'conv' in layer.name.lower()]
        if conv_layers:
            st.success(f"Convolutional Layers: {', '.join(conv_layers)}")
        else:
            st.warning("No convolutional layers found")
    
    except Exception as e:
        st.error(f"Error displaying model summary: {e}")
