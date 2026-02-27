import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
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

# 3. Initialize and train the Linear Regression model
print("Training Linear Regression model...")
model = LinearRegression()

model.fit(X_train, y_train)

# 4. Evaluate the model
print("\nEvaluating model...")
y_pred = model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"\nMean Squared Error (MSE): {mse:.4f}")
print(f"R-squared (R2): {r2:.4f}")

# 5. Save the model
model_filename = 'linear_regression_fiber_model.pkl'
with open(model_filename, 'wb') as file:
    pickle.dump(model, file)
    
print(f"\nModel saved successfully as '{model_filename}'")
