import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import xgboost as xgb
import pickle

# 1. Load the dataset
print("Loading dataset...")
df = pd.read_csv('fiber_ml_dataset_1000.csv')

# 2. Preprocess the data
# We don't need the timestamp for training
X = df.drop(columns=['timestamp', 'label'])
y = df['label']

# Split into training and testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Initialize and train the XGBoost Classifier
print("Training XGBoost model...")
# Using objective='multi:softmax' since we have 3 classes (0=Safe, 1=Warning, 2=Critical)
model = xgb.XGBClassifier(
    objective='multi:softmax', 
    num_class=3, 
    random_state=42,
    eval_metric='mlogloss'
)

model.fit(X_train, y_train)

# 4. Evaluate the model
print("\nEvaluating model...")
y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print(f"\nAccuracy: {accuracy:.4f}")

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['Safe (0)', 'Warning (1)', 'Critical (2)']))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# 5. Save the model
model_filename = 'xgboost_fiber_model.pkl'
with open(model_filename, 'wb') as file:
    pickle.dump(model, file)
    
print(f"\nModel saved successfully as '{model_filename}'")
