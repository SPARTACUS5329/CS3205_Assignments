class DNSPacket:
    def __init__(self, bitStream) -> None:
        if len(bitStream): bitStream = "0" + bitStream # leftPading the bitStream to get octects
        self.bitStream = bitStream
        if len(self.bitStream) % 8: raise Exception("Invalid data")
        self.header = Header(bitStream[:96])
        bitStream = bitStream[96:]
        self.question = Question(bitStream)
        print(self.question.domain)
        bitStream = bitStream[self.question.totalLength:]
        self.answer = ResourceRecord(bitStream)

class Header:
    def __init__(self, headerString) -> None:
        header = [headerString[i : i + 16] for i in range(0, len(headerString), 16)]
        self.id = header[0]
        self.flags = header[1]
        self.qdCount = header[2]
        self.anCount = header[3]
        self.nsCount = header[4]
        self.arCount = header[5]

class Payload:
    def extract(self, bitStream):
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
    
class ResourceRecord(Payload):
    def __init__(self, bitStream) -> None:
        self.resource, self.resourceLength = super().extract(bitStream)
        self.totalLength = self.resourceLength + 7 * 16 # Assuming A record an class IN

if __name__ == "__main__":
    try:
        bitStream = bin(int(input("Enter DNS hexadecimcal byte stream: "), 16))[2:]
        dnsPacket = DNSPacket(bitStream)
        print(dnsPacket.question.domain)
        if dnsPacket.answer.resource: print(dnsPacket.answer.resource)
    except:
        print("Invalid data")
        exit()