import socket
from filereader import get_id, FilePacketWriter

class Receiver:
    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip = socket.gethostbyname(socket.gethostname())
        self._socket.bind((ip, 0))
        port = self.socket.getsockname()[1]
        print("Reciever active on", ip, "port", port)
        self._writer = {}
        self._ret_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def run(self):
        packet, ret_addr = self._socket.recvfrom(1024) # ??????????????????? magic number wtf
        id = get_id(packet)
        if id not in self._writer:
            self._writer[id] = FilePacketWriter("file" + str(id), id)
        if self._writer[id].write(packet):
            seq = self._writer[id].get_last_seq()
            print("Succesfully write file" + str(id) + " seq " + str(seq))
            self._ret_socket.sendto(self._writer[id].generate_ack(), (ret_addr, self._port))
        else:
            print("wtf is that shit")
