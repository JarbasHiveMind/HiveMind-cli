"""The terminal connects with its own identity (HIVEMIND-CRYPTO-1 §2)."""
from unittest.mock import MagicMock, patch

import hivemind_cli_terminal
from hivemind_cli_terminal import JarbasCliTerminal


def test_the_terminal_builds_its_client_with_its_own_identity():
    identity = MagicMock()
    with patch.object(hivemind_cli_terminal, "NodeIdentity", return_value=identity) as ctor, \
         patch.object(hivemind_cli_terminal, "HiveMessageBusClient") as client:
        JarbasCliTerminal("k", password="p")
    ctor.assert_called_once_with(app_name="hivemind-cli")
    assert client.call_args.kwargs["identity"] is identity


def test_a_given_identity_is_used_as_is():
    identity = MagicMock()
    with patch.object(hivemind_cli_terminal, "NodeIdentity") as ctor, \
         patch.object(hivemind_cli_terminal, "HiveMessageBusClient") as client:
        JarbasCliTerminal("k", password="p", identity=identity)
    ctor.assert_not_called()
    assert client.call_args.kwargs["identity"] is identity
