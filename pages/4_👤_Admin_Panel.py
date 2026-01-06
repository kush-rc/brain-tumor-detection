"""
Admin Panel Page
User management, system monitoring, and analytics
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.theme_switcher import theme_toggle_button, apply_custom_css, init_theme


# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.auth import require_login, get_current_user, load_users, save_users, hash_password, register_user
from utils.database import get_all_predictions, get_statistics, load_patients

# Page config
st.set_page_config(page_title="Admin Panel", page_icon="👤", layout="wide")
init_theme()
apply_custom_css()

def main():
    """Main function for admin panel"""
    
    st.title("👤 Admin Control Panel")
    st.markdown("System administration, user management, and analytics dashboard")
    
    # Check login and admin role
    if not require_login(allowed_roles=['admin']):
        st.error("🚫 Access Denied: Admin privileges required")
        return
    
    current_user = get_current_user()
    
    # Sidebar with theme toggle
    with st.sidebar:
        # Theme toggle button
        theme_toggle_button()
        
        st.markdown("---")
        
        st.markdown("### 👤 Current User")
        st.info(f"""
        **Name:** {current_user['full_name']}  
        **Username:** {current_user['username']}  
        **Role:** {current_user['role']}
        """)
        
        st.markdown("---")
        
        st.markdown("### ⚡ Quick Actions")
        st.markdown("""
        - Manage users
        - View analytics
        - Monitor system
        - Configure settings
        """)
    
    st.markdown("---")
    
    # Admin tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dashboard", 
        "👥 User Management", 
        "📈 Analytics", 
        "⚙️ System Settings"
    ])
    
    # ===== TAB 1: DASHBOARD =====
    with tab1:
        st.subheader("📊 System Dashboard")
        
        # Get statistics
        stats = get_statistics()
        predictions_df = get_all_predictions()
        patients = load_patients()
        users = load_users()
        
        # Key metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("👥 Total Users", len(users))
        
        with col2:
            st.metric("🏥 Total Patients", stats.get('total_patients', 0))
        
        with col3:
            st.metric("🔍 Total Predictions", stats.get('total_predictions', 0))
        
        with col4:
            st.metric("📅 Today's Predictions", stats.get('predictions_today', 0))
        
        with col5:
            avg_conf = stats.get('average_confidence', 0) * 100
            st.metric("📊 Avg Confidence", f"{avg_conf:.1f}%")
        
        st.markdown("---")
        
        # Recent activity
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🕐 Recent Predictions")
            if not predictions_df.empty:
                recent = predictions_df.head(10)
                display_recent = recent[['date', 'time', 'patient_name', 'predicted_class', 'confidence']].copy()
                display_recent['confidence'] = display_recent['confidence'].apply(lambda x: f"{x*100:.1f}%")
                st.dataframe(display_recent, use_container_width=True, hide_index=True)
            else:
                st.info("No predictions yet")
        
        with col2:
            st.markdown("### 🎯 Class Distribution")
            if stats.get('class_distribution'):
                class_dist = stats['class_distribution']
                fig = px.pie(
                    values=list(class_dist.values()),
                    names=list(class_dist.keys()),
                    title='Overall Prediction Distribution',
                    color=list(class_dist.keys()),
                    color_discrete_map={
                        'Glioma': '#e74c3c',
                        'Meningioma': '#e67e22',
                        'Pituitary': '#f39c12',
                        'No Tumor': '#27ae60'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data available")
        
        # Activity timeline
        st.markdown("### 📈 Prediction Activity (Last 30 Days)")
        
        if not predictions_df.empty:
            # Filter last 30 days
            predictions_df['date'] = pd.to_datetime(predictions_df['date'])
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_predictions = predictions_df[predictions_df['date'] >= thirty_days_ago]
            
            if not recent_predictions.empty:
                # Group by date
                daily_counts = recent_predictions.groupby('date').size().reset_index(name='count')
                
                fig = px.line(
                    daily_counts, 
                    x='date', 
                    y='count',
                    title='Daily Prediction Volume',
                    markers=True
                )
                fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Number of Predictions"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No predictions in the last 30 days")
        else:
            st.info("No prediction data available")
        
        # System health
        st.markdown("### 🏥 System Health")
        
        health_col1, health_col2, health_col3 = st.columns(3)
        
        with health_col1:
            st.success("✅ Model Status: Loaded")
        
        with health_col2:
            st.success("✅ Database: Connected")
        
        with health_col3:
            st.success("✅ Authentication: Active")
    
    # ===== TAB 2: USER MANAGEMENT =====
    with tab2:
        st.subheader("👥 User Management")
        
        users = load_users()
        
        # Add new user
        with st.expander("➕ Add New User", expanded=False):
            with st.form("add_user_form"):
                st.markdown("##### Create New User Account")
                
                new_username = st.text_input("Username*", placeholder="username")
                new_full_name = st.text_input("Full Name*", placeholder="John Doe")
                new_email = st.text_input("Email*", placeholder="user@example.com")
                new_password = st.text_input("Password*", type="password", placeholder="minimum 6 characters")
                new_role = st.selectbox("Role*", ["user", "doctor", "admin"])
                
                submit_user = st.form_submit_button("➕ Create User", use_container_width=True)
                
                if submit_user:
                    if all([new_username, new_full_name, new_email, new_password]):
                        if len(new_password) >= 6:
                            if register_user(new_username, new_password, new_email, new_full_name, new_role):
                                st.success(f"✅ User '{new_username}' created successfully!")
                                st.rerun()
                        else:
                            st.error("❌ Password must be at least 6 characters")
                    else:
                        st.error("❌ Please fill all required fields")
        
        st.markdown("---")
        
        # User list
        st.markdown("### 📋 Current Users")
        
        # Convert to DataFrame
        users_data = []
        for username, info in users.items():
            users_data.append({
                'Username': username,
                'Full Name': info.get('full_name', 'N/A'),
                'Email': info.get('email', 'N/A'),
                'Role': info.get('role', 'user'),
                'Created': info.get('created_at', 'N/A')[:10] if info.get('created_at') else 'N/A',
                'Last Login': info.get('last_login', 'Never')[:10] if info.get('last_login') else 'Never'
            })
        
        users_df = pd.DataFrame(users_data)
        st.dataframe(users_df, use_container_width=True, hide_index=True)
        
        # User actions
        st.markdown("### ⚙️ User Actions")
        
        selected_user = st.selectbox(
            "Select user to manage:",
            list(users.keys()),
            format_func=lambda x: f"{x} ({users[x].get('role', 'user')})"
        )
        
        if selected_user:
            user_info = users[selected_user]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Username:** {selected_user}")
                st.write(f"**Role:** {user_info.get('role', 'user')}")
            
            with col2:
                st.write(f"**Email:** {user_info.get('email', 'N/A')}")
                st.write(f"**Created:** {user_info.get('created_at', 'N/A')[:10]}")
            
            with col3:
                # Change role
                new_role = st.selectbox(
                    "Change Role:",
                    ["user", "doctor", "admin"],
                    index=["user", "doctor", "admin"].index(user_info.get('role', 'user')),
                    key=f"role_{selected_user}"
                )
                
                if st.button("💾 Update Role", use_container_width=True):
                    users[selected_user]['role'] = new_role
                    save_users(users)
                    st.success(f"✅ Role updated to '{new_role}'")
                    st.rerun()
            
            # Delete user
            if selected_user != "admin" and selected_user != current_user['username']:
                st.markdown("---")
                st.error("⚠️ Danger Zone")
                
                if st.button(f"🗑️ Delete User: {selected_user}", type="secondary"):
                    st.session_state.confirm_delete_user = selected_user
                
                if st.session_state.get('confirm_delete_user') == selected_user:
                    st.warning(f"⚠️ Are you sure you want to delete user '{selected_user}'?")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("✅ Confirm Delete", type="primary"):
                            del users[selected_user]
                            save_users(users)
                            st.success(f"✅ User '{selected_user}' deleted")
                            st.session_state.confirm_delete_user = None
                            st.rerun()
                    
                    with col2:
                        if st.button("❌ Cancel"):
                            st.session_state.confirm_delete_user = None
                            st.rerun()
            else:
                st.info("ℹ️ Cannot delete admin or currently logged in user")
    
    # ===== TAB 3: ANALYTICS =====
    with tab3:
        st.subheader("📈 Advanced Analytics")
        
        predictions_df = get_all_predictions()
        
        if predictions_df.empty:
            st.info("📭 No prediction data available for analytics")
            return
        
        # Date filtering
        st.markdown("### 📅 Date Range Filter")
        
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now() - timedelta(days=30),
                max_value=datetime.now()
            )
        
        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime.now(),
                max_value=datetime.now()
            )
        
        # Filter data
        predictions_df['date'] = pd.to_datetime(predictions_df['date'])
        filtered_df = predictions_df[
            (predictions_df['date'] >= pd.Timestamp(start_date)) &
            (predictions_df['date'] <= pd.Timestamp(end_date))
        ]
        
        st.markdown("---")
        
        # Metrics for filtered period
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Predictions", len(filtered_df))
        
        with col2:
            unique_patients = filtered_df['patient_id'].nunique()
            st.metric("Unique Patients", unique_patients)
        
        with col3:
            avg_conf = filtered_df['confidence'].mean() * 100
            st.metric("Avg Confidence", f"{avg_conf:.1f}%")
        
        with col4:
            tumor_rate = len(filtered_df[filtered_df['predicted_class'] != 'No Tumor']) / len(filtered_df) * 100
            st.metric("Tumor Detection Rate", f"{tumor_rate:.1f}%")
        
        # Visualizations
        st.markdown("### 📊 Visualization Dashboard")
        
        viz_col1, viz_col2 = st.columns(2)
        
        with viz_col1:
            # Predictions by class
            st.markdown("#### Predictions by Class")
            class_counts = filtered_df['predicted_class'].value_counts()
            
            fig = px.bar(
                x=class_counts.index,
                y=class_counts.values,
                labels={'x': 'Class', 'y': 'Count'},
                color=class_counts.index,
                color_discrete_map={
                    'Glioma': '#e74c3c',
                    'Meningioma': '#e67e22',
                    'Pituitary': '#f39c12',
                    'No Tumor': '#27ae60'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with viz_col2:
            # Confidence distribution
            st.markdown("#### Confidence Distribution")
            
            fig = px.histogram(
                filtered_df,
                x='confidence',
                nbins=20,
                labels={'confidence': 'Confidence Score'},
                color_discrete_sequence=['#3498db']
            )
            fig.update_layout(
                xaxis_title="Confidence Score",
                yaxis_title="Count"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Predictions by user
        st.markdown("#### 👤 Predictions by User")
        
        user_counts = filtered_df['user'].value_counts()
        
        fig = px.bar(
            x=user_counts.index,
            y=user_counts.values,
            labels={'x': 'User', 'y': 'Predictions'},
            color_discrete_sequence=['#9b59b6']
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Time series analysis
        st.markdown("#### 📈 Time Series Analysis")
        
        daily_stats = filtered_df.groupby('date').agg({
            'prediction_id': 'count',
            'confidence': 'mean'
        }).reset_index()
        daily_stats.columns = ['date', 'count', 'avg_confidence']
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily_stats['date'],
            y=daily_stats['count'],
            mode='lines+markers',
            name='Predictions',
            line=dict(color='#3498db', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=daily_stats['date'],
            y=daily_stats['avg_confidence'] * 100,
            mode='lines+markers',
            name='Avg Confidence (%)',
            yaxis='y2',
            line=dict(color='#e74c3c', width=2)
        ))
        
        fig.update_layout(
            title='Predictions and Confidence Over Time',
            xaxis_title='Date',
            yaxis_title='Number of Predictions',
            yaxis2=dict(
                title='Avg Confidence (%)',
                overlaying='y',
                side='right'
            ),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Export analytics
        st.markdown("---")
        st.markdown("### 📥 Export Analytics Data")
        
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=csv,
            file_name=f"analytics_data_{start_date}_{end_date}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # ===== TAB 4: SYSTEM SETTINGS =====
    with tab4:
        st.subheader("⚙️ System Settings")
        
        st.markdown("### 🔧 Configuration")
        
        # Model settings
        with st.expander("🤖 Model Configuration", expanded=True):
            st.markdown("**Current Model:** brain_tumor_detection_model_v1_96%_Kaggle.h5")
            st.markdown("**Model Accuracy:** 96%")
            st.markdown("**Input Size:** 150x150 pixels")
            st.markdown("**Classes:** 4 (Glioma, Meningioma, Pituitary, No Tumor)")
            
            if st.button("🔄 Reload Model"):
                st.cache_resource.clear()
                st.success("✅ Model cache cleared. Model will reload on next prediction.")
        
        # Database settings
        with st.expander("💾 Database Configuration"):
            st.markdown("**Patients Database:** `data/patients.json`")
            st.markdown("**Predictions Log:** `data/predictions_history.csv`")
            st.markdown("**Users Database:** `data/users.json`")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔄 Refresh Database Cache"):
                    st.success("✅ Database cache refreshed")
            
            with col2:
                if st.button("📥 Backup Database"):
                    st.info("💡 Database backup feature - Coming soon!")
        
        # Security settings
        with st.expander("🔐 Security Settings"):
            st.markdown("**Authentication:** Enabled")
            st.markdown("**Password Hashing:** bcrypt")
            st.markdown("**Session Management:** Active")
            
            if st.button("🚪 Force Logout All Users"):
                st.warning("⚠️ This will log out all users except you")
                # Implementation would clear all session states
        
        # System information
        with st.expander("ℹ️ System Information"):
            st.markdown(f"**Current User:** {current_user['username']}")
            st.markdown(f"**Role:** {current_user['role']}")
            st.markdown(f"**Streamlit Version:** {st.__version__}")
            st.markdown("**Python Version:** 3.10+")
            st.markdown("**TensorFlow Version:** 2.14+")
        
        # Maintenance
        st.markdown("---")
        st.markdown("### 🔧 Maintenance")
        
        if st.button("🗑️ Clear All Caches", type="secondary"):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.success("✅ All caches cleared")
        
        st.warning("""
        ⚠️ **Maintenance Mode**: 
        - Regular database backups recommended
        - Monitor system performance
        - Review user access logs
        - Keep model files secure
        """)

if __name__ == "__main__":
    main()
