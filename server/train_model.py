import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report
import pickle
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Load the dataset
try:
    df = pd.read_csv('sms_spam_dataset.csv')
except FileNotFoundError:
    print("Error: 'sms_spam_dataset.csv' not found. Please ensure the file is in the same directory as this script.")
    exit(1)

def preprocess_text(text):
    if pd.isna(text):
        return ""
    if not isinstance(text, str):
        text = str(text)
    # Tokenize the text
    tokens = word_tokenize(text.lower())
    # Remove stopwords and non-alphabetic tokens
    stop_words = set(stopwords.words('english'))
    tokens = [t for t in tokens if t.isalpha() and t not in stop_words]
    return ' '.join(tokens)

# Preprocess the text data
df['processed_text'] = df['text'].apply(preprocess_text)

# Convert labels to binary
df['label_binary'] = df['label'].map({'ham': 0, 'spam': 1})

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(df['processed_text'], df['label_binary'], test_size=0.2, random_state=42)

# Create and fit the vectorizer (using TF-IDF instead of CountVectorizer)
vectorizer = TfidfVectorizer()
X_train_vectorized = vectorizer.fit_transform(X_train)

# Train the Naive Bayes model
model = MultinomialNB()
model.fit(X_train_vectorized, y_train)

# Evaluate the model
X_test_vectorized = vectorizer.transform(X_test)
y_pred = model.predict(X_test_vectorized)
print(classification_report(y_test, y_pred, target_names=['ham', 'spam']))

# Save the model and vectorizer
with open('spam_model.pkl', 'wb') as f:
    pickle.dump(model, f)
with open('vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)

print("Model and vectorizer saved successfully.")