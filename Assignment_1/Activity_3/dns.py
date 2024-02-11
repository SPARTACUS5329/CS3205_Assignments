class Header:
    def __init__(self, headerString) -> None:
        header = [headerString[i : i + 16] for i in range(0, len(headerString), 16)]
        self.id = header[0]
        self.flags = header[1]
        self.qdCount = header[2]
        self.anCount = header[3]
        self.nsCount = header[4]
        self.arCount = header[5]

class Question:
    def __init__(self, bitStream) -> None:
        self.domain = self.extractDomain(bitStream)
    
    def extractDomain(self, bitStream) -> str:
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
        return ".".join(labels)

if __name__ == "__main__":
    try:
        bitStream = bin(int(input("Enter DNS hexadecimcal byte stream: "), 16))[2:]
    except:
        print("Enter a valid hexadecimal byte stream")
        exit()
    if len(bitStream) % 2: bitStream = "0" + bitStream
    header = Header(bitStream[:96])
    bitStream = bitStream[96:]
    question = Question(bitStream)
    print(question.domain)