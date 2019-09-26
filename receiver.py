import socket
import sys
from filepacket import get_id, FilePacketReceiver

# class to receive packet over UDP socket and distribute the packet to multiples file writer
class Receiver:
    def __init__(self, port_number):
        self._port = port_number
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind(('', port_number)) # automatically find open port to connect to
        self._ip = self._socket.getsockname()[0]
        print("receiver active on", socket.gethostbyname(socket.gethostname()), "port", self._port)
        self._writer = {}

    # receive packet from (ip, port) and distribute it to the corresponding file writer
    def run(self):
        while True:
            packet, ret_addr = self._socket.recvfrom(65536)
            id = get_id(packet)
            if id < 0:
                continue
            idd = ret_addr[0] + "-" + str(ret_addr[1]) + "-" + str(id)
            if idd not in self._writer:
                self._writer[idd] = FilePacketReceiver(packet)
            else:
                self._writer[idd].receive_packet(packet)
            if self._writer[idd].success():
                seq = self._writer[idd].rcv_seq()
                print("received file", self._writer[idd].filename(), "seq", seq)
                self._socket.sendto(self._writer[idd].send_ack(), ret_addr)
            else:
                print("received bad packet from", ret_addr)

if __name__ == "__main__":
    port_number = sys.argv[1]
    rec = Receiver(port_number)
    rec.run()