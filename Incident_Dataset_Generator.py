import pandas as pd
import random
import streamlit as st
from faker import Faker

fake = Faker()

# Defining sample data categories
departments = ['ICU', 'Surgery Room', 'Emergency Room', 'Pharmacy', 'Radiology', 'Pediatrics Ward', 'General Ward', 'Maternity Ward', 'Oncology']
incident_types = ['Medication Error', 'Fall', 'Infection Control', 'Equipment Failure', 'Patient Miscommunication', 'Surgical Error', 'Procedure Complication', 'Pressure Ulcer']
outcomes = ['Patient stable', 'No harm', 'Minor injury', 'Major intervention', 'Isolated cases', 'Rescheduled scan']
staff = ['Nurse', 'Surgeon', 'Technician', 'Radiologist', 'Respiratory Therapist', 'Pharmacist', 'Physical Therapist', 'Infection Control Nurse']
actions = ['Review medication protocols', 'Increase monitoring', 'Equipment maintenance review', 'Implement strict protocols', 'Staff training session', 'Reinforce chemotherapy protocols', 'Review patient care practices']
severity = ['High', 'Medium', 'Low']

# Function to generate random data
def generate_incident_data(num_records):
    incidents = []
    for _ in range(num_records):
        incident = {
            'Incident Number': fake.unique.random_number(digits=8, fix_len=True),
            'Date': fake.date_this_year(),
            'Time': fake.time(),
            'Department': random.choice(departments),
            'Incident Type': random.choice(incident_types),
            'Description': fake.sentence(),
            'Severity': random.choice(severity),
            'Outcome': random.choice(outcomes),
            'Responsible Staff': random.choice(staff),
            'Action Taken': random.choice(actions),
            'Priority': random.randint(1, 5)
        }
        incidents.append(incident)
    return incidents

# Streamlit App
def main():
    st.title("Incident Data Generator and Viewer")
    
    # Number of records to generate
    st.sidebar.header("Settings")
    num_records = st.sidebar.number_input("Number of Records to Generate", min_value=1, max_value=10000, value=5000, step=100)
    
    # Generate data
    st.sidebar.write("Click 'Generate Data' to create random incidents.")
    if st.sidebar.button("Generate Data"):
        st.write("### Generated Incident Data")
        incident_data = generate_incident_data(num_records)
        df = pd.DataFrame(incident_data)
        
        # Display data in Streamlit
        st.dataframe(df)
        
        # Download CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Incident Data as CSV",
            data=csv,
            file_name='incident_data.csv',
            mime='text/csv'
        )
        
        # Basic summary statistics
        st.write("### Summary Statistics")
        st.write("#### Severity Count")
        st.bar_chart(df['Severity'].value_counts())
        
        st.write("#### Department-wise Incidents")
        st.bar_chart(df['Department'].value_counts())

# Run the Streamlit app
if __name__ == "__main__":
    main()