from filepacket import FilePacketSender, FilePacketReceiver
import random

if __name__ == "__main__":
    sender = FilePacketSender("test", 0)
    packet = sender.send_packet()
    receiver = FilePacketReceiver(packet)
    while not sender.is_done():
        packet = sender.send_packet()
        # if random.randrange(100) < 35:
        #     for i in range(len(packet)):
        #         if random.randrange(100) < 5:
        #             packet[i] = random.randrange(256)
        print(packet)
        if receiver.receive_packet(packet):
            ack = receiver.send_ack()
            if random.randrange(100) < 35:
                for i in range(len(ack)):
                    if random.randrange(100) < 5:
                        ack[i] = random.randrange(256)
            if not sender.receive_ack(ack):
                print("received bad ack")
        else:
            print("received bad packet")
    print("done")
