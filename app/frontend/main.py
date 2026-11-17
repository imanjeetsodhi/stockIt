"""Stackit Streamlit Frontend Main Entrypoint."""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from app.frontend.components.sidebar import render_sidebar

# Configure global page properties
st.set_page_config(
    page_title="Stackit — Portfolio Optimization",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load global CSS theme
css_path = Path(__file__).parent / "styles" / "theme.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Register pages with clean titles and icons
pages_dir = Path(__file__).parent / "pages"
page_home = st.Page(pages_dir / "01_Home.py", title="Home", icon="🏠", default=True)
page_explorer = st.Page(pages_dir / "02_Dataset_Explorer.py", title="Dataset Explorer", icon="🔍")
page_builder = st.Page(pages_dir / "03_Portfolio_Builder.py", title="Portfolio Builder", icon="⚙️")
page_results = st.Page(pages_dir / "04_Portfolio_Results.py", title="Portfolio Results", icon="📊")
page_compare = st.Page(pages_dir / "05_Strategy_Comparison.py", title="Strategy Comparison", icon="⚖️")
# page_methodology = st.Page(pages_dir / "06_Methodology.py", title="Methodology", icon="📚")

st.session_state["PAGES"] = {
    "home": page_home,
    "explorer": page_explorer,
    "builder": page_builder,
    "results": page_results,
    "compare": page_compare,
    # "methodology": page_methodology
}

pg = st.navigation([
    page_home,
    page_explorer,
    page_builder,
    page_results,
    page_compare,
    # page_methodology
])

render_sidebar()
pg.run()
