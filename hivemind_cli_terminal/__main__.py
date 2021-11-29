from hivemind_cli_terminal import JarbasCliTerminal, JarbasCursesTerminal


def connect_to_hivemind(access_key,
                        host="wss://127.0.0.1",
                        port=5678,
                        crypto_key=None,
                        curses=False):
    if curses:
        terminal = JarbasCursesTerminal(access_key,
                                        host=host,
                                        port=port,
                                        self_signed=True,
                                        crypto_key=crypto_key)
    else:
        terminal = JarbasCliTerminal(access_key,
                                     host=host,
                                     port=port,
                                     self_signed=True,
                                     crypto_key=crypto_key)
    # this is a thread, can be set as a daemon
    terminal.start()


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--access_key", help="access key")
    parser.add_argument("--crypto_key", help="payload encryption key", default=None)
    parser.add_argument("--host", help="HiveMind host", default="wss://127.0.0.1")
    parser.add_argument("--port", help="HiveMind port number", default=5678)
    parser.add_argument("--curses", help="use curses interface", default=True)

    args = parser.parse_args()

    connect_to_hivemind(host=args.host,
                        port=args.port,
                        access_key=args.access_key,
                        crypto_key=args.crypto_key,
                        curses=args.curses)


if __name__ == '__main__':
    main()
