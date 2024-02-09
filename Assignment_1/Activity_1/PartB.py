import pyshark
import matplotlib.pyplot as plt
import math
from dotenv import load_dotenv
import os

load_dotenv()

LOCAL_IP_ADDRESS = os.getenv("LOCAL_IP_ADDRESS_B")
if not LOCAL_IP_ADDRESS:
    print("You don't have a valid local ip address in your .env")
    exit()
print(f"Your local IP is: {LOCAL_IP_ADDRESS}")
DOWNLINK="DOWNLINK"

if __name__ == "__main__":
    websites = ["deccan", "jagran", "mit", "usach", "sinu"]
    websiteFiles = {website: f"./{website}.pcap" for website in websites}
    captures = {website: pyshark.FileCapture(websiteFiles[website]) for website in websites}

    totalDuration = 10
    granularity = 0.1
    numIntervals = int(totalDuration / granularity)
    downlinkPacketsPerInterval = {website: [0]*numIntervals for website in websites}

    for website, capture in captures.items():
        isDNSQueryStarted, isDNSQueryEnded, httpStart, isTTFB, diffReference = False, False, None, False, None
        downlinkPacketsCollected = 0
        intervalEndTime = granularity
        interval = 0
        for packet in capture:
            # if isTTFB: break
            protocol = packet.highest_layer
            packetTime = float(packet.sniff_timestamp)
            if not diffReference: diffReference = packetTime
            packetTime -= diffReference

            # DNS Time
            if not isDNSQueryEnded:
                if protocol == "DNS":
                    dnsStart = packetTime
                    isDNSQueryStarted = True
                    continue
                elif isDNSQueryStarted and not protocol == "DNS":
                    dnsEnd = packetTime
                    dnsTimeElapsed = dnsEnd - dnsStart
                    print(f"Time taken for DNS query to complete: {dnsTimeElapsed}")
                    isDNSQueryStarted = False
                    isDNSQueryEnded = True

            # TTFB
            if "http" in packet:
                print("Reaching")
                if packet.http.request_in:
                    httpStart = packetTime
                elif packet.http.response_in:
                    httpEnd = packetTime
                    isTTFB = True
                    if httpStart is None:
                        print("Something went wrong")
                        continue
                    httpTimeElapsed = httpEnd - httpStart
                    print(f"TTFB: {httpTimeElapsed}")
            
            # Cumulative downlink rraffic
            if "ip" in packet and LOCAL_IP_ADDRESS not in packet.ip.src:
                downlinkPacketsCollected += 1
                downlinkPacketsPerInterval[website][interval] = downlinkPacketsCollected
                if packetTime > intervalEndTime:
                    interval = math.floor(packetTime / granularity)
                    if interval >= numIntervals:
                        print("Interval exceeded maximum limit")
                        break
                    intervalEndTime = (interval + 1) * granularity
    
        print(f"Website {website} done")
        
    print("All captured files parsed")

    for website, graph in downlinkPacketsPerInterval.items():
        for i in range(len(graph) - 1):
            if not graph[i + 1]:
                graph[i + 1] = graph[i]

        plt.plot(graph, label=website)
    
    plt.xlabel("Time")
    plt.ylabel("Data accumulated")
    plt.title("Cumulative data")
    plt.legend()
    plt.show()