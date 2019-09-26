import threading
import socket
from filepacket import FilePacketSender
import time
import sys
import os
# class for a thread that runs function with args every time seconds
class ThreadTimer(threading.Thread):
    def __init__(self, event, time, function, args):
        threading.Thread.__init__(self)
        self.stopped = event
        self.function = function
        self.args = args
        self.time = time

    def run(self):
        while not self.stopped.wait(self.time):
            self.function(self.args)

# class for reading data from file named filename and send packet to (ip, port)
class Sender:
    def __init__(self, ip, port, filename, id):
        self._receiver_ip = ip
        self._receiver_port = port
        self._id = id
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._reader = FilePacketSender(filename, self._id)
        self.filesize = os.stat(filename).st_size + 1 + len(filename)
        self.partsize = 0
        global progress

    # send MESSAGE to (ip, port)
    def send_message(self,MESSAGE):
        self._socket.sendto(MESSAGE, (self._receiver_ip, self._receiver_port))
        
    # read data from file named filename and send packet to (ip, port)
    def run(self):
        while not(self._reader.is_done()):
            stop_flag = threading.Event()
            timer = ThreadTimer(stop_flag, 5, self.send_message, self._reader.send_packet())
            self.send_message(self._reader.send_packet())
            timer.start()
            ack, _ = self._socket.recvfrom(1024)
            while not(self._reader.receive_ack(ack)):
                ack, _ = self._socket.recvfrom(1024)
            stop_flag.set()
            self.partsize = (self._reader.rcv_seq() + 1) * 32768
            if self.partsize > self.filesize:
                self.partsize = self.filesize
            progress[self._id] = self.partsize/self.filesize
        

# thread for a sender for each file
def file_sender_thread(ip, port, filepath, id):
    sender = Sender(ip, port, filepath, id)
    sender.run()
    print(ip, port, filepath, id)


# retuns True if all progress has ended
def progress_ended(progress, n):
    end = True
    for i in range(n):
        if progress[i] < 1:
            end = False
    return end

if __name__ == "__main__":
    UDP_IP = sys.argv[1]
    UDP_PORT = int(sys.argv[2])
    n = int(input("Insert number of files to send: "))

    thread = []
    filepath = []

    global progress
    progress = []

    for i in range(n):
        progress.append(0)
        filepath.append(input('Insert Filepath #' + str(i) + ': '))
        thread.append(threading.Thread(target=file_sender_thread, args=(UDP_IP,  UDP_PORT, filepath[i], i)))

    for i in range(n):
        thread[i].start()

    while not progress_ended(progress, n): 
        if os.name =='nt':
            os.system('cls')
        else:
            os.system('clear')

        for i in range(n):
            sys.stdout.write("[%-20s]" % ('='*int(progress[i]*20)))
            sys.stdout.write(str(int(progress[i]*100))+"%")
            sys.stdout.write("/100%")
            sys.stdout.write("   " + filepath[i])
            sys.stdout.write('\n')
            sys.stdout.flush()
        
    sys.stdout.write("All files successfully sent\n")
        
    

