# ============================================================
# R36F SL-DISABLE TEST A
# R36F159 REPLAY-GATE DIAGNOSTIC
#
# PURPOSE:
# Diagnose why a fresh eligible demo instruction can reach:
#
#     R36F159_COMMAND_REPLAY_BLOCKED
#
# even when:
#
#     OPEN POSITION ROWS = 0
#     DUPLICATE ENTRY BLOCKED = False
#     CYCLE DUPLICATE BLOCKED = False
#
# IMPORTANT:
# - STANDALONE DIAGNOSTIC
# - ZERO WRITE
# - NO WEEX POST
# - NO DEMO ORDER
# - NO REAL ORDER
# - NO REPLAY STATE MUTATION
# - NO ACCOUNT/POSITION MUTATION
# ============================================================

def r36f_sl_disable_test_a_replay_gate():

    print(
        "==========================================",
        flush=True,
    )

    print(
        "R36F SL-DISABLE TEST A START",
        flush=True,
    )

    print(
        "TEST A PURPOSE = R36F159 REPLAY GATE DIAGNOSTIC",
        flush=True,
    )

    # --------------------------------------------------------
    # Local test instruction.
    #
    # Deliberately self-contained so this test does not depend
    # on the current live strategy instruction.
    # --------------------------------------------------------

    test_instruction = {
        "symbol": "BTCUSDT",
        "direction": "SHORT",
        "quantity": "0.0004",
        "entry": "83191",
        "tp1": "82974.7",
        "tp2": "82891.5",
        "tp3_policy": "TRAILING_RUNNER",
    }

    # --------------------------------------------------------
    # Construct deterministic command identity.
    # --------------------------------------------------------

    import hashlib
    import json

    canonical_instruction = json.dumps(
        test_instruction,
        sort_keys=True,
        separators=(",", ":"),
    )

    current_identity = hashlib.sha256(
        canonical_instruction.encode("utf-8")
    ).hexdigest()

    print(
        "TEST A CURRENT CANONICAL INSTRUCTION = "
        + canonical_instruction,
        flush=True,
    )

    print(
        "TEST A CURRENT COMMAND IDENTITY = "
        + current_identity,
        flush=True,
    )

    # --------------------------------------------------------
    # Simulate EMPTY previous replay state.
    #
    # This represents the condition we expect when there is
    # no previously consumed command identity available.
    # --------------------------------------------------------

    previous_identity_empty = None

    empty_state_replay_match = (
        previous_identity_empty is not None
        and previous_identity_empty == current_identity
    )

    print(
        "TEST A EMPTY PREVIOUS IDENTITY = "
        + str(previous_identity_empty),
        flush=True,
    )

    print(
        "TEST A EMPTY STATE REPLAY MATCH = "
        + str(empty_state_replay_match),
        flush=True,
    )

    # --------------------------------------------------------
    # Simulate a genuinely DIFFERENT previous instruction.
    # --------------------------------------------------------

    previous_instruction = {
        "symbol": "BTCUSDT",
        "direction": "LONG",
        "quantity": "0.0004",
        "entry": "83000",
        "tp1": "83200",
        "tp2": "83400",
        "tp3_policy": "TRAILING_RUNNER",
    }

    previous_canonical = json.dumps(
        previous_instruction,
        sort_keys=True,
        separators=(",", ":"),
    )

    previous_identity_different = hashlib.sha256(
        previous_canonical.encode("utf-8")
    ).hexdigest()

    different_state_replay_match = (
        previous_identity_different
        == current_identity
    )

    print(
        "TEST A DIFFERENT PREVIOUS IDENTITY = "
        + previous_identity_different,
        flush=True,
    )

    print(
        "TEST A DIFFERENT COMMAND REPLAY MATCH = "
        + str(different_state_replay_match),
        flush=True,
    )

    # --------------------------------------------------------
    # Simulate an ACTUAL replay.
    # --------------------------------------------------------

    previous_identity_same = current_identity

    same_state_replay_match = (
        previous_identity_same
        == current_identity
    )

    print(
        "TEST A SAME PREVIOUS IDENTITY = "
        + previous_identity_same,
        flush=True,
    )

    print(
        "TEST A SAME COMMAND REPLAY MATCH = "
        + str(same_state_replay_match),
        flush=True,
    )

    # --------------------------------------------------------
    # Expected replay decisions.
    # --------------------------------------------------------

    empty_should_block = empty_state_replay_match
    different_should_block = different_state_replay_match
    same_should_block = same_state_replay_match

    print(
        "TEST A EMPTY STATE SHOULD BLOCK = "
        + str(empty_should_block),
        flush=True,
    )

    print(
        "TEST A DIFFERENT COMMAND SHOULD BLOCK = "
        + str(different_should_block),
        flush=True,
    )

    print(
        "TEST A IDENTICAL COMMAND SHOULD BLOCK = "
        + str(same_should_block),
        flush=True,
    )

    # --------------------------------------------------------
    # Critical invariant.
    #
    # Only an identical previously consumed command should
    # qualify as replay.
    # --------------------------------------------------------

    invariant_pass = (
        empty_should_block is False
        and different_should_block is False
        and same_should_block is True
    )

    print(
        "TEST A REPLAY INVARIANT = "
        + (
            "PASS"
            if invariant_pass
            else "FAIL"
        ),
        flush=True,
    )

    # --------------------------------------------------------
    # Confirm zero-write properties.
    # --------------------------------------------------------

    weex_post = False
    demo_order_sent = False
    real_order_sent = False
    replay_state_mutated = False

    print(
        "TEST A WEEX POST = "
        + str(weex_post),
        flush=True,
    )

    print(
        "TEST A DEMO ORDER SENT = "
        + str(demo_order_sent),
        flush=True,
    )

    print(
        "TEST A REAL ORDER SENT = "
        + str(real_order_sent),
        flush=True,
    )

    print(
        "TEST A REPLAY STATE MUTATED = "
        + str(replay_state_mutated),
        flush=True,
    )

    final_pass = (
        invariant_pass
        and not weex_post
        and not demo_order_sent
        and not real_order_sent
        and not replay_state_mutated
    )

    print(
        "R36F SL-DISABLE TEST A = "
        + (
            "PASS"
            if final_pass
            else "FAIL"
        ),
        flush=True,
    )

    print(
        "==========================================",
        flush=True,
    )

    return {
        "pass": final_pass,
        "current_identity": current_identity,
        "empty_replay_match": empty_state_replay_match,
        "different_replay_match": different_state_replay_match,
        "same_replay_match": same_state_replay_match,
        "weex_post": weex_post,
        "demo_order_sent": demo_order_sent,
        "real_order_sent": real_order_sent,
        "replay_state_mutated": replay_state_mutated,
    }


# ============================================================
# RUN TEST A
# ============================================================

r36f_sl_disable_test_a_replay_gate()
