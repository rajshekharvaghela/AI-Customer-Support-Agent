import streamlit as st
import requests
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="AI Refund Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 18px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Configuration
st.sidebar.title("⚙️ Configuration")
api_url = st.sidebar.text_input("API URL", value="http://localhost:8000")
st.sidebar.markdown("---")

# Initialize session state
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "current_order_id" not in st.session_state:
    st.session_state.current_order_id = None

# Main layout with tabs
tab1, tab2, tab3 = st.tabs(["💬 Customer Chat", "📊 Admin Dashboard", "📋 Policy Viewer"])

with tab1:
    st.header("Customer Refund Request")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Submit Your Refund Request")
        
        customer_id = st.text_input("Customer ID", placeholder="e.g., CUST_001")
        order_id = st.text_input("Order ID", placeholder="e.g., ORD_12345")
        
        refund_reason = st.selectbox(
            "Reason for Refund",
            ["Item not as described", "Changed mind", "Item damaged", "Wrong item received", "Other"]
        )
        
        additional_details = st.text_area("Additional Details")
        
        if st.button("Submit Refund Request", use_container_width=True):
            if customer_id and order_id:
                # Send to backend
                message = f"Refund Request - Order: {order_id}, Reason: {refund_reason}. {additional_details}"
                
                try:
                    response = requests.post(
                        f"{api_url}/api/chat",
                        json={"user_message": message, "customer_id": customer_id, "order_id": order_id},
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.conversation_history.append({
                            "role": "user",
                            "content": message,
                            "timestamp": datetime.now().isoformat()
                        })
                        st.session_state.conversation_history.append({
                            "role": "assistant",
                            "content": result.get("response"),
                            "decision": result.get("decision"),
                            "timestamp": datetime.now().isoformat()
                        })
                        st.session_state.current_order_id = order_id
                        st.rerun()
                    else:
                        st.error(f"API Error: {response.status_code}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")
            else:
                st.warning("Please provide Customer ID and Order ID")
    
    with col2:
        st.subheader("Quick Info")
        st.info("The AI Agent will:\n1. Query your order\n2. Check refund policy\n3. Make decision\n4. Log reasoning")

with tab2:
    st.header("Admin Dashboard - Agent Reasoning")
    
    if st.session_state.current_order_id:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.metric("Last Order Processed", st.session_state.current_order_id)
        
        try:
            response = requests.get(
                f"{api_url}/api/reasoning/{st.session_state.current_order_id}",
                timeout=5
            )
            if response.status_code == 200:
                logs = response.json().get("logs", [])
                st.subheader("Reasoning Logs")
                for log in logs:
                    with st.expander(f"Step: {log.get('step', 'Unknown')}"):
                        st.write(log.get("reasoning", ""))
        except Exception as e:
            st.error(f"Failed to fetch logs: {e}")
    else:
        st.info("Process a refund request first to see reasoning logs")

with tab3:
    st.header("Refund Policy Document")
    
    try:
        with open("../backend/policy/refund_policy.txt", "r") as f:
            policy_content = f.read()
        st.markdown(policy_content)
    except FileNotFoundError:
        st.warning("Policy document not found")

# Footer
st.markdown("---")
st.markdown("🔧 Built with Streamlit + FastAPI + LangGraph | Worknoon AI Challenge")