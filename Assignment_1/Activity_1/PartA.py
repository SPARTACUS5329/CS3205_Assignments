import pyshark
import matplotlib.pyplot as plt
import math
from dotenv import load_dotenv
import os

load_dotenv()

LOCAL_IP_ADDRESS = os.getenv("LOCAL_IP_ADDRESS_A")
if not LOCAL_IP_ADDRESS:
    print("You don't have a valid local ip address in your .env")
    exit()
print(f"Your local IP is: {LOCAL_IP_ADDRESS}")
UPLINK="UPLINK"
DOWNLINK="DOWNLINK"

if __name__ == "__main__":
    resolutions = ["480", "720", "1080", "2k", "4k"]
    youtubeFiles = {res: f"./youtube_{res}.pcap" for res in resolutions}
    captures = {res: pyshark.FileCapture(youtubeFiles[res]) for res in resolutions}

    totalDuration = 60
    granularity = 0.1
    numIntervals = int(totalDuration / granularity)
    uplinkPacketsPerInterval = {res: [0]*numIntervals for res in resolutions}
    downlinkPacketsPerInterval = {res: [0]*numIntervals for res in resolutions}

    for res, capture in captures.items():
        interval = 0
        intervalEndTime = granularity
        diffReference = None
        downlinkSlots = 0
        burstSlots = 0
        observedSlots = 0
        for packet in capture:
            if not "ip" in packet: continue
            if LOCAL_IP_ADDRESS in packet.ip.src: typeOfPacket = UPLINK
            else:
                typeOfPacket = DOWNLINK
                downlinkSlots += 1
            packetTime = float(packet.sniff_timestamp)
            if not diffReference: diffReference = packetTime
            packetTime -= diffReference
            if packetTime > intervalEndTime:
                interval = math.floor(packetTime / granularity)
                if interval >= numIntervals:
                    print("Interval exceeded maximum limit")
                    break
                intervalEndTime = (interval + 1) * granularity
                if downlinkSlots > 100: burstSlots += 1
                downlinkSlots = 0
                observedSlots += 1
            if typeOfPacket == UPLINK:
                uplinkPacketsPerInterval[res][interval] += 1
            else:
                downlinkPacketsPerInterval[res][interval] += 1
        
        burstFraction = burstSlots / observedSlots
        print(f"Burst Fraction for res = {res}: {burstFraction}")
        print(f"Finished resolution {res}")
    
    uplinkPacketsPerSecond = {res: [packets / granularity for packets in uplinkPacketsPerInterval[res]] for res in resolutions}
    downlinkPacketsPerSecond = {res: [packets / granularity for packets in downlinkPacketsPerInterval[res]] for res in resolutions}
    print("All captured files parsed")

    plt.subplot(1, 2, 1)
    for res, graph in uplinkPacketsPerSecond.items():
        plt.plot(graph, label=res)
    
    plt.xlabel("Time")
    plt.ylabel("Packets/sec")
    plt.legend()
    plt.title("Uplink traffic")
    
    plt.subplot(1, 2, 2)
    for res, graph in downlinkPacketsPerSecond.items():
        plt.plot(graph, label=res)

    plt.xlabel("Time")
    plt.ylabel("Packets/sec")
    plt.legend()
    plt.title("Downlink traffic")
    plt.show()