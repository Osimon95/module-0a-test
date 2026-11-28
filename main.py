
# ============================================================
# WEEX DEMO POSITION CONTROLLER V1
# RENDER ENVIRONMENT CONTROL
# REUSES EXISTING UNIT 14 DEMO API
# DOES NOT MODIFY EXISTING ENVIRONMENT VARIABLES
# ============================================================

import os as _dpc_os
import json as _dpc_json
import hashlib as _dpc_hashlib
from decimal import Decimal as _DPC_D
from decimal import ROUND_DOWN as _DPC_ROUND_DOWN

_DPC_JOURNAL_DIR = "/var/data/demo_position_control"


def dpc_setting(name, default=""):
    return _dpc_os.getenv(name, default).strip()


def dpc_positions():
    return unit_14_v3_positions()


def dpc_inspect():
    positions = dpc_positions()
    mark = unit_14_v3_mark()

    print("=" * 80, flush=True)
    print("DEMO POSITION CONTROLLER = INSPECT", flush=True)
    print("DEMO ENVIRONMENT = WEEX SIM", flush=True)
    print("DEMO MARK PRICE =", mark, flush=True)
    print("DEMO OPEN POSITIONS =", len(positions), flush=True)

    for side, p in positions.items():
        size = _DPC_D(str(p["size"]))
        entry_raw = (
            p.get("avgPrice")
            or p.get("entryPrice")
            or p.get("openPriceAvg")
        )

        entry = (
            _DPC_D(str(entry_raw))
            if entry_raw is not None
            else None
        )

        leverage = p.get("leverage", "UNAVAILABLE")
        liquidation = p.get(
            "liquidationPrice",
            p.get("liqPrice", "UNAVAILABLE")
        )

        pnl = None
        if entry is not None:
            if side == "LONG":
                pnl = (mark - entry) * size
            else:
                pnl = (entry - mark) * size

        print("-" * 60, flush=True)
        print("POSITION SIDE =", side, flush=True)
        print("POSITION SIZE =", size, flush=True)
        print("ENTRY PRICE =", entry, flush=True)
        print("MARK PRICE =", mark, flush=True)
        print("LEVERAGE =", leverage, flush=True)
        print("LIQUIDATION PRICE =", liquidation, flush=True)
        print(
            "ESTIMATED UNREALIZED PNL =",
            pnl if pnl is not None else "UNAVAILABLE",
            flush=True
        )
        print("PNL EXCLUDES FEES AND FUNDING", flush=True)

    print("=" * 80, flush=True)
    return positions


def dpc_command_claim(command_id):
    # Persistent disk required for restart-safe execution.
    if not _dpc_os.path.isdir("/var/data"):
        raise RuntimeError(
            "DEMO CONTROL REQUIRES PERSISTENT /var/data"
        )

    _dpc_os.makedirs(
        _DPC_JOURNAL_DIR,
        exist_ok=True
    )

    digest = _dpc_hashlib.sha256(
        command_id.encode("utf-8")
    ).hexdigest()

    path = _dpc_os.path.join(
        _DPC_JOURNAL_DIR,
        digest + ".json"
    )

    # Exclusive creation prevents reuse of the same
    # command ID, including after worker restarts.
    fd = _dpc_os.open(
        path,
        _dpc_os.O_WRONLY
        | _dpc_os.O_CREAT
        | _dpc_os.O_EXCL,
        0o600
    )

    with _dpc_os.fdopen(fd, "w") as f:
        _dpc_json.dump({
            "command_id": command_id,
            "state": "CLAIMED_BEFORE_SUBMISSION"
        }, f)
        f.flush()
        _dpc_os.fsync(f.fileno())

    return path


def dpc_close(side, command_id):
    positions = dpc_positions()

    if side not in positions:
        print(
            "DEMO CONTROL POSITION NOT FOUND =",
            side,
            flush=True
        )
        return "NO_POSITION"

    p = positions[side]

    size = _DPC_D(str(p["size"]))
    step = _DPC_D("0.0001")

    quantity = (
        (size / step).to_integral_value(
            rounding=_DPC_ROUND_DOWN
        ) * step
    )

    if quantity <= 0:
        raise RuntimeError(
            "DEMO CONTROL INVALID CLOSE QUANTITY"
        )

    # Re-read exchange position immediately
    # before submitting the manual close.
    latest = dpc_positions().get(side)

    if latest is None:
        return "POSITION_CHANGED"

    latest_size = _DPC_D(str(latest["size"]))

    if latest_size != size:
        print(
            "DEMO CONTROL POSITION SIZE CHANGED",
            flush=True
        )
        return "POSITION_CHANGED"

    payload = {
        "symbol": unit_13_14_active_symbols()[1],
        "side": "SELL" if side == "LONG" else "BUY",
        "positionSide": side,
        "type": "MARKET",
        "quantity": format(quantity, "f"),
        "newClientOrderId": (
            "DPC-"
            + _dpc_hashlib.sha256(
                (command_id + ":" + side).encode()
            ).hexdigest()[:24]
        )
    }

    # Claim before POST, never automatically retry.
    dpc_command_claim(command_id)

    print(
        "DEMO CONTROL SUBMITTING CLOSE =",
        side,
        flush=True
    )

    reply = unit_14_v3_signed_request(
        "POST",
        UNIT14_V3_ORDER,
        payload=payload
    )

    print(
        "DEMO CONTROL ORDER RESPONSE =",
        reply,
        flush=True
    )

    if (
        not isinstance(reply, dict)
        or reply.get("success") is not True
        or not reply.get("orderId")
    ):
        return "SUBMISSION_UNCONFIRMED"

    # Acknowledgment is not proof of a fill.
    remaining = dpc_positions().get(side)

    if remaining is None:
        return "CLOSED_CONFIRMED"

    return "SUBMITTED_RECONCILIATION_REQUIRED"


def dpc_process():
    command = dpc_setting(
        "DEMO_POSITION_CONTROL", "OFF"
    ).upper()

    arm = dpc_setting(
        "DEMO_CONTROL_ARM", "NO"
    ).upper()

    command_id = dpc_setting(
        "DEMO_CONTROL_COMMAND_ID", ""
    )

    if command == "OFF":
        return "OFF"

    if command in ("INSPECT", "STATUS"):
        dpc_inspect()
        return "INSPECTED"

    if command not in (
        "CLOSE_LONG",
        "CLOSE_SHORT",
        "CLOSE_ALL"
    ):
        print(
            "DEMO CONTROL UNKNOWN COMMAND =",
            command,
            flush=True
        )
        return "REJECTED"

    if arm != "YES":
        print(
            "DEMO CONTROL CLOSE NOT ARMED",
            flush=True
        )
        return "NOT_ARMED"

    if not command_id:
        print(
            "DEMO CONTROL COMMAND ID REQUIRED",
            flush=True
        )
        return "REJECTED"

    # CLOSE_ALL requires a separate, explicit
    # command ID for each side.
    if command == "CLOSE_ALL":
        positions = dpc_positions()
        results = {}

        for side in ("LONG", "SHORT"):
            if side in positions:
                results[side] = dpc_close(
                    side,
                    command_id + "-" + side
                )

        print(
            "DEMO CONTROL CLOSE ALL RESULTS =",
            results,
            flush=True
        )
        return "CLOSE_ALL_PROCESSED"

    side = command.split("_", 1)[1]

    try:
        result = dpc_close(side, command_id)
    except FileExistsError:
        print(
            "DEMO CONTROL DUPLICATE COMMAND ID",
            flush=True
        )
        return "DUPLICATE_BLOCKED"

    print(
        "DEMO CONTROL RESULT =",
        result,
        flush=True
    )

    return result


# ============================================================
# END WEEX DEMO POSITION CONTROLLER V1
# ============================================================


# ============================================================
# START CONTINUOUS SCANNING
# All demo controller functions are now defined.
# ============================================================

scan_forever()

# ============================================================
# END CONTINUOUS SCAN CONTROLLER V1
# ============================================================
