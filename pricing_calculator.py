import streamlit as st
import pandas as pd
import sqlite3
import json

# Database setup
conn = sqlite3.connect('jobs.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS jobs
             (name TEXT PRIMARY KEY, details TEXT)''')
conn.commit()

def save_job(job_details):
    job_name = job_details['Job Name']
    job_details_json = json.dumps(job_details)
    c.execute("INSERT OR REPLACE INTO jobs (name, details) VALUES (?, ?)",
              (job_name, job_details_json))
    conn.commit()

def load_jobs():
    c.execute("SELECT * FROM jobs")
    return {row[0]: json.loads(row[1]) for row in c.fetchall()}

def quote_job(job_name, job_price=None, labour_hours=None, cogs_percentage=0.15, labour_rate_per_hour=35, sourcing_hours=2, gst_rate=0.1):
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

saved_jobs = load_jobs()
job_names = ["New Job"] + list(saved_jobs.keys())
selected_job = st
