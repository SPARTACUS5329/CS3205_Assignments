class UDT:
    @staticmethod
    def send(packet, sock, addr):
        sock.sendto(packet, addr)
        return

    @staticmethod
    def recv(sock):
        packet, addr = sock.recvfrom(26000)
        return packet, addr
