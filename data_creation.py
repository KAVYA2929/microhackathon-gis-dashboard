import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set seed for reproducibility
np.random.seed(42)
n_samples = 1000

# Probabilities: 70% Safe, 20% Warning, 10% Critical
states = np.random.choice([0, 1, 2], size=n_samples, p=[0.70, 0.20, 0.10])

timestamps, vib_1, vib_2, gyro, photodiode = [], [], [], [], []

# Starting timestamp
current_time = datetime(2026, 2, 27, 12, 0, 0)

for state in states:
    timestamps.append(current_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
    current_time += timedelta(milliseconds=100) # 100ms interval
    
    if state == 0:  # SAFE
        vib_1.append(0)
        vib_2.append(0)
        gyro.append(round(np.random.uniform(0.0, 0.5), 2))
        photodiode.append(round(np.random.uniform(98.0, 100.0), 1))
        
    elif state == 1:  # WARNING
        # At least one sensor triggers
        v1, v2 = np.random.choice([0, 1]), np.random.choice([0, 1])
        if v1 == 0 and v2 == 0: v1 = 1 
        vib_1.append(v1)
        vib_2.append(v2)
        gyro.append(round(np.random.uniform(2.0, 5.0), 2))
        photodiode.append(round(np.random.uniform(95.0, 100.0), 1))
        
    else:  # CRITICAL
        vib_1.append(1)
        vib_2.append(1)
        gyro.append(round(np.random.uniform(4.0, 9.0), 2))
        # Light drops due to bending
        photodiode.append(round(np.random.uniform(40.0, 80.0), 1))

# Create the DataFrame
df = pd.DataFrame({
    'timestamp': timestamps,
    'vib_1': vib_1,
    'vib_2': vib_2,
    'gyro': gyro,
    'photodiode': photodiode,
    'label': states
})

# Save directly to a CSV file
df.to_csv('fiber_ml_dataset_1000.csv', index=False)
print("1000 rows generated and saved to 'fiber_ml_dataset_1000.csv'")