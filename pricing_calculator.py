import streamlit as st
import pandas as pd

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
        "Job Name": job_name,
        "Job Price (Incl. GST)": f"${job_price:.2f}",
        "Net Price (Excl. GST)": f"${net_price:.2f}",
        "GST Amount (10%)": f"${gst_amount:.2f}",
        "COGS Cost (15%)": f"${cogs_cost:.2f}",
        "Labour Cost (20%)": f"${labour_cost:.2f}",
        "Total Cost": f"${total_cost:.2f}",
        "Profit per Job": f"${profit:.2f}",
        "Recommended Labour Hours (Excluding Sourcing)": f"{round(labour_hours, 2)} hours" if job_price is not None else f"{labour_hours} hours",
    }

# Streamlit App for Interactive Quoting
st.title("Job Pricing Calculator")

st.write("Enter either a job price or the estimated labour hours, and the calculator will provide a full cost breakdown.")

if "saved_jobs" not in st.session_state:
    st.session_state.saved_jobs = []

# Load saved job names
job_names = [job["Job Name"] for job in st.session_state.saved_jobs]
selected_job = st.selectbox("Select an existing job or create a new one:", options=["New Job"] + job_names, key="job_select")

if selected_job == "New Job":
    job_name = st.text_input("Enter New Job Name:")
    job_price = st.number_input("Enter Job Price (Incl. GST) ($):", min_value=0.0, step=50.0, format="%.2f")
    labour_hours = st.number_input("Enter Labour Hours (excluding sourcing):", min_value=0.0, step=0.5, format="%.1f")
else:
    job_details = next((job for job in st.session_state.saved_jobs if job["Job Name"] == selected_job), None)
    if job_details:
        job_name = job_details["Job Name"]
        job_price = float(job_details["Job Price (Incl. GST)"].replace("$", ""))
        labour_hours = float(job_details["Recommended Labour Hours (Excluding Sourcing)"].replace(" hours", ""))
        st.write("**Loaded Job Details:**")
        for key, value in job_details.items():
            st.write(f"**{key}:** {value}")

if st.button("Calculate"):
    if job_price > 0:
        quote = quote_job(job_price=job_price)
    elif labour_hours > 0:
        quote = quote_job(labour_hours=labour_hours)
    else:
        st.error("Please enter either a job price or labour hours.")
        quote = None
    
    if quote:
        for key, value in quote.items():
            st.write(f"**{key}:** {value}")
        
        if job_name and selected_job == "New Job":
            if st.button("Save Quote", key="save_button"):
                st.session_state.saved_jobs.append({"Job Name": job_name, **quote})
                st.session_state["job_select"] = job_name  # Update dropdown selection
                st.success(f"Saved: {job_name}")
                st.experimental_rerun()

# Ensure saved jobs update after saving
if st.session_state.saved_jobs:
    st.subheader("Saved Quotes")
    df = pd.DataFrame(st.session_state.saved_jobs)
    st.dataframe(df)
