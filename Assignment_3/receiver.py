import socket
import random
import time
import sys
import udt

from packet import UDPPacket

RECEIVER_ADDR = ("localhost", 8081)

def printd(*args):
    global DEBUG
    if DEBUG: print(*args)

def receive(sock, filename):
    try:
        file = open(filename, "wb")
    except IOError:
        print("Unable to open", filename)
        return
    
    expected_num = 0
    start_time = None
    while True:
        pkt, addr = udt.recv(sock)
        if not start_time: start_time = time.time()
        if not pkt: break

        seq_num, data = UDPPacket.extract(pkt)
        printd("Got packet", seq_num)

        if seq_num == expected_num:
            printd("Got expected packet")
            printd("Sending ACK", expected_num)
            pkt = UDPPacket.make(expected_num)
            udt.send(pkt, sock, addr)
            expected_num += 1
            file.write(data)
        else:
            printd("Sending ACK", expected_num - 1)
            pkt = UDPPacket.make(expected_num - 1)
            udt.send(pkt, sock, addr)

    end_time = time.time()
    file.close() 

    return end_time - start_time

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Not enough arguments")
        exit()
        
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(RECEIVER_ADDR) 

    filename = sys.argv[1]
    DEBUG = True if len(sys.argv) > 2 and sys.argv[2] == "1" else False

    time_taken = receive(sock, filename)

    sock.close()
    print(time_taken) 
