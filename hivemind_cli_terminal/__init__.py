from threading import Thread

from mycroft_bus_client import Message

from hivemind_bus_client import HiveMessageBusClient

try:
    from curses import wrapper
    import curses
except ImportError:
    print("WARNING: curses interface not available")
    curses = None


class JarbasCliTerminal(Thread):
    platform = "JarbasCliTerminalV0.4"

    def __init__(self, access_key=None,
                 host="wss://127.0.0.1",
                 port=5678,
                 crypto_key=None,
                 self_signed=False,
                 lang="en-us", bus=None):
        super().__init__()
        self.lang = lang

        if bus:
            # got a connection already
            self.bus = bus
        else:
            # connect to hivemind
            self.bus = HiveMessageBusClient(key=access_key,
                                            port=port,
                                            host=host,
                                            crypto_key=crypto_key,
                                            ssl=host.startswith("wss:"),
                                            useragent=self.platform,
                                            self_signed=self_signed,
                                            debug=False)

            self.bus.run_in_thread()
            # block until hivemind connects
            print("Waiting for Hivemind connection")
            self.bus.connected_event.wait()

        self.bus.on_mycroft("speak", self.handle_speak)

    # terminal
    def say(self, utterance):
        self.bus.emit(Message("recognizer_loop:utterance",
                              {"utterances": [utterance],
                               "lang": self.lang}))

    def speak(self, utterance):
        print(" Mycroft:", utterance)

    def run(self):
        print("ask mycroft:")
        while True:
            utterance = input()
            self.say(utterance)

    def handle_speak(self, message):
        utterance = message.data["utterance"]
        self.speak(utterance)


if curses is None:
    JarbasCursesTerminal = JarbasCliTerminal
else:

    class JarbasCursesTerminal(JarbasCliTerminal):
        platform = "JarbasCursesTerminalV0.2"

        # terminal
        def speak(self, utterance):
            self.msg_box.addstr(f"Mycroft > {utterance} \n")
            self._refresh()

        def _refresh(self):
            self.header_box.refresh()
            self.msg_box.refresh()
            self.input_box.refresh()

        def _run_curses_gui(self, stdscr):
            curses.echo()
            lasty, lastx = stdscr.getmaxyx()
            self.input_box = curses.newwin(0, lastx, lasty - 3, 0)

            self.header_box = curses.newwin(lasty - 4, lastx, 0, 0)
            self.header_box.addstr(f"=== {self.platform} ===")

            self.msg_box = curses.newwin(lasty - 4, lastx, 1, 0)
            self.msg_box.scrollok(True)

            while True:
                self._refresh()
                self.input_box.addstr("Input > ")
                msg = self.input_box.getstr()
                self._refresh()
                if msg:
                    utterance = str(msg.decode("utf-8"))
                    self.msg_box.addstr("You > " + utterance + "\n")
                    self.say(utterance)
                self.input_box.clear()

        def run(self):
            wrapper(self._run_curses_gui)
