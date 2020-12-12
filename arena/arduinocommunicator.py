import serial, threading, queue, io, time
from datetime import datetime
from kivy.logger import Logger
from serial.threaded import LineReader, ReaderThread


class ArduinoCommunicator:
    def __init__(self, serialConnection):
        self.conn = serialConnection
        self.io = io.TextIOWrapper(io.BufferedRWPair(self.conn, self.conn))
        self.q = queue.Queue()
        self.ready_lock = threading.Lock()
        self._is_ready = False
        self.processing_thread = threading.Thread(target=self._do_send_receive)
        self.processing_thread.start()
    
    def _do_send_receive(self):
        t = threading.currentThread()
        while not self.is_ready:
            readyText = self.io.readline()
            if readyText == "ready\n":
                self.ready_lock.acquire()
                self._is_ready = True
                self.ready_lock.release()
                Logger.info("Received ready command from arduino")

        while getattr(t, "do_run", True):
            value = None
            try:
                value = self.q.get_nowait()
                if value == None:
                    continue
            except queue.Empty:
                continue
            if value == "":
                continue
            self.io.write(value + "\n")
            self.io.flush()
            receivedResponse = False
            while not receivedResponse and getattr(t, "do_run", True):
                value = self.io.readline()
                if value.startswith("OK"):
                    receivedResponse = True
                    continue
                if value.startswith("ERR:"):
                    receivedResponse = True
                    Logger.warning("Received error from arduiono " + value)

                if value.startswith("DEBUG:"):
                    pass
        
    def write_line(self, text):
        self.q.put_nowait(text)

    def stop(self):
        self.processing_thread.do_run = False
        self.processing_thread.join()
        self.io.write("pixels.clear\npixels.show\n")
        self.io.flush()
        
    @property
    def is_ready(self):
        with self.ready_lock:
            return self._is_ready