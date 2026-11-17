"""Sidebar component for system status and financial parameters."""

import streamlit as st
from app.frontend.utils.api_client import api_client

def render_sidebar():
    with st.sidebar:
        st.markdown("### **STACKIT**")
        st.markdown("---")
