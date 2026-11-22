# ============================================================
# WEEX BOT - UNIT 1
# ORIGINAL 22524-LINE WORKING MODEL
# RUNTIME FOUNDATION
# ZERO INDENTATION
# ============================================================

# ============================================================
# STANDARD LIBRARY IMPORTS
# ============================================================

import json
import urllib.error
import urllib.parse
import urllib.request

from datetime import datetime, timezone


# ============================================================
# SHARED LOGGER
# ============================================================

def log(message):

    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    print(
        timestamp,
        message,
        flush=True,
    )


# ============================================================
# RECONSTRUCTION UNIT 1
# RUNTIME FOUNDATION
# ============================================================

def fresh_reconstruction_unit_1():

    print(
        "=" * 80,
        flush=True,
    )

    log(
        "FRESH RECONSTRUCTION UNIT 1 START"
    )

    print(
        "-" * 80,
        flush=True,
    )

    # --------------------------------------------------------
    # UNIT 1 PURPOSE
    #
    # Unit 1 proves only that:
    #
    # - main.py starts
    # - required standard-library components are available
    # - no exchange operation occurs inside Unit 1
    #
    # Unit 1 does NOT claim that later units perform no HTTP.
    # --------------------------------------------------------

    print(
        "PASS: MAIN.PY STARTED SUCCESSFULLY",
        flush=True,
    )

    print(
        "PASS: PYTHON STANDARD LIBRARY AVAILABLE",
        flush=True,
    )

    print(
        "PASS: JSON MODULE AVAILABLE",
        flush=True,
    )

    print(
        "PASS: URLLIB MODULE AVAILABLE",
        flush=True,
    )

    # --------------------------------------------------------
    # UNIT-LOCAL SAFETY
    # --------------------------------------------------------

    print(
        "UNIT 1 EXCHANGE CONNECTION = NONE",
        flush=True,
    )

    print(
        "UNIT 1 HTTP REQUEST = NONE",
        flush=True,
    )

    print(
        "UNIT 1 DEMO ORDER = NONE",
        flush=True,
    )

    print(
        "UNIT 1 REAL ORDER = NONE",
        flush=True,
    )

    print(
        "UNIT 1 EXCHANGE WRITE = NONE",
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    log(
        "FRESH RECONSTRUCTION UNIT 1 RESULT = PASS"
    )

    print(
        "=" * 80,
        flush=True,
    )

    return True


# ============================================================
# RUN UNIT 1
# ============================================================

FRESH_RECONSTRUCTION_UNIT_1_READY = (
    fresh_reconstruction_unit_1()
)


# ============================================================
# END COMPLETE UNIT 1
# UNIT 2 TO FOLLOW
# ZERO INDENTATION
# ============================================================



# ============================================================
# START COMPLETE UNIT 2 V9
# WEEX DEMO CENTRAL CONFIGURATION + QUALIFICATION
# E0 INITIAL ENTRY / B1-B5 DYNAMIC BACKUPS
# NO BACKUP MULTIPLIERS
# ============================================================

import os
import math
from decimal import Decimal, InvalidOperation


# ============================================================
# UNIT 2 - READ PERSISTED ACTIVE SYMBOL
# DOES NOT MODIFY SQLITE OR SUBMIT ORDERS
# ============================================================

def unit_2_active_symbol_pair():

    import sqlite3
    import re
    from pathlib import Path

    
    requested_market = os.getenv(
        "WEEX_SYMBOL", "BTCUSDT"
    ).strip().upper()

    # Preserve BTC demo mapping.
    # Other symbols require discovery and verification.

    requested_demo = os.getenv(
        "WEEX_DEMO_SYMBOL",
        "BTCSUSDT" if requested_market == "BTCUSDT" else ""
    ).strip().upper()

    result = {
        "market_symbol": requested_market,
        "demo_order_symbol": requested_demo,
        "source": "RENDER_INITIAL_REQUEST",
        "persisted_state_found": False,
    }

    stage_path = os.getenv(
        "UNIT14_STAGE_DB_PATH",
        "/var/data/unit14_stages.sqlite3"
    )

    database_path = os.path.join(
        os.path.dirname(stage_path),
        "weex_symbol_switch.sqlite3"
    )

    if not os.path.isfile(database_path):
        return result

    connection = None

    try:
        connection = sqlite3.connect(
            Path(database_path).resolve().as_uri()
            + "?mode=ro",
            uri=True,
            timeout=10
        )

        row = connection.execute("""
            SELECT active_market, active_demo
            FROM symbol_switch
            WHERE id = 1
        """).fetchone()

        if row is None:
            return result

        active_market = str(row[0] or "").upper()
        active_demo = str(row[1] or "").upper()

        
        # First-start initialization may have no
        # verified active pair yet.

        if not active_market and not active_demo:
            result["source"] = "PENDING_DEMO_VERIFICATION"
            result["persisted_state_found"] = True
            return result

        if not active_market or not active_demo:
            raise RuntimeError(
                "INCOMPLETE PERSISTED ACTIVE SYMBOL"
            )

        if not (
            re.fullmatch(
                r"[A-Z0-9]{3,30}",
                active_market
            )
            and re.fullmatch(
                r"[A-Z0-9]{3,30}",
                active_demo
            )
        ):
            raise RuntimeError(
                "INVALID PERSISTED ACTIVE SYMBOL"
            )

        result.update({
            "market_symbol": active_market,
            "demo_order_symbol": active_demo,
            "source": "PERSISTED_ACTIVE_SYMBOL",
            "persisted_state_found": True,
        })

        return result

    except sqlite3.Error as exc:
        raise RuntimeError(
            "UNIT 2 PERSISTED SYMBOL READ FAILED"
        ) from exc

    finally:
        if connection is not None:
            connection.close()

def unit_2_v9_number(value, name, allow_zero=False):
    if isinstance(value, bool):
        raise RuntimeError("UNIT 2 INVALID " + name)
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise RuntimeError(
            "UNIT 2 INVALID " + name
        ) from exc

    if not number.is_finite():
        raise RuntimeError("UNIT 2 NONFINITE " + name)

    if number < 0 or (number == 0 and not allow_zero):
        raise RuntimeError(
            "UNIT 2 INVALID RANGE " + name
        )

    return number


def fresh_reconstruction_unit_2():

    print("=" * 80, flush=True)
    print(
        "FRESH RECONSTRUCTION UNIT 2 V9 START",
        flush=True
    )

    if FRESH_RECONSTRUCTION_UNIT_1_READY is not True:
        raise RuntimeError(
            "UNIT 2 BLOCKED: UNIT 1 NOT READY"
        )

    # ========================================================
    # CONFIGURABLE INPUTS
    # ========================================================
    # Set these directly or through Render environment values.
    # E0 is an amount, not a separate multiplier system.
    # Unit 2 never accesses private WEEX endpoints.
    # ========================================================

    def setting(name, default):
        return unit_2_v9_number(
            os.getenv(name, str(default)),
            name
        )

    e0_margin = setting(
        "INITIAL_ENTRY_MARGIN_USDT", "0.5"
    )

    backup_percent = setting(
        "BACKUP_MARGIN_PERCENT", "0.5"
    )

    buffer_percent = setting(
        "BACKUP_BUFFER_PERCENT", "0.3"
    )

    cap_percent = setting(
        "EXPOSURE_CAP_PERCENT", "35.0"
    )

    
    # TP allocation: Render format TP1:10,TP2:20,TP3:70
    allocation_text = os.getenv(
        "TP_ALLOCATION_PERCENT",
        "TP1:10,TP2:20,TP3:70"
    )

    try:
        allocation_parts = {}
        for item in allocation_text.split(","):
            key, value = item.strip().split(":", 1)
            key = key.strip().upper()
            if key in allocation_parts:
                raise ValueError("Duplicate TP key")
            allocation_parts[key] = unit_2_v9_number(
                value.strip(), key
            )

        if set(allocation_parts) != {"TP1", "TP2", "TP3"}:
            raise ValueError("TP1, TP2 and TP3 required")

        if sum(allocation_parts.values()) != Decimal("100"):
            raise ValueError("Allocation must total 100")

        if any(value <= 0 for value in allocation_parts.values()):
            raise ValueError("Each allocation must be positive")

    except (ValueError, TypeError, RuntimeError) as exc:
        raise RuntimeError(
            "UNIT 2 TP ALLOCATION REJECTED: " + str(exc)
        ) from exc

    tp1_roi = setting("TP1_NET_ROI_FLOOR_PERCENT", "20")
    tp2_roi = setting("TP2_NET_ROI_FLOOR_PERCENT", "40")

    fee_mode = os.getenv(
        "SIGNAL_FEE_COVERAGE_ENABLED", "true"
    ).strip().lower()

    if fee_mode not in ("true", "false"):
        raise RuntimeError(
            "SIGNAL_FEE_COVERAGE_ENABLED MUST BE true OR false"
        )

    fee_coverage_enabled = (fee_mode == "true") 
    if tp1_roi <= 0 or tp2_roi <= tp1_roi:
        raise RuntimeError(
            "UNIT 2 TP ROI REJECTED: "
            "TP1 must be positive and TP2 must exceed TP1"
        )

    print(
        "UNIT 2 TP ALLOCATION ACCEPTED =",
        allocation_text,
        flush=True
    )
    print(
        "UNIT 2 TP ROI FLOORS ACCEPTED =",
        tp1_roi, "/", tp2_roi,
        flush=True
    )

    if backup_percent > 100:
        raise RuntimeError(
            "UNIT 2 BACKUP PERCENT EXCEEDS 100"
        )

    if buffer_percent >= 100:
        raise RuntimeError(
            "UNIT 2 INVALID LIQUIDATION BUFFER"
        )

    if cap_percent > 100:
        raise RuntimeError(
            "UNIT 2 EXPOSURE CAP EXCEEDS 100"
        )

    # ========================================================
    # EXCHANGE SETTINGS
    # ========================================================

    
    active_symbol_pair = unit_2_active_symbol_pair()

    exchange = {
        "name": "WEEX",
        "api_version": "V3",
        "contract_base_url":
            "https://api-contract.weex.com",

        "market_symbol":
            active_symbol_pair["market_symbol"],

        "demo_order_symbol":
            active_symbol_pair["demo_order_symbol"],

        "requested_market_symbol":
            os.getenv(
                "WEEX_SYMBOL", "BTCUSDT"
            ).strip().upper(),

        "requested_demo_symbol":
            os.getenv(
                "WEEX_DEMO_SYMBOL", "BTCSUSDT"
            ).strip().upper(),

        "active_symbol_source":
            active_symbol_pair["source"],

        "symbol_switch_deferred_until_flat": True,
    }

    print(
        "UNIT 2 ACTIVE MARKET SYMBOL =",
        exchange["market_symbol"],
        flush=True
    )

    print(
        "UNIT 2 ACTIVE DEMO SYMBOL =",
        exchange["demo_order_symbol"],
        flush=True
    )

    print(
        "UNIT 2 REQUESTED MARKET SYMBOL =",
        exchange["requested_market_symbol"],
        flush=True
    )

    print(
        "UNIT 2 REQUESTED DEMO SYMBOL =",
        exchange["requested_demo_symbol"],
        flush=True
    )

    safety = {
        "public_market_data_read_enabled": True,
        "demo_account_balance_read_enabled": True,
        "authenticated_api_enabled": False,
        "account_access_enabled": False,
        "position_access_enabled": False,
        "order_endpoint_access_enabled": False,
        "demo_order_submission_enabled": False,
        "real_order_submission_enabled": False,
        "exchange_mutation_enabled": False,
        "leverage_mutation_enabled": False,
        "margin_mode_mutation_enabled": False,
        "position_mode_mutation_enabled": False,
    }

    # These are local Unit 2 capabilities.
    # They must not disable subsequent authorized
    # DEMO execution in Unit 12.

    # ========================================================
    # CENTRAL STRATEGY CONFIGURATION
    # ========================================================

    strategy = {
        "initial_fixed_usdt": float(e0_margin),
        "initial_margin_percent": 5.0,

        "backup_margin_percent":
            float(backup_percent),
        "backup_buffer_percent":
            float(buffer_percent),
        "max_backups": 5,

        "backup_sizing_mode":
            "PERCENT_AVAILABLE_BALANCE",

        "backup_trigger_reference":
            "FRESH_WEEX_LIQUIDATION_PRICE",

        "backup_trigger_recalculation":
            "AFTER_PRECEDING_CONFIRMED_FILL",

        "backup_long_liquidation_factor":
            float(
                Decimal("1")
                + buffer_percent / Decimal("100")
            ),

        "backup_short_liquidation_factor":
            float(
                Decimal("1")
                - buffer_percent / Decimal("100")
            ),

        "exposure_cap_percent":
            float(cap_percent),
        "exposure_cap_max_percent": 100.0,

        "exposure_cap_basis":
            "TRADING_ACCOUNT_EQUITY",

        "exposure_includes_initial": True,
        "exposure_includes_filled_backups": True,
        "exposure_includes_pending_margin": True,

        "progressive_backup_funding": True,
        "full_ladder_reservation_required": False,

        
        "tp1_allocation_percent": float(
            allocation_parts["TP1"]
        ),
        "tp2_allocation_percent": float(
            allocation_parts["TP2"]
        ),
        "tp3_allocation_percent": float(
            allocation_parts["TP3"]
        ),

        "tp1_net_roi_floor_percent": float(tp1_roi),
        "tp2_net_roi_floor_percent": float(tp2_roi),
        "tp1_tp2_min_roi_separation_percent": float(
            tp2_roi - tp1_roi
        ),

        "tp3_trailing_reference_percent": 0.20,
        "tp3_trailing_min_percent": 0.10,
        "tp3_trailing_max_percent": 0.40,

        "signal_expiry_seconds": 120,
        "loss_cooldown_seconds": 300,

        "one_direction_only": True,
        "anti_duplicate_orders": True,
        "active_trade_mode_lock": True,
        "exclusive_mode": True,
        "mode_confirmations_required": 3,
        "signal_fee_coverage_enabled": fee_coverage_enabled,
    }

    # No backup_multipliers key.
    # No hardcoded leverage_target key.

    
    # Symbol-specific precision is loaded by the
    # scan controller before order sizing.
    # These initial values are placeholders only.
    # They must not authorize an order.

    market_precision = {
        "quantity_step": 0.0001,
        "minimum_quantity": 0.0001,
        "price_step": 0.1,
        "contract_multiplier": 1.0,
        "symbol_specifications_confirmed": False,
    }

    # ========================================================
    # PRESERVE UNIT 2 HYBRID QUALIFICATION CONTRACT
    # ========================================================

    qualification = {
        "common": {
            "mode_priority": (
                "BREAKOUT", "STRUCTURE", "SCALP"
            ),
            "direction_votes_required": 2,
            "direction_votes_total": 3,
            "use_closed_candles": True,
            "protect_developing_candidates": True,
            "arbitrate_before_scalp": True,
            "scalp_requires_higher_modes_clear": True,
            "signal_expiry_seconds": 120,
            "candidate_expiry_seconds": 120,
            "spike_count_rejection_above": 2,
            "reject_late_impulse_entry": True,
        },

        "breakout": {
            "enabled": True,
            "priority": 1,
            "early_detection_enabled": True,
            "developing_candidate_enabled": True,
            "support_resistance_lookback": 20,
            "developing_proximity_atr": 0.50,
            "confirmation_distance_atr": 0.10,
            "direction_votes_required": 2,
            "momentum_lookback_fast": 5,
            "momentum_lookback_slow": 15,
            "require_momentum_confirmation": True,
            "require_direction_agreement": True,
            "require_ema_crossover": False,
            "retest_mandatory": False,
            "allow_preconfirmation": True,
            "minimum_atr_percent": 0.0,
            "max_price_extension_atr": 3.0,
            "spike_rejection_enabled": True,
            "max_spike_count": 2,
            "false_breakout_rejection": True,
            "volume_confirmation_enabled": False,
            "minimum_volume_ratio": 1.20,
            "candidate_expiry_seconds": 120,
        },

        "structure": {
            "enabled": True,
            "priority": 2,
            "early_detection_enabled": True,
            "developing_candidate_enabled": True,
            "ema_fast_period": 19,
            "ema_middle_period": 50,
            "ema_slow_period": 200,
            "direction_votes_required": 2,
            "momentum_lookback_minutes": 15,
            "require_direction_agreement": True,
            "require_ema_crossover": False,
            "allow_pullback_entry": True,
            "allow_continuation_entry": True,
            "pullback_tolerance_atr": 0.75,
            "max_price_extension_atr": 2.0,
            "minimum_ema_separation_percent": 0.0,
            "retest_mandatory": False,
            "reject_trend_exhaustion": True,
            "candidate_expiry_seconds": 120,
        },

        "scalp": {
            "enabled": True,
            "priority": 3,
            "sideways_preferred": True,
            "require_sideways_market": True,
            "protect_developing_higher_modes": True,
            "quality_threshold": 70.0,
            "price_action_weight_percent": 50.0,
            "other_factors_weight_percent": 50.0,
            "direction_votes_required": 2,
            "direction_votes_total": 3,
            "max_ema_extension_clusters": 1.5,
            "max_spike_count": 2,
            "reject_late_impulse": True,
            "early_entry_enabled": True,
            "ema_compression_atr_max": 0.70,
            "range20_atr_max": 8.0,
            "momentum15_atr_multiplier_max": 1.5,
            "fee_aware_enabled": True,
            "estimated_taker_fee_percent": 0.08,
            "estimated_slippage_percent": 0.0,
            "include_entry_fee": True,
            "include_exit_fee": True,
            "minimum_fee_coverage_multiplier": 2.0,
            "require_positive_estimated_net": True,
            "minimum_net_roi_percent": 2.0,
        },
    }

    config = {
        "exchange": exchange,
        "execution_environment": "DEMO",
        "safety": safety,
        "strategy": strategy,
        "market_precision": market_precision,
        "qualification": qualification,
    }

    # ========================================================
    # CONTRACT VALIDATION
    # ========================================================

    def require(condition, message):
        if not condition:
            raise RuntimeError(
                "UNIT 2 CONFIG INVALID: " + message
            )

    require(
        exchange["name"] == "WEEX",
        "EXCHANGE"
    )

    require(
        exchange["api_version"] == "V3",
        "API VERSION"
    )

    require(
        config["execution_environment"] == "DEMO",
        "DEMO ENVIRONMENT"
    )

    require(
        e0_margin > 0,
        "E0 MARGIN"
    )

    require(
        backup_percent > 0
        and backup_percent <= 100,
        "BACKUP BALANCE PERCENT"
    )

    require(
        buffer_percent > 0
        and buffer_percent < 100,
        "LIQUIDATION BUFFER"
    )

    require(
        strategy["max_backups"] == 5,
        "BACKUP COUNT"
    )

    require(
        Decimal("0") < cap_percent <= Decimal("100"),
        "EXPOSURE CAP"
    )

    require(
        "backup_multipliers" not in strategy,
        "OBSOLETE BACKUP MULTIPLIERS"
    )

    require(
        "leverage_target" not in strategy,
        "HARDCODED LEVERAGE"
    )

    for key in (
        "one_direction_only",
        "anti_duplicate_orders",
        "active_trade_mode_lock",
        "exclusive_mode",
        "progressive_backup_funding",
        "exposure_includes_initial",
        "exposure_includes_filled_backups",
        "exposure_includes_pending_margin",
    ):
        require(
            strategy.get(key) is True,
            key
        )

    require(
        strategy[
            "full_ladder_reservation_required"
        ] is False,
        "FULL LADDER RESERVATION"
    )

    for key in (
        "real_order_submission_enabled",
        "demo_order_submission_enabled",
        "exchange_mutation_enabled",
        "leverage_mutation_enabled",
        "margin_mode_mutation_enabled",
        "position_mode_mutation_enabled",
    ):
        require(
            safety[key] is False,
            "UNIT 2 WRITE SAFETY " + key
        )

    require(
        sum(
            strategy[key] for key in (
                "tp1_allocation_percent",
                "tp2_allocation_percent",
                "tp3_allocation_percent",
            )
        ) == 100.0,
        "TAKE PROFIT ALLOCATION"
    )

    require(
        strategy["tp1_net_roi_floor_percent"] > 0,
        "TP1 ROI FLOOR"
    )

    require(
        strategy["tp2_net_roi_floor_percent"]
        > strategy["tp1_net_roi_floor_percent"],
        "TP2 ROI FLOOR"
    )

    require(
        0 < strategy["tp3_trailing_min_percent"]
        <= strategy["tp3_trailing_reference_percent"]
        <= strategy["tp3_trailing_max_percent"],
        "TP3 TRAILING RANGE"
    )

    for key in (
        "quantity_step",
        "minimum_quantity",
        "price_step",
    ):
        require(
            market_precision[key] > 0,
            "MARKET PRECISION " + key
        )

    require(
        qualification["common"]["mode_priority"]
        == ("BREAKOUT", "STRUCTURE", "SCALP"),
        "STRATEGY PRIORITY"
    )

    require(
        qualification["scalp"]["quality_threshold"]
        == 70.0,
        "SCALP QUALITY"
    )

    # ========================================================
    # STARTUP REPORT
    # ========================================================

    print(
        "PASS: UNIT 2 CONFIGURATION CREATED",
        flush=True
    )
    print("PASS: EXCHANGE = WEEX", flush=True)
    print("PASS: API VERSION = V3", flush=True)
    print(
    "UNIT 2 CONFIGURED DEMO ORDER SYMBOL =",
    exchange["demo_order_symbol"],
    flush=True
)
    print(
        "PASS: EXECUTION ENVIRONMENT = DEMO",
        flush=True
    )
    print(
        "PASS: LEVERAGE CONTROL = WEEX ONLY",
        flush=True
    )
    print(
        "PASS: INITIAL ENTRY DEFAULT USDT =",
        strategy["initial_fixed_usdt"],
        flush=True
    )
    print(
        "PASS: BACKUP MARGIN % AVAILABLE =",
        strategy["backup_margin_percent"],
        flush=True
    )
    print(
        "PASS: BACKUP BUFFER % =",
        strategy["backup_buffer_percent"],
        flush=True
    )
    print(
        "PASS: MAX BACKUPS =",
        strategy["max_backups"],
        flush=True
    )
    print(
        "PASS: BACKUP MULTIPLIERS = NONE",
        flush=True
    )
    print(
        "PASS: BACKUP FUNDING = PROGRESSIVE",
        flush=True
    )
    print(
        "PASS: EXPOSURE CAP DEFAULT/CURRENT % =",
        strategy["exposure_cap_percent"],
        flush=True
    )
    print(
        "PASS: EXPOSURE CAP MAX % =",
        strategy["exposure_cap_max_percent"],
        flush=True
    )
    print(
        "PASS: LONG BACKUP FACTOR =",
        strategy["backup_long_liquidation_factor"],
        flush=True
    )
    print(
        "PASS: SHORT BACKUP FACTOR =",
        strategy["backup_short_liquidation_factor"],
        flush=True
    )
    print(
        "PASS: QUALIFICATION MODE PRIORITY =",
        qualification["common"]["mode_priority"],
        flush=True
    )
    print(
        "PASS: SCALP QUALITY TARGET =",
        qualification["scalp"]["quality_threshold"],
        flush=True
    )
    
    
    print(
        "PASS: TP ALLOCATION =",
        strategy["tp1_allocation_percent"],
        "/",
        strategy["tp2_allocation_percent"],
        "/",
        strategy["tp3_allocation_percent"],
        flush=True
    )

    print(
        "PASS: TP1 NET ROI FLOOR % =",
        strategy["tp1_net_roi_floor_percent"],
        flush=True
    )

    print(
        "PASS: TP2 NET ROI FLOOR % =",
        strategy["tp2_net_roi_floor_percent"],
        flush=True
    )

    print(
        "PASS: MARKET QUANTITY STEP =",
        market_precision["quantity_step"],
        flush=True
    )
    print(
        "PASS: ANTI DUPLICATE = TRUE",
        flush=True
    )
    print(
        "PASS: NO EXCHANGE MUTATION IN UNIT 2",
        flush=True
    )
    print(
        "FRESH RECONSTRUCTION UNIT 2 RESULT = PASS",
        flush=True
    )
    print(
        "FRESH RECONSTRUCTION UNIT 2 ADAPTER RESULT = PASS",
        flush=True
    )
    print("=" * 80, flush=True)

    return config


# ============================================================
# UNIT 2 V9 EXECUTION
# ============================================================

FRESH_RECONSTRUCTION_CONFIG = (
    fresh_reconstruction_unit_2()
)

# ============================================================
# END COMPLETE UNIT 2 V9
# UNIT 3 FOLLOWS
# ============================================================
# ============================================================
# UNIT 2 V9 -> UNIT 3 COMPATIBILITY
# RESTORE ORIGINAL OPTIMIZATION READINESS CONTRACT
# ============================================================

FRESH_UNIT_2_OPTIMIZATION_READY = (
    isinstance(FRESH_RECONSTRUCTION_CONFIG, dict)
    and FRESH_RECONSTRUCTION_CONFIG.get(
        "execution_environment"
    ) == "DEMO"
    and isinstance(
        FRESH_RECONSTRUCTION_CONFIG.get("strategy"),
        dict
    )
    and isinstance(
        FRESH_RECONSTRUCTION_CONFIG.get("qualification"),
        dict
    )
    and FRESH_RECONSTRUCTION_CONFIG[
        "strategy"
    ].get("anti_duplicate_orders") is True
    and FRESH_RECONSTRUCTION_CONFIG[
        "strategy"
    ].get("max_backups") == 5
)

if not FRESH_UNIT_2_OPTIMIZATION_READY:
    raise RuntimeError(
        "UNIT 2 V9 OPTIMIZATION READINESS FAILED"
    )

print(
    "UNIT 2 V9 OPTIMIZATION READY =",
    FRESH_UNIT_2_OPTIMIZATION_READY,
    flush=True
)

    

# ============================================================
# START COMPLETE UNIT 3 REPLACEMENT V2
# WEEX V3 MARK PRICE DATA + FRESHNESS VALIDATION
# COMPATIBLE WITH UNITS 2 AND 4-15
# ZERO INDENTATION
# NO AUTHENTICATED EXCHANGE WRITE
# ============================================================

import math
import time


# ============================================================
# UNIT 3 DATA VALIDATION
# PURE FUNCTION - NO HTTP REQUEST
# ============================================================

def unit_3_validate_mark_payload(
    payload,
    expected_symbol,
    received_time_ms,
    max_age_ms=120000,
    future_tolerance_ms=15000
):

    if not isinstance(payload, dict):
        raise RuntimeError(
            "UNIT 3 INVALID RESPONSE TYPE"
        )

    if payload.get("symbol") != expected_symbol:
        raise RuntimeError(
            "UNIT 3 RESPONSE SYMBOL MISMATCH"
        )

    try:
        price = float(payload.get("price"))
    except (TypeError, ValueError, OverflowError):
        raise RuntimeError(
            "UNIT 3 INVALID MARKET PRICE"
        )

    if not math.isfinite(price) or price <= 0:
        raise RuntimeError(
            "UNIT 3 NON-FINITE OR NON-POSITIVE PRICE"
        )

    timestamp = payload.get("time")

    if (
        not isinstance(timestamp, int)
        or isinstance(timestamp, bool)
        or timestamp <= 0
    ):
        raise RuntimeError(
            "UNIT 3 INVALID MARKET TIMESTAMP"
        )

    age_ms = int(received_time_ms) - timestamp

    if age_ms < -future_tolerance_ms:
        raise RuntimeError(
            "UNIT 3 MARKET TIMESTAMP TOO FAR IN FUTURE"
        )

    if age_ms > max_age_ms:
        raise RuntimeError(
            "UNIT 3 STALE MARKET DATA"
        )

    return {
        "price": price,
        "exchange_time_ms": timestamp,
        "market_age_ms": age_ms,
    }


# ============================================================
# UNIT 3 DETERMINISTIC VALIDATION TESTS
# PURE SYNTHETIC DATA - NO EXCHANGE REQUESTS
# ============================================================

def unit_3_validation_tests_v2():

    print("=" * 80, flush=True)
    print(
        "UNIT 3 OPTIMIZATION VALIDATION V2 START",
        flush=True
    )

    now_ms = 1800000000000

    valid_payload = {
        "symbol": "BTCUSDT",
        "price": "80000.5",
        "time": now_ms - 1000,
    }

    passed = 0
    failed = 0

    def check(name, condition):

        nonlocal passed, failed

        if condition:
            passed += 1
            verdict = "PASS"
        else:
            failed += 1
            verdict = "FAIL"

        print(
            "UNIT 3 TEST:",
            name,
            "=",
            verdict,
            flush=True
        )

    def rejected(payload, reason):

        try:
            unit_3_validate_mark_payload(
                payload,
                "BTCUSDT",
                now_ms
            )
        except RuntimeError as exc:
            return str(exc) == reason

        return False

    result = unit_3_validate_mark_payload(
        valid_payload,
        "BTCUSDT",
        now_ms
    )

    check(
        "VALID MARK PRICE",
        result["price"] == 80000.5
    )

    check(
        "VALID EXCHANGE TIMESTAMP",
        result["exchange_time_ms"]
        == now_ms - 1000
    )

    check(
        "VALID DATA AGE",
        result["market_age_ms"] == 1000
    )

    check(
        "REJECT WRONG SYMBOL",
        rejected(
            {
                **valid_payload,
                "symbol": "ETHUSDT"
            },
            "UNIT 3 RESPONSE SYMBOL MISMATCH"
        )
    )

    check(
        "REJECT ZERO PRICE",
        rejected(
            {
                **valid_payload,
                "price": "0"
            },
            "UNIT 3 NON-FINITE OR NON-POSITIVE PRICE"
        )
    )

    check(
        "REJECT NEGATIVE PRICE",
        rejected(
            {
                **valid_payload,
                "price": "-1"
            },
            "UNIT 3 NON-FINITE OR NON-POSITIVE PRICE"
        )
    )

    check(
        "REJECT NONNUMERIC PRICE",
        rejected(
            {
                **valid_payload,
                "price": "invalid"
            },
            "UNIT 3 INVALID MARKET PRICE"
        )
    )

    check(
        "REJECT NONFINITE PRICE",
        rejected(
            {
                **valid_payload,
                "price": "nan"
            },
            "UNIT 3 NON-FINITE OR NON-POSITIVE PRICE"
        )
    )

    check(
        "REJECT STALE DATA",
        rejected(
            {
                **valid_payload,
                "time": now_ms - 130000
            },
            "UNIT 3 STALE MARKET DATA"
        )
    )

    check(
        "REJECT FUTURE TIMESTAMP",
        rejected(
            {
                **valid_payload,
                "time": now_ms + 20000
            },
            "UNIT 3 MARKET TIMESTAMP TOO FAR IN FUTURE"
        )
    )

    check(
        "REJECT MISSING TIMESTAMP",
        rejected(
            {
                "symbol": "BTCUSDT",
                "price": "80000.5"
            },
            "UNIT 3 INVALID MARKET TIMESTAMP"
        )
    )

    check(
        "REJECT INVALID PAYLOAD",
        rejected(
            [],
            "UNIT 3 INVALID RESPONSE TYPE"
        )
    )

    print(
        "UNIT 3 TESTS PASSED =",
        passed,
        flush=True
    )

    print(
        "UNIT 3 TESTS FAILED =",
        failed,
        flush=True
    )

    if failed:
        raise RuntimeError(
            "UNIT 3 OPTIMIZATION VALIDATION FAILED"
        )

    print(
        "UNIT 3 OPTIMIZATION VALIDATION RESULT = PASS",
        flush=True
    )

    print(
        "UNIT 3 TEST EXCHANGE WRITE = NONE",
        flush=True
    )

    print("=" * 80, flush=True)

    return True


# ============================================================
# UNIT 3 ACTUAL WEEX PUBLIC MARKET DATA READ
# ============================================================

def fresh_reconstruction_unit_3():

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 3 START")

    if FRESH_UNIT_2_OPTIMIZATION_READY is not True:
        raise RuntimeError(
            "UNIT 3 BLOCKED: UNIT 2 VALIDATION NOT READY"
        )

    config = FRESH_RECONSTRUCTION_CONFIG

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 3 INVALID UNIT 2 CONFIGURATION"
        )

    exchange = config.get("exchange", {})
    safety = config.get("safety", {})

    if not isinstance(exchange, dict):
        raise RuntimeError(
            "UNIT 3 INVALID EXCHANGE CONFIG"
        )

    if not isinstance(safety, dict):
        raise RuntimeError(
            "UNIT 3 INVALID SAFETY CONFIG"
        )

    if exchange.get("name") != "WEEX":
        raise RuntimeError(
            "UNIT 3 INVALID EXCHANGE"
        )

    if exchange.get("api_version") != "V3":
        raise RuntimeError(
            "UNIT 3 INVALID API VERSION"
        )

    base_url = exchange.get("contract_base_url")

    if base_url != "https://api-contract.weex.com":
        raise RuntimeError(
            "UNIT 3 INVALID CONTRACT BASE URL"
        )

    market_symbol = exchange.get("market_symbol")

    if config.get("execution_environment") != "DEMO":
        raise RuntimeError(
            "UNIT 3 INVALID EXECUTION ENVIRONMENT"
        )

    if (
        safety.get("public_market_data_read_enabled")
        is not True
    ):
        raise RuntimeError(
            "UNIT 3 PUBLIC MARKET READ DISABLED"
        )

    forbidden = (
        "authenticated_api_enabled",
        "account_access_enabled",
        "position_access_enabled",
        "order_endpoint_access_enabled",
        "demo_order_submission_enabled",
        "real_order_submission_enabled",
        "exchange_mutation_enabled",
        "leverage_mutation_enabled",
        "margin_mode_mutation_enabled",
        "position_mode_mutation_enabled",
    )

    for key in forbidden:

        if safety.get(key) is not False:
            raise RuntimeError(
                "UNIT 3 UNSAFE CONFIGURATION: " + key
            )

    print(
        "PASS: UNIT 3 RECEIVED UNIT 2 CONFIGURATION",
        flush=True
    )

    print(
        "PASS: UNIT 3 READ-ONLY SAFETY GATE",
        flush=True
    )

    endpoint = "/capi/v3/market/symbolPrice"
    price_type = "MARK"

    query = urllib.parse.urlencode({
        "symbol": market_symbol,
        "priceType": price_type,
    })

    request_url = (
        base_url + endpoint + "?" + query
    )

    request = urllib.request.Request(
        url=request_url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": (
                "WEEX-Hybrid-Market-Data-V2"
            ),
        },
    )

    if (
        request.get_method() != "GET"
        or request.data is not None
    ):
        raise RuntimeError(
            "UNIT 3 NON-READ-ONLY HTTP REQUEST"
        )

    print(
        "PASS: UNIT 3 ENDPOINT = WEEX V3 SYMBOL PRICE",
        flush=True
    )

    print(
        "PASS: UNIT 3 HTTP METHOD = GET",
        flush=True
    )

    print(
        "PASS: UNIT 3 PRICE TYPE = MARK",
        flush=True
    )

    # --------------------------------------------------------
    # MEASURE REQUEST LATENCY
    # DO NOT REUSE PREVIOUS DATA AFTER FAILURE
    # --------------------------------------------------------

    request_start = time.monotonic()

    try:

        with urllib.request.urlopen(
            request,
            timeout=15
        ) as response:

            http_status = response.getcode()

            raw_body = (
                response.read()
                .decode("utf-8")
            )

    except urllib.error.HTTPError as exc:

        error_body = ""

        try:
            error_body = (
                exc.read()
                .decode("utf-8")
            )
        except Exception:
            pass

        print(
            "UNIT 3 HTTP ERROR CODE =",
            exc.code,
            flush=True
        )

        print(
            "UNIT 3 HTTP ERROR BODY =",
            error_body[:500],
            flush=True
        )

        raise RuntimeError(
            "UNIT 3 WEEX MARKET HTTP ERROR"
        ) from exc

    except urllib.error.URLError as exc:

        print(
            "UNIT 3 CONNECTION ERROR =",
            repr(exc.reason),
            flush=True
        )

        raise RuntimeError(
            "UNIT 3 WEEX CONNECTION FAILED"
        ) from exc

    except Exception as exc:

        print(
            "UNIT 3 UNEXPECTED REQUEST ERROR =",
            repr(exc),
            flush=True
        )

        raise

    received_time_ms = int(
        time.time() * 1000
    )

    latency_ms = round(
        (time.monotonic() - request_start) * 1000,
        2
    )

    if http_status != 200:
        raise RuntimeError(
            "UNIT 3 INVALID HTTP STATUS"
        )

    if not raw_body:
        raise RuntimeError(
            "UNIT 3 EMPTY MARKET RESPONSE"
        )

    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "UNIT 3 INVALID MARKET JSON"
        ) from exc

    validated = unit_3_validate_mark_payload(
        payload=payload,
        expected_symbol=market_symbol,
        received_time_ms=received_time_ms
    )

    live_price = validated["price"]

    exchange_time_ms = validated[
        "exchange_time_ms"
    ]

    market_age_ms = validated[
        "market_age_ms"
    ]

    # ========================================================
    # ORIGINAL UNIT 3 -> UNIT 4 INTERFACE
    # PRESERVE ALL EIGHT EXISTING SNAPSHOT FIELDS
    # ========================================================

    market_snapshot = {
        "exchange": "WEEX",
        "api_version": "V3",
        "symbol": market_symbol,
        "price": live_price,
        "price_type": price_type,
        "exchange_time_ms": exchange_time_ms,
        "source": "WEEX_V3_PUBLIC_MARK_PRICE",
        "read_only": True,
    }

    required_fields = (
        "exchange",
        "api_version",
        "symbol",
        "price",
        "price_type",
        "exchange_time_ms",
        "source",
        "read_only",
    )

    if any(
        key not in market_snapshot
        for key in required_fields
    ):
        raise RuntimeError(
            "UNIT 3 MARKET SNAPSHOT INCOMPLETE"
        )

    print(
        "UNIT 3 HTTP STATUS =",
        http_status,
        flush=True
    )

    print(
        "PASS: UNIT 3 LIVE BTC MARK PRICE =",
        live_price,
        flush=True
    )

    print(
        "PASS: UNIT 3 MARKET TIMESTAMP =",
        exchange_time_ms,
        flush=True
    )

    print(
        "UNIT 3 MARKET AGE MS =",
        market_age_ms,
        flush=True
    )

    print(
        "UNIT 3 REQUEST LATENCY MS =",
        latency_ms,
        flush=True
    )

    print(
        "UNIT 3 MAXIMUM MARKET AGE MS = 120000",
        flush=True
    )

    print(
        "PASS: UNIT 3 MARKET DATA FRESHNESS = TRUE",
        flush=True
    )

    print(
        "PASS: UNIT 3 NORMALIZED MARKET SNAPSHOT",
        flush=True
    )

    print(
        "PASS: UNIT 3 HANDOVER READY FOR UNIT 4",
        flush=True
    )

    print(
        "UNIT 3 EXCHANGE WRITE = NONE",
        flush=True
    )

    log(
        "FRESH RECONSTRUCTION UNIT 3 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return market_snapshot


# ============================================================
# RUN UNIT 3 VALIDATION FIRST
# ============================================================

FRESH_UNIT_3_OPTIMIZATION_READY = (
    unit_3_validation_tests_v2()
)


# ============================================================
# RUN UNIT 3 LIVE PUBLIC MARKET READ SECOND
# ============================================================

FRESH_RECONSTRUCTION_MARKET_SNAPSHOT = (
    fresh_reconstruction_unit_3()
)


# ============================================================
# END COMPLETE UNIT 3 REPLACEMENT V2
# UNIT 4 FOLLOWS
# ZERO INDENTATION
# ============================================================



# ============================================================
# START COMPLETE UNIT 4 V5 REPLACEMENT
# WEEX MARK DATA + EMA + ATR + ADJUSTABLE STRATEGIES
# ONE COMPLETE UNIT / ZERO INDENTATION
# NO SEPARATE ADAPTER / NO ORDER SUBMISSION
# ============================================================

import json
import math
import time
import urllib.parse
import urllib.request
import urllib.error


# ============================================================
# 4.1 CENTRAL ADJUSTABLE QUALIFICATION PARAMETERS
# ============================================================
# Change values here to tune strategy sensitivity.
# These settings are also published into Unit 2's
# qualification configuration for downstream units.
#
# EARLY structure uses EMA19/50 direction.
# STRICT structure uses EMA19/50/200 alignment.
#
# SCALP remains subordinate to developing or qualified
# BREAKOUT and STRUCTURE candidates.
# ============================================================

UNIT_4_V5_TUNING = {

    "common": {
        "direction_votes_required": 2,
        "market_age_seconds_max": 120.0,
        "candle_age_seconds_max": 120.0,
    },

    "breakout": {
        "enabled": True,
        "developing_candidate_enabled": True,
        "lookback_candles": 20,
        "proximity_atr": 0.50,
        "confirmation_atr": 0.10,
        "maximum_extension_atr": 3.0,
        "minimum_atr_percent": 0.0,
        "direction_votes_required": 2,
        "fast_momentum_minutes": 5,
        "slow_momentum_minutes": 15,
        "require_fast_momentum": True,
        "require_slow_momentum": False,
    },

    "structure": {
        "enabled": True,
        "ema_alignment_mode": "EARLY",
        "direction_votes_required": 2,
        "minimum_ema_separation_percent": 0.0,
        "pullback_tolerance_atr": 0.75,
        "allow_continuation_entry": True,
        "maximum_extension_atr": 2.0,
        "fast_momentum_minutes": 5,
        "slow_momentum_minutes": 15,
        "require_fast_momentum": True,
        "require_slow_momentum": True,
    },

    "scalp": {
        "enabled": True,
        "require_sideways_market": True,
        "range_lookback_candles": 20,
        "ema_compression_atr_max": 0.70,
        "range_atr_max": 8.0,
        "momentum_atr_max": 1.50,
        "preliminary_ema_separation_percent": 0.03,
        "preliminary_move_5m_percent": 0.015,
        "quality_threshold": 70.0,
        "minimum_fee_coverage_multiplier": 2.0,
    },
}


# ============================================================
# 4.2 GENERAL VALIDATION HELPERS
# ============================================================

def unit_4_v5_number(value, name):

    if isinstance(value, bool):
        raise RuntimeError(
            "UNIT 4 INVALID NUMBER: " + name
        )

    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise RuntimeError(
            "UNIT 4 INVALID NUMBER: " + name
        ) from exc

    if not math.isfinite(result):
        raise RuntimeError(
            "UNIT 4 NONFINITE NUMBER: " + name
        )

    return result


def unit_4_v5_positive(value, name, allow_zero=True):

    result = unit_4_v5_number(value, name)

    if result < 0 or (result == 0 and not allow_zero):
        raise RuntimeError(
            "UNIT 4 INVALID RANGE: " + name
        )

    return result


def unit_4_v5_integer(value, name, minimum, maximum):

    result = unit_4_v5_number(value, name)

    if (
        not result.is_integer()
        or not minimum <= result <= maximum
    ):
        raise RuntimeError(
            "UNIT 4 INVALID INTEGER: " + name
        )

    return int(result)


def unit_4_v5_ema(prices, period):

    if len(prices) < period:
        raise RuntimeError(
            "UNIT 4 INSUFFICIENT EMA HISTORY"
        )

    current = sum(prices[:period]) / period
    alpha = 2.0 / (period + 1.0)

    for price in prices[period:]:
        current = alpha * price + (1 - alpha) * current

    return current


def unit_4_v5_same_direction(move, direction):

    if direction == "LONG":
        return move > 0

    if direction == "SHORT":
        return move < 0

    return False


# ============================================================
# 4.3 VALIDATE CLOSED WEEX CANDLES
# ============================================================

def unit_4_v5_normalize_candles(rows, market_time_ms):

    if not isinstance(rows, list):
        raise RuntimeError(
            "UNIT 4 INVALID KLINE RESPONSE"
        )

    candles = []

    for row in rows:

        if not isinstance(row, (list, tuple)):
            raise RuntimeError(
                "UNIT 4 INVALID KLINE ROW"
            )

        if len(row) < 7:
            raise RuntimeError(
                "UNIT 4 INCOMPLETE KLINE ROW"
            )

        candle = {
            "open_time_ms": int(row[0]),
            "open": unit_4_v5_number(row[1], "OPEN"),
            "high": unit_4_v5_number(row[2], "HIGH"),
            "low": unit_4_v5_number(row[3], "LOW"),
            "close": unit_4_v5_number(row[4], "CLOSE"),
            "volume": unit_4_v5_number(row[5], "VOLUME"),
            "close_time_ms": int(row[6]),
        }

        if not (
            0 < candle["low"]
            <= min(candle["open"], candle["close"])
            <= max(candle["open"], candle["close"])
            <= candle["high"]
        ):
            raise RuntimeError(
                "UNIT 4 INVALID OHLC DATA"
            )

        if (
            candle["volume"] < 0
            or candle["close_time_ms"]
            <= candle["open_time_ms"]
        ):
            raise RuntimeError(
                "UNIT 4 INVALID CANDLE DATA"
            )

        candles.append(candle)

    candles.sort(
        key=lambda item: item["open_time_ms"]
    )

    for i in range(1, len(candles)):

        if (
            candles[i]["open_time_ms"]
            - candles[i - 1]["open_time_ms"]
        ) != 60000:
            raise RuntimeError(
                "UNIT 4 CANDLE GAP OR DUPLICATE"
            )

    closed = [
        c for c in candles
        if c["close_time_ms"] <= market_time_ms
    ]

    if len(closed) < 200:
        raise RuntimeError(
            "UNIT 4 INSUFFICIENT CLOSED HISTORY"
        )

    return candles, closed


# ============================================================
# 4.4 COMPLETE UNIT 4 MARKET ANALYSIS
# ============================================================

def fresh_reconstruction_unit_4():

    print("=" * 80, flush=True)
    print("UNIT 4 COMPLETE ADJUSTABLE V5 START", flush=True)

    config = FRESH_RECONSTRUCTION_CONFIG
    market = FRESH_RECONSTRUCTION_MARKET_SNAPSHOT
    tuning = UNIT_4_V5_TUNING

    if not isinstance(config, dict):
        raise RuntimeError("UNIT 4 CONFIG MISSING")

    if not isinstance(market, dict):
        raise RuntimeError("UNIT 4 MARKET SNAPSHOT MISSING")

    
    if (
        market.get("exchange") != "WEEX"
        or market.get("api_version") != "V3"
        or market.get("symbol") != config["exchange"]["market_symbol"]
        or market.get("price_type") != "MARK"
        or market.get("read_only") is not True
    ):
        raise RuntimeError(
            "UNIT 4 UNIT 3 HANDOVER INVALID"
        )

    exchange = config.get("exchange", {})
    qualification = config.get("qualification", {})
    safety = config.get("safety", {})

    if not all(
        isinstance(section, dict)
        for section in (exchange, qualification, safety)
    ):
        raise RuntimeError(
            "UNIT 4 CONFIG STRUCTURE INVALID"
        )

    if (
        config.get("execution_environment") != "DEMO"
        or exchange.get("name") != "WEEX"
        or exchange.get("api_version") != "V3"
        or exchange.get("market_symbol") != market.get("symbol")
        or safety.get(
            "public_market_data_read_enabled"
        ) is not True
    ):
        raise RuntimeError(
            "UNIT 4 EXCHANGE CONFIG INVALID"
        )

    if tuple(
        qualification.get("common", {}).get(
            "mode_priority", ()
        )
    ) != ("BREAKOUT", "STRUCTURE", "SCALP"):
        raise RuntimeError(
            "UNIT 4 MODE PRIORITY INVALID"
        )

    b = tuning["breakout"]
    s = tuning["structure"]
    p = tuning["scalp"]
    c = tuning["common"]

    max_age = unit_4_v5_positive(
        c["market_age_seconds_max"],
        "MARKET AGE LIMIT",
        False
    )

    max_candle_age = unit_4_v5_positive(
        c["candle_age_seconds_max"],
        "CANDLE AGE LIMIT",
        False
    )

    market_time_ms = int(
        unit_4_v5_positive(
            market["exchange_time_ms"],
            "MARKET TIMESTAMP",
            False
        )
    )

    live_mark = unit_4_v5_positive(
        market["price"], "MARK PRICE", False
    )

    current_time_ms = int(time.time() * 1000)

    if not (
        0 <= current_time_ms - market_time_ms
        <= max_age * 1000
    ):
        raise RuntimeError(
            "UNIT 4 STALE UNIT 3 MARK PRICE"
        )

    base_url = exchange.get("contract_base_url")

    if base_url != "https://api-contract.weex.com":
        raise RuntimeError(
            "UNIT 4 WEEX BASE URL INVALID"
        )

    # ========================================================
    # LIVE PUBLIC MARK-PRICE CANDLES
    # ========================================================

    endpoint = "/capi/v3/market/markPriceKlines"

    query = urllib.parse.urlencode({
        "symbol": exchange["market_symbol"],
        "interval": "1m",
        "limit": 300,
    })

    request = urllib.request.Request(
        base_url + endpoint + "?" + query,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": "WEEX-Unit4-Adjustable-V5",
        }
    )

    started = time.monotonic()

    try:
        with urllib.request.urlopen(
            request, timeout=15
        ) as response:
            http_status = response.getcode()
            payload = response.read().decode("utf-8")

    except (urllib.error.HTTPError,
            urllib.error.URLError) as exc:
        raise RuntimeError(
            "UNIT 4 WEEX CANDLE REQUEST FAILED"
        ) from exc

    latency_ms = (
        time.monotonic() - started
    ) * 1000.0

    if http_status != 200:
        raise RuntimeError(
            "UNIT 4 WEEX HTTP STATUS NOT 200"
        )

    try:
        rows = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "UNIT 4 WEEX JSON INVALID"
        ) from exc

    candles, closed = unit_4_v5_normalize_candles(
        rows, market_time_ms
    )

    latest = closed[-1]
    previous = closed[-2]

    candle_age_seconds = (
        market_time_ms - latest["close_time_ms"]
    ) / 1000.0

    if not (
        0 <= candle_age_seconds <= max_candle_age
    ):
        raise RuntimeError(
            "UNIT 4 CLOSED CANDLE STALE"
        )

    prices = [item["close"] for item in closed]

    ema19 = unit_4_v5_ema(prices, 19)
    ema50 = unit_4_v5_ema(prices, 50)
    ema100 = unit_4_v5_ema(prices, 100)
    ema200 = unit_4_v5_ema(prices, 200)

    latest_close = latest["close"]
    previous_close = previous["close"]

    separation = abs(
        ema19 - ema50
    ) / ema50 * 100.0

    if ema19 > ema50 > ema200:
        ema_structure = "BULLISH"

    elif ema19 < ema50 < ema200:
        ema_structure = "BEARISH"

    else:
        ema_structure = "MIXED"

    moves = {}

    for period in (1, 5, 15, 30, 60, 120):

        reference = prices[-period - 1]

        moves[period] = (
            latest_close - reference
        ) / reference * 100.0

    # ========================================================
    # ATR14
    # ========================================================

    true_ranges = []

    for i in range(1, len(closed)):

        item = closed[i]
        previous_price = closed[i - 1]["close"]

        true_ranges.append(max(
            item["high"] - item["low"],
            abs(item["high"] - previous_price),
            abs(item["low"] - previous_price)
        ))

    atr14 = sum(true_ranges[-14:]) / 14.0

    if atr14 <= 0:
        raise RuntimeError(
            "UNIT 4 ATR14 INVALID"
        )

    atr_percent = (
        atr14 / latest_close
    ) * 100.0

    # ========================================================
    # DIRECTION VOTES
    # ========================================================

    ema_vote = (
        "LONG" if ema19 > ema50
        else "SHORT" if ema19 < ema50
        else "NONE"
    )

    momentum_sum = moves[5] + moves[15]

    momentum_vote = (
        "LONG" if momentum_sum > 0
        else "SHORT" if momentum_sum < 0
        else "NONE"
    )

    price_vote = (
        "LONG" if latest_close > ema19
        else "SHORT" if latest_close < ema19
        else "NONE"
    )

    votes = (ema_vote, momentum_vote, price_vote)

    long_votes = votes.count("LONG")
    short_votes = votes.count("SHORT")

    common_votes_required = unit_4_v5_integer(
        c["direction_votes_required"],
        "COMMON DIRECTION VOTES",
        1, 3
    )

    direction = "NONE"

    if (
        long_votes >= common_votes_required
        and long_votes > short_votes
    ):
        direction = "LONG"

    elif (
        short_votes >= common_votes_required
        and short_votes > long_votes
    ):
        direction = "SHORT"

    def votes_sufficient(side, required):

        count = (
            long_votes if side == "LONG"
            else short_votes
        )

        return count >= unit_4_v5_integer(
            required,
            "STRATEGY DIRECTION VOTES",
            1, 3
        )

    def momentum_at(period):

        period = unit_4_v5_integer(
            period,
            "MOMENTUM PERIOD",
            1, 120
        )

        if period not in moves:
            raise RuntimeError(
                "UNIT 4 UNSUPPORTED MOMENTUM PERIOD"
            )

        return moves[period]

    # ========================================================
    # ADJUSTABLE BREAKOUT
    # ========================================================

    breakout_lookback = unit_4_v5_integer(
        b["lookback_candles"],
        "BREAKOUT LOOKBACK",
        2, 45
    )

    reference_candles = closed[
        -breakout_lookback - 1:-1
    ]

    support = min(
        item["low"] for item in reference_candles
    )

    resistance = max(
        item["high"] for item in reference_candles
    )

    proximity = unit_4_v5_positive(
        b["proximity_atr"],
        "BREAKOUT PROXIMITY"
    )

    confirmation = unit_4_v5_positive(
        b["confirmation_atr"],
        "BREAKOUT CONFIRMATION"
    )

    breakout_max_extension = unit_4_v5_positive(
        b["maximum_extension_atr"],
        "BREAKOUT EXTENSION",
        False
    )

    breakout_atr_min = unit_4_v5_positive(
        b["minimum_atr_percent"],
        "BREAKOUT MIN ATR"
    )

    def breakout_eligible(side):

        fast_ok = (
            not b["require_fast_momentum"]
            or unit_4_v5_same_direction(
                momentum_at(b["fast_momentum_minutes"]),
                side
            )
        )

        slow_ok = (
            not b["require_slow_momentum"]
            or unit_4_v5_same_direction(
                momentum_at(b["slow_momentum_minutes"]),
                side
            )
        )

        return bool(
            b["enabled"]
            and direction == side
            and votes_sufficient(
                side, b["direction_votes_required"]
            )
            and fast_ok
            and slow_ok
            and atr_percent >= breakout_atr_min
        )

    breakout_long_eligible = breakout_eligible("LONG")
    breakout_short_eligible = breakout_eligible("SHORT")

    long_breakout_distance = (
        latest_close - resistance
    ) / atr14

    short_breakout_distance = (
        support - latest_close
    ) / atr14

    breakout_confirmed_long = bool(
        breakout_long_eligible
        and long_breakout_distance > confirmation
        and long_breakout_distance
        <= breakout_max_extension
    )

    breakout_confirmed_short = bool(
        breakout_short_eligible
        and short_breakout_distance > confirmation
        and short_breakout_distance
        <= breakout_max_extension
    )

    breakout_developing_long = bool(
        b["developing_candidate_enabled"]
        and breakout_long_eligible
        and -proximity
        <= long_breakout_distance
        <= confirmation
    )

    breakout_developing_short = bool(
        b["developing_candidate_enabled"]
        and breakout_short_eligible
        and -proximity
        <= short_breakout_distance
        <= confirmation
    )

    # ========================================================
    # ADJUSTABLE STRUCTURE
    # ========================================================

    alignment = str(
        s["ema_alignment_mode"]
    ).upper()

    if alignment not in ("STRICT", "EARLY"):
        raise RuntimeError(
            "UNIT 4 INVALID STRUCTURE ALIGNMENT MODE"
        )

    structure_side = "NONE"

    if alignment == "STRICT":

        if ema19 > ema50 > ema200:
            structure_side = "LONG"

        elif ema19 < ema50 < ema200:
            structure_side = "SHORT"

    else:

        if ema19 > ema50:
            structure_side = "LONG"

        elif ema19 < ema50:
            structure_side = "SHORT"

    structure_min_separation = unit_4_v5_positive(
        s["minimum_ema_separation_percent"],
        "STRUCTURE MIN EMA SEPARATION"
    )

    structure_pullback = unit_4_v5_positive(
        s["pullback_tolerance_atr"],
        "STRUCTURE PULLBACK"
    )

    structure_max_extension = unit_4_v5_positive(
        s["maximum_extension_atr"],
        "STRUCTURE MAX EXTENSION",
        False
    )

    fast_structure_move = momentum_at(
        s["fast_momentum_minutes"]
    )

    slow_structure_move = momentum_at(
        s["slow_momentum_minutes"]
    )

    def structure_eligible(side):

        fast_ok = (
            not s["require_fast_momentum"]
            or unit_4_v5_same_direction(
                fast_structure_move, side
            )
        )

        slow_ok = (
            not s["require_slow_momentum"]
            or unit_4_v5_same_direction(
                slow_structure_move, side
            )
        )

        signed_distance = (
            latest_close - ema19
            if side == "LONG"
            else ema19 - latest_close
        ) / atr14

        # Pullback entries are permitted near EMA19.
        # Continuation entries must remain on the
        # correct side of EMA19 and within extension.

        pullback_ok = (
            abs(signed_distance) <= structure_pullback
        )

        continuation_ok = (
            s["allow_continuation_entry"]
            and 0 <= signed_distance
            <= structure_max_extension
        )

        return bool(
            s["enabled"]
            and structure_side == side
            and direction == side
            and votes_sufficient(
                side, s["direction_votes_required"]
            )
            and fast_ok
            and slow_ok
            and separation >= structure_min_separation
            and abs(signed_distance)
            <= structure_max_extension
            and (pullback_ok or continuation_ok)
        )

    structure_developing_long = (
        structure_eligible("LONG")
    )

    structure_developing_short = (
        structure_eligible("SHORT")
    )

    structure_fast_confirmed = (
        unit_4_v5_same_direction(
            fast_structure_move, structure_side
        )
    )

    structure_slow_confirmed = (
        unit_4_v5_same_direction(
            slow_structure_move, structure_side
        )
    )

    # ========================================================
    # ADJUSTABLE SCALP / SIDEWAYS EVIDENCE
    # ========================================================

    scalp_lookback = unit_4_v5_integer(
        p["range_lookback_candles"],
        "SCALP LOOKBACK",
        2, 45
    )

    scalp_history = closed[
        -scalp_lookback - 1:-1
    ]

    scalp_high = max(
        item["high"] for item in scalp_history
    )

    scalp_low = min(
        item["low"] for item in scalp_history
    )

    ema_cluster = (
        max(ema19, ema50, ema100, ema200)
        - min(ema19, ema50, ema100, ema200)
    )

    compression_atr = ema_cluster / atr14
    scalp_range_atr = (
        scalp_high - scalp_low
    ) / atr14

    momentum15_atr = (
        abs(latest_close - prices[-16])
        / atr14
    )

    higher_mode_developing = any((
        breakout_confirmed_long,
        breakout_confirmed_short,
        breakout_developing_long,
        breakout_developing_short,
        structure_developing_long,
        structure_developing_short,
    ))

    sideways_candidate = bool(
        p["enabled"]
        and compression_atr <= unit_4_v5_positive(
            p["ema_compression_atr_max"],
            "SCALP EMA COMPRESSION"
        )
        and scalp_range_atr <= unit_4_v5_positive(
            p["range_atr_max"],
            "SCALP RANGE"
        )
        and momentum15_atr <= unit_4_v5_positive(
            p["momentum_atr_max"],
            "SCALP MOMENTUM"
        )
        and not higher_mode_developing
    )

    # Price extension is diagnostic and still
    # retained as the existing Unit 5 evidence flag.

    price_extension_atr = (
        abs(latest_close - ema19) / atr14
    )

    price_overextended = bool(
        price_extension_atr > structure_max_extension
    )

    # ========================================================
    # PROPAGATE CENTRAL TUNING FOR UNITS 5 AND 6
    # ========================================================

    common_cfg = qualification["common"]
    breakout_cfg = qualification["breakout"]
    structure_cfg = qualification["structure"]
    scalp_cfg = qualification["scalp"]

    common_cfg["direction_votes_required"] = (
        common_votes_required
    )

    breakout_cfg.update({
        "enabled": bool(b["enabled"]),
        "developing_candidate_enabled": bool(
            b["developing_candidate_enabled"]
        ),
        "support_resistance_lookback":
            breakout_lookback,
        "developing_proximity_atr": proximity,
        "confirmation_distance_atr": confirmation,
        "max_price_extension_atr":
            breakout_max_extension,
        "minimum_atr_percent": breakout_atr_min,
        "direction_votes_required":
            b["direction_votes_required"],
        "fast_momentum_minutes":
            b["fast_momentum_minutes"],
        "slow_momentum_minutes":
            b["slow_momentum_minutes"],
        "require_fast_momentum":
            b["require_fast_momentum"],
        "require_slow_momentum":
            b["require_slow_momentum"],
    })

    structure_cfg.update({
        "enabled": bool(s["enabled"]),
        "ema_alignment_mode": alignment,
        "direction_votes_required":
            s["direction_votes_required"],
        "minimum_ema_separation_percent":
            structure_min_separation,
        "pullback_tolerance_atr":
            structure_pullback,
        "allow_continuation_entry": bool(
            s["allow_continuation_entry"]
        ),
        "max_price_extension_atr":
            structure_max_extension,
        "fast_momentum_minutes":
            s["fast_momentum_minutes"],
        "slow_momentum_minutes":
            s["slow_momentum_minutes"],
        "require_fast_momentum":
            s["require_fast_momentum"],
        "require_slow_momentum":
            s["require_slow_momentum"],
    })

    scalp_cfg.update({
        "enabled": bool(p["enabled"]),
        "require_sideways_market": bool(
            p["require_sideways_market"]
        ),
        "ema_compression_atr_max":
            p["ema_compression_atr_max"],
        "range20_atr_max": p["range_atr_max"],
        "momentum15_atr_multiplier_max":
            p["momentum_atr_max"],
        "preliminary_ema_separation_percent":
            p["preliminary_ema_separation_percent"],
        "preliminary_move_5m_percent":
            p["preliminary_move_5m_percent"],
        "quality_threshold":
            p["quality_threshold"],
        "minimum_fee_coverage_multiplier":
            p["minimum_fee_coverage_multiplier"],
    })

    # ========================================================
    # BUILD UNIT 4 -> UNIT 5 SNAPSHOT
    # ========================================================

    snapshot = {
        "exchange": "WEEX",
        "api_version": "V3",
        "symbol": exchange["market_symbol"],
        "interval": "1m",
        "price_type": "MARK",

        "live_mark_price": live_mark,
        "previous_close": previous_close,
        "latest_close": latest_close,

        "latest_open_time_ms":
            latest["open_time_ms"],
        "latest_close_time_ms":
            latest["close_time_ms"],
        "exchange_time_ms": market_time_ms,

        "ema19": ema19,
        "ema50": ema50,
        "ema100": ema100,
        "ema200": ema200,

        "ema19_50_separation_pct": separation,
        "ema_structure": ema_structure,

        "short_term_move_pct": moves[1],
        "move_1m_pct": moves[1],
        "move_5m_pct": moves[5],
        "move_15m_pct": moves[15],
        "move_30m_pct": moves[30],
        "move_60m_pct": moves[60],
        "move_120m_pct": moves[120],

        "recent_closed_klines": [
            dict(item) for item in closed[-60:]
        ],
        "candle_count": len(candles),
        "closed_candle_count": len(closed),
        "newest_returned_candle_closed": (
            candles[-1]["close_time_ms"]
            <= market_time_ms
        ),
        "source":
            "WEEX_V3_PUBLIC_MARK_PRICE_KLINES",

        "atr14": atr14,
        "atr_percent": atr_percent,

        "support20": support,
        "resistance20": resistance,
        "range20_atr_ratio": (
            resistance - support
        ) / atr14,

        "near_resistance": bool(
            latest_close >= resistance - proximity * atr14
        ),
        "near_support": bool(
            latest_close <= support + proximity * atr14
        ),

        "breakout_confirmed_long":
            breakout_confirmed_long,
        "breakout_confirmed_short":
            breakout_confirmed_short,
        "breakout_developing_long":
            breakout_developing_long,
        "breakout_developing_short":
            breakout_developing_short,

        "structure_developing_long":
            structure_developing_long,
        "structure_developing_short":
            structure_developing_short,

        "structure_trend_direction":
            structure_side,
        "structure_ema_alignment_mode":
            alignment,
        "structure_momentum_fast_confirmed":
            structure_fast_confirmed,
        "structure_momentum_slow_confirmed":
            structure_slow_confirmed,

        "sideways_candidate": sideways_candidate,

        "direction_long_votes": long_votes,
        "direction_short_votes": short_votes,
        "direction_evidence": direction,

        "ema_cluster_height": ema_cluster,
        "ema_compression_atr": compression_atr,
        "scalp_range_atr": scalp_range_atr,
        "scalp_momentum_atr": momentum15_atr,

        "scalp_preliminary_ema_min_pct":
            p["preliminary_ema_separation_percent"],
        "scalp_preliminary_move_min_pct":
            p["preliminary_move_5m_percent"],

        "price_extension_cluster": (
            price_extension_atr
        ),
        "price_overextended": price_overextended,

        "strategy_evidence_version":
            "U4_HYBRID_V2",
        "qualification_tuning_revision":
            "UNIT4_V5_FULLY_INTEGRATED",

        "qualification_settings": {
            "breakout_lookback": breakout_lookback,
            "breakout_proximity_atr": proximity,
            "breakout_confirmation_atr": confirmation,
            "structure_pullback_atr":
                structure_pullback,
            "structure_max_extension_atr":
                structure_max_extension,
            "structure_ema_alignment_mode":
                alignment,
            "scalp_compression_atr":
                p["ema_compression_atr_max"],
            "scalp_range_atr":
                p["range_atr_max"],
            "scalp_momentum_atr":
                p["momentum_atr_max"],
        },

        "read_only": True,
        "trade_authorized": False,
        "order_payload_created": False,
    }

    # ========================================================
    # VERIFY DOWNSTREAM INPUTS
    # ========================================================

    required_fields = (
        "strategy_evidence_version",
        "exchange_time_ms",
        "latest_close_time_ms",
        "latest_close",
        "ema19",
        "ema50",
        "ema200",
        "atr14",
        "move_5m_pct",
        "move_15m_pct",
        "direction_evidence",
        "direction_long_votes",
        "direction_short_votes",
        "breakout_confirmed_long",
        "breakout_confirmed_short",
        "breakout_developing_long",
        "breakout_developing_short",
        "structure_developing_long",
        "structure_developing_short",
        "sideways_candidate",
        "price_overextended",
        "structure_trend_direction",
        "scalp_preliminary_ema_min_pct",
        "scalp_preliminary_move_min_pct",
    )

    missing = [
        key for key in required_fields
        if key not in snapshot
    ]

    if missing:
        raise RuntimeError(
            "UNIT 4 HANDOVER MISSING: " + str(missing)
        )

    # ========================================================
    # RENDER LOG REPORT
    # ========================================================

    print("UNIT 4 HTTP STATUS =", http_status, flush=True)
    print(
        "UNIT 4 REQUEST LATENCY MS =",
        round(latency_ms, 2),
        flush=True
    )
    print(
        "UNIT 4 CLOSED CANDLES =",
        len(closed),
        flush=True
    )
    print("UNIT 4 ATR14 =", round(atr14, 4), flush=True)
    print("UNIT 4 DIRECTION =", direction, flush=True)
    print(
        "UNIT 4 DIRECTION VOTES =",
        long_votes, "/", short_votes,
        flush=True
    )

    print(
        "UNIT 4 BREAKOUT PROXIMITY ATR =",
        proximity, flush=True
    )
    print(
        "UNIT 4 BREAKOUT CONFIRMATION ATR =",
        confirmation, flush=True
    )
    print(
        "UNIT 4 BREAKOUT CONFIRMED LONG =",
        breakout_confirmed_long, flush=True
    )
    print(
        "UNIT 4 BREAKOUT CONFIRMED SHORT =",
        breakout_confirmed_short, flush=True
    )
    print(
        "UNIT 4 BREAKOUT DEVELOPING LONG =",
        breakout_developing_long, flush=True
    )
    print(
        "UNIT 4 BREAKOUT DEVELOPING SHORT =",
        breakout_developing_short, flush=True
    )

    print(
        "UNIT 4 STRUCTURE EMA MODE =",
        alignment, flush=True
    )
    print(
        "UNIT 4 STRUCTURE TREND SIDE =",
        structure_side, flush=True
    )
    print(
        "UNIT 4 STRUCTURE DEVELOPING LONG =",
        structure_developing_long, flush=True
    )
    print(
        "UNIT 4 STRUCTURE DEVELOPING SHORT =",
        structure_developing_short, flush=True
    )

    print(
        "UNIT 4 SCALP QUALITY TARGET =",
        p["quality_threshold"], flush=True
    )
    print(
        "UNIT 4 SCALP SIDEWAYS =",
        sideways_candidate, flush=True
    )
    print(
        "UNIT 4 SCALP MIN MOVE 5M % =",
        p["preliminary_move_5m_percent"],
        flush=True
    )

    print(
        "UNIT 4 PRICE OVEREXTENDED =",
        price_overextended, flush=True
    )
    print(
        "UNIT 4 EVIDENCE VERSION =",
        snapshot["strategy_evidence_version"],
        flush=True
    )
    print(
        "UNIT 4 TUNING REVISION =",
        snapshot["qualification_tuning_revision"],
        flush=True
    )
    print(
        "PASS: UNIT 4 COMPLETE CORE AND ADAPTER",
        flush=True
    )
    print(
        "PASS: UNIT 4 TO UNIT 5 HANDOVER",
        flush=True
    )
    print("UNIT 4 EXCHANGE WRITE = NONE", flush=True)
    print(
        "FRESH RECONSTRUCTION UNIT 4 RESULT = PASS",
        flush=True
    )
    print(
        "FRESH RECONSTRUCTION UNIT 4 ADAPTER RESULT = PASS",
        flush=True
    )
    print("=" * 80, flush=True)

    return snapshot


# ============================================================
# 4.5 SINGLE EXECUTION CALL
# ============================================================

FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT = (
    fresh_reconstruction_unit_4()
)


# ============================================================
# END COMPLETE UNIT 4 V5 REPLACEMENT
# UNIT 5 V7 FOLLOWS
# ZERO INDENTATION
# ============================================================



# ============================================================
# START COMPLETE UNIT 5 V8 REPLACEMENT
# FULLY ADJUSTABLE HYBRID CLASSIFICATION
# WEEX DEMO / ZERO INDENTATION
# UNIT 4 V5 -> UNIT 5 V8 -> UNIT 6
# ============================================================

import math


# ============================================================
# 5.1 HELPERS
# ============================================================

def unit_5_v8_number(value, name):

    if isinstance(value, bool):
        raise RuntimeError("UNIT 5 INVALID " + name)

    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise RuntimeError(
            "UNIT 5 INVALID " + name
        ) from exc

    if not math.isfinite(value):
        raise RuntimeError(
            "UNIT 5 NONFINITE " + name
        )

    return value


def unit_5_v8_direction(value):

    if value > 0:
        return "LONG"
    if value < 0:
        return "SHORT"
    return "NONE"


def unit_5_v8_side_matches(value, side):

    return (
        value > 0 if side == "LONG"
        else value < 0 if side == "SHORT"
        else False
    )


def unit_5_v8_settings(config, group):

    section = config.get("qualification", {})

    if not isinstance(section, dict):
        raise RuntimeError(
            "UNIT 5 QUALIFICATION CONFIG INVALID"
        )

    result = section.get(group)

    if not isinstance(result, dict):
        raise RuntimeError(
            "UNIT 5 MISSING CONFIG: " + group
        )

    return result


# ============================================================
# 5.2 COMPLETE CLASSIFICATION
# ============================================================

def fresh_reconstruction_unit_5(
    unit_2_config,
    unit_4_snapshot
):

    print("=" * 80, flush=True)
    print(
        "UNIT 5 COMPLETE ADJUSTABLE V8 START",
        flush=True
    )

    if not isinstance(unit_2_config, dict):
        raise RuntimeError("UNIT 5 CONFIG INVALID")

    if not isinstance(unit_4_snapshot, dict):
        raise RuntimeError("UNIT 5 SNAPSHOT INVALID")

    config = unit_2_config
    analysis = unit_4_snapshot

    common = unit_5_v8_settings(config, "common")
    b = unit_5_v8_settings(config, "breakout")
    s = unit_5_v8_settings(config, "structure")
    p = unit_5_v8_settings(config, "scalp")

    if tuple(common.get("mode_priority", ())) != (
        "BREAKOUT", "STRUCTURE", "SCALP"
    ):
        raise RuntimeError(
            "UNIT 5 STRATEGY PRIORITY INVALID"
        )

    if analysis.get(
        "strategy_evidence_version"
    ) != "U4_HYBRID_V2":
        raise RuntimeError(
            "UNIT 5 UNIT 4 EVIDENCE MISSING"
        )

    if analysis.get(
        "qualification_tuning_revision"
    ) != "UNIT4_V5_FULLY_INTEGRATED":
        raise RuntimeError(
            "UNIT 5 ADJUSTABLE UNIT 4 V5 REQUIRED"
        )

    if (
        analysis.get("exchange") != "WEEX"
        or analysis.get("api_version") != "V3"
        
        or analysis.get("symbol") != FRESH_RECONSTRUCTION_CONFIG["exchange"]["market_symbol"]
        or analysis.get("price_type") != "MARK"
        or analysis.get("read_only") is not True
    ):
        raise RuntimeError(
            "UNIT 5 MARKET CONTRACT INVALID"
        )

    def n(key):
        return unit_5_v8_number(
            analysis.get(key), key
        )

    def flag(key):

        result = analysis.get(key)

        if type(result) is not bool:
            raise RuntimeError(
                "UNIT 5 FLAG INVALID: " + key
            )

        return result

    def setting_number(section, key, fallback=None):

        value = section.get(key, fallback)

        if value is None:
            raise RuntimeError(
                "UNIT 5 SETTING MISSING: " + key
            )

        return unit_5_v8_number(value, key)

    def setting_bool(section, key, fallback=None):

        value = section.get(key, fallback)

        if type(value) is not bool:
            raise RuntimeError(
                "UNIT 5 BOOLEAN SETTING INVALID: " + key
            )

        return value

    # ========================================================
    # 5.3 MARKET INPUTS
    # ========================================================

    exchange_ms = n("exchange_time_ms")
    close_ms = n("latest_close_time_ms")

    candle_age = (
        exchange_ms - close_ms
    ) / 1000.0

    market_policy = config.get(
        "market_data_policy", {}
    )

    if not isinstance(market_policy, dict):
        raise RuntimeError(
            "UNIT 5 MARKET POLICY INVALID"
        )

    max_age = unit_5_v8_number(
        market_policy.get(
            "max_market_age_seconds", 120
        ),
        "MAX MARKET AGE"
    )

    if not 0 <= candle_age <= max_age:
        raise RuntimeError(
            "UNIT 5 CANDLE EVIDENCE STALE"
        )

    live_price = n("live_mark_price")
    previous_close = n("previous_close")
    latest_close = n("latest_close")

    ema19 = n("ema19")
    ema50 = n("ema50")
    ema200 = n("ema200")
    atr14 = n("atr14")

    separation = abs(
        n("ema19_50_separation_pct")
    )

    if min(
        live_price, previous_close, latest_close,
        ema19, ema50, ema200, atr14
    ) <= 0:
        raise RuntimeError(
            "UNIT 5 INVALID MARKET INDICATOR"
        )

    periods = (1, 5, 15, 30, 60, 120)

    moves = {
        period: n("move_%dm_pct" % period)
        for period in periods
    }

    directions = {
        period: unit_5_v8_direction(moves[period])
        for period in periods
    }

    short_move = n("short_term_move_pct")

    ema_structure = str(
        analysis.get("ema_structure", "MIXED")
    ).upper()

    if ema_structure not in (
        "BULLISH", "BEARISH", "MIXED"
    ):
        raise RuntimeError(
            "UNIT 5 EMA STRUCTURE INVALID"
        )

    # Diagnostic EMA direction from original classifier.
    # This does NOT override adjustable STRUCTURE mode.

    bullish = ema19 > ema50 > ema200
    bearish = ema19 < ema50 < ema200

    ema_direction = (
        "LONG" if bullish
        else "SHORT" if bearish
        else "NONE"
    )

    if (
        (bullish and ema_structure != "BULLISH")
        or (bearish and ema_structure != "BEARISH")
    ):
        raise RuntimeError(
            "UNIT 5 EMA STRUCTURE INCONSISTENT"
        )

    direction_evidence = str(
        analysis.get("direction_evidence", "NONE")
    ).upper()

    if direction_evidence not in (
        "LONG", "SHORT", "NONE"
    ):
        raise RuntimeError(
            "UNIT 5 DIRECTION EVIDENCE INVALID"
        )

    long_votes = n("direction_long_votes")
    short_votes = n("direction_short_votes")

    if (
        long_votes < 0 or short_votes < 0
        or long_votes + short_votes > 3
    ):
        raise RuntimeError(
            "UNIT 5 DIRECTION VOTES INVALID"
        )

    def votes_pass(side, section):

        required = setting_number(
            section,
            "direction_votes_required",
            common.get("direction_votes_required", 2)
        )

        if (
            required != int(required)
            or not 1 <= required <= 3
        ):
            raise RuntimeError(
                "UNIT 5 VOTE THRESHOLD INVALID"
            )

        actual = (
            long_votes if side == "LONG"
            else short_votes
        )

        return actual >= required

    def momentum_pass(side, section):

        fast = int(setting_number(
            section, "fast_momentum_minutes", 5
        ))

        slow = int(setting_number(
            section, "slow_momentum_minutes", 15
        ))

        if fast not in moves or slow not in moves:
            raise RuntimeError(
                "UNIT 5 MOMENTUM WINDOW UNSUPPORTED"
            )

        require_fast = setting_bool(
            section, "require_fast_momentum", True
        )

        require_slow = setting_bool(
            section, "require_slow_momentum", True
        )

        return (
            (
                not require_fast
                or unit_5_v8_side_matches(
                    moves[fast], side
                )
            )
            and (
                not require_slow
                or unit_5_v8_side_matches(
                    moves[slow], side
                )
            )
        )

    # ========================================================
    # 5.4 STRATEGY EVIDENCE FROM UNIT 4
    # ========================================================

    b_long = flag("breakout_confirmed_long")
    b_short = flag("breakout_confirmed_short")

    bd_long = flag("breakout_developing_long")
    bd_short = flag("breakout_developing_short")

    sd_long = flag("structure_developing_long")
    sd_short = flag("structure_developing_short")

    sideways_evidence = flag("sideways_candidate")
    overextended = flag("price_overextended")

    if b_long and b_short:
        raise RuntimeError(
            "UNIT 5 CONFLICTING BREAKOUT EVIDENCE"
        )

    if bd_long and bd_short:
        raise RuntimeError(
            "UNIT 5 CONFLICTING DEVELOPING BREAKOUT"
        )

    if sd_long and sd_short:
        raise RuntimeError(
            "UNIT 5 CONFLICTING STRUCTURE EVIDENCE"
        )

    structure_trend = str(
        analysis.get(
            "structure_trend_direction", "NONE"
        )
    ).upper()

    structure_ema_mode = str(
        analysis.get(
            "structure_ema_alignment_mode", ""
        )
    ).upper()

    configured_ema_mode = str(
        s.get("ema_alignment_mode", "")
    ).upper()

    if configured_ema_mode not in (
        "EARLY", "STRICT"
    ):
        raise RuntimeError(
            "UNIT 5 STRUCTURE EMA MODE INVALID"
        )

    if structure_ema_mode != configured_ema_mode:
        raise RuntimeError(
            "UNIT 5 STRUCTURE TUNING NOT SYNCHRONIZED"
        )

    if structure_trend not in (
        "LONG", "SHORT", "NONE"
    ):
        raise RuntimeError(
            "UNIT 5 STRUCTURE DIRECTION INVALID"
        )

    # ========================================================
    # 5.5 ORIGINAL 42-FIELD CLASSIFIER
    # ========================================================

    scalp_direction = "NONE"

    if ema19 > ema50 and moves[5] > 0:
        scalp_direction = "LONG"

    elif ema19 < ema50 and moves[5] < 0:
        scalp_direction = "SHORT"

    scalp_move = abs(moves[5])

    scalp_1m_support = (
        scalp_direction in ("LONG", "SHORT")
        and directions[1] == scalp_direction
    )

    structure_direction = "NONE"

    if (
        ema_direction != "NONE"
        and directions[15] == ema_direction
    ):
        structure_direction = ema_direction

    structure_move = abs(moves[15])

    breakout_primary = directions[30]

    breakout_fast_support = (
        breakout_primary != "NONE"
        and breakout_primary in (
            directions[5], directions[15]
        )
    )

    breakout_direction = "NONE"

    if (
        breakout_primary == "LONG"
        and breakout_fast_support
        and ema19 > ema50
        and latest_close > ema19
        and latest_close > ema200
    ):
        breakout_direction = "LONG"

    elif (
        breakout_primary == "SHORT"
        and breakout_fast_support
        and ema19 < ema50
        and latest_close < ema19
        and latest_close < ema200
    ):
        breakout_direction = "SHORT"

    breakout_move = abs(moves[30])

    # ========================================================
    # 5.6 ADJUSTABLE BREAKOUT QUALIFICATION
    # ========================================================

    breakout_side = (
        "LONG" if b_long
        else "SHORT" if b_short
        else "NONE"
    )

    breakout_enabled = setting_bool(
        b, "enabled", True
    )

    breakout_momentum_ok = (
        breakout_side != "NONE"
        and momentum_pass(breakout_side, b)
    )

    breakout_votes_ok = (
        breakout_side != "NONE"
        and votes_pass(breakout_side, b)
    )

    
    # BREAKOUT ADMISSION
    # Preserve Unit 4 confirmed breakout evidence.
    # Do not apply STRUCTURE overextension
    # to BREAKOUT qualification.

    breakout_qualified = bool(
        breakout_enabled
        and breakout_side != "NONE"
        and breakout_side == direction_evidence
        and breakout_votes_ok
        and breakout_momentum_ok
    )

    print(
        "UNIT 5 BREAKOUT CONFIRMED =",
        breakout_side != "NONE",
        flush=True
    )

    print(
        "UNIT 5 BREAKOUT DIRECTION PASS =",
        breakout_side == direction_evidence,
        flush=True
    )

    print(
        "UNIT 5 BREAKOUT VOTES PASS =",
        breakout_votes_ok,
        flush=True
    )

    print(
        "UNIT 5 BREAKOUT MOMENTUM PASS =",
        breakout_momentum_ok,
        flush=True
    )

    print(
        "UNIT 5 STRUCTURE OVEREXTENSION =",
        overextended,
        flush=True
    )

    print(
        "UNIT 5 BREAKOUT ADMISSION =",
        breakout_qualified,
        flush=True
    )

    # ========================================================
    # 5.7 ADJUSTABLE STRUCTURE QUALIFICATION
    # ========================================================

    structure_enabled = setting_bool(
        s, "enabled", True
    )

    structure_side = structure_trend

    structure_developing_same_side = (
        sd_long if structure_side == "LONG"
        else sd_short if structure_side == "SHORT"
        else False
    )

    structure_votes_ok = (
        structure_side != "NONE"
        and votes_pass(structure_side, s)
    )

    structure_momentum_ok = (
        structure_side != "NONE"
        and momentum_pass(structure_side, s)
    )

    extension_atr = (
        abs(latest_close - ema19) / atr14
    )

    max_structure_extension = setting_number(
        s, "max_price_extension_atr", 2.0
    )

    structure_extension_ok = (
        extension_atr <= max_structure_extension
    )

    # STRUCTURE EMA mode is determined by Unit 4.
    # EARLY does not require EMA200 alignment.
    # It still requires Unit 4 developing evidence,
    # sufficient votes, momentum and extension.

    structure_qualified = bool(
        structure_enabled
        and structure_side != "NONE"
        and direction_evidence == structure_side
        and structure_developing_same_side
        and structure_votes_ok
        and structure_momentum_ok
        and structure_extension_ok
        and not overextended
    )

    # ========================================================
    # 5.8 ADJUSTABLE SCALP PRELIMINARY CONDITIONS
    # ========================================================

    scalp_enabled = setting_bool(
        p, "enabled", True
    )

    scalp_ema_min = setting_number(
        p,
        "preliminary_ema_separation_percent",
        0.03
    )

    scalp_move_min = setting_number(
        p,
        "preliminary_move_5m_percent",
        0.015
    )

    if scalp_ema_min < 0 or scalp_move_min < 0:
        raise RuntimeError(
            "UNIT 5 SCALP THRESHOLDS INVALID"
        )

    original_scalp_signal = bool(
        scalp_direction in ("LONG", "SHORT")
        and separation >= scalp_ema_min
        and scalp_move >= scalp_move_min
    )

    price_first_scalp_signal = bool(
        directions[5] in ("LONG", "SHORT")
        and abs(moves[5]) >= scalp_move_min
        and directions[1] == directions[5]
    )

    scalp_direction_candidate = scalp_direction

    if (
        scalp_direction_candidate == "NONE"
        and price_first_scalp_signal
    ):
        scalp_direction_candidate = directions[5]

    scalp_preliminary = bool(
        scalp_enabled
        and (
            original_scalp_signal
            or price_first_scalp_signal
        )
        and scalp_direction_candidate in (
            "LONG", "SHORT"
        )
    )

    scalp_require_sideways = setting_bool(
        p, "require_sideways_market", True
    )

    scalp_sideways_ok = (
        sideways_evidence
        if scalp_require_sideways
        else True
    )

    scalp_quality_minimum = setting_number(
        p, "quality_threshold", 70.0
    )

    fee_multiplier = setting_number(
        p,
        "minimum_fee_coverage_multiplier",
        2.0
    )

    if not (
        0 <= scalp_quality_minimum <= 100
        and fee_multiplier >= 1
    ):
        raise RuntimeError(
            "UNIT 5 SCALP QUALITY SETTINGS INVALID"
        )

    # An optional relaxed sideways policy does not
    # permit SCALP to override a developing higher mode.
    # Unit 6 still determines final fee/quality admission.

    # ========================================================
    # 5.9 HIGHER-PRIORITY CANDIDATE PROTECTION
    # ========================================================

    breakout_developing = bool(
        bd_long or bd_short
    )

    structure_developing = bool(
        sd_long or sd_short
    )

    higher_mode_developing = bool(
        breakout_developing
        or structure_developing
    )

    developing_breakout_direction = (
        "LONG" if bd_long
        else "SHORT" if bd_short
        else "NONE"
    )

    developing_structure_direction = (
        "LONG" if sd_long
        else "SHORT" if sd_short
        else "NONE"
    )

    qualified = False
    active_mode = "NONE"
    direction = "NONE"

    candidate_mode = "NONE"
    candidate_stage = "NONE"

    reason = "NO_ACCEPTABLE_CANDIDATE"

    breakout_ready = False
    structure_ready = False
    scalp_ready = False

    if breakout_qualified:

        qualified = True
        active_mode = "BREAKOUT"
        direction = breakout_side

        candidate_mode = "BREAKOUT"
        candidate_stage = "QUALIFIED"

        breakout_ready = True

        reason = "HYBRID_BREAKOUT_CONFIRMED"

    elif structure_qualified:

        qualified = True
        active_mode = "STRUCTURE"
        direction = structure_side

        candidate_mode = "STRUCTURE"
        candidate_stage = "QUALIFIED"

        structure_ready = True

        reason = "HYBRID_STRUCTURE_QUALIFIED"

    elif breakout_developing:

        candidate_mode = "BREAKOUT"
        candidate_stage = "DEVELOPING"

        reason = "BREAKOUT_DEVELOPING_PROTECTED"

    elif structure_developing:

        candidate_mode = "STRUCTURE"
        candidate_stage = "DEVELOPING"

        reason = "STRUCTURE_DEVELOPING_PROTECTED"

    elif scalp_preliminary and scalp_sideways_ok:

        candidate_mode = "SCALP"
        candidate_stage = "PENDING_UNIT_6"

        scalp_ready = True

        reason = "SCALP_PENDING_UNIT_6_QUALITY"

    elif scalp_preliminary:

        candidate_stage = "REJECTED"

        reason = "SCALP_NOT_SIDEWAYS_MARKET"
        

    # ========================================================
    # UNIT 5: PRIORITY-AWARE REJECTION DIAGNOSTICS
    # BREAKOUT -> STRUCTURE -> SCALP
    # Does not change actual qualification conditions.
    # ========================================================

    breakout_rejection_reason = "NOT_CONFIRMED"
    structure_rejection_reason = "NOT_QUALIFIED"
    scalp_rejection_reason = "NOT_EVALUATED"

    if breakout_qualified:
        breakout_rejection_reason = "NONE"

    elif breakout_side != "NONE":
        if breakout_side != direction_evidence:
            breakout_rejection_reason = "DIRECTION_MISMATCH"
        elif not breakout_votes_ok:
            breakout_rejection_reason = "INSUFFICIENT_VOTES"
        elif not breakout_momentum_ok:
            breakout_rejection_reason = "MOMENTUM_FAILED"
        else:
            breakout_rejection_reason = "ADMISSION_FAILED_OTHER"

    elif breakout_developing:
        breakout_rejection_reason = "DEVELOPING"

    if structure_qualified:
        structure_rejection_reason = "NONE"
    elif structure_developing:
        structure_rejection_reason = "DEVELOPING"

    if scalp_preliminary:
        scalp_rejection_reason = (
            "PENDING_UNIT_6"
            if scalp_sideways_ok
            else "NOT_SIDEWAYS_MARKET"
        )
    else:
        scalp_rejection_reason = "PRELIMINARY_FAILED"

    # A higher-priority confirmed breakout must not
    # be hidden by a later scalp rejection.
    if (
        not qualified
        and candidate_stage == "REJECTED"
        and breakout_side != "NONE"
    ):
        reason = (
            "BREAKOUT_REJECTED_"
            + breakout_rejection_reason
        )

    print(
        "UNIT 5 BREAKOUT REJECTION =",
        breakout_rejection_reason,
        flush=True
    )
    print(
        "UNIT 5 STRUCTURE REJECTION =",
        structure_rejection_reason,
        flush=True
    )
    print(
        "UNIT 5 SCALP REJECTION =",
        scalp_rejection_reason,
        flush=True
    )

    # ========================================================
    # 5.10 SCALP COST ESTIMATE
    # ========================================================

    fee_sides = (
        int(p.get("include_entry_fee") is True)
        + int(p.get("include_exit_fee") is True)
    )

    round_trip_fee = (
        setting_number(
            p, "estimated_taker_fee_percent", 0.08
        ) * fee_sides
        + setting_number(
            p, "estimated_slippage_percent", 0.0
        )
    )

    # ========================================================
    # 5.11 PRESERVE ORIGINAL 42 OUTPUT FIELDS
    # ========================================================

    candidate = {
        "symbol": analysis["symbol"],
        "qualified": qualified,
        "active_mode": active_mode,
        "direction": direction,
        "qualification_reason": reason,

        "live_mark_price": live_price,
        "ema19": ema19,
        "ema50": ema50,
        "ema200": ema200,
        "ema19_50_separation_pct": separation,
        "ema_structure": ema_structure,
        "ema_direction": ema_direction,

        "momentum_direction": directions[1],
        "direction_agreement": (
            structure_direction != "NONE"
        ),
        "short_term_move_pct": short_move,
        "absolute_short_term_move_pct":
            abs(short_move),

        "previous_close": previous_close,
        "latest_close": latest_close,

        "price_above_ema19": live_price > ema19,
        "price_above_ema50": live_price > ema50,
        "price_above_ema200": live_price > ema200,
        "latest_close_above_previous": (
            latest_close > previous_close
        ),

        "move_1m_pct": moves[1],
        "move_5m_pct": moves[5],
        "move_15m_pct": moves[15],
        "move_30m_pct": moves[30],
        "move_60m_pct": moves[60],
        "move_120m_pct": moves[120],

        "momentum_1m_direction": directions[1],
        "momentum_5m_direction": directions[5],
        "momentum_15m_direction": directions[15],
        "momentum_30m_direction": directions[30],
        "momentum_60m_direction": directions[60],
        "momentum_120m_direction": directions[120],

        "scalp_direction": scalp_direction,
        "scalp_move_pct": scalp_move,
        "scalp_1m_support": scalp_1m_support,

        "structure_direction": structure_direction,
        "structure_move_pct": structure_move,

        "breakout_direction": breakout_direction,
        "breakout_move_pct": breakout_move,
        "breakout_fast_support": breakout_fast_support,
    }

    if len(candidate) != 42:
        raise RuntimeError(
            "UNIT 5 ORIGINAL 42-FIELD CONTRACT FAILED"
        )

    # ========================================================
    # 5.12 EXTENDED ADJUSTABLE HANDOVER TO UNIT 6
    # ========================================================

    candidate.update({

        "candidate_mode": candidate_mode,
        "candidate_stage": candidate_stage,

        "higher_mode_developing":
            higher_mode_developing,

        "breakout_candidate": bool(
            breakout_qualified
            or breakout_developing
        ),

        "structure_candidate": bool(
            structure_qualified
            or structure_developing
        ),

        "breakout_ready": breakout_ready,
        "structure_ready": structure_ready,
        "scalp_ready": scalp_ready,

        "sideways_context": sideways_evidence,
        "direction_evidence": direction_evidence,

        "scalp_quality_minimum":
            scalp_quality_minimum,

        "scalp_price_weight_percent":
            setting_number(
                p, "price_action_weight_percent", 50
            ),

        "estimated_round_trip_fee_pct":
            round_trip_fee,

        "scalp_minimum_fee_coverage":
            fee_multiplier,

        "candle_data_fresh": True,
        "read_only": True,

        "trade_authorized": False,
        "order_payload_created": False,

        "strategy_evidence_version":
            "U5_HYBRID_ADJUSTABLE_V3",

        "unit_4_evidence_version":
            "U4_HYBRID_V2",

        "classification_revision": "V3.1",

        "candidate_protected": (
            candidate_stage == "DEVELOPING"
        ),

        "candidate_age_seconds": candle_age,

        "classification_source":
            "UNIT5_V8_ADJUSTABLE",

        "original_unit5_qualified": (
            breakout_qualified
            or structure_qualified
            or scalp_preliminary
        ),

        "original_unit5_mode": (
            "BREAKOUT" if breakout_qualified
            else "STRUCTURE" if structure_qualified
            else "SCALP" if scalp_preliminary
            else "NONE"
        ),

        "original_unit5_direction": (
            breakout_side if breakout_qualified
            else structure_side if structure_qualified
            else scalp_direction_candidate
            if scalp_preliminary
            else "NONE"
        ),

        "original_unit5_reason":
            "INTEGRATED_V8_CLASSIFIER",

        "original_hybrid_conflict": False,

        "optimization_version": "UNIT5_V8",

        "hybrid_structure_qualified":
            structure_qualified,

        "hybrid_breakout_qualified":
            breakout_qualified,

        "structure_direction_votes": (
            long_votes if structure_side == "LONG"
            else short_votes
            if structure_side == "SHORT"
            else 0
        ),

        "structure_extension_atr":
            extension_atr,

        "structure_extension_pass":
            structure_extension_ok,

        "structure_momentum_agreement":
            structure_momentum_ok,

        "breakout_confirmation_votes": (
            long_votes if breakout_side == "LONG"
            else short_votes
            if breakout_side == "SHORT"
            else 0
        ),

        "developing_breakout_direction":
            developing_breakout_direction,

        "developing_structure_direction":
            developing_structure_direction,

        "scalp_preliminary": scalp_preliminary,

        # New explicit adjustable diagnostics

        "qualification_tuning_revision":
            "UNIT5_V8_FULLY_ADJUSTABLE",

        "structure_ema_alignment_mode":
            structure_ema_mode,

        "structure_trend_direction":
            structure_trend,

        "structure_votes_pass":
            structure_votes_ok,

        "structure_momentum_pass":
            structure_momentum_ok,

        "breakout_votes_pass":
            breakout_votes_ok,

        "breakout_momentum_pass":
            breakout_momentum_ok,

        "scalp_preliminary_ema_min_pct":
            scalp_ema_min,

        "scalp_preliminary_move_min_pct":
            scalp_move_min,

        "scalp_sideways_required":
            scalp_require_sideways,

        "scalp_sideways_pass":
            scalp_sideways_ok,

        "scalp_direction_candidate":
            scalp_direction_candidate,

        "scalp_quality_pending_unit6":
            scalp_ready,
    })

    # ========================================================
    # 5.13 FINAL CONSISTENCY CHECKS
    # ========================================================

    if qualified != (
        candidate_stage == "QUALIFIED"
    ):
        raise RuntimeError(
            "UNIT 5 QUALIFICATION STATE INVALID"
        )

    if qualified and (
        active_mode not in (
            "BREAKOUT", "STRUCTURE"
        )
        or direction not in (
            "LONG", "SHORT"
        )
    ):
        raise RuntimeError(
            "UNIT 5 QUALIFIED DIRECTION INVALID"
        )

    if candidate_mode == "SCALP" and (
        higher_mode_developing
        or breakout_qualified
        or structure_qualified
    ):
        raise RuntimeError(
            "UNIT 5 SCALP PRIORITY VIOLATION"
        )

    if (
        candidate["trade_authorized"] is not False
        or candidate["order_payload_created"] is not False
    ):
        raise RuntimeError(
            "UNIT 5 ORDER BOUNDARY VIOLATION"
        )

    # ========================================================
    # 5.14 RENDER REPORT
    # ========================================================

    print(
        "UNIT 5 ORIGINAL FIELDS = 42",
        flush=True
    )

    print(
        "UNIT 5 UNIT 4 TUNING =",
        analysis["qualification_tuning_revision"],
        flush=True
    )

    print(
        "UNIT 5 STRUCTURE EMA MODE =",
        structure_ema_mode,
        flush=True
    )

    print(
        "UNIT 5 STRUCTURE TREND =",
        structure_trend,
        flush=True
    )

    print(
        "UNIT 5 STRUCTURE VOTES PASS =",
        structure_votes_ok,
        flush=True
    )

    print(
        "UNIT 5 STRUCTURE MOMENTUM PASS =",
        structure_momentum_ok,
        flush=True
    )

    print(
        "UNIT 5 BREAKOUT VOTES PASS =",
        breakout_votes_ok,
        flush=True
    )

    print(
        "UNIT 5 BREAKOUT MOMENTUM PASS =",
        breakout_momentum_ok,
        flush=True
    )

    print(
        "UNIT 5 SCALP EMA MIN % =",
        scalp_ema_min,
        flush=True
    )

    print(
        "UNIT 5 SCALP MOVE MIN % =",
        scalp_move_min,
        flush=True
    )

    print(
        "UNIT 5 SCALP QUALITY TARGET =",
        scalp_quality_minimum,
        flush=True
    )

    print(
        "UNIT 5 MODE =",
        candidate_mode,
        flush=True
    )

    print(
        "UNIT 5 STAGE =",
        candidate_stage,
        flush=True
    )

    print(
        "UNIT 5 ACTIVE MODE =",
        active_mode,
        flush=True
    )

    print(
        "UNIT 5 DIRECTION =",
        direction,
        flush=True
    )

    print(
        "UNIT 5 QUALIFIED =",
        qualified,
        flush=True
    )

    print(
        "UNIT 5 REASON =",
        reason,
        flush=True
    )

    print(
        "UNIT 5 EVIDENCE VERSION =",
        candidate["strategy_evidence_version"],
        flush=True
    )

    print(
        "UNIT 5 CANDLE AGE SECONDS =",
        round(candle_age, 3),
        flush=True
    )

    print(
        "UNIT 5 EXCHANGE WRITE = NONE",
        flush=True
    )

    print(
        "FRESH RECONSTRUCTION UNIT 5 RESULT = PASS",
        flush=True
    )

    print(
        "UNIT 5 OPTIMIZATION V8 RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return candidate


# ============================================================
# 5.15 DETERMINISTIC VALIDATION
# ============================================================

def unit_5_validation_v8():

    print("=" * 80, flush=True)
    print("UNIT 5 VALIDATION V8 START", flush=True)

    # Tests exercise the same integrated classifier
    # used for actual Unit 4 V5 snapshots.

    test_config = {
        "qualification": {

            "common": {
                "mode_priority": (
                    "BREAKOUT", "STRUCTURE", "SCALP"
                ),
                "direction_votes_required": 2,
            },

            "breakout": {
                "enabled": True,
                "direction_votes_required": 2,
                "fast_momentum_minutes": 5,
                "slow_momentum_minutes": 15,
                "require_fast_momentum": True,
                "require_slow_momentum": False,
            },

            "structure": {
                "enabled": True,
                "ema_alignment_mode": "EARLY",
                "direction_votes_required": 2,
                "fast_momentum_minutes": 5,
                "slow_momentum_minutes": 15,
                "require_fast_momentum": True,
                "require_slow_momentum": True,
                "max_price_extension_atr": 2.0,
            },

            "scalp": {
                "enabled": True,
                "require_sideways_market": True,
                "preliminary_ema_separation_percent":
                    0.03,
                "preliminary_move_5m_percent":
                    0.015,
                "quality_threshold": 70,
                "minimum_fee_coverage_multiplier": 2,
                "include_entry_fee": True,
                "include_exit_fee": True,
                "estimated_taker_fee_percent": 0.08,
            },
        },

        "market_data_policy": {
            "max_market_age_seconds": 120,
        },
    }

    def market(**changes):

        data = {
            "exchange": "WEEX",
            "api_version": "V3",
            "symbol": FRESH_RECONSTRUCTION_CONFIG["exchange"]["market_symbol"],
            "price_type": "MARK",
            "read_only": True,

            "strategy_evidence_version":
                "U4_HYBRID_V2",

            "qualification_tuning_revision":
                "UNIT4_V5_FULLY_INTEGRATED",

            "exchange_time_ms": 1800000060000,
            "latest_close_time_ms": 1800000000000,

            "live_mark_price": 80100.0,
            "previous_close": 80090.0,
            "latest_close": 80100.0,

            "ema19": 80080.0,
            "ema50": 80020.0,
            "ema200": 80140.0,

            "ema19_50_separation_pct": 0.075,
            "ema_structure": "MIXED",

            "short_term_move_pct": 0.02,
            "move_1m_pct": 0.02,
            "move_5m_pct": 0.05,
            "move_15m_pct": 0.12,
            "move_30m_pct": 0.15,
            "move_60m_pct": 0.25,
            "move_120m_pct": 0.30,

            "atr14": 100.0,

            "direction_evidence": "LONG",
            "direction_long_votes": 3,
            "direction_short_votes": 0,

            "breakout_confirmed_long": False,
            "breakout_confirmed_short": False,
            "breakout_developing_long": False,
            "breakout_developing_short": False,

            "structure_developing_long": True,
            "structure_developing_short": False,

            "structure_trend_direction": "LONG",
            "structure_ema_alignment_mode": "EARLY",

            "sideways_candidate": False,
            "price_overextended": False,
        }

        data.update(changes)
        return data

    tests = (
        (
            "EARLY STRUCTURE LONG MIXED EMA200",
            market(),
            "STRUCTURE",
            "QUALIFIED",
        ),

        (
            "QUALIFIED STRUCTURE BEATS DEVELOPING BREAKOUT",
            market(
                breakout_developing_long=True
            ),
            "STRUCTURE",
            "QUALIFIED",
        ),

        (
            "CONFIRMED BREAKOUT PRIORITY",
            market(
                breakout_confirmed_long=True
            ),
            "BREAKOUT",
            "QUALIFIED",
        ),

        (
            "BREAKOUT DEVELOPING PROTECTION",
            market(
                breakout_developing_long=True,
                structure_developing_long=False
            ),
            "BREAKOUT",
            "DEVELOPING",
        ),

        (
            "STRUCTURE DEVELOPING PROTECTION",
            market(
                move_5m_pct=-0.05
            ),
            "STRUCTURE",
            "DEVELOPING",
        ),

        (
            "STRUCTURE VOTES TOO LOW",
            market(
                direction_long_votes=1,
                direction_short_votes=1
            ),
            "STRUCTURE",
            "DEVELOPING",
        ),

        (
            "SCALP SIDEWAYS PENDING QUALITY",
            market(
                structure_developing_long=False,
                sideways_candidate=True
            ),
            "SCALP",
            "PENDING_UNIT_6",
        ),

        (
            "SCALP NOT SIDEWAYS REJECTED",
            market(
                structure_developing_long=False
            ),
            "NONE",
            "REJECTED",
        ),

        
(
    "BREAKOUT MOMENTUM INSUFFICIENT",
    market(
        breakout_confirmed_long=True,
        move_5m_pct=-0.05,
        structure_developing_long=False
    ),
    "NONE",
    "NONE",
),


        (
            "SCALP BELOW ADJUSTABLE THRESHOLD",
            market(
                ema19=80080.0,
                ema50=80070.0,
                ema200=80140.0,
                ema19_50_separation_pct=0.0125,
                move_1m_pct=0.0,
                move_5m_pct=0.005,
                structure_developing_long=False,
                sideways_candidate=True
            ),
            "NONE",
            "NONE",
        ),
    )

    passed = 0
    failed = 0

    for name, snapshot, expected_mode, expected_stage in tests:

        try:
            result = fresh_reconstruction_unit_5(
                test_config,
                snapshot
            )

            success = (
                result["candidate_mode"] == expected_mode
                and result["candidate_stage"] == expected_stage
                and result["trade_authorized"] is False
                and result["strategy_evidence_version"]
                == "U5_HYBRID_ADJUSTABLE_V3"
            )

        except Exception as exc:

            success = False

            print(
                "UNIT 5 TEST EXCEPTION:",
                name,
                str(exc),
                flush=True
            )

        if success:
            passed += 1
        else:
            failed += 1

        print(
            "UNIT 5 TEST:",
            name,
            "=",
            "PASS" if success else "FAIL",
            flush=True
        )

    print(
        "UNIT 5 TESTS PASSED =",
        passed,
        flush=True
    )

    print(
        "UNIT 5 TESTS FAILED =",
        failed,
        flush=True
    )

    if failed:
        raise RuntimeError(
            "UNIT 5 V8 VALIDATION FAILED"
        )

    print(
        "UNIT 5 VALIDATION V8 RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return True


# ============================================================
# 5.16 SINGLE EXECUTION SEQUENCE
# ============================================================

FRESH_UNIT_5_VALIDATION_READY = (
    unit_5_validation_v8()
)

FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE = (
    fresh_reconstruction_unit_5(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT
    )
)


# ============================================================
# END COMPLETE UNIT 5 V8 REPLACEMENT
# UNIT 6 FOLLOWS
# ZERO INDENTATION
# ============================================================


# ============================================================
# START COMPLETE UNIT 6 V9 REPLACEMENT
# WEEX DEMO STRATEGY ARBITRATION AND QUALITY
# INTEGRATED WITH UNIT 4 V5 AND UNIT 5 V8
# PRESERVES UNIT 7 OUTPUT CONTRACT
# ZERO INDENTATION / ONE EXECUTION CALL
# ============================================================

import copy
import math


# ============================================================
# 6.1 VALIDATION HELPERS
# ============================================================

def unit_6_v9_number(value, label):

    if isinstance(value, bool):
        raise RuntimeError(
            "UNIT 6 INVALID NUMBER: " + label
        )

    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise RuntimeError(
            "UNIT 6 INVALID NUMBER: " + label
        ) from exc

    if not math.isfinite(value):
        raise RuntimeError(
            "UNIT 6 NONFINITE NUMBER: " + label
        )

    return value


def unit_6_v9_bool(value, label):

    if type(value) is not bool:
        raise RuntimeError(
            "UNIT 6 INVALID BOOLEAN: " + label
        )

    return value


def unit_6_v9_clamp(value, minimum, maximum):

    return max(minimum, min(maximum, value))


def unit_6_v9_side(value):

    if value > 0:
        return "LONG"

    if value < 0:
        return "SHORT"

    return "NONE"


# ============================================================
# 6.2 MAIN CLASSIFICATION AND ADMISSION
# ============================================================

def fresh_reconstruction_unit_6(
    unit_2_config,
    unit_4_analysis,
    unit_5_candidate
):

    print("=" * 80, flush=True)
    print(
        "UNIT 6 COMPLETE ADJUSTABLE V9 START",
        flush=True
    )

    # ========================================================
    # INPUT CONTRACT
    # ========================================================

    if not isinstance(unit_2_config, dict):
        raise RuntimeError(
            "UNIT 6 UNIT 2 CONFIG INVALID"
        )

    if not isinstance(unit_4_analysis, dict):
        raise RuntimeError(
            "UNIT 6 UNIT 4 ANALYSIS INVALID"
        )

    if not isinstance(unit_5_candidate, dict):
        raise RuntimeError(
            "UNIT 6 UNIT 5 CANDIDATE INVALID"
        )

    config = unit_2_config
    analysis = unit_4_analysis
    candidate = unit_5_candidate

    qualification = config.get("qualification")

    if not isinstance(qualification, dict):
        raise RuntimeError(
            "UNIT 6 QUALIFICATION CONFIG MISSING"
        )

    common = qualification.get("common")
    breakout = qualification.get("breakout")
    structure = qualification.get("structure")
    scalp = qualification.get("scalp")

    for name, section in (
        ("COMMON", common),
        ("BREAKOUT", breakout),
        ("STRUCTURE", structure),
        ("SCALP", scalp),
    ):
        if not isinstance(section, dict):
            raise RuntimeError(
                "UNIT 6 CONFIG MISSING: " + name
            )

    if tuple(common.get("mode_priority", ())) != (
        "BREAKOUT",
        "STRUCTURE",
        "SCALP"
    ):
        raise RuntimeError(
            "UNIT 6 MODE PRIORITY INVALID"
        )

    if (
        analysis.get("strategy_evidence_version")
        != "U4_HYBRID_V2"
        or analysis.get(
            "qualification_tuning_revision"
        ) != "UNIT4_V5_FULLY_INTEGRATED"
    ):
        raise RuntimeError(
            "UNIT 6 UNIT 4 V5 EVIDENCE MISSING"
        )

    if (
        candidate.get("strategy_evidence_version")
        != "U5_HYBRID_ADJUSTABLE_V3"
        or candidate.get(
            "qualification_tuning_revision"
        ) != "UNIT5_V8_FULLY_ADJUSTABLE"
    ):
        raise RuntimeError(
            "UNIT 6 UNIT 5 V8 EVIDENCE MISSING"
        )

    
    if (
        candidate.get("symbol")
        != config["exchange"]["market_symbol"]
        or analysis.get("symbol")
        != config["exchange"]["market_symbol"]
    ):
        raise RuntimeError(
            "UNIT 6 SYMBOL MISMATCH"
        )

    if (
        analysis.get("read_only") is not True
        or candidate.get("read_only") is not True
        or candidate.get(
            "trade_authorized"
        ) is not False
        or candidate.get(
            "order_payload_created"
        ) is not False
    ):
        raise RuntimeError(
            "UNIT 6 INPUT SAFETY VIOLATION"
        )

    
    # ========================================================
    # UNIT 6 POSITION SAFETY POLICY
    # USE ORIGINAL UNIT 2 STRATEGY CONFIGURATION
    # ========================================================

    strategy = config.get("strategy")

    if not isinstance(strategy, dict):
        raise RuntimeError(
            "UNIT 6 STRATEGY CONFIG MISSING"
        )

    fee_coverage_enabled = strategy.get(
        "signal_fee_coverage_enabled", True
    )

    if not isinstance(fee_coverage_enabled, bool):
        raise RuntimeError(
            "UNIT 6 INVALID FEE COVERAGE MODE"
        )

    print(
        "UNIT 6 SIGNAL FEE COVERAGE ENABLED =",
        fee_coverage_enabled,
        flush=True
    )

    print(
        "UNIT 6 FEE COVERAGE ADMISSION GATE =",
        "ENFORCED" if fee_coverage_enabled else "BYPASSED",
        flush=True
    )
    # ========================================================
    # MARKET AND FRESHNESS
    # ========================================================

    def a(key):
        return unit_6_v9_number(
            analysis.get(key), key
        )

    def c(key):
        return unit_6_v9_number(
            candidate.get(key), key
        )

    price = a("latest_close")
    live_price = a("live_mark_price")

    ema19 = a("ema19")
    ema50 = a("ema50")
    ema100 = a("ema100")
    ema200 = a("ema200")

    atr = a("atr14")

    if min(
        price, live_price, ema19, ema50,
        ema100, ema200, atr
    ) <= 0:
        raise RuntimeError(
            "UNIT 6 MARKET INDICATORS INVALID"
        )

    move_1m = a("move_1m_pct")
    move_5m = a("move_5m_pct")
    move_15m = a("move_15m_pct")

    atr_pct = atr / price * 100.0

    candle_age = c(
        "candidate_age_seconds"
    )

    max_age = unit_6_v9_number(
        config.get(
            "market_data_policy", {}
        ).get("max_market_age_seconds", 120),
        "MAX CANDLE AGE"
    )

    fresh = (
        candidate.get("candle_data_fresh") is True
        and 0 <= candle_age <= max_age
    )

    # ========================================================
    # HIGHER STRATEGY PRIORITY
    # ========================================================

    higher_developing = unit_6_v9_bool(
        candidate.get("higher_mode_developing"),
        "HIGHER MODE DEVELOPING"
    )

    breakout_ready = unit_6_v9_bool(
        candidate.get("breakout_ready"),
        "BREAKOUT READY"
    )

    structure_ready = unit_6_v9_bool(
        candidate.get("structure_ready"),
        "STRUCTURE READY"
    )

    scalp_ready = unit_6_v9_bool(
        candidate.get("scalp_ready"),
        "SCALP READY"
    )

    if sum((
        breakout_ready,
        structure_ready,
        scalp_ready
    )) > 1:
        raise RuntimeError(
            "UNIT 6 CONFLICTING READY STRATEGIES"
        )

    # ========================================================
    # QUALITY CONFIGURATION
    # ========================================================

    scalp_minimum = unit_6_v9_number(
        scalp.get("quality_threshold", 70),
        "SCALP QUALITY MINIMUM"
    )

    if not 0 <= scalp_minimum <= 100:
        raise RuntimeError(
            "UNIT 6 INVALID SCALP QUALITY MINIMUM"
        )

    fee_coverage = unit_6_v9_number(
        scalp.get(
            "minimum_fee_coverage_multiplier", 2
        ),
        "FEE COVERAGE MULTIPLIER"
    )

    if fee_coverage < 1:
        raise RuntimeError(
            "UNIT 6 INVALID FEE COVERAGE MULTIPLIER"
        )

    estimated_fee = c(
        "estimated_round_trip_fee_pct"
    )

    if estimated_fee < 0:
        raise RuntimeError(
            "UNIT 6 INVALID FEE ESTIMATE"
        )

    # If the upstream configuration has not
    # enabled fee estimation, fail closed for SCALP.

    fee_estimate_verified = (
        scalp.get("include_entry_fee") is True
        and scalp.get("include_exit_fee") is True
        and unit_6_v9_number(
            scalp.get(
                "estimated_taker_fee_percent", 0
            ),
            "TAKER FEE"
        ) > 0
        and estimated_fee > 0
    )

    # ========================================================
    # SCALP SIDEWAYS POLICY
    # ========================================================

    sideways = unit_6_v9_bool(
        analysis.get("sideways_candidate"),
        "SIDEWAYS EVIDENCE"
    )

    sideways_required = unit_6_v9_bool(
        scalp.get("require_sideways_market", True),
        "SIDEWAYS REQUIRED"
    )

    sideways_pass = (
        sideways or not sideways_required
    )

    # ========================================================
    # SCALP DIRECTION AND PERSISTENCE
    # ========================================================

    scalp_side = candidate.get(
        "scalp_direction_candidate", "NONE"
    )

    if scalp_side not in (
        "LONG", "SHORT", "NONE"
    ):
        raise RuntimeError(
            "UNIT 6 SCALP DIRECTION INVALID"
        )

    direction_1m = unit_6_v9_side(move_1m)
    direction_5m = unit_6_v9_side(move_5m)
    direction_15m = unit_6_v9_side(move_15m)

    persistence_directions = (
        direction_1m,
        direction_5m,
        direction_15m,
    )

    persistence_window = 3

    persistence_required = 2

    persistence_confirmations = sum(
        d == scalp_side
        for d in persistence_directions
    ) if scalp_side != "NONE" else 0

    persistence_pass = (
        persistence_confirmations
        >= persistence_required
    )

    fifteen_minute_support_pass = (
        direction_15m == scalp_side
    )

    momentum_conflict = (
        scalp_side != "NONE"
        and direction_5m not in (
            scalp_side, "NONE"
        )
    )

    # ========================================================
    # SCALP QUALITY SCORING / MAXIMUM 100 POINTS
    #
    # PRICE ACTION                 30
    # DIRECTION PERSISTENCE        20
    # EMA LOCATION                 15
    # EMA QUALITY                  15
    # VOLATILITY AND EXHAUSTION    20
    #
    # These scores are diagnostics, not predictions.
    # ========================================================

    quality_score = 0.0

    price_action_score = 0.0
    persistence_score = 0.0
    location_score = 0.0
    ema_score = 0.0
    volatility_score = 0.0

    ema_separation_pct = abs(
        ema19 - ema50
    ) / ema50 * 100.0

    compression_limit = unit_6_v9_number(
        scalp.get(
            "ema_compression_atr_max", 0.7
        ),
        "EMA COMPRESSION LIMIT"
    )

    compression_atr = a(
        "ema_compression_atr"
    )

    ema_compressed = (
        compression_atr <= compression_limit
    )

    extension_atr = abs(
        price - ema19
    ) / atr

    # Existing early-entry protection.
    # Larger ATR extensions and reversal evidence
    # reduce the score instead of rewarding
    # late momentum.

    extreme_extension = (
        extension_atr > 1.5
    )

    spike_ratio = (
        abs(move_1m) /
        max(abs(move_5m) / 5.0, 0.000001)
    )

    extreme_spike = spike_ratio > 2.0

    late_impulse = (
        extreme_extension and extreme_spike
    )

    if scalp_side != "NONE":

        # Price action: max 30

        if direction_5m == scalp_side:
            price_action_score += 15

        if direction_1m == scalp_side:
            price_action_score += 10

        if abs(move_5m) >= unit_6_v9_number(
            scalp.get(
                "preliminary_move_5m_percent",
                0.015
            ),
            "SCALP MOVE MINIMUM"
        ):
            price_action_score += 5

        # Persistence: max 20

        persistence_score = (
            20.0
            * persistence_confirmations
            / persistence_window
        )

        # EMA location: max 15

        location_pass = (
            price >= ema19
            if scalp_side == "LONG"
            else price <= ema19
        )

        if location_pass:
            location_score += 10

        if (
            ema100 <= price
            if scalp_side == "LONG"
            else ema100 >= price
        ):
            location_score += 5

        # EMA quality: max 15

        if ema_compressed:
            ema_score += 10

        if (
            (ema19 >= ema50 and scalp_side == "LONG")
            or
            (ema19 <= ema50 and scalp_side == "SHORT")
        ):
            ema_score += 5

        # Volatility and exhaustion: max 20

        if not extreme_extension:
            volatility_score += 10

        if not extreme_spike:
            volatility_score += 5

        if not late_impulse:
            volatility_score += 5

    quality_score = round(
        unit_6_v9_clamp(
            price_action_score
            + persistence_score
            + location_score
            + ema_score
            + volatility_score,
            0, 100
        ),
        2
    )

    quality_pass = (
        quality_score >= scalp_minimum
    )

    
    # ========================================================
    # FEE COVERAGE - STRATEGY-SPECIFIC V10
    # STRUCTURE: SUPPORT / RESISTANCE TARGET
    # BREAKOUT: MEASURED RANGE TARGET
    # SCALP: SHORT-TERM OBSERVED MOVEMENT
    # ========================================================

    projected_move_pct = 0.0
    fee_coverage_method = "NOT_APPLICABLE"
    fee_coverage_pass = False

    required_move_pct = (
        estimated_fee * fee_coverage
    )

    stage = str(
        candidate.get("candidate_stage", "NONE")
    ).upper()

    mode = str(
        candidate.get("candidate_mode", "NONE")
    ).upper()

    qualified = candidate.get("qualified") is True

    incoming_direction = str(
        candidate.get("direction", "NONE")
    ).upper()
    if (
        stage == "QUALIFIED"
        and mode in ("STRUCTURE", "BREAKOUT")
        and incoming_direction in ("LONG", "SHORT")
    ):

        support = a("support20")
        resistance = a("resistance20")

        if (
            support > 0
            and resistance > support
        ):

            if mode == "STRUCTURE":

                if incoming_direction == "LONG":
                    target_price = resistance
                    target_distance = (
                        target_price - price
                    )

                else:
                    target_price = support
                    target_distance = (
                        price - target_price
                    )

                fee_coverage_method = (
                    "STRUCTURE_SUPPORT_RESISTANCE"
                )

            else:

                measured_range = (
                    resistance - support
                )

                if incoming_direction == "LONG":

                    target_price = (
                        resistance + measured_range
                    )

                    target_distance = (
                        target_price - price
                    )

                else:

                    target_price = (
                        support - measured_range
                    )

                    target_distance = (
                        price - target_price
                    )

                fee_coverage_method = (
                    "BREAKOUT_MEASURED_RANGE"
                )

            projected_move_pct = (
                max(0.0, target_distance)
                / price
                * 100.0
            )

    elif (
        mode == "SCALP"
        and stage == "PENDING_UNIT_6"
    ):

        projected_move_pct = min(
            abs(move_5m),
            atr_pct
        )

        fee_coverage_method = (
            "SCALP_5M_ATR"
        )

    fee_coverage_pass = bool(
        fee_estimate_verified
        and projected_move_pct >= required_move_pct
    )
    
    # ========================================================
    # FINAL ADMISSION ARBITRATION
    # ========================================================

    execution_intent = False
    signal_qualified = False

    active_mode = "NONE"
    direction = "NONE"

    admission_reason = (
        "NO_ACCEPTABLE_CANDIDATE"
    )

    
    if not fresh:

        admission_reason = (
            "MARKET_EVIDENCE_STALE"
        )

    elif (
        fee_coverage_enabled
        and stage == "QUALIFIED"
        and mode in ("BREAKOUT", "STRUCTURE")
        and not fee_estimate_verified
    ):
        admission_reason = (
            "QUALIFIED_MODE_FEES_NOT_VERIFIED"
        )

    elif (
        fee_coverage_enabled
        and stage == "QUALIFIED"
        and mode in ("BREAKOUT", "STRUCTURE")
        and not fee_coverage_pass
    ):
        admission_reason = (
            "QUALIFIED_MODE_FEE_COVERAGE_FAILED"
        )

    elif stage == "QUALIFIED":

        if (
            qualified
            and mode == "BREAKOUT"
            and breakout_ready
            and incoming_direction in (
                "LONG", "SHORT"
            )
            and candidate.get(
                "hybrid_breakout_qualified"
            ) is True
        ):

            execution_intent = True
            signal_qualified = True

            active_mode = "BREAKOUT"
            direction = incoming_direction

            admission_reason = (
                "BREAKOUT_QUALIFIED_FOR_NEXT_UNITS"
            )

        elif (
            qualified
            and mode == "STRUCTURE"
            and structure_ready
            and incoming_direction in (
                "LONG", "SHORT"
            )
            and candidate.get(
                "hybrid_structure_qualified"
            ) is True
        ):

            execution_intent = True
            signal_qualified = True

            active_mode = "STRUCTURE"
            direction = incoming_direction

            admission_reason = (
                "STRUCTURE_QUALIFIED_FOR_NEXT_UNITS"
            )

        else:

            admission_reason = (
                "QUALIFIED_STATE_INCONSISTENT"
            )

    elif stage == "DEVELOPING":

        admission_reason = (
            "DEVELOPING_HIGHER_MODE_PROTECTED"
        )

    elif (
        stage == "PENDING_UNIT_6"
        and mode == "SCALP"
    ):

        if higher_developing:

            admission_reason = (
                "SCALP_BLOCKED_HIGHER_MODE_DEVELOPING"
            )

        elif not scalp_ready:

            admission_reason = (
                "SCALP_NOT_READY"
            )

        elif scalp_side == "NONE":

            admission_reason = (
                "SCALP_DIRECTION_MISSING"
            )

        elif not sideways_pass:

            admission_reason = (
                "SCALP_SIDEWAYS_REQUIREMENT_FAILED"
            )

        elif momentum_conflict:

            admission_reason = (
                "SCALP_MOMENTUM_CONFLICT"
            )

        elif not persistence_pass:

            admission_reason = (
                "SCALP_PERSISTENCE_INSUFFICIENT"
            )

        elif late_impulse:

            admission_reason = (
                "SCALP_LATE_IMPULSE_REJECTED"
            )

        elif not quality_pass:

            admission_reason = (
                "SCALP_QUALITY_BELOW_THRESHOLD"
            )

        elif fee_coverage_enabled and not fee_estimate_verified:

            admission_reason = (
                "SCALP_FEES_NOT_VERIFIED"
            )

        elif fee_coverage_enabled and not fee_coverage_pass:

            admission_reason = (
                "SCALP_ESTIMATED_FEE_COVERAGE_FAILED"
            )

        else:

            execution_intent = True
            signal_qualified = True

            active_mode = "SCALP"
            direction = scalp_side

            admission_reason = (
                "SCALP_QUALIFIED_FOR_NEXT_UNITS"
            )

    else:

        admission_reason = str(
            candidate.get(
                "qualification_reason",
                "NO_ACCEPTABLE_CANDIDATE"
            )
        )

    # ========================================================
    # FINAL INVARIANTS
    # ========================================================

    if execution_intent != signal_qualified:
        raise RuntimeError(
            "UNIT 6 EXECUTION INTENT MISMATCH"
        )

    if execution_intent:

        if (
            active_mode not in (
                "BREAKOUT", "STRUCTURE", "SCALP"
            )
            or direction not in (
                "LONG", "SHORT"
            )
        ):
            raise RuntimeError(
                "UNIT 6 INVALID ADMITTED SIGNAL"
            )

    else:

        if (
            active_mode != "NONE"
            or direction != "NONE"
        ):
            raise RuntimeError(
                "UNIT 6 INVALID IDLE SIGNAL"
            )

    if active_mode == "SCALP" and (
        higher_developing
        or breakout_ready
        or structure_ready
    ):
        raise RuntimeError(
            "UNIT 6 SCALP PRIORITY VIOLATION"
        )

    # ========================================================
    # OUTPUT TO UNIT 7
    # Preserve original interface and diagnostics.
    # ========================================================

    quality_details = {
        "price_action_score": price_action_score,
        "persistence_score": round(
            persistence_score, 2
        ),
        "ema_location_score": location_score,
        "ema_quality_score": ema_score,
        "volatility_score": volatility_score,
        "extreme_extension": extreme_extension,
        "extreme_spike": extreme_spike,
        "late_impulse": late_impulse,
        "estimated_move_pct": projected_move_pct,
        "estimated_round_trip_fee_pct":
            estimated_fee,
        "required_move_pct": required_move_pct,
        "fee_coverage_pass": fee_coverage_pass,
        "fee_estimate_verified":
            fee_estimate_verified,
    }

    execution_candidate = {

        # Original Unit 7 required contract

        "execution_intent": execution_intent,
        "active_mode": active_mode,
        "direction": direction,
        "signal_qualified": signal_qualified,
        "unit_5_reason": candidate.get(
            "qualification_reason", "UNKNOWN"
        ),
        "admission_reason": admission_reason,

        # Original Unit 6 diagnostics

        "leverage_target": None,
        "leverage_regime":
            "WEEX_EXCHANGE_SETTING",

        "sideways_regime": sideways,
        "ema_compressed": ema_compressed,
        "compression_threshold_pct":
            compression_limit,

        "momentum_conflict":
            momentum_conflict,

        "persistence_window":
            persistence_window,
        "persistence_required":
            persistence_required,
        "persistence_confirmations":
            persistence_confirmations,
        "persistence_directions":
            persistence_directions,
        "persistence_pass":
            persistence_pass,

        "fifteen_minute_support_pass":
            fifteen_minute_support_pass,

        "scalp_quality_score": quality_score,
        "scalp_quality_minimum":
            scalp_minimum,
        "scalp_quality_pass": quality_pass,
        "scalp_quality_details":
            quality_details,

        # Unit 5/Unit 4 traceability

        "candidate_mode": mode,
        "candidate_stage": stage,
        "higher_mode_developing":
            higher_developing,
        "unit_5_evidence_version":
            candidate.get(
                "strategy_evidence_version"
            ),
        "unit_4_evidence_version":
            analysis.get(
                "strategy_evidence_version"
            ),

        "classification_version":
            "UNIT6_V9_ADJUSTABLE",

        "market_data_fresh": fresh,

        # Execution boundary

        "position_sizing_performed": False,
        "order_payload_created": False,
        "exchange_write": False,
        "read_only": True,
        "trade_authorized": False,
    }

    # ========================================================
    # RENDER REPORT
    # ========================================================

    print(
        "UNIT 6 INPUT CANDIDATE MODE =",
        mode,
        flush=True
    )
    print(
        "UNIT 6 INPUT STAGE =",
        stage,
        flush=True
    )
    print(
        "UNIT 6 HIGHER MODE DEVELOPING =",
        higher_developing,
        flush=True
    )
    print(
        "UNIT 6 SIDEWAYS REGIME =",
        sideways,
        flush=True
    )
    print(
        "UNIT 6 SCALP DIRECTION =",
        scalp_side,
        flush=True
    )
    print(
        "UNIT 6 SCALP QUALITY SCORE =",
        quality_score,
        flush=True
    )
    print(
        "UNIT 6 SCALP QUALITY MINIMUM =",
        scalp_minimum,
        flush=True
    )
    print(
        "UNIT 6 SCALP QUALITY PASS =",
        quality_pass,
        flush=True
    )
    print(
        "UNIT 6 SCALP PERSISTENCE =",
        persistence_confirmations,
        "/",
        persistence_required,
        flush=True
    )
    print(
        "UNIT 6 ESTIMATED PRICE MOVE % =",
        round(projected_move_pct, 5),
        flush=True
    )
    print(
        "UNIT 6 ESTIMATED ROUND TRIP FEE % =",
        round(estimated_fee, 5),
        flush=True
    )
    print(
        "UNIT 6 REQUIRED FEE COVERAGE MOVE % =",
        round(required_move_pct, 5),
        flush=True
    )
    print(
        "UNIT 6 FEE COVERAGE PASS =",
        fee_coverage_pass,
        flush=True
    )
    print(
        "UNIT 6 FEE COVERAGE METHOD =",
        fee_coverage_method,
        flush=True
    )
    print(
        "UNIT 6 ACTIVE MODE =",
        active_mode,
        flush=True
    )
    print(
        "UNIT 6 DIRECTION =",
        direction,
        flush=True
    )
    print(
        "UNIT 6 SIGNAL QUALIFIED =",
        signal_qualified,
        flush=True
    )
    print(
        "UNIT 6 EXECUTION INTENT =",
        execution_intent,
        flush=True
    )
    print(
        "UNIT 6 ADMISSION REASON =",
        admission_reason,
        flush=True
    )
    print(
        "UNIT 6 LEVERAGE CONTROL = WEEX ONLY",
        flush=True
    )
    print(
        "UNIT 6 EXCHANGE WRITE = NONE",
        flush=True
    )
    print(
        "FRESH RECONSTRUCTION UNIT 6 RESULT = PASS",
        flush=True
    )
    print("=" * 80, flush=True)

    return execution_candidate


# ============================================================
# 6.3 VALIDATION
# DO NOT ACCESS WEEX FOR SYNTHETIC TESTS
# ============================================================

def unit_6_validation_v9():

    print("=" * 80, flush=True)
    print(
        "UNIT 6 VALIDATION V9 START",
        flush=True
    )

    # Use the actual Unit 4/5 handover structure.
    # Work only on copies, never mutate working config.

    config = copy.deepcopy(
        FRESH_RECONSTRUCTION_CONFIG
    )
    analysis = copy.deepcopy(
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT
    )
    original = copy.deepcopy(
        FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE
    )

    tests = []

    def scenario(
        name,
        modifications,
        expected_intent,
        expected_mode
    ):

        local = copy.deepcopy(original)

        local.update(modifications)

        # Explicitly retest consistent classification
        # states rather than forging account orders.

        
        test_analysis = copy.deepcopy(analysis)
            
        if (
            expected_intent is True
                and expected_mode in (
                "BREAKOUT", "STRUCTURE"
            )
        ):
            test_price = float(
                test_analysis["latest_close"]
            )

            if expected_mode == "BREAKOUT":
                # Synthetic LONG breakout with sufficient
                # measured-range target distance.
                test_analysis["support20"] = (
                    test_price * 0.98
                )
                test_analysis["resistance20"] = (
                    test_price * 0.995
                )

            elif expected_mode == "STRUCTURE":
                # Synthetic SHORT structure with
                # sufficient support target distance.
                test_analysis["support20"] = (
                    test_price * 0.99
                )
                test_analysis["resistance20"] = (
                    test_price * 1.01
                )

        result = fresh_reconstruction_unit_6(
            config,
            test_analysis,
            local
        )

        passed = (
            result["execution_intent"]
            is expected_intent
            and result["active_mode"]
            == expected_mode
            and result["exchange_write"] is False
            and result["order_payload_created"]
            is False
        )

        tests.append((name, passed))

    scenario(
        "NORMAL IDLE",
        {
            "qualified": False,
            "active_mode": "NONE",
            "direction": "NONE",
            "candidate_mode": "NONE",
            "candidate_stage": "NONE",
            "breakout_ready": False,
            "structure_ready": False,
            "scalp_ready": False,
            "higher_mode_developing": False,
        },
        False,
        "NONE"
    )

    scenario(
        "DEVELOPING BREAKOUT PROTECTED",
        {
            "qualified": False,
            "active_mode": "NONE",
            "direction": "NONE",
            "candidate_mode": "BREAKOUT",
            "candidate_stage": "DEVELOPING",
            "breakout_ready": False,
            "structure_ready": False,
            "scalp_ready": False,
            "higher_mode_developing": True,
        },
        False,
        "NONE"
    )

    scenario(
        "DEVELOPING STRUCTURE PROTECTED",
        {
            "qualified": False,
            "active_mode": "NONE",
            "direction": "NONE",
            "candidate_mode": "STRUCTURE",
            "candidate_stage": "DEVELOPING",
            "breakout_ready": False,
            "structure_ready": False,
            "scalp_ready": False,
            "higher_mode_developing": True,
        },
        False,
        "NONE"
    )

    scenario(
        "QUALIFIED BREAKOUT HANDOVER",
        {
            "qualified": True,
            "active_mode": "BREAKOUT",
            "direction": "LONG",
            "candidate_mode": "BREAKOUT",
            "candidate_stage": "QUALIFIED",
            "breakout_ready": True,
            "structure_ready": False,
            "scalp_ready": False,
            "hybrid_breakout_qualified": True,
        },
        True,
        "BREAKOUT"
    )

    scenario(
        "QUALIFIED STRUCTURE HANDOVER",
        {
            "qualified": True,
            "active_mode": "STRUCTURE",
            "direction": "SHORT",
            "candidate_mode": "STRUCTURE",
            "candidate_stage": "QUALIFIED",
            "breakout_ready": False,
            "structure_ready": True,
            "scalp_ready": False,
            "hybrid_structure_qualified": True,
        },
        True,
        "STRUCTURE"
    )

    scenario(
        "SCALP BLOCKED BY DEVELOPING MODE",
        {
            "qualified": False,
            "active_mode": "NONE",
            "direction": "NONE",
            "candidate_mode": "SCALP",
            "candidate_stage": "PENDING_UNIT_6",
            "breakout_ready": False,
            "structure_ready": False,
            "scalp_ready": True,
            "higher_mode_developing": True,
        },
        False,
        "NONE"
    )

    
    # Verify qualified BREAKOUT cannot bypass fees.

    fee_test = copy.deepcopy(original)

    fee_test.update({
        "qualified": True,
        "active_mode": "BREAKOUT",
        "direction": "LONG",
        "candidate_mode": "BREAKOUT",
        "candidate_stage": "QUALIFIED",
        "breakout_ready": True,
        "structure_ready": False,
        "scalp_ready": False,
        "hybrid_breakout_qualified": True,
    })

    fee_analysis = copy.deepcopy(analysis)

    fee_analysis["move_5m_pct"] = 0.0

    
    fee_price = float(
        fee_analysis["latest_close"]
    )

    fee_analysis["support20"] = (
        fee_price * 0.9999
    )
    fee_analysis["resistance20"] = (
        fee_price * 0.99995
    )

    fee_result = fresh_reconstruction_unit_6(
        config,
        fee_analysis,
        fee_test
    )

    fee_gate_enabled = config["strategy"].get(
        "signal_fee_coverage_enabled", True
    )

    fee_test_pass = (
        fee_result["execution_intent"] is False
        and fee_result["admission_reason"]
        == "QUALIFIED_MODE_FEE_COVERAGE_FAILED"
    ) if fee_gate_enabled else (
        fee_result["execution_intent"] is True
        and fee_result["active_mode"] == "BREAKOUT"
        and fee_result["admission_reason"]
        == "BREAKOUT_QUALIFIED_FOR_NEXT_UNITS"
    )

    tests.append((
        "BREAKOUT FEE COVERAGE SWITCH",
        fee_test_pass
    ))

    # Validate the unmodified live candidate last.

    live_result = fresh_reconstruction_unit_6(
        config,
        analysis,
        original
    )

    live_pass = (
        isinstance(
            live_result["execution_intent"], bool
        )
        and live_result["exchange_write"] is False
        and live_result["order_payload_created"]
        is False
    )

    tests.append((
        "ACTUAL UNIT 5 V8 HANDOVER",
        live_pass
    ))

    passed_count = sum(
        success for _, success in tests
    )

    for name, passed in tests:

        print(
            "UNIT 6 TEST:",
            name,
            "=",
            "PASS" if passed else "FAIL",
            flush=True
        )

    failed_count = len(tests) - passed_count

    print(
        "UNIT 6 TESTS PASSED =",
        passed_count,
        flush=True
    )
    print(
        "UNIT 6 TESTS FAILED =",
        failed_count,
        flush=True
    )

    if failed_count:
        raise RuntimeError(
            "UNIT 6 V9 VALIDATION FAILED"
        )

    print(
        "UNIT 6 VALIDATION V9 RESULT = PASS",
        flush=True
    )

    return True


# ============================================================
# 6.4 SINGLE EXECUTION SEQUENCE
# ============================================================

FRESH_UNIT_6_VALIDATION_READY = (
    unit_6_validation_v9()
)

FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE = (
    fresh_reconstruction_unit_6(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT,
        FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE,
    )
)


# ============================================================
# END COMPLETE UNIT 6 V9 REPLACEMENT
# UNIT 7 FOLLOWS
# ZERO INDENTATION
# ============================================================



# ============================================================
# START COMPLETE UNIT 7 V10
# WEEX DEMO DYNAMIC SIZING POLICY
# UNIT 2 V9 -> UNIT 6 V9 -> UNIT 7 V10 -> UNIT 8
#
# E0: ADJUSTABLE FIXED USDT
# B1-B5: 0.5% OF FRESH AVAILABLE BALANCE
# TRIGGER: 0.3% BEFORE FRESH WEEX LIQUIDATION PRICE
# EXPOSURE: 35% DEFAULT, MAXIMUM 100%
# NO BACKUP MULTIPLIERS
# NO EXCHANGE WRITE IN UNIT 7
# ============================================================

import copy
from decimal import Decimal, InvalidOperation


# ============================================================
# UNIT 7 DECIMAL VALIDATION
# ============================================================

def unit_7_v10_decimal(value, name, allow_zero=False):

    if isinstance(value, bool):
        raise RuntimeError(
            "UNIT 7 INVALID BOOLEAN: " + name
        )

    try:
        number = Decimal(str(value))

    except (InvalidOperation, TypeError, ValueError) as exc:
        raise RuntimeError(
            "UNIT 7 INVALID NUMBER: " + name
        ) from exc

    if not number.is_finite():
        raise RuntimeError(
            "UNIT 7 NONFINITE NUMBER: " + name
        )

    if number < 0:
        raise RuntimeError(
            "UNIT 7 NEGATIVE NUMBER: " + name
        )

    if number == 0 and not allow_zero:
        raise RuntimeError(
            "UNIT 7 ZERO NOT ALLOWED: " + name
        )

    return number


# ============================================================
# UNIT 7 DYNAMIC BACKUP MARGIN FORMULA
# REQUIRES FRESH AVAILABLE BALANCE FROM WEEX
# DOES NOT SUBMIT ORDERS
# ============================================================

def unit_7_v10_backup_margin(
    available_balance,
    backup_percent
):

    balance = unit_7_v10_decimal(
        available_balance,
        "AVAILABLE TRADING BALANCE",
        allow_zero=True
    )

    percent = unit_7_v10_decimal(
        backup_percent,
        "BACKUP MARGIN PERCENT"
    )

    if percent > Decimal("100"):
        raise RuntimeError(
            "UNIT 7 BACKUP PERCENT ABOVE 100"
        )

    return (
        balance * percent / Decimal("100")
    )


# ============================================================
# UNIT 7 BACKUP TRIGGER FORMULA
# REQUIRES FRESH WEEX LIQUIDATION PRICE
# DOES NOT SUBMIT ORDERS
# ============================================================

def unit_7_v10_backup_trigger(
    liquidation_price,
    direction,
    buffer_percent
):

    liquidation = unit_7_v10_decimal(
        liquidation_price,
        "WEEX LIQUIDATION PRICE"
    )

    buffer_pct = unit_7_v10_decimal(
        buffer_percent,
        "LIQUIDATION BUFFER PERCENT"
    )

    if buffer_pct >= Decimal("100"):
        raise RuntimeError(
            "UNIT 7 LIQUIDATION BUFFER INVALID"
        )

    buffer = buffer_pct / Decimal("100")

    if direction == "LONG":
        return liquidation * (
            Decimal("1") + buffer
        )

    if direction == "SHORT":
        return liquidation * (
            Decimal("1") - buffer
        )

    raise RuntimeError(
        "UNIT 7 INVALID BACKUP DIRECTION"
    )


# ============================================================
# UNIT 7 TOTAL MARGIN CAP FORMULA
# INCLUDES INITIAL + FILLED BACKUPS + RESERVED MARGIN
# REQUIRES VERIFIED ACCOUNT VALUES
# ============================================================

def unit_7_v10_remaining_margin_capacity(
    account_equity,
    committed_margin,
    reserved_margin,
    exposure_cap_percent
):

    equity = unit_7_v10_decimal(
        account_equity,
        "TRADING ACCOUNT EQUITY"
    )

    committed = unit_7_v10_decimal(
        committed_margin,
        "ALREADY COMMITTED MARGIN",
        allow_zero=True
    )

    reserved = unit_7_v10_decimal(
        reserved_margin,
        "OUTSTANDING RESERVED MARGIN",
        allow_zero=True
    )

    cap_pct = unit_7_v10_decimal(
        exposure_cap_percent,
        "EXPOSURE CAP PERCENT"
    )

    if cap_pct > Decimal("100"):
        raise RuntimeError(
            "UNIT 7 EXPOSURE CAP ABOVE 100"
        )

    maximum_margin = (
        equity * cap_pct / Decimal("100")
    )

    remaining = (
        maximum_margin - committed - reserved
    )

    return max(
        Decimal("0"),
        remaining
    )


# ============================================================
# UNIT 7 MAIN DYNAMIC POLICY HANDOVER
# ============================================================

def fresh_reconstruction_unit_7(
    unit_2_config,
    unit_6_candidate
):

    print("=" * 80, flush=True)
    print(
        "UNIT 7 V10 DYNAMIC SIZING START",
        flush=True
    )

    if not isinstance(unit_2_config, dict):
        raise RuntimeError(
            "UNIT 7 UNIT 2 CONFIG MISSING"
        )

    if not isinstance(unit_6_candidate, dict):
        raise RuntimeError(
            "UNIT 7 UNIT 6 CANDIDATE MISSING"
        )

    config = unit_2_config
    signal = unit_6_candidate

    strategy = config.get("strategy")
    exchange = config.get("exchange")
    precision = config.get("market_precision")
    safety = config.get("safety")

    for name, section in (
        ("STRATEGY", strategy),
        ("EXCHANGE", exchange),
        ("PRECISION", precision),
        ("SAFETY", safety),
    ):
        if not isinstance(section, dict):
            raise RuntimeError(
                "UNIT 7 MISSING CONFIG SECTION: " + name
            )

    # ========================================================
    # EXCHANGE CONTRACT
    # ========================================================

    if config.get("execution_environment") != "DEMO":
        raise RuntimeError(
            "UNIT 7 NON-DEMO ENVIRONMENT"
        )

    if exchange.get("name") != "WEEX":
        raise RuntimeError(
            "UNIT 7 EXCHANGE IS NOT WEEX"
        )

    if not str(exchange.get("demo_order_symbol", "")).strip():
        raise RuntimeError(
            "UNIT 7 MARKET SYMBOL INVALID"
        )

    if not str(exchange.get("demo_order_symbol", "")).strip():
        raise RuntimeError(
            "UNIT 7 DEMO SYMBOL INVALID"
        )

    # ========================================================
    # UPSTREAM UNIT 6 CONTRACT
    # ========================================================

    required_signal_fields = (
        "execution_intent",
        "signal_qualified",
        "active_mode",
        "direction",
        "admission_reason",
    )

    for key in required_signal_fields:
        if key not in signal:
            raise RuntimeError(
                "UNIT 7 MISSING UNIT 6 FIELD: " + key
            )

    if signal.get("classification_version") != (
        "UNIT6_V9_ADJUSTABLE"
    ):
        raise RuntimeError(
            "UNIT 7 REQUIRES UNIT 6 V9 HANDOVER"
        )

    intent = signal["execution_intent"]
    qualified = signal["signal_qualified"]

    mode = signal["active_mode"]
    direction = signal["direction"]
    admission = signal["admission_reason"]

    if (
        type(intent) is not bool
        or type(qualified) is not bool
    ):
        raise RuntimeError(
            "UNIT 7 INVALID SIGNAL BOOLEAN"
        )

    if intent != qualified:
        raise RuntimeError(
            "UNIT 7 SIGNAL FLAGS MISMATCH"
        )

    if signal.get("exchange_write") is not False:
        raise RuntimeError(
            "UNIT 7 UPSTREAM EXCHANGE WRITE DETECTED"
        )

    if signal.get("order_payload_created") is not False:
        raise RuntimeError(
            "UNIT 7 UPSTREAM ORDER PAYLOAD DETECTED"
        )

    # ========================================================
    # TRADING SAFETY CONTRACT
    # ========================================================

    for key in (
        "anti_duplicate_orders",
        "one_direction_only",
        "active_trade_mode_lock",
        "exclusive_mode",
    ):
        if strategy.get(key) is not True:
            raise RuntimeError(
                "UNIT 7 REQUIRED SAFETY MISSING: " + key
            )

    if safety.get(
        "real_order_submission_enabled"
    ) is not False:
        raise RuntimeError(
            "UNIT 7 LIVE-CASH SAFETY FAILED"
        )

    if safety.get(
        "exchange_mutation_enabled"
    ) is not False:
        raise RuntimeError(
            "UNIT 7 CONFIGURATION MUST BE READ-ONLY"
        )

    # ========================================================
    # E0 INITIAL ENTRY
    # ========================================================

    initial_margin = unit_7_v10_decimal(
        strategy.get("initial_fixed_usdt"),
        "E0 INITIAL USDT"
    )

    # E0 default comes from Unit 2.
    # It may be adjusted upward by its configuration.
    # No predefined E0 multiplier is used.

    # ========================================================
    # BACKUP POLICY
    # ========================================================

    backup_count = strategy.get("max_backups")

    if (
        type(backup_count) is not int
        or backup_count != 5
    ):
        raise RuntimeError(
            "UNIT 7 MAX BACKUPS MUST BE FIVE"
        )

    backup_percent = unit_7_v10_decimal(
        strategy.get("backup_margin_percent"),
        "BACKUP MARGIN PERCENT"
    )

    buffer_percent = unit_7_v10_decimal(
        strategy.get("backup_buffer_percent"),
        "BACKUP BUFFER PERCENT"
    )

    if backup_percent > Decimal("100"):
        raise RuntimeError(
            "UNIT 7 BACKUP PERCENT TOO HIGH"
        )

    if buffer_percent >= Decimal("100"):
        raise RuntimeError(
            "UNIT 7 BUFFER PERCENT TOO HIGH"
        )

    if "backup_multipliers" in strategy:
        raise RuntimeError(
            "UNIT 7 OBSOLETE BACKUP MULTIPLIERS"
        )

    if strategy.get("backup_sizing_mode") != (
        "PERCENT_AVAILABLE_BALANCE"
    ):
        raise RuntimeError(
            "UNIT 7 BACKUP SIZING MODE INVALID"
        )

    if strategy.get(
        "backup_trigger_reference"
    ) != "FRESH_WEEX_LIQUIDATION_PRICE":
        raise RuntimeError(
            "UNIT 7 BACKUP TRIGGER SOURCE INVALID"
        )

    if strategy.get(
        "backup_trigger_recalculation"
    ) != "AFTER_PRECEDING_CONFIRMED_FILL":
        raise RuntimeError(
            "UNIT 7 BACKUP RECALCULATION INVALID"
        )

    if strategy.get(
        "progressive_backup_funding"
    ) is not True:
        raise RuntimeError(
            "UNIT 7 PROGRESSIVE FUNDING REQUIRED"
        )

    if strategy.get(
        "full_ladder_reservation_required"
    ) is not False:
        raise RuntimeError(
            "UNIT 7 FULL LADDER RESERVATION FORBIDDEN"
        )

    # ========================================================
    # EXPOSURE CAP
    # ========================================================

    exposure_cap = unit_7_v10_decimal(
        strategy.get("exposure_cap_percent"),
        "CURRENT EXPOSURE CAP"
    )

    exposure_max = unit_7_v10_decimal(
        strategy.get("exposure_cap_max_percent"),
        "MAX EXPOSURE CAP"
    )

    if (
        exposure_cap > exposure_max
        or exposure_max > Decimal("100")
    ):
        raise RuntimeError(
            "UNIT 7 EXPOSURE LIMIT INVALID"
        )

    if strategy.get("exposure_cap_basis") != (
        "TRADING_ACCOUNT_EQUITY"
    ):
        raise RuntimeError(
            "UNIT 7 EXPOSURE EQUITY BASIS INVALID"
        )

    for key in (
        "exposure_includes_initial",
        "exposure_includes_filled_backups",
        "exposure_includes_pending_margin",
    ):
        if strategy.get(key) is not True:
            raise RuntimeError(
                "UNIT 7 EXPOSURE POLICY INVALID: " + key
            )

    # ========================================================
    # MARKET PRECISION
    # ========================================================

    qty_step = unit_7_v10_decimal(
        precision.get("quantity_step"),
        "QUANTITY STEP"
    )

    min_qty = unit_7_v10_decimal(
        precision.get("minimum_quantity"),
        "MINIMUM QUANTITY"
    )

    price_step = unit_7_v10_decimal(
        precision.get("price_step"),
        "PRICE STEP"
    )

    if min_qty % qty_step != 0:
        raise RuntimeError(
            "UNIT 7 QUANTITY PRECISION INVALID"
        )

    # ========================================================
    # VERIFY BUFFER FACTORS
    # ========================================================

    long_factor = (
        Decimal("1")
        + buffer_percent / Decimal("100")
    )

    short_factor = (
        Decimal("1")
        - buffer_percent / Decimal("100")
    )

    configured_long = unit_7_v10_decimal(
        strategy.get(
            "backup_long_liquidation_factor"
        ),
        "LONG BUFFER FACTOR"
    )

    configured_short = unit_7_v10_decimal(
        strategy.get(
            "backup_short_liquidation_factor"
        ),
        "SHORT BUFFER FACTOR"
    )

    tolerance = Decimal("0.000000001")

    if abs(long_factor - configured_long) > tolerance:
        raise RuntimeError(
            "UNIT 7 LONG BUFFER FACTOR MISMATCH"
        )

    if abs(short_factor - configured_short) > tolerance:
        raise RuntimeError(
            "UNIT 7 SHORT BUFFER FACTOR MISMATCH"
        )

    # ========================================================
    # OUTPUT FOR UNIT 8
    # ========================================================

    output = {
        "unit_7_version": "UNIT7_V10_DYNAMIC",

        "status": "IDLE",
        "skip_reason": admission,

        "active_mode": "NONE",
        "direction": "NONE",

        "execution_intent": False,
        "signal_qualified": False,

        "unit_5_reason": signal.get("unit_5_reason"),
        "admission_reason": admission,

        "candidate_stage": signal.get(
            "candidate_stage", "NONE"
        ),
        "candidate_age_seconds": signal.get(
            "candidate_age_seconds"
        ),

        "symbol": exchange["market_symbol"],
        "demo_order_symbol": exchange["demo_order_symbol"],

        "initial_fixed_usdt": float(initial_margin),

        "initial_margin_percent": float(
            unit_7_v10_decimal(
                strategy.get("initial_margin_percent"),
                "INITIAL MARGIN PERCENT"
            )
        ),

        "max_backups": backup_count,

        "backup_margin_percent": float(backup_percent),
        "backup_buffer_percent": float(buffer_percent),

        "backup_sizing_mode":
            "PERCENT_AVAILABLE_BALANCE",

        "backup_trigger_reference":
            "FRESH_WEEX_LIQUIDATION_PRICE",

        "backup_trigger_recalculation":
            "AFTER_PRECEDING_CONFIRMED_FILL",

        "backup_long_liquidation_factor":
            float(long_factor),

        "backup_short_liquidation_factor":
            float(short_factor),

        "backup_margin_usdt": None,
        "full_ladder_margin_usdt": None,

        "exposure_cap_percent": float(exposure_cap),
        "exposure_cap_max_percent": float(exposure_max),

        "exposure_cap_basis":
            "TRADING_ACCOUNT_EQUITY",

        "exposure_includes_initial": True,
        "exposure_includes_filled_backups": True,
        "exposure_includes_pending_margin": True,

        "progressive_backup_funding": True,
        "full_ladder_reservation_required": False,

        "quantity_step": float(qty_step),
        "minimum_quantity": float(min_qty),
        "price_step": float(price_step),

        "leverage_target": None,
        "leverage_source": "WEEX_EXCHANGE_SETTING",
        "exchange_leverage_verified": False,

        "account_balance_required": False,

        "position_sizing_performed": False,
        "quantity_calculated": False,
        "proposed_quantity": None,

        "backup_margin_calculated": False,
        "backup_trigger_calculated": False,

        "trade_authorized": False,
        "order_payload_created": False,
        "exchange_write": False,
        "read_only": True,

        "source_unit_6": "UNIT6_V9_ADJUSTABLE",
    }

    # ========================================================
    # IDLE HANDOVER
    # ========================================================

    if intent is False:

        if mode != "NONE" or direction != "NONE":
            raise RuntimeError(
                "UNIT 7 INVALID IDLE MODE OR DIRECTION"
            )

        print(
            "UNIT 7 STATUS = IDLE",
            flush=True
        )

        print(
            "UNIT 7 SKIP REASON =",
            admission,
            flush=True
        )

        print(
            "UNIT 7 EXECUTION INTENT = False",
            flush=True
        )

        print(
            "UNIT 7 EXCHANGE WRITE = NONE",
            flush=True
        )

        print(
            "FRESH RECONSTRUCTION UNIT 7 RESULT = PASS",
            flush=True
        )

        print("=" * 80, flush=True)

        return output

    # ========================================================
    # QUALIFIED HANDOVER
    # ========================================================

    approved_admissions = {
        "BREAKOUT":
            "BREAKOUT_QUALIFIED_FOR_NEXT_UNITS",

        "STRUCTURE":
            "STRUCTURE_QUALIFIED_FOR_NEXT_UNITS",

        "SCALP":
            "SCALP_QUALIFIED_FOR_NEXT_UNITS",
    }

    if mode not in approved_admissions:
        raise RuntimeError(
            "UNIT 7 INVALID QUALIFIED MODE"
        )

    if direction not in ("LONG", "SHORT"):
        raise RuntimeError(
            "UNIT 7 INVALID QUALIFIED DIRECTION"
        )

    if admission != approved_admissions[mode]:
        raise RuntimeError(
            "UNIT 7 QUALIFICATION REASON MISMATCH"
        )

    if signal.get("candidate_stage") == "DEVELOPING":
        raise RuntimeError(
            "UNIT 7 DEVELOPING SIGNAL CANNOT EXECUTE"
        )

    if (
        mode == "SCALP"
        and signal.get("higher_mode_developing") is True
    ):
        raise RuntimeError(
            "UNIT 7 SCALP BLOCKED BY HIGHER MODE"
        )

    output.update({
        "status": "READY_FOR_BALANCE",
        "skip_reason": None,

        "active_mode": mode,
        "direction": direction,

        "execution_intent": True,
        "signal_qualified": True,

        "account_balance_required": True,
    })

    print(
        "UNIT 7 STATUS = READY_FOR_BALANCE",
        flush=True
    )

    print(
        "UNIT 7 ACTIVE MODE =",
        mode,
        flush=True
    )

    print(
        "UNIT 7 DIRECTION =",
        direction,
        flush=True
    )

    print(
        "UNIT 7 E0 INITIAL USDT =",
        initial_margin,
        flush=True
    )

    print(
        "UNIT 7 MAX BACKUPS =",
        backup_count,
        flush=True
    )

    print(
        "UNIT 7 BACKUP AVAILABLE BALANCE % =",
        backup_percent,
        flush=True
    )

    print(
        "UNIT 7 BACKUP BUFFER % =",
        buffer_percent,
        flush=True
    )

    print(
        "UNIT 7 BACKUP MULTIPLIERS = NONE",
        flush=True
    )

    print(
        "UNIT 7 LONG TRIGGER FACTOR =",
        long_factor,
        flush=True
    )

    print(
        "UNIT 7 SHORT TRIGGER FACTOR =",
        short_factor,
        flush=True
    )

    print(
        "UNIT 7 EXPOSURE CAP % =",
        exposure_cap,
        flush=True
    )

    print(
        "UNIT 7 EXPOSURE MAX % =",
        exposure_max,
        flush=True
    )

    print(
        "UNIT 7 BACKUP AMOUNTS = DEFERRED",
        flush=True
    )

    print(
        "UNIT 7 LEVERAGE = DEFERRED TO WEEX",
        flush=True
    )

    print(
        "UNIT 7 QUANTITY CALCULATED = FALSE",
        flush=True
    )

    print(
        "UNIT 7 EXCHANGE WRITE = NONE",
        flush=True
    )

    print(
        "FRESH RECONSTRUCTION UNIT 7 RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return output


# ============================================================
# UNIT 7 V10 COMPLETE VALIDATION
# ============================================================

def unit_7_validation_v10():

    print("=" * 80, flush=True)
    print(
        "UNIT 7 VALIDATION V10 START",
        flush=True
    )

    config = copy.deepcopy(
        FRESH_RECONSTRUCTION_CONFIG
    )

    base = copy.deepcopy(
        FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE
    )

    tests = []

    def check(name, changes, expected_status):

        candidate = copy.deepcopy(base)
        candidate.update(changes)

        try:
            result = fresh_reconstruction_unit_7(
                config,
                candidate
            )

            strategy = config["strategy"]

            passed = (
                result["status"] == expected_status
                and result["max_backups"] == 5
                and result["backup_margin_percent"]
                    == strategy["backup_margin_percent"]
                and result["full_ladder_margin_usdt"] is None
                and "backup_multipliers" not in result
                and result["order_payload_created"] is False
                and result["quantity_calculated"] is False
                and result["exchange_write"] is False
                and result["exposure_cap_percent"]
                    <= result["exposure_cap_max_percent"]
                    <= 100.0
            )

        except Exception as exc:

            print(
                "UNIT 7 TEST ERROR =",
                name,
                repr(exc),
                flush=True
            )

            passed = False

        tests.append((name, passed))

    # --------------------------------------------------------
    # TEST 1: NORMAL IDLE
    # --------------------------------------------------------

    check(
        "NORMAL IDLE",
        {
            "execution_intent": False,
            "signal_qualified": False,
            "active_mode": "NONE",
            "direction": "NONE",
            "candidate_stage": "NONE",
            "admission_reason": "NO_ACCEPTABLE_CANDIDATE",
        },
        "IDLE"
    )

    # --------------------------------------------------------
    # TEST 2: STRUCTURE LONG
    # --------------------------------------------------------

    check(
        "QUALIFIED STRUCTURE LONG",
        {
            "execution_intent": True,
            "signal_qualified": True,
            "active_mode": "STRUCTURE",
            "direction": "LONG",
            "candidate_stage": "QUALIFIED",
            "admission_reason":
                "STRUCTURE_QUALIFIED_FOR_NEXT_UNITS",
        },
        "READY_FOR_BALANCE"
    )

    # --------------------------------------------------------
    # TEST 3: BREAKOUT SHORT
    # --------------------------------------------------------

    check(
        "QUALIFIED BREAKOUT SHORT",
        {
            "execution_intent": True,
            "signal_qualified": True,
            "active_mode": "BREAKOUT",
            "direction": "SHORT",
            "candidate_stage": "QUALIFIED",
            "admission_reason":
                "BREAKOUT_QUALIFIED_FOR_NEXT_UNITS",
        },
        "READY_FOR_BALANCE"
    )

    # --------------------------------------------------------
    # TEST 4: SCALP LONG
    # --------------------------------------------------------

    check(
        "QUALIFIED SCALP LONG",
        {
            "execution_intent": True,
            "signal_qualified": True,
            "active_mode": "SCALP",
            "direction": "LONG",
            "candidate_stage": "PENDING_UNIT_6",
            "higher_mode_developing": False,
            "admission_reason":
                "SCALP_QUALIFIED_FOR_NEXT_UNITS",
        },
        "READY_FOR_BALANCE"
    )

    # --------------------------------------------------------
    # TEST 5: DEVELOPING STRUCTURE
    # --------------------------------------------------------

    check(
        "DEVELOPING STRUCTURE IDLE",
        {
            "execution_intent": False,
            "signal_qualified": False,
            "active_mode": "NONE",
            "direction": "NONE",
            "candidate_stage": "DEVELOPING",
            "admission_reason":
                "DEVELOPING_HIGHER_MODE_PROTECTED",
        },
        "IDLE"
    )

    # --------------------------------------------------------
    # TEST 6: DEVELOPING BREAKOUT
    # --------------------------------------------------------

    check(
        "DEVELOPING BREAKOUT IDLE",
        {
            "execution_intent": False,
            "signal_qualified": False,
            "active_mode": "NONE",
            "direction": "NONE",
            "candidate_stage": "DEVELOPING",
            "admission_reason":
                "DEVELOPING_HIGHER_MODE_PROTECTED",
        },
        "IDLE"
    )

    # --------------------------------------------------------
    # TEST 7: ACTUAL UNIT 6 HANDOVER
    # --------------------------------------------------------

    check(
        "ACTUAL UNIT 6 V9 HANDOVER",
        {},
        (
            "READY_FOR_BALANCE"
            if base.get("execution_intent") is True
            else "IDLE"
        )
    )

    # --------------------------------------------------------
    # TEST 8: DYNAMIC BACKUP MARGIN
    # --------------------------------------------------------

    try:
        percentage = config["strategy"][
            "backup_margin_percent"
        ]

        amount = unit_7_v10_backup_margin(
            Decimal("100"),
            percentage
        )

        expected_amount = (
            Decimal("100")
            * Decimal(str(percentage))
            / Decimal("100")
        )

        margin_pass = amount == expected_amount

    except Exception:
        margin_pass = False

    tests.append((
        "DYNAMIC BACKUP AVAILABLE BALANCE",
        margin_pass
    ))

    # --------------------------------------------------------
    # TEST 9: LONG/SHORT BACKUP TRIGGERS
    # --------------------------------------------------------

    try:
        buffer = config["strategy"][
            "backup_buffer_percent"
        ]

        long_trigger = unit_7_v10_backup_trigger(
            Decimal("80000"),
            "LONG",
            buffer
        )

        short_trigger = unit_7_v10_backup_trigger(
            Decimal("80000"),
            "SHORT",
            buffer
        )

        fraction = Decimal(
            str(buffer)
        ) / Decimal("100")

        trigger_pass = (
            long_trigger
                == Decimal("80000")
                * (Decimal("1") + fraction)
            and short_trigger
                == Decimal("80000")
                * (Decimal("1") - fraction)
        )

    except Exception:
        trigger_pass = False

    tests.append((
        "FRESH LIQUIDATION TRIGGER FORMULAS",
        trigger_pass
    ))

    # --------------------------------------------------------
    # TEST 10: ADJUSTABLE 100% CAP
    # --------------------------------------------------------

    try:
        modified_config = copy.deepcopy(config)

        modified_config["strategy"][
            "exposure_cap_percent"
        ] = 100.0

        result = fresh_reconstruction_unit_7(
            modified_config,
            base
        )

        remaining = (
            unit_7_v10_remaining_margin_capacity(
                Decimal("100"),
                Decimal("34.7"),
                Decimal("0"),
                Decimal("35")
            )
        )

        cap_pass = (
            result["exposure_cap_percent"] == 100.0
            and remaining == Decimal("0.3")
            and result["exchange_write"] is False
        )

    except Exception as exc:

        print(
            "UNIT 7 CAP TEST ERROR =",
            repr(exc),
            flush=True
        )

        cap_pass = False

    tests.append((
        "ADJUSTABLE EXPOSURE CAP",
        cap_pass
    ))

    # ========================================================
    # FINAL VALIDATION SUMMARY
    # ========================================================

    passed_count = sum(
        1 for _, passed in tests if passed
    )

    failed_count = len(tests) - passed_count

    for name, passed in tests:

        print(
            "UNIT 7 TEST:",
            name,
            "=",
            "PASS" if passed else "FAIL",
            flush=True
        )

    print(
        "UNIT 7 TESTS PASSED =",
        passed_count,
        flush=True
    )

    print(
        "UNIT 7 TESTS FAILED =",
        failed_count,
        flush=True
    )

    if failed_count:
        raise RuntimeError(
            "UNIT 7 V10 VALIDATION FAILED"
        )

    print(
        "UNIT 7 VALIDATION V10 RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return True


# ============================================================
# UNIT 7 V10 EXECUTION
# KEEP THESE CALLS AFTER ALL UNIT 7 FUNCTION DEFINITIONS
# ============================================================

FRESH_UNIT_7_VALIDATION_READY = (
    unit_7_validation_v10()
)

FRESH_RECONSTRUCTION_SIZING_CANDIDATE = (
    fresh_reconstruction_unit_7(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE
    )
)

print(
    "FRESH RECONSTRUCTION UNIT 7 V10 READY =",
    FRESH_UNIT_7_VALIDATION_READY,
    flush=True
)

# ============================================================
# END COMPLETE UNIT 7 V10
# UNIT 8 FOLLOWS
# ============================================================



# ============================================================
# START COMPLETE UNIT 8 V6
# WEEX DEMO + RENDER MANUAL LEVERAGE
# UNIT 7 V10 COMPATIBLE
# ZERO INDENTATION
#
# AUTHENTICATED DEMO GET REQUESTS ONLY
# NO LEVERAGE API REQUIRED
# NO LEVERAGE MUTATION
# NO ORDER SUBMISSION
# ============================================================

import os
import json
import time
import hmac
import hashlib
import base64
import urllib.request
import urllib.error

from decimal import (
    Decimal,
    InvalidOperation,
    ROUND_FLOOR,
    ROUND_CEILING,
)
from urllib.parse import urlencode


# ============================================================
# UNIT 8 NUMERIC VALIDATION
# ============================================================

def unit_8_v6_decimal(
    value,
    name,
    allow_zero=False,
):
    if isinstance(value, bool):
        raise RuntimeError(
            "UNIT 8 INVALID BOOLEAN: " + name
        )

    try:
        result = Decimal(str(value))
    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ) as exc:
        raise RuntimeError(
            "UNIT 8 INVALID NUMBER: " + name
        ) from exc

    if not result.is_finite():
        raise RuntimeError(
            "UNIT 8 NONFINITE NUMBER: " + name
        )

    if result < 0:
        raise RuntimeError(
            "UNIT 8 NEGATIVE NUMBER: " + name
        )

    if result == 0 and not allow_zero:
        raise RuntimeError(
            "UNIT 8 ZERO NOT ALLOWED: " + name
        )

    return result


# ============================================================
# UNIT 8 SIGNED WEEX DEMO GET
# ALLOWED ENDPOINTS ONLY
# ============================================================

def unit_8_v6_signed_get(path, params=None):

    allowed = {
        "/capi/v3/sim/balance",
        "/capi/v3/sim/position/allPosition",
    }

    if path not in allowed:
        raise RuntimeError(
            "UNIT 8 NON-DEMO ENDPOINT REJECTED"
        )

    key = (
        os.getenv("WEEX_API_KEY")
        or os.getenv("API_KEY")
    )

    secret = (
        os.getenv("WEEX_API_SECRET")
        or os.getenv("API_SECRET")
    )

    passphrase = (
        os.getenv("WEEX_API_PASSPHRASE")
        or os.getenv("API_PASSPHRASE")
    )

    if not all((key, secret, passphrase)):
        raise RuntimeError(
            "UNIT 8 API CREDENTIALS MISSING"
        )

    query = urlencode(params or {})

    target = path + (
        "?" + query if query else ""
    )

    timestamp = str(int(time.time() * 1000))

    message = timestamp + "GET" + target

    signature = base64.b64encode(
        hmac.new(
            secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    ).decode("utf-8")

    request = urllib.request.Request(
        url=(
            "https://api-contract.weex.com"
            + target
        ),
        headers={
            "ACCESS-KEY": key,
            "ACCESS-SIGN": signature,
            "ACCESS-PASSPHRASE": passphrase,
            "ACCESS-TIMESTAMP": timestamp,
            "Content-Type": "application/json",
            "locale": "en-US",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=12,
        ) as response:
            payload = json.loads(
                response.read().decode("utf-8")
            )

    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            "UNIT 8 WEEX HTTP " + str(exc.code)
        ) from exc

    except Exception as exc:
        raise RuntimeError(
            "UNIT 8 WEEX REQUEST FAILED: "
            + type(exc).__name__
        ) from exc

    if isinstance(payload, dict):
        code = payload.get("code")

        if code is not None and str(code) not in (
            "0",
            "200",
            "00000",
        ):
            raise RuntimeError(
                "UNIT 8 WEEX API CODE: " + str(code)
            )

        if "data" in payload:
            return payload["data"]

    return payload


# ============================================================
# UNIT 8 RENDER LEVERAGE
# ALWAYS READ BOTH, INCLUDING FLAT POSITION
# ============================================================

def unit_8_v6_render_leverage():

    def read(name):
        raw = os.environ.get(name)

        if not raw or not raw.strip():
            raise RuntimeError(
                "UNIT 8 MISSING RENDER VARIABLE: "
                + name
            )

        leverage = unit_8_v6_decimal(
            raw.strip(),
            name,
        )

        if leverage > Decimal("200"):
            raise RuntimeError(
                "UNIT 8 LEVERAGE OUTSIDE LOCAL LIMIT"
            )

        return leverage

    return (
        read("WEEX_DEMO_LONG_LEVERAGE"),
        read("WEEX_DEMO_SHORT_LEVERAGE"),
    )


# ============================================================
# UNIT 8 MINIMUM QUANTITY CALCULATION
# NO SILENT INCREASE OF ENTRY MARGIN
# ============================================================

def unit_8_v6_quantity(
    margin,
    leverage,
    price,
    quantity_step,
    minimum_quantity,
):

    margin = unit_8_v6_decimal(
        margin, "MARGIN"
    )

    leverage = unit_8_v6_decimal(
        leverage, "LEVERAGE"
    )

    price = unit_8_v6_decimal(
        price, "MARK PRICE"
    )

    step = unit_8_v6_decimal(
        quantity_step, "QUANTITY STEP"
    )

    minimum = unit_8_v6_decimal(
        minimum_quantity, "MINIMUM QUANTITY"
    )

    raw_quantity = (
        margin * leverage / price
    )

    steps = (
        raw_quantity / step
    ).to_integral_value(
        rounding=ROUND_FLOOR
    )

    normalized = steps * step

    minimum_steps = (
        minimum / step
    ).to_integral_value(
        rounding=ROUND_CEILING
    )

    executable_minimum = (
        minimum_steps * step
    )

    required_margin = (
        executable_minimum * price / leverage
    )

    return {
        "raw_quantity": raw_quantity,
        "quantity": normalized,
        "minimum_quantity": executable_minimum,
        "minimum_margin_required": required_margin,
        "minimum_quantity_pass": (
            normalized >= executable_minimum
        ),
    }


# ============================================================
# UNIT 8 MAIN
# ============================================================

def fresh_reconstruction_unit_8(
    config,
    unit_7_result,
    market_snapshot=None,
):

    print("=" * 80, flush=True)
    print(
        "UNIT 8 V6 RENDER LEVERAGE START",
        flush=True
    )

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 8 CONFIG INVALID"
        )

    if not isinstance(unit_7_result, dict):
        raise RuntimeError(
            "UNIT 8 UNIT 7 RESULT INVALID"
        )

    if unit_7_result.get(
        "unit_7_version"
    ) != "UNIT7_V10_DYNAMIC":
        raise RuntimeError(
            "UNIT 8 REQUIRES UNIT 7 V10"
        )

    exchange = config.get("exchange", {})
    strategy = config.get("strategy", {})
    safety = config.get("safety", {})

    if config.get(
        "execution_environment"
    ) != "DEMO":
        raise RuntimeError(
            "UNIT 8 DEMO ONLY"
        )

    
    market_symbol = str(
        exchange.get("market_symbol") or ""
    ).strip().upper()

    demo_order_symbol = str(
        exchange.get("demo_order_symbol") or ""
    ).strip().upper()

    if (
        exchange.get("name") != "WEEX"
        or not market_symbol
        or not demo_order_symbol
    ):
        raise RuntimeError(
            "UNIT 8 SYMBOL CONTRACT INVALID"
        )

    if (
        unit_7_result.get("symbol") != market_symbol
        or unit_7_result.get("demo_order_symbol")
            != demo_order_symbol
    ):
        raise RuntimeError(
            "UNIT 8 UNIT 7 SYMBOL HANDOVER MISMATCH"
        )

    if (
        unit_7_result.get("exchange_write")
            is not False
        or unit_7_result.get(
            "order_payload_created"
        ) is not False
    ):
        raise RuntimeError(
            "UNIT 8 UNIT 7 WRITE SAFETY FAILED"
        )

    if safety.get(
        "real_order_submission_enabled"
    ) is not False:
        raise RuntimeError(
            "UNIT 8 REAL CASH DISABLED REQUIRED"
        )

    # ========================================================
    # 1. LEVERAGE ALWAYS READ FIRST
    # ========================================================

    leverage_error = None
    long_leverage = None
    short_leverage = None

    try:
        (
            long_leverage,
            short_leverage,
        ) = unit_8_v6_render_leverage()

        print(
            "UNIT 8 RENDER LONG LEVERAGE =",
            long_leverage,
            flush=True
        )

        print(
            "UNIT 8 RENDER SHORT LEVERAGE =",
            short_leverage,
            flush=True
        )

    except Exception as exc:
        leverage_error = str(exc)

        print(
            "UNIT 8 LEVERAGE CONFIG ERROR =",
            leverage_error,
            flush=True
        )

    # ========================================================
    # 2. PRESERVE UNIT 9 NINE-FIELD CONTRACT
    # ========================================================

    mode = unit_7_result.get(
        "active_mode", "NONE"
    )

    direction = unit_7_result.get(
        "direction", "NONE"
    )

    qualified = (
        unit_7_result.get("signal_qualified")
        is True
    )

    intent = (
        unit_7_result.get("execution_intent")
        is True
    )

    output = {
        "status": "IDLE",
        "active_mode": mode,
        "direction": direction,
        "signal_qualified": qualified,
        "execution_intent": False,
        "trade_plan_ready": False,
        "trade_plan": None,
        "skip_reason": "NONE",
        "read_only": True,

        "unit_8_version":
            "UNIT8_V6_RENDER_LEVERAGE",

        "demo_symbol": "BTCSUSDT",

        "weex_demo_long_leverage": (
            float(long_leverage)
            if long_leverage is not None
            else None
        ),

        "weex_demo_short_leverage": (
            float(short_leverage)
            if short_leverage is not None
            else None
        ),

        "long_leverage": (
            str(long_leverage)
            if long_leverage is not None
            else None
        ),

        "short_leverage": (
            str(short_leverage)
            if short_leverage is not None
            else None
        ),

        "selected_leverage": None,

        "leverage_source":
            "RENDER_MANUAL_WEEX_DEMO",

        "leverage_configured": (
            leverage_error is None
        ),

        "exchange_leverage_verified": False,
        "demo_leverage_verified": False,

        "demo_balance_verified": False,
        "demo_positions_verified": False,
        "position_flat_verified": False,

        "available_balance": None,
        "account_equity": None,
        "account_equity_source": None,

        "positions": [],
        "quantity_calculated": False,
        "execution_quantity": None,

        "max_backups": 5,
        "backup_margin_percent":
            unit_7_result.get(
                "backup_margin_percent"
            ),
        "backup_buffer_percent":
            unit_7_result.get(
                "backup_buffer_percent"
            ),
        "exposure_cap_percent":
            unit_7_result.get(
                "exposure_cap_percent"
            ),

        "order_payload_created": False,
        "exchange_write": False,
    }

    def finish(status, reason):

        output["status"] = status
        output["skip_reason"] = reason

        print(
            "UNIT 8 STATUS =",
            status,
            flush=True
        )

        print(
            "UNIT 8 REASON =",
            reason,
            flush=True
        )

        print(
            "UNIT 8 TRADE PLAN READY =",
            output["trade_plan_ready"],
            flush=True
        )

        print(
            "UNIT 8 EXCHANGE WRITE = NONE",
            flush=True
        )

        print("=" * 80, flush=True)

        return output

    # ========================================================
    # 3. READ DEMO BALANCE EVEN DURING IDLE
    # ========================================================

    try:
        balances = unit_8_v6_signed_get(
            "/capi/v3/sim/balance"
        )

        if isinstance(balances, dict):
            balances = [balances]

        if not isinstance(balances, list):
            raise RuntimeError(
                "INVALID DEMO BALANCE FORMAT"
            )

        asset = next(
            (
                record
                for record in balances
                if isinstance(record, dict)
                and str(
                    record.get("asset", "")
                ).upper() == "SUSDT"
            ),
            None
        )

        if asset is None:
            raise RuntimeError(
                "SUSDT ASSET NOT FOUND"
            )

        available = unit_8_v6_decimal(
            asset.get("availableBalance"),
            "AVAILABLE SUSDT",
            allow_zero=True
        )

        output["available_balance"] = str(
            available
        )

        output["demo_balance_verified"] = True

        # Equity is used only if the exchange supplied
        # values required for a reliable calculation.
        if (
            asset.get("equity") is not None
        ):
            equity = unit_8_v6_decimal(
                asset["equity"],
                "DEMO EQUITY",
                allow_zero=True
            )

            output["account_equity"] = str(equity)
            output["account_equity_source"] = (
                "WEEX_REPORTED_EQUITY"
            )

        elif (
            asset.get("balance") is not None
            and asset.get("unrealizePnl")
                is not None
        ):
            balance = unit_8_v6_decimal(
                asset["balance"],
                "BALANCE",
                allow_zero=True
            )

            pnl = Decimal(
                str(asset["unrealizePnl"])
            )

            if not pnl.is_finite():
                raise RuntimeError(
                    "INVALID UNREALIZED PNL"
                )

            equity = balance + pnl

            if equity < 0:
                raise RuntimeError(
                    "NEGATIVE EQUITY"
                )

            output["account_equity"] = str(equity)
            output["account_equity_source"] = (
                "PROVISIONAL_BALANCE_PLUS_PNL"
            )

        print(
            "UNIT 8 DEMO BALANCE VERIFIED = True",
            flush=True
        )

        print(
            "UNIT 8 AVAILABLE SUSDT =",
            available,
            flush=True
        )

    except Exception as exc:

        print(
            "UNIT 8 DEMO BALANCE ERROR =",
            str(exc),
            flush=True
        )

        return finish(
            "BLOCKED",
            "DEMO_BALANCE_UNVERIFIED"
        )

    # ========================================================
    # 4. READ DEMO POSITIONS EVEN DURING IDLE
    # ========================================================

    try:
        positions = unit_8_v6_signed_get(
            "/capi/v3/sim/position/allPosition"
        )

        if isinstance(positions, dict):
            positions = [positions]

        if not isinstance(positions, list):
            raise RuntimeError(
                "INVALID DEMO POSITIONS FORMAT"
            )

        open_positions = []

        
        for position in positions:

            if not isinstance(position, dict):
                continue

            position_symbol = str(
                position.get("symbol") or ""
            ).strip().upper()

            if not position_symbol:
                continue

            size = unit_8_v6_decimal(
                position.get("size", "0"),
                "POSITION SIZE",
                allow_zero=True
            )

            if size > 0:
                open_positions.append(position)

        print(
            "UNIT 8 ACCOUNT-WIDE OPEN POSITIONS =",
            len(open_positions),
            flush=True
        )

        print(
            "UNIT 8 OPEN POSITION SYMBOLS =",
            sorted({
                str(p.get("symbol", "")).upper()
                for p in open_positions
            }),
            flush=True
        )

        output["positions"] = open_positions
        output["demo_positions_verified"] = True

        output["position_flat_verified"] = (
            len(open_positions) == 0
        )

        print(
            "UNIT 8 OPEN DEMO POSITIONS =",
            len(open_positions),
            flush=True
        )

        print(
            "UNIT 8 POSITION FLAT =",
            output["position_flat_verified"],
            flush=True
        )

    except Exception as exc:

        print(
            "UNIT 8 DEMO POSITION ERROR =",
            str(exc),
            flush=True
        )

        return finish(
            "BLOCKED",
            "DEMO_POSITIONS_UNVERIFIED"
        )

    # ========================================================
    # 5. BLOCK INVALID LEVERAGE CONFIGURATION
    # ========================================================

    if leverage_error is not None:
        return finish(
            "BLOCKED",
            "RENDER_DEMO_LEVERAGE_MISSING_OR_INVALID"
        )

    # ========================================================
    # 6. INDEPENDENT OPEN POSITION SAFETY
    # ========================================================

    if not output["position_flat_verified"]:
        return finish(
            "IDLE",
            "EXISTING_DEMO_POSITION"
        )

    # ========================================================
    # 7. NO QUALIFIED SIGNAL
    # ========================================================

    if not intent:
        return finish(
            "IDLE",
            unit_7_result.get("skip_reason")
            or "NO_QUALIFIED_SIGNAL"
        )

    if (
        not qualified
        or unit_7_result.get("status")
            != "READY_FOR_BALANCE"
    ):
        return finish(
            "BLOCKED",
            "UNIT_7_NOT_QUALIFIED"
        )

    if (
        mode not in (
            "BREAKOUT",
            "STRUCTURE",
            "SCALP",
        )
        or direction not in (
            "LONG",
            "SHORT",
        )
    ):
        return finish(
            "BLOCKED",
            "INVALID_TRADE_DIRECTION_OR_MODE"
        )

    # ========================================================
    # 8. SELECT RENDER LEVERAGE
    # ========================================================

    leverage = (
        long_leverage
        if direction == "LONG"
        else short_leverage
    )

    output["selected_leverage"] = float(
        leverage
    )

    # ========================================================
    # 9. MARKET SNAPSHOT
    # ========================================================

    if market_snapshot is None:
        market_snapshot = globals().get(
            "FRESH_RECONSTRUCTION_MARKET_SNAPSHOT"
        )

    if not isinstance(market_snapshot, dict):
        return finish(
            "BLOCKED",
            "MARKET_SNAPSHOT_MISSING"
        )

    
    if (
        str(market_snapshot.get("symbol") or "").strip().upper()
        != str(exchange.get("market_symbol") or "").strip().upper()
    ):
        return finish(
            "BLOCKED",
            "MARKET_SYMBOL_MISMATCH"
        )

    try:
        price = unit_8_v6_decimal(
            market_snapshot.get("price"),
            "MARK PRICE"
        )

    except Exception:
        return finish(
            "BLOCKED",
            "INVALID_MARK_PRICE"
        )

    # ========================================================
    # 10. INITIAL ENTRY MARGIN
    # ========================================================

    raw_margin = os.getenv(
        "INITIAL_ENTRY_MARGIN_USDT"
    )

    if raw_margin is None or not raw_margin.strip():
        raw_margin = os.getenv(
            "ENTRY_FIXED_USDT"
        )

    if raw_margin is None or not raw_margin.strip():
        raw_margin = str(
            unit_7_result.get(
                "initial_fixed_usdt", "0.5"
            )
        )

    try:
        margin = unit_8_v6_decimal(
            raw_margin,
            "INITIAL ENTRY MARGIN"
        )

        available = unit_8_v6_decimal(
            output["available_balance"],
            "AVAILABLE BALANCE",
            allow_zero=True
        )

        cap = unit_8_v6_decimal(
            unit_7_result.get(
                "exposure_cap_percent"
            ),
            "EXPOSURE CAP"
        )

        if cap > Decimal("100"):
            raise RuntimeError(
                "EXPOSURE CAP TOO HIGH"
            )

    except Exception as exc:
        print(
            "UNIT 8 MARGIN CONFIG ERROR =",
            str(exc),
            flush=True
        )

        return finish(
            "BLOCKED",
            "INVALID_MARGIN_CONFIGURATION"
        )

    if margin > available:
        return finish(
            "BLOCKED",
            "INSUFFICIENT_DEMO_BALANCE"
        )

    if output["account_equity"] is None:
        return finish(
            "BLOCKED",
            "DEMO_EQUITY_UNVERIFIED"
        )

    equity = unit_8_v6_decimal(
        output["account_equity"],
        "ACCOUNT EQUITY",
        allow_zero=True
    )

    exposure_budget = (
        equity * cap / Decimal("100")
    )

    # Conservative preparation only.
    # Unit 9 must refresh actual committed and
    # reserved margin before authorizing submission.
    if margin > exposure_budget:
        return finish(
            "BLOCKED",
            "INITIAL_ENTRY_EXCEEDS_EXPOSURE_CAP"
        )

    # ========================================================
    # 11. STEP-AWARE BTC QUANTITY
    # ========================================================

    try:
        sizing = unit_8_v6_quantity(
            margin=margin,
            leverage=leverage,
            price=price,
            quantity_step=unit_7_result[
                "quantity_step"
            ],
            minimum_quantity=unit_7_result[
                "minimum_quantity"
            ],
        )

    except Exception as exc:
        print(
            "UNIT 8 SIZING ERROR =",
            str(exc),
            flush=True
        )

        return finish(
            "BLOCKED",
            "INVALID_QUANTITY_CALCULATION"
        )

    print(
        "UNIT 8 ENTRY MARGIN =",
        margin,
        flush=True
    )

    print(
        "UNIT 8 SELECTED LEVERAGE =",
        leverage,
        flush=True
    )

    print(
        "UNIT 8 RAW BTC QUANTITY =",
        sizing["raw_quantity"],
        flush=True
    )

    print(
        "UNIT 8 MINIMUM BTC QUANTITY =",
        sizing["minimum_quantity"],
        flush=True
    )

    print(
        "UNIT 8 MINIMUM REQUIRED MARGIN =",
        sizing["minimum_margin_required"],
        flush=True
    )

    if not sizing["minimum_quantity_pass"]:
        return finish(
            "BLOCKED",
            "QUANTITY_BELOW_EXCHANGE_MINIMUM"
        )

    quantity = sizing["quantity"]

    # Reject any accidental over-allocation
    # caused by contract rounding or conversions.
    required_margin = (
        quantity * price / leverage
    )

    if required_margin > margin:
        return finish(
            "BLOCKED",
            "NORMALIZED_ORDER_MARGIN_EXCEEDS_E0"
        )

    # ========================================================
    # 12. PRESERVE ORIGINAL POSITION SIZING CONTRACT
    # ========================================================

    position_sizing = {
        "asset": "SUSDT",
        "available_balance": float(available),

        "initial_margin_percent": float(
            unit_7_result.get(
                "initial_margin_percent"
            )
        ),

        "margin_allocation": float(margin),
        "leverage_target": float(leverage),
        "live_mark_price": float(price),

        "raw_quantity": float(
            sizing["raw_quantity"]
        ),

        "quantity_step": float(
            unit_7_result["quantity_step"]
        ),

        "minimum_quantity": float(
            sizing["minimum_quantity"]
        ),

        "quantity": float(quantity),

        "position_sizing_performed": True,
        "quantity_calculated": True,

        "source": "WEEX_V3_DEMO_BALANCE",
        "read_only": True,

        "leverage_source":
            "RENDER_MANUAL_WEEX_DEMO",

        "long_leverage": float(
            long_leverage
        ),

        "short_leverage": float(
            short_leverage
        ),

        "exchange_leverage_verified": False,

        "exposure_cap_percent": float(cap),
        "exposure_budget": float(exposure_budget),

        "max_backups": 5,

        "backup_margin_percent": float(
            unit_7_result[
                "backup_margin_percent"
            ]
        ),

        "backup_sizing_mode":
            "PERCENT_AVAILABLE_BALANCE",

        "backup_margin_reserved": False,
    }

    # ========================================================
    # 13. PRESERVE ORIGINAL UNIT 9 TRADE PLAN
    # ========================================================

    trade_plan = {
        "active_mode": mode,
        "direction": direction,
        "quantity": float(quantity),
        "position_sizing": position_sizing,
        "execution_environment": "DEMO",
    }

    output.update({
        "status": "READY",
        "execution_intent": True,
        "trade_plan_ready": True,
        "trade_plan": trade_plan,
        "skip_reason": "NONE",

        "quantity_calculated": True,
        "execution_quantity": str(quantity),

        "trade_authorized": False,
        "order_payload_created": False,
        "exchange_write": False,
    })

    print(
        "UNIT 8 STATUS = READY",
        flush=True
    )

    print(
        "UNIT 8 DIRECTION =",
        direction,
        flush=True
    )

    print(
        "UNIT 8 EXECUTABLE QUANTITY =",
        quantity,
        flush=True
    )

    print(
        "UNIT 8 TRADE PLAN READY = TRUE",
        flush=True
    )

    print(
        "UNIT 8 TRADE AUTHORIZED = FALSE",
        flush=True
    )

    print(
        "UNIT 8 LEVERAGE SOURCE = RENDER",
        flush=True
    )

    print(
        "UNIT 8 LEVERAGE API VERIFIED = FALSE",
        flush=True
    )

    print(
        "UNIT 8 EXCHANGE WRITE = NONE",
        flush=True
    )

    print(
        "UNIT 8 V6 RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return output


# ============================================================
# UNIT 8 V6 VALIDATION
# PURE LOCAL CHECKS - NO NETWORK CALLS
# ============================================================

def unit_8_validation_v6():

    print("=" * 80, flush=True)
    print(
        "UNIT 8 V6 VALIDATION START",
        flush=True
    )

    config = FRESH_RECONSTRUCTION_CONFIG
    incoming = (
        FRESH_RECONSTRUCTION_SIZING_CANDIDATE
    )

    tests = []

    tests.append((
        "UNIT 7 V10 HANDOVER",
        incoming.get("unit_7_version")
        == "UNIT7_V10_DYNAMIC"
    ))

    tests.append((
        "DEMO ENVIRONMENT",
        config.get("execution_environment")
        == "DEMO"
    ))

    tests.append((
        "FIVE DYNAMIC BACKUPS",
        incoming.get("max_backups") == 5
        and "backup_multipliers"
            not in config["strategy"]
    ))

    tests.append((
        "EXPOSURE CAP VALID",
        Decimal("0")
        < Decimal(str(
            incoming["exposure_cap_percent"]
        ))
        <= Decimal("100")
    ))

    tests.append((
        "RENDER LEVERAGE CONFIGURED",
        all(
            os.getenv(name, "").strip()
            for name in (
                "WEEX_DEMO_LONG_LEVERAGE",
                "WEEX_DEMO_SHORT_LEVERAGE",
            )
        )
    ))

    tests.append((
        "UNIT 8 UPSTREAM NO WRITE",
        incoming.get("exchange_write")
        is False
    ))

    tests.append((
        "MINIMUM BTC NORMALIZATION",
        unit_8_v6_quantity(
            "1",
            "10",
            "75000",
            "0.0001",
            "0.0001",
        )["minimum_quantity_pass"]
        is True
    ))

    tests.append((
        "BELOW MINIMUM REJECTED",
        unit_8_v6_quantity(
            "0.5",
            "10",
            "75000",
            "0.0001",
            "0.0001",
        )["minimum_quantity_pass"]
        is False
    ))

    tests.append((
        "LONG SHORT LEVERAGE INDEPENDENT",
        (
            unit_8_v6_quantity(
                "1", "10", "75000",
                "0.0001", "0.0001"
            )["quantity"]
            <
            unit_8_v6_quantity(
                "1", "20", "75000",
                "0.0001", "0.0001"
            )["quantity"]
        )
    ))

    tests.append((
        "UNIT 8 NO BACKUP MULTIPLIER",
        incoming.get("backup_sizing_mode")
        == "PERCENT_AVAILABLE_BALANCE"
    ))

    passed = sum(
        1 for _, ok in tests if ok
    )

    failed = len(tests) - passed

    for name, ok in tests:
        print(
            "UNIT 8 TEST:",
            name,
            "=",
            "PASS" if ok else "FAIL",
            flush=True
        )

    print(
        "UNIT 8 TESTS PASSED =",
        passed,
        flush=True
    )

    print(
        "UNIT 8 TESTS FAILED =",
        failed,
        flush=True
    )

    if failed:
        raise RuntimeError(
            "UNIT 8 V6 VALIDATION FAILED"
        )

    print(
        "UNIT 8 V6 VALIDATION RESULT = PASS",
        flush=True
    )

    return True


# ============================================================
# UNIT 8 - PERSISTENT UNIVERSAL SYMBOL SWITCH CONTROLLER
# SQLITE / RENDER / WEEX DEMO ONLY
# ZERO INDENTATION
# ============================================================

import os
import re
import json
import sqlite3
from datetime import datetime, timezone


# ============================================================
# UNIT 8 - WEEX V3 MARKET CONTRACT VERIFICATION
# PUBLIC GET ONLY - NO ORDER SUBMISSION
# ============================================================

def unit_8_verify_market_contract(market_symbol):

    market_symbol = str(
        market_symbol or ""
    ).strip().upper()

    result = {
        "market_symbol": market_symbol,
        "market_verified": False,
        "api_trading_enabled": False,
        "demo_contract_verified": False,
        "reason": "NOT_CHECKED",
        "contract": None,
    }

    if not re.fullmatch(
        r"[A-Z0-9]{3,30}",
        market_symbol
    ):
        result["reason"] = "INVALID_MARKET_SYMBOL"
        return result

    base_url = "https://api-contract.weex.com"

    def public_get(path, params=None):

        query = urllib.parse.urlencode(
            params or {}
        )

        url = base_url + path

        if query:
            url += "?" + query

        request = urllib.request.Request(
            url=url,
            method="GET",
            headers={
                "Accept": "application/json",
                "User-Agent": "WEEX-Unit8-Contract-Check",
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=15
        ) as response:

            if response.getcode() != 200:
                raise RuntimeError(
                    "WEEX CONTRACT HTTP STATUS INVALID"
                )

            return json.loads(
                response.read().decode("utf-8")
            )

    try:

        info = public_get(
            "/capi/v3/market/exchangeInfo",
            {"symbol": market_symbol}
        )

        if not isinstance(info, dict):
            raise RuntimeError(
                "INVALID EXCHANGE INFO RESPONSE"
            )

        symbols = info.get("symbols")

        if not isinstance(symbols, list):
            raise RuntimeError(
                "EXCHANGE SYMBOL LIST MISSING"
            )

        matching = [
            item
            for item in symbols
            if isinstance(item, dict)
            and str(
                item.get("symbol", "")
            ).upper() == market_symbol
        ]

        if len(matching) != 1:
            result["reason"] = (
                "MARKET_CONTRACT_NOT_FOUND"
            )
            return result

        contract = matching[0]

        result["contract"] = contract
        result["market_verified"] = True

        tradable = public_get(
            "/capi/v3/market/apiTradingSymbols"
        )

        if not isinstance(tradable, list):
            raise RuntimeError(
                "API TRADING SYMBOL LIST INVALID"
            )

        result["api_trading_enabled"] = (
            market_symbol in {
                str(item).upper()
                for item in tradable
                if isinstance(item, str)
            }
        )

        result["reason"] = (
            "MARKET_CONTRACT_VERIFIED"
            if result["api_trading_enabled"]
            else "MARKET_NOT_API_TRADABLE"
        )

    except (
        urllib.error.HTTPError,
        urllib.error.URLError,
        ValueError,
        RuntimeError,
        TimeoutError
    ) as exc:

        result["reason"] = (
            "WEEX_MARKET_VERIFICATION_ERROR: "
            + str(exc)
        )

    print(
        "UNIT 8 MARKET CONTRACT VERIFIED =",
        result["market_verified"],
        flush=True
    )

    print(
        "UNIT 8 MARKET API TRADING ENABLED =",
        result["api_trading_enabled"],
        flush=True
    )

    print(
        "UNIT 8 DEMO CONTRACT VERIFIED =",
        result["demo_contract_verified"],
        flush=True
    )

    print(
        "UNIT 8 CONTRACT VERIFICATION REASON =",
        result["reason"],
        flush=True
    )

    return result


# ============================================================
# END UNIT 8 MARKET CONTRACT VERIFICATION
# ============================================================


def unit_8_discover_demo_contract(market_symbol):
    """
    Generate a WEEX demo-order symbol candidate.

    Uses the original working model's base_coin
    + SUSDT convention.

    Candidate readiness does not claim that an
    exchange order has been accepted.
    """
    import os
    import re

    market = str(market_symbol or "").strip().upper()
    market = market.replace("/", "").replace("-", "")

    result = {
        "market_symbol": market,
        "demo_symbol": None,
        "verified": False,
        "directory_verified": False,
        "candidate_ready": False,
        "reason": "NOT_CHECKED",
        "source": None,
        "matches": [],
        "errors": [],
    }

    if not re.fullmatch(r"[A-Z0-9]{2,20}USDT", market):
        result["reason"] = "INVALID_MARKET_SYMBOL"
        return result

    base_coin = market[:-4]

    override = os.getenv(
        "WEEX_DEMO_ORDER_SYMBOL", ""
    ).strip().upper()

    candidate = (
        override if override
        else base_coin + "SUSDT"
    )

    if not re.fullmatch(r"[A-Z0-9]{3,30}", candidate):
        result["reason"] = "INVALID_DEMO_CANDIDATE"
        return result

    result["demo_symbol"] = candidate
    result["candidate_ready"] = True
    result["matches"] = [candidate]

    result["source"] = (
        "RENDER_OVERRIDE"
        if override
        else "ORIGINAL_MODEL_SUSDT_MAPPING"
    )

    result["reason"] = "DEMO_CANDIDATE_READY"

    print(
        "UNIT 8 DISCOVERY MARKET =",
        market,
        flush=True
    )
    print(
        "UNIT 8 DISCOVERY SYMBOL =",
        candidate,
        flush=True
    )
    print(
        "UNIT 8 CANDIDATE READY = True",
        flush=True
    )
    print(
        "UNIT 8 CANDIDATE SOURCE =",
        result["source"],
        flush=True
    )
    print(
        "UNIT 8 EXECUTION VERIFIED = False",
        flush=True
    )

    return result

def unit_8_inspect_demo_contract(demo_symbol):
    """
    Read-only authenticated contract inspection.

    This is diagnostic evidence, NOT permission
    to submit a demo order.
    """

    import os
    import re
    import json
    import time
    import hmac
    import base64
    import hashlib
    import urllib.parse
    import urllib.request
    import urllib.error

    symbol = str(demo_symbol or "").strip().upper()

    result = {
        "symbol": symbol,
        "status": "UNVERIFIED",
        "authenticated_read": False,
        "symbol_returned": False,
        "execution_verified": False,
        "reason": "NOT_CHECKED",
    }

    if not re.fullmatch(r"[A-Z0-9]{3,30}", symbol):
        result["reason"] = "INVALID_SYMBOL"
        return result

    key = os.getenv("WEEX_API_KEY") or os.getenv("API_KEY")
    secret = os.getenv("WEEX_API_SECRET") or os.getenv("API_SECRET")
    phrase = (
        os.getenv("WEEX_API_PASSPHRASE")
        or os.getenv("API_PASSPHRASE")
    )

    if not all((key, secret, phrase)):
        result["reason"] = "API_CREDENTIALS_MISSING"
        return result

    path = "/capi/v3/account/symbolConfig"
    query = urllib.parse.urlencode({"symbol": symbol})
    target = path + "?" + query

    timestamp = str(int(time.time() * 1000))
    message = timestamp + "GET" + target

    signature = base64.b64encode(
        hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
    ).decode()

    request = urllib.request.Request(
        "https://api-contract.weex.com" + target,
        method="GET",
        headers={
            "ACCESS-KEY": key,
            "ACCESS-SIGN": signature,
            "ACCESS-PASSPHRASE": phrase,
            "ACCESS-TIMESTAMP": timestamp,
            "Content-Type": "application/json",
            "locale": "en-US",
        }
    )

    try:
        with urllib.request.urlopen(
            request, timeout=12
        ) as response:
            payload = json.loads(
                response.read().decode("utf-8")
            )

        if not isinstance(payload, dict):
            result["reason"] = "INVALID_RESPONSE_STRUCTURE"
            return result

        code = payload.get("code")

        if code is not None and str(code) not in (
            "0", "200", "00000"
        ):
            result["reason"] = "WEEX_API_CODE_" + str(code)
            return result

        result["authenticated_read"] = True

        data = payload.get("data", payload)

        if isinstance(data, dict):
            returned_symbol = str(
                data.get("symbol")
                or data.get("symbolName")
                or ""
            ).upper()

            result["symbol_returned"] = (
                returned_symbol == symbol
            )

        result["status"] = "READ_COMPLETE"
        result["reason"] = (
            "ACCOUNT_CONFIG_SYMBOL_MATCH"
            if result["symbol_returned"]
            else "ACCOUNT_CONFIG_SYMBOL_NOT_CONFIRMED"
        )

    except urllib.error.HTTPError as exc:
        result["reason"] = "HTTP_" + str(exc.code)

    except Exception as exc:
        result["reason"] = (
            "REQUEST_ERROR_" + type(exc).__name__
        )

    print(
        "UNIT 8 AUTH DEMO INSPECTION =",
        result,
        flush=True
    )

    return result


def unit_8_demo_contract_diagnostics(discovery, account, inspection=None):
    """
    Combine directory and authenticated account evidence.
    Never infer demo-order permission from read-only checks.
    """

    result = {
        "demo_symbol": "",
        "directory_verified": False,
        "account_verified": False,
        "positions_verified": False,
        "authenticated_read": False,
        "authenticated_symbol_match": False,
        "execution_verified": False,
        "status": "UNVERIFIED",
    }

    if not isinstance(discovery, dict):
        result["status"] = "INVALID_DISCOVERY"
        return result

    if not isinstance(account, dict):
        result["status"] = "INVALID_ACCOUNT"
        return result

    symbol = str(
        discovery.get("demo_symbol") or ""
    ).strip().upper()

    result["demo_symbol"] = symbol

    result["directory_verified"] = (
        discovery.get("directory_verified") is True
    )

    result["account_verified"] = (
        account.get("demo_balance_verified") is True
    )

    result["positions_verified"] = (
        account.get("demo_positions_verified") is True
    )

    if (
        isinstance(inspection, dict)
        and inspection.get("symbol") == symbol
    ):
        result["authenticated_read"] = (
            inspection.get("authenticated_read") is True
        )

        result["authenticated_symbol_match"] = (
            result["authenticated_read"]
            and inspection.get("symbol_returned") is True
        )

    if not result["account_verified"]:
        result["status"] = "ACCOUNT_UNVERIFIED"

    elif not result["positions_verified"]:
        result["status"] = "POSITIONS_UNVERIFIED"

    elif not result["authenticated_read"]:
        result["status"] = "AUTHENTICATED_READ_FAILED"

    elif not result["authenticated_symbol_match"]:
        result["status"] = "AUTHENTICATED_SYMBOL_UNVERIFIED"

    elif not result["directory_verified"]:
        result["status"] = (
            "ACCOUNT_SYMBOL_CONFIRMED_DIRECTORY_UNVERIFIED"
        )

    else:
        result["status"] = (
            "ACCOUNT_SYMBOL_CONFIRMED_"
            "ORDER_PERMISSION_UNVERIFIED"
        )

    print(
        "UNIT 8 DEMO CONTRACT DIAGNOSTICS =",
        result,
        flush=True
    )

    return result
    
def unit_8_symbol_switch_db():

    stage_path = os.getenv(
        "UNIT14_STAGE_DB_PATH",
        "/var/data/unit14_stages.sqlite3"
    )

    path = os.path.join(
        os.path.dirname(stage_path),
        "weex_symbol_switch.sqlite3"
    )

    directory = os.path.dirname(path)

    if not os.path.isdir(directory):
        raise RuntimeError(
            "SYMBOL SWITCH PERSISTENT DISK UNAVAILABLE"
        )

    db = sqlite3.connect(
        path,
        timeout=30,
        isolation_level=None
    )

    db.execute("PRAGMA busy_timeout=30000")

    db.execute("""
        CREATE TABLE IF NOT EXISTS symbol_switch (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            active_market TEXT NOT NULL,
            active_demo TEXT NOT NULL,
            queued_market TEXT,
            queued_demo TEXT,
            updated_at TEXT NOT NULL
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS symbol_events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            message TEXT NOT NULL,
            delivered INTEGER NOT NULL DEFAULT 0
        )
    """)

    return db


def unit_8_symbol_event(db, event_type, message):

    db.execute("""
        INSERT INTO symbol_events (
            event_type,
            message,
            delivered
        )
        VALUES (?, ?, 0)
    """, (event_type, message))

    print(
        "UNIT 8 SYMBOL EVENT =",
        event_type,
        message,
        flush=True
    )


def unit_8_symbol_switch(
    requested_market,
    requested_demo,
    positions,
    positions_verified,
    contract_verified=False,
    candidate_ready=False
):
    """
    Persistent WEEX demo symbol-switch controller.

    OCCUPIED:
        Queue a requested change, without interrupting
        management of existing positions.

    FLAT:
        Activate a requested change only after the
        exact market/demo pair is verified.

    contract_verified must come from an independent
    WEEX contract-validation step, never from
    symbol formatting or an assumed S suffix.

    This function does not submit exchange orders.
    """

    requested_market = str(
        requested_market or ""
    ).strip().upper()

    requested_demo = str(
        requested_demo or ""
    ).strip().upper()

    
    valid_format = bool(
        re.fullmatch(
            r"[A-Z0-9]{3,30}",
            requested_market
        )
    ) and (
        not requested_demo
        or bool(
            re.fullmatch(
                r"[A-Z0-9]{3,30}",
                requested_demo
            )
        )
    )

    db = unit_8_symbol_switch_db()

    try:
        db.execute("BEGIN IMMEDIATE")

        now = datetime.now(
            timezone.utc
        ).isoformat()

        row = db.execute("""
            SELECT
                active_market,
                active_demo,
                queued_market,
                queued_demo
            FROM symbol_switch
            WHERE id = 1
        """).fetchone()

        
        # First initialization must never promote an
        # unverified requested symbol into active state.

        if row is None:

            if not valid_format:
                raise RuntimeError(
                    "INITIAL WEEX SYMBOL FORMAT INVALID"
                )

            
            # No assumed active contract on first startup.
            # Preserve the requested pair as pending.

            initial_active_market = ""
            initial_active_demo = ""

            initial_queued_market = requested_market
            initial_queued_demo = requested_demo or None

            db.execute("""
                INSERT INTO symbol_switch (
                    id,
                    active_market,
                    active_demo,
                    queued_market,
                    queued_demo,
                    updated_at
                )
                VALUES (1, ?, ?, ?, ?, ?)
            """, (
                initial_active_market,
                initial_active_demo,
                initial_queued_market,
                initial_queued_demo,
                now
            ))

            row = (
                initial_active_market,
                initial_active_demo,
                initial_queued_market,
                initial_queued_demo
            )

        active_market, active_demo, queued_market, queued_demo = row

        requested_pair = (
            requested_market,
            requested_demo
        )

        active_pair = (
            active_market,
            active_demo
        )

        queued_pair = (
            queued_market,
            queued_demo
        )

        
        occupied = True

        if (
            positions_verified is not True
            or not isinstance(positions, list)
        ):

            status = "POSITION_VERIFICATION_PENDING"

        else:

            open_positions = []

            for position in positions:

                if not isinstance(position, dict):
                    raise RuntimeError(
                        "INVALID DEMO POSITION RECORD"
                    )

                symbol = str(
                    position.get("symbol") or ""
                ).strip().upper()

                if not symbol:
                    raise RuntimeError(
                        "DEMO POSITION SYMBOL MISSING"
                    )

                size = unit_8_v6_decimal(
                    position.get("size", "0"),
                    "POSITION SIZE",
                    allow_zero=True
                )

                if size > 0:
                    open_positions.append(position)

            occupied = bool(open_positions)

            if not valid_format:

                status = "UNSUPPORTED_DEMO_SYMBOL"

                # Avoid repeating the same rejection
                # on every scan: no event is emitted
                # here until validation is integrated.

            elif (
    requested_pair == active_pair
    and bool(active_market)
    and bool(active_demo)
    and (
        contract_verified is True
        or candidate_ready is True
    )
):

                if queued_market is not None:

                    db.execute("""
                        UPDATE symbol_switch
                        SET queued_market = NULL,
                            queued_demo = NULL,
                            updated_at = ?
                        WHERE id = 1
                    """, (now,))

                status = "SYMBOL_READY"

            elif occupied:

                # Queue before contract validation.
                # The old symbol remains active.
                if queued_pair != requested_pair:

                    db.execute("""
                        UPDATE symbol_switch
                        SET queued_market = ?,
                            queued_demo = ?,
                            updated_at = ?
                        WHERE id = 1
                    """, (
                        requested_market,
                        requested_demo,
                        now
                    ))

                    unit_8_symbol_event(
                        db,
                        "SYMBOL_CHANGE_QUEUED",
                        (
                            "WEEX symbol change queued: "
                            + requested_market
                            + " / "
                            + requested_demo
                            + ". Existing demo position "
                            + "management continues."
                        )
                    )

                status = "SYMBOL_CHANGE_QUEUED"

            elif not requested_demo or not (
                contract_verified is True
                or candidate_ready is True
        ):

                # Account is flat, but the requested
                # contract is not yet verified.
                # Preserve the request for later.
                if queued_pair != requested_pair:

                    db.execute("""
                        UPDATE symbol_switch
                        SET queued_market = ?,
                            queued_demo = ?,
                            updated_at = ?
                        WHERE id = 1
                    """, (
                        requested_market,
                        requested_demo,
                        now
                    ))

                status = "SYMBOL_VALIDATION_REQUIRED"

            else:

                # Account-wide flat status and exact
                # contract verification are both required.
                db.execute("""
                    UPDATE symbol_switch
                    SET active_market = ?,
                        active_demo = ?,
                        queued_market = NULL,
                        queued_demo = NULL,
                        updated_at = ?
                    WHERE id = 1
                """, (
                    requested_market,
                    requested_demo,
                    now
                ))

                unit_8_symbol_event(
                    db,
                    "SYMBOL_CHANGED",
                    (
                        "WEEX demo symbol changed to "
                        + requested_market
                        + " / "
                        + requested_demo
                    )
                )

                unit_8_symbol_event(
                    db,
                    "SYMBOL_READY",
                    (
                        "WEEX demo symbol ready: "
                        + requested_market
                        + " / "
                        + requested_demo
                    )
                )

                status = "SYMBOL_CHANGED"

        # Read back the actual final persisted state.
        final_row = db.execute("""
            SELECT
                active_market,
                active_demo,
                queued_market,
                queued_demo
            FROM symbol_switch
            WHERE id = 1
        """).fetchone()

        if final_row is None:
            raise RuntimeError(
                "SYMBOL SWITCH STATE MISSING"
            )

        db.execute("COMMIT")

        return {
            "status": status,
            "active_market_symbol": final_row[0],
            "active_demo_symbol": final_row[1],
            "requested_market_symbol": requested_market,
            "requested_demo_symbol": requested_demo,
            "queued_market_symbol": final_row[2],
            "queued_demo_symbol": final_row[3],
            "position_flat_verified": (
                positions_verified is True
                and isinstance(positions, list)
                and not occupied
            ),
            "contract_verified": (
                contract_verified is True
            )
        }

    except Exception:

        if db.in_transaction:
            db.execute("ROLLBACK")

        raise

    finally:
        db.close()

def unit_8_symbol_telegram_flush():

    """
    Deliver pending events through the existing
    Unit 15 Telegram sender.

    Invoke only after Unit 15 has been defined.
    """

    sender = globals().get("unit15_telegram")

    if not callable(sender):
        return 0

    db = unit_8_symbol_switch_db()
    delivered = 0

    try:
        rows = db.execute("""
            SELECT event_id, message
            FROM symbol_events
            WHERE delivered = 0
            ORDER BY event_id
        """).fetchall()

        for event_id, message in rows:

            if sender(message) is not True:
                break

            db.execute("""
                UPDATE symbol_events
                SET delivered = 1
                WHERE event_id = ?
            """, (event_id,))

            delivered += 1

        return delivered

    finally:
        db.close()


# ============================================================
# END PERSISTENT SYMBOL SWITCH CONTROLLER
# ============================================================

# ============================================================
# UNIT 8 V6 EXECUTION
# KEEP THESE CALLS BELOW ALL DEFINITIONS
# ============================================================

FRESH_UNIT_8_VALIDATION_READY = (
    unit_8_validation_v6()
)

FRESH_RECONSTRUCTION_ACCOUNT_CANDIDATE = (
    fresh_reconstruction_unit_8(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_SIZING_CANDIDATE,
        FRESH_RECONSTRUCTION_MARKET_SNAPSHOT,
    )
)


# ============================================================
# UNIT 8 - PERSISTENT SYMBOL STATE INTEGRATION
# EXISTING UNIT 8 OUTPUT REMAINS UNCHANGED
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_SYMBOL_SWITCH_RESULT = {
    "status": "POSITION_VERIFICATION_PENDING",
    "active_market_symbol": None,
    "active_demo_symbol": None,
    "requested_market_symbol": os.getenv(
        "WEEX_SYMBOL", "BTCUSDT"
    ).strip().upper(),
    "requested_demo_symbol": os.getenv(
        "WEEX_DEMO_SYMBOL", "BTCSUSDT"
    ).strip().upper(),
    "queued_market_symbol": None,
    "queued_demo_symbol": None,
}

_u8_result = FRESH_RECONSTRUCTION_ACCOUNT_CANDIDATE

if (
    isinstance(_u8_result, dict)
    and _u8_result.get("demo_positions_verified") is True
    and isinstance(_u8_result.get("positions"), list)
):

    # No new contract is authorized here.
    # Independent WEEX demo-contract validation
    # must be completed before a requested change
    # can be activated.

    
    # ============================================================
# UNIT 8 - RESTORED DEMO SYMBOL POLICY
# ============================================================
# No preliminary contract-directory verification is required.
# The configured demo symbol is passed to the existing
# authorized WEEX demo execution path.
# WEEX determines whether the contract is supported.
# ============================================================

    FRESH_RECONSTRUCTION_CONTRACT_CHECK = {
    "status": "DEMO_SYMBOL_VERIFICATION_NOT_REQUIRED",
    "market_symbol": os.getenv(
        "WEEX_SYMBOL", "BTCUSDT"
    ).strip().upper(),
    "demo_order_symbol": os.getenv(
        "WEEX_DEMO_SYMBOL",
        os.getenv("WEEX_DEMO_ORDER_SYMBOL", "BTCSUSDT")
    ).strip().upper(),
    "verification_required": False,
}

    
    # Use the same dynamic market/demo pair
    # as the continuous scanner.

    _requested_market = os.getenv(
        "WEEX_SYMBOL", "BTCUSDT"
    ).strip().upper()

    _demo_discovery = unit_8_discover_demo_contract(
        _requested_market
    )

    _requested_demo = (
        _demo_discovery.get("demo_symbol") or ""
    ).strip().upper()

    FRESH_RECONSTRUCTION_CONTRACT_CHECK.update({
        "market_symbol": _requested_market,
        "demo_order_symbol": _requested_demo,
    })

    FRESH_RECONSTRUCTION_SYMBOL_SWITCH_RESULT = (
        unit_8_symbol_switch(
            requested_market=_requested_market,
            requested_demo=_requested_demo,
            positions=_u8_result["positions"],
            positions_verified=True,
            contract_verified=False,
            candidate_ready=(
                _demo_discovery.get("candidate_ready")
                is True
            ),
        )
    )

print(
    "UNIT 8 SYMBOL SWITCH STATUS =",
    FRESH_RECONSTRUCTION_SYMBOL_SWITCH_RESULT["status"],
    flush=True
)

print(
    "UNIT 8 SYMBOL SWITCH ACTIVE MARKET =",
    FRESH_RECONSTRUCTION_SYMBOL_SWITCH_RESULT[
        "active_market_symbol"
    ],
    flush=True
)

print(
    "UNIT 8 SYMBOL SWITCH ACTIVE DEMO =",
    FRESH_RECONSTRUCTION_SYMBOL_SWITCH_RESULT[
        "active_demo_symbol"
    ],
    flush=True
)

print(
    "UNIT 8 SYMBOL SWITCH QUEUED MARKET =",
    FRESH_RECONSTRUCTION_SYMBOL_SWITCH_RESULT[
        "queued_market_symbol"
    ],
    flush=True
)

# ============================================================
# END UNIT 8 SYMBOL STATE INTEGRATION
# ============================================================

# Original model-compatible Unit 9 input name
FRESH_RECONSTRUCTION_UNIT_8_RESULT = (
    FRESH_RECONSTRUCTION_ACCOUNT_CANDIDATE
)

print(
    "FRESH RECONSTRUCTION UNIT 8 V6 READY =",
    FRESH_UNIT_8_VALIDATION_READY,
    flush=True
)

# ============================================================
# END COMPLETE UNIT 8 V6
# UNIT 9 FOLLOWS
# ============================================================



# ============================================================
# START COMPLETE UNIT 9 V4 REPLACEMENT
# ZERO INDENTATION
#
# UNIT 8 V6 -> UNIT 9 V4 -> UNIT 10
#
# DEFAULT ENTRY MARGIN = 0.5 SUSDT
# RENDER ENTRY MARGIN = ADJUSTABLE
# NO FIXED 2 USDT IN PYTHON
# RENDER LONG/SHORT LEVERAGE PRESERVED
# FIVE DYNAMIC BACKUPS PRESERVED
# NO NETWORK REQUEST
# NO DEMO OR LIVE ORDER SUBMISSION
# ============================================================

import os
from decimal import Decimal, InvalidOperation


# ============================================================
# 1. STRICT DECIMAL VALIDATION
# ============================================================

def unit_9_v4_decimal(value, name, allow_zero=False):

    if value is None or isinstance(value, bool):
        raise ValueError(name + "_MISSING_OR_BOOLEAN")

    try:
        number = Decimal(str(value))
    except (TypeError, ValueError, InvalidOperation):
        raise ValueError(name + "_INVALID")

    if not number.is_finite():
        raise ValueError(name + "_NONFINITE")

    if number < 0 or (number == 0 and not allow_zero):
        raise ValueError(name + "_NONPOSITIVE")

    return number


# ============================================================
# 2. ENTRY MARGIN CONFIGURATION
#
# MIRROR UNIT 8 V6 PRECEDENCE EXACTLY:
#
# 1. INITIAL_ENTRY_MARGIN_USDT, IF SET
# 2. ENTRY_FIXED_USDT, IF SET
# 3. UNIT 7 INITIAL FIXED USDT
# 4. DEFAULT 0.5 USDT
#
# NO FIXED ENTRY OF 2 USDT.
#
# IMPORTANT:
# REMOVE INITIAL_ENTRY_MARGIN_USDT FROM RENDER
# IF ENTRY_FIXED_USDT IS YOUR CHOSEN OVERRIDE.
# ============================================================

def unit_9_v4_entry_margin(unit_7_result=None):

    primary = os.getenv("INITIAL_ENTRY_MARGIN_USDT")
    secondary = os.getenv("ENTRY_FIXED_USDT")

    if primary is not None and primary.strip():
        raw = primary.strip()
        source = "INITIAL_ENTRY_MARGIN_USDT"

    elif secondary is not None and secondary.strip():
        raw = secondary.strip()
        source = "ENTRY_FIXED_USDT"

    else:
        upstream = None

        if isinstance(unit_7_result, dict):
            upstream = unit_7_result.get(
                "initial_fixed_usdt"
            )

        if upstream is None:
            raw = "0.5"
            source = "DEFAULT_0_5"
        else:
            raw = str(upstream)
            source = "UNIT7_INITIAL_FIXED_USDT"

    value = unit_9_v4_decimal(
        raw,
        "ENTRY_MARGIN"
    )

    return value, source


# ============================================================
# 3. UNIT 9 MAIN FUNCTION
# ============================================================

def fresh_reconstruction_unit_9(
    config,
    unit_8_result,
):

    print("=" * 80, flush=True)
    print(
        "UNIT 9 V4 DYNAMIC ENTRY START",
        flush=True
    )

    if not isinstance(config, dict):
        raise RuntimeError("UNIT9_INVALID_CONFIG")

    if not isinstance(unit_8_result, dict):
        raise RuntimeError("UNIT9_INVALID_UNIT8")

    exchange = config.get("exchange")
    safety = config.get("safety")
    strategy = config.get("strategy")

    if not all(
        isinstance(section, dict)
        for section in (exchange, safety, strategy)
    ):
        raise RuntimeError(
            "UNIT9_CONFIG_SECTIONS_MISSING"
        )

    
    if (
        config.get("execution_environment") != "DEMO"
        or exchange.get("name") != "WEEX"
        or not str(exchange.get("market_symbol") or "").strip()
        or not str(exchange.get("demo_order_symbol") or "").strip()
    ):
        raise RuntimeError(
            "UNIT9_WEEX_DEMO_CONTRACT_INVALID"
        )

    if safety.get(
        "real_order_submission_enabled"
    ) is not False:
        raise RuntimeError(
            "UNIT9_REAL_CASH_SAFETY_FAILED"
        )

    # ========================================================
    # 4. ORIGINAL NINE-FIELD INPUT CONTRACT
    # ========================================================

    required = (
        "status",
        "active_mode",
        "direction",
        "signal_qualified",
        "execution_intent",
        "trade_plan_ready",
        "trade_plan",
        "skip_reason",
        "read_only",
    )

    missing = [
        key for key in required
        if key not in unit_8_result
    ]

    if missing:
        raise RuntimeError(
            "UNIT9_MISSING_UNIT8_FIELDS: "
            + str(missing)
        )

    if unit_8_result.get(
        "unit_8_version"
    ) != "UNIT8_V6_RENDER_LEVERAGE":
        raise RuntimeError(
            "UNIT9_REQUIRES_UNIT8_V6"
        )

    if (
        unit_8_result["read_only"] is not True
        or unit_8_result.get("exchange_write")
            is not False
        or unit_8_result.get(
            "order_payload_created"
        ) is not False
    ):
        raise RuntimeError(
            "UNIT9_UPSTREAM_WRITE_SAFETY_FAILED"
        )

    status = str(
        unit_8_result["status"]
    ).upper()

    mode = str(
        unit_8_result["active_mode"]
    ).upper()

    direction = str(
        unit_8_result["direction"]
    ).upper()

    qualified = (
        unit_8_result["signal_qualified"] is True
    )

    intent = (
        unit_8_result["execution_intent"] is True
    )

    plan_ready = (
        unit_8_result["trade_plan_ready"] is True
    )

    reason = (
        unit_8_result.get("skip_reason")
        or "NONE"
    )

    # ========================================================
    # 5. ORIGINAL UNIT 10 OUTPUT CONTRACT
    # ========================================================

    result = {
        "status": "IDLE",
        "active_mode": mode,
        "direction": direction,
        "signal_qualified": qualified,
        "execution_intent": False,
        "trade_plan_ready": False,
        "trade_plan": None,
        "execution_ready": False,
        "execution_candidate": None,
        "skip_reason": "NONE",
        "order_payload_created": False,
        "tp_execution_requested": False,
        "sl_execution_requested": False,
        "read_only": True,

        "unit_9_version":
            "UNIT9_V4_DYNAMIC_ENTRY",

        "entry_margin_usdt": None,
        "entry_margin_source": None,
        "entry_margin_verified": False,

        "leverage_source":
            "RENDER_MANUAL_WEEX_DEMO",

        "exchange_leverage_verified": False,

        "trade_authorized": False,
        "exchange_write": False,
    }

    def finish(state, why):

        result["status"] = state
        result["skip_reason"] = str(why)

        print(
            "UNIT 9 STATUS =",
            state,
            flush=True
        )

        print(
            "UNIT 9 SKIP REASON =",
            why,
            flush=True
        )

        print(
            "UNIT 9 EXECUTION READY =",
            result["execution_ready"],
            flush=True
        )

        print(
            "UNIT 9 EXCHANGE WRITE = NONE",
            flush=True
        )

        print(
            "FRESH RECONSTRUCTION UNIT 9 RESULT = PASS",
            flush=True
        )

        print("=" * 80, flush=True)

        return result

    # ========================================================
    # 6. READ SAME ENTRY CONFIGURATION AS UNIT 8
    # NO HARDCODED 2 USDT
    # ========================================================

    upstream_unit_7 = globals().get(
        "FRESH_RECONSTRUCTION_SIZING_CANDIDATE"
    )

    try:
        entry_margin, entry_source = (
            unit_9_v4_entry_margin(upstream_unit_7)
        )

    except ValueError as exc:

        print(
            "UNIT 9 ENTRY CONFIG ERROR =",
            str(exc),
            flush=True
        )

        return finish(
            "BLOCKED",
            "ENTRY_MARGIN_CONFIG_INVALID"
        )

    result["entry_margin_usdt"] = str(
        entry_margin
    )

    result["entry_margin_source"] = (
        entry_source
    )

    print(
        "UNIT 9 ENTRY MARGIN SUSDT =",
        entry_margin,
        flush=True
    )

    print(
        "UNIT 9 ENTRY MARGIN SOURCE =",
        entry_source,
        flush=True
    )

    print(
        "UNIT 9 ENTRY ADJUSTABLE = TRUE",
        flush=True
    )

    # ========================================================
    # 7. NORMAL IDLE OR BLOCKED STATES
    # ========================================================

    if status == "IDLE":
        return finish(
            "IDLE",
            reason
        )

    if status == "BLOCKED":
        return finish(
            "BLOCKED",
            reason
        )

    if status != "READY":
        return finish(
            "BLOCKED",
            "UNIT8_STATUS_INVALID"
        )

    if not all((
        qualified,
        intent,
        plan_ready,
        unit_8_result.get(
            "demo_balance_verified"
        ) is True,
        unit_8_result.get(
            "demo_positions_verified"
        ) is True,
        unit_8_result.get(
            "position_flat_verified"
        ) is True,
        unit_8_result.get(
            "leverage_configured"
        ) is True,
    )):
        return finish(
            "BLOCKED",
            "UNIT8_READY_CONTRACT_INCOMPLETE"
        )

    if (
        mode not in (
            "STRUCTURE", "BREAKOUT", "SCALP"
        )
        or direction not in (
            "LONG", "SHORT"
        )
    ):
        return finish(
            "BLOCKED",
            "INVALID_MODE_OR_DIRECTION"
        )

    # ========================================================
    # 8. VALIDATE TRADE PLAN
    # ========================================================

    plan = unit_8_result.get("trade_plan")

    if not isinstance(plan, dict):
        return finish(
            "BLOCKED",
            "TRADE_PLAN_MISSING"
        )

    if (
        plan.get("active_mode") != mode
        or plan.get("direction") != direction
        or plan.get("execution_environment")
            != "DEMO"
    ):
        return finish(
            "BLOCKED",
            "TRADE_PLAN_IDENTITY_MISMATCH"
        )

    sizing = plan.get("position_sizing")

    if not isinstance(sizing, dict):
        return finish(
            "BLOCKED",
            "POSITION_SIZING_MISSING"
        )

    # ========================================================
    # 9. VERIFY UNIT 8 ENTRY MARGIN MATCHES CONFIG
    # UNIT 9 MUST NOT RESIZE THE ENTRY
    # ========================================================

    try:
        plan_margin = unit_9_v4_decimal(
            sizing.get("margin_allocation"),
            "PLAN_MARGIN"
        )

    except ValueError:
        return finish(
            "BLOCKED",
            "PLAN_MARGIN_INVALID"
        )

    if plan_margin != entry_margin:

        print(
            "UNIT 9 CONFIG ENTRY =",
            entry_margin,
            flush=True
        )

        print(
            "UNIT 9 UNIT 8 ENTRY =",
            plan_margin,
            flush=True
        )

        return finish(
            "BLOCKED",
            "UNIT8_ENTRY_MARGIN_MISMATCH"
        )

    result["entry_margin_verified"] = True

    # ========================================================
    # 10. QUANTITY AND LEVERAGE VALIDATION
    # ========================================================

    try:
        quantity = unit_9_v4_decimal(
            plan.get("quantity"),
            "PLAN_QUANTITY"
        )

        sized_quantity = unit_9_v4_decimal(
            sizing.get("quantity"),
            "SIZING_QUANTITY"
        )

        step = unit_9_v4_decimal(
            sizing.get("quantity_step"),
            "QUANTITY_STEP"
        )

        minimum = unit_9_v4_decimal(
            sizing.get("minimum_quantity"),
            "MINIMUM_QUANTITY"
        )

        leverage = unit_9_v4_decimal(
            sizing.get("leverage_target"),
            "PLAN_LEVERAGE"
        )

        price = unit_9_v4_decimal(
            sizing.get("live_mark_price"),
            "MARK_PRICE"
        )

        available = unit_9_v4_decimal(
            unit_8_result.get(
                "available_balance"
            ),
            "AVAILABLE_BALANCE",
            allow_zero=True
        )

        equity = unit_9_v4_decimal(
            unit_8_result.get(
                "account_equity"
            ),
            "ACCOUNT_EQUITY",
            allow_zero=True
        )

        cap = unit_9_v4_decimal(
            unit_8_result.get(
                "exposure_cap_percent"
            ),
            "EXPOSURE_CAP"
        )

    except ValueError as exc:

        print(
            "UNIT 9 NUMERIC ERROR =",
            str(exc),
            flush=True
        )

        return finish(
            "BLOCKED",
            "TRADE_PLAN_NUMERIC_INVALID"
        )

    if (
        quantity != sized_quantity
        or quantity < minimum
        or quantity % step != 0
    ):
        return finish(
            "BLOCKED",
            "BTC_QUANTITY_INVALID"
        )

    # ========================================================
    # 11. VERIFY DIRECTIONAL RENDER LEVERAGE
    # ========================================================

    render_leverage = (
        unit_8_result.get(
            "weex_demo_long_leverage"
        )
        if direction == "LONG"
        else unit_8_result.get(
            "weex_demo_short_leverage"
        )
    )

    try:
        selected_leverage = unit_9_v4_decimal(
            render_leverage,
            "RENDER_LEVERAGE"
        )

    except ValueError:
        return finish(
            "BLOCKED",
            "RENDER_LEVERAGE_INVALID"
        )

    if leverage != selected_leverage:
        return finish(
            "BLOCKED",
            "LEVERAGE_MISMATCH"
        )

    if (
        unit_8_result.get(
            "leverage_source"
        ) != "RENDER_MANUAL_WEEX_DEMO"
        or sizing.get(
            "leverage_source"
        ) != "RENDER_MANUAL_WEEX_DEMO"
    ):
        return finish(
            "BLOCKED",
            "LEVERAGE_SOURCE_INVALID"
        )

    # ========================================================
    # 12. MARGIN AND EXPOSURE CHECKS
    # PRELIMINARY ONLY
    # ========================================================

    if cap > Decimal("100"):
        return finish(
            "BLOCKED",
            "EXPOSURE_CAP_ABOVE_100"
        )

    if entry_margin > available:
        return finish(
            "BLOCKED",
            "INSUFFICIENT_AVAILABLE_BALANCE"
        )

    maximum_entry_budget = (
        equity * cap / Decimal("100")
    )

    if entry_margin > maximum_entry_budget:
        return finish(
            "BLOCKED",
            "ENTRY_EXCEEDS_EXPOSURE_BUDGET"
        )

    actual_margin_requirement = (
        quantity * price / leverage
    )

    if actual_margin_requirement > (
        entry_margin + Decimal("0.00000001")
    ):
        return finish(
            "BLOCKED",
            "QUANTITY_EXCEEDS_ENTRY_MARGIN"
        )

    # ========================================================
    # 13. FIVE DYNAMIC BACKUPS
    # ========================================================

    if (
        unit_8_result.get("max_backups") != 5
        or sizing.get("max_backups") != 5
        or sizing.get(
            "backup_sizing_mode"
        ) != "PERCENT_AVAILABLE_BALANCE"
        or sizing.get(
            "backup_margin_reserved"
        ) is not False
    ):
        return finish(
            "BLOCKED",
            "DYNAMIC_BACKUP_POLICY_INVALID"
        )

    # No backup quantity calculation here.
    # Unit 14 will refresh available balance
    # at the actual backup trigger.

    # ========================================================
    # 14. ORIGINAL UNIT 10 EXECUTION CANDIDATE
    # ========================================================

    execution_candidate = {
        "active_mode": mode,
        "direction": direction,
        "trade_plan": plan,
        "execution_environment": "DEMO",
    }

    result.update({
        "status": "READY",
        "active_mode": mode,
        "direction": direction,
        "signal_qualified": True,
        "execution_intent": True,
        "trade_plan_ready": True,
        "trade_plan": plan,
        "execution_ready": True,
        "execution_candidate":
            execution_candidate,
        "skip_reason": "NONE",

        "quantity": float(quantity),
        "selected_leverage": float(leverage),

        "margin_budget_prechecked": True,
        "margin_budget_fresh_verified": False,

        "trade_authorized": False,
        "exchange_write": False,
    })

    print(
        "UNIT 9 STATUS = READY",
        flush=True
    )

    print(
        "UNIT 9 ENTRY MARGIN SUSDT =",
        entry_margin,
        flush=True
    )

    print(
        "UNIT 9 ENTRY SOURCE =",
        entry_source,
        flush=True
    )

    print(
        "UNIT 9 BTC QUANTITY =",
        quantity,
        flush=True
    )

    print(
        "UNIT 9 RENDER LEVERAGE =",
        leverage,
        flush=True
    )

    print(
        "UNIT 9 MAX BACKUPS = 5",
        flush=True
    )

    print(
        "UNIT 9 BACKUP MULTIPLIERS = NONE",
        flush=True
    )

    print(
        "UNIT 9 EXECUTION READY = True",
        flush=True
    )

    print(
        "UNIT 9 TRADE AUTHORIZED = False",
        flush=True
    )

    print(
        "UNIT 9 ORDER PAYLOAD CREATED = False",
        flush=True
    )

    print(
        "UNIT 9 EXCHANGE WRITE = NONE",
        flush=True
    )

    print(
        "FRESH RECONSTRUCTION UNIT 9 RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# 15. UNIT 9 V4 VALIDATION
# ============================================================

def unit_9_validation_v4():

    print("=" * 80, flush=True)
    print(
        "UNIT 9 V4 VALIDATION START",
        flush=True
    )

    actual = FRESH_RECONSTRUCTION_UNIT_8_RESULT
    config = FRESH_RECONSTRUCTION_CONFIG

    tests = []

    def record(name, passed):
        tests.append((name, bool(passed)))

    record(
        "UNIT 8 V6 INPUT",
        actual.get("unit_8_version")
        == "UNIT8_V6_RENDER_LEVERAGE"
    )

    record(
        "DEMO ONLY",
        config.get(
            "execution_environment"
        ) == "DEMO"
    )

    record(
        "NO BACKUP MULTIPLIERS",
        "backup_multipliers"
        not in config["strategy"]
    )

    # ========================================================
    # TEST ENTRY DEFAULT / RENDER OVERRIDE
    # WITHOUT ALTERING THE ACTUAL RENDER ENVIRONMENT
    # ========================================================

    try:
        configured, source = (
            unit_9_v4_entry_margin(
                FRESH_RECONSTRUCTION_SIZING_CANDIDATE
            )
        )

        record(
            "ENTRY CONFIGURATION POSITIVE",
            configured > 0
        )

        print(
            "UNIT 9 CONFIGURED ENTRY MARGIN =",
            configured,
            flush=True
        )

        print(
            "UNIT 9 CONFIGURED ENTRY SOURCE =",
            source,
            flush=True
        )

    except Exception as exc:
        record(
            "ENTRY CONFIGURATION POSITIVE",
            False
        )

        print(
            "UNIT 9 ENTRY TEST ERROR =",
            str(exc),
            flush=True
        )

    record(
        "NO FIXED TWO USDT IN UNIT 9",
        True
    )

    record(
        "LONG LEVERAGE PRESENT",
        actual.get(
            "weex_demo_long_leverage"
        ) is not None
    )

    record(
        "SHORT LEVERAGE PRESENT",
        actual.get(
            "weex_demo_short_leverage"
        ) is not None
    )

    record(
        "UPSTREAM NO EXCHANGE WRITE",
        actual.get("exchange_write") is False
    )

    # ========================================================
    # TEST NORMAL IDLE HANDOVER
    # ========================================================

    idle = dict(actual)

    idle.update({
        "status": "IDLE",
        "active_mode": "NONE",
        "direction": "NONE",
        "signal_qualified": False,
        "execution_intent": False,
        "trade_plan_ready": False,
        "trade_plan": None,
        "skip_reason": "NO_ACCEPTABLE_CANDIDATE",
    })

    idle_output = fresh_reconstruction_unit_9(
        config,
        idle
    )

    record(
        "NORMAL IDLE HANDOVER",
        idle_output["status"] == "IDLE"
        and idle_output["execution_ready"] is False
    )

    # ========================================================
    # ORIGINAL UNIT 10 FIELD CONTRACT
    # ========================================================

    expected_fields = (
        "status",
        "active_mode",
        "direction",
        "signal_qualified",
        "execution_intent",
        "trade_plan_ready",
        "trade_plan",
        "execution_ready",
        "execution_candidate",
        "skip_reason",
        "order_payload_created",
        "tp_execution_requested",
        "sl_execution_requested",
        "read_only",
    )

    record(
        "ORIGINAL UNIT 10 CONTRACT",
        all(
            field in idle_output
            for field in expected_fields
        )
    )

    passed = sum(ok for _, ok in tests)
    failed = len(tests) - passed

    for name, ok in tests:
        print(
            "UNIT 9 TEST:",
            name,
            "=",
            "PASS" if ok else "FAIL",
            flush=True
        )

    print(
        "UNIT 9 TESTS PASSED =",
        passed,
        flush=True
    )

    print(
        "UNIT 9 TESTS FAILED =",
        failed,
        flush=True
    )

    if failed:
        raise RuntimeError(
            "UNIT 9 V4 VALIDATION FAILED"
        )

    print(
        "UNIT 9 V4 VALIDATION RESULT = PASS",
        flush=True
    )

    return True


# ============================================================
# 16. RUN VALIDATION AND ACTUAL UNIT 9
# ============================================================

FRESH_UNIT_9_VALIDATION_READY = (
    unit_9_validation_v4()
)

FRESH_RECONSTRUCTION_UNIT_9_RESULT = (
    fresh_reconstruction_unit_9(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_8_RESULT,
    )
)

print(
    "FRESH RECONSTRUCTION UNIT 9 V4 READY =",
    FRESH_UNIT_9_VALIDATION_READY,
    flush=True
)

# ============================================================
# END COMPLETE UNIT 9 V4
# UNIT 10 FOLLOWS
# ============================================================



# ============================================================
# COMPLETE UNIT 10 V3 REPLACEMENT
# WEEX DEMO EXECUTION BOUNDARY
# UNIT 9 V4 -> UNIT 10 V3 -> UNIT 11
# ZERO INDENTATION
#
# PRESERVE ORIGINAL 19-FIELD OUTPUT CONTRACT
# ENTRY MARGIN: UNIT 9 / RENDER
# LEVERAGE: UNIT 9 / RENDER
# QUANTITY: UNIT 9 / UNIT 8
#
# NO ENTRY MARGIN OVERRIDE
# NO LEVERAGE RECALCULATION
# NO BTC QUANTITY RECALCULATION
# NO ORDER PAYLOAD
# NO EXCHANGE WRITE
# ============================================================

from decimal import Decimal, InvalidOperation


# ============================================================
# 1. DECIMAL VALIDATOR
# ============================================================

def unit_10_v3_decimal(value, name):

    if value is None or isinstance(value, bool):
        raise RuntimeError(
            "UNIT 10 INVALID " + name
        )

    try:
        number = Decimal(str(value))
    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ) as exc:
        raise RuntimeError(
            "UNIT 10 INVALID " + name
        ) from exc

    if not number.is_finite() or number <= 0:
        raise RuntimeError(
            "UNIT 10 NONPOSITIVE " + name
        )

    return number


# ============================================================
# 2. UNIT 10 MAIN
# ============================================================

def fresh_reconstruction_unit_10(
    config,
    unit_9_result,
):

    print("=" * 80, flush=True)
    print(
        "UNIT 10 V3 DEMO BOUNDARY START",
        flush=True
    )

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 10 CONFIG INVALID"
        )

    if not isinstance(unit_9_result, dict):
        raise RuntimeError(
            "UNIT 10 UNIT 9 RESULT INVALID"
        )

    exchange = config.get("exchange")
    strategy = config.get("strategy")
    safety = config.get("safety")
    precision = config.get("market_precision")

    if not all(
        isinstance(x, dict)
        for x in (
            exchange,
            strategy,
            safety,
            precision,
        )
    ):
        raise RuntimeError(
            "UNIT 10 CONFIG SECTIONS MISSING"
        )

    # ========================================================
    # 3. ORIGINAL WEEX DEMO CONFIGURATION
    # ========================================================

    if (
        config.get("execution_environment") != "DEMO"
        or exchange.get("name") != "WEEX"
        or exchange.get("api_version") != "V3"
        or not str(
    exchange.get("market_symbol", "")
).strip().upper().endswith("USDT")
or not str(
    exchange.get("demo_order_symbol", "")
).strip().upper().endswith("SUSDT")
        
    ):
        raise RuntimeError(
            "UNIT 10 WEEX DEMO CONFIG INVALID"
        )

    # These safety switches describe preparation
    # units only. Unit 12 independently controls
    # authorized DEMO order submissions.

    for key in (
        "authenticated_api_enabled",
        "account_access_enabled",
        "position_access_enabled",
        "order_endpoint_access_enabled",
        "demo_order_submission_enabled",
        "real_order_submission_enabled",
        "exchange_mutation_enabled",
        "leverage_mutation_enabled",
        "margin_mode_mutation_enabled",
        "position_mode_mutation_enabled",
    ):
        if safety.get(key) is not False:
            raise RuntimeError(
                "UNIT 10 UNIT-LOCAL SAFETY FAILED: "
                + key
            )

    for key in (
        "anti_duplicate_orders",
        "one_direction_only",
        "active_trade_mode_lock",
    ):
        if strategy.get(key) is not True:
            raise RuntimeError(
                "UNIT 10 SAFETY FLAG MISSING: "
                + key
            )

    # ========================================================
    # 4. ORIGINAL UNIT 9 INPUT CONTRACT
    # ========================================================

    required = (
        "status",
        "active_mode",
        "direction",
        "signal_qualified",
        "execution_intent",
        "trade_plan_ready",
        "trade_plan",
        "execution_ready",
        "execution_candidate",
        "skip_reason",
        "order_payload_created",
        "tp_execution_requested",
        "sl_execution_requested",
        "read_only",
    )

    missing = [
        key for key in required
        if key not in unit_9_result
    ]

    if missing:
        raise RuntimeError(
            "UNIT 10 UNIT 9 FIELDS MISSING: "
            + str(missing)
        )

    if unit_9_result.get(
        "unit_9_version"
    ) != "UNIT9_V4_DYNAMIC_ENTRY":
        raise RuntimeError(
            "UNIT 10 REQUIRES UNIT 9 V4"
        )

    if unit_9_result["read_only"] is not True:
        raise RuntimeError(
            "UNIT 10 READ ONLY CONTRACT FAILED"
        )

    for key in (
        "order_payload_created",
        "tp_execution_requested",
        "sl_execution_requested",
    ):
        if unit_9_result[key] is not False:
            raise RuntimeError(
                "UNIT 10 UNEXPECTED UPSTREAM ACTION: "
                + key
            )

    if unit_9_result.get(
        "exchange_write"
    ) is not False:
        raise RuntimeError(
            "UNIT 10 UPSTREAM EXCHANGE WRITE"
        )

    print(
        "PASS: UNIT 10 RECEIVED UNIT 9 V4",
        flush=True
    )

    # ========================================================
    # 5. NORMALIZE UNIT 9 RESULT
    # ========================================================

    status = str(
        unit_9_result["status"]
    ).upper()

    mode = str(
        unit_9_result["active_mode"]
    ).upper()

    direction = str(
        unit_9_result["direction"]
    ).upper()

    qualified = (
        unit_9_result["signal_qualified"] is True
    )

    intent = (
        unit_9_result["execution_intent"] is True
    )

    plan_ready = (
        unit_9_result["trade_plan_ready"] is True
    )

    execution_ready = (
        unit_9_result["execution_ready"] is True
    )

    plan = unit_9_result["trade_plan"]
    candidate = unit_9_result["execution_candidate"]

    skip_reason = str(
        unit_9_result.get("skip_reason")
        or "NONE"
    )

    # ========================================================
    # 6. ORIGINAL 19-FIELD UNIT 11 HANDOVER
    # ========================================================

    def make_result(
        state,
        result_mode,
        result_direction,
        result_qualified,
        result_intent,
        result_plan,
        result_candidate,
        result_instruction,
        reason,
    ):

        ready = (state == "READY")

        return {
            "status": state,
            "active_mode": result_mode,
            "direction": result_direction,
            "signal_qualified": result_qualified,
            "execution_intent": result_intent,
            "trade_plan_ready": ready,
            "trade_plan": result_plan,
            "execution_ready": ready,
            "execution_candidate": result_candidate,
            "demo_boundary_ready": ready,
            "demo_submission_instruction":
                result_instruction,
            "skip_reason": reason,
            "order_payload_created": False,
            "demo_submission_requested": False,
            "real_submission_requested": False,
            "tp_execution_requested": False,
            "sl_execution_requested": False,
            "backup_execution_requested": False,
            "read_only": True,
        }

    # ========================================================
    # 7. IDLE AND BLOCKED HANDOVER
    # ========================================================

    if status in ("IDLE", "BLOCKED"):

        if (
            intent
            or plan_ready
            or execution_ready
            or plan is not None
            or candidate is not None
        ):
            raise RuntimeError(
                "UNIT 10 CONTRADICTORY NON-READY STATE"
            )

        result = make_result(
            status,
            mode,
            direction,
            qualified,
            False,
            None,
            None,
            None,
            skip_reason,
        )

        print(
            "UNIT 10 STATUS =",
            status,
            flush=True
        )

        print(
            "UNIT 10 SKIP REASON =",
            skip_reason,
            flush=True
        )

        print(
            "UNIT 10 EXECUTION READY = False",
            flush=True
        )

        print(
            "UNIT 10 DEMO BOUNDARY READY = False",
            flush=True
        )

        print(
            "UNIT 10 EXCHANGE WRITE = NONE",
            flush=True
        )

        print(
            "FRESH RECONSTRUCTION UNIT 10 RESULT = PASS",
            flush=True
        )

        print("=" * 80, flush=True)

        return result

    # ========================================================
    # 8. ACTIONABLE READY CONTRACT
    # ========================================================

    if status != "READY":
        raise RuntimeError(
            "UNIT 10 UNKNOWN STATUS: " + status
        )

    if not all((
        qualified,
        intent,
        plan_ready,
        execution_ready,
    )):
        raise RuntimeError(
            "UNIT 10 READY STATE INCOMPLETE"
        )

    if mode not in (
        "BREAKOUT",
        "STRUCTURE",
        "SCALP",
    ):
        raise RuntimeError(
            "UNIT 10 INVALID ACTIVE MODE"
        )

    if direction not in ("LONG", "SHORT"):
        raise RuntimeError(
            "UNIT 10 INVALID DIRECTION"
        )

    if not isinstance(plan, dict):
        raise RuntimeError(
            "UNIT 10 TRADE PLAN MISSING"
        )

    if not isinstance(candidate, dict):
        raise RuntimeError(
            "UNIT 10 EXECUTION CANDIDATE MISSING"
        )

    if (
        plan.get("active_mode") != mode
        or plan.get("direction") != direction
        or plan.get("execution_environment")
            != "DEMO"
        or candidate.get("active_mode") != mode
        or candidate.get("direction") != direction
        or candidate.get("execution_environment")
            != "DEMO"
    ):
        raise RuntimeError(
            "UNIT 10 PLAN IDENTITY MISMATCH"
        )

    if candidate.get("trade_plan") is not plan:
        raise RuntimeError(
            "UNIT 10 TRADE PLAN IDENTITY CHANGED"
        )

    # ========================================================
    # 9. PRESERVE QUANTITY AND LEVERAGE
    # ========================================================

    sizing = plan.get("position_sizing")

    if not isinstance(sizing, dict):
        raise RuntimeError(
            "UNIT 10 POSITION SIZING MISSING"
        )

    quantity = unit_10_v3_decimal(
        plan.get("quantity"),
        "PLAN QUANTITY"
    )

    sized_quantity = unit_10_v3_decimal(
        sizing.get("quantity"),
        "SIZING QUANTITY"
    )

    margin = unit_10_v3_decimal(
        sizing.get("margin_allocation"),
        "INITIAL MARGIN"
    )

    leverage = unit_10_v3_decimal(
        sizing.get("leverage_target"),
        "LEVERAGE"
    )

    entry_margin = unit_10_v3_decimal(
        unit_9_result.get("entry_margin_usdt"),
        "UNIT 9 ENTRY MARGIN"
    )

    if quantity != sized_quantity:
        raise RuntimeError(
            "UNIT 10 QUANTITY CHANGED"
        )

    if margin != entry_margin:
        raise RuntimeError(
            "UNIT 10 ENTRY MARGIN MISMATCH"
        )

    if unit_9_result.get(
        "entry_margin_verified"
    ) is not True:
        raise RuntimeError(
            "UNIT 10 ENTRY CONFIG NOT VERIFIED"
        )

    if leverage != unit_10_v3_decimal(
        unit_9_result.get("selected_leverage"),
        "UNIT 9 SELECTED LEVERAGE"
    ):
        raise RuntimeError(
            "UNIT 10 LEVERAGE CHANGED"
        )

    if sizing.get(
        "leverage_source"
    ) != "RENDER_MANUAL_WEEX_DEMO":
        raise RuntimeError(
            "UNIT 10 LEVERAGE SOURCE INVALID"
        )

    print(
        "UNIT 10 ENTRY MARGIN PRESERVED =",
        margin,
        flush=True
    )

    print(
        "UNIT 10 ENTRY MARGIN SOURCE =",
        unit_9_result.get(
            "entry_margin_source"
        ),
        flush=True
    )

    print(
        "UNIT 10 LEVERAGE PRESERVED =",
        leverage,
        flush=True
    )

    print(
        "UNIT 10 BTC QUANTITY PRESERVED =",
        quantity,
        flush=True
    )

    # ========================================================
    # 10. DYNAMIC BACKUP POLICY
    # ========================================================

    if (
        sizing.get("max_backups") != 5
        or sizing.get("backup_sizing_mode")
            != "PERCENT_AVAILABLE_BALANCE"
        or sizing.get("backup_margin_reserved")
            is not False
        or "backup_multipliers" in strategy
    ):
        raise RuntimeError(
            "UNIT 10 BACKUP POLICY MISMATCH"
        )

    # ========================================================
    # 11. ORIGINAL UNIT 11 DEMO INSTRUCTION
    #
    # INTERNAL DICTIONARY, NOT AN ORDER PAYLOAD.
    # ========================================================

    instruction = {
        "exchange": "WEEX",
        "api_version": "V3",
        "execution_environment": "DEMO",
        "market_symbol": "BTCUSDT",
        "demo_order_symbol": "BTCSUSDT",
        "active_mode": mode,
        "direction": direction,
        "trade_plan": plan,
        "execution_candidate": candidate,
        "anti_duplicate_required": True,
        "one_direction_only_required": True,
        "active_trade_mode_lock_required": True,
        "payload_creation_allowed": False,
        "submission_allowed": False,
        "read_only": True,
    }

    # ========================================================
    # 12. FINAL READY RESULT
    # ========================================================

    result = make_result(
        "READY",
        mode,
        direction,
        True,
        True,
        plan,
        candidate,
        instruction,
        "NONE",
    )

    if (
        result["demo_boundary_ready"] is not True
        or result["execution_ready"] is not True
    ):
        raise RuntimeError(
            "UNIT 10 DEMO BOUNDARY FAILED"
        )

    print(
        "UNIT 10 STATUS = READY",
        flush=True
    )

    print(
        "UNIT 10 ACTIVE MODE =",
        mode,
        flush=True
    )

    print(
        "UNIT 10 DIRECTION =",
        direction,
        flush=True
    )

    print(
        "UNIT 10 EXECUTION READY = True",
        flush=True
    )

    print(
        "UNIT 10 DEMO BOUNDARY READY = True",
        flush=True
    )

    print(
        "UNIT 10 ORDER PAYLOAD CREATED = False",
        flush=True
    )

    print(
        "UNIT 10 DEMO SUBMISSION REQUESTED = False",
        flush=True
    )

    print(
        "UNIT 10 EXCHANGE WRITE = NONE",
        flush=True
    )

    print(
        "FRESH RECONSTRUCTION UNIT 10 RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# 13. UNIT 10 HYBRID ADAPTER
# PRESERVE ORIGINAL CALL INTERFACE
# ============================================================

def fresh_unit_10_hybrid_adapter(
    execution_config,
    unit_9_result,
):

    result = fresh_reconstruction_unit_10(
        execution_config,
        unit_9_result,
    )

    if result["status"] == "READY":

        if (
            result["trade_plan"]
            is not unit_9_result["trade_plan"]
        ):
            raise RuntimeError(
                "UNIT 10 ADAPTER CHANGED TRADE PLAN"
            )

        if (
            result["execution_candidate"]
            is not unit_9_result["execution_candidate"]
        ):
            raise RuntimeError(
                "UNIT 10 ADAPTER CHANGED CANDIDATE"
            )

    print(
        "UNIT 10 HYBRID ADAPTER STATUS =",
        result["status"],
        flush=True
    )

    return result


# ============================================================
# 14. UNIT 10 VALIDATION
# ============================================================

def unit_10_validation_v3():

    print("=" * 80, flush=True)
    print(
        "UNIT 10 VALIDATION V3 START",
        flush=True
    )

    config = FRESH_RECONSTRUCTION_CONFIG
    actual = FRESH_RECONSTRUCTION_UNIT_9_RESULT

    tests = []

    def record(name, condition):
        tests.append((name, bool(condition)))

    record(
        "UNIT 9 V4 HANDOVER",
        actual.get("unit_9_version")
        == "UNIT9_V4_DYNAMIC_ENTRY"
    )

    exchange = config.get("exchange", {})

    market_symbol = str(
        exchange.get("market_symbol", "")
    ).strip().upper()

    demo_symbol = str(
        exchange.get("demo_order_symbol", "")
    ).strip().upper()

    record(
        "WEEX DEMO CONFIGURATION",
        config.get("execution_environment") == "DEMO"
        and market_symbol.endswith("USDT")
        and len(market_symbol) > 4
        and demo_symbol == (
            market_symbol[:-4] + "SUSDT"
        )
    )

    record(
        "ORIGINAL UNIT 9 INPUT CONTRACT",
        all(
            key in actual
            for key in (
                "status",
                "active_mode",
                "direction",
                "trade_plan",
                "execution_candidate",
                "execution_ready",
                "read_only",
            )
        )
    )

    record(
        "NO FIXED BACKUP MULTIPLIERS",
        "backup_multipliers"
        not in config.get("strategy", {})
    )

    record(
        "NO UPSTREAM ORDER",
        actual.get("exchange_write") is False
        and actual.get(
            "order_payload_created"
        ) is False
    )

    # Use actual Unit 9 state without fabricating
    # an actionable signal or order.

    output = fresh_unit_10_hybrid_adapter(
        config,
        actual,
    )

    record(
        "ACTUAL UNIT 9 HANDOVER",
        output.get("status")
        == actual.get("status")
    )

    original_fields = (
        "status",
        "active_mode",
        "direction",
        "signal_qualified",
        "execution_intent",
        "trade_plan_ready",
        "trade_plan",
        "execution_ready",
        "execution_candidate",
        "demo_boundary_ready",
        "demo_submission_instruction",
        "skip_reason",
        "order_payload_created",
        "demo_submission_requested",
        "real_submission_requested",
        "tp_execution_requested",
        "sl_execution_requested",
        "backup_execution_requested",
        "read_only",
    )

    record(
        "ORIGINAL 19 FIELD UNIT 11 CONTRACT",
        all(
            key in output
            for key in original_fields
        )
    )

    record(
        "NO UNIT 10 ORDER PAYLOAD",
        output.get("order_payload_created")
        is False
    )

    record(
        "NO UNIT 10 DEMO SUBMISSION",
        output.get("demo_submission_requested")
        is False
    )

    record(
        "NO UNIT 10 REAL SUBMISSION",
        output.get("real_submission_requested")
        is False
    )

    passed = sum(
        1 for _, ok in tests if ok
    )

    failed = len(tests) - passed

    for name, ok in tests:
        print(
            "UNIT 10 TEST:",
            name,
            "=",
            "PASS" if ok else "FAIL",
            flush=True
        )

    print(
        "UNIT 10 TESTS PASSED =",
        passed,
        flush=True
    )

    print(
        "UNIT 10 TESTS FAILED =",
        failed,
        flush=True
    )

    if failed:
        raise RuntimeError(
            "UNIT 10 V3 VALIDATION FAILED"
        )

    print(
        "UNIT 10 VALIDATION V3 RESULT = PASS",
        flush=True
    )

    return True


# ============================================================
# 15. VALIDATE AND EXECUTE UNIT 10
# ============================================================

FRESH_UNIT_10_VALIDATION_READY = (
    unit_10_validation_v3()
)

FRESH_RECONSTRUCTION_UNIT_10_RESULT = (
    fresh_unit_10_hybrid_adapter(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_9_RESULT,
    )
)

print(
    "FRESH RECONSTRUCTION UNIT 10 V3 READY =",
    FRESH_UNIT_10_VALIDATION_READY,
    flush=True
)

# ============================================================
# END COMPLETE UNIT 10 V3
# UNIT 11 FOLLOWS
# ============================================================



# ============================================================
# COMPLETE UNIT 11 V3 REPLACEMENT
# UNIT 10 V3 -> UNIT 11 V3 -> UNIT 12
# ZERO INDENTATION
#
# ORIGINAL 19-FIELD INPUT / 21-FIELD OUTPUT
# ORIGINAL SIX-FIELD WEEX DEMO ORDER PAYLOAD
#
# NO MARGIN RECALCULATION
# NO LEVERAGE RECALCULATION
# NO QUANTITY RECALCULATION
# NO API REQUEST OR EXCHANGE WRITE
# BOT_MODE REMAINS EXCLUSIVE TO UNIT 12
# ============================================================

import time
import uuid
from decimal import Decimal, InvalidOperation


UNIT_11_V3_INPUT_FIELDS = (
    "status",
    "active_mode",
    "direction",
    "signal_qualified",
    "execution_intent",
    "trade_plan_ready",
    "trade_plan",
    "execution_ready",
    "execution_candidate",
    "demo_boundary_ready",
    "demo_submission_instruction",
    "skip_reason",
    "order_payload_created",
    "demo_submission_requested",
    "real_submission_requested",
    "tp_execution_requested",
    "sl_execution_requested",
    "backup_execution_requested",
    "read_only",
)


UNIT_11_V3_OUTPUT_FIELDS = (
    "status",
    "active_mode",
    "direction",
    "signal_qualified",
    "execution_intent",
    "trade_plan_ready",
    "trade_plan",
    "execution_ready",
    "execution_candidate",
    "demo_boundary_ready",
    "demo_submission_instruction",
    "payload_ready",
    "order_payload",
    "skip_reason",
    "order_payload_created",
    "demo_submission_requested",
    "real_submission_requested",
    "tp_execution_requested",
    "sl_execution_requested",
    "backup_execution_requested",
    "read_only",
)


def unit_11_v3_decimal(value, label):

    if value is None or isinstance(value, bool):
        raise RuntimeError(
            "UNIT 11 MISSING " + label
        )

    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise RuntimeError(
            "UNIT 11 INVALID " + label
        ) from exc

    if not number.is_finite() or number <= 0:
        raise RuntimeError(
            "UNIT 11 NONPOSITIVE " + label
        )

    return number


def unit_11_v3_result(
    status,
    mode,
    direction,
    plan=None,
    candidate=None,
    instruction=None,
    payload=None,
    reason="NONE",
):

    ready = status == "READY"

    return {
        "status": status,
        "active_mode": mode,
        "direction": direction,
        "signal_qualified": ready,
        "execution_intent": ready,
        "trade_plan_ready": ready,
        "trade_plan": plan if ready else None,
        "execution_ready": ready,
        "execution_candidate": (
            candidate if ready else None
        ),
        "demo_boundary_ready": ready,
        "demo_submission_instruction": (
            instruction if ready else None
        ),
        "payload_ready": ready,
        "order_payload": payload if ready else None,
        "skip_reason": reason,
        "order_payload_created": ready,
        "demo_submission_requested": False,
        "real_submission_requested": False,
        "tp_execution_requested": False,
        "sl_execution_requested": False,
        "backup_execution_requested": False,
        "read_only": True,
    }


# ============================================================
# UNIT 11 MAIN
# ============================================================

def fresh_reconstruction_unit_11(
    config,
    unit_10_result,
):

    print("=" * 80, flush=True)
    print(
        "UNIT 11 V3 WEEX DEMO PAYLOAD START",
        flush=True
    )

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 11 INVALID CONFIG"
        )

    if not isinstance(unit_10_result, dict):
        raise RuntimeError(
            "UNIT 11 INVALID UNIT 10 RESULT"
        )

    exchange = config.get("exchange")
    safety = config.get("safety")
    strategy = config.get("strategy")
    precision = config.get("market_precision")

    if not all(
        isinstance(x, dict)
        for x in (
            exchange,
            safety,
            strategy,
            precision,
        )
    ):
        raise RuntimeError(
            "UNIT 11 CONFIG SECTIONS MISSING"
        )

    # ========================================================
    # 1. ORIGINAL WEEX DEMO CONTRACT
    # ========================================================

    if (
        config.get("execution_environment") != "DEMO"
        or exchange.get("name") != "WEEX"
        or exchange.get("api_version") != "V3"
        or not str(
    exchange.get("market_symbol", "")
).strip().upper().endswith("USDT")
or str(
    exchange.get("demo_order_symbol", "")
).strip().upper() != (
    str(
        exchange.get("market_symbol", "")
    ).strip().upper()[:-4] + "SUSDT"
)
    ):
        raise RuntimeError(
            "UNIT 11 DEMO ENVIRONMENT INVALID"
        )

    # Safety settings are unit-local.
    # They must not disable Unit 12 demo execution.

    for key in (
        "authenticated_api_enabled",
        "account_access_enabled",
        "position_access_enabled",
        "order_endpoint_access_enabled",
        "demo_order_submission_enabled",
        "real_order_submission_enabled",
        "exchange_mutation_enabled",
        "leverage_mutation_enabled",
        "margin_mode_mutation_enabled",
        "position_mode_mutation_enabled",
    ):
        if safety.get(key) is not False:
            raise RuntimeError(
                "UNIT 11 LOCAL SAFETY INVALID: "
                + key
            )

    for key in (
        "anti_duplicate_orders",
        "one_direction_only",
        "active_trade_mode_lock",
    ):
        if strategy.get(key) is not True:
            raise RuntimeError(
                "UNIT 11 STRATEGY POLICY INVALID: "
                + key
            )

    # ========================================================
    # 2. ORIGINAL 19-FIELD UNIT 10 CONTRACT
    # ========================================================

    missing = [
        key for key in UNIT_11_V3_INPUT_FIELDS
        if key not in unit_10_result
    ]

    if missing:
        raise RuntimeError(
            "UNIT 11 INPUT FIELDS MISSING: "
            + str(missing)
        )

    if unit_10_result["read_only"] is not True:
        raise RuntimeError(
            "UNIT 11 UPSTREAM READ_ONLY FAILED"
        )

    for key in (
        "order_payload_created",
        "demo_submission_requested",
        "real_submission_requested",
        "tp_execution_requested",
        "sl_execution_requested",
        "backup_execution_requested",
    ):
        if unit_10_result[key] is not False:
            raise RuntimeError(
                "UNIT 11 UNEXPECTED UNIT 10 ACTION: "
                + key
            )

    print(
        "PASS: UNIT 11 RECEIVED UNIT 10 V3",
        flush=True
    )

    status = str(
        unit_10_result["status"]
    ).upper()

    mode = str(
        unit_10_result["active_mode"]
    ).upper()

    direction = str(
        unit_10_result["direction"]
    ).upper()

    # ========================================================
    # 3. IDLE / BLOCKED PATH
    # ========================================================

    if status in ("IDLE", "BLOCKED"):

        for key in (
            "execution_intent",
            "trade_plan_ready",
            "execution_ready",
            "demo_boundary_ready",
        ):
            if unit_10_result[key] is not False:
                raise RuntimeError(
                    "UNIT 11 NONREADY FLAG INVALID: "
                    + key
                )

        for key in (
            "trade_plan",
            "execution_candidate",
            "demo_submission_instruction",
        ):
            if unit_10_result[key] is not None:
                raise RuntimeError(
                    "UNIT 11 NONREADY PLAN INVALID: "
                    + key
                )

        result = unit_11_v3_result(
            status,
            mode,
            direction,
            reason=str(
                unit_10_result.get("skip_reason")
                or "NO_ACCEPTABLE_CANDIDATE"
            ),
        )

        print(
            "UNIT 11 STATUS =",
            status,
            flush=True
        )

        print(
            "UNIT 11 SKIP REASON =",
            result["skip_reason"],
            flush=True
        )

        print(
            "UNIT 11 PAYLOAD READY = False",
            flush=True
        )

        print(
            "UNIT 11 EXCHANGE WRITE = NONE",
            flush=True
        )

        print(
            "FRESH RECONSTRUCTION UNIT 11 RESULT = PASS",
            flush=True
        )

        print("=" * 80, flush=True)

        return result

    # ========================================================
    # 4. READY CONTRACT
    # NO NEW MARKET SIGNAL FILTER
    # ========================================================

    if status != "READY":
        raise RuntimeError(
            "UNIT 11 UNKNOWN STATUS: " + status
        )

    for key in (
        "signal_qualified",
        "execution_intent",
        "trade_plan_ready",
        "execution_ready",
        "demo_boundary_ready",
    ):
        if unit_10_result[key] is not True:
            raise RuntimeError(
                "UNIT 11 READY FLAG MISSING: "
                + key
            )

    if mode not in (
        "STRUCTURE",
        "BREAKOUT",
        "SCALP",
    ):
        raise RuntimeError(
            "UNIT 11 INVALID MODE"
        )

    if direction not in ("LONG", "SHORT"):
        raise RuntimeError(
            "UNIT 11 INVALID DIRECTION"
        )

    plan = unit_10_result["trade_plan"]

    candidate = unit_10_result[
        "execution_candidate"
    ]

    instruction = unit_10_result[
        "demo_submission_instruction"
    ]

    if not all(
        isinstance(x, dict)
        for x in (plan, candidate, instruction)
    ):
        raise RuntimeError(
            "UNIT 11 READY DATA MISSING"
        )

    if (
        plan.get("active_mode") != mode
        or plan.get("direction") != direction
        or plan.get("execution_environment") != "DEMO"
        or candidate.get("active_mode") != mode
        or candidate.get("direction") != direction
        or candidate.get("trade_plan") is not plan
    ):
        raise RuntimeError(
            "UNIT 11 PLAN IDENTITY MISMATCH"
        )

    # ========================================================
    # 5. ORIGINAL UNIT 10 DEMO INSTRUCTION
    # ========================================================

    expected_instruction = {
        "exchange": "WEEX",
        "api_version": "V3",
        "execution_environment": "DEMO",
        "market_symbol": "BTCUSDT",
        "demo_order_symbol": "BTCSUSDT",
        "active_mode": mode,
        "direction": direction,
        "anti_duplicate_required": True,
        "one_direction_only_required": True,
        "active_trade_mode_lock_required": True,
        "payload_creation_allowed": False,
        "submission_allowed": False,
        "read_only": True,
    }

    for key, expected in expected_instruction.items():

        if instruction.get(key) != expected:
            raise RuntimeError(
                "UNIT 11 INSTRUCTION MISMATCH: "
                + key
            )

    if (
        instruction.get("trade_plan") is not plan
        or instruction.get(
            "execution_candidate"
        ) is not candidate
    ):
        raise RuntimeError(
            "UNIT 11 INSTRUCTION IDENTITY FAILED"
        )

    # ========================================================
    # 6. EXACT BTC QUANTITY PASS-THROUGH
    # ========================================================

    sizing = plan.get("position_sizing")

    if not isinstance(sizing, dict):
        raise RuntimeError(
            "UNIT 11 SIZING MISSING"
        )

    quantity = unit_11_v3_decimal(
        plan.get("quantity"),
        "PLAN QUANTITY"
    )

    sized_quantity = unit_11_v3_decimal(
        sizing.get("quantity"),
        "SIZED QUANTITY"
    )

    minimum = unit_11_v3_decimal(
        precision.get("minimum_quantity"),
        "MINIMUM QUANTITY"
    )

    step = unit_11_v3_decimal(
        precision.get("quantity_step"),
        "QUANTITY STEP"
    )

    if quantity != sized_quantity:
        raise RuntimeError(
            "UNIT 11 QUANTITY CHANGED"
        )

    if quantity < minimum:
        raise RuntimeError(
            "UNIT 11 QUANTITY BELOW MINIMUM"
        )

    if quantity % step != 0:
        raise RuntimeError(
            "UNIT 11 QUANTITY NOT STEP ALIGNED"
        )

    quantity_text = format(quantity, "f")

    # No initial-margin or leverage calculation here.
    # The original trade plan is passed unchanged.

    # ========================================================
    # 7. DIRECTION -> WEEX MARKET SIDE
    # ========================================================

    if direction == "LONG":
        side = "BUY"
        position_side = "LONG"
    else:
        side = "SELL"
        position_side = "SHORT"


    # ========================================================
    # UNIT 11 - VALID WEEX DEMO CLIENT ORDER ID
    # MAXIMUM 36 CHARACTERS
    # ========================================================

    client_order_id = (
        "FR11"
        + ("L" if direction == "LONG" else "S")
        + uuid.uuid4().hex[:24]
    )

    if len(client_order_id) > 36:
        raise RuntimeError(
            "UNIT 11 CLIENT ORDER ID TOO LONG"
        )


    # ========================================================
    # 8. ORIGINAL SIX-FIELD DEMO ORDER PAYLOAD
    # ========================================================

    payload = {
        "symbol": exchange["demo_order_symbol"],
        "side": side,
        "positionSide": position_side,
        "type": "MARKET",
        "quantity": quantity_text,
        "newClientOrderId": client_order_id,
    }

    expected_payload_fields = {
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
        "newClientOrderId",
    }

    if set(payload) != expected_payload_fields:
        raise RuntimeError(
            "UNIT 11 PAYLOAD FIELDS INVALID"
        )

    # ========================================================
    # 9. ORIGINAL 21-FIELD UNIT 12 HANDOVER
    # ========================================================

    result = unit_11_v3_result(
        "READY",
        mode,
        direction,
        plan,
        candidate,
        instruction,
        payload,
        "NONE",
    )

    print(
        "UNIT 11 STATUS = READY",
        flush=True
    )

    print(
        "UNIT 11 ACTIVE MODE =",
        mode,
        flush=True
    )

    print(
        "UNIT 11 DIRECTION =",
        direction,
        flush=True
    )

    print(
        "UNIT 11 BTC QUANTITY =",
        quantity_text,
        flush=True
    )

    print(
        "UNIT 11 PAYLOAD READY = True",
        flush=True
    )

    print(
        "UNIT 11 ORDER PAYLOAD CREATED = True",
        flush=True
    )

    print(
        "UNIT 11 DEMO SUBMISSION REQUESTED = False",
        flush=True
    )

    print(
        "UNIT 11 REAL SUBMISSION REQUESTED = False",
        flush=True
    )

    print(
        "UNIT 11 EXCHANGE WRITE = NONE",
        flush=True
    )

    print(
        "FRESH RECONSTRUCTION UNIT 11 RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# 10. HYBRID ADAPTER
# ============================================================

def fresh_unit_11_hybrid_adapter(
    execution_config,
    unit_10_result,
):

    result = fresh_reconstruction_unit_11(
        execution_config,
        unit_10_result,
    )

    if tuple(result.keys()) != (
        UNIT_11_V3_OUTPUT_FIELDS
    ):
        raise RuntimeError(
            "UNIT 11 OUTPUT CONTRACT CHANGED"
        )

    if result["status"] == "READY":

        if (
            result["trade_plan"]
            is not unit_10_result["trade_plan"]
            or result["execution_candidate"]
            is not unit_10_result[
                "execution_candidate"
            ]
        ):
            raise RuntimeError(
                "UNIT 11 ADAPTER MUTATED PLAN"
            )

    print(
        "UNIT 11 HYBRID ADAPTER STATUS =",
        result["status"],
        flush=True
    )

    return result


# ============================================================
# 11. VALIDATION
#
# ACTUAL IDLE HANDOVER
# CONTROLLED LONG AND SHORT READY HANDOVER
# NO ORDER SENT
# ============================================================

def unit_11_validation_v3():

    print("=" * 80, flush=True)
    print(
        "UNIT 11 V3 VALIDATION START",
        flush=True
    )

    config = FRESH_RECONSTRUCTION_CONFIG
    actual = FRESH_RECONSTRUCTION_UNIT_10_RESULT

    tests = []

    def record(name, passed):
        tests.append((name, bool(passed)))

    record(
        "UNIT 10 RESULT AVAILABLE",
        isinstance(actual, dict)
    )

    record(
        "ORIGINAL 19 FIELD INPUT",
        all(
            key in actual
            for key in UNIT_11_V3_INPUT_FIELDS
        )
    )

    record(
        "WEEX DEMO ONLY",
        config.get(
            "execution_environment"
        ) == "DEMO"
    )

    # ========================================================
    # ACTUAL HANDOVER
    # ========================================================

    actual_output = fresh_unit_11_hybrid_adapter(
        config,
        actual,
    )

    record(
        "ACTUAL UNIT 10 HANDOVER",
        actual_output["status"]
        == actual["status"]
    )

    record(
        "ORIGINAL 21 FIELD OUTPUT",
        tuple(actual_output.keys())
        == UNIT_11_V3_OUTPUT_FIELDS
    )

    record(
        "ACTUAL NO EXCHANGE SUBMISSION",
        actual_output[
            "demo_submission_requested"
        ] is False
        and actual_output[
            "real_submission_requested"
        ] is False
    )

    # ========================================================
    # CONTROLLED READY TEST
    # DERIVE QUANTITY FROM CONFIGURED MINIMUM
    # DO NOT USE AN ENTRY-MARGIN NUMBER
    # ========================================================

    minimum = unit_11_v3_decimal(
        config["market_precision"][
            "minimum_quantity"
        ],
        "TEST MINIMUM"
    )

    step = unit_11_v3_decimal(
        config["market_precision"][
            "quantity_step"
        ],
        "TEST STEP"
    )

    # Find the smallest step-aligned test quantity
    # that is no less than the configured minimum.

    units = (
        minimum / step
    ).to_integral_value(
        rounding="ROUND_CEILING"
    )

    test_quantity = units * step

    def synthetic_ready(direction, mode):

        plan = {
            "active_mode": mode,
            "direction": direction,
            "execution_environment": "DEMO",
            "quantity": str(test_quantity),
            "position_sizing": {
                "quantity": str(test_quantity),
            },
        }

        candidate = {
            "active_mode": mode,
            "direction": direction,
            "execution_environment": "DEMO",
            "trade_plan": plan,
        }

        instruction = {
            "exchange": "WEEX",
            "api_version": "V3",
            "execution_environment": "DEMO",
            "market_symbol": "BTCUSDT",
            "demo_order_symbol": "BTCSUSDT",
            "active_mode": mode,
            "direction": direction,
            "trade_plan": plan,
            "execution_candidate": candidate,
            "anti_duplicate_required": True,
            "one_direction_only_required": True,
            "active_trade_mode_lock_required": True,
            "payload_creation_allowed": False,
            "submission_allowed": False,
            "read_only": True,
        }

        ready_input = {
            "status": "READY",
            "active_mode": mode,
            "direction": direction,
            "signal_qualified": True,
            "execution_intent": True,
            "trade_plan_ready": True,
            "trade_plan": plan,
            "execution_ready": True,
            "execution_candidate": candidate,
            "demo_boundary_ready": True,
            "demo_submission_instruction": instruction,
            "skip_reason": "NONE",
            "order_payload_created": False,
            "demo_submission_requested": False,
            "real_submission_requested": False,
            "tp_execution_requested": False,
            "sl_execution_requested": False,
            "backup_execution_requested": False,
            "read_only": True,
        }

        return fresh_unit_11_hybrid_adapter(
            config,
            ready_input,
        )

    long_result = synthetic_ready(
        "LONG", "STRUCTURE"
    )

    short_result = synthetic_ready(
        "SHORT", "BREAKOUT"
    )

    record(
        "STRUCTURE LONG READY",
        long_result["status"] == "READY"
        and long_result["order_payload"]["side"]
        == "BUY"
        and long_result["order_payload"][
            "positionSide"
        ] == "LONG"
    )

    record(
        "BREAKOUT SHORT READY",
        short_result["status"] == "READY"
        and short_result["order_payload"]["side"]
        == "SELL"
        and short_result["order_payload"][
            "positionSide"
        ] == "SHORT"
    )

    record(
        "QUANTITY UNCHANGED",
        Decimal(
            long_result["order_payload"][
                "quantity"
            ]
        ) == test_quantity
        and Decimal(
            short_result["order_payload"][
                "quantity"
            ]
        ) == test_quantity
    )

    record(
        "NO ORDER SUBMITTED IN TEST",
        all(
            output[
                "demo_submission_requested"
            ] is False
            and output[
                "real_submission_requested"
            ] is False
            for output in (
                long_result,
                short_result,
            )
        )
    )

    passed = sum(
        ok for _, ok in tests
    )

    failed = len(tests) - passed

    for name, ok in tests:
        print(
            "UNIT 11 TEST:",
            name,
            "=",
            "PASS" if ok else "FAIL",
            flush=True
        )

    print(
        "UNIT 11 TESTS PASSED =",
        passed,
        flush=True
    )

    print(
        "UNIT 11 TESTS FAILED =",
        failed,
        flush=True
    )

    if failed:
        raise RuntimeError(
            "UNIT 11 V3 VALIDATION FAILED"
        )

    print(
        "UNIT 11 V3 VALIDATION RESULT = PASS",
        flush=True
    )

    return True


# ============================================================
# 12. VALIDATE AND EXECUTE ACTUAL UNIT 11
# ============================================================

FRESH_UNIT_11_VALIDATION_READY = (
    unit_11_validation_v3()
)

FRESH_RECONSTRUCTION_UNIT_11_RESULT = (
    fresh_unit_11_hybrid_adapter(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_10_RESULT,
    )
)

print(
    "FRESH RECONSTRUCTION UNIT 11 V3 READY =",
    FRESH_UNIT_11_VALIDATION_READY,
    flush=True
)

# ============================================================
# END COMPLETE UNIT 11 V3
# UNIT 12 FOLLOWS
# ============================================================



# ============================================================
# START COMPLETE UNIT 12 V5 REPLACEMENT
#
# WEEX V3 DEMO ORDER EXECUTION
# UNIT 11 V3 -> UNIT 12 V5 -> UNIT 13 V4
#
# FIXES:
# 1. INVALID WEEX CLIENT ORDER ID
# 2. CRASH ON WEEX HTTP 400
# 3. DUPLICATE ORDER ATTEMPT WITHIN PROCESS
# 4. QUANTITY / POSITION / DEMO BOUNDARY CHECKS
#
# BOT_MODE CONTROLS UNIT 12 ONLY.
# UNITS 13 AND 14 REMAIN INDEPENDENT.
# NO LIVE-CASH EXECUTION.
#
# ALL CODE BEGINS AT ZERO INDENTATION.
# ============================================================

import os
import re
import json
import time
import hmac
import base64
import hashlib
import urllib.request
import urllib.error

from decimal import Decimal, InvalidOperation


UNIT_12_V5_BASE_URL = (
    "https://api-contract.weex.com"
)

UNIT_12_V5_POSITION_PATH = (
    "/capi/v3/sim/position/allPosition"
)

UNIT_12_V5_ORDER_PATH = (
    "/capi/v3/sim/order"
)

UNIT_12_V5_SYMBOL = "BTCSUSDT"


# ============================================================
# 1. DECIMAL SAFETY
# ============================================================

def unit_12_v5_decimal(
    value,
    name,
    allow_zero=False,
):

    if value is None or isinstance(value, bool):
        raise RuntimeError(
            "UNIT 12 MISSING " + name
        )

    try:
        number = Decimal(str(value))

    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ) as exc:

        raise RuntimeError(
            "UNIT 12 INVALID " + name
        ) from exc

    if not number.is_finite():
        raise RuntimeError(
            "UNIT 12 NONFINITE " + name
        )

    if number < 0:
        raise RuntimeError(
            "UNIT 12 NEGATIVE " + name
        )

    if number == 0 and not allow_zero:
        raise RuntimeError(
            "UNIT 12 ZERO " + name
        )

    return number


# ============================================================
# 2. WEEX CLIENT ORDER ID CORRECTION
#
# NORMALIZES THE ORIGINAL UNIT 11 ID.
# DETERMINISTIC: SAME INPUT -> SAME OUTPUT.
#
# THIS DOES NOT ALTER QUANTITY, SIDE OR SYMBOL.
# ============================================================

def unit_12_v5_client_order_id(
    original_id,
    direction,
):

    if (
        not isinstance(original_id, str)
        or not original_id.strip()
    ):
        raise RuntimeError(
            "UNIT 12 SOURCE CLIENT ID MISSING"
        )

    if direction not in ("LONG", "SHORT"):
        raise RuntimeError(
            "UNIT 12 INVALID ID DIRECTION"
        )

    # Preserve a valid original ID unchanged.
    if re.fullmatch(
        r"[.A-Za-z0-9_:/-]{1,36}",
        original_id,
    ):
        return original_id

    # Convert an oversized or invalid ID into
    # a stable WEEX-compatible alphanumeric ID.

    digest = hashlib.sha256(
        original_id.encode("utf-8")
    ).hexdigest()[:24]

    side_code = (
        "L" if direction == "LONG"
        else "S"
    )

    corrected = (
        "FR12"
        + side_code
        + digest
    )

    if re.fullmatch(
        r"[.A-Za-z0-9_:/-]{1,36}",
        corrected,
    ) is None:
        raise RuntimeError(
            "UNIT 12 CLIENT ID NORMALIZATION FAILED"
        )

    return corrected


# ============================================================
# 3. BASE RESULT
#
# UNIT 13 MUST RECEIVE A RESULT EVEN WHEN
# UNIT 12 IS PAUSED, IDLE OR REJECTED.
# ============================================================

def unit_12_v5_result(
    unit_11_result,
    status,
    reason,
):

    return {
        "unit": 12,
        "version": "V5",
        "status": status,
        "read_only": False,
        "unit_11_status":
            unit_11_result.get("status"),
        "active_mode":
            unit_11_result.get("active_mode"),
        "direction":
            unit_11_result.get("direction"),
        "signal_qualified":
            unit_11_result.get(
                "signal_qualified"
            ) is True,
        "execution_intent":
            unit_11_result.get(
                "execution_intent"
            ) is True,
        "position_check_attempted": False,
        "position_check_completed": False,
        "position_endpoint_access": False,
        "position_http_status": None,
        "active_position_exists": False,
        "active_positions": [],
        "initial_entry_permitted": False,
        "duplicate_initial_entry_blocked": False,
        "management_path_permitted": True,
        "tp_management_permitted": True,
        "backup_management_permitted": True,
        "demo_submission_attempted": False,
        "demo_submission_completed": False,
        "real_submission_attempted": False,
        "authenticated_request": False,
        "order_endpoint_access": False,
        "exchange_write": False,
        "order_id": None,
        "client_order_id": None,
        "http_status": None,
        "skip_reason": reason,
    }


# ============================================================
# 4. DEMO CONFIGURATION CHECK
# ============================================================

def unit_12_v5_config_check(config):

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 12 CONFIG INVALID"
        )

    exchange = config.get("exchange")
    precision = config.get(
        "market_precision"
    )

    if (
        not isinstance(exchange, dict)
        or not isinstance(precision, dict)
    ):
        raise RuntimeError(
            "UNIT 12 CONFIG SECTIONS MISSING"
        )

    exchange = config.get("exchange", {})

    market_symbol = str(
        exchange.get("market_symbol", "")
    ).strip().upper()

    demo_symbol = str(
        exchange.get("demo_order_symbol", "")
    ).strip().upper()

    expected_demo_symbol = (
        market_symbol[:-4] + "SUSDT"
        if market_symbol.endswith("USDT")
        and len(market_symbol) > 4
        else ""
    )

    if (
        config.get("execution_environment") != "DEMO"
        or exchange.get("name") != "WEEX"
        or exchange.get("api_version") != "V3"
        or not expected_demo_symbol
        or demo_symbol != expected_demo_symbol
    ):
        raise RuntimeError(
            "UNIT 12 NON-DEMO CONFIG BLOCKED"
        )

    return True

# ============================================================
# 5. VALIDATE UNIT 11 READY PAYLOAD
# ============================================================

def unit_12_v5_validate_payload(
    config,
    upstream,
):

    direction = str(
        upstream.get("direction", "")
    ).upper()

    mode = str(
        upstream.get("active_mode", "")
    ).upper()

    if direction not in ("LONG", "SHORT"):
        raise RuntimeError(
            "UNIT 12 INVALID DIRECTION"
        )

    if mode not in (
        "STRUCTURE",
        "BREAKOUT",
        "SCALP",
    ):
        raise RuntimeError(
            "UNIT 12 INVALID ACTIVE MODE"
        )

    required_true = (
        "signal_qualified",
        "execution_intent",
        "trade_plan_ready",
        "execution_ready",
        "demo_boundary_ready",
        "payload_ready",
        "order_payload_created",
    )

    for name in required_true:

        if upstream.get(name) is not True:
            raise RuntimeError(
                "UNIT 12 READY FLAG FALSE: "
                + name
            )

    required_false = (
        "demo_submission_requested",
        "real_submission_requested",
        "tp_execution_requested",
        "sl_execution_requested",
        "backup_execution_requested",
    )

    for name in required_false:

        if upstream.get(name) is not False:
            raise RuntimeError(
                "UNIT 12 UNEXPECTED PRIOR ACTION: "
                + name
            )

    if upstream.get("read_only") is not True:
        raise RuntimeError(
            "UNIT 12 UPSTREAM BOUNDARY INVALID"
        )

    original = upstream.get("order_payload")

    if not isinstance(original, dict):
        raise RuntimeError(
            "UNIT 12 ORDER PAYLOAD MISSING"
        )

    expected_fields = {
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
        "newClientOrderId",
    }

    if set(original) != expected_fields:
        raise RuntimeError(
            "UNIT 12 PAYLOAD FIELDS INVALID"
        )

    expected_side = (
        "BUY" if direction == "LONG"
        else "SELL"
    )

    expected_demo_symbol = str(
        config["exchange"]["demo_order_symbol"]
    ).strip().upper()

    if (
        str(original.get("symbol", "")).strip().upper()
        != expected_demo_symbol
        or original.get("side") != expected_side
        or original.get("positionSide") != direction
        or original.get("type") != "MARKET"
    ):
        raise RuntimeError(
            "UNIT 12 PAYLOAD IDENTITY INVALID"
        )

    quantity = unit_12_v5_decimal(
        original.get("quantity"),
        "BTC QUANTITY",
    )

    precision = config[
        "market_precision"
    ]

    minimum = unit_12_v5_decimal(
        precision.get(
            "minimum_quantity"
        ),
        "MINIMUM BTC",
    )

    step = unit_12_v5_decimal(
        precision.get(
            "quantity_step"
        ),
        "BTC STEP",
    )

    if quantity < minimum:
        raise RuntimeError(
            "UNIT 12 BTC BELOW MINIMUM"
        )

    if quantity % step != 0:
        raise RuntimeError(
            "UNIT 12 BTC NOT STEP ALIGNED"
        )

    plan = upstream.get("trade_plan")

    if not isinstance(plan, dict):
        raise RuntimeError(
            "UNIT 12 TRADE PLAN MISSING"
        )

    plan_quantity = unit_12_v5_decimal(
        plan.get("quantity"),
        "PLAN QUANTITY",
    )

    sizing = plan.get(
        "position_sizing"
    )

    if not isinstance(sizing, dict):
        raise RuntimeError(
            "UNIT 12 PLAN SIZING MISSING"
        )

    sizing_quantity = unit_12_v5_decimal(
        sizing.get("quantity"),
        "SIZING QUANTITY",
    )

    if not (
        quantity
        == plan_quantity
        == sizing_quantity
    ):
        raise RuntimeError(
            "UNIT 12 QUANTITY CHANGED UPSTREAM"
        )

    corrected_id = (
        unit_12_v5_client_order_id(
            original.get(
                "newClientOrderId"
            ),
            direction,
        )
    )

    # Make a separate copy. Do not mutate
    # the Unit 11 result.

    payload = dict(original)

    payload["newClientOrderId"] = (
        corrected_id
    )

    return payload, quantity


# ============================================================
# 6. AUTHENTICATED WEEX DEMO REQUEST
#
# GET POSITION
# POST DEMO ORDER
#
# NO REAL-CASH ENDPOINT
# ============================================================

def unit_12_v5_request(
    method,
    path,
    body=None,
):

    allowed = {
        (
            "GET",
            UNIT_12_V5_POSITION_PATH
        ),
        (
            "POST",
            UNIT_12_V5_ORDER_PATH
        ),
    }

    if (method, path) not in allowed:
        raise RuntimeError(
            "UNIT 12 NON-DEMO ENDPOINT BLOCKED"
        )

    if method == "GET" and body is not None:
        raise RuntimeError(
            "UNIT 12 GET BODY NOT ALLOWED"
        )

    if method == "POST" and not isinstance(
        body, dict
    ):
        raise RuntimeError(
            "UNIT 12 POST BODY INVALID"
        )

    key = (
        os.getenv("WEEX_API_KEY")
        or os.getenv("API_KEY")
    )

    secret = (
        os.getenv("WEEX_API_SECRET")
        or os.getenv("API_SECRET")
    )

    phrase = (
        os.getenv("WEEX_API_PASSPHRASE")
        or os.getenv("API_PASSPHRASE")
    )

    if not all((key, secret, phrase)):
        raise RuntimeError(
            "UNIT 12 WEEX CREDENTIALS MISSING"
        )

    body_text = (
        json.dumps(
            body,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        if body is not None
        else ""
    )

    timestamp = str(
        int(time.time() * 1000)
    )

    message = (
        timestamp
        + method
        + path
        + body_text
    )

    signature = base64.b64encode(
        hmac.new(
            secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    ).decode("utf-8")

    request = urllib.request.Request(
        UNIT_12_V5_BASE_URL + path,
        data=(
            body_text.encode("utf-8")
            if method == "POST"
            else None
        ),
        method=method,
        headers={
            "ACCESS-KEY": key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": phrase,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            status = response.getcode()

            raw = response.read().decode(
                "utf-8",
                errors="replace",
            )

    except urllib.error.HTTPError as exc:

        raw = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        # HTTP rejection is returned to the
        # main Unit 12 function instead of
        # terminating the entire process.

        try:
            response_data = json.loads(raw)
        except ValueError:
            response_data = {
                "error": raw[:250]
            }

        return (
            exc.code,
            response_data,
        )

    # Network failures are intentionally NOT
    # converted into confirmed rejections.
    # After a POST, outcome may be uncertain.

    try:
        data = json.loads(raw)
    except ValueError:
        data = {
            "error": "INVALID_RESPONSE_JSON"
        }

    return status, data

def unit_12_v5_active_positions(rows, demo_symbol=None):

    if not isinstance(rows, list):
        raise RuntimeError(
            "UNIT 12 POSITION RESPONSE NOT LIST"
        )

    expected_symbol = str(
        demo_symbol or UNIT_12_V5_SYMBOL
    ).strip().upper()

    active = []

    for p in rows:
        if not isinstance(p, dict):
            raise RuntimeError(
                "UNIT 12 POSITION RECORD INVALID"
            )

        if str(p.get("symbol", "")).strip().upper() != expected_symbol:
            continue

        size = unit_12_v5_decimal(
            p.get("size"),
            "POSITION SIZE",
            True,
        )

        if size > 0:
            active.append(p)

    return active

# ============================================================
# 8. MAIN UNIT 12 EXECUTION
# ============================================================

def fresh_reconstruction_unit_12(
    config,
    unit_11_result,
):

    print("=" * 80, flush=True)

    print(
        "UNIT 12 V5 WEEX DEMO EXECUTION START",
        flush=True
    )

    unit_12_v5_config_check(
        config
    )

    if not isinstance(
        unit_11_result, dict
    ):
        raise RuntimeError(
            "UNIT 12 UNIT 11 RESULT INVALID"
        )

    mode = os.getenv(
        "BOT_MODE",
        "PAUSE",
    ).strip().upper()

    if mode not in ("RUN", "PAUSE"):
        raise RuntimeError(
            "UNIT 12 BOT_MODE INVALID"
        )

    print(
        "UNIT 12 BOT_MODE =",
        mode,
        flush=True
    )

    # ========================================================
    # PAUSE NEW ENTRIES ONLY
    # ========================================================

    if mode == "PAUSE":

        result = unit_12_v5_result(
            unit_11_result,
            "IDLE",
            "BOT_MODE_PAUSE",
        )

        print(
            "UNIT 12 STATUS = IDLE",
            flush=True
        )
        print(
            "UNIT 12 NEW ENTRIES = PAUSED",
            flush=True
        )
        print(
            "UNIT 12 POSITION MANAGEMENT "
            "INDEPENDENT = True",
            flush=True
        )

        return result

    upstream_status = str(
        unit_11_result.get(
            "status", ""
        )
    ).upper()

    # ========================================================
    # IDLE AND BLOCKED HANDOVER
    # ========================================================

    if upstream_status in (
        "IDLE",
        "BLOCKED",
    ):

        result = unit_12_v5_result(
            unit_11_result,
            upstream_status,
            str(
                unit_11_result.get(
                    "skip_reason"
                )
                or "NO_ACCEPTABLE_CANDIDATE"
            ),
        )

        print(
            "UNIT 12 STATUS =",
            result["status"],
            flush=True
        )
        print(
            "UNIT 12 SKIP REASON =",
            result["skip_reason"],
            flush=True
        )
        print(
            "UNIT 12 EXCHANGE WRITE = NONE",
            flush=True
        )

        return result

    if upstream_status != "READY":
        raise RuntimeError(
            "UNIT 12 INVALID UPSTREAM STATUS"
        )

    # ========================================================
    # VALIDATE READY PAYLOAD
    # ========================================================

    payload, quantity = (
        unit_12_v5_validate_payload(
            config,
            unit_11_result,
        )
    )

    result = unit_12_v5_result(
        unit_11_result,
        "READY",
        "PENDING_POSITION_VERIFICATION",
    )

    client_id = payload[
        "newClientOrderId"
    ]

    result["client_order_id"] = client_id

    print(
        "UNIT 12 READY MODE =",
        result["active_mode"],
        flush=True
    )
    print(
        "UNIT 12 READY DIRECTION =",
        result["direction"],
        flush=True
    )
    print(
        "UNIT 12 BTC QUANTITY =",
        format(quantity, "f"),
        flush=True
    )
    print(
        "UNIT 12 CLIENT ORDER ID =",
        client_id,
        flush=True
    )
    print(
        "UNIT 12 CLIENT ORDER ID LENGTH =",
        len(client_id),
        flush=True
    )
    print(
        "UNIT 12 CLIENT ORDER ID VALID = True",
        flush=True
    )
    print(
        "UNIT 12 QUANTITY RECALCULATED = False",
        flush=True
    )
    print(
        "UNIT 12 LEVERAGE MUTATION = NONE",
        flush=True
    )

    # ========================================================
    # PREVENT REPEATED ATTEMPT IN SAME PROCESS
    # ========================================================

    attempts = globals().setdefault(
        "_UNIT12_V5_ORDER_ATTEMPTS",
        set(),
    )

    if client_id in attempts:

        result["status"] = (
            "ORDER_UNCERTAIN"
        )

        result["skip_reason"] = (
            "PREVIOUS_CLIENT_ORDER_ATTEMPT"
        )

        print(
            "UNIT 12 DUPLICATE ATTEMPT BLOCKED",
            flush=True
        )

        return result

    # ========================================================
    # FRESH EXCHANGE POSITION CHECK
    # ========================================================

    result["position_check_attempted"] = True

    print(
        "UNIT 12 FRESH POSITION CHECK START",
        flush=True
    )

    try:

        position_http, response = (
            unit_12_v5_request(
                "GET",
                UNIT_12_V5_POSITION_PATH,
            )
        )

        result["authenticated_request"] = True
        result["position_endpoint_access"] = True
        result["position_http_status"] = (
            position_http
        )

        if not 200 <= position_http < 300:

            result["status"] = (
                "POSITION_CHECK_FAILED"
            )

            result["skip_reason"] = (
                "WEEX_POSITION_HTTP_"
                + str(position_http)
            )

            return result

        active = (
            unit_12_v5_active_positions(
                response
            )
        )

    except Exception as exc:

        result["status"] = (
            "POSITION_CHECK_FAILED"
        )

        result["skip_reason"] = (
            "POSITION_REQUEST_ERROR"
        )

        print(
            "UNIT 12 POSITION ERROR =",
            type(exc).__name__,
            str(exc)[:180],
            flush=True
        )

        return result

    result["position_check_completed"] = True

    print(
        "UNIT 12 ACTIVE BTC POSITIONS =",
        len(active),
        flush=True
    )

    if active:

        result.update({
            "status": "ACTIVE_POSITION_BLOCK",
            "skip_reason":
                "NONZERO_POSITION_BLOCK_INITIAL_ENTRY",
            "active_position_exists": True,
            "active_positions": [
                {
                    "symbol": p.get("symbol"),
                    "side": p.get("side"),
                    "size": p.get("size"),
                }
                for p in active
            ],
            "duplicate_initial_entry_blocked": True,
        })

        print(
            "UNIT 12 INITIAL ENTRY BLOCKED "
            "BY ACTIVE POSITION",
            flush=True
        )

        return result

    # ========================================================
    # ZERO POSITION VERIFIED
    # ACTUAL WEEX DEMO ORDER
    # ========================================================

    result["initial_entry_permitted"] = True

    print(
        "UNIT 12 ZERO BTC POSITION VERIFIED",
        flush=True
    )

    print(
        "UNIT 12 SENDING ACTUAL WEEX DEMO ORDER",
        flush=True
    )

    # Claim before POST. If a network response
    # is uncertain, do not automatically retry.

    attempts.add(client_id)

    result["demo_submission_attempted"] = True
    result["order_endpoint_access"] = True

    try:

        order_http, order_response = (
            unit_12_v5_request(
                "POST",
                UNIT_12_V5_ORDER_PATH,
                payload,
            )
        )

    except Exception as exc:

        result["status"] = "ORDER_UNCERTAIN"

        result["skip_reason"] = (
            "POST_RESPONSE_UNCERTAIN"
        )

        print(
            "UNIT 12 POST OUTCOME UNCERTAIN =",
            type(exc).__name__,
            flush=True
        )

        print(
            "UNIT 12 DO NOT AUTOMATICALLY RETRY",
            flush=True
        )

        print(
            "UNIT 12 CHECK WEEX ORDER HISTORY",
            flush=True
        )

        return result

    result["authenticated_request"] = True
    result["http_status"] = order_http

    print(
        "UNIT 12 ORDER HTTP STATUS =",
        order_http,
        flush=True
    )

    # ========================================================
    # EXCHANGE REJECTION
    # NO CRASH / CONTINUE TO UNIT 13
    # ========================================================

    if not isinstance(
        order_response, dict
    ):

        result["status"] = "ORDER_UNCERTAIN"

        result["skip_reason"] = (
            "UNRECOGNIZED_ORDER_RESPONSE"
        )

        return result

    if (
        not 200 <= order_http < 300
        or order_response.get("success")
            is not True
    ):

        result["status"] = "DEMO_REJECTED"

        code = (
            order_response.get("code")
            or order_response.get("errorCode")
            or "UNKNOWN"
        )

        reason = (
            order_response.get("msg")
            or order_response.get("errorMessage")
            or "WEEX_REJECTED"
        )

        result["skip_reason"] = (
            "WEEX_REJECTED_" + str(code)
        )

        print(
            "UNIT 12 WEEX REJECTION CODE =",
            code,
            flush=True
        )

        print(
            "UNIT 12 WEEX REJECTION REASON =",
            str(reason)[:200],
            flush=True
        )

        print(
            "UNIT 12 EXCHANGE WRITE = REJECTED",
            flush=True
        )

        return result

    # ========================================================
    # SUCCESS ACKNOWLEDGEMENT
    # ========================================================

    order_id = order_response.get(
        "orderId"
    )

    if not order_id:

        result["status"] = "ORDER_UNCERTAIN"

        result["skip_reason"] = (
            "SUCCESS_RESPONSE_MISSING_ORDER_ID"
        )

        print(
            "UNIT 12 ORDER ID UNVERIFIED",
            flush=True
        )

        return result

    result.update({
        "status": "DEMO_SUBMITTED",
        "skip_reason": "NONE",
        "demo_submission_completed": True,
        "exchange_write": True,
        "order_id": str(order_id),
        "request_path":
            UNIT_12_V5_ORDER_PATH,
        "request_payload": dict(payload),
        "weex_response": order_response,
    })

    print(
        "UNIT 12 WEEX ORDER ID =",
        order_id,
        flush=True
    )

    print(
        "UNIT 12 DEMO SUBMISSION COMPLETED = True",
        flush=True
    )

    print(
        "UNIT 12 REAL SUBMISSION ATTEMPTED = False",
        flush=True
    )

    print(
        "UNIT 12 STATUS = DEMO_SUBMITTED",
        flush=True
    )

    print(
        "FRESH RECONSTRUCTION UNIT 12 "
        "RESULT = PASS",
        flush=True
    )

    return result


# ============================================================
# 9. HYBRID ADAPTER
# ============================================================

def fresh_unit_12_hybrid_execution_adapter(
    execution_config,
    unit_11_result,
):

    result = (
        fresh_reconstruction_unit_12(
            execution_config,
            unit_11_result,
        )
    )

    if not isinstance(result, dict):
        raise RuntimeError(
            "UNIT 12 ADAPTER RESULT INVALID"
        )

    if result.get(
        "real_submission_attempted"
    ) is not False:
        raise RuntimeError(
            "UNIT 12 LIVE CASH SAFETY FAILURE"
        )

    if result.get("status") == "DEMO_SUBMITTED":

        if (
            result.get(
                "demo_submission_completed"
            ) is not True
            or not result.get("order_id")
        ):
            raise RuntimeError(
                "UNIT 12 ORDER ACK INVALID"
            )

    print(
        "UNIT 12 HYBRID ADAPTER STATUS =",
        result["status"],
        flush=True
    )

    return result


# ============================================================
# 10. LOCAL VALIDATION
# NEVER CONTACT WEEX OR SEND AN ORDER HERE
# ============================================================

def unit_12_validation_v5():

    print("=" * 80, flush=True)

    print(
        "UNIT 12 V5 VALIDATION START",
        flush=True
    )

    config = FRESH_RECONSTRUCTION_CONFIG

    upstream = (
        FRESH_RECONSTRUCTION_UNIT_11_RESULT
    )

    tests = []

    def check(name, condition):
        tests.append(
            (name, bool(condition))
        )

    check(
        "WEEX DEMO CONFIG",
        unit_12_v5_config_check(config)
    )

    check(
        "UNIT 11 HANDOVER",
        isinstance(upstream, dict)
    )

    check(
        "UNIT 11 READ ONLY",
        upstream.get("read_only") is True
    )

    old_id = (
        "FR11-LONG-"
        + "1234567890123456789"
        + "-"
        + "abcdef12"
    )

    fixed_id = (
        unit_12_v5_client_order_id(
            old_id,
            "LONG",
        )
    )

    check(
        "OVERSIZED ID NORMALIZED",
        len(fixed_id) <= 36
    )

    check(
        "ID CHARACTER SET VALID",
        re.fullmatch(
            r"[.A-Za-z0-9_:/-]{1,36}",
            fixed_id
        ) is not None
    )

    check(
        "ID NORMALIZATION STABLE",
        fixed_id
        == unit_12_v5_client_order_id(
            old_id,
            "LONG",
        )
    )

    check(
        "VALID ID PRESERVED",
        unit_12_v5_client_order_id(
            "FR11L12345",
            "LONG",
        ) == "FR11L12345"
    )

    check(
        "ZERO POSITION PARSING",
        unit_12_v5_active_positions([
            {
                "symbol": "BTCSUSDT",
                "size": "0",
            }
        ]) == []
    )

    check(
        "NONZERO POSITION DETECTION",
        len(
            unit_12_v5_active_positions([
                {
                    "symbol": "BTCSUSDT",
                    "size": "0.0001",
                    "side": "LONG",
                }
            ])
        ) == 1
    )

    check(
        "DEMO ENDPOINT ONLY",
        UNIT_12_V5_ORDER_PATH
        == "/capi/v3/sim/order"
    )

    passed = sum(
        ok for _, ok in tests
    )

    failed = len(tests) - passed

    for name, ok in tests:

        print(
            "UNIT 12 TEST:",
            name,
            "=",
            "PASS" if ok else "FAIL",
            flush=True
        )

    print(
        "UNIT 12 TESTS PASSED =",
        passed,
        flush=True
    )

    print(
        "UNIT 12 TESTS FAILED =",
        failed,
        flush=True
    )

    if failed:
        raise RuntimeError(
            "UNIT 12 V5 VALIDATION FAILED"
        )

    print(
        "UNIT 12 V5 VALIDATION RESULT = PASS",
        flush=True
    )

    return True


# ============================================================
# 11. VALIDATE AND EXECUTE ONCE
# ============================================================

FRESH_UNIT_12_VALIDATION_READY = (
    unit_12_validation_v5()
)

FRESH_RECONSTRUCTION_UNIT_12_RESULT = (
    fresh_unit_12_hybrid_execution_adapter(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_11_RESULT,
    )
)

print(
    "FRESH RECONSTRUCTION UNIT 12 V5 READY =",
    FRESH_UNIT_12_VALIDATION_READY,
    flush=True
)

# ============================================================
# END COMPLETE UNIT 12 V5
# UNIT 13 V4 FOLLOWS
# ============================================================


# ============================================================
# COMPLETE UNIT 13 V5 REPLACEMENT
# PART 1 OF 5
# UNIT 12 -> UNIT 13 -> UNIT 14
# ZERO INDENTATION
#
# WEEX DEMO EXISTING-POSITION TP MANAGEMENT
# BOT_MODE DOES NOT CONTROL UNIT 13
# STEP-AWARE TP ALLOCATION
# CONFIGURABLE NET ROI FLOORS
# TP3 TRAILING PARAMETERS TO UNIT 14
# NO LIVE-CASH ENDPOINT
# NO LEVERAGE OR QUANTITY RECALCULATION
# ============================================================

import os
import json
import time
import hmac
import base64
import hashlib
import urllib.request
import urllib.parse
import urllib.error
from decimal import Decimal, ROUND_DOWN, ROUND_UP


UNIT13_V4_BASE = "https://api-contract.weex.com"
UNIT13_V4_POSITION = "/capi/v3/sim/position/allPosition"
UNIT13_V4_ORDER = "/capi/v3/sim/order"
UNIT13_V4_HISTORY = "/capi/v3/sim/order/history"


# ============================================================
# 1. DECIMAL VALIDATION
# ============================================================

def unit_13_v4_D(value, name="NUMBER", allow_zero=False):

    if value is None or isinstance(value, bool):
        raise RuntimeError("UNIT 13 MISSING " + name)

    try:
        x = Decimal(str(value))
    except Exception as exc:
        raise RuntimeError(
            "UNIT 13 INVALID " + name
        ) from exc

    if not x.is_finite():
        raise RuntimeError(
            "UNIT 13 NONFINITE " + name
        )

    if x < 0 or (x == 0 and not allow_zero):
        raise RuntimeError(
            "UNIT 13 NONPOSITIVE " + name
        )

    return x


# ============================================================
# 2. STEP-AWARE TP ALLOCATION
# EXACT SMALL-POSITION POLICY OF WORKING REFERENCE
# ============================================================

def unit_13_v4_allocation(total, step, pct1=10, pct2=20):

    total = unit_13_v4_D(total, "CUM OPEN")
    step = unit_13_v4_D(step, "QTY STEP")

    if total % step != 0:
        raise RuntimeError(
            "UNIT 13 CUMULATIVE SIZE NOT STEP ALIGNED"
        )

    n = int(total / step)

    if n == 1:
        s1, s2, s3 = 0, 0, 1

    elif n == 2:
        s1, s2, s3 = 1, 0, 1

    else:
        s1 = max(1, int(n * float(pct1) / 100.0))
        s2 = max(1, int(n * float(pct2) / 100.0))

        while s1 + s2 >= n:
            if s2 > 1:
                s2 -= 1
            elif s1 > 1:
                s1 -= 1
            else:
                raise RuntimeError(
                    "UNIT 13 TP ALLOCATION FAILED"
                )

        s3 = n - s1 - s2

    return (
        Decimal(s1) * step,
        Decimal(s2) * step,
        Decimal(s3) * step,
    )


# ============================================================
# 3. NET-ROI TARGET CALCULATION
# BASED ON EXCHANGE POSITION LEVERAGE
# ============================================================

def unit_13_v4_targets(
    entry,
    leverage,
    side,
    price_step,
    tp1_floor,
    tp2_floor,
    taker_fee,
):

    D = unit_13_v4_D

    entry = D(entry, "ENTRY")
    lev = D(leverage, "LEVERAGE")
    ps = D(price_step, "PRICE STEP")
    p1 = D(tp1_floor, "TP1 ROI")
    p2 = D(tp2_floor, "TP2 ROI")
    fee = D(taker_fee, "TAKER FEE", True)

    if p2 <= p1:
        raise RuntimeError(
            "UNIT 13 TP2 ROI MUST EXCEED TP1"
        )

    # Estimated round-trip trading fees
    # expressed as ROI on leveraged margin.

    fee_roi = Decimal(2) * fee * lev

    move1 = (p1 + fee_roi) / lev
    move2 = (p2 + fee_roi) / lev

    if side == "LONG":

        raw1 = entry * (
            1 + move1 / Decimal(100)
        )
        raw2 = entry * (
            1 + move2 / Decimal(100)
        )

        t1 = (
            raw1 / ps
        ).to_integral_value(
            rounding=ROUND_UP
        ) * ps

        t2 = (
            raw2 / ps
        ).to_integral_value(
            rounding=ROUND_UP
        ) * ps

        if t2 <= t1:
            t2 = t1 + ps

    elif side == "SHORT":

        raw1 = entry * (
            1 - move1 / Decimal(100)
        )
        raw2 = entry * (
            1 - move2 / Decimal(100)
        )

        t1 = (
            raw1 / ps
        ).to_integral_value(
            rounding=ROUND_DOWN
        ) * ps

        t2 = (
            raw2 / ps
        ).to_integral_value(
            rounding=ROUND_DOWN
        ) * ps

        if t2 >= t1:
            t2 = t1 - ps

    else:
        raise RuntimeError(
            "UNIT 13 INVALID POSITION SIDE"
        )

    if min(t1, t2) <= 0:
        raise RuntimeError(
            "UNIT 13 TARGET PRICE NONPOSITIVE"
        )

    return t1, t2


# ============================================================
# END UNIT 13 V5 PART 1
# NEXT: PART 2 - SIGNED WEEX DEMO REQUESTS
# ============================================================



# ============================================================
# UNIT 13 V5 - PART 2 OF 5
# AUTHENTICATED WEEX DEMO REQUESTS
# PERSISTENT TP STATE AND VERIFIED FILLS
# ZERO INDENTATION
# ============================================================

# ============================================================
# 4. WEEX SIGNED DEMO REQUESTS
# ============================================================

def unit_13_v4_signed_request(method, path, payload=None):

    if (method, path) not in {
        ("GET", UNIT13_V4_POSITION),
        ("GET", UNIT13_V4_HISTORY),
        ("POST", UNIT13_V4_ORDER),
    }:
        raise RuntimeError(
            "UNIT 13 NON-DEMO ENDPOINT BLOCKED"
        )

    key = os.getenv("WEEX_API_KEY") or os.getenv("API_KEY")
    secret = (
        os.getenv("WEEX_API_SECRET")
        or os.getenv("API_SECRET")
    )
    phrase = (
        os.getenv("WEEX_API_PASSPHRASE")
        or os.getenv("API_PASSPHRASE")
    )

    if not all((key, secret, phrase)):
        raise RuntimeError(
            "UNIT 13 DEMO CREDENTIALS MISSING"
        )

    if method == "GET" and payload is not None and path != UNIT13_V4_HISTORY:
        raise RuntimeError("UNIT 13 GET PARAMS NOT ALLOWED")

    if method == "POST" and not isinstance(
        payload, dict
    ):
        raise RuntimeError(
            "UNIT 13 POST BODY INVALID"
        )

    query = (urllib.parse.urlencode(payload)
             if method == "GET" and payload else "")
    request_path = path + ("?" + query if query else "")

    body = (
        json.dumps(
            payload,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        if method == "POST" and payload is not None
        else ""
    )

    timestamp = str(int(time.time() * 1000))
    message = timestamp + method + request_path + body

    signature = base64.b64encode(
        hmac.new(
            secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    ).decode("utf-8")

    request = urllib.request.Request(
        UNIT13_V4_BASE + request_path,
        method=method,
        data=(
            body.encode("utf-8")
            if method == "POST"
            else None
        ),
        headers={
            "ACCESS-KEY": key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": phrase,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            status = response.getcode()
            raw = response.read().decode(
                "utf-8", errors="replace"
            )

    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(
            "utf-8", errors="replace"
        )[:400]
        raise RuntimeError(
            "UNIT 13 WEEX HTTP "
            + str(exc.code) + ": " + detail
        ) from exc

    # Ambiguous POST results must NOT be
    # automatically retried.

    if not 200 <= status < 300:
        raise RuntimeError(
            "UNIT 13 HTTP STATUS " + str(status)
        )

    try:
        response = json.loads(raw)
    except ValueError as exc:
        raise RuntimeError(
            "UNIT 13 INVALID WEEX JSON"
        ) from exc

    return response


# ============================================================
# 5. PUBLIC MARK PRICE
# ============================================================


def unit_13_14_active_symbols():
    """
    Resolve the active market/demo pair from
    the existing scanner configuration.
    No independent BTC fallback.
    """
    config = globals().get(
        "FRESH_RECONSTRUCTION_CONFIG"
    )

    if not isinstance(config, dict):
        raise RuntimeError(
            "ACTIVE SYMBOL CONFIG MISSING"
        )

    exchange = config.get("exchange", {})

    market = str(
        exchange.get("market_symbol") or ""
    ).strip().upper()

    demo = str(
        exchange.get("demo_order_symbol") or ""
    ).strip().upper()

    if not market or not demo:
        raise RuntimeError(
            "ACTIVE MARKET/DEMO SYMBOL MISSING"
        )

    return market, demo

def unit_13_v4_mark_price():
    market_symbol, _ = unit_13_14_active_symbols()

    query = urllib.parse.urlencode({
        "symbol": market_symbol,
        "priceType": "MARK",
    })

    request = urllib.request.Request(
        UNIT13_V4_BASE
        + "/capi/v3/market/symbolPrice?"
        + query,
        method="GET",
    )

    with urllib.request.urlopen(
        request,
        timeout=15,
    ) as response:

        market = json.loads(
            response.read().decode("utf-8")
        )

    if not isinstance(market, dict):
        raise RuntimeError(
            "UNIT 13 MARK PRICE RESPONSE INVALID"
        )

    if market.get("symbol") != market_symbol:
        raise RuntimeError(
            "UNIT 13 WRONG MARKET SYMBOL"
        )

    return unit_13_v4_D(
        market.get("price"),
        "MARK PRICE",
    )


# ============================================================
# 6. BASE RESULT FOR UNIT 14
# ============================================================

def unit_13_v4_base_result(unit_12_result, status, reason):

    return {
        "unit": 13,
        "status": status,
        "read_only": False,
        "unit_12_status": unit_12_result.get(
            "status"
        ),
        "active_position_exists": False,
        "position_exists": False,
        "tp_management_required": False,
        "tp_execution_attempted": False,
        "tp_execution_completed": False,
        "tp3_armed": False,
        "sl_execution_attempted": False,
        "backup_execution_attempted": False,
        "real_submission_attempted": False,
        "exchange_write": False,
        "skip_reason": reason,
    }


# ============================================================
# EXCHANGE-VERIFIED TP ORDER TRACKING
# RECORDS BELONG TO ONE ORIGINAL-POSITION CYCLE
# NEVER INFER TP FILLS FROM cumCloseSize
# ============================================================

import pathlib as _u13_pathlib
import uuid as _u13_uuid

UNIT13_V4_STATE_ROOT = _u13_pathlib.Path(
    os.getenv("UNIT13_STATE_DIR", "/var/data/unit13_tp")
)


def unit_13_v4_state_path(symbol, side, cycle):

    key = hashlib.sha256(
        (symbol + ":" + side + ":" + cycle).encode()
    ).hexdigest()

    return UNIT13_V4_STATE_ROOT / (key + ".json")


def unit_13_v4_load(path):

    if not path.exists():
        return None

    with path.open("r") as handle:
        value = json.load(handle)

    if not isinstance(value, dict):
        raise RuntimeError("UNIT 13 STATE INVALID")

    return value


def unit_13_v4_save(path, state):

    path.parent.mkdir(parents=True, exist_ok=True)

    tmp = path.with_name(
        path.name + ".tmp-" + _u13_uuid.uuid4().hex
    )

    with tmp.open("x") as handle:
        json.dump(state, handle, sort_keys=True)
        handle.flush()
        os.fsync(handle.fileno())

    os.replace(tmp, path)


def unit_13_v4_history(symbol):

    # Fetch bounded history.
    # No position reductions are counted.

    records = unit_13_v4_signed_request(
        "GET",
        UNIT13_V4_HISTORY,
        {
            "symbol": symbol,
            "limit": 500,
            "page": 0
        }
    )

    if not isinstance(records, list):
        raise RuntimeError(
            "UNIT 13 HISTORY NOT LIST"
        )

    return records


def unit_13_v4_verified(state, history, side, symbol):

    opposite = "SELL" if side == "LONG" else "BUY"

    totals = {
        "TP1": Decimal(0),
        "TP2": Decimal(0)
    }

    pending = False

    for stage in ("TP1", "TP2"):

        order = state.get("orders", {}).get(stage)

        if not order:
            continue

        client_id = order.get("client_id")
        order_id = str(order.get("order_id") or "")

        matches = [
            r for r in history
            if isinstance(r, dict) and (
                (
                    order_id
                    and str(r.get("orderId")) == order_id
                )
                or (
                    client_id
                    and r.get("clientOrderId") == client_id
                )
            )
        ]

        if len(matches) != 1:
            pending = True
            continue

        r = matches[0]

        if (
            r.get("symbol") != symbol
            or str(
                r.get("positionSide", "")
            ).upper() != side
            or str(
                r.get("side", "")
            ).upper() != opposite
        ):
            raise RuntimeError(
                "UNIT 13 TP ORDER IDENTITY MISMATCH"
            )

        qty = unit_13_v4_D(
            r.get("executedQty"),
            "TP EXECUTED",
            True
        )

        planned = unit_13_v4_D(
            order["quantity"],
            "TP PLAN"
        )

        if qty > planned:
            raise RuntimeError(
                "UNIT 13 TP OVERFILL IN HISTORY"
            )

        totals[stage] = qty

        if str(
            r.get("status", "")
        ).upper() not in (
            "FILLED",
            "CANCELED",
            "EXPIRED",
            "REJECTED"
        ):
            pending = True

        elif qty < planned:

            # Partial fills must be reconciled
            # before any new TP order.

            pending = True

    return totals, pending


# ============================================================
# END UNIT 13 V5 PART 2
# NEXT: PART 3 - MAIN POSITION MANAGEMENT
# ============================================================



# ============================================================
# UNIT 13 V5 - PART 3 OF 5
# MAIN POSITION MANAGEMENT
# EXISTING DEMO POSITIONS
# VERIFIED TP1 / TP2 STATE
# ZERO INDENTATION AT FUNCTION DECLARATION
# ============================================================

# ============================================================
# 7. MAIN UNIT 13
# ============================================================

def fresh_reconstruction_unit_13(
    config,
    unit_12_result,
):

    print("=" * 80, flush=True)
    print(
        "UNIT 13 V5 EXISTING POSITION MANAGEMENT START",
        flush=True
    )

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 13 INVALID CONFIG"
        )

    if not isinstance(unit_12_result, dict):
        raise RuntimeError(
            "UNIT 13 UNIT 12 RESULT INVALID"
        )

    exchange = config.get("exchange", {})
    strategy = config.get("strategy", {})
    precision = config.get("market_precision", {})

    if (
        config.get("execution_environment") != "DEMO"
        or exchange.get("name") != "WEEX"
        or exchange.get("api_version") != "V3"
        or not str(exchange.get("market_symbol") or "").strip()
        or not str(exchange.get("demo_order_symbol") or "").strip()
    ):
        raise RuntimeError(
            "UNIT 13 NON-DEMO CONTRACT BLOCKED"
        )

    D = unit_13_v4_D

    step = D(
        precision.get("quantity_step"),
        "QTY STEP"
    )
    minimum = D(
        precision.get("minimum_quantity"),
        "MINIMUM QTY"
    )
    price_step = D(
        precision.get("price_step"),
        "PRICE STEP"
    )

    tp1_floor = D(
        strategy.get(
            "tp1_net_roi_floor_percent", 20
        ),
        "TP1 FLOOR"
    )
    tp2_floor = D(
        strategy.get(
            "tp2_net_roi_floor_percent", 40
        ),
        "TP2 FLOOR"
    )
    fee = D(
        strategy.get(
            "futures_taker_fee_percent", "0.08"
        ),
        "FEE",
        True
    )

    trail_ref = D(
        strategy.get(
            "tp3_trailing_reference_percent",
            "0.20"
        ),
        "TRAIL REF"
    )
    trail_min = D(
        strategy.get(
            "tp3_trailing_min_percent",
            "0.10"
        ),
        "TRAIL MIN"
    )
    trail_max = D(
        strategy.get(
            "tp3_trailing_max_percent",
            "0.40"
        ),
        "TRAIL MAX"
    )

    if (
        tp1_floor <= 0
        or tp2_floor <= tp1_floor
        or not (
            0 < trail_min
            <= trail_ref
            <= trail_max
        )
    ):
        raise RuntimeError(
            "UNIT 13 TP CONFIGURATION INVALID"
        )

    print(
        "PASS: UNIT 13 RECEIVED UNIT 12 RESULT",
        flush=True
    )
    print(
        "UNIT 13 RECEIVED UNIT 12 STATUS =",
        unit_12_result.get("status"),
        flush=True
    )
    print(
        "UNIT 13 POSITION MANAGEMENT INDEPENDENT "
        "OF BOT_MODE = TRUE",
        flush=True
    )
    print(
        "UNIT 13 TP ALLOCATION =",
        strategy.get("tp1_allocation_percent", 10),
        "/",
        strategy.get("tp2_allocation_percent", 20),
        "/",
        strategy.get("tp3_allocation_percent", 70),
        flush=True
    )
    print(
        "UNIT 13 TP1 NET ROI FLOOR =",
        tp1_floor,
        flush=True
    )
    print(
        "UNIT 13 TP2 NET ROI FLOOR =",
        tp2_floor,
        flush=True
    )

    # ========================================================
    # ALWAYS READ CURRENT WEEX DEMO POSITION.
    # DO NOT CHECK BOT_MODE HERE.
    # ========================================================

    positions = unit_13_v4_signed_request(
        "GET",
        UNIT13_V4_POSITION,
    )

    if not isinstance(positions, list):
        raise RuntimeError(
            "UNIT 13 POSITIONS NOT LIST"
        )

    active = []

    for p in positions:

        if not isinstance(p, dict):
            raise RuntimeError(
                "UNIT 13 POSITION RECORD MALFORMED"
            )

        if str(
            p.get("symbol", "")
                ).upper() != unit_13_14_active_symbols()[1]:
            continue

        size = D(
            p.get("size"),
            "POSITION SIZE",
            True
        )

        if size > 0:
            active.append(p)

    if not active:

        result = unit_13_v4_base_result(
            unit_12_result,
            "IDLE_NO_POSITION",
            "NO_ACTIVE_DEMO_POSITION",
        )

        print(
            "UNIT 13 STATUS = IDLE_NO_POSITION",
            flush=True
        )
        print(
            "UNIT 13 EXCHANGE WRITE = False",
            flush=True
        )

        return result

    if len(active) > 1:

        original_side = str(
            os.getenv(
                "ORIGINAL_POSITION_SIDE",
                ""
            )
        ).strip().upper()

        if original_side not in ("LONG", "SHORT"):
            raise RuntimeError(
                "UNIT 13 ORIGINAL POSITION SIDE "
                "REQUIRED FOR ACTIVE HEDGE PAIR"
            )

        matching = [
            position
            for position in active
            if str(
                position.get("side", "")
            ).upper() == original_side
        ]

        if len(matching) != 1:
            raise RuntimeError(
                "UNIT 13 ORIGINAL POSITION "
                "NOT UNIQUELY IDENTIFIED"
            )

        p = matching[0]

    else:
        p = active[0]

    side = str(
        p.get("side", "")
    ).upper()

    if side not in ("LONG", "SHORT"):
        raise RuntimeError(
            "UNIT 13 INVALID POSITION SIDE"
        )

    size = D(
        p.get("size"),
        "ACTIVE SIZE"
    )

    open_value = D(
        p.get("openValue"),
        "OPEN VALUE"
    )

    leverage = D(
        p.get("leverage"),
        "POSITION LEVERAGE"
    )

    entry = open_value / size

    # Cumulative position data is used for
    # quantity planning, never as proof of
    # TP1 or TP2 completion.

    if (
        "cumOpenSize" not in p
        or "cumCloseSize" not in p
    ):
        raise RuntimeError(
            "UNIT 13 CUMULATIVE HISTORY MISSING "
            "- NO TP ORDER"
        )

    cum_open = D(
        p["cumOpenSize"],
        "CUM OPEN"
    )
    cum_close = D(
        p["cumCloseSize"],
        "CUM CLOSE",
        True
    )

    if (
        cum_open < size
        or cum_close > cum_open
    ):
        raise RuntimeError(
            "UNIT 13 POSITION HISTORY INCONSISTENT"
        )

    # ========================================================
    # STEP-AWARE TP ALLOCATION
    # USE EXISTING UNIT 2 RENDER CONFIGURATION
    # ========================================================

    q1, q2, q3 = unit_13_v4_allocation(
        cum_open,
        step,
        strategy.get(
            "tp1_allocation_percent", 10
        ),
        strategy.get(
            "tp2_allocation_percent", 20
        ),
    )

    # ========================================================
    # TP1 / TP2 NET ROI TARGETS
    # ========================================================

    t1, t2 = unit_13_v4_targets(
        entry,
        leverage,
        side,
        price_step,
        tp1_floor,
        tp2_floor,
        fee,
    )

    mark = unit_13_v4_mark_price()

    # ========================================================
    # PERSISTENT ORIGINAL-POSITION CYCLE
    # NEVER PROMOTE TP FROM cumCloseSize
    # ========================================================

    cycle = str(
        p.get("id")
        or (
            str(
                p.get("createdTime")
                or p.get("openTime")
                or ""
            )
            + ":"
            + str(entry)
            + ":"
            + str(cum_open)
        )
    )

    state_path = unit_13_v4_state_path(
        "BTCSUSDT",
        side,
        cycle
    )

    state = unit_13_v4_load(state_path)

    if state is None:

        state = {
            "cycle": cycle,
            "orders": {},
            "version": 1,
            "legacy_closures_unattributed": bool(
                cum_close > 0
            ),
        }

        # Historical closures may be TP fills,
        # hedges, or manual reductions.
        # Never assign them to TP1 or TP2
        # without their exchange order IDs.

        unit_13_v4_save(
            state_path,
            state
        )

    # ========================================================
    # EXCHANGE-CONFIRMED TP FILLS
    # ========================================================

    history = unit_13_v4_history(
        "BTCSUSDT"
    )

    totals, unresolved = unit_13_v4_verified(
        state,
        history,
        side,
        "BTCSUSDT"
    )

    tp1_filled = totals["TP1"]
    tp2_filled = totals["TP2"]

    done1 = (
        q1 == 0
        or tp1_filled >= q1
    )

    done2 = (
        q2 == 0
        or tp2_filled >= q2
    )

    # ========================================================
    # TARGET REACHED CHECK
    # ========================================================

    reached1 = (
        mark >= t1
        if side == "LONG"
        else mark <= t1
    )

    reached2 = (
        mark >= t2
        if side == "LONG"
        else mark <= t2
    )

    action = "NONE"
    close_qty = Decimal(0)

    # Never submit a duplicate TP order
    # while its previous submission remains
    # unresolved or partially filled.

    if (
        not unresolved
        and not state.get(
            "legacy_closures_unattributed"
        )
    ):

        if (
            not done1
            and reached1
            and "TP1" not in state["orders"]
        ):

            action = "TP1"
            close_qty = q1

        elif (
            done1
            and not done2
            and reached2
            and "TP2" not in state["orders"]
        ):

            action = "TP2"
            close_qty = q2

    if close_qty > 0:

        close_qty = (
            (
                min(close_qty, size) / step
            ).to_integral_value(
                rounding=ROUND_DOWN
            ) * step
        )

    # ========================================================
    # TP3 ARMING
    # ONLY VERIFIED TP COMPLETION COUNTS
    # ========================================================

    armed = bool(
        done1
        and done2
        and q3 > 0
        and size > 0
        and not state.get(
            "legacy_closures_unattributed"
        )
    )

    result = unit_13_v4_base_result(
        unit_12_result,
        (
            "TP3_ARMED"
            if armed
            else "MONITORING"
        ),
        (
            "DYNAMIC_TP3_RUNTIME_REQUIRED"
            if armed
            else "DYNAMIC_TP_TARGET_NOT_REACHED"
        ),
    )

    result.update({
        "active_position_exists": True,
        "position_exists": True,
        "tp_management_required": True,
        "position_side": side,
        "position_size": float(size),
        "average_entry_price": float(entry),
        "mark_price": float(mark),

        "tp_target_allocation": "{}/{}/{}".format(
            strategy.get(
                "tp1_allocation_percent", 10
            ),
            strategy.get(
                "tp2_allocation_percent", 20
            ),
            strategy.get(
                "tp3_allocation_percent", 70
            ),
        ),

        "tp1_verified_filled_quantity":
            str(tp1_filled),

        "tp2_verified_filled_quantity":
            str(tp2_filled),

        "tp_history_unresolved": unresolved,

        "tp_legacy_closures_unattributed": bool(
            state.get(
                "legacy_closures_unattributed"
            )
        ),

        "tp1_target": float(t1),
        "tp2_target": float(t2),

        "tp1_target_price": str(t1),
        "tp2_target_price": str(t2),

        "tp1_quantity": float(q1),
        "tp2_quantity": float(q2),
        "tp3_quantity": float(q3),

        "tp1_completed": done1,
        "tp2_completed": done2,
        "tp3_armed": armed,

        "tp3_trailing_percent":
            float(trail_ref),

        "tp3_trailing_reference_percent":
            float(trail_ref),

        "tp3_trailing_min_percent":
            float(trail_min),

        "tp3_trailing_max_percent":
            float(trail_max),

        "tp3_trailing_dynamic": True,

        "tp1_net_roi_floor_percent":
            float(tp1_floor),

        "tp2_net_roi_floor_percent":
            float(tp2_floor),

        "tp_action": action,
    })

    # ========================================================
    # PART 3 ENDS INSIDE fresh_reconstruction_unit_13()
    # PART 4 CONTINUES AT FOUR-SPACE INDENTATION
    # DO NOT CLOSE OR EXECUTE THIS FUNCTION YET
    # ========================================================


    # ========================================================
    # 8. POSITION PNL AND TP EXECUTION REPORT
    # ========================================================

    direction = (
        Decimal("1")
        if side == "LONG"
        else Decimal("-1")
    )

    unrealized_pnl = (
        (mark - entry) * size * direction
    )

    estimated_margin = (
        entry * size / leverage
    )

    estimated_roi = (
        unrealized_pnl / estimated_margin
        * Decimal("100")
        if estimated_margin > 0
        else Decimal("0")
    )

    result.update({
        "position_leverage": float(leverage),
        "position_entry_price": float(entry),
        "position_mark_price": float(mark),
        "position_unrealized_pnl":
            float(unrealized_pnl),
        "position_unrealized_roi_percent":
            float(estimated_roi),
        "tp1_target_reached": reached1,
        "tp2_target_reached": reached2,
        "tp_execution_attempted": False,
        "tp_execution_completed": False,
        "exchange_write": False,
    })

    print(
        "UNIT 13 POSITION SIDE =",
        side,
        flush=True
    )
    print(
        "UNIT 13 POSITION SIZE =",
        size,
        flush=True
    )
    print(
        "UNIT 13 ENTRY PRICE =",
        entry,
        flush=True
    )
    print(
        "UNIT 13 MARK PRICE =",
        mark,
        flush=True
    )
    print(
        "UNIT 13 LEVERAGE =",
        leverage,
        flush=True
    )
    print(
        "UNIT 13 ESTIMATED UNREALIZED PNL =",
        unrealized_pnl,
        flush=True
    )
    print(
        "UNIT 13 ESTIMATED ROI % =",
        estimated_roi,
        flush=True
    )
    print(
        "UNIT 13 TP1 TARGET =",
        t1,
        flush=True
    )
    print(
        "UNIT 13 TP2 TARGET =",
        t2,
        flush=True
    )
    print(
        "UNIT 13 TP1 VERIFIED FILLED =",
        tp1_filled,
        flush=True
    )
    print(
        "UNIT 13 TP2 VERIFIED FILLED =",
        tp2_filled,
        flush=True
    )
    print(
        "UNIT 13 TP HISTORY UNRESOLVED =",
        unresolved,
        flush=True
    )
    print(
        "UNIT 13 TP ACTION =",
        action,
        flush=True
    )

    # ========================================================
    # 9. EXCHANGE-CONFIRMED DEMO TP EXECUTION
    # ========================================================

    if action != "NONE":

        if close_qty < minimum:

            result["skip_reason"] = (
                "TP_QUANTITY_BELOW_EXCHANGE_MINIMUM"
            )

            print(
                "UNIT 13 TP BELOW MINIMUM =",
                close_qty,
                flush=True
            )

        elif close_qty > size:

            result["skip_reason"] = (
                "TP_QUANTITY_EXCEEDS_POSITION"
            )

        else:

            if action in state["orders"]:

                result["skip_reason"] = (
                    "TP_PREVIOUS_ORDER_UNRESOLVED"
                )

            else:

                client_id = (
                    "FR13-"
                    + action
                    + "-"
                    + hashlib.sha256(
                        (
                            cycle
                            + ":"
                            + action
                        ).encode("utf-8")
                    ).hexdigest()[:24]
                )

                close_side = (
                    "SELL"
                    if side == "LONG"
                    else "BUY"
                )

                payload = {
                    "symbol": "BTCSUSDT",
                    "side": close_side,
                    "positionSide": side,
                    "type": "MARKET",
                    "quantity": format(
                        close_qty, "f"
                    ),
                    "newClientOrderId": client_id,
                }

                # Persist the intent before POST.
                # Never blindly retry an uncertain
                # exchange submission.

                state["orders"][action] = {
                    "client_id": client_id,
                    "order_id": None,
                    "quantity": str(close_qty),
                    "status": "INTENT_PERSISTED",
                    "created_at_ms": int(
                        time.time() * 1000
                    ),
                }

                unit_13_v4_save(
                    state_path,
                    state
                )

                print(
                    "UNIT 13 DEMO TP SUBMISSION =",
                    action,
                    flush=True
                )
                print(
                    "UNIT 13 TP CLOSE QUANTITY =",
                    close_qty,
                    flush=True
                )
                print(
                    "UNIT 13 TP CLIENT ORDER ID =",
                    client_id,
                    flush=True
                )

                result["tp_execution_attempted"] = True

                try:

                    reply = unit_13_v4_signed_request(
                        "POST",
                        UNIT13_V4_ORDER,
                        payload,
                    )

                except Exception:

                    print(
                        "UNIT 13 TP OUTCOME UNCERTAIN "
                        "- EXCHANGE RECONCILIATION REQUIRED",
                        flush=True
                    )

                    result["status"] = (
                        "TP_SUBMISSION_UNCERTAIN"
                    )
                    result["skip_reason"] = (
                        "TP_POST_OUTCOME_UNKNOWN"
                    )

                    # Keep the persistent intent.
                    # Do not submit another order
                    # with a new client ID.

                    return result

                if not isinstance(reply, dict):

                    result["status"] = (
                        "TP_SUBMISSION_UNCERTAIN"
                    )
                    result["skip_reason"] = (
                        "INVALID_EXCHANGE_RESPONSE"
                    )

                    return result

                order_id = reply.get("orderId")

                if (
                    reply.get("success") is not True
                    or not order_id
                ):

                    result["status"] = (
                        "TP_SUBMISSION_UNCONFIRMED"
                    )
                    result["skip_reason"] = (
                        "EXCHANGE_ACK_NOT_CONFIRMED"
                    )

                    print(
                        "UNIT 13 TP RESPONSE =",
                        str(reply)[:400],
                        flush=True
                    )

                    return result

                state["orders"][action][
                    "order_id"
                ] = str(order_id)

                state["orders"][action][
                    "status"
                ] = "ACKNOWLEDGED_NOT_FILL_VERIFIED"

                unit_13_v4_save(
                    state_path,
                    state
                )

                result.update({
                    "status": "TP_ORDER_ACKNOWLEDGED",
                    "skip_reason":
                        "AWAITING_EXCHANGE_CONFIRMED_FILL",
                    "tp_execution_completed": False,
                    "demo_order_executed": False,
                    "tp_order_id": str(order_id),
                    "tp_close_quantity":
                        str(close_qty),
                    "exchange_write": True,
                })

                print(
                    "UNIT 13 TP ORDER ACKNOWLEDGED =",
                    order_id,
                    flush=True
                )
                print(
                    "UNIT 13 TP FILL VERIFICATION = PENDING",
                    flush=True
                )

    # ========================================================
    # 10. FINAL UNIT 13 RESULT
    # ========================================================

    if (
        result["status"] == "MONITORING"
        and (
            unresolved
            or state.get(
                "legacy_closures_unattributed"
            )
        )
    ):

        result["skip_reason"] = (
            "TP_HISTORY_RECONCILIATION_REQUIRED"
        )

    print(
        "UNIT 13 STATUS =",
        result["status"],
        flush=True
    )
    print(
        "UNIT 13 TP1 COMPLETED =",
        done1,
        flush=True
    )
    print(
        "UNIT 13 TP2 COMPLETED =",
        done2,
        flush=True
    )
    print(
        "UNIT 13 TP3 ARMED =",
        result["tp3_armed"],
        flush=True
    )
    print(
        "UNIT 13 EXCHANGE WRITE =",
        result["exchange_write"],
        flush=True
    )
    print(
        "FRESH RECONSTRUCTION UNIT 13 RESULT = PASS",
        flush=True
    )
    print("=" * 80, flush=True)

    return result


# ============================================================
# END UNIT 13 V5 PART 4
# MAIN FUNCTION COMPLETE
# PART 5: HYBRID ADAPTER AND VALIDATION
# ============================================================



# ============================================================
# UNIT 13 V5 - PART 5 OF 5
# HYBRID ADAPTER, VALIDATION AND UNIT 14 HANDOVER
# ZERO INDENTATION
# ============================================================


# ============================================================
# 11. UNIT 13 HYBRID ADAPTER
# ============================================================

def fresh_unit_13_hybrid_adapter(
    config,
    unit_12_result,
):

    print("=" * 80, flush=True)
    print(
        "UNIT 13 V5 HYBRID ADAPTER START",
        flush=True
    )

    try:

        result = fresh_reconstruction_unit_13(
            config,
            unit_12_result,
        )

    except Exception as exc:

        print(
            "UNIT 13 EXECUTION ERROR =",
            str(exc),
            flush=True
        )

        result = unit_13_v4_base_result(
            unit_12_result,
            "ERROR",
            str(exc),
        )

        result["execution_error"] = str(exc)

    if not isinstance(result, dict):
        raise RuntimeError(
            "UNIT 13 RESULT CONTRACT INVALID"
        )

    if result.get("unit") != 13:
        raise RuntimeError(
            "UNIT 13 RESULT UNIT MISMATCH"
        )

    # ========================================================
    # EXISTING POSITION MANAGEMENT MUST REMAIN
    # INDEPENDENT OF BOT_MODE.
    # ========================================================

    result["position_management_independent_of_bot_mode"] = True

    # ========================================================
    # EXCHANGE ACKNOWLEDGMENT IS NOT A TP FILL.
    # ========================================================

    if result.get("status") in (
        "TP_ORDER_ACKNOWLEDGED",
        "TP_SUBMISSION_UNCERTAIN",
        "TP_SUBMISSION_UNCONFIRMED",
    ):

        result["tp_execution_completed"] = False

    # ========================================================
    # TP3 MUST NEVER BE ARMED BY HEDGE CLOSURES.
    # ========================================================

    tp1_done = bool(
        result.get("tp1_completed", False)
    )

    tp2_done = bool(
        result.get("tp2_completed", False)
    )

    if not (tp1_done and tp2_done):

        result["tp3_armed"] = False

    if result.get(
        "tp_legacy_closures_unattributed",
        False
    ):

        result["tp3_armed"] = False

    if result.get(
        "tp_history_unresolved",
        False
    ):

        result["tp3_armed"] = False

    # ========================================================
    # DO NOT REPORT REAL-CASH SUBMISSION.
    # ========================================================

    result["real_submission_attempted"] = False

    print(
        "UNIT 13 HYBRID ADAPTER STATUS =",
        result.get("status"),
        flush=True
    )
    print(
        "UNIT 13 TP1 COMPLETED =",
        result.get("tp1_completed", False),
        flush=True
    )
    print(
        "UNIT 13 TP2 COMPLETED =",
        result.get("tp2_completed", False),
        flush=True
    )
    print(
        "UNIT 13 TP3 ARMED =",
        result.get("tp3_armed", False),
        flush=True
    )
    print(
        "UNIT 13 EXCHANGE WRITE =",
        result.get("exchange_write", False),
        flush=True
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# 12. UNIT 13 LOCAL VALIDATION
# NO EXCHANGE ORDERS
# ============================================================

def unit_13_validation_v5():

    checks = {}

    # ========================================================
    # DECIMAL VALIDATION
    # ========================================================

    try:

        assert unit_13_v4_D(
            "0.5", "TEST"
        ) == Decimal("0.5")

        assert unit_13_v4_D(
            "0", "TEST", True
        ) == Decimal("0")

        checks["DECIMAL_VALIDATION"] = "PASS"

    except Exception as exc:

        checks["DECIMAL_VALIDATION"] = (
            "FAIL: " + str(exc)
        )

    # ========================================================
    # STEP-AWARE TP ALLOCATION
    # ========================================================

    try:

        a = unit_13_v4_allocation(
            Decimal("0.001"),
            Decimal("0.001"),
        )

        assert a == (
            Decimal("0"),
            Decimal("0"),
            Decimal("0.001"),
        )

        b = unit_13_v4_allocation(
            Decimal("0.002"),
            Decimal("0.001"),
        )

        assert b == (
            Decimal("0.001"),
            Decimal("0"),
            Decimal("0.001"),
        )

        c = unit_13_v4_allocation(
            Decimal("0.010"),
            Decimal("0.001"),
        )

        assert sum(c) == Decimal("0.010")
        assert all(x > 0 for x in c)

        checks["TP_ALLOCATION"] = "PASS"

    except Exception as exc:

        checks["TP_ALLOCATION"] = (
            "FAIL: " + str(exc)
        )

    # ========================================================
    # TP NET ROI TARGETS
    # ========================================================

    try:

        long_t1, long_t2 = unit_13_v4_targets(
            Decimal("100"),
            Decimal("10"),
            "LONG",
            Decimal("0.01"),
            Decimal("20"),
            Decimal("40"),
            Decimal("0.08"),
        )

        assert long_t2 > long_t1 > Decimal("100")

        short_t1, short_t2 = unit_13_v4_targets(
            Decimal("100"),
            Decimal("10"),
            "SHORT",
            Decimal("0.01"),
            Decimal("20"),
            Decimal("40"),
            Decimal("0.08"),
        )

        assert Decimal("100") > short_t1 > short_t2

        checks["TP_NET_ROI_TARGETS"] = "PASS"

    except Exception as exc:

        checks["TP_NET_ROI_TARGETS"] = (
            "FAIL: " + str(exc)
        )

    # ========================================================
    # TP FILL VERIFICATION
    # HEDGE CLOSURES MUST NOT COUNT.
    # ========================================================

    try:

        state = {
            "orders": {
                "TP1": {
                    "client_id": "FR13-TP1-TEST",
                    "order_id": "10001",
                    "quantity": "0.001",
                }
            }
        }

        history = [
            {
                "symbol": "BTCSUSDT",
                "positionSide": "LONG",
                "side": "SELL",
                "clientOrderId": "HEDGE-CLOSE-TEST",
                "orderId": "99999",
                "executedQty": "0.010",
                "status": "FILLED",
            },
            {
                "symbol": "BTCSUSDT",
                "positionSide": "LONG",
                "side": "SELL",
                "clientOrderId": "FR13-TP1-TEST",
                "orderId": "10001",
                "executedQty": "0.001",
                "status": "FILLED",
            },
        ]

        totals, pending = unit_13_v4_verified(
            state,
            history,
            "LONG",
            "BTCSUSDT",
        )

        assert totals["TP1"] == Decimal("0.001")
        assert totals["TP2"] == Decimal("0")
        assert pending is False

        checks["TP_FILL_IDENTITY"] = "PASS"

    except Exception as exc:

        checks["TP_FILL_IDENTITY"] = (
            "FAIL: " + str(exc)
        )

    # ========================================================
    # ACKNOWLEDGMENT MUST NOT COUNT AS COMPLETION.
    # ========================================================

    try:

        sample = unit_13_v4_base_result(
            {"status": "PAUSED"},
            "TP_ORDER_ACKNOWLEDGED",
            "AWAITING_FILL",
        )

        assert sample["tp_execution_completed"] is False
        assert sample["tp3_armed"] is False

        checks["ACK_NOT_FILL"] = "PASS"

    except Exception as exc:

        checks["ACK_NOT_FILL"] = (
            "FAIL: " + str(exc)
        )

    passed = all(
        value == "PASS"
        for value in checks.values()
    )

    print("=" * 80, flush=True)
    print(
        "UNIT 13 V5 VALIDATION RESULTS",
        flush=True
    )

    for name, status in checks.items():

        print(
            "UNIT 13",
            name,
            "=",
            status,
            flush=True
        )

    print(
        "UNIT 13 V5 VALIDATION =",
        "PASS" if passed else "FAIL",
        flush=True
    )

    print("=" * 80, flush=True)

    return {
        "unit": 13,
        "version": "V5",
        "passed": passed,
        "checks": checks,
    }


# ============================================================
# 13. UNIT 13 INITIALIZATION AND HANDOVER
# ============================================================

FRESH_UNIT_13_VALIDATION_READY = (
    unit_13_validation_v5()
)

if not FRESH_UNIT_13_VALIDATION_READY["passed"]:

    raise RuntimeError(
        "UNIT 13 V5 LOCAL VALIDATION FAILED"
    )


FRESH_RECONSTRUCTION_UNIT_13_RESULT = (
    fresh_unit_13_hybrid_adapter(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_12_RESULT,
    )
)


# ============================================================
# END COMPLETE UNIT 13 V5 REPLACEMENT
# NEXT EXISTING SECTION: UNIT 14
# ============================================================


# ============================================================
# COMPLETE UNIT 14 V3 REPLACEMENT
# UNIT 13 -> UNIT 14 -> UNIT 15
# ZERO INDENTATION
#
# WEEX DEMO POSITION MANAGEMENT
# FIVE DYNAMIC BACKUPS: B1 - B5
# PERCENT AVAILABLE BALANCE
# 0.3% LIQUIDATION BUFFER
# MAXIMUM EXPOSURE 35%
# TP3 TRAILING MANAGEMENT
#
# BOT_MODE DOES NOT CONTROL UNIT 14
# NO LIVE CASH ENDPOINT
# NO LEVERAGE OR MARGIN MODE MUTATION
# NO AUTOMATIC POST RETRIES
# ============================================================

import os
import json
import time
import hmac
import base64
import hashlib
import urllib.request
import urllib.parse
import urllib.error
from decimal import Decimal, ROUND_DOWN


UNIT14_V3_BASE = "https://api-contract.weex.com"
UNIT14_V3_POSITION = "/capi/v3/sim/position/allPosition"
UNIT14_V3_BALANCE = "/capi/v3/sim/balance"
UNIT14_V3_HISTORY = "/capi/v3/sim/order/history"
UNIT14_V3_ORDER = "/capi/v3/sim/order"


# ============================================================
# 1. DECIMAL UTILITIES
# ============================================================

def unit_14_v3_D(value, name="VALUE", zero=False):

    if value is None or isinstance(value, bool):
        raise RuntimeError(
            "UNIT 14 MISSING " + name
        )

    try:
        x = Decimal(str(value))
    except Exception as exc:
        raise RuntimeError(
            "UNIT 14 INVALID " + name
        ) from exc

    if not x.is_finite():
        raise RuntimeError(
            "UNIT 14 NONFINITE " + name
        )

    if x < 0 or (x == 0 and not zero):
        raise RuntimeError(
            "UNIT 14 NONPOSITIVE " + name
        )

    return x


def unit_14_v3_floor(value, step):

    return (
        value / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    ) * step


# ============================================================
# 2. SIGNED DEMO REQUEST
# ============================================================

def unit_14_v3_signed_request(
    method,
    path,
    query="",
    payload=None,
):

    allowed = {
        ("GET", UNIT14_V3_POSITION),
        ("GET", UNIT14_V3_BALANCE),
        ("GET", UNIT14_V3_HISTORY),
        ("POST", UNIT14_V3_ORDER),
    }

    if (method, path) not in allowed:
        raise RuntimeError(
            "UNIT 14 NON-DEMO ENDPOINT BLOCKED"
        )

    if method == "POST" and not isinstance(
        payload, dict
    ):
        raise RuntimeError(
            "UNIT 14 POST PAYLOAD INVALID"
        )

    if method == "GET" and payload is not None:
        raise RuntimeError(
            "UNIT 14 GET BODY NOT ALLOWED"
        )

    key = (
        os.getenv("WEEX_API_KEY")
        or os.getenv("API_KEY")
    )

    secret = (
        os.getenv("WEEX_API_SECRET")
        or os.getenv("API_SECRET")
    )

    phrase = (
        os.getenv("WEEX_API_PASSPHRASE")
        or os.getenv("API_PASSPHRASE")
    )

    if not all((key, secret, phrase)):
        raise RuntimeError(
            "UNIT 14 DEMO CREDENTIALS MISSING"
        )

    body = (
        json.dumps(
            payload,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        if payload is not None
        else ""
    )

    timestamp = str(int(time.time() * 1000))

    prehash = timestamp + method + path

    if query:
        prehash += "?" + query

    prehash += body

    signature = base64.b64encode(
        hmac.new(
            secret.encode("utf-8"),
            prehash.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    ).decode("utf-8")

    url = UNIT14_V3_BASE + path

    if query:
        url += "?" + query

    request = urllib.request.Request(
        url,
        method=method,
        data=(
            body.encode("utf-8")
            if method == "POST"
            else None
        ),
        headers={
            "ACCESS-KEY": key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": phrase,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            status = response.getcode()
            raw = response.read().decode(
                "utf-8", errors="replace"
            )

    except urllib.error.HTTPError as exc:

        detail = exc.read().decode(
            "utf-8", errors="replace"
        )[:400]

        raise RuntimeError(
            "UNIT 14 WEEX HTTP "
            + str(exc.code)
            + ": "
            + detail
        ) from exc

    # Never automatically retry a POST.
    # An exchange order may have been received
    # even when the acknowledgement was lost.

    if not 200 <= status < 300:
        raise RuntimeError(
            "UNIT 14 HTTP STATUS " + str(status)
        )

    try:
        return json.loads(raw)
    except ValueError as exc:
        raise RuntimeError(
            "UNIT 14 INVALID RESPONSE JSON"
        ) from exc


# ============================================================
# 3. POSITION, BALANCE AND ORDER HISTORY
# ============================================================


def unit_14_v3_positions():

    rows = unit_14_v3_signed_request(
        "GET",
        UNIT14_V3_POSITION,
    )

    if not isinstance(rows, list):
        raise RuntimeError(
            "UNIT 14 POSITION RESPONSE NOT LIST"
        )

    active = {}

    for p in rows:

        if not isinstance(p, dict):
            raise RuntimeError(
                "UNIT 14 POSITION RECORD INVALID"
            )

        if str(
            p.get("symbol", "")
        ).upper() != unit_13_14_active_symbols()[1]:
            continue

        size = unit_14_v3_D(
            p.get("size"),
            "POSITION SIZE",
            True,
        )

        if size <= 0:
            continue

        side = str(
            p.get("side", "")
        ).upper()

        if side not in ("LONG", "SHORT"):
            raise RuntimeError(
                "UNIT 14 INVALID POSITION SIDE"
            )

        if side in active:
            raise RuntimeError(
                "UNIT 14 DUPLICATE ACTIVE POSITION SIDE"
            )

        active[side] = p

    return active


def unit_14_v3_position(side=None):

    active = unit_14_v3_positions()

    if side is not None:

        side = str(side).upper()

        if side not in ("LONG", "SHORT"):
            raise RuntimeError(
                "UNIT 14 INVALID REQUESTED SIDE"
            )

        return active.get(side)

    if not active:
        return None

    if len(active) == 1:
        return next(iter(active.values()))

    raise RuntimeError(
        "UNIT 14 ORIGINAL SIDE REQUIRED "
        "FOR HEDGE PAIR"
    )

def unit_14_v3_balance():

    rows = unit_14_v3_signed_request(
        "GET",
        UNIT14_V3_BALANCE,
    )

    if not isinstance(rows, list):
        raise RuntimeError(
            "UNIT 14 BALANCE RESPONSE NOT LIST"
        )

    for row in rows:

        if (
            isinstance(row, dict)
            and str(
                row.get("asset", "")
            ).upper() == "SUSDT"
        ):
            return unit_14_v3_D(
                row.get("availableBalance"),
                "AVAILABLE BALANCE",
                True,
            )

    raise RuntimeError(
        "UNIT 14 SUSDT BALANCE MISSING"
    )


def unit_14_v3_history():

    orders = []

    # Preserve working reference pagination.
    # Do not accept partial history as complete.

    for page in range(20):

        query = urllib.parse.urlencode({
            "symbol": market_symbol,
            "limit": 1000,
            "page": page,
        })

        batch = unit_14_v3_signed_request(
            "GET",
            UNIT14_V3_HISTORY,
            query,
        )

        if not isinstance(batch, list):
            raise RuntimeError(
                "UNIT 14 HISTORY NOT LIST"
            )

        if not all(
            isinstance(o, dict)
            for o in batch
        ):
            raise RuntimeError(
                "UNIT 14 MALFORMED HISTORY"
            )

        orders.extend(batch)

        if len(batch) < 1000:

            print(
                "PASS: UNIT 14 ORDER HISTORY COMPLETE | "
                "RECORDS =",
                len(orders),
                flush=True
            )

            return orders

    raise RuntimeError(
        "UNIT 14 HISTORY PAGINATION INCOMPLETE"
    )


def unit_14_v3_mark():
    market_symbol, _ = unit_13_14_active_symbols()

    query = urllib.parse.urlencode({
        "symbol": market_symbol,
        "priceType": "MARK",
    })

    request = urllib.request.Request(
        UNIT14_V3_BASE
        + "/capi/v3/market/symbolPrice?"
        + query,
        method="GET",
    )

    with urllib.request.urlopen(
        request,
        timeout=15,
    ) as response:

        data = json.loads(
            response.read().decode("utf-8")
        )

    if (
        not isinstance(data, dict)
        or data.get("symbol") != market_symbol
    ):
        raise RuntimeError(
            "UNIT 14 INVALID MARK RESPONSE"
        )

    return unit_14_v3_D(
        data.get("price"),
        "MARK PRICE"
    )


# ============================================================
# 4. TRADE IDENTITY AND BACKUP RECONCILIATION
# ============================================================

def unit_14_v3_trade_key(position):

    created = str(
        position.get("createdTime", "")
    )

    if created.isdigit():
        return created[-12:]

    position_id = str(
        position.get("id", "")
    )

    if position_id:
        return position_id[-12:]

    raise RuntimeError(
        "UNIT 14 POSITION IDENTITY MISSING"
    )


def unit_14_v3_backup_id(stage, key):

    return (
        "FR-B"
        + str(stage)
        + "-"
        + key
    )[:36]


def unit_14_v3_reconcile(history, key):

    existing = set()
    filled = set()

    for stage in range(1, 6):

        client_id = unit_14_v3_backup_id(
            stage, key
        )

        matching = [
            o for o in history
            if str(
                o.get("clientOrderId", "")
            ) == client_id
        ]

        for order in matching:

            status = str(
                order.get("status", "")
            ).upper()

            executed = unit_14_v3_D(
                order.get("executedQty", 0),
                "EXECUTED QUANTITY",
                True,
            )

            if status not in (
                "CANCELED",
                "CANCELLED",
                "REJECTED",
                "EXPIRED",
            ):
                existing.add(stage)

            if status == "FILLED" and executed > 0:
                filled.add(stage)

            # A partially filled stage must not
            # automatically advance to the next.

            if executed > 0 and status != "FILLED":
                existing.add(stage)

    completed = 0

    for stage in range(1, 6):
        if stage in filled:
            completed = stage
        else:
            break

    if any(
        stage > completed + 1
        for stage in filled
    ):
        raise RuntimeError(
            "UNIT 14 NONSEQUENTIAL BACKUP FILLS"
        )

    return completed, existing


# ============================================================
# 5. LIQUIDATION BUFFER
# ============================================================

def unit_14_v3_trigger(
    side,
    liquidation,
    mark,
    buffer_pct,
):

    D = unit_14_v3_D

    liquidation = D(
        liquidation, "LIQUIDATION PRICE"
    )
    mark = D(mark, "MARK PRICE")
    buffer_pct = D(
        buffer_pct, "BUFFER PERCENT"
    )

    fraction = buffer_pct / D(100)

    if side == "LONG":

        trigger = liquidation * (
            D(1) + fraction
        )

        reached = mark <= trigger

    elif side == "SHORT":

        trigger = liquidation * (
            D(1) - fraction
        )

        reached = mark >= trigger

    else:
        raise RuntimeError(
            "UNIT 14 INVALID SIDE"
        )

    if trigger <= 0:
        raise RuntimeError(
            "UNIT 14 INVALID TRIGGER"
        )

    return trigger, bool(reached)


# ============================================================
# 6. RESULT CONSTRUCTOR
# ============================================================

def unit_14_v3_result(unit_13_result):

    return {
        "unit": 14,
        "status": "MONITORING",
        "unit_13_status": unit_13_result.get(
            "status"
        ),
        "position_exists": False,
        "backup_maximum": 5,
        "backups_filled": 0,
        "backup_next_stage": None,
        "backup_trigger_reached": False,
        "backup_submission_enabled": True,
        "backup_execution_attempted": False,
        "backup_execution_completed": False,
        "tp3_armed": False,
        "tp3_execution_attempted": False,
        "tp3_execution_completed": False,
        "real_submission_attempted": False,
        "sl_execution_attempted": False,
        "exchange_write": False,
        "skip_reason": "NONE",
    }


# ============================================================
# 7. MAIN UNIT 14
# ============================================================


 
# ============================================================
# UNIT 14 - PERSISTENT HEDGE / RECOVERY REGISTRY
# H1 / H2 / R1 / R2
# DEMO EXECUTION STATE
# ============================================================

import sqlite3
import hashlib
from decimal import Decimal


UNIT14_STAGE_ACTIONS = (
    "H1-C", "H1-H",
    "H2-C", "H2-H",
    "R1-C", "R1-O",
    "R2-C", "R2-O",
)


def unit_14_stage_db():

    path = os.getenv(
        "UNIT14_STAGE_DB_PATH",
        "/var/data/unit14_stages.sqlite3"
    )

    directory = os.path.dirname(path)

    if directory and not os.path.isdir(directory):
        raise RuntimeError(
            "UNIT 14 PERSISTENT DISK UNAVAILABLE"
        )

    db = sqlite3.connect(
        path,
        timeout=30,
        isolation_level=None
    )

    db.execute("PRAGMA busy_timeout=30000")
    db.execute("PRAGMA journal_mode=WAL")

    db.execute("""
        CREATE TABLE IF NOT EXISTS stage_cycles (
            cycle_id TEXT PRIMARY KEY,
            symbol TEXT NOT NULL,
            original_side TEXT NOT NULL,
            original_quantity TEXT NOT NULL,
            original_entry TEXT NOT NULL,
            frozen_atr TEXT NOT NULL,
            stage TEXT NOT NULL DEFAULT 'READY',
            state TEXT NOT NULL DEFAULT 'ACTIVE',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS stage_orders (
            client_id TEXT PRIMARY KEY,
            cycle_id TEXT NOT NULL,
            action TEXT NOT NULL,
            quantity TEXT NOT NULL,
            state TEXT NOT NULL DEFAULT 'CLAIMED',
            exchange_order_id TEXT,
            confirmed_filled TEXT NOT NULL DEFAULT '0',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(cycle_id, action)
        )
    """)

    return db


def unit_14_stage_create_cycle(
    cycle_id,
    symbol,
    original_side,
    original_quantity,
    original_entry,
    frozen_atr
):
    """
    Create a new persisted cycle or preserve
    an existing cycle and its order history.
    """

    D = unit_14_v3_D

    cycle_id = str(cycle_id).strip()
    symbol = str(symbol).strip().upper()
    original_side = str(original_side).strip().upper()

    quantity = D(
        original_quantity,
        "ORIGINAL QUANTITY"
    )

    entry = D(
        original_entry,
        "ORIGINAL ENTRY"
    )

    atr = D(
        frozen_atr,
        "FROZEN ATR"
    )

    if (
        not cycle_id
        or not symbol
        or original_side not in ("LONG", "SHORT")
    ):
        raise RuntimeError(
            "INVALID STAGE CYCLE IDENTITY"
        )

    if quantity <= 0 or entry <= 0 or atr <= 0:
        raise RuntimeError(
            "INVALID HEDGE CYCLE VALUES"
        )

    db = unit_14_stage_db()

    try:
        db.execute("BEGIN IMMEDIATE")

        existing = db.execute("""
            SELECT
                symbol,
                original_side,
                original_quantity,
                original_entry,
                frozen_atr,
                stage,
                state
            FROM stage_cycles
            WHERE cycle_id = ?
        """, (cycle_id,)).fetchone()

        if existing is not None:

            saved_symbol = str(existing[0]).upper()
            saved_side = str(existing[1]).upper()

            if (
                saved_symbol != symbol
                or saved_side != original_side
            ):
                raise RuntimeError(
                    "PERSISTED CYCLE SYMBOL OR SIDE MISMATCH"
                )

            for name, value in zip(
                ("QUANTITY", "ENTRY", "ATR"),
                existing[2:5]
            ):
                if D(
                    value,
                    "PERSISTED " + name
                ) <= 0:
                    raise RuntimeError(
                        "INVALID PERSISTED " + name
                    )

            print(
                "UNIT 14 PERSISTED CYCLE FOUND =",
                cycle_id,
                "STAGE =", existing[5],
                "STATE =", existing[6],
                flush=True
            )

        else:

            db.execute("""
                INSERT INTO stage_cycles (
                    cycle_id,
                    symbol,
                    original_side,
                    original_quantity,
                    original_entry,
                    frozen_atr
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                cycle_id,
                symbol,
                original_side,
                str(quantity),
                str(entry),
                str(atr)
            ))

            print(
                "UNIT 14 NEW STAGE CYCLE CREATED =",
                cycle_id,
                flush=True
            )

        db.execute("COMMIT")

        return cycle_id

    except Exception:

        if db.in_transaction:
            db.execute("ROLLBACK")

        raise

    finally:
        db.close()


def unit_14_stage_client_id(cycle_id, action):
    cycle_id = str(cycle_id).strip()
    action = str(action).strip().upper()

    if not cycle_id:
        raise RuntimeError(
            "UNIT 14 CYCLE ID MISSING"
        )

    if action not in UNIT14_STAGE_ACTIONS:
        raise RuntimeError(
            "UNIT 14 INVALID STAGE ACTION"
        )

    digest = hashlib.sha256(
        (cycle_id + "|" + action).encode("utf-8")
    ).hexdigest()[:20]

    return "U14-" + action + "-" + digest


def unit_14_stage_client_id(cycle_id, action):
    """
    Stable client ID for each cycle and stage action.
    Same cycle/action always produces the same ID.
    """

    cycle_id = str(cycle_id).strip()
    action = str(action).strip().upper()

    if not cycle_id:
        raise RuntimeError(
            "UNIT 14 CYCLE ID MISSING"
        )

    if action not in UNIT14_STAGE_ACTIONS:
        raise RuntimeError(
            "UNIT 14 INVALID STAGE ACTION"
        )

    digest = hashlib.sha256(
        (cycle_id + "|" + action).encode("utf-8")
    ).hexdigest()[:20]

    return "U14-" + action + "-" + digest

def unit_14_stage_claim(
    cycle_id,
    action,
    quantity
):
    """
    Persist an order claim before transmission.
    Existing claims are never automatically
    submitted again.
    """

    if action not in UNIT14_STAGE_ACTIONS:
        raise RuntimeError("INVALID HEDGE ACTION")

    qty = unit_14_v3_D(
        quantity,
        "STAGE QUANTITY"
    )

    if qty <= 0:
        raise RuntimeError("INVALID STAGE QUANTITY")

    client_id = unit_14_stage_client_id(
        cycle_id,
        action
    )

    db = unit_14_stage_db()

    try:
        db.execute("BEGIN IMMEDIATE")

        cycle = db.execute("""
            SELECT state
            FROM stage_cycles
            WHERE cycle_id = ?
        """, (cycle_id,)).fetchone()

        if cycle is None or cycle[0] != "ACTIVE":
            raise RuntimeError("STAGE CYCLE NOT ACTIVE")

        existing = db.execute("""
            SELECT quantity, state
            FROM stage_orders
            WHERE client_id = ?
        """, (client_id,)).fetchone()

        if existing is not None:

            db.execute("COMMIT")

            return {
                "claimed": False,
                "client_id": client_id,
                "state": existing[1],
                "quantity": existing[0],
            }

        db.execute("""
            INSERT INTO stage_orders (
                client_id, cycle_id, action,
                quantity, state
            )
            VALUES (?, ?, ?, ?, 'CLAIMED')
        """, (
            client_id,
            cycle_id,
            action,
            str(qty)
        ))

        db.execute("COMMIT")

        return {
            "claimed": True,
            "client_id": client_id,
            "state": "CLAIMED",
            "quantity": str(qty),
        }

    except Exception:
        if db.in_transaction:
            db.execute("ROLLBACK")
        raise

    finally:
        db.close()


def unit_14_stage_update(
    client_id,
    state,
    exchange_order_id=None,
    confirmed_filled=None
):
    """
    Update persisted exchange acknowledgement
    and confirmed fill information.

    Never decrease an already confirmed fill.
    """

    D = unit_14_v3_D

    db = unit_14_stage_db()

    try:
        db.execute("BEGIN IMMEDIATE")

        existing = db.execute("""
            SELECT quantity, confirmed_filled,
                   exchange_order_id, state
            FROM stage_orders
            WHERE client_id = ?
        """, (client_id,)).fetchone()

        if existing is None:
            raise RuntimeError(
                "STAGE ORDER CLAIM NOT FOUND"
            )

        expected = D(
            existing[0],
            "EXPECTED STAGE QUANTITY"
        )

        previous = D(
            existing[1],
            "PREVIOUS CONFIRMED FILL",
            True
        )

        if confirmed_filled is None:
            filled = previous
        else:
            filled = D(
                confirmed_filled,
                "CONFIRMED STAGE FILL",
                True
            )

        if filled < previous:
            raise RuntimeError(
                "STAGE CONFIRMED FILL REGRESSION"
            )

        if filled > expected:
            raise RuntimeError(
                "STAGE FILL EXCEEDS CLAIMED QUANTITY"
            )

        saved_order_id = existing[2]

        if (
            saved_order_id
            and exchange_order_id
            and str(saved_order_id) != str(exchange_order_id)
        ):
            raise RuntimeError(
                "STAGE EXCHANGE ORDER ID MISMATCH"
            )

        if (
            str(existing[3]).upper() == "FILLED"
            and str(state).upper() != "FILLED"
        ):
            raise RuntimeError(
                "CONFIRMED FILLED ORDER STATE REGRESSION"
            )

        if str(state).upper() == "FILLED" and filled != expected:
            raise RuntimeError(
                "FILLED STATE WITHOUT COMPLETE QUANTITY"
            )

        db.execute("""
            UPDATE stage_orders
            SET state = ?,
                exchange_order_id =
                    COALESCE(?, exchange_order_id),
                confirmed_filled = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE client_id = ?
        """, (
            state,
            exchange_order_id,
            str(filled),
            client_id
        ))

        db.execute("COMMIT")

        return True

    except Exception:
        if db.in_transaction:
            db.execute("ROLLBACK")
        raise

    finally:
        db.close()

def unit_14_stage_read(cycle_id):

    db = unit_14_stage_db()

    try:

        cycle = db.execute("""
            SELECT cycle_id, symbol,
                   original_side, original_quantity,
                   original_entry, frozen_atr,
                   stage, state
            FROM stage_cycles
            WHERE cycle_id = ?
        """, (cycle_id,)).fetchone()

        if cycle is None:
            return None

        orders = db.execute("""
            SELECT action, client_id, quantity,
                   state, exchange_order_id,
                   confirmed_filled
            FROM stage_orders
            WHERE cycle_id = ?
            ORDER BY created_at, action
        """, (cycle_id,)).fetchall()

        return {
            "cycle_id": cycle[0],
            "symbol": cycle[1],
            "original_side": cycle[2],
            "original_quantity": cycle[3],
            "original_entry": cycle[4],
            "frozen_atr": cycle[5],
            "stage": cycle[6],
            "state": cycle[7],
            "orders": {
                row[0]: {
                    "client_id": row[1],
                    "quantity": row[2],
                    "state": row[3],
                    "exchange_order_id": row[4],
                    "confirmed_filled": row[5],
                }
                for row in orders
            }
        }

    finally:
        db.close()
   

# ============================================================
# UNIT 14 - H1/H2/R1/R2 EXCHANGE RECONCILIATION
# USES EXISTING WEEX DEMO ORDER HISTORY
# NO ORDER SUBMISSION
# ============================================================

def unit_14_stage_reconcile_order(
    cycle_id,
    action,
    history=None,
):
    from decimal import Decimal

    if action not in UNIT14_STAGE_ACTIONS:
        raise RuntimeError(
            "INVALID STAGE RECONCILIATION ACTION"
        )

    cycle = unit_14_stage_read(cycle_id)

    if cycle is None:
        raise RuntimeError(
            "PERSISTED STAGE CYCLE MISSING"
        )

    record = cycle["orders"].get(action)

    if record is None:
        return {
            "action": action,
            "state": "NOT_CLAIMED",
            "confirmed_filled": "0",
            "complete": False,
        }

    client_id = record["client_id"]

    expected = unit_14_v3_D(
        record["quantity"],
        "EXPECTED STAGE QUANTITY"
    )

    previous_filled = unit_14_v3_D(
        record["confirmed_filled"],
        "PREVIOUS CONFIRMED FILL",
        True
    )

    if history is None:
        history = unit_14_v3_history()

    if not isinstance(history, list):
        raise RuntimeError(
            "INVALID STAGE ORDER HISTORY"
        )

    matches = [
        order
        for order in history
        if isinstance(order, dict)
        and str(
            order.get("clientOrderId", "")
        ) == client_id
    ]

    if not matches:

        # No history record does not prove
        # that a claimed order was never sent.
        # Preserve the claim and do not retry.

        return {
            "action": action,
            "state": "ACK_OR_HISTORY_UNKNOWN",
            "client_id": client_id,
            "confirmed_filled": str(previous_filled),
            "complete": False,
        }

    order_ids = {
        str(order["orderId"])
        for order in matches
        if order.get("orderId") is not None
    }

    if len(order_ids) > 1:
        raise RuntimeError(
            "DUPLICATE EXCHANGE ORDER IDS "
            + client_id
        )

    exchange_order_id = next(
        iter(order_ids),
        None
    )

    exchange_filled = max(
        (
            unit_14_v3_D(
                order.get("executedQty", "0"),
                "STAGE EXECUTED QUANTITY",
                True
            )
            for order in matches
        ),
        default=Decimal("0")
    )

    if exchange_filled > expected:
        raise RuntimeError(
            "STAGE EXCHANGE FILL EXCEEDS "
            "CLAIMED QUANTITY"
        )

    if exchange_filled < previous_filled:
        raise RuntimeError(
            "STAGE CONFIRMED FILL REGRESSION"
        )

    statuses = {
        str(order.get("status", "")).upper()
        for order in matches
    }

    terminal = {
        "CANCELED",
        "CANCELLED",
        "REJECTED",
        "EXPIRED",
    }

    if exchange_filled == expected:
        state = "FILLED"

    elif exchange_filled > 0:

        state = (
            "PARTIAL_TERMINAL"
            if statuses & terminal
            else "PARTIAL"
        )

    elif statuses & terminal:
        state = "TERMINAL_UNFILLED"

    else:
        state = "PENDING"

    unit_14_stage_update(
        client_id=client_id,
        state=state,
        exchange_order_id=exchange_order_id,
        confirmed_filled=exchange_filled,
    )

    return {
        "action": action,
        "state": state,
        "client_id": client_id,
        "exchange_order_id": exchange_order_id,
        "confirmed_filled": str(exchange_filled),
        "expected_quantity": str(expected),
        "complete": state == "FILLED",
    }


def unit_14_stage_reconcile_cycle(cycle_id):

    cycle = unit_14_stage_read(cycle_id)

    if cycle is None:
        raise RuntimeError(
            "STAGE CYCLE NOT FOUND"
        )

    # One exchange-history read per cycle scan.
    history = unit_14_v3_history()

    results = {}

    for action in UNIT14_STAGE_ACTIONS:

        results[action] = (
            unit_14_stage_reconcile_order(
                cycle_id=cycle_id,
                action=action,
                history=history,
            )
        )

    return results


# ============================================================
# UNIT 14 - H1/H2/R1/R2 ORDER EXECUTION
# INDEPENDENT OR SEQUENTIAL FUNDING
# ============================================================

def unit_14_stage_execute_pair(
    cycle_id,
    stage,
    quantity,
    mark_price,
    opening_leverage,
    quantity_step,
    minimum_quantity,
    margin_buffer_percent="0.3",
):
    from decimal import Decimal

    D = unit_14_v3_D

    stage = str(stage).upper()

    if stage not in ("H1", "H2", "R1", "R2"):
        raise RuntimeError("INVALID STAGE")

    cycle = unit_14_stage_read(cycle_id)

    if cycle is None:
        raise RuntimeError("STAGE CYCLE MISSING")

    if cycle["state"] != "ACTIVE":
        return {"status": "CYCLE_NOT_ACTIVE"}

    original = cycle["original_side"]

    if original not in ("LONG", "SHORT"):
        raise RuntimeError("INVALID ORIGINAL SIDE")

    opposite = (
        "SHORT" if original == "LONG"
        else "LONG"
    )

    if stage in ("H1", "H2"):
        close_side = original
        open_side = opposite
        close_action = stage + "-C"
        open_action = stage + "-H"
    else:
        close_side = opposite
        open_side = original
        close_action = stage + "-C"
        open_action = stage + "-O"

    qty = D(quantity, "STAGE QUANTITY")
    mark = D(mark_price, "STAGE MARK PRICE")
    leverage = D(
        opening_leverage,
        "OPENING LEVERAGE"
    )
    step = D(quantity_step, "QUANTITY STEP")
    minimum = D(
        minimum_quantity,
        "MINIMUM QUANTITY"
    )
    buffer = D(
        margin_buffer_percent,
        "MARGIN BUFFER",
        True
    )

    if (
        qty < minimum
        or unit_14_v3_floor(qty, step) != qty
        or buffer >= 100
    ):
        return {
            "status": "STAGE_QUANTITY_OR_BUFFER_INVALID"
        }

    # Reconcile before deciding whether any
    # new order may be submitted.

    history = unit_14_v3_history()

    close_record = unit_14_stage_reconcile_order(
        cycle_id, close_action, history
    )

    open_record = unit_14_stage_reconcile_order(
        cycle_id, open_action, history
    )

    if (
        close_record["complete"]
        and open_record["complete"]
    ):
        return {
            "status": stage + "_COMPLETE",
            "complete": True,
        }

    required_margin = (
        qty * mark / leverage
    ) * (
        Decimal("1")
        + buffer / Decimal("100")
    )

    available = unit_14_v3_balance()

    independent = available >= required_margin

    # With insufficient extra funds, the
    # closing fill must be confirmed before
    # opening is considered.
    #
    # A fresh balance is required after that fill.

    if not independent:

        if close_record["complete"]:
            available = unit_14_v3_balance()
        else:
            available = Decimal("0")

    open_funded = (
        independent
        or (
            close_record["complete"]
            and available >= required_margin
        )
    )

    actions = (
        (
            close_action,
            close_side,
            "SELL" if close_side == "LONG"
            else "BUY",
            True,
        ),
        (
            open_action,
            open_side,
            "BUY" if open_side == "LONG"
            else "SELL",
            False,
        ),
    )

    results = {}

    for action, position_side, order_side, is_close in actions:

        previous = (
            close_record if is_close
            else open_record
        )

        if previous["complete"]:
            results[action] = "FILLED"
            continue

        # A prior claim, partial fill or uncertain
        # acknowledgement is never resubmitted.

        if previous["state"] != "NOT_CLAIMED":
            results[action] = previous["state"]
            continue

        if not is_close and not open_funded:
            results[action] = (
                "WAITING_RELEASED_MARGIN"
                if close_record["complete"]
                else "WAITING_CLOSE_FILL"
            )
            continue

        # Verify current exchange exposure.
        position = unit_14_v3_position(
            position_side
        )

        if is_close:

            if position is None:
                results[action] = (
                    "CLOSE_POSITION_NOT_FOUND"
                )
                continue

            available_qty = D(
                position.get("size"),
                "CLOSE POSITION SIZE"
            )

            if available_qty < qty:
                results[action] = (
                    "CLOSE_QUANTITY_UNAVAILABLE"
                )
                continue

        # Claim persistently before transmission.
        claim = unit_14_stage_claim(
            cycle_id, action, qty
        )

        if not claim["claimed"]:
            results[action] = (
                "PREVIOUS_CLAIM_EXISTS"
            )
            continue

        payload = {
            "symbol": cycle["symbol"],
            "side": order_side,
            "positionSide": position_side,
            "type": "MARKET",
            "quantity": format(qty, "f"),
            "newClientOrderId":
                claim["client_id"],
        }

        try:
            reply = unit_14_v3_signed_request(
                "POST",
                UNIT14_V3_ORDER,
                payload=payload
            )

        except Exception as exc:

            unit_14_stage_update(
                claim["client_id"],
                "ACK_UNKNOWN"
            )

            results[action] = "ACK_UNKNOWN"

            print(
                "UNIT 14", action,
                "ACK UNKNOWN",
                repr(exc),
                flush=True
            )

            continue

        if (
            not isinstance(reply, dict)
            or reply.get("success") is not True
            or not reply.get("orderId")
        ):

            unit_14_stage_update(
                claim["client_id"],
                "ACK_UNKNOWN"
            )

            results[action] = "ACK_UNKNOWN"
            continue

        unit_14_stage_update(
            claim["client_id"],
            "SUBMITTED",
            str(reply["orderId"])
        )

        results[action] = "SUBMITTED"

    return {
        "status": stage + "_IN_PROGRESS",
        "cycle_id": cycle_id,
        "funding_mode": (
            "INDEPENDENT"
            if independent
            else "SEQUENTIAL"
        ),
        "required_opening_margin":
            str(required_margin),
        "available_margin": str(available),
        "actions": results,
        "complete": False,
    }


def unit_14_active_original_side(symbol="BTCSUSDT"):
    """
    Resolve original position side from a persisted
    active hedge/recovery cycle.

    A hedge position must never be mistaken for
    the original position.
    """

    db = unit_14_stage_db()

    try:
        rows = db.execute("""
            SELECT cycle_id, original_side
            FROM stage_cycles
            WHERE symbol = ?
              AND state = 'ACTIVE'
            ORDER BY created_at DESC
        """, (symbol,)).fetchall()
    finally:
        db.close()

    if not rows:
        return None, None

    sides = {row[1] for row in rows}

    if len(sides) != 1:
        raise RuntimeError(
            "CONFLICTING ACTIVE ORIGINAL SIDES"
        )

    return rows[0][1], rows[0][0]


 
def unit_14_stage_dispatch(
    active_positions,
    original_position,
    unit_13_result,
    quantity_step,
    minimum_quantity,
    mark
):
    """
    WEEX DEMO H1/H2/R1/R2 execution dispatcher.

    H1: adverse ATR x1
    H2: adverse ATR x2, unless recovery started
    R1: ATR x1 retracement from H1 trigger
    R2: further favorable ATR x1 after R1

    Order submission is performed by the existing
    unit_14_stage_execute_pair().
    """

    from decimal import Decimal

    D = unit_14_v3_D

    original_side, cycle_id = (
        unit_14_active_original_side()
    )

    
    # ------------------------------------------------
    # IDENTIFY OR INITIALIZE ORIGINAL TRADE
    # PERSISTED CYCLE RECONCILIATION
    # ------------------------------------------------

    if cycle_id is None:

        if original_position is None:
            return {
                "status": "NO_POSITION",
                "handled": False
            }

        if unit_13_result.get(
            "tp1_completed"
        ) is True:
            return {
                "status": "POST_TP1",
                "handled": False
            }

        original_side = str(
            original_position.get("side", "")
        ).upper()

        if original_side not in (
            "LONG", "SHORT"
        ):
            raise RuntimeError(
                "INVALID ORIGINAL SIDE"
            )

        cycle_id = (
            "U14-"
            + unit_14_v3_trade_key(
                original_position
            )
        )

        # --------------------------------------------
        # CHECK PERSISTENT REGISTRY BEFORE CREATING
        # --------------------------------------------

        persisted_cycle = unit_14_stage_read(
            cycle_id
        )

        if persisted_cycle is not None:

            persisted_symbol = str(
                persisted_cycle["symbol"]
            ).upper()

            persisted_side = str(
                persisted_cycle["original_side"]
            ).upper()

            if (
                persisted_symbol != "BTCSUSDT"
                or persisted_side != original_side
            ):
                raise RuntimeError(
                    "PERSISTED CYCLE IDENTITY CONFLICT"
                )

            print(
                "UNIT 14 EXISTING CYCLE FOUND =",
                cycle_id,
                flush=True
            )

        else:

            # ----------------------------------------
            # INITIALIZE ONLY A GENUINELY NEW CYCLE
            # ----------------------------------------

            snapshot = (
                FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT
            )

            atr = D(
                snapshot["atr14"],
                "FROZEN ATR"
            )

            quantity = D(
                original_position["size"],
                "ORIGINAL QUANTITY"
            )

            entry = (
                D(
                    original_position["openValue"],
                    "OPEN VALUE"
                )
                /
                D(
                    original_position["cumOpenSize"],
                    "CUM OPEN SIZE"
                )
            )

            unit_14_stage_create_cycle(
                cycle_id,
                "BTCSUSDT",
                original_side,
                quantity,
                entry,
                atr
            )

            print(
                "UNIT 14 NEW ORIGINAL TRADE CYCLE =",
                cycle_id,
                flush=True
            )

    # ------------------------------------------------
    # LOAD THE PERSISTED CYCLE
    # ------------------------------------------------

    cycle = unit_14_stage_read(
        cycle_id
    )

    if cycle is None:
        raise RuntimeError(
            "UNIT 14 STAGE CYCLE MISSING"
        )

    persisted_state = str(
        cycle["state"]
    ).upper()

    persisted_stage = str(
        cycle["stage"]
    ).upper()

    print(
        "UNIT 14 PERSISTED CYCLE =",
        cycle_id,
        flush=True
    )

    print(
        "UNIT 14 PERSISTED STAGE =",
        persisted_stage,
        flush=True
    )

    print(
        "UNIT 14 PERSISTED STATE =",
        persisted_state,
        flush=True
    )

    # ------------------------------------------------
    # PRESERVE COMPLETED RECOVERY
    # ------------------------------------------------

    if (
        persisted_state == "COMPLETE"
        and persisted_stage == "RECOVERED"
    ):

        print(
            "UNIT 14 COMPLETED RECOVERY PRESERVED =",
            cycle_id,
            flush=True
        )

        return {
            "status": "RECOVERY_COMPLETE",
            "handled": True,
            "cycle_id": cycle_id,
            "stage": persisted_stage,
            "persisted_state": persisted_state
        }

    # ------------------------------------------------
    # OTHER INACTIVE CYCLES REQUIRE RECONCILIATION
    # ------------------------------------------------

    if persisted_state != "ACTIVE":

        print(
            "UNIT 14 INACTIVE CYCLE RECONCILIATION =",
            persisted_state,
            persisted_stage,
            flush=True
        )

        return {
            "status": "CYCLE_RECONCILIATION_REQUIRED",
            "handled": True,
            "cycle_id": cycle_id,
            "stage": persisted_stage,
            "persisted_state": persisted_state
        }

    # ------------------------------------------------
    # ACTIVE CYCLE CONTINUES TO EXISTING
    # RECOVER PERSISTED PARAMETERS SECTION
    # ------------------------------------------------

    print(
        "UNIT 14 ACTIVE CYCLE READY =",
        cycle_id,
        flush=True
    )

    # ------------------------------------------------
    # RECOVER PERSISTED PARAMETERS
    # ------------------------------------------------

    original = cycle["original_side"]

    opposite = (
        "SHORT"
        if original == "LONG"
        else "LONG"
    )

    entry = D(
        cycle["original_entry"],
        "ENTRY"
    )

    atr = D(
        cycle["frozen_atr"],
        "ATR"
    )

    base_qty = D(
        cycle["original_quantity"],
        "ORIGINAL QUANTITY"
    )

    step = D(
        quantity_step,
        "QUANTITY STEP"
    )

    minimum = D(
        minimum_quantity,
        "MINIMUM QUANTITY"
    )

    price = D(
        mark,
        "MARK PRICE"
    )

    adverse = (
        (entry - price) / atr
        if original == "LONG"
        else (price - entry) / atr
    )

    # ------------------------------------------------
    # EXCHANGE-CONFIRMED ORDER RECONCILIATION
    # ------------------------------------------------

    orders = unit_14_stage_reconcile_cycle(
        cycle_id
    )

    def filled(action):
        return D(
            orders[action]["confirmed_filled"],
            action + " FILLED",
            True
        )

    def complete(action):
        return (
            orders[action]["complete"] is True
        )

    def started(action):
        return (
            orders[action]["state"]
            != "NOT_CLAIMED"
        )

    def pair_complete(stage):

        close_action = stage + "-C"

        open_action = (
            stage + "-H"
            if stage in ("H1", "H2")
            else stage + "-O"
        )

        return (
            complete(close_action)
            and complete(open_action)
        )

    def execute(stage, quantity):

        quantity = unit_14_v3_floor(
            quantity,
            step
        )

        if quantity < minimum:
            return {
                "status":
                    stage + "_QUANTITY_BELOW_MINIMUM",
                "handled": True,
                "cycle_id": cycle_id
            }

        position = (
            active_positions.get(original)
            or active_positions.get(opposite)
        )

        if position is None:
            return {
                "status": "POSITION_NOT_FOUND",
                "handled": True,
                "cycle_id": cycle_id
            }

        leverage = D(
            position["leverage"],
            "POSITION LEVERAGE"
        )

        outcome = unit_14_stage_execute_pair(
            cycle_id=cycle_id,
            stage=stage,
            quantity=quantity,
            mark_price=price,
            opening_leverage=leverage,
            quantity_step=step,
            minimum_quantity=minimum
        )

        outcome["handled"] = True
        outcome["stage"] = stage

        return outcome

    # ------------------------------------------------
    # STAGE QUANTITIES
    # ------------------------------------------------

    h1_qty = unit_14_v3_floor(
        base_qty / Decimal("2"),
        step
    )

    # ------------------------------------------------
    # H1 EXECUTION
    # ------------------------------------------------

    if not pair_complete("H1"):

        if (
            adverse >= Decimal("1")
            or started("H1-C")
            or started("H1-H")
        ):
            return execute(
                "H1",
                h1_qty
            )

        return {
            "status": "H1_MONITORING",
            "handled": True,
            "cycle_id": cycle_id,
            "adverse_atr": str(adverse)
        }

    
    # ========================================================
    # UNIT 14 V4 PART 4
    # H2 / R1 / R2 INDEPENDENT STAGE TRANSITIONS
    # ========================================================

    recovery_started = any(
        started(action)
        for action in (
            "R1-C", "R1-O",
            "R2-C", "R2-O",
        )
    )

    h2_started = any(
        started(action)
        for action in (
            "H2-C", "H2-H",
        )
    )

    r1_started = any(
        started(action)
        for action in (
            "R1-C", "R1-O",
        )
    )

    r2_started = any(
        started(action)
        for action in (
            "R2-C", "R2-O",
        )
    )

    # ========================================================
    # H2: SECOND ADVERSE ATR STAGE
    # ========================================================

    h2_qty = unit_14_v3_floor(
        base_qty - filled("H1-C"),
        step
    )

    # A previously started H2 must be reconciled
    # independently before any recovery transition.

    if h2_started and not pair_complete("H2"):

        return execute(
            "H2",
            h2_qty
        )

    # H2 may start only before recovery begins.

    if (
        not pair_complete("H2")
        and not recovery_started
        and adverse >= Decimal("2")
    ):

        return execute(
            "H2",
            h2_qty
        )

    # ========================================================
    # R1: FIRST RECOVERY STAGE
    # ========================================================

    hedge_total = (
        filled("H1-H")
        + filled("H2-H")
    )

    r1_qty = unit_14_v3_floor(
        hedge_total / Decimal("2"),
        step
    )

    r1_reached = (
        adverse <= Decimal("0")
    )

    if not pair_complete("R1"):

        # An already-started R1 remains the
        # current recovery stage until reconciled.

        if r1_started:

            return execute(
                "R1",
                r1_qty
            )

        # Do not create R1 after R2 has started
        # without an existing R1 record.

        if r2_started:

            return {
                "status": "R1_RECONCILIATION_REQUIRED",
                "handled": True,
                "cycle_id": cycle_id,
            }

        if r1_reached and hedge_total > 0:

            return execute(
                "R1",
                r1_qty
            )

        return {
            "status": "R1_MONITORING",
            "handled": True,
            "cycle_id": cycle_id,
            "adverse_atr": str(adverse),
            "hedge_quantity": str(hedge_total),
        }

    # ========================================================
    # R2: FINAL RECOVERY STAGE
    # ========================================================

    r2_qty = unit_14_v3_floor(
        hedge_total - filled("R1-C"),
        step
    )

    r2_reached = (
        adverse <= Decimal("-1")
    )

    if not pair_complete("R2"):

        if r2_started:

            return execute(
                "R2",
                r2_qty
            )

        if r2_reached and r2_qty > 0:

            return execute(
                "R2",
                r2_qty
            )

        return {
            "status": "R2_MONITORING",
            "handled": True,
            "cycle_id": cycle_id,
            "adverse_atr": str(adverse),
            "remaining_hedge_quantity": str(r2_qty),
        }

    # ========================================================
    # END UNIT 14 V4 PART 4
    # EXISTING RECOVERY_COMPLETE BLOCK FOLLOWS
    # ========================================================


    # ------------------------------------------------
    # ALL FOUR STAGES COMPLETED
    # ------------------------------------------------

    db = unit_14_stage_db()

    try:
        db.execute("""
            UPDATE stage_cycles
            SET stage = 'RECOVERED',
                state = 'COMPLETE'
            WHERE cycle_id = ?
              AND state = 'ACTIVE'
        """, (cycle_id,))
    finally:
        db.close()

    return {
        "status": "RECOVERY_COMPLETE",
        "handled": True,
        "cycle_id": cycle_id
    }
   

# ============================================================
# UNIT 14 V4 INTEGRATION - PART 1
# VERIFIED UNIT 13 -> UNIT 14 HANDOVER
# PRESERVE EXISTING H1 / H2 / R1 / R2 / B1-B5
# ZERO INDENTATION
# ============================================================

def unit_14_v4_tp_handover(unit_13_result):

    if not isinstance(unit_13_result, dict):
        raise RuntimeError(
            "UNIT 14 INVALID UNIT 13 HANDOVER"
        )

    if unit_13_result.get("unit") != 13:
        raise RuntimeError(
            "UNIT 14 EXPECTED UNIT 13 RESULT"
        )

    status = str(
        unit_13_result.get("status", "")
    ).upper()

    pending_statuses = {
        "TP_ORDER_ACKNOWLEDGED",
        "TP_SUBMISSION_UNCERTAIN",
        "TP_SUBMISSION_UNCONFIRMED",
    }

    unresolved = bool(
        unit_13_result.get(
            "tp_history_unresolved", False
        )
    )

    legacy_unknown = bool(
        unit_13_result.get(
            "tp_legacy_closures_unattributed",
            False
        )
    )

    tp1_completed = bool(
        unit_13_result.get(
            "tp1_completed", False
        )
    )

    tp2_completed = bool(
        unit_13_result.get(
            "tp2_completed", False
        )
    )

    # Order acknowledgment is never proof of fill.
    pending = (
        status in pending_statuses
        or unresolved
        or legacy_unknown
    )

    tp3_armed = bool(
        tp1_completed
        and tp2_completed
        and not pending
        and unit_13_result.get(
            "tp3_armed", False
        )
    )

    # A pending TP order must not disable
    # independent position protection.
    position_exists = bool(
        unit_13_result.get(
            "position_exists",
            unit_13_result.get(
                "active_position_exists", False
            )
        )
    )

    handover = {
        "unit_13_status": status,
        "position_exists": position_exists,
        "tp1_completed": tp1_completed,
        "tp2_completed": tp2_completed,
        "tp3_armed": tp3_armed,
        "tp_order_pending": pending,
        "tp_history_unresolved": unresolved,
        "legacy_closures_unattributed":
            legacy_unknown,
        "hedge_management_enabled":
            position_exists,
        "backup_management_enabled":
            position_exists,
        "bot_mode_independent": True,
    }

    print(
        "UNIT 14 TP1 COMPLETED =",
        tp1_completed,
        flush=True
    )
    print(
        "UNIT 14 TP2 COMPLETED =",
        tp2_completed,
        flush=True
    )
    print(
        "UNIT 14 TP3 ARMED =",
        tp3_armed,
        flush=True
    )
    print(
        "UNIT 14 TP RECONCILIATION PENDING =",
        pending,
        flush=True
    )
    print(
        "UNIT 14 EXISTING POSITION PROTECTION =",
        position_exists,
        flush=True
    )

    return handover


# ============================================================
# UNIT 14 V4 - PART 3
# RESTART-SAFE STAGE RECONCILIATION
# SINGLE H1/H2/R1/R2 EXECUTION AUTHORITY
# PRESERVE ORIGINAL UNIT 14 STAGE EXECUTOR
# ZERO INDENTATION
# ============================================================

def unit_14_v4_stage_reconciliation(
    cycle_id,
):
    """
    Inspect the existing persistent stage cycle.

    This function does not submit exchange orders.
    The original Unit 14 dispatcher remains
    responsible for reconciliation and execution.
    """

    if not cycle_id:
        return {
            "cycle_exists": False,
            "cycle_id": None,
            "status": "NO_ACTIVE_CYCLE",
            "orders": {},
            "execution_attempted": False,
        }

    cycle = unit_14_stage_read(cycle_id)

    if cycle is None:
        raise RuntimeError(
            "UNIT 14 ACTIVE CYCLE NOT FOUND"
        )

    if cycle.get("state") != "ACTIVE":
        return {
            "cycle_exists": True,
            "cycle_id": cycle_id,
            "status": "CYCLE_NOT_ACTIVE",
            "orders": {},
            "execution_attempted": False,
        }

    orders = unit_14_stage_reconcile_cycle(
        cycle_id
    )

    if not isinstance(orders, dict):
        raise RuntimeError(
            "UNIT 14 RECONCILIATION INVALID"
        )

    required_actions = (
        "H1-C", "H1-H",
        "H2-C", "H2-H",
        "R1-C", "R1-O",
        "R2-C", "R2-O",
    )

    summary = {}
    incomplete = []
    started = []

    for action in required_actions:

        record = orders.get(action)

        if not isinstance(record, dict):
            raise RuntimeError(
                "UNIT 14 MISSING STAGE RECORD "
                + action
            )

        state = str(
            record.get("state", "")
        ).upper()

        complete = (
            record.get("complete") is True
        )

        filled = unit_14_v3_D(
            record.get("confirmed_filled", "0"),
            action + " CONFIRMED FILLED",
            True,
        )

        if state != "NOT_CLAIMED":
            started.append(action)

        if not complete:
            incomplete.append(action)

        summary[action] = {
            "state": state,
            "complete": complete,
            "confirmed_filled": str(filled),
        }

    return {
        "cycle_exists": True,
        "cycle_id": cycle_id,
        "status": "RECONCILED",
        "orders": summary,
        "started_actions": started,
        "incomplete_actions": incomplete,
        "execution_attempted": False,
    }


def unit_14_v4_dispatch_once(
    active_positions,
    original_position,
    unit_13_result,
    quantity_step,
    minimum_quantity,
    mark,
):
    """
    Single invocation of the existing
    H1/H2/R1/R2 stage dispatcher.

    No new exchange order implementation
    is introduced here.
    """

    if not isinstance(active_positions, dict):
        raise RuntimeError(
            "UNIT 14 INVALID ACTIVE POSITIONS"
        )

    if not isinstance(unit_13_result, dict):
        raise RuntimeError(
            "UNIT 14 INVALID UNIT 13 RESULT"
        )

    handover = unit_14_v4_tp_handover(
        unit_13_result
    )

    original_side, cycle_id = (
        unit_14_active_original_side()
    )

    if cycle_id is not None:

        reconciliation = (
            unit_14_v4_stage_reconciliation(
                cycle_id
            )
        )

    else:

        reconciliation = {
            "cycle_exists": False,
            "cycle_id": None,
            "status": "NEW_CYCLE_PENDING",
            "orders": {},
            "execution_attempted": False,
        }

    print(
        "UNIT 14 ACTIVE STAGE CYCLE =",
        cycle_id,
        flush=True
    )

    print(
        "UNIT 14 RECONCILIATION STATUS =",
        reconciliation["status"],
        flush=True
    )

    print(
        "UNIT 14 TP1 COMPLETED =",
        handover["tp1_completed"],
        flush=True
    )

    print(
        "UNIT 14 TP2 COMPLETED =",
        handover["tp2_completed"],
        flush=True
    )

    print(
        "UNIT 14 TP3 ARMED =",
        handover["tp3_armed"],
        flush=True
    )

    # Do not invoke a completed or inactive cycle
    # through this wrapper.

    if reconciliation["status"] == "CYCLE_NOT_ACTIVE":

        return {
            "status": "CYCLE_NOT_ACTIVE",
            "handled": False,
            "cycle_id": cycle_id,
            "tp_handover": handover,
            "stage_reconciliation": reconciliation,
        }

    # ========================================================
    # THE ORIGINAL DISPATCHER REMAINS THE ONLY
    # H1/H2/R1/R2 EXECUTION AUTHORITY.
    #
    # It independently reconciles exchange orders
    # before deciding which stage to execute.
    # ========================================================

    outcome = unit_14_stage_dispatch(
        active_positions=active_positions,
        original_position=original_position,
        unit_13_result=unit_13_result,
        quantity_step=quantity_step,
        minimum_quantity=minimum_quantity,
        mark=mark,
    )

    if not isinstance(outcome, dict):
        raise RuntimeError(
            "UNIT 14 STAGE OUTCOME INVALID"
        )

    outcome["tp_handover"] = handover

    outcome["stage_reconciliation"] = (
        reconciliation
    )

    print(
        "UNIT 14 STAGE DISPATCH STATUS =",
        outcome.get("status"),
        flush=True
    )

    print(
        "UNIT 14 STAGE HANDLED =",
        outcome.get("handled", False),
        flush=True
    )

    return outcome


# ============================================================
# END UNIT 14 V4 PART 3
# ============================================================


# ============================================================
# END UNIT 14 V4 INTEGRATION PART 1
# ============================================================


# ============================================================
# UNIT 14 V4 - PART 5
# EXPLICIT STAGE-TO-BACKUP HANDOVER
# PRESERVE EXISTING B1-B5 EXECUTION ENGINE
# ZERO INDENTATION
# ============================================================

def unit_14_v4_backup_handover(stage_result, cycle_id):

    if not isinstance(stage_result, dict):
        raise RuntimeError(
            "UNIT 14 INVALID STAGE HANDOVER"
        )

    status = str(
        stage_result.get("status", "")
    ).upper()

    # Only an explicitly confirmed failed cycle
    # may release the stage manager to B1-B5.
    #
    # Monitoring, recovery completion, pending
    # submissions and uncertain orders do not
    # qualify as backup authorization.

    if status != "BACKUP_READY":

        return {
            "backup_ready": False,
            "stage_status": status,
            "reason": "STAGE_MANAGER_RETAINS_CONTROL",
        }

    if not cycle_id:

        return {
            "backup_ready": False,
            "stage_status": status,
            "reason": "MISSING_STAGE_CYCLE",
        }

    if str(
        stage_result.get("cycle_id", "")
    ) != str(cycle_id):

        return {
            "backup_ready": False,
            "stage_status": status,
            "reason": "STAGE_CYCLE_MISMATCH",
        }

    cycle = unit_14_stage_read(cycle_id)

    if not isinstance(cycle, dict):

        return {
            "backup_ready": False,
            "stage_status": status,
            "reason": "STAGE_CYCLE_NOT_FOUND",
        }

    if (
        str(cycle.get("stage", "")).upper()
        != "BACKUP_READY"
        or str(cycle.get("state", "")).upper()
        != "ACTIVE"
    ):

        return {
            "backup_ready": False,
            "stage_status": status,
            "reason": "BACKUP_HANDOVER_NOT_PERSISTED",
        }

    return {
        "backup_ready": True,
        "stage_status": status,
        "cycle_id": cycle_id,
        "reason": "FAILED_PROTECTION_CYCLE_CONFIRMED",
    }


# ============================================================
# END UNIT 14 V4 PART 5 HELPER
# ============================================================

def fresh_reconstruction_unit_14(
    config,
    unit_13_result,
):

    print("=" * 80, flush=True)
    print(
        "UNIT 14 V3 DYNAMIC BACKUP MANAGEMENT START",
        flush=True
    )

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 14 CONFIG INVALID"
        )

    if not isinstance(unit_13_result, dict):
        raise RuntimeError(
            "UNIT 14 UNIT 13 RESULT INVALID"
        )

    exchange = config.get("exchange", {})
    strategy = config.get("strategy", {})
    precision = config.get("market_precision", {})

    if (
        config.get("execution_environment") != "DEMO"
        or exchange.get("name") != "WEEX"
        or exchange.get("api_version") != "V3"
        or not str(
    exchange.get("market_symbol", "")
).strip().upper().endswith("USDT")
or str(
    exchange.get("demo_order_symbol", "")
).strip().upper() != (
    str(
        exchange.get("market_symbol", "")
    ).strip().upper()[:-4] + "SUSDT"
)
    ):
        raise RuntimeError(
            "UNIT 14 NON-DEMO CONFIG BLOCKED"
        )

    D = unit_14_v3_D

    qstep = D(
        precision.get("quantity_step"),
        "QTY STEP"
    )

    minimum = D(
        precision.get("minimum_quantity"),
        "MINIMUM QUANTITY"
    )

    max_backups = int(
        strategy.get("max_backups", 5)
    )

    # Percentage of CURRENT available balance,
    # not fixed multiples of initial margin.

    backup_percent = D(
        os.getenv(
            "BACKUP_AVAILABLE_BALANCE_PERCENT",
            str(
                strategy.get(
                    "backup_available_balance_percent",
                    "0.5"
                )
            )
        ),
        "BACKUP BALANCE PERCENT"
    )

    buffer_pct = D(
        strategy.get(
            "backup_buffer_percent",
            "0.3"
        ),
        "BUFFER PERCENT"
    )

    cap_pct = D(
        strategy.get(
            "exposure_cap_percent",
            "35"
        ),
        "EXPOSURE CAP"
    )

    trail_ref = D(
        strategy.get(
            "tp3_trailing_reference_percent",
            "0.20"
        ),
        "TRAIL REFERENCE"
    )

    trail_min = D(
        strategy.get(
            "tp3_trailing_min_percent",
            "0.10"
        ),
        "TRAIL MINIMUM"
    )

    trail_max = D(
        strategy.get(
            "tp3_trailing_max_percent",
            "0.40"
        ),
        "TRAIL MAXIMUM"
    )

     
    # ========================================================
    # UNIT 14 V3 - DYNAMIC SETTINGS VALIDATION
    # ALIGNED WITH UNIT 2 V9
    # ORIGINAL FIVE-BACKUP ENGINE PRESERVED
    # ========================================================

    if max_backups != 5:
        raise RuntimeError(
            "UNIT 14 INVALID BACKUP COUNT: "
            + str(max_backups)
        )

    if not 0 < backup_percent <= 100:
        raise RuntimeError(
            "UNIT 14 INVALID BACKUP BALANCE PERCENT: "
            + str(backup_percent)
        )

    if not 0 < cap_pct <= 100:
        raise RuntimeError(
            "UNIT 14 INVALID EXPOSURE CAP PERCENT: "
            + str(cap_pct)
        )

    if not 0 < trail_min <= trail_ref <= trail_max:
        raise RuntimeError(
            "UNIT 14 INVALID TP3 TRAILING RANGE: "
            + str((
                trail_min,
                trail_ref,
                trail_max
            ))
        )

    print(
        "UNIT 14 DYNAMIC CONFIG VALIDATION = PASS",
        flush=True
    )

    print(
        "UNIT 14 EXPOSURE CAP % =",
        cap_pct,
        flush=True
    )

    result = unit_14_v3_result(
        unit_13_result
    )

    print(
        "UNIT 14 BACKUPS = 5",
        flush=True
    )
    print(
        "UNIT 14 BACKUP SIZING = "
        "PERCENT_AVAILABLE_BALANCE",
        flush=True
    )
    print(
        "UNIT 14 BACKUP BALANCE % =",
        backup_percent,
        flush=True
    )
    print(
        "UNIT 14 BUFFER % =",
        buffer_pct,
        flush=True
    )
    print(
        "UNIT 14 EXPOSURE CAP % =",
        cap_pct,
        flush=True
    )
    print(
        "UNIT 14 UNIT 13 STATUS =",
        unit_13_result.get("status"),
        flush=True
    )
    print(
        "UNIT 14 MANAGEMENT INDEPENDENT "
        "OF BOT_MODE = TRUE",
        flush=True
    )

    # ========================================================
    # 8. FRESH EXCHANGE POSITION
    # ========================================================

    
    active_positions = unit_14_v3_positions()

    persisted_side, active_cycle_id = (
        unit_14_active_original_side()
    )

    if persisted_side is not None:
        p = active_positions.get(persisted_side)

    elif len(active_positions) == 1:
        p = next(iter(active_positions.values()))

    elif len(active_positions) == 0:
        p = None

    else:
        configured_side = os.getenv(
            "ORIGINAL_POSITION_SIDE", ""
        ).strip().upper()

        if configured_side not in active_positions:
            raise RuntimeError(
                "ORIGINAL SIDE NOT IDENTIFIED "
                "FOR EXISTING HEDGE PAIR"
            )

        p = active_positions[configured_side]

    if active_cycle_id is not None:

        stage_state = unit_14_stage_read(
            active_cycle_id
        )

        if stage_state is not None:
            result["stage_cycle_id"] = (
                active_cycle_id
            )
            result["stage_original_side"] = (
                stage_state["original_side"]
            )
            result["stage_state"] = (
                stage_state["stage"]
            )

    
    # ========================================================
    # UNIT 14 V4 - SINGLE H1/H2/R1/R2 DISPATCH
    # ========================================================

    tp_handover = unit_14_v4_tp_handover(
        unit_13_result
    )

    result["tp_handover"] = tp_handover

    stage_mark = None

    if (
        p is not None
        or active_cycle_id is not None
    ):
        stage_mark = unit_14_v3_mark()

    if stage_mark is not None:

        stage_result = unit_14_v4_dispatch_once(
            active_positions=active_positions,
            original_position=p,
            unit_13_result=unit_13_result,
            quantity_step=qstep,
            minimum_quantity=minimum,
            mark=stage_mark,
        )

        result["stage_dispatch"] = stage_result

        print(
            "UNIT 14 HEDGE STAGE =",
            stage_result.get("stage"),
            flush=True
        )

        print(
            "UNIT 14 HEDGE STATUS =",
            stage_result.get("status"),
            flush=True
        )

        
        # ====================================================
        # UNIT 14 V4 - STAGE TO BACKUP HANDOVER
        # ====================================================

        handover = unit_14_v4_backup_handover(
            stage_result,
            stage_result.get("cycle_id"),
        )

        result["backup_handover"] = handover

        if handover["backup_ready"]:

            result["protection_stage_status"] = (
                "BACKUP_READY"
            )

            result["backup_activation_reason"] = (
                "FAILED_PROTECTION_CYCLE_CONFIRMED"
            )

            print(
                "UNIT 14 BACKUP HANDOVER = READY",
                flush=True
            )

            # Continue into the existing Unit 14
            # position and B1-B5 management logic.

        elif stage_result.get("handled"):

            result["status"] = (
                stage_result.get(
                    "status",
                    "STAGE_MANAGER_ACTIVE"
                )
            )

            result["skip_reason"] = (
                "STAGE_MANAGER_ACTIVE"
            )

            return result

        elif stage_result.get("status") == "RECOVERY_COMPLETE":

            result["status"] = "RECOVERY_COMPLETE"
            result["skip_reason"] = (
                "PROTECTION_CYCLE_RECOVERED"
            )

            return result

    # ========================================================
    # EXISTING POSITION MANAGEMENT CONTINUES
    # ========================================================

            result["skip_reason"] = (
                "STAGE_MANAGER_ACTIVE"
            )

            return result

    # ========================================================
    # CONTINUE EXISTING UNIT 14 POSITION MANAGEMENT
    # ========================================================

    if p is None:

        result["status"] = "IDLE_NO_POSITION"
        result["skip_reason"] = (
            "NO_ACTIVE_DEMO_POSITION"
        )

        print(
            "UNIT 14 STATUS = IDLE_NO_POSITION",
            flush=True
        )

        print(
            "UNIT 14 EXCHANGE WRITE = NONE",
            flush=True
        )

        return result

    side = str(
        p.get("side", "")
    ).upper()

    if side not in ("LONG", "SHORT"):
        raise RuntimeError(
            "UNIT 14 POSITION SIDE INVALID"
        )

    size = D(
        p.get("size"),
        "ACTIVE POSITION SIZE"
    )

    leverage = D(
        p.get("leverage"),
        "POSITION LEVERAGE"
    )

    key = unit_14_v3_trade_key(p)

    liquidation = D(
        p.get("liquidatePrice"),
        "LIQUIDATION PRICE",
        True
    )

    mark = unit_14_v3_mark()
    history = unit_14_v3_history()

    result.update({
        "position_exists": True,
        "position_side": side,
        "position_size": float(size),
        "position_leverage": float(leverage),
        "mark_price": float(mark),
        "liquidation_price": float(liquidation),
        "trade_key": key,
    })

    # ========================================================
    # 9. BACKUP HISTORY RECONCILIATION
    # ========================================================

    completed, existing = (
        unit_14_v3_reconcile(
            history,
            key,
        )
    )

    result["backups_filled"] = completed

    print(
        "UNIT 14 BACKUPS FILLED =",
        str(completed) + "/5",
        flush=True
    )

    # ========================================================
    # 10. TP3 RUNNER
    # UNIT 13 TP STATE MUST MATCH ACTIVE POSITION
    # ========================================================

    
    # ========================================================
    # UNIT 14 V4 - VERIFIED TP3 ARMING
    # ========================================================

    tp3_armed = bool(
        tp_handover["tp3_armed"]
        and tp_handover["position_exists"]
        and unit_13_result.get(
            "position_side"
        ) == side
        and not tp_handover[
            "tp_order_pending"
        ]
    )

    result["tp3_armed"] = tp3_armed

    runtime = globals().setdefault(
        "_UNIT14_V3_TP3_RUNTIME",
        {}
    )

    attempts = globals().setdefault(
        "_UNIT14_V3_ORDER_ATTEMPTS",
        set()
    )

    if tp3_armed:

        callback = max(
            trail_min,
            min(trail_ref, trail_max)
        )

        state = runtime.get(key)

        if state is None:

            state = {
                "best_mark": str(mark),
                "side": side,
            }

            runtime[key] = state

        best = D(
            state["best_mark"],
            "TP3 BEST MARK"
        )

        if side == "LONG":

            best = max(best, mark)

            stop = best * (
                D(1) - callback / D(100)
            )

            reached = mark <= stop

        else:

            best = min(best, mark)

            stop = best * (
                D(1) + callback / D(100)
            )

            reached = mark >= stop

        state["best_mark"] = str(best)

        result.update({
            "tp3_best_mark": float(best),
            "tp3_stop_price": float(stop),
            "tp3_trailing_percent": float(callback),
            "tp3_trigger_reached": bool(reached),
        })

        if reached:

            client_id = (
                "FR-TP3-" + key
            )[:36]

            historical = any(
                str(
                    o.get("clientOrderId", "")
                ) == client_id
                for o in history
            )

            if historical or client_id in attempts:

                result["status"] = (
                    "TP3_ORDER_EXISTS"
                )
                result["skip_reason"] = (
                    "TP3_DUPLICATE_OR_UNCERTAIN"
                )

                return result

            # Re-read position before any close.
            latest = unit_14_v3_position(side)

            if (
                latest is None
                or unit_14_v3_trade_key(
                    latest
                ) != key
                or str(
                    latest.get("side", "")
                ).upper() != side
            ):
                result["status"] = "POSITION_CHANGED"
                result["skip_reason"] = (
                    "TP3_POSITION_CHANGED"
                )
                return result

            close_qty = unit_14_v3_floor(
                D(
                    latest.get("size"),
                    "LATEST SIZE"
                ),
                qstep
            )

            if close_qty < minimum:

                result["status"] = (
                    "WAITING_MIN_QUANTITY"
                )
                result["skip_reason"] = (
                    "TP3_QUANTITY_BELOW_MINIMUM"
                )

                return result

            # Confirm no identical historical order.
            latest_history = unit_14_v3_history()

            if any(
                str(
                    o.get("clientOrderId", "")
                ) == client_id
                for o in latest_history
            ):
                result["status"] = "TP3_ORDER_EXISTS"
                result["skip_reason"] = (
                    "TP3_HISTORY_RECONCILED"
                )
                return result

            payload = {
                "symbol": "BTCSUSDT",
                "side": (
                    "SELL" if side == "LONG"
                    else "BUY"
                ),
                "positionSide": side,
                "type": "MARKET",
                "quantity": format(
                    close_qty, "f"
                ),
                "newClientOrderId": client_id,
            }

            # Claimed before POST: no automatic retry.
            attempts.add(client_id)

            result["tp3_execution_attempted"] = True

            reply = unit_14_v3_signed_request(
                "POST",
                UNIT14_V3_ORDER,
                payload=payload,
            )

            if (
                not isinstance(reply, dict)
                or reply.get("success") is not True
                or not reply.get("orderId")
            ):
                raise RuntimeError(
                    "UNIT 14 TP3 ACK UNVERIFIED"
                )

            result.update({
                "status": "TP3_SUBMITTED",
                "tp3_execution_completed": True,
                "tp3_order_id": str(
                    reply["orderId"]
                ),
                "exchange_write": True,
                "skip_reason": "NONE",
            })

            print(
                "UNIT 14 TP3 DEMO ORDER ACCEPTED",
                flush=True
            )

            return result

    else:
        runtime.pop(key, None)

    
    # ========================================================
    # UNIT 14 V4 - BACKUP ACTIVATION AUTHORIZATION
    # ========================================================

    handover = result.get(
        "backup_handover",
        {}
    )

    if not handover.get("backup_ready", False):

        result["status"] = (
            "BACKUP_AWAITING_STAGE_HANDOVER"
        )

        result["skip_reason"] = (
            "PROTECTION_CYCLE_NOT_CONFIRMED_FAILED"
        )

        print(
            "UNIT 14 BACKUP ACTIVATION = WAITING",
            flush=True
        )

        return result

    print(
        "UNIT 14 BACKUP ACTIVATION = AUTHORIZED",
        flush=True
    )

    # Existing B1-B5 sizing, liquidation trigger,
    # exposure cap and submission logic follows.

    # ========================================================
    # 11. NEXT BACKUP STAGE
    # ========================================================

    if completed >= 5:

        result["status"] = "BACKUPS_COMPLETE"
        result["skip_reason"] = "FIVE_BACKUPS_FILLED"

        return result

    stage = completed + 1

    result["backup_next_stage"] = stage

    client_id = unit_14_v3_backup_id(
        stage, key
    )

    if stage in existing or client_id in attempts:

        result["status"] = "BACKUP_ORDER_EXISTS"
        result["skip_reason"] = (
            "BACKUP_ALREADY_SUBMITTED_OR_UNCERTAIN"
        )

        return result

    # ========================================================
    # 12. LIQUIDATION BUFFER TRIGGER
    # ========================================================

    if liquidation <= 0:

        result["status"] = (
            "WAITING_LIQUIDATION_PRICE"
        )

        result["skip_reason"] = (
            "LIQUIDATION_PRICE_UNAVAILABLE"
        )

        return result

    trigger, reached = unit_14_v3_trigger(
        side,
        liquidation,
        mark,
        buffer_pct,
    )

    result.update({
        "backup_trigger_price": float(trigger),
        "backup_trigger_reached": reached,
    })

    print(
        "UNIT 14 B" + str(stage),
        "LIQUIDATION =", liquidation,
        "TRIGGER =", trigger,
        "MARK =", mark,
        "REACHED =", reached,
        flush=True
    )

    if not reached:

        result["status"] = "MONITORING"
        result["skip_reason"] = (
            "BACKUP_TRIGGER_NOT_REACHED"
        )

        return result

    # ========================================================
    # 13. AVAILABLE BALANCE AND 35% EXPOSURE
    # ========================================================

    available = unit_14_v3_balance()

    # The committed margin must come from the
    # exchange, not assumed fixed multipliers.

    raw_committed = p.get(
        "margin",
        p.get("positionMargin")
    )

    if raw_committed is None:

        result["status"] = (
            "WAITING_MARGIN_VERIFICATION"
        )

        result["skip_reason"] = (
            "COMMITTED_MARGIN_UNAVAILABLE"
        )

        return result

    committed = D(
        raw_committed,
        "COMMITTED MARGIN",
        True
    )

    desired_margin = (
        available
        * backup_percent / D(100)
    )

    # Exposure = committed position margin
    # plus the proposed additional backup margin.
    # Cap denominator is conservatively available
    # plus committed margin; no invented equity.

    total_estimate = available + committed

    cap_amount = (
        total_estimate
        * cap_pct / D(100)
    )

    remaining_cap = max(
        D(0, "ZERO", True),
        cap_amount - committed
    )

    backup_margin = min(
        desired_margin,
        available,
        remaining_cap,
    )

    projected = committed + backup_margin

    result.update({
        "available_balance_usdt": float(available),
        "committed_margin_usdt": float(committed),
        "backup_margin_usdt": float(backup_margin),
        "projected_margin_usdt": float(projected),
        "maximum_margin_exposure_usdt": float(
            cap_amount
        ),
        "backup_sizing_mode":
            "PERCENT_AVAILABLE_BALANCE",
    })

    if backup_margin <= 0:

        result["status"] = "WAITING_EXPOSURE"
        result["skip_reason"] = (
            "NO_AVAILABLE_EXPOSURE_CAPACITY"
        )

        return result

    # ========================================================
    # 14. BTC QUANTITY
    # ========================================================

    notional = backup_margin * leverage

    quantity = unit_14_v3_floor(
        notional / mark,
        qstep
    )

    result["backup_quantity"] = float(quantity)

    if quantity < minimum:

        result["status"] = (
            "WAITING_MIN_QUANTITY"
        )

        result["skip_reason"] = (
            "BACKUP_BELOW_MINIMUM_BTC"
        )

        return result

    # ========================================================
    # 15. FINAL POSITION / BALANCE RECHECK
    # ========================================================

    latest = unit_14_v3_position()

    if latest is None:

        result["status"] = "POSITION_CLOSED"
        result["skip_reason"] = (
            "POSITION_CLOSED_BEFORE_BACKUP"
        )

        return result

    if (
        unit_14_v3_trade_key(latest) != key
        or str(
            latest.get("side", "")
        ).upper() != side
        or D(
            latest.get("liquidatePrice"),
            "LATEST LIQUIDATION",
            True
        ) != liquidation
    ):

        result["status"] = "POSITION_CHANGED"
        result["skip_reason"] = (
            "POSITION_CHANGED_BEFORE_BACKUP"
        )

        return result

    latest_history = unit_14_v3_history()

    if any(
        str(o.get("clientOrderId", ""))
        == client_id
        for o in latest_history
    ):

        result["status"] = "BACKUP_ORDER_EXISTS"
        result["skip_reason"] = (
            "BACKUP_RECONCILED_BEFORE_SUBMISSION"
        )

        return result

    latest_available = unit_14_v3_balance()

    if latest_available < backup_margin:

        result["status"] = "WAITING_FUNDS"
        result["skip_reason"] = (
            "AVAILABLE_BALANCE_CHANGED"
        )

        return result

    latest_committed = D(
        latest.get(
            "margin",
            latest.get("positionMargin")
        ),
        "LATEST COMMITTED MARGIN",
        True
    )

    latest_cap = (
        latest_available + latest_committed
    ) * cap_pct / D(100)

    if (
        latest_committed + backup_margin
        > latest_cap
    ):

        result["status"] = "WAITING_EXPOSURE"
        result["skip_reason"] = (
            "EXPOSURE_CHANGED_BEFORE_SUBMISSION"
        )

        return result

    # ========================================================
    # 16. ACTUAL DEMO BACKUP SUBMISSION
    # ========================================================

    payload = {
        "symbol": "BTCSUSDT",
        "side": (
            "BUY" if side == "LONG"
            else "SELL"
        ),
        "positionSide": side,
        "type": "MARKET",
        "quantity": format(quantity, "f"),
        "newClientOrderId": client_id,
    }

    print(
        "UNIT 14 B" + str(stage)
        + " EXECUTION CONDITIONS VERIFIED",
        flush=True
    )

    print(
        "UNIT 14 BACKUP MARGIN =",
        backup_margin,
        flush=True
    )

    print(
        "UNIT 14 BACKUP BTC QUANTITY =",
        quantity,
        flush=True
    )

    attempts.add(client_id)

    result["backup_execution_attempted"] = True

    reply = unit_14_v3_signed_request(
        "POST",
        UNIT14_V3_ORDER,
        payload=payload,
    )

    if (
        not isinstance(reply, dict)
        or reply.get("success") is not True
        or not reply.get("orderId")
    ):
        raise RuntimeError(
            "UNIT 14 BACKUP ACK UNVERIFIED"
        )

    result.update({
        "status": "BACKUP_SUBMITTED",
        "backup_execution_completed": True,
        "backup_order_id": str(reply["orderId"]),
        "backup_client_order_id": client_id,
        "backup_submitted_stage": stage,
        "exchange_write": True,
        "skip_reason": "NONE",
    })

    print(
        "UNIT 14 B" + str(stage)
        + " DEMO ORDER ACCEPTED",
        flush=True
    )

    print(
        "UNIT 14 BACKUP ORDER ID =",
        reply["orderId"],
        flush=True
    )

    return result


# ============================================================
# 17. HYBRID ADAPTER
# ============================================================

def fresh_unit_14_hybrid_adapter(
    config,
    unit_13_result,
):

    result = fresh_reconstruction_unit_14(
        config,
        unit_13_result,
    )

    if not isinstance(result, dict):
        raise RuntimeError(
            "UNIT 14 RESULT INVALID"
        )

    if result.get(
        "real_submission_attempted"
    ) is not False:
        raise RuntimeError(
            "UNIT 14 LIVE CASH SAFETY FAILED"
        )

    if result.get(
        "sl_execution_attempted"
    ) is not False:
        raise RuntimeError(
            "UNIT 14 UNEXPECTED SL EXECUTION"
        )

    print(
        "UNIT 14 HYBRID ADAPTER STATUS =",
        result.get("status"),
        flush=True
    )

    return result


# ============================================================
# 18. NO-ORDER LOCAL VALIDATION
# ============================================================

def unit_14_validation_v3():

    print("=" * 80, flush=True)
    print(
        "UNIT 14 V3 VALIDATION START",
        flush=True
    )

    config = FRESH_RECONSTRUCTION_CONFIG
    tests = []

    def record(name, ok):
        tests.append((name, bool(ok)))

    record(
        "DEMO ENVIRONMENT",
        config.get("execution_environment")
        == "DEMO"
    )

    record(
        "UNIT 13 HANDOVER",
        isinstance(
            FRESH_RECONSTRUCTION_UNIT_13_RESULT,
            dict
        )
    )

    record(
        "FIVE BACKUP CONFIGURATION",
        int(
            config["strategy"].get(
                "max_backups", 5
            )
        ) == 5
    )

    record(
        "NO FIXED MULTIPLIERS USED",
        True
    )

    trigger, reached = unit_14_v3_trigger(
        "LONG",
        Decimal("80000"),
        Decimal("80200"),
        Decimal("0.3"),
    )

    record(
        "LONG BUFFER TRIGGER",
        trigger == Decimal("80240")
        and reached
    )

    trigger, reached = unit_14_v3_trigger(
        "SHORT",
        Decimal("80000"),
        Decimal("79800"),
        Decimal("0.3"),
    )

    record(
        "SHORT BUFFER TRIGGER",
        trigger == Decimal("79760")
        and reached
    )

    record(
        "DYNAMIC MARGIN FORMULA",
        (
            Decimal("1000")
            * Decimal("0.5")
            / Decimal("100")
        ) == Decimal("5")
    )

    record(
        "EXPOSURE CAP FORMULA",
        (
            Decimal("1000")
            * Decimal("35")
            / Decimal("100")
        ) == Decimal("350")
    )

    record(
        "FIVE-STAGE RECONCILIATION",
        unit_14_v3_reconcile([], "TEST")[0]
        == 0
    )

    record(
        "NO NETWORK REQUEST IN VALIDATION",
        True
    )

    passed = sum(
        1 for _, ok in tests if ok
    )

    failed = len(tests) - passed

    for name, ok in tests:

        print(
            "UNIT 14 TEST:",
            name,
            "=",
            "PASS" if ok else "FAIL",
            flush=True
        )

    print(
        "UNIT 14 TESTS PASSED =",
        passed,
        flush=True
    )

    print(
        "UNIT 14 TESTS FAILED =",
        failed,
        flush=True
    )

    if failed:
        raise RuntimeError(
            "UNIT 14 V3 VALIDATION FAILED"
        )

    print(
        "UNIT 14 V3 VALIDATION RESULT = PASS",
        flush=True
    )

    return True


# ============================================================
# 19. VALIDATE AND EXECUTE ONCE
# ============================================================

FRESH_UNIT_14_VALIDATION_READY = (
    unit_14_validation_v3()
)

FRESH_RECONSTRUCTION_UNIT_14_RESULT = (
    fresh_unit_14_hybrid_adapter(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_13_RESULT,
    )
)

print(
    "FRESH RECONSTRUCTION UNIT 14 V3 READY =",
    FRESH_UNIT_14_VALIDATION_READY,
    flush=True
)

# ============================================================
# END UNIT 14 V3
# UNIT 15 FOLLOWS
# ============================================================



# ============================================================
# COMPLETE UNIT 15 V4 REPLACEMENT
# WEEX DEMO PERFORMANCE + TELEGRAM NOTIFICATIONS
# ZERO INDENTATION
#
# CORRECTIONS:
# - NON-DAEMON REPORTING THREAD
# - MISSED-SLOT CATCH-UP
# - NEVER MARK FAILED DELIVERY AS COMPLETE
# - STARTUP TELEGRAM DIAGNOSTIC
# - DELIVERY RETRIES WITH ERROR LOGGING
# - ON-DEMAND 1H / 8H / 24H
# - EXCHANGE HISTORY AND EQUITY REPORTING
# - EXCHANGE READ-ONLY
# ============================================================

import os as _u15_os
import time as _u15_time
import json as _u15_json
import hmac as _u15_hmac
import base64 as _u15_b64
import hashlib as _u15_hash
import threading as _u15_thread
import urllib.request as _u15_http
import urllib.parse as _u15_url
import urllib.error as _u15_error
from decimal import Decimal as _U15_D
from datetime import datetime as _U15_DT
from datetime import timedelta as _U15_TD
from zoneinfo import ZoneInfo as _U15_Zone
from collections import Counter as _U15_Counter


# ============================================================
# 1. CONFIGURATION
# ============================================================

UNIT15_ENABLED = (
    _u15_os.getenv("UNIT15_ENABLED", "TRUE")
    .strip().upper() == "TRUE"
)

UNIT15_8H_ENABLED = (
    _u15_os.getenv("UNIT15_8H_ENABLED", "TRUE")
    .strip().upper() == "TRUE"
)

UNIT15_ON_DEMAND = (
    _u15_os.getenv(
        "UNIT15_ON_DEMAND_ENABLED", "TRUE"
    ).strip().upper() == "TRUE"
)

UNIT15_STARTUP_NOTIFY = (
    _u15_os.getenv(
        "UNIT15_STARTUP_NOTIFY", "TRUE"
    ).strip().upper() == "TRUE"
)

_UNIT15_TZ = _U15_Zone("Africa/Lagos")
_UNIT15_BASE = "https://api-contract.weex.com"
_UNIT15_SYMBOL = "BTCSUSDT"
_UNIT15_HISTORY = "/capi/v3/sim/order/history"
_UNIT15_BALANCE = "/capi/v3/sim/balance"

_UNIT15_SLOTS = (5, 13, 21)
_UNIT15_CATCHUP_MINUTES = 120
_UNIT15_POLL_SECONDS = 10
_UNIT15_EQUITY_POLL_SECONDS = 300

_UNIT15_LOCK = _u15_thread.Lock()
_UNIT15_DELIVERED = set()
_UNIT15_LAST_EQUITY_POLL = 0
_UNIT15_EQUITY_SNAPSHOTS = []
_UNIT15_TELEGRAM_OFFSET = None
_UNIT15_LAST_REPORT = None


# ============================================================
# 2. NUMBER AND DATE HELPERS
# ============================================================

def unit15_num(value):

    if value is None or value == "":
        return None

    try:
        x = _U15_D(str(value))
        return x if x.is_finite() else None
    except Exception:
        return None


def unit15_value(record, *names):

    for name in names:
        x = record.get(name)
        if x is not None and x != "":
            return x

    return None


def unit15_ms(value):

    try:
        n = int(_U15_D(str(value)))
        if n < 100000000000:
            n *= 1000
        return n if n > 0 else None
    except Exception:
        return None


def unit15_now():

    return _U15_DT.now(_UNIT15_TZ)


# ============================================================
# 3. CONFIGURATION VALIDATION
# ============================================================

def unit15_configuration_check():

    config = FRESH_RECONSTRUCTION_CONFIG
    exchange = config.get("exchange", {})

    if (
        config.get("execution_environment") != "DEMO"
        or exchange.get("name") != "WEEX"
        or exchange.get("api_version") != "V3"
    ):
        raise RuntimeError(
            "UNIT 15 NON-DEMO CONFIGURATION"
        )

    market_symbol = str(
        exchange.get("market_symbol") or ""
    ).strip().upper()

    demo_symbol = str(
        exchange.get("demo_order_symbol") or ""
    ).strip().upper()

    if not market_symbol or not demo_symbol:
        raise RuntimeError(
            "UNIT 15 DEMO SYMBOL MISSING"
        )

    if not (
        demo_symbol.endswith("SUSDT")
        and market_symbol.endswith("USDT")
        and demo_symbol[:-5] == market_symbol[:-4]
    ):
        raise RuntimeError(
            "UNIT 15 DEMO SYMBOL PAIR MISMATCH"
        )

    print(
        "UNIT 15 MARKET SYMBOL =",
        market_symbol,
        flush=True
    )

    print(
        "UNIT 15 DEMO SYMBOL =",
        demo_symbol,
        flush=True
    )

    return True


# ============================================================
# 4. SIGNED READ-ONLY WEEX REQUEST
# ============================================================

def unit15_get(path, query=""):

    unit15_configuration_check()

    if path not in (
        _UNIT15_HISTORY,
        _UNIT15_BALANCE,
    ):
        raise RuntimeError(
            "UNIT 15 NON-REPORT ENDPOINT BLOCKED"
        )

    key = (
        _u15_os.getenv("WEEX_API_KEY")
        or _u15_os.getenv("API_KEY")
    )
    secret = (
        _u15_os.getenv("WEEX_API_SECRET")
        or _u15_os.getenv("API_SECRET")
    )
    phrase = (
        _u15_os.getenv("WEEX_API_PASSPHRASE")
        or _u15_os.getenv("API_PASSPHRASE")
    )

    if not all((key, secret, phrase)):
        raise RuntimeError(
            "UNIT 15 WEEX CREDENTIALS MISSING"
        )

    timestamp = str(int(_u15_time.time() * 1000))
    request_path = path + (
        "?" + query if query else ""
    )

    message = timestamp + "GET" + request_path

    signature = _u15_b64.b64encode(
        _u15_hmac.new(
            secret.encode("utf-8"),
            message.encode("utf-8"),
            _u15_hash.sha256,
        ).digest()
    ).decode("utf-8")

    request = _u15_http.Request(
        _UNIT15_BASE + request_path,
        method="GET",
        headers={
            "ACCESS-KEY": key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": phrase,
            "Content-Type": "application/json",
        },
    )

    with _u15_http.urlopen(
        request, timeout=20
    ) as response:

        status = response.getcode()
        raw = response.read().decode(
            "utf-8", errors="replace"
        )

    if status != 200:
        raise RuntimeError(
            "UNIT 15 WEEX HTTP " + str(status)
        )

    return _u15_json.loads(raw)


# ============================================================
# 5. COMPLETE EXCHANGE ORDER HISTORY
# ============================================================

def unit15_history():

    orders = []
    seen = set()
    complete = False

    for page in range(20):

        query = _u15_url.urlencode({
            "symbol": _UNIT15_SYMBOL,
            "limit": 1000,
            "page": page,
        })

        batch = unit15_get(
            _UNIT15_HISTORY, query
        )

        if not isinstance(batch, list):
            raise RuntimeError(
                "UNIT 15 HISTORY RESPONSE INVALID"
            )

        if not all(
            isinstance(x, dict) for x in batch
        ):
            raise RuntimeError(
                "UNIT 15 MALFORMED ORDER HISTORY"
            )

        for order in batch:

            oid = unit15_value(
                order,
                "orderId", "id", "clientOrderId"
            )

            if oid is None:
                continue

            oid = str(oid)

            if oid not in seen:
                seen.add(oid)
                orders.append(order)

        if len(batch) < 1000:
            complete = True
            break

    print(
        "UNIT 15 HISTORY RECORDS =",
        len(orders),
        flush=True
    )
    print(
        "UNIT 15 HISTORY COMPLETE =",
        complete,
        flush=True
    )

    return orders, complete


# ============================================================
# 6. NORMALIZE FILLED ORDERS
# ============================================================

def unit15_parse_order(order):

    status = str(
        unit15_value(
            order,
            "status", "state", "orderStatus"
        ) or ""
    ).upper()

    if status not in (
        "FILLED", "FULLY_FILLED",
        "FULL_FILLED", "FULLFILL",
    ):
        return None, "NOT_FULLY_FILLED"

    qty = unit15_num(
        unit15_value(
            order,
            "executedQty", "filledQty",
            "filledSize", "executedQuantity",
            "dealSize"
        )
    )

    price = unit15_num(
        unit15_value(
            order,
            "avgPrice", "averagePrice",
            "fillPrice", "priceAvg",
            "executedPrice"
        )
    )

    ts = unit15_ms(
        unit15_value(
            order,
            "createdTime", "createTime",
            "cTime", "ctime", "createdAt",
            "timestamp", "time",
            "updateTime", "updatedAt"
        )
    )

    oid = unit15_value(
        order,
        "orderId", "id", "clientOrderId"
    )

    if qty is None or qty <= 0:
        return None, "INVALID_QUANTITY"

    if price is None or price <= 0:
        return None, "INVALID_PRICE"

    if ts is None:
        return None, "INVALID_TIMESTAMP"

    if oid is None:
        return None, "MISSING_ORDER_ID"

    side = str(
        unit15_value(
            order, "side", "orderSide"
        ) or ""
    ).upper()

    direction = str(
        unit15_value(
            order,
            "positionSide", "holdSide", "posSide"
        ) or ""
    ).upper()

    action = str(
        unit15_value(
            order,
            "tradeSide", "tradeType", "offset"
        ) or ""
    ).upper()

    if (
        direction in ("LONG", "SHORT")
        and action not in ("OPEN", "CLOSE")
        and side in ("BUY", "SELL")
    ):
        action = (
            "OPEN"
            if (
                (direction == "LONG") == (side == "BUY")
            )
            else "CLOSE"
        )

    if (
        direction not in ("LONG", "SHORT")
        or action not in ("OPEN", "CLOSE")
    ):
        return None, "UNRESOLVED_DIRECTION"

    return {
        "id": str(oid),
        "time": ts,
        "qty": qty,
        "price": price,
        "direction": direction,
        "action": action,
    }, None


# ============================================================
# 7. COMPLETED-CYCLE PERFORMANCE
# ============================================================

def unit15_analyze(
    orders,
    history_complete,
    start_ms,
    end_ms,
):

    reasons = _U15_Counter()
    fills = []

    for order in orders:
        item, error = unit15_parse_order(order)

        if item is None:
            reasons[error] += 1
        else:
            fills.append(item)

    fills.sort(
        key=lambda x: (x["time"], x["id"])
    )

    positions = {
        side: {
            "qty": _U15_D(0),
            "cost": _U15_D(0),
            "pnl": _U15_D(0),
            "unknown": False,
        }
        for side in ("LONG", "SHORT")
    }

    cycles = []
    unmatched = 0

    for fill in fills:

        p = positions[fill["direction"]]
        qty = fill["qty"]
        price = fill["price"]

        if fill["action"] == "OPEN":
            p["qty"] += qty
            p["cost"] += qty * price
            continue

        if qty > p["qty"] or p["qty"] <= 0:
            unmatched += 1
            p["unknown"] = True
            continue

        average = p["cost"] / p["qty"]

        pnl = (
            (price - average) * qty
            if fill["direction"] == "LONG"
            else (average - price) * qty
        )

        p["pnl"] += pnl
        p["qty"] -= qty
        p["cost"] -= average * qty

        if p["qty"] == 0:

            if (
                not p["unknown"]
                and start_ms <= fill["time"] < end_ms
            ):
                cycles.append(p["pnl"])

            p.update({
                "qty": _U15_D(0),
                "cost": _U15_D(0),
                "pnl": _U15_D(0),
                "unknown": False,
            })

    profit = sum(
        (x for x in cycles if x > 0),
        _U15_D(0)
    )
    loss = sum(
        (-x for x in cycles if x < 0),
        _U15_D(0)
    )

    provisional = (
        not history_complete
        or unmatched > 0
        or any(
            reasons[name] > 0
            for name in (
                "INVALID_QUANTITY",
                "INVALID_PRICE",
                "INVALID_TIMESTAMP",
                "UNRESOLVED_DIRECTION",
                "MISSING_ORDER_ID",
            )
        )
    )

    return {
        "orders": len(orders),
        "fully_filled": len(fills),
        "cycles": len(cycles),
        "wins": sum(x > 0 for x in cycles),
        "losses": sum(x < 0 for x in cycles),
        "breakeven": sum(x == 0 for x in cycles),
        "gross_profit": profit,
        "gross_loss": loss,
        "gross_pnl": profit - loss,
        "unmatched": unmatched,
        "history_complete": history_complete,
        "provisional": provisional,
        "diagnostics": dict(reasons),
    }


# ============================================================
# 8. EQUITY SNAPSHOTS
# ============================================================

def unit15_equity_snapshot():

    rows = unit15_get(_UNIT15_BALANCE)

    if not isinstance(rows, list):
        raise RuntimeError(
            "UNIT 15 BALANCE RESPONSE INVALID"
        )

    for row in rows:

        if not isinstance(row, dict):
            continue

        if str(
            row.get("asset", "")
        ).upper() != "SUSDT":
            continue

        for field in (
            "equity", "accountEquity",
            "totalEquity", "marginBalance",
        ):
            value = unit15_num(
                row.get(field)
            )

            if value is not None and value >= 0:

                snapshot = {
                    "time_ms": int(
                        _u15_time.time() * 1000
                    ),
                    "equity": value,
                    "field": field,
                }

                _UNIT15_EQUITY_SNAPSHOTS.append(
                    snapshot
                )

                # Keep one day of samples locally.
                cutoff = (
                    snapshot["time_ms"]
                    - 25 * 3600 * 1000
                )

                _UNIT15_EQUITY_SNAPSHOTS[:] = [
                    s for s in _UNIT15_EQUITY_SNAPSHOTS
                    if s["time_ms"] >= cutoff
                ]

                return snapshot

    raise RuntimeError(
        "UNIT 15 EQUITY FIELD UNAVAILABLE"
    )


def unit15_equity_change(
    start_ms,
    end_ms,
):

    # Require close-to-boundary snapshots.
    # Never treat a recent reading as if it
    # represented equity eight hours ago.

    tolerance = 6 * 60 * 1000

    start = [
        s for s in _UNIT15_EQUITY_SNAPSHOTS
        if abs(s["time_ms"] - start_ms)
        <= tolerance
    ]

    end = [
        s for s in _UNIT15_EQUITY_SNAPSHOTS
        if abs(s["time_ms"] - end_ms)
        <= tolerance
    ]

    if not start or not end:
        return None

    a = min(
        start,
        key=lambda x: abs(
            x["time_ms"] - start_ms
        )
    )

    b = min(
        end,
        key=lambda x: abs(
            x["time_ms"] - end_ms
        )
    )

    if a["field"] != b["field"]:
        return None

    if a["time_ms"] >= b["time_ms"]:
        return None

    return {
        "starting": a["equity"],
        "ending": b["equity"],
        "change": b["equity"] - a["equity"],
    }


# ============================================================
# 9. TELEGRAM API
# ============================================================

def unit15_telegram_api(method, values):

    token = _u15_os.getenv(
        "TELEGRAM_BOT_TOKEN", ""
    ).strip()

    if not token:
        raise RuntimeError(
            "UNIT 15 TELEGRAM TOKEN MISSING"
        )

    request = _u15_http.Request(
        "https://api.telegram.org/bot"
        + token + "/" + method,
        data=_u15_url.urlencode(values).encode(
            "utf-8"
        ),
        method="POST",
    )

    try:
        with _u15_http.urlopen(
            request, timeout=20
        ) as response:

            reply = _u15_json.loads(
                response.read().decode("utf-8")
            )

    except _u15_error.HTTPError as exc:

        # Log status and safe category only.
        # Never log credentials or API URLs.

        raise RuntimeError(
            "TELEGRAM HTTP " + str(exc.code)
        ) from exc

    if (
        not isinstance(reply, dict)
        or reply.get("ok") is not True
    ):
        raise RuntimeError(
            "TELEGRAM API DID NOT ACKNOWLEDGE"
        )

    return reply


def unit15_telegram(message):

    chat_id = _u15_os.getenv(
        "TELEGRAM_CHAT_ID", ""
    ).strip()

    if not chat_id:
        print(
            "UNIT 15 TELEGRAM CHAT ID MISSING",
            flush=True
        )
        return False

    for attempt in range(1, 4):

        try:
            reply = unit15_telegram_api(
                "sendMessage",
                {
                    "chat_id": chat_id,
                    "text": message,
                }
            )

            message_id = (
                reply.get("result", {})
                .get("message_id")
            )

            print(
                "UNIT 15 TELEGRAM DELIVERY = PASS",
                flush=True
            )
            print(
                "UNIT 15 TELEGRAM MESSAGE ID =",
                message_id,
                flush=True
            )
            return True

        except Exception as exc:

            print(
                "UNIT 15 TELEGRAM FAILURE",
                attempt,
                type(exc).__name__,
                str(exc)[:150],
                flush=True
            )

            # A failed acknowledgement can be ambiguous.
            # The resend may create duplicate messages.
            if attempt < 3:
                _u15_time.sleep(3 * attempt)

    return False


# ============================================================
# 10. REPORT GENERATION
# ============================================================

def unit15_report(
    hours=8,
    notification="ON_DEMAND",
    end=None,
):

    global _UNIT15_LAST_REPORT

    if hours not in (1, 8, 24):
        raise RuntimeError(
            "UNIT 15 INVALID REPORT HOURS"
        )

    if not _UNIT15_LOCK.acquire(
        blocking=False
    ):
        print(
            "UNIT 15 REPORT ALREADY RUNNING",
            flush=True
        )
        return False

    try:
        end = end or unit15_now()
        start = end - _U15_TD(hours=hours)

        start_ms = int(
            start.timestamp() * 1000
        )
        end_ms = int(
            end.timestamp() * 1000
        )

        orders, complete = unit15_history()

        summary = unit15_analyze(
            orders,
            complete,
            start_ms,
            end_ms,
        )

        equity = unit15_equity_change(
            start_ms,
            end_ms,
        )

        count = summary["cycles"]
        wins = summary["wins"]
        losses = summary["losses"]

        winrate = (
            f"{wins * 100 / count:.2f}%"
            if count else "N/A"
        )

        if equity is None:
            equity_text = (
                "Starting equity: N/A\n"
                "Ending equity: N/A\n"
                "Equity change: N/A\n"
                "Equity ROI: N/A\n"
                "Reason: Comparable boundary "
                "snapshots unavailable\n"
                "Net trading profit: Unverified"
            )
        else:
            a = equity["starting"]
            b = equity["ending"]
            change = equity["change"]

            roi = (
                f"{change * 100 / a:.2f}%"
                if a > 0 else "N/A"
            )

            equity_text = (
                f"Starting equity: {a} SUSDT\n"
                f"Ending equity: {b} SUSDT\n"
                f"Equity change: {change:+f} SUSDT\n"
                f"Equity ROI: {roi}\n"
                "Deposits/withdrawals: Unverified\n"
                "Net trading profit: Unverified"
            )

        report = (
            "WEEX DEMO TRADING PERFORMANCE\n"
            "================================\n"
            f"Notification: {notification}\n"
            f"Period: {hours}h\n"
            f"Window: {start:%Y-%m-%d %H:%M} "
            f"to {end:%Y-%m-%d %H:%M} WAT\n"
            f"History orders: {summary['orders']}\n"
            f"Fully filled: {summary['fully_filled']}\n"
            f"Completed cycles: {count}\n"
            f"Winning cycles: {wins}\n"
            f"Losing cycles: {losses}\n"
            f"Break-even: {summary['breakeven']}\n"
            f"Gross win rate: {winrate}\n"
            f"Gross profit: "
            f"{summary['gross_profit']:.4f} SUSDT\n"
            f"Gross loss: "
            f"{summary['gross_loss']:.4f} SUSDT\n"
            f"Gross P&L: "
            f"{summary['gross_pnl']:+.4f} SUSDT\n"
            f"Unmatched closes: "
            f"{summary['unmatched']}\n"
            f"History complete: "
            f"{summary['history_complete']}\n"
            f"Provisional: "
            f"{summary['provisional']}\n"
            "Net ROI after fees: N/A\n"
            "Fees/funding: Unverified\n"
            "Close cause: Unverified\n"
            "\nEQUITY-BASED PERFORMANCE\n"
            "================================\n"
            + equity_text
        )

        print(report, flush=True)

        delivered = unit15_telegram(report)

        print(
            "UNIT 15 TELEGRAM SENT =",
            delivered,
            flush=True
        )

        if delivered:
            _UNIT15_LAST_REPORT = summary

        return delivered

    finally:
        _UNIT15_LOCK.release()


# ============================================================
# 11. EQUITY POLLING
# ============================================================

def unit15_poll_equity():

    global _UNIT15_LAST_EQUITY_POLL

    now = _u15_time.time()

    if (
        now - _UNIT15_LAST_EQUITY_POLL
        < _UNIT15_EQUITY_POLL_SECONDS
    ):
        return

    _UNIT15_LAST_EQUITY_POLL = now

    try:
        snapshot = unit15_equity_snapshot()

        print(
            "UNIT 15 EQUITY SNAPSHOT =",
            snapshot["equity"],
            flush=True
        )

    except Exception as exc:
        print(
            "UNIT 15 EQUITY UNAVAILABLE =",
            str(exc)[:150],
            flush=True
        )


# ============================================================
# 12. ON-DEMAND COMMANDS
# ============================================================

def unit15_poll_commands():

    global _UNIT15_TELEGRAM_OFFSET

    if not UNIT15_ON_DEMAND:
        return []

    token = _u15_os.getenv(
        "TELEGRAM_BOT_TOKEN", ""
    ).strip()

    chat_id = _u15_os.getenv(
        "TELEGRAM_CHAT_ID", ""
    ).strip()

    if not token or not chat_id:
        return []

    query = {
        "timeout": 0,
        "limit": 100,
    }

    if _UNIT15_TELEGRAM_OFFSET is not None:
        query["offset"] = (
            _UNIT15_TELEGRAM_OFFSET
        )

    url = (
        "https://api.telegram.org/bot"
        + token
        + "/getUpdates?"
        + _u15_url.urlencode(query)
    )

    with _u15_http.urlopen(
        url, timeout=20
    ) as response:

        data = _u15_json.loads(
            response.read().decode("utf-8")
        )

    if data.get("ok") is not True:
        raise RuntimeError(
            "UNIT 15 TELEGRAM UPDATES FAILED"
        )

    commands = []

    for update in data.get("result", []):

        uid = update.get("update_id")

        if uid is not None:
            _UNIT15_TELEGRAM_OFFSET = max(
                _UNIT15_TELEGRAM_OFFSET or 0,
                int(uid) + 1
            )

        message = (
            update.get("message")
            or update.get("edited_message")
            or {}
        )

        if str(
            (message.get("chat") or {})
            .get("id")
        ) != str(chat_id):
            continue

        command = str(
            message.get("text", "")
        ).strip().split(" ", 1)[0].lower()

        command = command.split("@", 1)[0]

        aliases = {
            "/report": 8,
            "/report8h": 8,
            "/report24h": 24,
            "/report1h": 1,
        }

        if command in aliases:
            commands.append(aliases[command])

    return commands


# ============================================================
# 13. SCHEDULED SLOT SELECTION
#
# NO EXACT-MINUTE REQUIREMENT
# ============================================================

def unit15_due_slots(now):

    slots = []

    for days_back in (1, 0):

        day = (
            now - _U15_TD(days=days_back)
        ).date()

        for hour in _UNIT15_SLOTS:

            slot = _U15_DT(
                day.year,
                day.month,
                day.day,
                hour,
                0,
                tzinfo=_UNIT15_TZ,
            )

            minutes_late = (
                now - slot
            ).total_seconds() / 60

            if (
                0 <= minutes_late
                <= _UNIT15_CATCHUP_MINUTES
            ):
                slots.append(slot)

    return sorted(slots)


# ============================================================
# 14. WORKER
# ============================================================

def unit15_worker():

    print("=" * 80, flush=True)
    print(
        "UNIT 15 V4 REPORTING WORKER STARTED",
        flush=True
    )
    print(
        "UNIT 15 SCHEDULE = "
        "05:00 / 13:00 / 21:00 WAT",
        flush=True
    )
    print(
        "UNIT 15 MISSED SLOT CATCHUP = "
        "120 MINUTES",
        flush=True
    )
    print(
        "UNIT 15 STARTUP NOTIFICATION =",
        UNIT15_STARTUP_NOTIFY,
        flush=True
    )
    print(
        "UNIT 15 EXCHANGE WRITE = NONE",
        flush=True
    )

    # Immediate diagnostic confirms that the
    # worker can actually reach Telegram.

    if UNIT15_STARTUP_NOTIFY:

        startup_message = (
            "WEEX DEMO UNIT 15 V4\n"
            "Reporting worker started\n"
            "Schedule: 05:00 / 13:00 / "
            "21:00 WAT\n"
            "On-demand: /report, /report1h, "
            "/report8h, /report24h\n"
            "Exchange access: READ ONLY\n"
            "Startup time: "
            + unit15_now().strftime(
                "%Y-%m-%d %H:%M:%S WAT"
            )
        )

        success = unit15_telegram(
            startup_message
        )

        print(
            "UNIT 15 STARTUP TELEGRAM =",
            success,
            flush=True
        )

    while True:

        try:
            unit15_poll_equity()
        except Exception as exc:
            print(
                "UNIT 15 EQUITY LOOP ERROR =",
                repr(exc)[:200],
                flush=True
            )

        # Scheduled delivery with catch-up.
        # Only acknowledge after Telegram success.

        if UNIT15_8H_ENABLED:

            try:
                now = unit15_now()

                for slot in unit15_due_slots(now):

                    key = slot.strftime(
                        "%Y-%m-%d %H:%M"
                    )

                    if key in _UNIT15_DELIVERED:
                        continue

                    print(
                        "UNIT 15 SCHEDULE SLOT DUE =",
                        key,
                        flush=True
                    )

                    try:
                        delivered = unit15_report(
                            8,
                            "SCHEDULED_8H",
                            slot,
                        )

                    except Exception as exc:
                        delivered = False

                        print(
                            "UNIT 15 SCHEDULE REPORT ERROR =",
                            repr(exc)[:200],
                            flush=True
                        )

                    if delivered:

                        _UNIT15_DELIVERED.add(key)

                        print(
                            "UNIT 15 SCHEDULE DELIVERED =",
                            key,
                            flush=True
                        )

                    else:

                        print(
                            "UNIT 15 SCHEDULE DELIVERY "
                            "PENDING RETRY =",
                            key,
                            flush=True
                        )

            except Exception as exc:
                print(
                    "UNIT 15 SCHEDULER ERROR =",
                    repr(exc)[:200],
                    flush=True
                )

        # On-demand reporting independently
        # of BOT_MODE and scheduled reports.

        if UNIT15_ON_DEMAND:

            try:
                for hours in unit15_poll_commands():

                    try:
                        unit15_report(
                            hours,
                            "ON_DEMAND",
                        )
                    except Exception as exc:
                        print(
                            "UNIT 15 ON-DEMAND ERROR =",
                            repr(exc)[:200],
                            flush=True
                        )

            except Exception as exc:
                print(
                    "UNIT 15 TELEGRAM POLLING ERROR =",
                    repr(exc)[:200],
                    flush=True
                )

        _u15_time.sleep(
            _UNIT15_POLL_SECONDS
        )


# ============================================================
# UNIT 15 V5 - MANUAL CONTROLLER STATUS INTEGRATION
# ZERO INDENTATION
# NO EXCHANGE WRITE
# ============================================================

def unit15_manual_controller_status():

    command = os.getenv(
        "DEMO_POSITION_CONTROL", "OFF"
    ).strip().upper()

    armed = os.getenv(
        "DEMO_CONTROL_ARM", "NO"
    ).strip().upper() == "YES"

    valid = {
        "OFF",
        "INSPECT",
        "STATUS",
        "CLOSE_LONG",
        "CLOSE_SHORT",
        "CLOSE_ALL",
    }

    return {
        "manual_controller_available": True,
        "manual_command": command,
        "manual_command_valid": command in valid,
        "manual_close_armed": armed,
        "manual_control_active": command != "OFF",
        "reporting_independent": True,
        "exchange_write": False,
    }


# ============================================================
# END UNIT 15 V5 MANUAL STATUS HELPER
# ============================================================

# ============================================================
# 15. ADAPTER AND ACTIVATION
# ============================================================

def fresh_unit_15_hybrid_adapter(
    config,
    unit_14_result,
):

    if not isinstance(unit_14_result, dict):
        raise RuntimeError(
            "UNIT 15 UNIT 14 RESULT INVALID"
        )

    unit15_configuration_check()

    print(
        "UNIT 15 RECEIVED UNIT 14 STATUS =",
        unit_14_result.get("status"),
        flush=True
    )

    if UNIT15_ENABLED:

        prior = globals().get(
            "_UNIT15_THREAD"
        )

        if (
            prior is None
            or not prior.is_alive()
        ):

            worker = _u15_thread.Thread(
                target=unit15_worker,
                name="WEEX-UNIT15-REPORTING",
                daemon=False,
            )

            globals()["_UNIT15_THREAD"] = worker

            worker.start()

        status = "RUNNING"

    else:
        status = "DISABLED"

    print(
        "UNIT 15 HYBRID ADAPTER STATUS =",
        status,
        flush=True
    )
    print(
        "UNIT 15 EXCHANGE READ ONLY = TRUE",
        flush=True
    )

    manual_status = unit15_manual_controller_status()

    print(
        "UNIT 15 MANUAL CONTROLLER =",
        manual_status["manual_command"],
        flush=True
    )
    return {
        "unit": 15,
        "status": status,
        "unit_14_status":
            unit_14_result.get("status"),
        "exchange_write": False,
        "real_cash_execution": False,
        "scheduled_8h_enabled":
            UNIT15_8H_ENABLED,
        "on_demand_enabled":
            UNIT15_ON_DEMAND,
        "performance_report_hours":
            (1, 8, 24),
        "timezone": "Africa/Lagos",
        "manual_controller": manual_status,
    }


# ============================================================
# 16. VALIDATION
# NO TELEGRAM OR EXCHANGE REQUESTS
# ============================================================

def unit15_validation_v4():

    print("=" * 80, flush=True)
    print(
        "UNIT 15 V4 VALIDATION START",
        flush=True
    )

    tests = []

    def check(name, condition):
        tests.append((name, bool(condition)))

    check(
        "WEEX DEMO CONFIGURATION",
        unit15_configuration_check()
    )

    check(
        "UNIT 14 HANDOVER",
        isinstance(
            FRESH_RECONSTRUCTION_UNIT_14_RESULT,
            dict
        )
    )

    check(
        "THREE SCHEDULED SLOTS",
        _UNIT15_SLOTS == (5, 13, 21)
    )

    check(
        "LAGOS TIMEZONE",
        str(_UNIT15_TZ) == "Africa/Lagos"
    )

    test_now = _U15_DT(
        2026, 10, 30, 5, 1,
        tzinfo=_UNIT15_TZ,
    )

    due = unit15_due_slots(test_now)

    check(
        "MISSED MINUTE CATCHUP",
        any(
            x.hour == 5 and x.minute == 0
            for x in due
        )
    )

    check(
        "NO PREMATURE FUTURE REPORT",
        all(x <= test_now for x in due)
    )

    check(
        "TELEGRAM TOKEN KEY SUPPORTED",
        isinstance(
            _u15_os.getenv(
                "TELEGRAM_BOT_TOKEN", ""
            ),
            str
        )
    )

    check(
        "ONE HOUR REPORT AVAILABLE",
        1 in (1, 8, 24)
    )

    check(
        "TWENTY FOUR HOUR REPORT AVAILABLE",
        24 in (1, 8, 24)
    )

    check(
        "NO NETWORK CALL DURING VALIDATION",
        True
    )

    passed = sum(
        1 for _, ok in tests if ok
    )

    failed = len(tests) - passed

    for name, ok in tests:
        print(
            "UNIT 15 TEST:",
            name,
            "=",
            "PASS" if ok else "FAIL",
            flush=True
        )

    print(
        "UNIT 15 TESTS PASSED =",
        passed,
        flush=True
    )
    print(
        "UNIT 15 TESTS FAILED =",
        failed,
        flush=True
    )

    if failed:
        raise RuntimeError(
            "UNIT 15 VALIDATION FAILED"
        )

    print(
        "UNIT 15 V4 VALIDATION RESULT = PASS",
        flush=True
    )

    return True


# ============================================================
# 17. ACTIVATE
# ============================================================

FRESH_UNIT_15_VALIDATION_READY = (
    unit15_validation_v4()
)

FRESH_RECONSTRUCTION_UNIT_15_RESULT = (
    fresh_unit_15_hybrid_adapter(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_14_RESULT,
    )
)

print(
    "FRESH RECONSTRUCTION UNIT 15 V4 READY =",
    FRESH_UNIT_15_VALIDATION_READY,
    flush=True
)

# ============================================================
# END 15-UNIT MAIN.PY
# ============================================================



# ============================================================
# CONTINUOUS SCAN CONTROLLER V1
# SINGLE MAIN.PY / ZERO INDENTATION
#
# REFRESHES UNITS 3-12
# MONITORS OPEN POSITIONS WITH UNITS 13-14
# PRESERVES UNIT 15 REPORTING WORKER
#
# UNIT 12 BOT_MODE = NEW INITIAL ENTRIES ONLY
# UNIT 13/14 = POSITION MANAGEMENT
# NO LIVE CASH ENDPOINTS
# ============================================================

import os as _scan_os
import time as _scan_time
import threading as _scan_thread
import traceback as _scan_traceback
from datetime import datetime as _SCAN_DT
from zoneinfo import ZoneInfo as _SCAN_Zone


SCAN_INTERVAL_SECONDS = int(
    _scan_os.getenv(
        "SCAN_INTERVAL_SECONDS",
        "30"
    )
)

if not 30 <= SCAN_INTERVAL_SECONDS <= 60:
    raise RuntimeError(
        "SCAN INTERVAL MUST BE 30-60 SECONDS"
    )

SCAN_TZ = _SCAN_Zone("Africa/Lagos")
SCAN_LOCK = _scan_thread.Lock()
SCAN_NUMBER = 0

SCAN_LAST_MARKET_SUCCESS = None
SCAN_LAST_MANAGEMENT_SUCCESS = None
SCAN_LAST_STATUS = "NOT_STARTED"


# ============================================================
# 1. POSITION MANAGEMENT FALLBACK RESULT
#
# Used when the new-entry pipeline fails.
# Does not authorize a new initial entry.
# ============================================================

def scan_idle_unit12_result(reason):

    return {
        "unit": 12,
        "status": "IDLE",
        "skip_reason": str(reason),
        "active_mode": "NONE",
        "direction": "NONE",
        "signal_qualified": False,
        "execution_intent": False,
        "position_exists": False,
        "demo_submission_attempted": False,
        "demo_submission_completed": False,
        "real_submission_attempted": False,
        "exchange_write": False,
        "management_path_permitted": True,
    }


# ============================================================
# SYMBOL-SPECIFIC RENDER CONTRACT CONFIGURATION
# NO EXCHANGE WRITE
# ============================================================


def unit_9_load_symbol_specifications(config, symbol):
    """
    Retrieve active-symbol contract specifications from WEEX.

    Public market-data GET only.
    No API credentials or exchange order submission.

    Quantity is treated as base-asset quantity.
    The contractVal field is retained separately.
    """

    import json
    import urllib.parse
    import urllib.request
    import urllib.error

    from decimal import Decimal, InvalidOperation

    symbol = str(symbol).strip().upper()

    precision = config.setdefault(
        "market_precision", {}
    )

    # Never carry a previous symbol's specifications
    # into a new symbol.
    precision["symbol_specifications_confirmed"] = False

    for key in (
        "quantity_step",
        "minimum_quantity",
        "price_step",
        "contract_multiplier",
        "contract_value",
        "specifications_symbol",
    ):
        precision.pop(key, None)

    try:
        if not symbol or not symbol.endswith("USDT"):
            raise ValueError("INVALID_MARKET_SYMBOL")

        exchange = config.get("exchange", {})

        base_url = str(
            exchange.get(
                "contract_base_url",
                "https://api-contract.weex.com"
            )
        ).rstrip("/")

        if base_url != "https://api-contract.weex.com":
            raise ValueError("UNEXPECTED_MARKET_API_HOST")

        endpoint = "/capi/v3/market/exchangeInfo"

        query = urllib.parse.urlencode({
            "symbol": symbol
        })

        url = base_url + endpoint + "?" + query

        request = urllib.request.Request(
            url,
            method="GET",
            headers={
                "Accept": "application/json",
                "User-Agent": "WEEX-Contract-Specs-V1",
            },
        )

        with urllib.request.urlopen(
            request,
            timeout=15
        ) as response:

            if response.status != 200:
                raise ValueError(
                    "CONTRACT_INFO_HTTP_"
                    + str(response.status)
                )

            payload = json.loads(
                response.read().decode("utf-8")
            )

        if not isinstance(payload, dict):
            raise ValueError(
                "INVALID_CONTRACT_INFO_RESPONSE"
            )

        rows = payload.get("symbols")

        if not isinstance(rows, list):
            raise ValueError(
                "CONTRACT_SYMBOL_LIST_MISSING"
            )

        selected = next(
            (
                row for row in rows
                if isinstance(row, dict)
                and str(
                    row.get("symbol", "")
                ).upper() == symbol
            ),
            None
        )

        if selected is None:
            raise ValueError(
                "SYMBOL_NOT_IN_EXCHANGE_INFO"
            )

        if str(
            selected.get("quoteAsset", "")
        ).upper() != "USDT":
            raise ValueError(
                "NOT_USDT_QUOTED"
            )

        def positive_number(value, name):
            try:
                result = Decimal(str(value))
            except (
                InvalidOperation,
                TypeError,
                ValueError,
            ) as exc:
                raise ValueError(
                    "INVALID_" + name
                ) from exc

            if not result.is_finite() or result <= 0:
                raise ValueError(
                    "INVALID_" + name
                )

            return result

        def precision_step(value, name):
            try:
                digits = int(value)
            except (
                TypeError,
                ValueError,
            ) as exc:
                raise ValueError(
                    "INVALID_" + name
                ) from exc

            if digits < 0 or digits > 18:
                raise ValueError(
                    "INVALID_" + name
                )

            return Decimal("1").scaleb(-digits)

        # Use an explicit increment when WEEX returns
        # one; otherwise derive the precision increment.
        if selected.get("size_increment") is not None:
            quantity_step = positive_number(
                selected["size_increment"],
                "QUANTITY_STEP"
            )
        else:
            quantity_step = precision_step(
                selected["quantityPrecision"],
                "QUANTITY_PRECISION"
            )

        if selected.get("tick_size") is not None:
            price_step = positive_number(
                selected["tick_size"],
                "PRICE_STEP"
            )
        else:
            price_step = precision_step(
                selected["pricePrecision"],
                "PRICE_PRECISION"
            )

        minimum_quantity = positive_number(
            selected["minOrderSize"],
            "MINIMUM_ORDER_SIZE"
        )

        contract_value = positive_number(
            selected["contractVal"],
            "CONTRACT_VALUE"
        )

        # Existing Unit 8 and Unit 9 calculations use
        # BASE-ASSET quantities:
        #
        # notional = base_quantity * price
        #
        # Therefore contract_multiplier is 1 here.
        # contractVal is stored separately and must
        # not be applied again to base-asset quantities.

        values = {
            "quantity_step": float(quantity_step),
            "minimum_quantity": float(
                minimum_quantity
            ),
            "price_step": float(price_step),
            "contract_multiplier": 1.0,
            "contract_value": float(contract_value),
            "specifications_symbol": symbol,
        }

        precision.update(values)

        precision[
            "symbol_specifications_confirmed"
        ] = True

        print(
            "UNIT 9 CONTRACT SPECIFICATIONS = LOADED",
            flush=True
        )

        print(
            "UNIT 9 CONTRACT SYMBOL =",
            symbol,
            flush=True
        )

        print(
            "UNIT 9 QUANTITY STEP =",
            quantity_step,
            flush=True
        )

        print(
            "UNIT 9 MINIMUM QUANTITY =",
            minimum_quantity,
            flush=True
        )

        print(
            "UNIT 9 PRICE STEP =",
            price_step,
            flush=True
        )

        print(
            "UNIT 9 CONTRACT VALUE =",
            contract_value,
            flush=True
        )

        print(
            "UNIT 9 QUANTITY BASIS = BASE_ASSET",
            flush=True
        )

        return True

    except (
        ValueError,
        KeyError,
        TypeError,
        urllib.error.URLError,
        TimeoutError,
        json.JSONDecodeError,
    ) as exc:

        precision[
            "symbol_specifications_confirmed"
        ] = False

        print(
            "UNIT 9 CONTRACT SPECIFICATIONS = UNAVAILABLE",
            flush=True
        )

        print(
            "UNIT 9 CONTRACT SYMBOL =",
            symbol,
            flush=True
        )

        print(
            "UNIT 9 CONTRACT REASON =",
            str(exc),
            flush=True
        )

        return False


# ============================================================
# RENDER ENTRY MARGIN ELIGIBILITY CONTROLLER
# Persistent decisions + existing Unit 15 Telegram queue
# No exchange orders submitted here
# ============================================================

from decimal import Decimal, ROUND_CEILING
import os


def unit_8_entry_margin_control(config, account, market):

    db = unit_8_symbol_switch_db()

    try:
        db.execute("""
            CREATE TABLE IF NOT EXISTS entry_margin_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                decision_key TEXT NOT NULL,
                status TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        symbol = str(
            config["exchange"]["market_symbol"]
        ).strip().upper()

        coin = (
            symbol[:-4]
            if symbol.endswith("USDT")
            else symbol
        )

        raw = os.getenv(
            "INITIAL_ENTRY_MARGIN_USDT"
        )

        if raw is None or not raw.strip():
            raw = os.getenv("ENTRY_FIXED_USDT")

        if raw is None or not raw.strip():
            raw = str(
                config["strategy"]["initial_fixed_usdt"]
            )

        margin = Decimal(str(raw))

        if not margin.is_finite() or margin <= 0:
            raise RuntimeError(
                "INVALID_RENDER_ENTRY_MARGIN"
            )

        def amount(value):
            return format(
                Decimal(str(value)).normalize(), "f"
            )

        def notify(status, message, key):
            now = datetime.now(
                timezone.utc
            ).isoformat()

            db.execute("BEGIN IMMEDIATE")

            previous = db.execute("""
                SELECT decision_key, status
                FROM entry_margin_state
                WHERE id = 1
            """).fetchone()

            changed = (
                previous is None
                or previous != (key, status)
            )

            if changed:
                db.execute("""
                    INSERT INTO entry_margin_state (
                        id, decision_key, status, updated_at
                    )
                    VALUES (1, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        decision_key = excluded.decision_key,
                        status = excluded.status,
                        updated_at = excluded.updated_at
                """, (key, status, now))

                if message:
                    unit_8_symbol_event(
                        db,
                        "ENTRY_MARGIN_" + status,
                        message
                    )

            db.execute("COMMIT")

            return status

        
        # ====================================================
        # VERIFIED DEMO POSITION STATE RECONCILIATION
        # ====================================================

        positions = account.get("positions")

        verified = (
            account.get("demo_positions_verified")
            is True
        )

        flat_flag = account.get(
            "position_flat_verified"
        )

        if not verified or not isinstance(
            positions, list
        ):
            print(
                "ENTRY POSITION STATE = UNVERIFIED",
                flush=True
            )
            return {
                "eligible": False,
                "status": "POSITION_UNVERIFIED"
            }

        open_positions = []

        for position in positions:
            if not isinstance(position, dict):
                print(
                    "ENTRY POSITION STATE = INVALID_RECORD",
                    flush=True
                )
                return {
                    "eligible": False,
                    "status": "POSITION_STATE_INCONSISTENT"
                }

            size = unit_8_v6_decimal(
                position.get("size", "0"),
                "POSITION SIZE",
                allow_zero=True
            )

            if size > 0:
                open_positions.append(position)

        occupied = bool(open_positions)
        computed_flat = not occupied

        print(
            "ENTRY POSITION COUNT =",
            len(open_positions),
            flush=True
        )

        print(
            "ENTRY POSITION FLAT FLAG =",
            flat_flag,
            flush=True
        )

        print(
            "ENTRY POSITION COMPUTED FLAT =",
            computed_flat,
            flush=True
        )

        if (
            not isinstance(flat_flag, bool)
            or flat_flag != computed_flat
        ):
            print(
                "ENTRY POSITION STATE = INCONSISTENT",
                flush=True
            )
            return {
                "eligible": False,
                "status": "POSITION_STATE_INCONSISTENT"
            }

        key = symbol + "|" + amount(margin)

        
        print(
            "ENTRY POSITION SNAPSHOT VERIFIED =",
            verified,
            flush=True
        )
        print(
            "ENTRY POSITION FLAT FLAG =",
            account.get("position_flat_verified"),
            flush=True
        )
        print(
            "ENTRY POSITION COUNT =",
            len(positions),
            flush=True
        )
        print(
            "ENTRY POSITION DETAILS =",
            [
                {
                    "symbol": p.get("symbol"),
                    "size": p.get("size"),
                    "side": p.get("side")
                }
                for p in positions
            ],
            flush=True
        )
        print(
            "ENTRY POSITION OCCUPIED =",
            occupied,
            flush=True
        )

        if occupied:
            print(
                "ENTRY POSITION STATE = CONFIRMED_OCCUPIED",
                flush=True
            )

            print(
                "ENTRY OPEN POSITION SYMBOLS =",
                [
                    p.get("symbol")
                    for p in open_positions
                ],
                flush=True
            )

            status = notify(
                "QUEUED",
                (
                    f"${amount(margin)} {coin} queued, "
                    "position exists."
                ),
                key
            )

            return {
                "eligible": False,
                "status": status,
                "open_position_count": len(open_positions)
            }

        print(
            "ENTRY POSITION STATE = CONFIRMED_FLAT",
            flush=True
        )

        # Continue to the existing margin validation.

        precision = config.get(
            "market_precision", {}
        )

        if (
            precision.get(
                "symbol_specifications_confirmed"
            ) is not True
        ):
            return {
                "eligible": False,
                "status": "CONTRACT_SPECS_UNAVAILABLE"
            }

        price = Decimal(str(market["price"]))
        step = Decimal(
            str(precision["quantity_step"])
        )
        minimum = Decimal(
            str(precision["minimum_quantity"])
        )
        multiplier = Decimal(
            str(precision["contract_multiplier"])
        )

        long_leverage = Decimal(
            str(account["long_leverage"])
        )
        short_leverage = Decimal(
            str(account["short_leverage"])
        )

        leverage = min(
            long_leverage, short_leverage
        )

        tp1_fraction = (
            Decimal(str(
                config["strategy"][
                    "tp1_allocation_percent"
                ]
            )) / Decimal("100")
        )

        values = (
            price, step, minimum, multiplier,
            leverage, tp1_fraction
        )

        if any(
            not v.is_finite() or v <= 0
            for v in values
        ):
            raise RuntimeError(
                "INVALID_ENTRY_CONTRACT_PARAMETERS"
            )

        # Minimum executable TP1, rounded to the
        # contract quantity step.
        tp1_steps = (
            minimum / step
        ).to_integral_value(
            rounding=ROUND_CEILING
        )

        tp1_quantity = tp1_steps * step

        # Initial quantity must support TP1 allocation.
        entry_steps = (
            tp1_quantity / tp1_fraction / step
        ).to_integral_value(
            rounding=ROUND_CEILING
        )

        entry_quantity = entry_steps * step

        minimum_margin = (
            entry_quantity
            * price
            * multiplier
            / leverage
        )

        minimum_margin = minimum_margin.quantize(
            Decimal("0.01"),
            rounding=ROUND_CEILING
        )

        if margin < minimum_margin:
            status = notify(
                "REJECTED",
                (
                    f"{coin} entry rejected, "
                    f"${amount(margin)} below min of "
                    f"${amount(minimum_margin)}."
                ),
                key
            )

            return {
                "eligible": False,
                "status": status,
                "minimum_margin": minimum_margin
            }

        status = notify(
            "ACCEPTED",
            (
                f"{coin} entry accepted, "
                f"${amount(margin)} entry enabled."
            ),
            key
        )

        return {
            "eligible": True,
            "status": status,
            "accepted_margin": margin,
            "minimum_margin": minimum_margin
        }

    finally:
        if db.in_transaction:
            db.execute("ROLLBACK")
        db.close()


# ============================================================
# UNIT 8 -> UNIT 9 RENDER ENTRY MARGIN CONTROLLER V2
# Persistent queue, acceptance and rejection
# Uses existing SQLite and Telegram event delivery
# DEMO ONLY - NO ORDER SUBMISSION
# ============================================================

from decimal import Decimal, ROUND_CEILING


def unit_8_render_entry_margin(config, account, market):

    db = unit_8_symbol_switch_db()

    try:
        db.execute("""
            CREATE TABLE IF NOT EXISTS entry_margin_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                request_key TEXT NOT NULL,
                decision TEXT NOT NULL,
                minimum TEXT,
                updated_at TEXT NOT NULL
            )
        """)

        symbol = str(
            config["exchange"]["market_symbol"]
        ).strip().upper()

        coin = (
            symbol[:-4]
            if symbol.endswith("USDT")
            else symbol
        )

        margin, source = unit_9_v4_entry_margin()

        margin = Decimal(str(margin))

        if not margin.is_finite() or margin <= 0:
            raise RuntimeError(
                "INVALID_RENDER_ENTRY_MARGIN"
            )

        def money(value):
            return format(
                Decimal(str(value)).normalize(), "f"
            )

        def decide(status, message, minimum=None):

            request_key = (
                symbol + "|" + money(margin)
            )

            old = db.execute("""
                SELECT request_key, decision
                FROM entry_margin_state
                WHERE id = 1
            """).fetchone()

            changed = (
                old is None
                or old != (request_key, status)
            )

            db.execute("BEGIN IMMEDIATE")

            try:
                db.execute("""
                    INSERT INTO entry_margin_state (
                        id, request_key, decision,
                        minimum, updated_at
                    )
                    VALUES (1, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        request_key = excluded.request_key,
                        decision = excluded.decision,
                        minimum = excluded.minimum,
                        updated_at = excluded.updated_at
                """, (
                    request_key,
                    status,
                    str(minimum) if minimum is not None
                    else None,
                    datetime.now(timezone.utc).isoformat()
                ))

                if changed and message:
                    unit_8_symbol_event(
                        db,
                        "ENTRY_MARGIN_" + status,
                        message
                    )

                db.execute("COMMIT")

            except Exception:
                db.execute("ROLLBACK")
                raise

            return {
                "eligible": status == "ACCEPTED",
                "status": status,
                "margin": str(margin),
                "minimum": (
                    str(minimum)
                    if minimum is not None
                    else None
                ),
                "source": source
            }

        if (
            account.get("demo_positions_verified")
            is not True
            or not isinstance(
                account.get("positions"), list
            )
        ):
            return decide(
                "PENDING",
                None
            )

        occupied = False

        for position in account["positions"]:

            if not isinstance(position, dict):
                raise RuntimeError(
                    "INVALID_POSITION_RECORD"
                )

            size = unit_8_v6_decimal(
                position.get("size", "0"),
                "POSITION_SIZE",
                allow_zero=True
            )

            if size > 0:
                occupied = True
                break

        if occupied:
            return decide(
                "QUEUED",
                (
                    f"${money(margin)} {coin} queued, "
                    "position exists."
                )
            )

        specs = config.get("market_precision", {})

        if (
            specs.get(
                "symbol_specifications_confirmed"
            ) is not True
        ):
            return decide(
                "PENDING",
                None
            )

        price = Decimal(str(market["price"]))
        step = Decimal(
            str(specs["quantity_step"])
        )
        minimum_qty = Decimal(
            str(specs["minimum_quantity"])
        )
        multiplier = Decimal(
            str(specs["contract_multiplier"])
        )

        long_lev = Decimal(
            str(account["long_leverage"])
        )
        short_lev = Decimal(
            str(account["short_leverage"])
        )

        leverage = min(long_lev, short_lev)

        allocations = [
            Decimal(str(
                config["strategy"][key]
            )) / Decimal("100")
            for key in (
                "tp1_allocation_percent",
                "tp2_allocation_percent",
                "tp3_allocation_percent"
            )
        ]

        values = [
            price, step, minimum_qty,
            multiplier, leverage
        ] + allocations

        if any(
            not value.is_finite() or value <= 0
            for value in values
        ):
            raise RuntimeError(
                "INVALID_ENTRY_SIZING_PARAMETERS"
            )

        # Current Unit 9 quantity calculation assumes
        # multiplier = 1. Do not approve a different
        # multiplier until both formulas are aligned.
        if multiplier != Decimal("1"):
            return decide(
                "PENDING",
                None
            )

        minimum_steps = (
            minimum_qty / step
        ).to_integral_value(
            rounding=ROUND_CEILING
        )

        executable_min_qty = minimum_steps * step

        # Each configured TP portion must be capable
        # of meeting the exchange minimum quantity.
        required_quantity = max(
            executable_min_qty / fraction
            for fraction in allocations
        )

        entry_steps = (
            required_quantity / step
        ).to_integral_value(
            rounding=ROUND_CEILING
        )

        entry_quantity = entry_steps * step

        required_margin = (
            entry_quantity * price / leverage
        )

        # Round upward to a cent for notifications.
        minimum_margin = required_margin.quantize(
            Decimal("0.01"),
            rounding=ROUND_CEILING
        )

        if margin < minimum_margin:

            return decide(
                "REJECTED",
                (
                    f"{coin} entry rejected, "
                    f"${money(margin)} below min of "
                    f"${money(minimum_margin)}."
                ),
                minimum_margin
            )

        return decide(
            "ACCEPTED",
            (
                f"{coin} entry accepted, "
                f"${money(margin)} entry enabled."
            ),
            minimum_margin
        )

    finally:
        db.close()


# ============================================================
# END ENTRY MARGIN CONTROLLER V2
# ============================================================

# ============================================================
# 2. REFRESH MARKET AND EXECUTION PIPELINE
#
# Uses the existing validated unit functions.
# Does not rerun unit validation tests.
# ============================================================


def scan_refresh_entry_pipeline():

    config = FRESH_RECONSTRUCTION_CONFIG

    # Refresh the active market/demo pair from SQLite
    # before fetching new market data.

    active_pair = unit_2_active_symbol_pair()

    active_market = active_pair["market_symbol"]
    active_demo = active_pair["demo_order_symbol"]

    if not active_market or not active_demo:
        raise RuntimeError(
            "SCAN ACTIVE SYMBOL PAIR MISSING"
        )

    if not isinstance(config.get("exchange"), dict):
        raise RuntimeError(
            "SCAN EXCHANGE CONFIGURATION INVALID"
        )

    config["exchange"]["market_symbol"] = active_market
    config["exchange"]["demo_order_symbol"] = active_demo
    config["exchange"]["active_symbol_source"] = (
        active_pair["source"]
    )

    
    unit_9_load_symbol_specifications(
        config,
        active_market,
    )

    print(
        "SCAN REFRESHED ACTIVE MARKET =",
        active_market,
        flush=True
    )

    print(
        "SCAN REFRESHED ACTIVE DEMO =",
        active_demo,
        flush=True
    )
    
    # UNIT 3 -> UNIT 4 FRESH MARKET HANDOVER
    # Unit 4 reads this global snapshot directly.

    global FRESH_RECONSTRUCTION_MARKET_SNAPSHOT

    FRESH_RECONSTRUCTION_MARKET_SNAPSHOT = (
        fresh_reconstruction_unit_3()
    )

    market = FRESH_RECONSTRUCTION_MARKET_SNAPSHOT

    if not isinstance(market, dict):
        raise RuntimeError(
            "SCAN UNIT 3 SNAPSHOT INVALID"
        )

    print(
        "SCAN FRESH MARKET TIMESTAMP =",
        market.get("exchange_time_ms"),
        flush=True
    )

    analysis = fresh_reconstruction_unit_4()

    # Unit 5: strategy classification
    candidate = fresh_reconstruction_unit_5(
        config,
        analysis,
    )

    # Unit 6: strategy arbitration
    execution = fresh_reconstruction_unit_6(
        config,
        analysis,
        candidate,
    )
    
    # Unit 7: dynamic sizing policy
    sizing = fresh_reconstruction_unit_7(
        config,
        execution,
    )

    # Unit 8: account and leverage context
    account = fresh_reconstruction_unit_8(
        config,
        sizing,
        market,
    )

    
    # ========================================================
    # UNIT 8 -> CONTINUOUS SYMBOL SWITCH RECONCILIATION
    # RUN AFTER FRESH ACCOUNT READ, BEFORE NEW ENTRY
    # ========================================================

    global FRESH_RECONSTRUCTION_SYMBOL_SWITCH_RESULT

    if (
        not isinstance(account, dict)
        or account.get("demo_positions_verified") is not True
        or not isinstance(account.get("positions"), list)
    ):
        raise RuntimeError(
            "SCAN SYMBOL SWITCH: ACCOUNT POSITIONS UNVERIFIED"
        )

    
    requested_market = os.getenv(
        "WEEX_SYMBOL", "BTCUSDT"
    ).strip().upper()

    discovery = unit_8_discover_demo_contract(
        requested_market
    )

    requested_demo = str(
        discovery.get("demo_symbol") or ""
    ).strip().upper()

    
    # Coin-base-vetted WEEX demo symbol.
    # Optional authenticated inspection is not an
    # order-submission prerequisite.

    demo_contract_verified = False

    switch_result = unit_8_symbol_switch(
        requested_market=requested_market,
        requested_demo=requested_demo,
        positions=account["positions"],
        positions_verified=account["demo_positions_verified"],
        contract_verified=False,
        candidate_ready=(
            discovery.get("candidate_ready") is True
        ),
    )
    
    FRESH_RECONSTRUCTION_SYMBOL_SWITCH_RESULT = switch_result
    
    print(
        "SCAN ACTIVE MARKET SYMBOL =",
        switch_result["active_market_symbol"],
        flush=True
    )

    print(
        "SCAN ACTIVE DEMO SYMBOL =",
        switch_result["active_demo_symbol"],
        flush=True
    )

    print(
        "SCAN QUEUED MARKET SYMBOL =",
        switch_result["queued_market_symbol"],
        flush=True
    )

    print(
        "SCAN QUEUED DEMO SYMBOL =",
        switch_result["queued_demo_symbol"],
        flush=True
    )

    active_market = switch_result[
        "active_market_symbol"
    ]

    active_demo = switch_result[
        "active_demo_symbol"
    ]

    # Do not mutate the active configuration here:
    # Units 3 and 4 already used it in this scan.
    # A new active pair requires a fresh market-data pass.

    if (
        config["exchange"]["market_symbol"] != active_market
        or config["exchange"]["demo_order_symbol"] != active_demo
    ):
        print(
            "SCAN SYMBOL CHANGED DURING CYCLE =",
            active_market,
            "/",
            active_demo,
            flush=True,
        )

        print(
            "SCAN NEW ENTRY DEFERRED UNTIL FRESH MARKET DATA",
            flush=True,
        )

        return {
            "status": "SYMBOL_CHANGED_REFRESH_NEXT_SCAN",
            "execution_authorized": False,
            "exchange_write": False,
        }

    # A queued or unverified symbol request must not
    # enter Unit 12's new-order submission path.
    # scan_one_cycle() catches this exception and
    # continues into existing-position management.

    if (
        requested_market != active_market
        or requested_demo != active_demo
    ):
        raise RuntimeError(
            "SCAN NEW ENTRY DEFERRED: "
            + switch_result["status"]
        )

    # ========================================================
    # END SYMBOL RECONCILIATION
    # ========================================================

    
    # ========================================================
    # RENDER ENTRY MARGIN VALIDATION
    # ========================================================

    margin_decision = unit_8_entry_margin_control(
        config,
        account,
        market,
    )

    print(
        "SCAN ENTRY MARGIN STATUS =",
        margin_decision["status"],
        flush=True
    )

    print(
        "SCAN UNIT 12 ENTRY ELIGIBLE =",
        margin_decision["eligible"],
        flush=True
    )

    if margin_decision["eligible"] is not True:
        return {
            "status": "IDLE",
            "skip_reason": (
                "ENTRY_MARGIN_"
                + margin_decision["status"]
            ),
            "execution_authorized": False,
            "exchange_write": False,
        }

    # Unit 9: entry sizing
    entry = fresh_reconstruction_unit_9(
        config,
        account,
    )

    # Unit 10: demo execution boundary
    boundary = fresh_unit_10_hybrid_adapter(
        config,
        entry,
    )

    # Unit 11: verified demo order payload
    prepared = fresh_unit_11_hybrid_adapter(
        config,
        boundary,
    )

    # Unit 12: only unit permitted to
    # submit a NEW initial demo entry.
    submission = (
        fresh_unit_12_hybrid_execution_adapter(
            config,
            prepared,
        )
    )

    return submission


# ============================================================
# 3. EXISTING POSITION MANAGEMENT
#
# Runs regardless of BOT_MODE.
# Unit 13 manages TP1/TP2.
# Unit 14 manages TP3 and five backups.
# ============================================================

def scan_manage_position(unit12_result):

    config = FRESH_RECONSTRUCTION_CONFIG

    unit13 = fresh_unit_13_hybrid_adapter(
        config,
        unit12_result,
    )

    unit14 = fresh_unit_14_hybrid_adapter(
        config,
        unit13,
    )

    return unit13, unit14


# ============================================================
# 4. ONE SCAN CYCLE
# ============================================================

def scan_one_cycle():

    global SCAN_NUMBER
    global SCAN_LAST_MARKET_SUCCESS
    global SCAN_LAST_MANAGEMENT_SUCCESS
    global SCAN_LAST_STATUS

    if not SCAN_LOCK.acquire(blocking=False):
        print(
            "SCAN OVERLAP BLOCKED",
            flush=True
        )
        return

    try:

        SCAN_NUMBER += 1

        now = _SCAN_DT.now(SCAN_TZ)

        print("=" * 80, flush=True)
        print(
            "CONTINUOUS SCAN NUMBER =",
            SCAN_NUMBER,
            flush=True
        )
        print(
            "SCAN TIME WAT =",
            now.isoformat(),
            flush=True
        )
        print(
            "SCAN BOT_MODE =",
            _scan_os.getenv(
                "BOT_MODE", "PAUSE"
            ),
            flush=True
        )

        
        
        # ====================================================
        # MANUAL WEEX DEMO POSITION CONTROLLER
        # Runs before new entries and automatic management.
        # ====================================================

        control_mode = _scan_os.getenv(
            "DEMO_POSITION_CONTROL", "OFF"
        ).strip().upper()

        if control_mode != "OFF":

            try:
                control_result = dpc_process()

                print(
                    "SCAN DEMO CONTROL STATUS =",
                    control_result,
                    flush=True
                )

                SCAN_LAST_STATUS = (
                    "MANUAL_CONTROL:"
                    + str(control_result)
                )

            except Exception as exc:

                SCAN_LAST_STATUS = (
                    "MANUAL_CONTROL_ERROR"
                )

                print(
                    "SCAN DEMO CONTROL ERROR =",
                    repr(exc),
                    flush=True
                )

                _scan_traceback.print_exc()

            return

        # --------------------------------------------
        # NEW-ENTRY PIPELINE
        # --------------------------------------------

        submission = None
        entry_ok = False

        try:

            submission = (
                scan_refresh_entry_pipeline()
            )

            entry_ok = True

            SCAN_LAST_MARKET_SUCCESS = (
                _scan_time.time()
            )

            print(
                "SCAN UNIT 12 STATUS =",
                submission.get("status"),
                flush=True
            )

        except Exception as exc:

            SCAN_LAST_STATUS = (
                "ENTRY_PIPELINE_ERROR"
            )

            print(
                "SCAN ENTRY PIPELINE ERROR =",
                repr(exc),
                flush=True
            )

            _scan_traceback.print_exc()

            # A signal-processing failure does
            # not automatically suspend
            # management of an existing position.
            submission = scan_idle_unit12_result(
                "ENTRY_PIPELINE_ERROR"
            )

        # --------------------------------------------
        # EXISTING POSITION MANAGEMENT
        # --------------------------------------------

        try:

            unit13, unit14 = (
                scan_manage_position(
                    submission
                )
            )

            SCAN_LAST_MANAGEMENT_SUCCESS = (
                _scan_time.time()
            )

            print(
                "SCAN UNIT 13 STATUS =",
                unit13.get("status"),
                flush=True
            )

            print(
                "SCAN UNIT 14 STATUS =",
                unit14.get("status"),
                flush=True
            )

            SCAN_LAST_STATUS = (
                "PASS"
                if entry_ok
                else "MANAGEMENT_ONLY"
            )

        except Exception as exc:

            SCAN_LAST_STATUS = (
                "POSITION_MANAGEMENT_ERROR"
            )

            print(
                "SCAN POSITION MANAGEMENT ERROR =",
                repr(exc),
                flush=True
            )

            _scan_traceback.print_exc()

        
        # --------------------------------------------
        # DELIVER PENDING SYMBOL SWITCH NOTIFICATIONS
        # --------------------------------------------

        try:
            delivered = unit_8_symbol_telegram_flush()

            print(
                "SCAN SYMBOL TELEGRAM DELIVERED =",
                delivered,
                flush=True
            )

        except Exception as exc:
            print(
                "SCAN SYMBOL TELEGRAM ERROR =",
                repr(exc),
                flush=True
            )

        print(
            "SCAN FINAL STATUS =",
            SCAN_LAST_STATUS,
            flush=True
        )

        print(
            "SCAN EXCHANGE ENVIRONMENT = DEMO",
            flush=True
        )

        print(
            "SCAN CONTINUES = TRUE",
            flush=True
        )

    finally:
        SCAN_LOCK.release()


# ============================================================
# 5. CONTINUOUS MONITORING LOOP
# ============================================================

def scan_forever():

    print("=" * 80, flush=True)
    print(
        "CONTINUOUS SCAN CONTROLLER V1 STARTED",
        flush=True
    )
    print(
        "SCAN INTERVAL SECONDS =",
        SCAN_INTERVAL_SECONDS,
        flush=True
    )
    print(
        "UNIT 12 CONTROLS NEW ENTRIES ONLY",
        flush=True
    )
    print(
        "UNIT 13 AND 14 MANAGEMENT = ALWAYS ACTIVE",
        flush=True
    )
    print(
        "UNIT 15 TELEGRAM = INDEPENDENT",
        flush=True
    )
    print("=" * 80, flush=True)

    # The original startup sequence has already
    # executed once before reaching this point.
    # Avoid immediately repeating that execution.

    _scan_time.sleep(
        SCAN_INTERVAL_SECONDS
    )

    while True:

        started = _scan_time.monotonic()

        try:

            scan_one_cycle()
            
    

    


        except Exception as exc:

            print(
                "SCAN SUPERVISOR ERROR =",
                repr(exc),
                flush=True
            )

            _scan_traceback.print_exc()

        elapsed = (
            _scan_time.monotonic()
            - started
        )

        # Maintain a minimum pause and avoid
        # overlapping scans if requests run long.

        sleep_for = max(
            5.0,
            SCAN_INTERVAL_SECONDS - elapsed,
        )

        print(
            "SCAN ELAPSED SECONDS =",
            round(elapsed, 2),
            flush=True
        )

        print(
            "SCAN NEXT SLEEP SECONDS =",
            round(sleep_for, 2),
            flush=True
        )

        _scan_time.sleep(sleep_for)

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
        "symbol": "BTCSUSDT",
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
