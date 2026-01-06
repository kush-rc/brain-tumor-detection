"""
Theme switcher utility for light/dark mode
DEFAULT: Dark Theme
"""

import streamlit as st

def init_theme():
    """Initialize theme in session state - defaults to DARK"""
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark'  # Default to dark theme

def toggle_theme():
    """Toggle between light and dark theme"""
    if st.session_state.theme == 'light':
        st.session_state.theme = 'dark'
    else:
        st.session_state.theme = 'light'
    
    st.rerun()

def get_theme_icon():
    """Get icon based on current theme"""
    if st.session_state.get('theme', 'dark') == 'light':
        return "🌙"  # Moon for switching to dark
    else:
        return "☀️"  # Sun for switching to light

def apply_custom_css():
    """Apply custom CSS that works with both themes"""
    theme = st.session_state.get('theme', 'dark')  # Default to dark
    
    if theme == 'dark':
        # Dark theme CSS
        st.markdown("""
        <style>
            /* Force dark theme */
            :root {
                --background-color: #0e1117;
                --secondary-background-color: #262730;
                --text-color: #fafafa;
            }
            
            .main-header {
                font-size: 3rem;
                font-weight: bold;
                text-align: center;
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                padding: 1rem 0;
            }
            .info-box {
                padding: 1.5rem;
                border-radius: 10px;
                background-color: #262730;
                border-left: 5px solid #667eea;
                margin: 1rem 0;
            }
            .metric-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 1rem;
                border-radius: 10px;
                color: white;
                text-align: center;
            }
            .prediction-box {
                padding: 2rem;
                border-radius: 15px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
                margin: 1rem 0;
            }
            .stButton>button {
                border-radius: 10px;
                height: 3rem;
                font-weight: bold;
            }
        </style>
        """, unsafe_allow_html=True)
    else:
        # Light theme CSS
        st.markdown("""
        <style>
            .main-header {
                font-size: 3rem;
                font-weight: bold;
                text-align: center;
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                padding: 1rem 0;
            }
            .info-box {
                padding: 1.5rem;
                border-radius: 10px;
                background-color: #f0f2f6;
                border-left: 5px solid #667eea;
                margin: 1rem 0;
            }
            .metric-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 1rem;
                border-radius: 10px;
                color: white;
                text-align: center;
            }
            .prediction-box {
                padding: 2rem;
                border-radius: 15px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
                margin: 1rem 0;
            }
            .stButton>button {
                border-radius: 10px;
                height: 3rem;
                font-weight: bold;
            }
        </style>
        """, unsafe_allow_html=True)

def theme_toggle_button():
    """Display theme toggle button in sidebar"""
    init_theme()
    
    icon = get_theme_icon()
    theme_name = "Light Mode" if st.session_state.theme == 'dark' else "Dark Mode"
    
    if st.sidebar.button(f"{icon} {theme_name}", use_container_width=True, key="theme_toggle"):
        toggle_theme()
