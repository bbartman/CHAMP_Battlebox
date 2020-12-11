# import asyncio, time, serial_asyncio, serial
import serial, time, sys
from serial.threaded import LineReader, ReaderThread

class PrintLines(LineReader):
    def connection_made(self, transport):
        super(PrintLines, self).connection_made(transport)
        sys.stdout.write('port opened\n')
        self.write_line('hello world')

    def handle_line(self, data):
        sys.stdout.write('line received: {}\n'.format(repr(data)))

    def connection_lost(self, exc):
        if exc:
            traceback.print_exc(exc)
        sys.stdout.write('port closed\n')

ser = serial.Serial("/dev/ttyUSB0", baudrate=56700, timeout=1)
with ReaderThread(ser, PrintLines) as protocol:
  time.sleep(2)
  protocol.write_line("<pixels.reset, 3, 3>")
  STOP_LIGHT_RED = (255, 0, 0)
  STOP_LIGHT_ORANGE =	(0, 0, 150)
  STOP_LIGHT_YELLOW = (239, 200, 0)
  STOP_LIGHT_GREEN = (0, 132, 80)
  protocol.write_line("<pixels.setBrightness, 255><pixels.fill, {0}, {1}, {2}, 0><pixels.show>".format(*[int(x) for x in STOP_LIGHT_ORANGE]))
  time.sleep(2)
  STOP_LIGHT_RED = ()
  protocol.write_line("<pixels.clear><pixels.show>")
  time.sleep(2)

# class Output(asyncio.Protocol):
#     def connection_made(self, transport):
#         self.transport = transport
#         print('port opened', transport)
#         # transport.serial.rts = False  # You can manipulate Serial object via transport
#         # transport.write(b'Hello, World!\n')  # Write serial data via transport

#     def data_received(self, data):
#         print('data received', repr(data))
#         if b'\n' in data:
#             self.transport.close()

#     def connection_lost(self, exc):
#         print('port closed')
#         self.transport.loop.stop()

#     def pause_writing(self):
#         print('pause writing')
#         print(self.transport.get_write_buffer_size())

#     def resume_writing(self):
#         print(self.transport.get_write_buffer_size())
#         print('resume writing')

# loop = asyncio.get_event_loop()
# coro = serial_asyncio.create_serial_connection(loop, Output, '/dev/ttyUSB0', baudrate=9600, timeout=3)
# loop.run_until_complete(coro)
# # print(coro())
# # loop.run_forever()
# coro.write_line("<pixel.fill, 255, 0, 0, 4><pixel.show>")
# time.sleep(1)
# coro.write_line("<pixel.clear><pixel.show>")
# loop.close()
