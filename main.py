import streamlit as st
import requests
from PIL import Image
import numpy as np
import tensorflow as tf

# Load your pre-trained model
@st.cache_resource
def load_custom_model():
    # Replace 'food_classifier_model.h5' with the actual path to your model
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

# Spoonacular API settings for fetching recipes
API_KEY = "ed20cd1e0a5e4e83831f587399444f6c"
API_URL = "https://api.spoonacular.com/recipes/complexSearch"
RECIPE_DETAIL_URL = "https://api.spoonacular.com/recipes/{}/information"

# Function to fetch recipes
def fetch_recipes(food_item):
    params = {
        "query": food_item,
        "number": 1,  # Number of recipes to fetch
        "apiKey": API_KEY
    }

    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()  # Will raise an exception for 4xx/5xx status codes

        # Check if response is valid JSON
        try:
            data = response.json()
        except ValueError:
            st.error("Error: The API response is not in valid JSON format.")
            return []

        # Check if recipes are found
        if "results" in data and len(data["results"]) > 0:
            recipes = []
            for recipe in data["results"]:
                recipe_id = recipe['id']
                recipe_detail_response = requests.get(RECIPE_DETAIL_URL.format(recipe_id), params={"apiKey": API_KEY})
                recipe_detail = recipe_detail_response.json()

                ingredients = [ingredient['name'] for ingredient in recipe_detail.get('extendedIngredients', [])]
                instructions = recipe_detail.get('instructions', "Instructions not available")

                recipes.append({
                    "recipe_name": recipe.get("title", "N/A"),
                    "ingredients": ingredients,
                    "instructions": instructions
                })
            return recipes
        else:
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from Spoonacular API: {e}")
        return []

# Streamlit App
st.title("AI-Powered Recipe Finder")

# Upload an image
uploaded_file = st.file_uploader("Upload a food image", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    # Show the uploaded image
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

    # Predict food item from the uploaded image
    st.write("Classifying...")
    food_item, confidence = classify_image(uploaded_file)
    st.write(f"Identified Food Item: {food_item} (Confidence: {confidence:.2f})")

    # Fetch and display recipes based on the predicted food item
    st.write("Fetching Recipes...")
    recipes = fetch_recipes(food_item)
    if recipes:
        st.write("Suggested Recipes:")
        for recipe in recipes:
            st.write(f"**{recipe['recipe_name']}**")
            st.write(f"Ingredients: {', '.join(recipe['ingredients'])}")
            st.write(f"Instructions: {recipe['instructions']}")
    else:
        st.write("No recipes found for this food item.")
