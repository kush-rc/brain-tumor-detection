"""
Theme switcher utility for light/dark mode
DEFAULT: Dark Theme with full Streamlit integration
"""

import streamlit as st

def init_theme():
    """Initialize theme in session state - defaults to DARK"""
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark'  # Default to dark theme
        apply_streamlit_theme('dark')

def apply_streamlit_theme(theme):
    """Apply theme to Streamlit's global config"""
    try:
        if theme == 'dark':
            # Dark theme colors
            st._config.set_option('theme.base', 'dark')
            st._config.set_option('theme.backgroundColor', '#0e1117')
            st._config.set_option('theme.secondaryBackgroundColor', '#262730')
            st._config.set_option('theme.textColor', '#fafafa')
            st._config.set_option('theme.primaryColor', '#667eea')
        else:
            # Light theme colors
            st._config.set_option('theme.base', 'light')
            st._config.set_option('theme.backgroundColor', '#ffffff')
            st._config.set_option('theme.secondaryBackgroundColor', '#f0f2f6')
            st._config.set_option('theme.textColor', '#262730')
            st._config.set_option('theme.primaryColor', '#667eea')
    except:
        # Config might be locked, ignore
        pass

def toggle_theme():
    """Toggle between light and dark theme"""
    if st.session_state.theme == 'light':
        st.session_state.theme = 'dark'
        apply_streamlit_theme('dark')
    else:
        st.session_state.theme = 'light'
        apply_streamlit_theme('light')
    
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
    
    # Apply Streamlit theme
    apply_streamlit_theme(theme)
    
    if theme == 'dark':
        # Dark theme CSS
        st.markdown("""
        <style>
            /* Global dark theme adjustments */
            .main {
                background-color: #0e1117;
                color: #fafafa;
            }
            
            .stApp {
                background-color: #0e1117;
            }
            
            [data-testid="stSidebar"] {
                background-color: #262730;
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
                background-color: #262730 !important;
                border-left: 5px solid #667eea;
                margin: 1rem 0;
                color: #fafafa !important;
            }
            
            .info-box h3 {
                color: #667eea !important;
                margin-bottom: 1rem;
            }
            
            .info-box ul {
                color: #e0e0e0 !important;
                list-style-position: inside;
            }
            
            .info-box li {
                margin: 0.5rem 0;
                color: #e0e0e0 !important;
            }
            
            .metric-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                padding: 1.5rem;
                border-radius: 10px;
                color: white !important;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            }
            
            .metric-card h2 {
                color: white !important;
                font-size: 2.5rem;
                margin: 0;
            }
            
            .metric-card p {
                color: white !important;
                margin: 0.5rem 0 0 0;
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
            
            /* Fix for dark boxes in features */
            div[data-testid="stVerticalBlock"] > div {
                background-color: transparent !important;
            }
        </style>
        """, unsafe_allow_html=True)
    else:
        # Light theme CSS
        st.markdown("""
        <style>
            /* Global light theme adjustments */
            .main {
                background-color: #ffffff;
                color: #262730;
            }
            
            .stApp {
                background-color: #ffffff;
            }
            
            [data-testid="stSidebar"] {
                background-color: #f0f2f6;
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
                background-color: #f0f2f6 !important;
                border-left: 5px solid #667eea;
                margin: 1rem 0;
                color: #262730 !important;
            }
            
            .info-box h3 {
                color: #667eea !important;
                margin-bottom: 1rem;
            }
            
            .info-box ul {
                color: #262730 !important;
                list-style-position: inside;
            }
            
            .info-box li {
                margin: 0.5rem 0;
                color: #262730 !important;
            }
            
            .metric-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                padding: 1.5rem;
                border-radius: 10px;
                color: white !important;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            
            .metric-card h2 {
                color: white !important;
                font-size: 2.5rem;
                margin: 0;
            }
            
            .metric-card p {
                color: white !important;
                margin: 0.5rem 0 0 0;
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
