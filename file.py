import streamlit as st
import pandas as pd
from datetime import datetime

# Global Hardcoded Data
patients = [
    {"PatientID": 1, "Patient_Name": "Alice Johnson", "Gender": "Female", "DateOfBirth": "1985-02-15", "Address": "123 Main St, Cityville", "ContactInformation": "555-1234", "InsuranceInformation": "HealthIns A", "MedicalHistory": "Allergic to penicillin"},
    {"PatientID": 2, "Patient_Name": "Bob Smith", "Gender": "Male", "DateOfBirth": "1990-05-23", "Address": "456 Elm St, Townsville", "ContactInformation": "555-5678", "InsuranceInformation": "HealthIns B", "MedicalHistory": "No known allergies"},
    {"PatientID": 3, "Patient_Name": "Catherine Lee", "Gender": "Female", "DateOfBirth": "1978-11-30", "Address": "789 Oak St, Villageburg", "ContactInformation": "555-9012", "InsuranceInformation": "HealthIns C", "MedicalHistory": "Asthma"}
]

# Streamlit App
def main():
    global patients  # Use the global patients list
    st.title("Virtual Healthcare Record Management System (VHRMS)")
    menu = st.sidebar.selectbox("Select Section", ["Home", "Patients", "Physicians", "Appointments", "Medical Records"])

    # Home Section
    if menu == "Home":
        st.header("Welcome to VHRMS")
        st.write("Navigate using the sidebar to manage records.")

    # Patients Section
    elif menu == "Patients":
        st.header("Patient Management")

        # Display Patients
        st.subheader("Patient List")
        patients_df = pd.DataFrame(patients)
        if not patients_df.empty:
            for index, row in patients_df.iterrows():
                col1, col2, col3 = st.columns([4, 1, 1])
                with col1:
                    st.write(f"**{row['Patient_Name']}**")
                    st.write(f"**Gender:** {row['Gender']}, **DOB:** {row['DateOfBirth']}")
                    st.write(f"**Address:** {row['Address']}, **Contact:** {row['ContactInformation']}")
                with col2:
                    if st.button(f"Delete #{row['PatientID']}", key=f"delete_{row['PatientID']}"):
                        patients = [p for p in patients if p["PatientID"] != row["PatientID"]]
                        st.experimental_rerun()

        else:
            st.write("No patient records found.")

        # Add Patient
        st.subheader("Add Patient")
        with st.form("Add Patient"):
            patient_name = st.text_input("Name")
            gender = st.selectbox("Gender", ["Male", "Female"])
            dob = st.date_input("Date of Birth")
            address = st.text_input("Address")
            contact = st.text_input("Contact Information")
            insurance = st.text_input("Insurance Information")
            history = st.text_area("Medical History")
            submit_patient = st.form_submit_button("Add Patient")
            if submit_patient:
                new_id = max([p["PatientID"] for p in patients]) + 1 if patients else 1
                new_patient = {
                    "PatientID": new_id,
                    "Patient_Name": patient_name,
                    "Gender": gender,
                    "DateOfBirth": dob.strftime('%Y-%m-%d'),
                    "Address": address,
                    "ContactInformation": contact,
                    "InsuranceInformation": insurance,
                    "MedicalHistory": history
                }
                patients.append(new_patient)
                st.success(f"Patient {patient_name} added successfully!")
                st.experimental_rerun()  # Refresh to show the updated list

if __name__ == "__main__":
    main()
