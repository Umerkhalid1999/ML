import streamlit as st
import base64

# Set page config
st.set_page_config(
    page_title="Umar Khalid Mirza - Portfolio",
    page_icon="🌐",
    layout="wide"
)

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
add_bg_from_local('backgrouc.jpeg')

# Custom CSS for responsiveness
st.markdown(
    """
    <style>
    /* General body styling */
    body {
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 0;
    }

    /* Responsive columns */
    @media screen and (max-width: 768px) {
        .stApp .stColumns {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
    }

    /* Button styling */
    .stButton button {
        background-color: #4CAF50;
        color: black;
        font-weight: bold;
        border: none;
        padding: 10px 20px;
        text-align: center;
        font-size: 16px;
        margin: 10px auto;
        cursor: pointer;
        border-radius: 8px;
        transition: transform 0.2s, backgroud-color 0.2s;
    }
    .stButton button:hover {
        background-color: #45a049;
        transform: scale(1.1);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Header section
st.title("Welcome to Umar Khalid Mirza's Portfolio")
st.markdown(
    """Explore my work and expertise in various fields of Artificial Intelligence. Choose a category below to learn more."""
)

# Define categories
categories = {
    "Machine Learning": "Machine Learning projects involving supervised and unsupervised learning, predictive modeling, and optimization. [View Projects](https://example.com/ml-projects)",
    "Deep Learning": "Deep Learning projects utilizing neural networks like CNNs, RNNs, and transformers for advanced AI tasks. [View Projects](https://example.com/dl-projects)",
    "Data Science": "Comprehensive data science projects including EDA, feature engineering, and model deployment. [View Projects](https://example.com/data-science-projects)",
    "Data Analysis": "Insights derived from data through statistical analysis, visualization, and business intelligence tools. [View Projects](https://example.com/data-analysis-projects)",
    "Generative-AI": "Generative AI applications, including text generation, image synthesis, and AI creativity. [View Projects](https://example.com/gen-ai-projects)",
    "AI Chat Bots": "Interactive chatbots built using NLP techniques for customer support and automation. [View Projects](https://example.com/chatbots)",
    "AI Tools": "Custom-built AI tools tailored for specific applications. Stay tuned for more details! [View Projects](https://example.com/ai-tools)",
    "Others": "Explore additional projects and innovative ideas that don't fit into the above categories. [View Projects](https://example.com/others)"
}

# Layout for category buttons
cols = st.columns(3 if st.sidebar.button('Web') else 1)

# Generate buttons for each category
for i, (category, description) in enumerate(categories.items()):
    with cols[i % len(cols)]:
        if st.button(category):
            st.subheader(f"{category} Projects")
            st.write(description)

# Footer
st.markdown("---")
st.write("Thank you for visiting my portfolio. Feel free to [contact me](https://example.com/contact) for collaborations or inquiries!")
