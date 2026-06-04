"""ACL policy-admission e2e tests for HiveMind-cli.

Three enforcement paths from the new PolicyChain model
(MessageTypeACLPolicy + OVOSAgentPolicy):

1. allowed_types denial — client whose allowed_types excludes
   recognizer_loop:utterance has its utterance blocked with
   ACL_DISALLOWED_TYPE; the message never reaches the agent bus.

2. Skill-blacklist injection — client allowed to inject utterances but
   registered with skill_blacklist=["skill-weather"]; OVOSAgentPolicy injects
   session.blacklisted_skills=["skill-weather"] before the message reaches
   the OVOS pipeline.

3. session_id="default" denied for non-admin — a non-admin client that sends
   session_id="default" is rejected with SESSION_ID_DEFAULT_FORBIDDEN per
   OVOS-SESSION-1 §3.1.  Marked xfail(strict=False): the bridge's
   _install_client_session rewrites the session before the policy runs in
   e2e dispatch (by design, not a pending merge); SESSION_ID_DEFAULT_FORBIDDEN
   is covered by ovos-agent-plugin unit tests.
"""

import time

import pytest
from hivemind_bus_client.message import HiveMessage, HiveMessageType
from ovos_bus_client.message import Message

from hivescope.scenarios import with_acl_enforcement
from hivescope.assertions import (
    assert_policy_denied,
    assert_session_blacklists_injected,
    ACL_DISALLOWED_TYPE,
    SESSION_ID_DEFAULT_FORBIDDEN,
)


def test_allowed_types_denial():
    """Non-admin client whose allowed_types excludes recognizer_loop:utterance
    has its utterance blocked by MessageTypeACLPolicy (ACL_DISALLOWED_TYPE).

    The message must not reach the agent bus.
    """
    b = with_acl_enforcement()
    b.start_all()
    try:
        m = b.get_master("M0")
        s = b.get_satellite("S_RESTRICTED_TYPE")

        s.send(HiveMessage(
            HiveMessageType.BUS,
            payload=Message("recognizer_loop:utterance", {"utterances": ["what is the weather"]}),
        ))

        time.sleep(0.2)  # give any errant dispatch a window to land

        assert_policy_denied(
            m, s,
            msg_type="recognizer_loop:utterance",
            deny_code=ACL_DISALLOWED_TYPE,
        )
    finally:
        b.stop_all()


def test_skill_blacklist_injection():
    """Client with skill_blacklist=["skill-weather"] can inject an utterance
    (allowed_types includes recognizer_loop:utterance) but OVOSAgentPolicy
    injects session.blacklisted_skills=["skill-weather"] so the OVOS pipeline
    cannot route to the blacklisted skill.
    """
    b = with_acl_enforcement()
    b.start_all()
    try:
        m = b.get_master("M0")
        s = b.get_satellite("S_RESTRICTED_SKILL")

        seen = []
        m.agent_protocol.bus.on("recognizer_loop:utterance", seen.append)

        s.send(HiveMessage(
            HiveMessageType.BUS,
            payload=Message("recognizer_loop:utterance", {"utterances": ["what is the weather"]}),
        ))

        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline and not seen:
            time.sleep(0.02)

        assert seen, "utterance did not reach the agent bus at all"

        assert_session_blacklists_injected(
            m, s,
            msg_type="recognizer_loop:utterance",
            expected_skills=["skill-weather"],
        )
    finally:
        b.stop_all()


@pytest.mark.xfail(
    strict=False,
    reason=(
        "INTENTIONAL defence-in-depth: the bridge's _install_client_session "
        "rewrites the session before the policy runs in e2e dispatch — by design, "
        "not a pending merge.  SESSION_ID_DEFAULT_FORBIDDEN is covered by "
        "ovos-agent-plugin unit tests."
    ),
)
def test_default_session_id_denied_for_non_admin():
    """A non-admin client sending session_id="default" is denied per
    OVOS-SESSION-1 §3.1 (SESSION_ID_DEFAULT_FORBIDDEN).

    Only admin peers may use the reserved default session.
    S_RESTRICTED_SKILL has allowed_types=["recognizer_loop:utterance"] so the
    message passes the type gate; OVOSAgentPolicy then checks session_id and
    rejects it with SESSION_ID_DEFAULT_FORBIDDEN.
    """
    b = with_acl_enforcement()
    b.start_all()
    try:
        m = b.get_master("M0")
        # Use S_RESTRICTED_SKILL: utterance type is allowed, so MessageTypeACLPolicy
        # passes and OVOSAgentPolicy evaluates the reserved session_id.
        s = b.get_satellite("S_RESTRICTED_SKILL")

        s.send(HiveMessage(
            HiveMessageType.BUS,
            payload=Message(
                "recognizer_loop:utterance",
                {"utterances": ["hello"]},
                context={"session": {"session_id": "default"}},
            ),
        ))

        time.sleep(0.2)

        assert_policy_denied(
            m, s,
            msg_type="recognizer_loop:utterance",
            deny_code=SESSION_ID_DEFAULT_FORBIDDEN,
        )
    finally:
        b.stop_all()
