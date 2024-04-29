import pandas as pd
import numpy as np
import os

def soc_calc(df_path, initial_charge):
    df = pd.read_csv(df_path)
    t_exp = df['time'].values / 3600  # Convert time to hours

    # Initialize SOC_CC
    SOC_CC = np.zeros(len(t_exp))
    SOC_CC[0] = initial_charge

    C_N = 2.00  # Nominal capacity in Ah

    current_cycle = df['cycle'][0]
    for n in range(1, len(t_exp)):
        if df['cycle'][n] != current_cycle:  # Check if the cycle has changed
            SOC_CC[n] = 1 if 'charge' in df_path else 0  # Reset based on file type
            current_cycle = df['cycle'][n]
        else:
            C_n = df['capacity'][n]
            delta_t = t_exp[n] - t_exp[n - 1]  # Time difference in hours
            SOC_CC[n] = SOC_CC[n - 1] + (delta_t / C_N) * df['current_measured'][n]

            # Calibration at upper and lower voltage limits
            if (SOC_CC[n] > 1):
                SOC_CC[n] = 1
            elif (SOC_CC[n] < 0):
                SOC_CC[n] = 0

    # Update the DataFrame with the calculated SOC_CC values
    df['SOC_CC'] = SOC_CC

    # Save the updated DataFrame to a new CSV file
    df.to_csv(df_path, index=False)

def process_files(folder_path):
    for file in os.listdir(folder_path):
        if file.endswith(".csv"):
            file_path = os.path.join(folder_path, file)
            initial_charge = 1.0 if 'discharge' in file else 0.0
            soc_calc(file_path, initial_charge)

if __name__ == '__main__':
    folder_path = 'Data'
    process_files(folder_path)