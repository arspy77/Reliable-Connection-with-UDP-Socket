import io

def xor_all(data):
    xor_val = 0
    data_stream = io.BytesIO(data)
    switch = False
    val = data_stream.read(1)
    while val != b'':
        if switch:
            xor_val ^= int.from_bytes(val, "big") << 8
        else:
            xor_val ^= int.from_bytes(val, "big")
        switch = not(switch)
        val = data_stream.read(1)
    return xor_val


def int_to_bytes(b):
    return b >> 8, b & 0xFF

def bytes_to_int(a, b):
    return (a << 8) | b

def get_id(packet):
    _, id = int_to_bytes(packet[0])
    return id

MAX_PACKET_DATA = 32768

# class to read from a file and generate packet formated in TCP sim
class FilePacketReader:
    def __init__(self, filename, id):
        self._file = open(filename, "rb")
        self._id = id
        self._last_seq = 0
        self._is_done = False
        self._data = self._file.read(MAX_PACKET_DATA)
        if self._data == b'':
            self._is_done = True
        self._next_data = self._file.read(MAX_PACKET_DATA)
        if self._next_data == b'':
            self._file.close()
        self._create_packet()
    
    def _create_packet(self):
        self._packet = bytearray(7)
        if self._next_data == b'':
            self._packet[0] ^= 0x20
        self._packet[0] ^= self._id
        self._packet[1], self._packet[2] = int_to_bytes(self._last_seq)
        self._packet[3], self._packet[4] = int_to_bytes(len(self._data))
        self._packet[5], self._packet[6] = int_to_bytes(xor_all(self._packet[:5] + self._data))
        self._packet += self._data

    # seq_number is 0-indexed number of packet that need to be sent
    def read(self, seq_number):
        if self._is_done:
            return bytearray(b'')
        if self._file.closed:
            self._is_done = True
            return self._packet
        if seq_number == self._last_seq + 1:
            self._data = self._next_data
            self._next_data = self._file.read(MAX_PACKET_DATA)
            self._last_seq += 1
            if self._next_data == b'':
                self._file.close()
            self._create_packet()
        return self._packet

    def check_ack(self, packet):
        if len(packet) != 7:
            return False
        if packet[0] & 0x10 == 0:
            return False
        if self._is_done ^ bool(packet[0] & 0x20 == 0):
            return False
        if packet[0] & 0x11 != self._id:
            return False
        if self._last_seq != bytes_to_int(packet[1], packet[2]):
            return False
        if packet[3] or packet[4]:
            return False
        if xor_all(packet[:5] + self._data) != bytes_to_int(packet[5], packet[6]):
            return False
        return True
    


class FilePacketWriter:
    def __init__(self, filename, id):
        self._file = open(filename, "wb")
        self._id = id
        self._last_seq = -1
        self._is_done = False

    def generate_ack(self):
        packet = bytearray(7)
        packet[0] ^= 0x10
        if self._is_done == b'':
            packet[0] ^= 0x20
        packet[0] ^= self._id
        packet[1], packet[2] = int_to_bytes(self._last_seq)
        packet[3], packet[4] = int_to_bytes(0)
        packet[5], packet[6] = int_to_bytes(xor_all(packet[:5] + self._data))
        return packet

    def _check_packet(self):
        self._data = self._packet[7:]
        length = self._packet[3:5]
        sequence_n = self._packet[1:3]
        true_xor_val = self._packet[5:7]
        if true_xor_val == bytearray(int_to_bytes(xor_all(self._packet[:5] + self._data))) and \
            (sequence_n == bytearray(int_to_bytes(self._last_seq)) or \
            sequence_n == bytearray(int_to_bytes(self._last_seq + 1))) and \
            length == bytearray(int_to_bytes(len(self._data))):
            return True
        else:
            return False

    def write(self, packet):
        self._packet = packet
        if not self._check_packet() or self._is_done:
            return False
        if self._packet[1:3] == self._last_seq:
            return True
        types, _ = int_to_bytes(packet[0])
        self._file.write(self._data)
        self._last_seq = self._packet[1:3]
        if types == 0x02:
            self._file.close()
            self._is_done = True
        return True
    
    def get_last_seq(self):
        return self._last_seq

if __name__ == "__main__":
    a = FilePacketReader("test_file.dat", 0)
    b = FilePacketWriter("test_file_2.dat", 0)
    for i in range(100):
        packet = a.read(i)
        if not b.write(packet):
            break
        print(packet)
