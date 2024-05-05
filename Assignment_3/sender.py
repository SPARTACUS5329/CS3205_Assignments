import socket
import sys
import _thread
import time
import udt

from timer import Timer
from packet import UDPPacket

PACKET_SIZE = 500 
RECEIVER_ADDR = ("localhost", 8080)
SENDER_ADDR = ("localhost", 0)
SLEEP_INTERVAL = 0.005
TIMEOUT_INTERVAL = 0.2

base = 0
mutex = _thread.allocate_lock()
send_timer = Timer(TIMEOUT_INTERVAL)

def printd(*args):
    global DEBUG
    if DEBUG: print(*args)

def set_window_size(num_packets):
    global base
    return min(WINDOW_SIZE, num_packets - base)

def send(sock, filename):
    global mutex
    global base
    global send_timer

    try:
        file = open(filename, "rb")
    except IOError:
        printd("Unable to open", filename)
        return
    
    packets = []
    seq_num = 0
    while True:
        data = file.read(PACKET_SIZE)
        if not data:
            break
        packets.append(UDPPacket.make(seq_num, data))
        seq_num += 1

    num_packets = len(packets)
    print("I got", num_packets)
    print("Beginning to send in 5 seconds ...")
    time.sleep(5)
    window_size = set_window_size(num_packets)
    next_to_send = 0
    base = 0

    _thread.start_new_thread(receive, (sock,))

    while base < num_packets:
        mutex.acquire()
        while next_to_send < base + window_size:
            printd("Sending packet", next_to_send)
            udt.send(packets[next_to_send], sock, RECEIVER_ADDR)
            next_to_send += 1

        if not send_timer.running():
            printd("Starting timer")
            send_timer.start()

        while send_timer.running() and not send_timer.timeout():
            mutex.release()
            printd("Sleeping")
            time.sleep(SLEEP_INTERVAL)
            mutex.acquire()

        if send_timer.timeout():
            printd("Timeout")
            send_timer.stop();
            next_to_send = base
        else:
            printd("Shifting window")
            window_size = set_window_size(num_packets)
        mutex.release()

    udt.send(UDPPacket.make_empty(), sock, RECEIVER_ADDR)
    file.close()
    
def receive(sock):
    global mutex
    global base
    global send_timer

    while True:
        pkt, _ = udt.recv(sock);
        ack, _ = UDPPacket.extract(pkt);

        printd("Got ACK", ack)
        if (ack >= base):
            mutex.acquire()
            base = ack + 1
            printd("Base updated", base)
            send_timer.stop()
            mutex.release()

if __name__ == "__main__":
    args = sys.argv[1:] # [filename, method, window_size]
    DEBUG = False
    if len(args) < 2 or (args[1] == "GBN" and len(args) < 3):
        printd("Not enough arguments")
        exit()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(SENDER_ADDR)

    filename = sys.argv[1]
    METHOD = args[1]
    if METHOD == "GBN": WINDOW_SIZE = int(args[2])
    elif METHOD == "SW": WINDOW_SIZE = 1
    else:
        printd("Invalid method name")
        exit()

    send(sock, filename)
    sock.close()
