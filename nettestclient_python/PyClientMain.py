import os
import argparse
import json
import random
import sys
import time
import traceback

import websocket
from websocket import WebSocketApp


from command.handle.HandlePriority import HandlePriority
from command.handle.handleFactory import HandleFactory
from command.handle.handleSelfCmds import HandleSelfCmds
from command.interfaces.netSend import NetSend
from command.event.EventPacketText import EventPacketText
from command.event.eventPacketBinary import EventPacketBinary
from command.cmd.text.packetCmd import PacketCmd as PacketCmdText
from command.cmd.binary.packetCmd import PacketCmd as PacketCmdTBinary
from common.ledControl import LedControl
from config.config import Config
from expand.logDecorator.logDecoretor import LoggerPrint, CustomLogger


class WebsocketMain(NetSend):
    def __init__(self, config:Config) -> None:
        super().__init__()
        dirname, _ = os.path.split(os.path.abspath(sys.argv[0]))
        # sys.stdout = LoggerPrint(os.path.join(dirname, "Data", "Debug"))
        sys.stdout = CustomLogger(os.path.join(dirname, "Data", "Debug"))
        print("new WebsocketMain")
        self.url = config.settings["WebSocketUrl"]
        self.ws = None
        self.handle_factory = HandleFactory()
        self.handle_selfCmds = HandleSelfCmds()
        self.handle_priority = HandlePriority()
        self.connected = False

    def isConnect(self) -> bool:
        print(f"current connect:{self.connected}")
        return self.connected

    def sendMessage(self, text: str) -> bool:
        try:
            if not self.connected:
                return False
            self.ws.send(text)
            return True
        except Exception as e:
            print(e)
            return False

    def sendData(self, buf: bytes) -> bool:
        try:
            if not self.connected:
                return False
            self.ws.send(buf, websocket.ABNF.OPCODE_BINARY)
            return True
        except Exception as e:
            print(e)

    def on_message(self, ws, message):
        try:
            # print(f"message:{message}")
            if type(message) is str:
                print(f"message:{message}")
            packet_event = self.getPcket_event(message)
            if self.handle_priority.instances:
                if self.handle_priority.handle_instance(packet_event):
                    return
            process = self.handle_factory.getHandle(self)
            process.handle(packet_event)
        except Exception as e:
            text = f"on message error:{traceback.format_exc()}"
            print(text)

    def getPcket_event(self, message):
        if isinstance(message, str):
            cmd = PacketCmdText.parse(message)
            packet_event = EventPacketText("packet", cmd)
        elif isinstance(message, bytes):
            cmd = PacketCmdTBinary.parse(message)
            packet_event = EventPacketBinary("packet", cmd)
        else:
            return None
        return packet_event

    def on_error(self, ws, error):
        print(f"error:{error}")
        self.connected = False
        if self.handle_priority.instances:
            if self.handle_priority.handle_instance(packet_event):
                return

    def on_close(self, ws, code, message):
        print(f"on close,code = {code},{message}")
        self.connected = False

    def on_ping(self, ws, message):
        pass

    def on_pong(self, ws, message):
        pass

    def on_open(self, ws):
        self.ws = ws
        self.connected = True

    def start(self):
        while 1:
            try:
                print("connect server")
                self.ws = WebSocketApp(self.url, on_close=self.on_close, on_open=self.on_open, on_message=self.on_message,
                                       on_error=self.on_error, on_ping=self.on_ping, on_pong=self.on_pong)
                self.ws.run_forever(ping_interval=20, ping_timeout=10)
                print("connect server Network error")
                LedControl.offline()
                randome_time = random.randint(10, 15)
                print(f"{str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))}:无法连接服务器,{randome_time}s后重新连接")
                time.sleep(randome_time)
            except Exception as e:
                print(f"connect server error:{str(e)}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-ip", help="severs ip")
    pr = parser.parse_args()
    ip = pr.ip
    try:
        if ip:
            cfg = "config/appsettings.json"
            with open(cfg, "r") as f:
                info = json.loads(f.read())
            with open(cfg, "w") as f:
                info["WebSocketUrl"] = f"ws://{ip}/api/Server/connect"
                json.dump(info, f, indent=4)
    except Exception as e:
        raise e
    config = Config()
    WebsocketMain(config).start()

