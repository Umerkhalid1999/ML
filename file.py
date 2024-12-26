import streamlit as st
import pandas as pd
from datetime import datetime

# Hardcoded Data
patients = [
    {"PatientID": 1, "Patient_Name": "Alice Johnson", "Gender": "Female", "DateOfBirth": "1985-02-15", "Address": "123 Main St, Cityville", "ContactInformation": "555-1234", "InsuranceInformation": "HealthIns A", "MedicalHistory": "Allergic to penicillin"},
    {"PatientID": 2, "Patient_Name": "Bob Smith", "Gender": "Male", "DateOfBirth": "1990-05-23", "Address": "456 Elm St, Townsville", "ContactInformation": "555-5678", "InsuranceInformation": "HealthIns B", "MedicalHistory": "No known allergies"},
    {"PatientID": 3, "Patient_Name": "Catherine Lee", "Gender": "Female", "DateOfBirth": "1978-11-30", "Address": "789 Oak St, Villageburg", "ContactInformation": "555-9012", "InsuranceInformation": "HealthIns C", "MedicalHistory": "Asthma"}
]

physicians = [
    {"PhysicianID": 1, "Physician_Name": "Dr. Sarah Thompson", "Specialization": "Cardiology", "ContactInformation": "555-1111", "WorkSchedule": "Mon-Fri 9am-5pm"},
    {"PhysicianID": 2, "Physician_Name": "Dr. Michael Green", "Specialization": "Pediatrics", "ContactInformation": "555-2222", "WorkSchedule": "Mon-Fri 10am-4pm"}
]

appointments = [
    {"AppointmentID": 1, "PatientID": 1, "PhysicianID": 1, "AppointmentDateTime": "2024-11-01 10:00:00", "Purpose": "Routine check-up", "Status": "Scheduled"},
    {"AppointmentID": 2, "PatientID": 2, "PhysicianID": 2, "AppointmentDateTime": "2024-11-01 11:00:00", "Purpose": "Pediatric consultation", "Status": "Scheduled"}
]

medical_records = [
    {"RecordID": 1, "PatientID": 1, "PhysicianID": 1, "EncounterDate": "2024-11-01", "Diagnosis": "Hypertension", "Treatment": "Lifestyle changes, Medication", "FollowUpCare": "Follow-up in 6 months"}
]

# Convert lists to DataFrames
patients_df = pd.DataFrame(patients)
physicians_df = pd.DataFrame(physicians)
appointments_df = pd.DataFrame(appointments)
medical_records_df = pd.DataFrame(medical_records)

# Streamlit App
def main():
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
        st.dataframe(patients_df)

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
                new_id = patients_df["PatientID"].max() + 1 if not patients_df.empty else 1
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
                global patients
                patients.append(new_patient)
                st.success(f"Patient {patient_name} added successfully!")

    # Physicians Section
    elif menu == "Physicians":
        st.header("Physician Management")

        # Display Physicians
        st.subheader("Physician List")
        st.dataframe(physicians_df)

        # Add Physician
        st.subheader("Add Physician")
        with st.form("Add Physician"):
            physician_name = st.text_input("Name")
            specialization = st.text_input("Specialization")
            contact = st.text_input("Contact Information")
            schedule = st.text_input("Work Schedule")
            submit_physician = st.form_submit_button("Add Physician")
            if submit_physician:
                new_id = physicians_df["PhysicianID"].max() + 1 if not physicians_df.empty else 1
                new_physician = {
                    "PhysicianID": new_id,
                    "Physician_Name": physician_name,
                    "Specialization": specialization,
                    "ContactInformation": contact,
                    "WorkSchedule": schedule
                }
                global physicians
                physicians.append(new_physician)
                st.success(f"Physician {physician_name} added successfully!")

    # Appointments Section
    elif menu == "Appointments":
        st.header("Appointment Management")

        # Display Appointments
        st.subheader("Appointment List")
        st.dataframe(appointments_df)

        # Schedule Appointment
        st.subheader("Schedule Appointment")
        with st.form("Schedule Appointment"):
            patient_id = st.number_input("Patient ID", step=1)
            physician_id = st.number_input("Physician ID", step=1)
            appointment_date = st.date_input("Appointment Date")
            appointment_time = st.time_input("Appointment Time")
            purpose = st.text_input("Purpose")
            status = st.selectbox("Status", ["Scheduled", "Completed", "Cancelled"])
            submit_appointment = st.form_submit_button("Schedule Appointment")
            if submit_appointment:
                new_id = appointments_df["AppointmentID"].max() + 1 if not appointments_df.empty else 1
                new_appointment = {
                    "AppointmentID": new_id,
                    "PatientID": patient_id,
                    "PhysicianID": physician_id,
                    "AppointmentDateTime": f"{appointment_date} {appointment_time}",
                    "Purpose": purpose,
                    "Status": status
                }
                global appointments
                appointments.append(new_appointment)
                st.success("Appointment scheduled successfully!")

if __name__ == "__main__":
    main()
