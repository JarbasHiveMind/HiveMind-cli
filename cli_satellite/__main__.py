from cli_satellite import JarbasCliTerminal, platform
from jarbas_hive_mind import HiveMindConnection
from jarbas_hive_mind.discovery import LocalDiscovery
from jarbas_utils.log import LOG


def connect_to_hivemind(host="wss://127.0.0.1",
                        port=5678, name="JarbasCliTerminal",
                        key="dummy_key", crypto_key=None,
                        useragent=platform):
    con = HiveMindConnection(host, port)

    terminal = JarbasCliTerminal(con.address,
                                 crypto_key=crypto_key,
                                 headers=con.get_headers(name, key),
                                 useragent=useragent)

    con.connect(terminal)


def discover_hivemind():

    discovery = LocalDiscovery()
    dont_have_key = []
    headers = HiveMindConnection.get_headers(name, key)

    while True:
        for node_url in discovery.scan():
            if node_url in dont_have_key:
                continue
            LOG.info("Fetching Node data: {url}".format(url=node_url))
            node = discovery.nodes[node_url]
            node.connect(crypto_key=crypto_key,
                         node_type=JarbasCliTerminal,
                         headers=headers
                         )
            dont_have_key.append(node_url)


if __name__ == '__main__':
    # TODO arg parse
    key = "dummy_key"
    name = "JarbasCliTerminal"
    crypto_key = None

    ### Auto discovery
    discover_hivemind()

    # Direct Connection
    #connect_to_hivemind(host, port, name=name, key=dummy_key, crypto_key=crypto_key)
