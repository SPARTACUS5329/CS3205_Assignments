import numpy as np
import matplotlib.pyplot as plt

# Define methods, latencies, and losses
methods = ["GBN", "SW"]
latencies = [50, 100, 150, 200, 250, 500]
losses = [0.1, 0.5, 1, 1.5, 2, 5]

# Function to read results from files
def read_results(method):
    filename = f"{method.lower()}.txt"
    with open(filename, "r") as file:
        results = [float(line.strip()) for line in file]
    return np.array(results).reshape(len(latencies), len(losses))

# Generate heatmaps for each method
for method in methods:
    results = read_results(method)
    print(results)

    plt.figure(figsize=(8, 6))
    plt.imshow(results, cmap="hot", interpolation="nearest")
    plt.title(f"Heatmap for {method}")
    plt.xlabel("Loss")
    plt.ylabel("Latency")
    plt.xticks(np.arange(len(losses)), losses)
    plt.yticks(np.arange(len(latencies)), latencies)
    plt.colorbar(label="Result")
    plt.show()
