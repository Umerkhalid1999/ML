# import streamlit as st
#
# # Set page config
# st.set_page_config(
#     page_title="Umar Khalid Mirza - Portfolio",
#     page_icon="🌐",
#     layout="wide"
# )
#
# # Header section
# st.title("Welcome to Umar Khalid Mirza's Portfolio")
# st.markdown(
#     """Explore my work and expertise in various fields of Artificial Intelligence. Choose a category below to learn more."""
# )
#
# # Define categories
# categories = {
#     "Machine Learning": "Machine Learning projects involving supervised and unsupervised learning, predictive modeling, and optimization. [View Projects](https://example.com/ml-projects)",
#     "Deep Learning": "Deep Learning projects utilizing neural networks like CNNs, RNNs, and transformers for advanced AI tasks. [View Projects](https://example.com/dl-projects)",
#     "Data Science": "Comprehensive data science projects including EDA, feature engineering, and model deployment. [View Projects](https://example.com/data-science-projects)",
#     "Data Analysis": "Insights derived from data through statistical analysis, visualization, and business intelligence tools. [View Projects](https://example.com/data-analysis-projects)",
#     "Generative-AI": "Generative AI applications, including text generation, image synthesis, and AI creativity. [View Projects](https://example.com/gen-ai-projects)",
#     "AI Chat Bots": "Interactive chatbots built using NLP techniques for customer support and automation. [View Projects](https://example.com/chatbots)",
#     "AI Tools": "Custom-built AI tools tailored for specific applications. Stay tuned for more details! [View Projects](https://example.com/ai-tools)",
#     "Others": "Explore additional projects and innovative ideas that don't fit into the above categories. [View Projects](https://example.com/others)"
# }
#
# # Layout for category buttons
# cols = st.columns(3)
#
# # Generate buttons for each category
# for i, (category, description) in enumerate(categories.items()):
#     with cols[i % 3]:
#         if st.button(category):
#             st.subheader(f"{category} Projects")
#             st.write(description)
#
# # Footer
# st.markdown("---")
# st.write("Thank you for visiting my portfolio. Feel free to [contact me](https://example.com/contact) for collaborations or inquiries!")
import streamlit as st
import nbformat
from nbconvert import HTMLExporter


# Function to convert Jupyter Notebook to HTML
def notebook_to_html(notebook_path):
    with open(notebook_path, "r", encoding="utf-8") as nb_file:
        notebook_content = nb_file.read()

    notebook = nbformat.reads(notebook_content, as_version=4)
    html_exporter = HTMLExporter()
    (body, _) = html_exporter.from_notebook_node(notebook)
    return body


# Streamlit app
st.title("Jupyter Notebook Integration")

# File uploader for Jupyter Notebook
uploaded_file = st.file_uploader("Upload a Jupyter Notebook (.ipynb)", type="ipynb")

if uploaded_file is not None:
    # Convert the uploaded notebook to HTML
    notebook_html = notebook_to_html(uploaded_file)

    # Display the notebook content in Streamlit
    st.components.v1.html(notebook_html, height=800, scrolling=True)

else:
    st.write("Please upload a Jupyter Notebook to display.")
