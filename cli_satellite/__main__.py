import base64
from cli_satellite import JarbasCliTerminal, platform, logger
from twisted.internet import reactor, ssl


def connect_to_hivemind(host="127.0.0.1",
                        port=5678, name="Jarbas Cli Terminal",
                        api="cli_key", useragent=platform):
    authorization = bytes(name + ":" + api, encoding="utf-8")
    usernamePasswordDecoded = authorization
    api = base64.b64encode(usernamePasswordDecoded)
    headers = {'authorization': api}
    address = u"wss://" + host + u":" + str(port)
    logger.info("[INFO] connecting to hive mind at " + address)
    terminal = JarbasCliTerminal(address, headers=headers,
                                 useragent=useragent)
    contextFactory = ssl.ClientContextFactory()
    reactor.connectSSL(host, port, terminal, contextFactory)
    reactor.run()


if __name__ == '__main__':
    # TODO argparse
    connect_to_hivemind()
