import streamlit as st
import pandas as pd
import os
from PIL import Image

def quote_job(job_price=None, labour_hours=None, cogs_percentage=0.15, labour_rate_per_hour=35, sourcing_hours=2, gst_rate=0.1):
    """
    Calculate job profitability based on job price, labour hours, COGS, labour costs, and GST.
    Allows estimating either job price or required labour hours.
    """
    if job_price is not None:
        # Extract GST from job price (assuming job price includes GST)
        gst_amount = job_price * (gst_rate / (1 + gst_rate))
        net_price = job_price - gst_amount  # Excluding GST
        
        # Calculate costs
        cogs_cost = net_price * cogs_percentage
        labour_cost = net_price * 0.2  # Labour is assumed to be 20% of net price
        total_cost = cogs_cost + labour_cost
        
        # Calculate profit
        profit = net_price - total_cost
        
        # Calculate recommended labour hours (excluding sourcing time)
        labour_hours = (labour_cost / labour_rate_per_hour) - sourcing_hours
    
    elif labour_hours is not None:
        # Estimate job price based on labour hours
        labour_cost = (labour_hours + sourcing_hours) * labour_rate_per_hour
        net_price = labour_cost / 0.2  # Since labour is 20% of net price
        job_price = net_price * (1 + gst_rate)  # Convert back to GST-inclusive price
        
        # Extract GST from job price
        gst_amount = job_price * (gst_rate / (1 + gst_rate))
        
        # Calculate COGS and total cost
        cogs_cost = net_price * cogs_percentage
        total_cost = cogs_cost + labour_cost
        
        # Calculate profit
        profit = net_price - total_cost
    
    else:
        raise ValueError("Either job_price or labour_hours must be provided.")
    
    # Return results
    return {
        "Job Price (Incl. GST)": f"${job_price:.2f}",
        "Net Price (Excl. GST)": f"${net_price:.2f}",
        "GST Amount (10%)": f"${gst_amount:.2f}",
        "COGS Cost": f"${cogs_cost:.2f}",
        "Labour Cost": f"${labour_cost:.2f}",
        "Total Cost": f"${total_cost:.2f}",
        "Profit per Job": f"${profit:.2f}",
        "Recommended Labour Hours (Excluding Sourcing)": f"{round(labour_hours, 2)} hours" if job_price is not None else f"{labour_hours} hours",
    }

# Streamlit App for Interactive Quoting with Adjustable Assumptions
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
    <p style='text-align: center; font-size: 18px; color: #5C4033;'>Easily estimate job costs and profitability.</p>
    <hr>
""", unsafe_allow_html=True)

# Sidebar for adjustable assumptions
st.sidebar.header("Adjustable Assumptions")
cogs_percentage = st.sidebar.slider("COGS Percentage", min_value=0.0, max_value=1.0, value=0.15, step=0.01)
labour_rate_per_hour = st.sidebar.number_input("Labour Rate ($/hr)", min_value=10.0, value=35.0, step=1.0)
sourcing_hours = st.sidebar.number_input("Sourcing Time (hrs)", min_value=0.0, value=2.0, step=0.5)
gst_rate = st.sidebar.slider("GST Rate", min_value=0.0, max_value=0.2, value=0.1, step=0.01)

if "saved_jobs" not in st.session_state:
    st.session_state.saved_jobs = []
if "selected_saved_job" not in st.session_state:
    st.session_state.selected_saved_job = None

# New Job Entry Section
st.subheader("Create a New Job")
job_name = st.text_input("Enter New Job Name:")
job_price = st.number_input("Enter Job Price (Incl. GST) ($):", min_value=0.0, step=50.0, format="%.2f")
labour_hours = st.number_input("Enter Labour Hours (excluding sourcing):", min_value=0.0, step=0.5, format="%.1f")

quote = None  # Ensure quote exists before saving

if st.button("Calculate New Job", help="Click to calculate job costs and profit"):
    if job_price > 0:
        quote = quote_job(job_price=job_price, cogs_percentage=cogs_percentage, labour_rate_per_hour=labour_rate_per_hour, sourcing_hours=sourcing_hours, gst_rate=gst_rate)
    elif labour_hours > 0:
        quote = quote_job(labour_hours=labour_hours, cogs_percentage=cogs_percentage, labour_rate_per_hour=labour_rate_per_hour, sourcing_hours=sourcing_hours, gst_rate=gst_rate)
    else:
        st.error("Please enter either a job price or labour hours.")
        quote = None
    
    if quote:
        st.subheader("Job Quote Breakdown")
        st.write("### Estimated Costs & Profit")
        for key, value in quote.items():
            st.markdown(f"**{key}:** {value}")
