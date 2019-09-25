import io

# bytearray -> int
# divide data into 16 bits chunks and xor all of them
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

# int -> int, int
# divide 16 bit integer into two 8 bit integers
def int_to_bytes(b):
    return b >> 8, b & 0xFF

# int, int -> int
# combine two 8 bit integers into 16 bit integer
def bytes_to_int(a, b):
    return (a << 8) | b

# bytearray -> int
# get the id number (between range 0 - 4) of a packet
def get_id(packet):
    if len(packet) < 7:
        return -1
    id = packet[0] & 0xF
    return id

# max data length in a single transport packet
MAX_PACKET_DATA = 32768


# class to read from filename, generate packets to sent over protocol, and verify ack
class FilePacketSender:
    # string, int
    def __init__(self, filename, id):
        self._file = open(filename, "rb")
        self._id = id
        self._read_seq = 0 # sequence number of self._data
        self._rcv_seq = -1 # sequence number of last confirmed ack
        self._is_done = False # the last data is confirmed
        self._data = bytes([len(filename)]) + filename.encode()
        self._data += self._file.read(MAX_PACKET_DATA - len(self._data))
        self._next_data = self._file.read(MAX_PACKET_DATA)
        if self._next_data == b'':
            self._file.close()
        self._create_packet()
    
    # None -> None
    # create self._packet based on self._data read from file
    def _create_packet(self):
        self._packet = bytearray(7)
        if self._file.closed:
            self._packet[0] ^= 0x20
        self._packet[0] ^= self._id
        self._packet[1], self._packet[2] = int_to_bytes(self._read_seq)
        self._packet[3], self._packet[4] = int_to_bytes(len(self._data))
        self._packet[5], self._packet[6] = int_to_bytes(xor_all(self._packet[:5] + self._data))
        self._packet += self._data

    # None -> None
    # read the next data in the file, check if all data are read
    def _read_next_data(self):
        if self._file.closed:
            self._is_done = True
        else:
            self._data = self._next_data
            self._next_data = self._file.read(MAX_PACKET_DATA)
            self._read_seq += 1
            if self._next_data == b'':
                self._file.close()
            self._create_packet()

    # None -> bytearray
    # return packet of first data not confirmed, if all packet is confirmed, return b''
    def send_packet(self):
        if self._is_done:
            return bytearray(b'')
        else:
            return self._packet.copy()

    # bytearray -> bool
    # check validity of ack based on last sent packet, change the value of rcv_seq
    def receive_ack(self, packet):
        if len(packet) < 7:
            return False
        types = packet[0] >> 4
        id = packet[0] & 0x0F
        seq_num = bytes_to_int(packet[1], packet[2])
        length = bytes_to_int(packet[3], packet[4])
        checksum = bytes_to_int(packet[5], packet[6])
        if types & 0x1 == 0x1 and (self._file.closed ^ bool(types & 0x2 == 0x0)) and \
            id == self._id and \
            seq_num == self._read_seq and \
            length == 0  and len(packet) == 7 and \
            checksum == xor_all(packet[:5]):
            self._rcv_seq += 1
            self._read_next_data()
            return True
        else:
            return False

    # None -> bool
    # check if all file read is already received
    def is_done(self):
        return self._is_done
    

# class to write to filename, verify packet received, and generate ack
class FilePacketReceiver:
    # string, id
    def __init__(self, packet):
        self._id = get_id(packet)
        filename_len = packet[7]
        self._filename = packet[8:8+filename_len].decode()
        self._file = open("rcv_" + self._filename, "wb")
        self._write_seq = -1 # packet sequence number of last writen data
        self._rcv_seq = -1 # packet sequence number of last received valid data
        self._is_done = False
        self._success = self.receive_packet(packet)

    # None -> bool
    # check whether received packet is valid or not
    def _check_packet(self, packet):
        if len(packet) < 7:
            return False
        self._types = packet[0] >> 4
        id = packet[0] & 0x0F
        seq_num = bytes_to_int(packet[1], packet[2])
        length = bytes_to_int(packet[3], packet[4])
        checksum = bytes_to_int(packet[5], packet[6])
        self._data = packet[7:]
        if self._types & 0x1 == 0x0 and \
            id == self._id and \
            length == len(self._data) and \
            checksum == xor_all(packet[:5] + self._data):
            self._rcv_seq = seq_num
            return True
        else:
            return False

    # None -> bool
    # verify and write packet received
    def receive_packet(self, packet):
        if not self._check_packet(packet):
            self._success = False
            return False
        if bytes_to_int(packet[1], packet[2]) == 0:
            filename_len = self._data[0]
            self._data = self._data[filename_len+1:]
        if self._rcv_seq == self._write_seq + 1:
            self._file.write(self._data)
            self._write_seq += 1
            if self._types == 0x02:
                self._file.close()
                self._is_done = True
        self._success = True
        return True
    
    # None -> bytearray
    # generate ack for last data received
    def send_ack(self):
        packet = bytearray(7)
        packet[0] ^= 0x10
        if self._is_done == True:
            packet[0] ^= 0x20
        packet[0] ^= self._id
        packet[1], packet[2] = int_to_bytes(self._rcv_seq)
        packet[3], packet[4] = int_to_bytes(0)
        packet[5], packet[6] = int_to_bytes(xor_all(packet[:5]))
        return packet

    def write_seq(self):
        return self._write_seq

    def rcv_seq(self):
        return self._rcv_seq

    def is_done(self):
        return self._is_done
        
    def filename(self):
        return self._filename

    def success(self):
        return self._success