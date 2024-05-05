import numpy as np
import matplotlib.pyplot as plt

methods = ["SW", "GBN", "SR"]
latencies = [50, 100, 150, 200, 250, 500]
losses = [0.1, 0.5, 1, 1.5, 2, 5]

def read_results(method):
    filename = f"{method.lower()}.txt"
    with open(filename, "r") as file:
        results = [float(line.strip()) for line in file]
    return np.array(results).reshape(len(latencies), len(losses))

global_min = np.inf
global_max = -np.inf
for method in methods:
    results = read_results(method)
    global_min = min(global_min, np.min(results))
    global_max = max(global_max, np.max(results))

for method in methods:
    results = read_results(method)
    print(results)

    plt.figure(figsize=(8, 6))
    plt.imshow(results, cmap="hot", interpolation="nearest", vmin=global_min, vmax=global_max)
    plt.title(f"Heatmap for {method}")
    plt.xlabel("Loss")
    plt.ylabel("Latency")
    plt.xticks(np.arange(len(losses)), losses)
    plt.yticks(np.arange(len(latencies)), latencies)
    plt.colorbar(label="Time to download")
    plt.show()
