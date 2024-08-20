import streamlit as st
import base64
import pandas as pd


# Function to add a background image
def add_bg_from_local(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/jpeg;base64,{encoded_string.decode()});
            background-size: cover;
            background-position: center;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


# Adding the background image
add_bg_from_local('/Users/macvision/PycharmProjects/Quiz.py/istockphoto-879557418-612x612.jpg')


# Function to calculate BMR
def calculate_bmr(weight, height, age, gender):
    if gender == 'Male':
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    return bmr


# Function to calculate TDEE
def calculate_tdee(bmr, activity_level):
    activity_multipliers = {
        'Sedentary': 1.2,
        'Lightly Active': 1.375,
        'Moderately Active': 1.55,
        'Very Active': 1.725,
        'Super Active': 1.9
    }
    return bmr * activity_multipliers[activity_level]


# Function to adjust TDEE based on fitness goals
def adjust_tdee_for_goal(tdee, goal):
    adjustment = 0
    if goal == 'Fat Loss':
        adjustment = -20  # Example adjustment percentage for fat loss
    elif goal == 'Muscle Gain':
        adjustment = 20  # Example adjustment percentage for muscle gain
    return tdee + (tdee * adjustment / 100.0)


# Function to calculate macros
def calculate_macros(weight, calories, protein_per_kg, fat_percentage):
    protein = weight * protein_per_kg
    protein_calories = protein * 4

    fat_calories = calories * fat_percentage / 100.0
    fat_intake = fat_calories / 9

    carb_calories = calories - (protein_calories + fat_calories)
    carb_intake = carb_calories / 4

    return protein, fat_intake, carb_intake


# Function to calculate BMI
def calculate_bmi(weight, height):
    height_in_m = height * 0.01  # converting height to meters
    bmi = weight / (height_in_m ** 2)
    return bmi


# Function to calculate body fat percentage
def calculate_body_fat(bmi, gender, age):
    if gender == 'Male':
        body_fat = (1.20 * bmi) + (0.23 * age) - 16.2
    else:
        body_fat = (1.20 * bmi) + (0.23 * age) - 5.4
    return body_fat


# Streamlit app title
st.title("Your Nutritionist Coach")

# Input Section
st.header("Enter Your Details")
gender = st.selectbox("Gender", ["Male", "Female"])
weight = st.number_input("Weight (kg)", min_value=1.0, value=70.0)
height = st.number_input("Height (cm)", min_value=1.0, value=170.0)
age = st.number_input("Age (years)", min_value=1, value=25)

activity_level = st.selectbox("Activity Level",
                              ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Super Active"])

goal = st.selectbox("Fitness Goal", ["Fat Loss", "Muscle Gain", "Maintenance"])

# Tips for setting protein and fat percentage
st.sidebar.header("Tips for Setting Protein and Fat Percentage")
st.sidebar.write("**For Fat Loss:**\n"
                 "- Protein: 1.2 to 1.5 g/kg\n"
                 "- Fat: 20% to 30% of total calories")
st.sidebar.write("**For Muscle Gain:**\n"
                 "- Protein: 1.6 to 2.2 g/kg\n"
                 "- Fat: 20% to 30% of total calories")
st.sidebar.write("**For Maintenance:**\n"
                 "- Protein: 1.0 to 1.2 g/kg\n"
                 "- Fat: 20% to 30% of total calories")
st.sidebar.write("______________________________________")
height_conversions = {
    "4 feet 0 inches": 121.92,
    "4 feet 1 inch": 124.46,
    "4 feet 2 inches": 126.99,
    "4 feet 3 inches": 129.54,
    "4 feet 4 inches": 132.08,
    "4 feet 5 inches": 134.62,
    "4 feet 6 inches": 137.16,
    "4 feet 7 inches": 139.7,
    "4 feet 8 inches": 142.24,
    "4 feet 9 inches": 144.78,
    "4 feet 10 inches": 147.32,
    "4 feet 11 inches": 149.86,
    "5 feet 0 inches": 152.4,
    "5 feet 1 inch": 155.48,
    "5 feet 2 inches": 157.48,
    "5 feet 3 inches": 160.02,
    "5 feet 4 inches": 162.56,
    "5 feet 5 inches": 165.1,
    "5 feet 6 inches": 167.64,
    "5 feet 7 inches": 170.18,
    "5 feet 8 inches": 172.72,
    "5 feet 9 inches": 175.26,
    "5 feet 10 inches": 177.8,
    "5 feet 11 inches": 180.34,
    "6 feet 0 inches": 182.88,
    "6 feet 1 inch": 185.42,
    "6 feet 2 inches": 187.96,
    "6 feet 3 inches": 190.5,
    "6 feet 4 inches": 193.04,
    "6 feet 5 inches": 195.58,
}

# Extract height options
height_options = list(height_conversions.keys())

# Sidebar with height slider
selected_height = st.sidebar.selectbox("Check your Height in cm:", height_options)

# Display the corresponding height in cm
height_cm = height_conversions[selected_height]
st.sidebar.write(f"**{selected_height}** = {height_cm} cm")

st.sidebar.write("______________________________________")
# Tips for the number of meals per day based on goals
st.sidebar.header("Guideline: Meals Per Day")
st.sidebar.write("**For Fat Loss:**\n"
                 "- Aim for 3-4 meals per day.\n"
                 "- Space meals evenly to manage hunger.\n")

st.sidebar.write("**For Maintenance:**\n"
                 "- 3-5 meals per day is recommended.\n"
                 "- Focus on balanced meals.\n")

st.sidebar.write("**For Muscle Gain:**\n"
                 "- Aim for 4-6 meals per day.\n"
                 "- Ensure protein is included in each meal.\n")

# Protein and Fat Inputs with Tips
protein_per_kg = st.number_input("Protein per kg of Body Weight", min_value=1.0, max_value=2.5, value=1.5, step=0.1)
fat_percentage = st.number_input("Fat Percentage of Total Calories", min_value=20, max_value=30, value=25, step=1)

# Meals per day input
meals_per_day = st.number_input("How many meals per day?", min_value=1, value=3)

# Calculate and display results only after user clicks "Calculate"
if st.button("Calculate"):
    # BMR and TDEE Calculation
    bmr = calculate_bmr(weight, height, age, gender)
    tdee = calculate_tdee(bmr, activity_level)
    adjusted_tdee = adjust_tdee_for_goal(tdee, goal)

    # BMI and Body Fat Percentage Calculation
    bmi = calculate_bmi(weight, height)
    body_fat = calculate_body_fat(bmi, gender, age)

    # Macronutrient Calculation
    protein, fat_intake, carb_intake = calculate_macros(weight, adjusted_tdee, protein_per_kg, fat_percentage)

    # Displaying the results with improved layout
    st.markdown("---")
    data1 = {
        'Body-fat %': [f"{body_fat:.2f}%"],
        'BMI': [f"{bmi:.2f}"],
        'overall calories/day': [f"{tdee:.2f}"],
        'Adjusted calories/day': [f"{adjusted_tdee:.2f}"],
        'Caloric Deficit/day': [f"{tdee - adjusted_tdee:.2f}"]

    }

    st.markdown(f"### Macronutrient Breakdown for {goal}")

    # Display results in a tabular format
    data = {
        "Nutrient": ["Protein (g)", "Fat (g)", "Carbohydrates (g)"],
        "Total per Day": [f"{protein:.2f}", f"{fat_intake:.2f}", f"{carb_intake:.2f}"],
        "Per Meal": [f"{(protein / meals_per_day):.2f}", f"{(fat_intake / meals_per_day):.2f}",
                     f"{(carb_intake / meals_per_day):.2f}"]
    }
    df = pd.DataFrame(data)
    df1 = pd.DataFrame(data1)
    st.table(df1)
    st.table(df)

