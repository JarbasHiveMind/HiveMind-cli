from hivemind_presence import LocalDiscovery
from hivemind_cli_terminal import JarbasCliTerminal, JarbasCursesTerminal


def connect_to_hivemind(access_key=None,
                        host="ws://127.0.0.1",
                        port=5678,
                        password=None,
                        curses=False,
                        self_signed=False,
                        bus=None):
    if curses:
        terminal = JarbasCursesTerminal(access_key,
                                        host=host,
                                        port=port,
                                        self_signed=self_signed,
                                        password=password,
                                        bus=bus)
    else:
        terminal = JarbasCliTerminal(access_key,
                                     host=host,
                                     port=port,
                                     self_signed=self_signed,
                                     password=password,
                                     bus=bus)
    # this is a thread, can be set as a daemon
    terminal.start()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--access-key", help="access key", required=True)
    parser.add_argument("--password", help="password", default=None)
    parser.add_argument("--host", help="HiveMind host")
    parser.add_argument("--port", help="HiveMind port number (default 5678)", default=5678)
    parser.add_argument("--no-curses", help="do not use curses interface", action="store_true")
    parser.add_argument("--self-signed", help="accept self sigyned ssl certificates", action="store_true")

    args = parser.parse_args()

    if not args.host:
        print("You did not specify a host to connect")
        scan = input("scan for node and attempt to connect? y/n: ")
        if not scan.lower().startswith("y"):
            print("Scan aborted and host not specified, exiting")
            exit(2)
        scanner = LocalDiscovery()
        for node in scanner.scan():
            print("Found HiveMind node: ", node.address)
            try:
                bus = node.connect(args.access_key, args.password,
                                   useragent=JarbasCliTerminal.platform,
                                   self_signed=args.self_signed)
                scanner.stop()
                connect_to_hivemind(curses=not args.no_curses, bus=bus)
            except:
                print("failed to connect!")
        exit(2)
    elif not args.host.startswith("ws"):
        print("Invalid host, please specify a protocol")
        print(f"ws://{args.host} or wss://{args.host}")
        exit(1)
    connect_to_hivemind(host=args.host,
                        port=args.port,
                        access_key=args.access_key,
                        password=args.password,
                        self_signed=args.self_signed,
                        curses=not args.no_curses)


if __name__ == '__main__':
    main()
