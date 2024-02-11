class DNSPacket:
    def __init__(self, bitStream) -> None:
        if len(bitStream) % 2: bitStream = "0" + bitStream # leftPading the bitStream to get octects
        self.bitStream = bitStream
        if len(self.bitStream) % 8: raise Exception("Incomplete octets")
        self.header = Header(bitStream[:96])
        bitStream = bitStream[96:]
        self.question = Question(bitStream)
        bitStream = bitStream[self.question.totalLength:]
        self.answer = ResourceRecord(bitStream, self.bitStream)

class Header:
    def __init__(self, headerString) -> None:
        header = [headerString[i : i + 16] for i in range(0, len(headerString), 16)]
        self.id = header[0]
        self.flags = header[1]
        if self.flags[9 : 12] != "000": raise Exception("Invalid reserved flag")
        self.qdCount = header[2]
        self.anCount = header[3]
        self.nsCount = header[4]
        self.arCount = header[5]

class Payload: # Parent class for resources and questions
    def extract(self, bitStream): # Extracts the domain name from the bitStream
        i = 0
        labels = []
        while bitStream[i : i + 8] != "0" * 8:
            lengthOctet = int(bitStream[i : i + 8], 2)
            label = ""
            j = i + 8
            for _ in range(lengthOctet):
                label += chr(int(bitStream[j : j + 8], 2))
                j += 8
            labels.append(label)
            i += (lengthOctet + 1) * 8
        i += 8
        return ".".join(labels), i

class Question(Payload):
    def __init__(self, bitStream) -> None:
        self.domain, self.nameLength = super().extract(bitStream)
        self.totalLength = self.nameLength + 2 * 16 # QTYPE and QCLASS
    
class ResourceRecord(Payload): # Can be used as a parent class for all RR based fields
    def __init__(self, bitStream, originalBitStream) -> None:
        # Message compression check
        if bitStream[:2] == "11":
            offset = int(bitStream[2:16], 2)
            bitStreamCopy = originalBitStream[8 * offset:]
            self.domain, self.domainLength = super().extract(bitStreamCopy)
            bitStream = bitStream[5 * 16:] # TYPE, CLASS and TTL
        # In case no message compression
        elif bitStream[:2] == "00":
            self.domain, self.domainLength = super().extract(bitStream)
            bitStream = bitStream[self.domainLength + 4 * 16:] # TYPE, CLASS and TTL
        # Invalid opCode for message compression i.e. "01" or "10"
        else: raise Exception("Invalid message compression")
        
        self.rdLength = int(bitStream[:16], 2)
        bitStream = bitStream[16:]
        labels = []
        for i in range(0, 8 * self.rdLength, 8):
            octet = bitStream[i : i + 8]
            label = int(octet, 2)
            labels.append(str(label))
        
        self.resource = ".".join(labels)



if __name__ == "__main__":
    try:
        bitStream = bin(int(input("Enter DNS hexadecimcal byte stream: "), 16))[2:]
        dnsPacket = DNSPacket(bitStream)
        print(f"Question:{dnsPacket.question.domain}")
        if dnsPacket.answer.resource: print(f"Answer: {dnsPacket.answer.resource}")
    except Exception as err:
        print(err)
        print("Invalid data")
        exit()