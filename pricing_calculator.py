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
    return [{row[0]: json.loads(row[1])} for row in c.fetchall()]

# ... (keep the quote_job function as is)

# Streamlit App for Interactive Quoting
st.title("Job Pricing Calculator")

st.write("Enter either a job price or the estimated labour hours, and the calculator will provide a full cost breakdown.")

saved_jobs = load_jobs()
job_names = ["New Job"] + [list(job.keys())[0] for job in saved_jobs]
selected_job = st.selectbox("Select an existing job or create a new one:", options=job_names)

if selected_job == "New Job":
    job_name = st.text_input("Enter New Job Name:")
    job_price = st.number_input("Enter Job Price (Incl. GST) ($):", min_value=0.0, step=50.0, format="%.2f")
    labour_hours = st.number_input("Enter Labour Hours (excluding sourcing):", min_value=0.0, step=0.5, format="%.1f")

    if st.button("Calculate"):
        if job_name and (job_price > 0 or labour_hours > 0):
            result = quote_job(job_name, job_price if job_price > 0 else None, labour_hours if labour_hours > 0 else None)
            st.write("**Job Details:**")
            for key, value in result.items():
                st.write(f"**{key}:** {value}")
            
            if st.button("Save Job"):
                save_job(result)
                st.success("Job saved successfully!")
        else:
            st.error("Please enter a job name and either a price or labour hours.")

else:
    job_details = next(job[selected_job] for job in saved_jobs if selected_job in job)
    st.write("**Loaded Job Details:**")
    for key, value in job_details.items():
        st.write(f"**{key}:** {value}")

    if st.button("Delete Job"):
        c.execute("DELETE FROM jobs WHERE name = ?", (selected_job,))
        conn.commit()
        st.success("Job deleted successfully!")
        st.experimental_rerun()

# Close the database connection when the app is done
conn.close()
