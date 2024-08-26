from microbit import *

HEADER_0 = 0x55
HEADER_1 = 0xAA
ADDRESS = 0x11
FRAME_BUFFER_SIZE = 128
HEADER_0_INDEX = 0
HEADER_1_INDEX = 1
ADDRESS_INDEX = 2
CONTENT_SIZE_INDEX = 3
COMMAND_INDEX = 4
CONTENT_INDEX = 5
PROTOCOL_SIZE = 6

COMMAND_REQUEST = 0x20
COMMAND_RETURN_INFO = 0x29
COMMAND_RETURN_FRAME = 0x2A
COMMAND_RETURN_ARROW = 0x2B

class HuskyLens:
    def __init__(self):
        self.protocol_ptr = [[0] * 6 for _ in range(10)]
        self.protocol_t = [0] * 6
        self.send_index = 0
        self.receive_index = 0
        self.receive_buffer = [0] * FRAME_BUFFER_SIZE
        self.send_buffer = [0] * FRAME_BUFFER_SIZE
        self.send_fail = False
        self.receive_fail = False
        self.content_current = 0
        self.content_end = 0
        self.content_read_end = False
        self.time_out_duration = 100
        self.time_out_timer = 0

    def validate_checksum(self):
        stack_sum_index = self.receive_buffer[CONTENT_SIZE_INDEX] + CONTENT_INDEX
        hk_sum = sum(self.receive_buffer[:stack_sum_index]) & 0xff
        return hk_sum == self.receive_buffer[stack_sum_index]

    def husky_lens_protocol_write_end(self):
        if self.send_fail:
            return 0
        if self.send_index + 1 >= FRAME_BUFFER_SIZE:
            return 0
        self.send_buffer[CONTENT_SIZE_INDEX] = self.send_index - CONTENT_INDEX
        hk_sum = sum(self.send_buffer[:self.send_index]) & 0xff
        self.send_buffer[self.send_index] = hk_sum
        self.send_index += 1
        return self.send_index

    def husky_lens_protocol_write_begin(self, command=0):
        self.send_fail = False
        self.send_buffer[HEADER_0_INDEX] = HEADER_0
        self.send_buffer[HEADER_1_INDEX] = HEADER_1
        self.send_buffer[ADDRESS_INDEX] = ADDRESS
        self.send_buffer[COMMAND_INDEX] = command
        self.send_index = CONTENT_INDEX
        return self.send_buffer

    def protocol_write(self, buffer):
        i2c.write(0x32, bytearray(buffer), False)

    def process_return(self):
        if not self.wait(COMMAND_RETURN_INFO):
            return False
        self.protocol_read_five_int16(COMMAND_RETURN_INFO)
        for i in range(self.protocol_t[1]):
            if not self.wait():
                return False
            if self.protocol_read_five_int161(i, COMMAND_RETURN_FRAME):
                continue
            elif self.protocol_read_five_int161(i, COMMAND_RETURN_ARROW):
                continue
            else:
                return False
        return True

    def wait(self, command=0):
        self.timer_begin()
        while not self.timer_available():
            if self.protocol_available():
                if command:
                    if self.husky_lens_protocol_read_begin(command):
                        return True
                else:
                    return True
            else:
                return False
        return False

    def husky_lens_protocol_read_begin(self, command=0):
        if command == self.receive_buffer[COMMAND_INDEX]:
            self.content_current = CONTENT_INDEX
            self.content_read_end = False
            self.receive_fail = False
            return True
        return False

    def timer_begin(self):
        self.time_out_timer = running_time()

    def timer_available(self):
        return running_time() - self.time_out_timer > self.time_out_duration

    def protocol_available(self):
        buf = i2c.read(0x32, 16, False)
        for i in range(16):
            if self.husky_lens_protocol_receive(buf[i]):
                return True
        return False

    def husky_lens_protocol_receive(self, data):
        if self.receive_index == HEADER_0_INDEX:
            if data != HEADER_0:
                self.receive_index = 0
                return False
            self.receive_buffer[HEADER_0_INDEX] = HEADER_0
        elif self.receive_index == HEADER_1_INDEX:
            if data != HEADER_1:
                self.receive_index = 0
                return False
            self.receive_buffer[HEADER_1_INDEX] = HEADER_1
        elif self.receive_index == ADDRESS_INDEX:
            self.receive_buffer[ADDRESS_INDEX] = data
        elif self.receive_index == CONTENT_SIZE_INDEX:
            if data >= FRAME_BUFFER_SIZE - PROTOCOL_SIZE:
                self.receive_index = 0
                return False
            self.receive_buffer[CONTENT_SIZE_INDEX] = data
        else:
            self.receive_buffer[self.receive_index] = data
            if self.receive_index == self.receive_buffer[CONTENT_SIZE_INDEX] + CONTENT_INDEX:
                self.content_end = self.receive_index
                self.receive_index = 0
                return self.validate_checksum()
        self.receive_index += 1
        return False

    def husky_lens_protocol_write_int16(self, content):
        x = len(str(content))
        if self.send_index + x >= FRAME_BUFFER_SIZE:
            self.send_fail = True
            return
        self.send_buffer[self.send_index] = content & 0xff
        self.send_buffer[self.send_index + 1] = (content >> 8) & 0xff
        self.send_index += 2

    def protocol_read_five_int16(self, command=0):
        if self.husky_lens_protocol_read_begin(command):
            self.protocol_t[0] = command
            self.protocol_t[1] = self.husky_lens_protocol_read_int16()
            self.protocol_t[2] = self.husky_lens_protocol_read_int16()
            self.protocol_t[3] = self.husky_lens_protocol_read_int16()
            self.protocol_t[4] = self.husky_lens_protocol_read_int16()
            self.protocol_t[5] = self.husky_lens_protocol_read_int16()
            self.husky_lens_protocol_read_end()
            return True
        return False

    def protocol_read_five_int161(self, i, command=0):
        if self.husky_lens_protocol_read_begin(command):
            self.protocol_ptr[i][0] = command
            self.protocol_ptr[i][1] = self.husky_lens_protocol_read_int16()
            self.protocol_ptr[i][2] = self.husky_lens_protocol_read_int16()
            self.protocol_ptr[i][3] = self.husky_lens_protocol_read_int16()
            self.protocol_ptr[i][4] = self.husky_lens_protocol_read_int16()
            self.protocol_ptr[i][5] = self.husky_lens_protocol_read_int16()
            self.husky_lens_protocol_read_end()
            return True
        return False

    def husky_lens_protocol_read_int16(self):
        if self.content_current >= self.content_end or self.content_read_end:
            self.receive_fail = True
            return 0
        result = self.receive_buffer[self.content_current + 1] << 8 | self.receive_buffer[self.content_current]
        self.content_current += 2
        return result

    def husky_lens_protocol_read_end(self):
        if self.receive_fail:
            self.receive_fail = False
            return False
        return self.content_current == self.content_end

    def count_learned_ids(self):
        return self.protocol_t[2]

    def count_frames(self):
        counter = 0
        for i in range(self.protocol_t[1]):
            if self.protocol_ptr[i][0] == COMMAND_RETURN_FRAME:
                counter += 1
        return counter

    def count_arrows(self):
        counter = 0
        for i in range(self.protocol_t[1]):
            if self.protocol_ptr[i][0] == COMMAND_RETURN_ARROW:
                counter += 1
        return counter

    def count_frames_id(self, ID):
        counter = 0
        for i in range(self.protocol_t[1]):
            if self.protocol_ptr[i][0] == COMMAND_RETURN_FRAME and self.protocol_ptr[i][5] == ID:
                counter += 1
        return counter

    def request_frames(self):
        self.husky_lens_protocol_write_begin(COMMAND_REQUEST)
        self.husky_lens_protocol_write_int16(COMMAND_RETURN_FRAME)
        self.husky_lens_protocol_write_end()
        self.protocol_write(self.send_buffer)
        if self.process_return() and self.count_frames() != 0:
            return {
                "frames": [
                    {"id": p[5], "x": p[1], "y": p[2], "width": p[3], "height": p[4]}
                    for p in self.protocol_ptr
                    if p[0] == COMMAND_RETURN_FRAME
                ]
            }
        else:
            return {"frames": []}

    def request_arrows(self):
        self.husky_lens_protocol_write_begin(COMMAND_REQUEST)
        self.husky_lens_protocol_write_int16(COMMAND_RETURN_ARROW)
        self.husky_lens_protocol_write_end()
        self.protocol_write(self.send_buffer)
        if self.process_return() and self.count_arrows() != 0:
            return {
                "arrows": [
                    {"id": p[5], "x1": p[1], "y1": p[2], "x2": p[3], "y2": p[4]}
                    for p in self.protocol_ptr
                    if p[0] == COMMAND_RETURN_ARROW
                ]
            }
        else:
            return {"arrows": []}

    def get_x_values(self):
        frames = self.request_frames().get("frames", [])
        return [frame["x"] for frame in frames]

    def get_y_values(self):
        frames = self.request_frames().get("frames", [])
        return [frame["y"] for frame in frames]
        
    def get_width_values(self):
        frames = self.request_frames().get("frames", [])
        return [frame["width"] for frame in frames]
        
    def get_height_values(self):
        frames = self.request_frames().get("frames", [])
        return [frame["height"] for frame in frames]

    def get_x1_values(self):
        arrows = self.request_arrows().get("arrows", [])
        return [frame["x1"] for frame in arrows]

    def get_y1_values(self):
        arrows = self.request_arrows().get("arrows", [])
        return [frame["y1"] for frame in arrows]

    def get_x2_values(self):
        arrows = self.request_arrows().get("arrows", [])
        return [frame["x2"] for frame in arrows]

    def get_y2_values(self):
        arrows = self.request_arrows().get("arrows", [])
        return [frame["y2"] for frame in arrows]
