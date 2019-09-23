import socket
from filepacket import get_id, FilePacketWriter

# class to recieve packet over UDP socket and distribute the packet to multiples file writer
class Receiver:
    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._ip = socket.gethostbyname(socket.gethostname()) # get current computer IP address
        self._socket.bind((ip, 0)) # automatically find open port to connect to
        self._port = self.socket.getsockname()[1]
        print("Reciever active on", ip, "port", port)
        self._writer = {}
        self._ret_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # recieve packet from (ip, port) and distribute it to the corresponding file writer
    def run(self):
        while True:
            packet, ret_addr = self._socket.recvfrom(1024)
            id = get_id(packet)
            if id < 0:
                continue
            idd = ret_addr + "-" + str(id)
            if idd not in self._writer:
            self._writer[idd] = FilePacketWriter(idd, id)
        if self._writer[idd].recieve_packet(packet):
            seq = self._writer[id].rcv_seq()
            print("Recieved packet", idd, "seq", seq)
            self._ret_socket.sendto(self._writer[idd].send_ack(), (ret_addr, self._port))
        else:
            print("Recieved bad packet from", ret_addr)
