from jarbas_hive_mind.slave.terminal import HiveMindTerminalProtocol, HiveMindTerminal
from jarbas_utils.log import LOG
from jarbas_utils import create_daemon
from jarbas_utils.messagebus import Message
from time import sleep


platform = "JarbasCliTerminalV0.3"


class JarbasCliTerminalProtocol(HiveMindTerminalProtocol):

    def onOpen(self):
        super().onOpen()
        create_daemon(self.factory.run_cli)


class JarbasCliTerminal(HiveMindTerminal):
    protocol = JarbasCliTerminalProtocol

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.waiting = False
        self.debug = kwargs.get("debug", False)

    # terminal
    def speak(self, utterance):
        print("Mycroft:", utterance)

    def on_handled(self):
        if self.debug:
            print("DEBUG: Intent handling finished")
        self.waiting = False

    def run_cli(self):
        while True:
            utterance = input("Input:")
            msg = {"data": {"utterances": [utterance],
                            "lang": "en-us"},
                   "type": "recognizer_loop:utterance",
                   "context": {"source": self.client.peer,
                               "destination": "hive_mind",
                               "platform": platform}}
            self.send_to_hivemind_bus(msg)
            self.waiting = True
            if self.debug:
                print("DEBUG: Waiting for Intent handling, BLOCKING HERE")
            while self.waiting:
                sleep(0.5)

    # parsed protocol messages
    def handle_incoming_mycroft(self, message):
        assert isinstance(message, Message)
        if message.msg_type == "speak":
            utterance = message.data["utterance"]
            self.speak(utterance)
        elif message.msg_type == "hive.complete_intent_failure":
            LOG.error("complete intent failure")
            self.speak('I don\'t know how to answer that')
        elif message.msg_type == "mycroft.skill.handler.complete":
            self.on_handled()

