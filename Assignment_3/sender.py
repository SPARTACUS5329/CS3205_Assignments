import socket
import sys
import _thread
import time

from timer import Timer
from udt import UDT
from packet import UDPPacket

PACKET_SIZE = 500
RECEIVER_ADDR = ("localhost", 8081)
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
    print("Total packets: ", num_packets)
    window_size = set_window_size(num_packets)
    next_to_send = 0
    base = 0

    _thread.start_new_thread(receive, (sock,))

    while base < num_packets:
        mutex.acquire()
        while next_to_send < base + window_size:
            printd("Sending packet", next_to_send)
            UDT.send(packets[next_to_send], sock, RECEIVER_ADDR)
            next_to_send += 1

        if not send_timer.running(): send_timer.start()

        while send_timer.running() and not send_timer.timeout():
            mutex.release()
            time.sleep(SLEEP_INTERVAL)
            mutex.acquire()

        if send_timer.timeout():
            printd("Timeout")
            send_timer.stop()
            next_to_send = base
        else:
            printd("Shifting window")
            window_size = set_window_size(num_packets)
            printd("window_size:", window_size)
            if window_size <= 0:
                if DEBUG: time.sleep(3)
                base = float("inf")
        mutex.release()

    UDT.send(UDPPacket.make_empty(), sock, RECEIVER_ADDR)
    printd("Send empty packet")
    if DEBUG: time.sleep(3)
    file.close()
    
def receive(sock):
    global mutex
    global base
    global send_timer

    while True:
        try:
            pkt, _ = UDT.recv(sock)
        except:
            printd("Empty packet, terminating server")
            break
        ack, _ = UDPPacket.extract(pkt)

        printd("Got ACK", ack)
        if ack >= base:
            mutex.acquire()
            base = ack + 1
            printd("Base updated", base)
            send_timer.stop()
            mutex.release()

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 2 or (args[1] in ["GBN", "SR"] and len(args) < 3):
        printd("Not enough arguments")
        exit()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(SENDER_ADDR)

    filename = sys.argv[1]
    METHOD = args[1]
    if METHOD == "GBN":
        WINDOW_SIZE = int(args[2])
        DEBUG = True if len(args) > 3 and args[3] == "1" else False
        send(sock, filename)
    elif METHOD == "SW":
        WINDOW_SIZE = 1
        DEBUG = True if len(args) > 2 and args[2] == "1" else False
        send(sock, filename)
    elif METHOD == "SR":
        WINDOW_SIZE = int(args[2])
        DEBUG = True if len(args) > 2 and args[2] == "1" else False
        send(sock, filename)
    else:
        printd("Invalid method name")
        exit()

    sock.close()
    printd("Exiting program, socket closed")
