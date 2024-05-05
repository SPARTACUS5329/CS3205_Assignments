import socket
import time
import sys

from packet import UDPPacket
from udt import UDT

RECEIVER_ADDR = ("localhost", 8081)
writeData = []

def printd(*args):
    global DEBUG
    if DEBUG: print(*args)

def receiveGBN(sock, filename):
    try:
        file = open(filename, "wb")
    except IOError:
        print("Unable to open", filename)
        return
    
    expected_num = 0
    start_time = None
    while True:
        pkt, addr = UDT.recv(sock)
        if not start_time: start_time = time.time()
        if not pkt: break

        seq_num, data = UDPPacket.extract(pkt)
        printd("Got packet", seq_num)

        if seq_num == expected_num:
            printd("Got expected packet")
            printd("Sending ACK", expected_num)
            pkt = UDPPacket.make(expected_num)
            UDT.send(pkt, sock, addr)
            expected_num += 1
            file.write(data)
        else:
            printd("Sending ACK", expected_num - 1)
            pkt = UDPPacket.make(expected_num - 1)
            UDT.send(pkt, sock, addr)

    end_time = time.time()
    file.close() 

    return end_time - start_time

def receiveSR(sock, filename):
    try:
        file = open(filename, "wb")
    except IOError:
        print("Unable to open", filename)
        return
    
    expected_num = 0
    expected_future = 1
    start_time = None
    while True:
        pkt, addr = UDT.recv(sock)
        if not start_time: start_time = time.time()
        if not pkt: break

        seq_num, data = UDPPacket.extract(pkt)
        printd("Got packet", seq_num)

        if seq_num == expected_num:
            printd("Got expected packet")
            printd("Sending ACK", expected_num)
            if expected_future - expected_num <= 1:
                pkt = UDPPacket.make(expected_num)
            else:
                pkt = UDPPacket.make(expected_future - 1)
            UDT.send(pkt, sock, addr)
            expected_num, expected_future = expected_future, expected_future + 1
            writeData.append(data)
        elif seq_num == expected_future:
            printd("Got future packet")
            expected_future += 1
        else:
            printd("Sending ACK", expected_num - 1)
            pkt = UDPPacket.make(expected_num - 1)
            UDT.send(pkt, sock, addr)

    end_time = time.time()

    for data in writeData:
        file.write(data)

    file.close() 

    return end_time - start_time

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Not enough arguments")
        exit()
        
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(RECEIVER_ADDR) 

    filename = sys.argv[1]
    method = sys.argv[2]
    DEBUG = True if len(sys.argv) > 3 and sys.argv[3] == "1" else False

    if method in ["GBN", "SW"]: time_taken = receiveGBN(sock, filename)
    elif method == "SR": time_taken = receiveSR(sock, filename)
    else: print("Invalid method")

    sock.close()

    print(time_taken)
