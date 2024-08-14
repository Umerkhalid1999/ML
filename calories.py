import streamlit as st
import pickle
import numpy as np

# Load the trained model
with open('poly_model.pkl', 'rb') as model_file:
    poly_model = pickle.load(model_file)

# Title and description
st.title("Calorie Prediction System")
st.write("Enter the following details to predict your daily calorie needs.")

# Input fields
age = st.number_input("Age", value=35)
sex = st.selectbox("Sex", options=[0, 1], format_func=lambda x: "Female" if x == 0 else "Male")
weight = st.number_input("Weight (kg)", value=91.0)
height = st.number_input("Height (cm)", value=187.0)
body_fat_percentage = st.number_input("Body Fat Percentage (%)", value=15.0)
activity_level = st.selectbox("Activity Level", options=[0, 1, 2, 3],
                              format_func=lambda x: ["Sedentary", "Lightly active", "Moderately active", "Very active"][x])
fitness_goals = st.selectbox("Fitness Goals", options=[0, 1, 2],
                             format_func=lambda x: ["Lose weight", "Maintain weight", "Gain weight"][x])

# Input array
input_features = np.array([[age, sex, weight, height, body_fat_percentage, activity_level, fitness_goals]])

# Predict button
if st.button("Predict Calories"):
    # Make the prediction
    prediction = poly_model.predict(input_features)
    # Display the result
    st.write(f"The predicted daily calories are: {prediction[0]:.2f} kcal")

