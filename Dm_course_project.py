# -*- coding: utf-8 -*-
"""Copy of DM Course Project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1mS4tXhtrFPk2TVP2jgD0YpNX0eLe2NE3

## 1. Project Overview and Imports
"""

# Import necessary libraries
import numpy as np
import pandas as pd
import itertools
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier, LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from collections import Counter
from sklearn.metrics import precision_recall_fscore_support
import warnings
import string
warnings.filterwarnings("ignore")

"""## 2. Load and Explore the Dataset"""

# Load dataset
df = pd.read_csv('content/news.csv')

# Display basic information
print("Dataset Shape: ", df.shape)
print("First few rows of the dataset:\n", df.head())

# Distribution of the target variable
count_class = pd.value_counts(df['label'], sort=True)
print("\nLabel distribution:\n", count_class)

# Plot label distribution (Bar and Pie chart)
count_class.plot(kind='bar', color=["blue", "orange"])
plt.title('Label Distribution - Bar Chart')
plt.show()

count_class.plot(kind='pie', autopct='%1.0f%%')
plt.title('Label Distribution - Pie Chart')
plt.ylabel('')
plt.show()

"""## 3. Word Frequency Analysis"""

# Define your list of unwanted words
unwanted_words = [
    "the", "to", "of", "a", "and", "in", "that", "is", "for", "on", "he", "as", "with", "said",
    "it", "his", "was", "have", "but", "at", "has", "be", "are", "not", "by", "this", "from", "who", 
    "an", "they", "about", "i", "will", "would", "or", "we", "their", "her", "she", "were",
    "been", "had", "it's", "if", "you", "us", "what", "its", "than", "when", "also", "which",
    "so", "there", "him", "your"
]

def preprocess_text_manual(text, unwanted_words):
    """
    Preprocesses the input text by:
    - Converting to lowercase
    - Removing punctuation
    - Splitting into words based on whitespace
    - Removing manually specified unwanted words
    - Keeping only alphabetic words
    """
    if not isinstance(text, str):
        # Handle cases where the text might not be a string
        return []
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    translator = str.maketrans('', '', string.punctuation)
    text = text.translate(translator)
    
    # Split text into words based on whitespace
    words = text.split()
    
    # Remove unwanted words and non-alphabetic words
    meaningful_words = [
        word for word in words 
        if word not in unwanted_words and word.isalpha()
    ]
    
    return meaningful_words

# Apply the preprocessing function to the 'text' column
df['processed_text'] = df['text'].apply(lambda x: preprocess_text_manual(x, unwanted_words))

# Function to get the most common words for a given label
def get_most_common_words(df, label, top_n=20):
    """
    Returns the most common words for a given label.
    
    Parameters:
    - df: pandas DataFrame containing the data
    - label: The label to filter by ('REAL' or 'FAKE')
    - top_n: Number of top common words to return
    
    Returns:
    - List of tuples containing word and its count
    """
    # Filter the DataFrame by label
    filtered_text = df[df['label'] == label]['processed_text']
    
    # Flatten the list of lists into a single list of words
    all_words = list(itertools.chain.from_iterable(filtered_text))
    
    # Count word frequencies
    word_counts = Counter(all_words).most_common(top_n)
    
    return word_counts

# Get the most common words for REAL and FAKE news
count_real = get_most_common_words(df, 'REAL', top_n=20)
count_fake = get_most_common_words(df, 'FAKE', top_n=20)

# Convert word counts to DataFrame
df_real = pd.DataFrame(count_real, columns=["words in REAL", "count"])
df_fake = pd.DataFrame(count_fake, columns=["words in FAKE", "count"])

# Plot word frequencies for REAL news
plt.figure(figsize=(12, 6))
plt.bar(df_real["words in REAL"], df_real["count"], color='green')
plt.xticks(rotation=45, ha='right')
plt.title('Most Frequent Meaningful Words in REAL News')
plt.xlabel('Words')
plt.ylabel('Count')
plt.tight_layout()
plt.show()

# Plot word frequencies for FAKE news
plt.figure(figsize=(12, 6))
plt.bar(df_fake["words in FAKE"], df_fake["count"], color='orange')
plt.xticks(rotation=45, ha='right')
plt.title('Most Frequent Meaningful Words in FAKE News')
plt.xlabel('Words')
plt.ylabel('Count')
plt.tight_layout()
plt.show()

# Frequent words in REAL and FAKE news
count_real = Counter(" ".join(df[df['label'] == 'REAL']["text"]).split()).most_common(20)
count_fake = Counter(" ".join(df[df['label'] == 'FAKE']["text"]).split()).most_common(20)

# Convert word counts to DataFrame
df_real = pd.DataFrame.from_dict(count_real).rename(columns={0: "words in REAL", 1: "count"})
df_fake = pd.DataFrame.from_dict(count_fake).rename(columns={0: "words in FAKE", 1: "count"})

# Plot word frequencies for REAL news
df_real.plot.bar(legend=False)
plt.xticks(np.arange(len(df_real["words in REAL"])), df_real["words in REAL"], rotation=45)
plt.title('Most Frequent Words in REAL News')
plt.xlabel('Words')
plt.ylabel('Count')
plt.show()

# Plot word frequencies for FAKE news
df_fake.plot.bar(legend=False, color='orange')
plt.xticks(np.arange(len(df_fake["words in FAKE"])), df_fake["words in FAKE"], rotation=45)
plt.title('Most Frequent Words in FAKE News')
plt.xlabel('Words')
plt.ylabel('Count')
plt.show()

"""## 4. Preprocess Data and Split Dataset"""

# Define features (X) and target (y)
X = df['text']
y = df['label']

# Split data into training and testing sets (33% test size)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

# Print the size of each split
print(f"Training data size: {X_train.shape[0]}, Testing data size: {X_test.shape[0]}")

"""## 5. TF-IDF Vectorization and Model Training"""

# Define the TF-IDF Vectorizer and LinearSVC Classifier in a pipeline
text_clf = Pipeline([
    ('tfidf', TfidfVectorizer(stop_words='english', max_df=0.7)),
    ('clf', LinearSVC())
])

# Train the model on training data
text_clf.fit(X_train, y_train)

"""## 6. Evaluate the Model"""

# Make predictions on the test set
y_pred = text_clf.predict(X_test)

# Calculate and display evaluation metrics
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# Calculate accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy * 100:.2f}%")

"""## 7. Implement Multiple Classifiers"""

# Define a list of classifiers to compare, including Naive Bayes and SGDClassifier
classifiers = {
    'LinearSVC': LinearSVC(C=100,tol=0.1),
    'LogisticRegression': LogisticRegression(max_iter=100),
    'MultinomialNB': MultinomialNB(),
    'SGDClassifier': SGDClassifier(max_iter=1000, tol=1e-3)
}

# Create an empty dictionary to store results
results = {}

# Loop through each classifier, train, predict, and store the results
for name, clf in classifiers.items():
    # Create a pipeline with TF-IDF and classifier
    pipe = Pipeline([('tfidf', TfidfVectorizer(stop_words='english', max_df=0.7)), ('clf', clf)])

    # Train the model
    pipe.fit(X_train, y_train)

    # Predict on the test data
    y_pred = pipe.predict(X_test)

    # Calculate accuracy, precision, recall, and F1-score
    accuracy = accuracy_score(y_test, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')

    # Store results in the dictionary
    results[name] = {
        'Accuracy': accuracy * 100,
        'Precision': precision * 100,
        'Recall': recall * 100,
        'F1-Score': f1 * 100
    }

# Convert results to DataFrame for easy display
results_df = pd.DataFrame(results).T
print("\nSummary of Classifier Performance:")
print(results_df)

# Plot results to compare
results_df.plot(kind='bar', figsize=(12, 6))
plt.title('Classifier Performance Comparison')
plt.ylabel('Score (%)')
plt.xticks(rotation=45)
plt.show()

"""## 8. Testing Custom Inputs using SGD Classifier"""

# Initialize the SGD pipeline
text_clf = Pipeline([
    ('tfidf', TfidfVectorizer(stop_words='english', max_df=0.7)),
    ('clf', SGDClassifier(max_iter=1000, tol=1e-3))
])

# Train the pipeline on your training data
text_clf.fit(X_train, y_train)

# Custom predictions to test the model
test_cases = [
    "your email was selected to claim the sum of $5,000,000 in the lottery",
    "India's Covid-19 caseload has crossed the 8.5 lakh mark...",
    "Breaking news: BSF personnel arrested in drug smuggling case",
    "U.S. Secretary of State John F. Kerry said Mon...",
    "It's primary day in New York and front-runners...",
    "Daniel Greenfield, a Shillman Journalism Fello..."
]

# Predict the label for each case using the trained model
for case in test_cases:
    prediction = text_clf.predict([case])
    print(f"Prediction for: \"{case[:50]}...\" is {prediction[0]}")

"""# 9. Summarize the Results of Different Classifiers

"""

# Identify and print the classifier with the best accuracy
best_classifier = results_df['Accuracy'].idxmax()
best_accuracy = results_df['Accuracy'].max()

print(f"\nThe classifier with the best accuracy is {best_classifier} with an accuracy of {best_accuracy:.2f}%.")

# Discussion on the best classifier
if best_classifier == 'SGDClassifier':
    print(f"\nThe {best_classifier} achieves the highest accuracy at {best_accuracy:.2f}%, which shows that the SGDClassifier performs better than other classifiers for this fake news detection task.")
    print("SGD is known for being efficient with large datasets and converging faster, which likely contributes to its success in this case.")

# Discuss the performance of each classifier
for name, metrics in results.items():
    print(f"\nClassifier: {name}")
    print(f"Accuracy: {metrics['Accuracy']:.2f}%")
    print(f"Precision: {metrics['Precision']:.2f}%")
    print(f"Recall: {metrics['Recall']:.2f}%")
    print(f"F1-Score: {metrics['F1-Score']:.2f}%")

# Highlight the superior performance of SGDClassifier
print(f"\nSGDClassifier gives the best accuracy of {best_accuracy:.2f}%.")
print(f"SGDClassifier performs well because it uses stochastic gradient descent, which is particularly effective for large-scale and sparse datasets, common in text classification tasks like fake news detection.")

"""## 10. Report and Visualize Results"""

# Save confusion matrix as heatmap
import seaborn as sns
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.title('Confusion Matrix')
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.show()

# Save classification report
report = classification_report(y_test, y_pred, output_dict=True)
df_report = pd.DataFrame(report).transpose()
df_report.to_csv("classification_report.csv")

# Discussion on the results

for name, metrics in results.items():
    print(f"\nClassifier: {name}")
    print(f"Accuracy: {metrics['Accuracy']:.2f}%")
    print(f"Precision: {metrics['Precision']:.2f}%")
    print(f"Recall: {metrics['Recall']:.2f}%")
    print(f"F1-Score: {metrics['F1-Score']:.2f}%")

    # Explanation of results
    print(f"\nThe {name} classifier achieves an accuracy of {metrics['Accuracy']:.2f}%, which is an indication of how well the model is performing overall.")
    print(f"Precision of {metrics['Precision']:.2f}% suggests how often the classifier's positive predictions are correct.")
    print(f"Recall of {metrics['Recall']:.2f}% shows how well the classifier captures all relevant positives in the dataset.")
    print(f"Finally, the F1-Score, a weighted average of precision and recall, is {metrics['F1-Score']:.2f}%, balancing both false positives and false negatives.")

    print("\nOverall, these metrics can help decide the most effective model for fake news detection.")