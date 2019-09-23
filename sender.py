import threading
import socket
from filepacket import FilePacketSender
import time
import string
import random

class ThreadTimer(threading.Thread):
    def __init__(self, event, time, function):
        threading.Thread.__init__(self)
        self.stopped = event
        self.function = function
        self.args = args
        self.time = time

    def run(self):
        while not self.stopped.wait(self.time):
            self.function(self.args)

class Sender:
    def __init__(self, ip, port, filename, id):
        self._receiver_ip = ip
        self._receiver_port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._ret_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        my_ip = socket.gethostbyname(socket.gethostname())
        self._ret_socket.bind((my_ip, port))
        self._reader = FilePacketReader(filename, id)
        
    def send_message(self,MESSAGE):
        self._sock.sendto(MESSAGE, (self._receiver_ip, self._receiver_port))

    def run(self):
        seq_number = 0
        packet = self._reader.read(seq_number)
        while packet != b'':
            stop_flag = threading.Event()
            timer = ThreadTimer(stop_flag, 5, self.send_message, packet)
            self.send_message(packet)
            timer.start()
            self._ret_socket.recvfrom(1024)
            stop_flag.set()
        # still need to impl


def file_sender_thread(ip, port, filepath, id):
    sender = Sender(ip, port, filepath, id)
    sender.run()

if __name__ == "__main__":
    # UDP_IP = input("Insert reciever IP   : ")
    # UDP_PORT = int(input("Insert reciever port : "))
    letters = string.ascii_lowercase
    message = ''.join(random.choice(letters) for i in range(10))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        sock.sendto(message.encode(), ('localhost', 10000))
        print(message)
        time.sleep(1)