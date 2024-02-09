import pyshark

if __name__ == "__main__":
    websites = ["deccan", "jagran", "mit", "usach", "sinu"]
    websiteFiles = {website: f"./{website}.pcap" for website in websites}
    captures = {website: pyshark.FileCapture(websiteFiles[website]) for website in websites}

    for website in websites:
        capture = captures[website]
        isDNSQueryStarted = False
        isDNSQueryEnded = False
        for packet in capture:
            if isDNSQueryEnded: break
            protocol = packet.highest_layer
            if protocol == "DNS":
                dnsStart = float(packet.sniff_timestamp)
                isDNSQueryStarted = True
            if isDNSQueryStarted and not protocol == "DNS":
                dnsEnd = float(packet.sniff_timestamp)
                dnsTimeElapsed = dnsEnd - dnsStart
                print(f"Time taken for DNS query to complete: {dnsTimeElapsed}")
                isDNSQueryStarted = False
                isDNSQueryEnded = True
    
        print(f"Website {website} done")
