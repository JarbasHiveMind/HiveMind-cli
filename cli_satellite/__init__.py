import json
import logging
import sys
from threading import Thread

from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol
from twisted.internet.protocol import ReconnectingClientFactory

platform = "JarbasCliTerminalv0.1"
logger = logging.getLogger(platform)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel("INFO")


class JarbasCliTerminalProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        logger.info("[INFO] Server connected: {0}".format(response.peer))
        self.factory.client = self
        self.factory.status = "connected"

    def onOpen(self):
        logger.info("[INFO] WebSocket connection open. ")
        self.input_loop = Thread(target=self.get_cli_input)
        self.input_loop.setDaemon(True)
        self.input_loop.start()

    def onMessage(self, payload, isBinary):
        if not isBinary:
            payload = payload.decode("utf-8")
            msg = json.loads(payload)
            if msg.get("type", "") == "speak":
                utterance = msg["data"]["utterance"]
                logger.info("[OUTPUT] " + utterance)
            elif msg.get("type", "") == "hive.complete_intent_failure":
                logger.error("[ERROR] complete intent failure")
        else:
            pass

    def onClose(self, wasClean, code, reason):
        logger.info("[INFO] WebSocket connection closed: {0}".format(reason))
        self.factory.client = None
        self.factory.status = "disconnected"
        if "Internalservererror:InvalidAPIkey" in reason:
            logger.error("[ERROR] invalid user:key provided")
            raise ConnectionAbortedError("invalid user:key provided")

    # cli input thread
    def get_cli_input(self):
        logger.info("[INFO] waiting for input")
        while True:
            line = input("")
            msg = {"data": {"utterances": [line], "lang": "en-us"},
                   "type": "recognizer_loop:utterance",
                   "context": {"source": self.peer,
                               "destination": "hive_mind",
                               "platform": platform}}
            msg = json.dumps(msg)
            msg = bytes(msg, encoding="utf-8")
            self.sendMessage(msg, False)


class JarbasCliTerminal(WebSocketClientFactory, ReconnectingClientFactory):
    protocol = JarbasCliTerminalProtocol

    def __init__(self, *args, **kwargs):
        super(JarbasCliTerminal, self).__init__(*args, **kwargs)
        self.status = "disconnected"
        self.client = None

    # websocket handlers
    def clientConnectionFailed(self, connector, reason):
        logger.info("[INFO] Client connection failed: " + str(
            reason) + " .. retrying ..")
        self.status = "disconnected"
        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        logger.info("[INFO] Client connection lost: " + str(
            reason) + " .. retrying ..")
        self.status = "disconnected"
        self.retry(connector)

