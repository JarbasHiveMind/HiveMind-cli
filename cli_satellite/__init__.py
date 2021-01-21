from jarbas_hive_mind.slave.terminal import HiveMindTerminalProtocol, HiveMindTerminal
from ovos_utils.log import LOG
from ovos_utils import create_daemon
from ovos_utils.messagebus import Message
try:
    from curses import wrapper
    import curses
except ImportError:
    print("WARNING: curses interface not available")
    curses = None

from time import sleep


class JarbasCliTerminalProtocol(HiveMindTerminalProtocol):

    def onOpen(self):
        super().onOpen()
        create_daemon(self.factory.run_cli)


class JarbasCliTerminal(HiveMindTerminal):
    protocol = JarbasCliTerminalProtocol
    platform = "JarbasCliTerminalV0.3"

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
                               "platform": self.platform}}
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


if curses is None:
    JarbasCursesTerminalProtocol = JarbasCliTerminalProtocol
    JarbasCursesTerminal = JarbasCliTerminal
else:
    class JarbasCursesTerminalProtocol(HiveMindTerminalProtocol):

        def onOpen(self):
            super().onOpen()
            create_daemon(self.factory.run_curses)


    class JarbasCursesTerminal(JarbasCliTerminal):
        protocol = JarbasCursesTerminalProtocol
        platform = "JarbasCursesTerminalV0.1"

        # terminal
        def speak(self, utterance):
            self.msg_box.addstr(
                "Mycroft > {utterance} \n".format(utterance=utterance))

        def _run_curses_gui(self, stdscr):
            curses.echo()
            lasty, lastx = stdscr.getmaxyx()
            self.input_box = curses.newwin(0, lastx, lasty - 3, 0)

            self.header_box = curses.newwin(lasty - 4, lastx, 0, 0)
            self.header_box.addstr("=== {platform} ===".format(
                platform=self.platform))

            self.msg_box = curses.newwin(lasty - 4, lastx, 1, 0)
            self.msg_box.scrollok(True)

            def refresh():
                while True:
                    self.header_box.refresh()
                    self.msg_box.refresh()
                    self.input_box.refresh()
                    sleep(0.5)

            create_daemon(refresh)

            while True:
                self.input_box.addstr("Input > ")
                msg = self.input_box.getstr()
                if msg:
                    utterance = str(msg.decode("utf-8"))
                    self.msg_box.addstr("You > " + utterance + "\n")
                    msg = {"data": {"utterances": [utterance],
                                    "lang": "en-us"},
                           "type": "recognizer_loop:utterance",
                           "context": {"source": self.client.peer,
                                       "destination": "hive_mind",
                                       "platform": self.platform}}
                    self.send_to_hivemind_bus(msg)
                    self.waiting = True
                self.input_box.clear()

        def run_curses(self):
            wrapper(self._run_curses_gui)
