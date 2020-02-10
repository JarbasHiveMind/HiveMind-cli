from time import sleep
from jarbas_hive_mind.slave.terminal import HiveMindTerminalProtocol, HiveMindTerminal
from jarbas_utils.log import LOG
from jarbas_utils import create_daemon
from jarbas_utils.messagebus import Message

platform = "JarbasCliTerminalV0.2"


class JarbasCliTerminalProtocol(HiveMindTerminalProtocol):

    def onOpen(self):
        super().onOpen()
        create_daemon(self.factory.get_cli_input)


class JarbasCliTerminal(HiveMindTerminal):
    protocol = JarbasCliTerminalProtocol

    def __init__(self, colors=True, debug=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = colors
        self.debug = debug
        self.waiting = False

    # terminal
    def say(self, utterance):
        if self.debug:
            LOG.debug("[UTTERANCE] " + utterance)
        if self.color:
            print('\x1b[6;33;40m YOU: ' + utterance + ' \x1b[0m')
        else:
            print('YOU: ' + utterance)

    def speak(self, utterance):
        if self.debug:
            LOG.debug("[SPEAK] " + utterance)
        if self.color:
            print('\x1b[6;34;40m MYCROFT: ' + utterance + ' \x1b[0m')
        else:
            print('MYCROFT: ' + utterance)

    def on_handled(self):
        if self.debug:
            LOG.debug("Request handled")
        self.waiting = False

    def get_cli_input(self):
        while True:
            if self.waiting:
                sleep(0.3)
                continue
            if self.debug:
                LOG.debug("waiting for input")
            if self.color:
                line = input("\x1b[6;33;40m INPUT: \x1b[0m")
            else:
                line = input("INPUT:")
            self.say(line)

            msg = {"data": {"utterances": [line],
                            "lang": "en-us"},
                   "type": "recognizer_loop:utterance",
                   "context": {"source": self.client.peer,
                               "destination": "hive_mind",
                               "platform": platform}}
            self.send_to_hivemind_bus(msg)
            self.waiting = True

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

