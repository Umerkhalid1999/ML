import streamlit as st
import requests
from PIL import Image
import numpy as np
import tensorflow as tf
import os
import base64

def add_bg_image(image_file_path):
    with open(image_file_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')  # Correct encoding and decoding
    b64_image = f"data:image/jpg;base64,{encoded_image}"
    # Include the Streamlit code to set the background (this assumes you're using Streamlit)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{b64_image}");
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# Example usage:
# Make sure to provide the correct path to the image file
add_bg_image("food - Copy.jpg")

# Load your pre-trained model
@st.cache_resource
def load_custom_model():
    model = tf.keras.models.load_model("food_recognition_subset_model.h5")
    return model

# Preprocess the uploaded image for classification
def preprocess_image(uploaded_file):
    image = Image.open(uploaded_file).convert("RGB")
    image = image.resize((224, 224))  # Resize to the input size required by your model
    image_array = np.array(image)
    image_array = image_array / 255.0  # Normalize to [0, 1] if required by your model
    return np.expand_dims(image_array, axis=0)  # Add batch dimension

# Classify the uploaded image
def classify_image(uploaded_file):
    model = load_custom_model()  # Load your pre-trained model
    image_array = preprocess_image(uploaded_file)  # Preprocess the image

    # Predict the class probabilities
    predictions = model.predict(image_array)
    confidence = np.max(predictions)  # Get the highest probability (confidence score)
    predicted_index = np.argmax(predictions, axis=1)[0]  # Get the index of the highest probability

    # Map the index to the corresponding category
    categories = [
        "baklava", "carrot_cake", "chicken_curry", "clam_chowder", "club_sandwich",
        "donuts", "falafel", "french_onion_soup", "frozen_yogurt", "greek_salad",
        "lobster_bisque", "macarons", "nachos", "onion_rings", "peking_duck",
        "pizza", "red_velvet_cake", "samosa", "spaghetti_carbonara"
    ]
    predicted_category = categories[predicted_index]
    return predicted_category, confidence

# Sidebar for categories
st.sidebar.title("Food Categories")
categories = [
    "baklava", "carrot_cake", "chicken_curry", "clam_chowder", "club_sandwich",
    "donuts", "falafel", "french_onion_soup", "frozen_yogurt", "greek_salad",
    "lobster_bisque", "macarons", "nachos", "onion_rings", "peking_duck",
    "pizza", "red_velvet_cake", "samosa", "spaghetti_carbonara"
]
st.sidebar.write("Explore the categories recognized by the model:")
for category in categories:
    st.sidebar.write(f"- {category}")

# Add the background image (update the path to your local file)

# Streamlit App
st.title("AI-Powered Recipe Finder")

# Add a disclaimer
st.markdown(
    "**Note:** This model is currently under development and is trained only 28%. The predictions may not be fully accurate."
)

# Upload an image
uploaded_file = st.file_uploader("Upload a food image", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    # Show the uploaded image
    st.image(uploaded_file, caption="Uploaded Image (from food Categories)", use_container_width=True)

    # Predict food item from the uploaded image
    st.write("Classifying.....")
    food_item, confidence = classify_image(uploaded_file)
    st.write(f"Identified Food Item: {food_item} (Confidence: {confidence:.2f})")
