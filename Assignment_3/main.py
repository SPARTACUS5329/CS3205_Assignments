import subprocess
import numpy as np
import time
import os

if __name__ == "__main__":
    BANDWIDTH = 100
    latencies = [50, 100, 150, 200, 250, 500]
    losses = [0.1, 0.5, 1, 1.5, 2, 5]
    methods = ["GBN", "SW", "SR"]

    # os.system("tc qdisc add dev eth0 root handle 1:0 netem rate 800kbit")

    sw, gbn, sr = np.ones((6, 6)), np.ones((6, 6)), np.ones((6, 6))
    results = [sw, gbn, sr]

    for i in range(len(latencies)):
        latency = latencies[i]
        # os.system("tc qdisc change dev eth0 root netem delay ${latency}ms 10ms distribution normal")
        for j in range(len(losses)):
            loss = losses[j]
            # os.system("tc qdisc change dev eth0 root netem loss ${loss}%")
            for method in methods:
                print(f"Starting {method} for {latency} {loss}")
                if method == "GBN":
                    start_time = time.time()

                    receiver_command = ["python3", "receiver.py", "out.jpeg"]
                    sender_command = ["python3", "sender.py", "loco.jpeg", "GBN", "10"]
                    receiver_process = subprocess.Popen(receiver_command)
                    sender_process = subprocess.Popen(sender_command)

                    receiver_process.wait()
                    sender_process.wait()

                    end_time = time.time()

                elif method == "SW":
                    start_time = time.time()

                    receiver_command = ["python3", "receiver.py", "out.jpeg"]
                    sender_command = ["python3", "sender.py", "loco.jpeg", "SW"]
                    receiver_process = subprocess.Popen(receiver_command)
                    sender_process = subprocess.Popen(sender_command)

                    end_time = time.time()

                elif method == "SR":
                    print("Not implemented yet")

                else:
                    print("Invalid method name")
                    continue

                print(f"Finished {method} for {latency} {loss}")
                print(f"Time elapsed: {end_time - start_time}")
