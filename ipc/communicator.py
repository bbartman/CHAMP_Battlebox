import socket
import asyncio
import aiohttp
import sys
import os
from kivy.config import Config
from kivy.logger import Logger

class InstructionServer:
    def _remove_prev_socket(self, addr):
        try:
            os.unlink(addr)
        except OSError:
            if os.path.exists(addr):
                raise

    def __init__(self, path, on_ready_cb):
        self.path = path
        self._on_ready = on_ready_cb
        self._remove_prev_socket(self.path)
        self._connections = []

    async def send_to_all(self, message):
        Logger.info("Sending to everyone!")
        for s in self._connections:
            s.write(bytes(message+"\n", encoding="UTF-8"))

    async def on_connection(self, reader, writer):
        try:
            self._connections.append(writer)
            while True:
                line = await reader.readline()
                if not line:
                    Logger.info('Instruction Server->on_connection: Disconnecting from writer')
                    break
                line = line.decode('UTF-8').rstrip()
                if line:
                    Logger.info(f'Instruction Server->on_connection: Response {line}')
                if line == "ready":
                    self._on_ready(line)
            self._connections.remove(writer)
        except asyncio.CancelledError:
            self._connections.remove(writer)
            Logger.info("Instruction Server->on_connection: Coroutine cancelled.")
            return

    async def run_server(self):
        try:
            Logger.info(f"Instruction Server: Launching server on {self.path}")
            self.server = await asyncio.start_unix_server(self.on_connection, self.path)
            addr = self.server.sockets[0].getsockname()
            Logger.info(f'Instruction Server: Serving on {addr}')
            async with self.server:
                await self.server.serve_forever()

        except asyncio.CancelledError:
            Logger.info("Instruction Server: Coroutine cancelled.")
            await self.server.wait_closed()
            Logger.info("Instruction Server: Sever closed.")


async def connect_to_main_server(path, on_instruction_received_cb):
    try:
        Logger.info(f"connect_to_main_server: attempting to connect to main server {path}")
        assert on_instruction_received_cb is not None, "Missing callback"
        reader, writer = await asyncio.open_unix_connection(path)
        Logger.info(f"connect_to_main_server: connection to main server established")
        writer.write(bytes("ready\n", encoding='UTF-8'))
        await writer.drain()
        while True:
            line = await reader.readline()
            if not line:
                Logger.info('connect_to_main_server: Disconnected from server')
                break

            line = line.decode('UTF-8').rstrip()
            on_instruction_received_cb(line)
    except asyncio.CancelledError:
        Logger.info('connect_to_main_server: Connection cancelled.')
        writer.close()