import streamlit as st
import pandas as pd
import os

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
        "COGS Cost (15%)": f"${cogs_cost:.2f}",
        "Labour Cost (20%)": f"${labour_cost:.2f}",
        "Total Cost": f"${total_cost:.2f}",
        "Profit per Job": f"${profit:.2f}",
        "Recommended Labour Hours (Excluding Sourcing)": f"{round(labour_hours, 2)} hours" if job_price is not None else f"{labour_hours} hours",
    }

# Streamlit App for Interactive Quoting with Farmacy Branding
st.set_page_config(page_title="Farmacy Job Pricing Calculator", page_icon="🌱", layout="centered")

# Upload Farmacy Logo
st.sidebar.subheader("Upload Farmacy Logo")
logo_file = st.sidebar.file_uploader("Upload a PNG file", type=["png"])

if logo_file is not None:
    st.sidebar.success("Logo uploaded successfully!")
    st.image(logo_file, width=250)
elif os.path.exists("Farmacy logo.png"):
    st.image("Farmacy logo.png", width=250)
else:
    st.warning("No logo found. Upload a logo in the sidebar.")

st.markdown("""
    <h1 style='text-align: center; color: #8B5A2B;'>Farmacy Job Pricing Calculator</h1>
    <p style='text-align: center; font-size: 18px; color: #5C4033;'>Easily estimate job costs and profitability.</p>
    <hr>
""", unsafe_allow_html=True)

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
        quote = quote_job(job_price=job_price)
    elif labour_hours > 0:
        quote = quote_job(labour_hours=labour_hours)
    else:
        st.error("Please enter either a job price or labour hours.")
        quote = None
    
    if quote:
        st.subheader("Job Quote Breakdown")
        st.write("### Estimated Costs & Profit")
        for key, value in quote.items():
            st.markdown(f"**{key}:** {value}")

# Save Job
if job_name and quote:
    if st.button("Save Job", help="Click to save this job for future reference"):
        new_job = {"Job Name": job_name, **quote}
        st.session_state.saved_jobs.append(new_job)
        st.session_state.selected_saved_job = job_name  # Update selected job
        st.success(f"Saved: {job_name}")

# Display Saved Jobs Section only if there are saved jobs
if len(st.session_state.saved_jobs) > 0:
    st.subheader("📂 Saved Jobs")
    saved_job_names = [job["Job Name"] for job in st.session_state.saved_jobs]
    selected_saved_job = st.selectbox("Select a saved job to view:", ["Select a Job"] + saved_job_names, index=0, key="saved_job_dropdown")
    
    if selected_saved_job != "Select a Job":
        job_details = next((job for job in st.session_state.saved_jobs if job["Job Name"] == selected_saved_job), None)
        if job_details:
            st.subheader(f"📋 Job Details: {selected_saved_job}")
            for key, value in job_details.items():
                st.markdown(f"**{key}:** {value}")
