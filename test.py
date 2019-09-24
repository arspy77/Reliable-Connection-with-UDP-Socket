from filepacket import FilePacketSender, FilePacketReceiver
import random

if __name__ == "__main__":
    sender = FilePacketSender("testImage.jpg", 0)
    reciever = FilePacketReceiver("testImage2.jpg", 0)
    while not sender.is_done():
        packet = sender.send_packet()
        if random.randrange(100) < 35:
            for i in range(len(packet)):
                if random.randrange(100) < 5:
                    packet[i] = random.randrange(256)
        # print(packet)
        if reciever.recieve_packet(packet):
            ack = reciever.send_ack()
            if random.randrange(100) < 35:
                for i in range(len(ack)):
                    if random.randrange(100) < 5:
                        ack[i] = random.randrange(256)
            if not sender.recieve_ack(ack):
                print("recieved bad ack")
        else:
            print("recieved bad packet")
    print("done")
