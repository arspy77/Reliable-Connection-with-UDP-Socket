import socket
from filepacket import get_id, FilePacketReceiver

# class to recieve packet over UDP socket and distribute the packet to multiples file writer
class Receiver:
    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._ip = socket.gethostbyname(socket.gethostname()) # get current computer IP address
        self._socket.bind((self._ip, 0)) # automatically find open port to connect to
        self._port = self._socket.getsockname()[1]
        print("Reciever active on", self._ip, "port", self._port)
        self._writer = {}

    # recieve packet from (ip, port) and distribute it to the corresponding file writer
    def run(self):
        while True:
            packet, ret_addr = self._socket.recvfrom(65536)
            id = get_id(packet)
            if id < 0:
                continue
            idd = ret_addr[0] + "-" + str(ret_addr[1]) + "-" + str(id)
            if idd not in self._writer:
                self._writer[idd] = FilePacketReceiver(idd, id)
            if self._writer[idd].recieve_packet(packet):
                seq = self._writer[idd].rcv_seq()
                print("Recieved packet", idd, "seq", seq)
                self._socket.sendto(self._writer[idd].send_ack(), ret_addr)
            else:
                print("Recieved bad packet from", ret_addr)

if __name__ == "__main__":
    rec = Receiver()
    rec.run()