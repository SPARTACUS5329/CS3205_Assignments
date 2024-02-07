import pyshark
import matplotlib.pyplot as plt
import math

if __name__ == "__main__":
    resolutions = ["480", "720", "1080", "2k", "4k"]
    youtubeFiles = {res: f"./youtube_{res}.pcap" for res in resolutions}
    captures = {res: pyshark.FileCapture(youtubeFiles[res]) for res in resolutions}

    totalDuration = 60
    granularity = 0.1
    numIntervals = int(totalDuration / granularity)
    packetsPerInterval = {res: [0]*numIntervals for res in resolutions}

    for res, capture in captures.items():
        interval = 0
        intervalEndTime = granularity
        diffReference = None
        for packet in capture:
            packetTime = float(packet.sniff_timestamp)
            if not diffReference:
                print("Reaching")
                diffReference = packetTime
            packetTime -= diffReference
            if packetTime > intervalEndTime:
                interval = math.floor(packetTime / granularity)
                if interval >= numIntervals:
                    print("Interval exceeded maximum limit")
                    break
                intervalEndTime = (interval + 1) * granularity
            packetsPerInterval[res][interval] += 1
        print(f"Finished resolution {res}")
    
    packetsPerSecond = {res: [packets / granularity for packets in packetsPerInterval[res]] for res in resolutions}
    print("All captured files parsed")

    for res, graph in packetsPerSecond.items():
        plt.plot(graph, label=res)

    plt.xlabel("Time")
    plt.ylabel("Packets/sec")
    plt.legend()
    plt.title("Packets/sec for all resolutions")
    plt.show()