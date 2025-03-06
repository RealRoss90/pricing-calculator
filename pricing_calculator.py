import streamlit as st
import pandas as pd
import os
from PIL import Image

def calculate_final_price(original_piece_min, original_piece_max, labour_cost, profit, gst_rate=0.1):
    """
    Calculate the final price of a job including GST based on the original piece cost, labour, and fixed profit.
    """
    net_price_min = original_piece_min + labour_cost + profit
    net_price_max = original_piece_max + labour_cost + profit
    
    # Apply GST
    final_price_min = net_price_min * (1 + gst_rate)
    final_price_max = net_price_max * (1 + gst_rate)
    
    return {
        "Final Job Price (Incl. GST)": f"${final_price_min:.2f} - ${final_price_max:.2f}" if original_piece_min != original_piece_max else f"${final_price_min:.2f}",
        "Net Price (Excl. GST)": f"${net_price_min:.2f} - ${net_price_max:.2f}" if original_piece_min != original_piece_max else f"${net_price_min:.2f}",
        "GST Amount (10%)": f"${(final_price_min - net_price_min):.2f} - ${(final_price_max - net_price_max):.2f}" if original_piece_min != original_piece_max else f"${(final_price_min - net_price_min):.2f}"
    }

# Streamlit App for Interactive Pricing Calculation
st.set_page_config(page_title="Pricing Calculator", page_icon="🌱", layout="centered")

# Define Logo Path
logo_path = "uploaded_logo.png"

# Display the saved logo
if os.path.exists(logo_path):
    st.image(logo_path, width=250)
elif os.path.exists("Farmacy logo.png"):
    st.image("Farmacy logo.png", width=250)
else:
    st.warning("No logo found. Upload a logo in the sidebar.")
    with st.sidebar:
        st.subheader("Upload Farmacy Logo")
        logo_file = st.file_uploader("Upload a PNG file", type=["png"])
        if logo_file is not None:
            with open(logo_path, "wb") as f:
                f.write(logo_file.getbuffer())
            st.success("Logo uploaded successfully! It will be saved for future use.")
            st.experimental_rerun()

st.markdown("""
    <h1 style='text-align: center; color: #8B5A2B;'>Pricing Calculator</h1>
    <p style='text-align: center; font-size: 18px; color: #5C4033;'>Calculate your final job price based on costs and fixed profit.</p>
    <hr>
""", unsafe_allow_html=True)

# Sidebar for adjustable assumptions
st.sidebar.header("Adjustable Inputs")
original_piece_min, original_piece_max = st.sidebar.slider("Price of Original Piece ($)", min_value=20.0, max_value=500.0, value=(100.0, 200.0), step=10.0)
labour_hours = st.sidebar.number_input("Labour Hours (Including Sourcing)", min_value=0.0, value=3.0, step=0.5)
labour_cost = labour_hours * 80  # Fixed hourly rate at $50
profit = 500  # Fixed profit per job
gst_rate = st.sidebar.slider("GST Rate", min_value=0.0, max_value=0.2, value=0.1, step=0.01)

# Calculate Final Price
price_quote = calculate_final_price(original_piece_min, original_piece_max, labour_cost, profit, gst_rate)

# Display Results
st.subheader("Job Price Calculation")
st.write("### Estimated Final Price & Breakdown")
for key, value in price_quote.items():
    st.markdown(f"**{key}:** {value}")
