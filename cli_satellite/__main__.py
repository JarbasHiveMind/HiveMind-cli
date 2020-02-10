from cli_satellite import JarbasCliTerminal, platform
from jarbas_hive_mind import HiveMindConnection


def connect_to_hivemind(host="wss://127.0.0.1",
                        port=5678, name="JarbasCliTerminal",
                        key="cli_key", crypto_key="rh6K5q0FBiCzT5Wg",
                        useragent=platform):
    con = HiveMindConnection(host, port)

    terminal = JarbasCliTerminal(con.address,
                                 crypto_key=crypto_key,
                                 headers=con.get_headers(name, key),
                                 useragent=useragent)

    con.connect(terminal)


if __name__ == '__main__':
    # TODO argparse
    connect_to_hivemind()
