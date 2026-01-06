"""
About Page
Information about the system, model, and documentation
"""

import streamlit as st
from utils.theme_switcher import theme_toggle_button, apply_custom_css, init_theme


# Page config
st.set_page_config(page_title="About", page_icon="ℹ️", layout="wide")
init_theme()
apply_custom_css()  

def main():
    """Main function for about page"""
    
    st.title("ℹ️ About Brain Tumor Detection AI")
    st.markdown("Learn about the system, model architecture, and usage guidelines")
    
    # Sidebar with theme toggle
    with st.sidebar:
        # Theme toggle button
        theme_toggle_button()
        
        st.markdown("---")
        
        st.markdown("### 📚 Quick Links")
        st.markdown("""
        - [User Manual](#overview)
        - [Model Details](#model-architecture)
        - [Technology Stack](#technology-stack)
        - [Contact](#contact--support)
        """)
        
        st.markdown("---")
        
        st.markdown("### 📊 Version Info")
        st.code("""
            Version: 1.0.0
            Release: Jan 2026
            Model: CNN 96%
        """)
        
        st.markdown("---")
        
        st.markdown("### 🌟 Features")
        st.success("✅ 96% Accuracy")
        st.success("✅ Real-time Analysis")
        st.success("✅ PDF Reports")
        st.success("✅ Patient History")
    
    st.markdown("---")
    
    st.markdown("---")
    
    # Overview
    st.markdown("## 🎯 Overview")
    
    st.markdown("""
    This Brain Tumor Detection System is an advanced AI-powered medical imaging application 
    that uses Convolutional Neural Networks (CNN) to classify brain tumors from MRI scans. 
    The system achieves **96% accuracy** on test data and can identify four distinct categories:
    
    - **Glioma**: Malignant brain tumors arising from glial cells
    - **Meningioma**: Typically benign tumors from the meninges
    - **Pituitary**: Tumors in the pituitary gland
    - **No Tumor**: Healthy brain tissue
    
    ### Key Features:
    
    - 🔍 **Single Image Analysis**: Upload and analyze individual MRI scans with instant results
    - 📊 **Batch Processing**: Analyze multiple scans simultaneously for efficiency
    - 🔥 **Grad-CAM Visualization**: Understand model decisions with attention heatmaps
    - 📋 **Patient History**: Track and manage patient records over time
    - 📄 **PDF Reports**: Generate professional medical reports
    - 👥 **User Management**: Secure authentication and role-based access control
    - 📈 **Analytics Dashboard**: Comprehensive system analytics and insights
    """)
    
    st.markdown("---")
    
    # Model Architecture
    st.markdown("## 🤖 Model Architecture")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        ### CNN Architecture Details
        
        **Architecture Type:** Convolutional Neural Network (CNN)
        
        **Input Specifications:**
        - Image Size: 150 x 150 pixels
        - Color Channels: 3 (RGB)
        - Input Shape: (150, 150, 3)
        
        **Training Details:**
        - Framework: TensorFlow/Keras
        - Training Accuracy: ~96%
        - Validation Accuracy: ~96%
        - Optimizer: Adam
        - Loss Function: Categorical Crossentropy
        
        **Output:**
        - 4 classes with probability scores
        - Softmax activation for multi-class classification
        """)
    
    with col2:
        st.markdown("""
        ### Model Performance
        
        **Accuracy Metrics:**
        - Overall Accuracy: 96%
        - Precision: High across all classes
        - Recall: Balanced for clinical use
        - F1-Score: Optimized for medical diagnosis
        
        **Class-wise Performance:**
        - Glioma: High sensitivity
        - Meningioma: Excellent specificity
        - Pituitary: Balanced accuracy
        - No Tumor: Very high accuracy
        
        **Inference Speed:**
        - Single prediction: < 2 seconds
        - Batch processing: ~1-2 sec per image
        - Grad-CAM generation: +1 second
        """)
    
    st.markdown("---")
    
    # Technology Stack
    st.markdown("## 🛠️ Technology Stack")
    
    tech_col1, tech_col2, tech_col3 = st.columns(3)
    
    with tech_col1:
        st.markdown("""
        ### Frontend
        - **Streamlit**: Web interface
        - **Plotly**: Interactive visualizations
        - **Matplotlib**: Static plots
        - **Pillow**: Image processing
        """)
    
    with tech_col2:
        st.markdown("""
        ### Backend
        - **TensorFlow**: Deep learning
        - **Keras**: Model building
        - **NumPy**: Numerical computing
        - **Pandas**: Data management
        """)
    
    with tech_col3:
        st.markdown("""
        ### Other Tools
        - **ReportLab**: PDF generation
        - **bcrypt**: Password hashing
        - **OpenCV**: Image operations
        - **JSON**: Data storage
        """)
    
    st.markdown("---")
    
    # Usage Guidelines
    st.markdown("## 📖 Usage Guidelines")
    
    st.markdown("""
    ### For Healthcare Professionals
    
    1. **Image Quality**: Use high-resolution MRI scans for best results
    2. **Multiple Views**: Analyze multiple scan angles when available
    3. **Patient History**: Always maintain complete patient records
    4. **Clinical Context**: Combine AI predictions with clinical examination
    5. **Documentation**: Generate PDF reports for medical records
    
    ### For Administrators
    
    1. **User Management**: Regularly review user access and permissions
    2. **Data Backup**: Implement regular database backups
    3. **System Monitoring**: Track prediction accuracy and system performance
    4. **Updates**: Keep model and dependencies up to date
    5. **Security**: Enforce strong passwords and access controls
    
    ### Best Practices
    
    - ✅ Always verify AI predictions with clinical expertise
    - ✅ Use Grad-CAM visualizations to understand model decisions
    - ✅ Track patient history for longitudinal analysis
    - ✅ Generate reports for documentation and referrals
    - ✅ Maintain HIPAA compliance for patient data
    - ❌ Never use as the sole diagnostic tool
    - ❌ Don't ignore clinical symptoms contradicting AI results
    - ❌ Avoid low-quality or corrupted images
    """)
    
    st.markdown("---")
    
    # Limitations and Disclaimer
    st.markdown("## ⚠️ Limitations & Disclaimer")
    
    st.error("""
    ### Medical Disclaimer
    
    This Brain Tumor Detection System is designed for **research and educational purposes only**. 
    
    **Important Notes:**
    
    - This tool should **NOT** be used as the sole basis for medical diagnosis
    - Always consult qualified healthcare professionals for proper medical evaluation
    - AI predictions may contain errors or inaccuracies
    - Clinical judgment should always take precedence over AI suggestions
    - The system is not FDA-approved for clinical use
    
    **Limitations:**
    
    - Model accuracy is ~96% on test data, but individual results may vary
    - Performance depends on image quality and scan protocols
    - Rare tumor types may not be accurately classified
    - System requires validation on diverse patient populations
    - Cannot detect tumors smaller than resolution limits
    
    **Data Privacy:**
    
    - Patient data should be handled according to HIPAA guidelines
    - Secure storage and transmission of medical images required
    - User authentication protects sensitive information
    - Regular security audits recommended
    """)
    
    st.markdown("---")
    
    # Contact and Support
    st.markdown("## 📞 Contact & Support")
    
    support_col1, support_col2 = st.columns(2)
    
    with support_col1:
        st.markdown("""
        ### Technical Support
        
        **Email:** kushchhunchha@gmail.com  
        **Documentation:** [GitHub Wiki](https://github.com/kush-rc/brain-tumor-detection)  
        **Issues:** [GitHub Issues](https://github.com/kush-rc/brain-tumor-detection/issues)  
        **Response Time:** 24-48 hours
        """)
    
    with support_col2:
        st.markdown("""
        ### Resources
        
        - 📖 [User Manual](https://github.com/kush-rc/brain-tumor-detection/wiki)
        - 🎓 [Tutorial Videos](https://youtube.com)
        - 💬 [Community Forum](https://github.com/discussions)
        - 📊 [Model Documentation](https://github.com/kush-rc/brain-tumor-detection/blob/main/MODEL.md)
        """)
    
    st.markdown("---")
    
    # Credits
    st.markdown("## 👏 Credits & Acknowledgments")
    
    st.markdown("""
    ### Development Team
    
    - **Lead Developer**: Your Name
    - **ML Engineer**: Team Member
    - **Medical Advisor**: Dr. Medical Professional
    - **UI/UX Designer**: Designer Name
    
    ### Dataset
    
    - Brain MRI Images Dataset (Kaggle)
    - Training samples: 3000+ images
    - Test samples: 1000+ images
    
    ### Technologies
    
    - TensorFlow & Keras teams
    - Streamlit developers
    - Open-source community
    
    ### References
    
    1. Research paper on CNN for brain tumor classification
    2. Grad-CAM: Visual Explanations from Deep Networks
    3. Medical imaging best practices
    """)
    
    st.markdown("---")
    
    # Version Information
    st.markdown("## 📌 Version Information")
    
    st.code("""
    Version: 1.0.0
    Release Date: January 2026
    Last Updated: January 6, 2026
    License: MIT License
    Repository: github.com/kush-rc/brain-tumor-detection
    """)
    
    st.markdown("---")
    
    # Footer
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #7f8c8d;">
        <p>© 2026 Brain Tumor Detection AI System | All Rights Reserved</p>
        <p>Built with ❤️ using Streamlit and TensorFlow</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
