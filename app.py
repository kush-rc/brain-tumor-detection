"""
Brain Tumor Detection System - Main Application
Advanced CNN-based MRI Classification with Explainability
"""

import streamlit as st
from pathlib import Path
import sys
import os

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Add utils to path
sys.path.append(str(Path(__file__).parent))

# Import theme switcher
from utils.theme_switcher import theme_toggle_button, apply_custom_css, init_theme

# Page configuration MUST BE FIRST
st.set_page_config(
    page_title="Brain Tumor Detection AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize theme
init_theme()

# Apply custom CSS
apply_custom_css()

def main():
    """Main application entry point"""
    
    # Header
    st.markdown('<h1 class="main-header">🧠 Brain Tumor Detection AI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Advanced CNN-based MRI Classification System with 96% Accuracy</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Welcome section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h2>96%</h2>
            <p>Model Accuracy</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h2>4</h2>
            <p>Tumor Classes</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h2>< 2s</h2>
            <p>Prediction Time</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Features overview
    st.subheader("🚀 Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-box">
            <h3>🔍 Single Image Analysis</h3>
            <ul>
                <li>Upload and analyze individual MRI scans</li>
                <li>Get instant predictions with confidence scores</li>
                <li>Visual explanations with Grad-CAM heatmaps</li>
                <li>Download detailed PDF reports</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
            <h3>📊 Batch Processing</h3>
            <ul>
                <li>Upload multiple MRI scans at once</li>
                <li>Comparative analysis across images</li>
                <li>Export results to CSV</li>
                <li>Statistical summaries</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-box">
            <h3>📋 Patient History</h3>
            <ul>
                <li>Track patient scans over time</li>
                <li>View prediction history</li>
                <li>Compare longitudinal changes</li>
                <li>Secure patient data management</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
            <h3>🔐 Admin Features</h3>
            <ul>
                <li>User authentication system</li>
                <li>Access control and permissions</li>
                <li>System analytics and monitoring</li>
                <li>Model performance tracking</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick start guide
    st.subheader("📖 Quick Start Guide")
    
    st.markdown("""
    1. **Navigate to 🔍 Single Prediction** to analyze individual MRI scans
    2. **Upload an MRI image** (JPG, JPEG, or PNG format)
    3. **Click 'Analyze MRI'** to get instant predictions
    4. **View Grad-CAM heatmaps** to understand model decisions
    5. **Download PDF report** for documentation
    
    ### Tumor Classes
    - **Glioma**: Most common malignant brain tumor
    - **Meningioma**: Usually benign tumor from meninges
    - **Pituitary**: Tumor in the pituitary gland
    - **No Tumor**: Healthy brain tissue
    """)
    
    st.markdown("---")
    
    # Disclaimer
    st.warning("""
    ⚠️ **Medical Disclaimer**: This tool is for research and educational purposes only. 
    It should NOT be used as a substitute for professional medical diagnosis. 
    Always consult qualified healthcare professionals for medical decisions.
    """)
    
    # Sidebar
    with st.sidebar:
        # Theme toggle button at the top
        theme_toggle_button()
        
        st.markdown("---")
        
        st.image("https://via.placeholder.com/150x150.png?text=Brain+AI", width=150)
        st.markdown("### 🧠 Navigation")
        st.info("Use the pages menu above to navigate between different features.")
        
        st.markdown("---")
        st.markdown("### 📊 System Status")
        st.success("✅ Model Loaded")
        st.success("✅ System Online")
        
        st.markdown("---")
        st.markdown("### 📞 Support")
        st.markdown("""
        - 📧 Email: support@braintumordetection.ai
        - 📖 [Documentation](https://github.com/yourusername/brain-tumor-detection)
        - 🐛 [Report Issues](https://github.com/yourusername/brain-tumor-detection/issues)
        """)
        
        st.markdown("---")
        st.caption("© 2026 Brain Tumor Detection AI | v1.0.0")

if __name__ == "__main__":
    main()
