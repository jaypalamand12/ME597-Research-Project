import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import StandardScaler


def mse(y_true, y_pred):
    return tf.reduce_mean(tf.square(y_true - y_pred))
# Load pre-trained LSTM model
model_path = '/Users/jaypalamand/Desktop/ME597/DeepLearningModels/LSTM_model.h5'
model = tf.keras.models.load_model(model_path, custom_objects={'mse': mse})

# Function to normalize and create sequences
def normalize_and_sequence(df, sequence_length):
    scaler = StandardScaler()
    features = df.drop('Capacity', axis=1)  # Assuming 'Capacity' is your label
    df_normalized = pd.DataFrame(scaler.fit_transform(features), columns=features.columns)
    df_normalized['Capacity'] = df['Capacity']  # Reattach label
    sequences = []
    labels = []
    for i in range(len(df_normalized) - sequence_length + 1):
        sequences.append(df_normalized.iloc[i:i+sequence_length, :-1].values)
        labels.append(df_normalized.iloc[i+sequence_length-1, -1])
    return np.array(sequences), np.array(labels)

# Define sequence length used in the LSTM model
sequence_length = 10

# Load DataFrames
batteries = ['B0005', 'B0006', 'B0007', 'B0018']
base_path = '/Users/jaypalamand/Desktop/ME597/TransformedData/'
dfs = [pd.read_csv(f'{base_path}{battery}_results.csv') for battery in batteries]

# New base path for saving
new_base_path = '/Users/jaypalamand/Desktop/ME597/Data/NewResults/'

# Process each DataFrame
for battery, df in zip(batteries, dfs):
    print(battery)
    X, _ = normalize_and_sequence(df, sequence_length)
    # Predict SOH
    test_dataset = tf.data.Dataset.from_tensor_slices(X).batch(32)
    predictions = model.predict(test_dataset).flatten()
    print(predictions)
    # Map predictions to their corresponding cycles
    soh_values = pd.Series(predictions, index=np.arange(sequence_length-1, len(df)))
    df['SOH'] = soh_values
    df['SOH'] = df['SOH'].fillna(method='ffill')  # Forward fill to handle the first few cycles without predictions
    
    # Save updated DataFrame
    df.to_csv(f'{new_base_path}{battery}_results_with_SOH.csv', index=False)

