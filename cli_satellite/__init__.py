import json
from threading import Thread
from time import sleep
from jarbas_hive_mind.slave.terminal import HiveMindTerminalProtocol, HiveMindTerminal
from jarbas_utils.log import LOG

platform = "JarbasCliTerminalV0.2"


class JarbasCliTerminalProtocol(HiveMindTerminalProtocol):
    waiting = False

    def onOpen(self):
        LOG.info("WebSocket connection open. ")
        self.input_loop = Thread(target=self.get_cli_input)
        self.input_loop.setDaemon(True)
        self.input_loop.start()

    def onMessage(self, payload, isBinary):
        if not isBinary:
            payload = payload.decode("utf-8")
            msg = json.loads(payload)
            if msg.get("type", "") == "speak":
                utterance = msg["data"]["utterance"]
                print('\x1b[6;34;40m MYCROFT: ' + utterance + ' \x1b[0m')
                LOG.info("[SPEAK] " + utterance)
            elif msg.get("type", "") == "hive.complete_intent_failure":
                LOG.error("complete intent failure")
            elif msg.get("type", "") == "mycroft.skill.handler.complete":
                LOG.debug("Request handled")
                self.waiting = False
        else:
            pass

    # cli input thread
    def get_cli_input(self):
        while True:
            if self.waiting:
                sleep(0.3)
                continue
            LOG.info("waiting for input")
            line = input("\x1b[6;33;40m INPUT: \x1b[0m")
            LOG.info("[UTTERANCE] " + line)
            msg = {"data": {"utterances": [line], "lang": "en-us"},
                   "type": "recognizer_loop:utterance",
                   "context": {"source": self.peer,
                               "destination": "hive_mind",
                               "platform": platform}}
            msg = json.dumps(msg)
            msg = bytes(msg, encoding="utf-8")
            self.sendMessage(msg, False)
            self.waiting = True
            print('\x1b[6;33;40m YOU: ' + line + ' \x1b[0m')


class JarbasCliTerminal(HiveMindTerminal):
    protocol = JarbasCliTerminalProtocol
