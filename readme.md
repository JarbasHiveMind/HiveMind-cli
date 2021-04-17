# HiveMind - Mycroft Command Line Chat

Command line client for [Mycroft HiveMind](https://github.com/JarbasSkills/skill-hivemind)

![](./cli_terminal.png)
![](./remote_cli.png)

## Install

```bash
$ pip install HiveMind-cli
```
## Usage

If host is not provided auto discovery will be used

```bash
$ HiveMind-cli --help

usage: HiveMind-cli [-h] [--access_key ACCESS_KEY] [--crypto_key CRYPTO_KEY]
                   [--name NAME] [--host HOST] [--port PORT] [--curses CURSES]

optional arguments:
  -h, --help            show this help message and exit
  --access_key ACCESS_KEY
                        access key
  --crypto_key CRYPTO_KEY
                        payload encryption key
  --name NAME           human readable device name
  --host HOST           HiveMind host
  --port PORT           HiveMind port number
  --curses CURSES       use curses interface
```
