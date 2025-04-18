import streamlit as st
import joblib
import numpy as np

# Load trained model
model = joblib.load("gradient_boosting_optimized.pkl")

# Page settings
st.set_page_config(page_title="Diabetes Predictor", layout="centered")
st.title("🩺 Diabetes Prediction App")
st.markdown("Provide the following medical details to predict diabetes risk:")

# Create input columns
col1, col2 = st.columns(2)

with col1:
    pregnancies = st.number_input("Pregnancies", 0, 20, 1)
    glucose = st.number_input("Glucose Level", 0, 200, 120)
    blood_pressure = st.number_input("Blood Pressure (mm Hg)", 0, 150, 70)
    skin_thickness = st.number_input("Skin Thickness (mm)", 0, 100, 20)
    insulin = st.number_input("Insulin Level", 0, 900, 80)

with col2:
    bmi = st.number_input("BMI", 0.0, 70.0, 25.0)
    dpf = st.number_input("Diabetes Pedigree Function", 0.0, 3.0, 0.5)
    age = st.number_input("Age", 1, 120, 33)
    diabetes_risk_index = st.number_input("Diabetes Risk Index", 0.0, 100.0, 50.0)
    insulin_sensitivity = st.number_input("Insulin Sensitivity", 0.0, 1.0, 0.5)
    age_bmi_factor = st.number_input("Age-BMI Factor", 0.0, 5000.0, 825.0)

# Prediction
if st.button("🔍 Predict Diabetes"):
    features = np.array([[pregnancies, glucose, blood_pressure, skin_thickness, insulin,
                          bmi, dpf, age, diabetes_risk_index, insulin_sensitivity, age_bmi_factor]])
    
    prediction = model.predict(features)[0]

    if prediction == 1:
        st.error("⚠️ The person is likely to have **diabetes.**")
    else:
        st.success("✅ The person is **unlikely to have diabetes.**")