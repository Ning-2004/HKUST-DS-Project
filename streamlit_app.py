import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import LatentDirichletAllocation as LDA
from sklearn.feature_extraction.text import CountVectorizer
import nltk
from nltk.corpus import stopwords
import re

# Download NLTK stopwords if not already downloaded
nltk.download('stopwords', quiet=True)
default_stopwords = set(stopwords.words('english'))

def clean_text(text, custom_stopwords):
    """Clean and preprocess the text."""
    text = re.sub(r'\W+', ' ', text)  # Remove non-word characters
    text = text.lower()  # Convert to lowercase
    text = ' '.join(word for word in text.split() if word not in custom_stopwords)  # Remove stopwords
    return text

def perform_topic_modeling(texts, num_topics):
    """Perform topic modeling using LDA."""
    vectorizer = CountVectorizer()
    dtm = vectorizer.fit_transform(texts)
    lda = LDA(n_components=num_topics)
    lda.fit(dtm)
    return lda, vectorizer

def display_topics(model, vectorizer, num_words=5):
    """Display the topics generated by the model."""
    topics = {}
    for idx, topic in enumerate(model.components_):
        topics[f'Topic {idx+1}'] = [vectorizer.get_feature_names_out()[i] for i in topic.argsort()[-num_words:]]
    return topics

# Streamlit UI
st.title("Topic Model Web Tool")

# Sidebar for parameters
st.sidebar.header("Upload and Parameters")
uploaded_files = st.sidebar.file_uploader("Choose text files or Excel files", accept_multiple_files=True)
stopwords_file = st.sidebar.file_uploader("Upload custom stopwords (one per line)", type=["txt"])
num_topics = st.sidebar.slider("Number of Topics", min_value=2, max_value=10, value=5)

# Initialize custom stopwords
custom_stopwords = default_stopwords.copy()

if stopwords_file is not None:
    # Read the uploaded custom stopwords
    custom_stopwords = set()
    stopwords_text = stopwords_file.read().decode("utf-8")
    custom_stopwords.update(stopwords_text.splitlines())

texts = []

if uploaded_files:
    for uploaded_file in uploaded_files:
        if uploaded_file.name.endswith('.xlsx') or uploaded_file.name.endswith('.xls'):
            # Read Excel file
            df = pd.read_excel(uploaded_file)
            # Assume the text is in the first column; you can customize this as needed
            text_column = df.columns[0]  # Modify this if you have a specific column name
            for text in df[text_column].dropna():  # Drop NaN values
                cleaned_text = clean_text(text, custom_stopwords)
                texts.append(cleaned_text)
        else:
            # Read text file
            text = uploaded_file.read().decode("utf-8")
            cleaned_text = clean_text(text, custom_stopwords)
            texts.append(cleaned_text)

    # Display cleaned texts
    st.subheader("Uploaded Texts")
    for i, text in enumerate(texts):
        st.write(f"**Text {i+1}:** {text[:200]}...")  # Display first 200 characters

    # Perform topic modeling
    lda_model, vectorizer = perform_topic_modeling(texts, num_topics)
    topics = display_topics(lda_model, vectorizer)

    # Display generated topics
    st.subheader("Generated Topics")
    for topic, words in topics.items():
        st.write(f"**{topic}:** {', '.join(words)}")

    # Visualize topic distribution
    topic_distribution = lda_model.transform(vectorizer.transform(texts))
    plt.figure(figsize=(10, 6))
    plt.bar(range(num_topics), topic_distribution.mean(axis=0), color='skyblue')
    plt.xticks(range(num_topics), [f'Topic {i+1}' for i in range(num_topics)])
    plt.xlabel("Topics")
    plt.ylabel("Average Distribution")
    plt.title("Average Topic Distribution Across Texts")
    st.pyplot(plt)
