import csv
import numpy as np
import matplotlib.pyplot as plt

def read_csv(file_name):
    times = []
    values = []
    
    with open(file_name, mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if len(row) == 2:
                try:
                    time = float(row[0])
                    value = float(row[1])
                    times.append(time)
                    values.append(value)
                except ValueError:
                    continue
    
    return np.array(times), np.array(values)

def analyze_data(times, values):
    # Low values are assumed to be below 0.2
    low_values = values < 0.2
    high_values = values >= 0.2
    
    low_times = times[low_values]
    high_times = times[high_values]
    
    # Analyzing the time intervals
    low_intervals = np.diff(low_times) if len(low_times) > 1 else []
    high_intervals = np.diff(high_times) if len(high_times) > 1 else []
    
    print(f"Low value count: {len(low_times)}")
    print(f"High value count: {len(high_times)}")
    
    # Print intervals between low and high values
    print(f"Average low interval: {np.mean(low_intervals) if low_intervals else 0} ms")
    print(f"Average high interval: {np.mean(high_intervals) if high_intervals else 0} ms")
    
    return low_times, high_times, low_intervals, high_intervals

def plot_data(times, values):
    plt.figure(figsize=(10, 6))
    plt.plot(times, values, label="Signal")
    plt.title("Signal Analysis")
    plt.xlabel("Time (ms)")
    plt.ylabel("Signal Value")
    plt.grid(True)
    plt.show()

def main():
    # Read the CSV file
    times, values = read_csv('NewFile3.csv')
    
    # Analyze the data
    low_times, high_times, low_intervals, high_intervals = analyze_data(times, values)
    
    # Plot the data
    plot_data(times, values)

if __name__ == "__main__":
    main()
