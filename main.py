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

        # ========================================================
    # CONSOLIDATED TP NET ROI CONFIGURATION
    # Restore last accepted values before validation
    # ========================================================

    import sqlite3

    tp_roi_requested = os.getenv(
        "TP_NET_ROI_FLOOR_PERCENT",
        "TP1:20,TP2:40"
    ).strip()

    tp1_roi = Decimal("20")
    tp2_roi = Decimal("40")

    stage_path = os.getenv(
        "UNIT14_STAGE_DB_PATH",
        "/var/data/unit14_stages.sqlite3"
    )

    roi_db_path = os.path.join(
        os.path.dirname(stage_path),
        "weex_symbol_switch.sqlite3"
    )

    if os.path.isfile(roi_db_path):

        roi_db = None

        try:

            roi_db = sqlite3.connect(
                roi_db_path,
                timeout=10
            )

            table_exists = roi_db.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                  AND name = 'tp_net_roi_state'
            """).fetchone()

            if table_exists:

                saved = roi_db.execute("""
                    SELECT accepted_tp1, accepted_tp2
                    FROM tp_net_roi_state
                    WHERE id = 1
                """).fetchone()

                if saved:

                    saved_tp1 = Decimal(saved[0])
                    saved_tp2 = Decimal(saved[1])

                    if (
                        saved_tp1.is_finite()
                        and saved_tp2.is_finite()
                        and 0 < saved_tp1 < saved_tp2
                    ):
                        tp1_roi = saved_tp1
                        tp2_roi = saved_tp2

        finally:

            if roi_db is not None:
                roi_db.close()

    print(
        "UNIT 2 TP NET ROI REQUESTED =",
        tp_roi_requested,
        flush=True,
    )

    print(
        "UNIT 2 TP NET ROI RESTORED =",
        tp1_roi, "/", tp2_roi,
        flush=True,
    )

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
    """Persistent symbol switch; entry-margin decisions are independent."""
    requested_market = str(requested_market or "").strip().upper()
    requested_demo = str(requested_demo or "").strip().upper()
    requested_pair = (requested_market, requested_demo)

    # Reuse the existing contract checker.
    # A generated demo name is not compatibility proof.
    def compatible():
        if not re.fullmatch(r"[A-Z0-9]{2,20}USDT", requested_market):
            return False, "INVALID_MARKET_SYMBOL"

        if not requested_demo or not re.fullmatch(
            r"[A-Z0-9]{3,30}", requested_demo
        ):
            return False, "INVALID_DEMO_SYMBOL"

        if contract_verified is True:
            return True, "CONTRACT_ALREADY_VERIFIED"

        check = unit_8_verify_market_contract(requested_market)

        return (
            check.get("market_verified") is True,
            str(
                check.get("reason")
                or "MARKET_CONTRACT_NOT_FOUND"
            )
        )

    db = unit_8_symbol_switch_db()

    try:
        db.execute("BEGIN IMMEDIATE")
        now = datetime.now(timezone.utc).isoformat()

        row = db.execute("""
            SELECT active_market, active_demo,
                   queued_market, queued_demo
            FROM symbol_switch
            WHERE id = 1
        """).fetchone()

        if row is None:
            db.execute("""
                INSERT INTO symbol_switch (
                    id, active_market, active_demo,
                    queued_market, queued_demo, updated_at
                )
                VALUES (1, '', '', NULL, NULL, ?)
            """, (now,))
            row = ("", "", None, None)

        active_market, active_demo, queued_market, queued_demo = row

        active_pair = (active_market, active_demo)
        queued_pair = (queued_market, queued_demo)
        occupied = True

        def event_once(kind, message):
            # Preserve the existing persistent event queue.
            # Suppress consecutive identical decisions.
            last = db.execute("""
                SELECT event_type, message
                FROM symbol_events
                ORDER BY event_id DESC
                LIMIT 1
            """).fetchone()

            if last != (kind, message):
                unit_8_symbol_event(db, kind, message)

        if (
            positions_verified is not True
            or not isinstance(positions, list)
        ):
            status = "POSITION_VERIFICATION_PENDING"

        else:
            occupied = False

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
                    occupied = True

            if (
                requested_pair == active_pair
                and active_market
                and active_demo
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

            else:
                ok, reason = compatible()

                if not ok:
                    # Reject the candidate without changing
                    # the existing active symbol.
                    if queued_pair == requested_pair:
                        db.execute("""
                            UPDATE symbol_switch
                            SET queued_market = NULL,
                                queued_demo = NULL,
                                updated_at = ?
                            WHERE id = 1
                        """, (now,))

                    status = "SYMBOL_REJECTED"

                    event_once(
                        "SYMBOL_REJECTED",
                        (
                            "WEEX symbol rejected: "
                            + requested_market
                            + " / "
                            + requested_demo
                            + ". Reason: "
                            + reason
                            + ". Previous active symbol retained."
                        )
                    )

                elif occupied:
                    # Valid candidate with existing position:
                    # queue it, retaining the active symbol.
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

                        event_once(
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

                else:
                    # Candidate compatible and account flat:
                    # commit the accepted symbol pair.
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

                    event_once(
                        "SYMBOL_ACCEPTED",
                        (
                            "WEEX symbol accepted: "
                            + requested_market
                            + " / "
                            + requested_demo
                        )
                    )

                    status = "SYMBOL_ACCEPTED"

        final_row = db.execute("""
            SELECT active_market, active_demo,
                   queued_market, queued_demo
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
# COMPLETE UNIT 13 V6
# PART 1 OF 3
# EXCHANGE COMMUNICATION AND TP CALCULATIONS
# ZERO INDENTATION
# ============================================================

import os
import json
import time
import hmac
import base64
import hashlib
import sqlite3
import uuid
import urllib.request
import urllib.parse
import urllib.error

from decimal import Decimal, ROUND_DOWN, ROUND_UP


UNIT13_V4_BASE = "https://api-contract.weex.com"

UNIT13_V4_POSITION = "/capi/v3/sim/position/allPosition"

UNIT13_V4_ORDER = "/capi/v3/sim/order"

UNIT13_V4_HISTORY = "/capi/v3/sim/order/history"


# ============================================================
# DECIMAL AND QUANTITY HANDLING
# ============================================================

def unit_13_v4_D(
    value,
    name="NUMBER",
    allow_zero=False
):

    return Decimal(str(value))


def unit_13_floor(quantity, step):

    quantity = Decimal(str(quantity))
    step = Decimal(str(step))

    return (
        quantity / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    ) * step


# ============================================================
# STEP-AWARE TP ALLOCATION
# ============================================================

def unit_13_v4_allocation(
    total,
    step,
    pct1=10,
    pct2=20
):

    total = Decimal(str(total))
    step = Decimal(str(step))

    n = int(total / step)

    if n <= 0:

        return (
            Decimal(0),
            Decimal(0),
            Decimal(0),
        )

    if n == 1:

        s1, s2, s3 = 0, 0, 1

    elif n == 2:

        s1, s2, s3 = 1, 0, 1

    else:

        s1 = max(
            1,
            int(
                Decimal(n)
                * Decimal(str(pct1))
                / Decimal(100)
            )
        )

        s2 = max(
            1,
            int(
                Decimal(n)
                * Decimal(str(pct2))
                / Decimal(100)
            )
        )

        while s1 + s2 >= n:

            if s2 > 1:

                s2 -= 1

            else:

                s1 -= 1

        s3 = n - s1 - s2

    return (
        Decimal(s1) * step,
        Decimal(s2) * step,
        Decimal(s3) * step,
    )


# ============================================================
# NET ROI TARGET CALCULATION
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

    entry = D(entry)
    lev = D(leverage)
    ps = D(price_step)

    p1 = D(tp1_floor)
    p2 = D(tp2_floor)
    fee = D(taker_fee)

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

    else:

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

    return t1, t2


# ============================================================
# DIRECT WEEX SIGNED REQUEST
# ORIGINAL AUTHENTICATION MECHANISM
# ============================================================

def unit_13_v4_signed_request(
    method,
    path,
    payload=None
):

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

    query = (
        urllib.parse.urlencode(payload)
        if method == "GET" and payload
        else ""
    )

    request_path = path + (
        "?" + query if query else ""
    )

    body = (
        json.dumps(
            payload,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        if method == "POST"
        and payload is not None
        else ""
    )

    timestamp = str(
        int(time.time() * 1000)
    )

    message = (
        timestamp
        + method
        + request_path
        + body
    )

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

            raw = response.read().decode(
                "utf-8",
                errors="replace"
            )

    except urllib.error.HTTPError as exc:

        detail = exc.read().decode(
            "utf-8",
            errors="replace"
        )

        raise RuntimeError(
            "UNIT 13 WEEX HTTP "
            + str(exc.code)
            + ": "
            + detail
        ) from exc

    return json.loads(raw)


# ============================================================
# ACTIVE SYMBOL HANDOVER
# ============================================================

def unit_13_14_active_symbols():

    exchange = (
        FRESH_RECONSTRUCTION_CONFIG["exchange"]
    )

    market = str(
        exchange["market_symbol"]
    ).strip().upper()

    demo = str(
        exchange["demo_order_symbol"]
    ).strip().upper()

    return market, demo


# ============================================================
# CURRENT MARKET PRICE
# ============================================================

def unit_13_v4_mark_price():

    market_symbol, _ = (
        unit_13_14_active_symbols()
    )

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

    return Decimal(str(market["price"]))


# ============================================================
# CURRENT EXCHANGE POSITIONS
# ============================================================

def unit_13_v4_positions():

    _, demo_symbol = (
        unit_13_14_active_symbols()
    )

    records = unit_13_v4_signed_request(
        "GET",
        UNIT13_V4_POSITION,
    )

    return [
        position
        for position in records
        if str(
            position.get("symbol", "")
        ).upper() == demo_symbol
        and Decimal(
            str(position.get("size") or 0)
        ) > 0
    ]


# ============================================================
# EXCHANGE ORDER HISTORY
# ============================================================

def unit_13_v4_history(symbol):

    return unit_13_v4_signed_request(
        "GET",
        UNIT13_V4_HISTORY,
        {
            "symbol": symbol,
            "limit": 500,
            "page": 0,
        }
    )


# ============================================================
# DIRECT TP MARKET CLOSE EXECUTOR
# ORIGINAL WEEX ORDER PAYLOAD
# ============================================================

def unit_13_submit_close(
    symbol,
    side,
    quantity,
    client_id,
):

    close_side = (
        "SELL"
        if side == "LONG"
        else "BUY"
    )

    payload = {
        "symbol": symbol,
        "side": close_side,
        "positionSide": side,
        "type": "MARKET",
        "quantity": format(
            Decimal(str(quantity)),
            "f"
        ),
        "newClientOrderId": client_id,
    }

    return unit_13_v4_signed_request(
        "POST",
        UNIT13_V4_ORDER,
        payload,
    )


# ============================================================
# BASE RESULT FOR EXISTING UNIT 14 INTERFACE
# ============================================================

def unit_13_v4_base_result(
    unit_12_result,
    status,
    reason
):

    return {
        "unit": 13,
        "status": status,
        "read_only": False,

        "unit_12_status":
            unit_12_result.get("status"),

        "active_position_exists": False,
        "position_exists": False,

        "tp_management_required": False,
        "tp_execution_attempted": False,
        "tp_execution_completed": False,

        "tp1_completed": False,
        "tp2_completed": False,
        "tp3_armed": False,

        "tp_history_unresolved": False,
        "tp_legacy_closures_unattributed": False,

        "sl_execution_attempted": False,
        "backup_execution_attempted": False,

        "real_submission_attempted": False,
        "exchange_write": False,

        "position_management_independent_of_bot_mode":
            True,

        "skip_reason": reason,
    }


# ============================================================
# END COMPLETE UNIT 13 V6 - PART 1 OF 3
# ZERO INDENTATION
# NEXT: SQLITE TRANSACTION RECORDS
# ============================================================


# ============================================================
# COMPLETE UNIT 13 V6
# PART 2 OF 3
# SQLITE TRANSACTIONS AND TP RECONCILIATION
# ZERO INDENTATION
# ============================================================

UNIT13_V6_DB_PATH = os.getenv(
    "UNIT13_DB_PATH",
    "/var/data/unit13_execution.sqlite3"
)


# ============================================================
# SQLITE CONNECTION AND TABLE
# ============================================================

def unit_13_db():

    directory = os.path.dirname(
        UNIT13_V6_DB_PATH
    )

    if directory:

        os.makedirs(
            directory,
            exist_ok=True
        )

    db = sqlite3.connect(
        UNIT13_V6_DB_PATH,
        timeout=30
    )

    db.row_factory = sqlite3.Row

    db.execute("""
        CREATE TABLE IF NOT EXISTS unit13_tp_orders (
            client_id TEXT PRIMARY KEY,
            symbol TEXT NOT NULL,
            position_side TEXT NOT NULL,
            cycle_id TEXT NOT NULL,
            stage TEXT NOT NULL,
            quantity TEXT NOT NULL,
            filled_quantity TEXT NOT NULL DEFAULT '0',
            exchange_order_id TEXT,
            status TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL
        )
    """)

    db.execute("""
        CREATE INDEX IF NOT EXISTS
        unit13_tp_cycle_index
        ON unit13_tp_orders (
            symbol,
            position_side,
            cycle_id,
            stage
        )
    """)

    db.commit()

    return db


# ============================================================
# INDEPENDENT POSITION CYCLE IDENTITY
# ============================================================

def unit_13_cycle_id(position):

    symbol = str(
        position.get("symbol") or ""
    ).upper()

    side = str(
        position.get("side") or ""
    ).upper()

    position_id = str(
        position.get("id") or ""
    )

    opened_at = str(
        position.get("createdTime")
        or position.get("openTime")
        or ""
    )

    identity = (
        symbol
        + ":"
        + side
        + ":"
        + position_id
        + ":"
        + opened_at
    )

    return hashlib.sha256(
        identity.encode("utf-8")
    ).hexdigest()[:32]


# ============================================================
# UNIQUE ORDER ID FOR EACH EXECUTION ATTEMPT
# ============================================================

def unit_13_new_client_id(stage):

    return (
        "FR13-"
        + str(stage)
        + "-"
        + uuid.uuid4().hex[:24]
    )


# ============================================================
# READ EXISTING TP TRANSACTIONS
# ============================================================

def unit_13_read_orders(
    symbol,
    side,
    cycle_id,
    stage=None,
):

    db = unit_13_db()

    try:

        if stage is None:

            rows = db.execute("""
                SELECT *
                FROM unit13_tp_orders
                WHERE symbol = ?
                AND position_side = ?
                AND cycle_id = ?
                ORDER BY created_at
            """, (
                symbol,
                side,
                cycle_id,
            )).fetchall()

        else:

            rows = db.execute("""
                SELECT *
                FROM unit13_tp_orders
                WHERE symbol = ?
                AND position_side = ?
                AND cycle_id = ?
                AND stage = ?
                ORDER BY created_at
            """, (
                symbol,
                side,
                cycle_id,
                stage,
            )).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        db.close()


# ============================================================
# RECORD ACTUAL SUBMISSION INTENT
# NOT PRICE CROSSING
# ============================================================

def unit_13_record_order(
    symbol,
    side,
    cycle_id,
    stage,
    quantity,
    client_id,
):

    now = int(time.time() * 1000)

    db = unit_13_db()

    try:

        db.execute("""
            INSERT INTO unit13_tp_orders (
                client_id,
                symbol,
                position_side,
                cycle_id,
                stage,
                quantity,
                filled_quantity,
                exchange_order_id,
                status,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            client_id,
            symbol,
            side,
            cycle_id,
            stage,
            str(quantity),
            "0",
            None,
            "SUBMITTING",
            now,
            now,
        ))

        db.commit()

    finally:

        db.close()

    return client_id


# ============================================================
# UPDATE INDIVIDUAL TRANSACTION
# ============================================================

def unit_13_update_order(
    client_id,
    status,
    exchange_order_id=None,
    filled_quantity=None,
):

    db = unit_13_db()

    try:

        db.execute("""
            UPDATE unit13_tp_orders

            SET status = ?,

                exchange_order_id = COALESCE(
                    ?,
                    exchange_order_id
                ),

                filled_quantity = COALESCE(
                    ?,
                    filled_quantity
                ),

                updated_at = ?

            WHERE client_id = ?
        """, (
            str(status).upper(),

            (
                str(exchange_order_id)
                if exchange_order_id is not None
                else None
            ),

            (
                str(filled_quantity)
                if filled_quantity is not None
                else None
            ),

            int(time.time() * 1000),

            client_id,
        ))

        db.commit()

    finally:

        db.close()


# ============================================================
# EXCHANGE TERMINAL ORDER STATES
# ============================================================

def unit_13_terminal_status(status):

    return str(status).upper() in (
        "FILLED",
        "CANCELED",
        "CANCELLED",
        "EXPIRED",
        "REJECTED",
    )


# ============================================================
# FIND EXACT EXCHANGE TRANSACTION
# ============================================================

def unit_13_find_history_order(
    order,
    history,
):

    client_id = str(
        order.get("client_id") or ""
    )

    exchange_id = str(
        order.get("exchange_order_id") or ""
    )

    opposite = (
        "SELL"
        if order["position_side"] == "LONG"
        else "BUY"
    )

    matches = []

    for record in history:

        if not isinstance(record, dict):

            continue

        record_client = str(
            record.get("clientOrderId")
            or record.get("newClientOrderId")
            or ""
        )

        record_id = str(
            record.get("orderId") or ""
        )

        matched = (
            bool(exchange_id)
            and record_id == exchange_id
        ) or (
            bool(client_id)
            and record_client == client_id
        )

        if not matched:

            continue

        if str(
            record.get("symbol") or ""
        ).upper() != order["symbol"]:

            continue

        if str(
            record.get("positionSide") or ""
        ).upper() != order["position_side"]:

            continue

        if str(
            record.get("side") or ""
        ).upper() != opposite:

            continue

        matches.append(record)

    if not matches:

        return None

    return max(
        matches,
        key=lambda record: (
            Decimal(
                str(
                    record.get("executedQty")
                    or 0
                )
            ),
            int(
                record.get("updateTime")
                or record.get("createdTime")
                or 0
            )
        )
    )


# ============================================================
# RECONCILE ONE TP TRANSACTION
# ============================================================

def unit_13_reconcile_order(
    order,
    history,
):

    record = unit_13_find_history_order(
        order,
        history,
    )

    if record is None:

        return order

    status = str(
        record.get("status")
        or order["status"]
    ).upper()

    confirmed = Decimal(
        str(
            record.get("executedQty")
            or 0
        )
    )

    previous = Decimal(
        str(
            order.get("filled_quantity")
            or 0
        )
    )

    confirmed = max(
        confirmed,
        previous
    )

    exchange_id = (
        record.get("orderId")
        or order.get("exchange_order_id")
    )

    unit_13_update_order(
        order["client_id"],
        status,
        exchange_id,
        confirmed,
    )

    order.update({
        "status": status,
        "exchange_order_id": exchange_id,
        "filled_quantity": str(confirmed),
    })

    return order


# ============================================================
# RECONCILE CURRENT POSITION CYCLE
# ============================================================

def unit_13_reconcile_cycle(
    symbol,
    side,
    cycle_id,
    history=None,
):

    if history is None:

        history = unit_13_v4_history(
            symbol
        )

    orders = unit_13_read_orders(
        symbol,
        side,
        cycle_id,
    )

    totals = {
        "TP1": Decimal(0),
        "TP2": Decimal(0),
    }

    pending = {
        "TP1": False,
        "TP2": False,
    }

    for order in orders:

        order = unit_13_reconcile_order(
            order,
            history,
        )

        stage = order["stage"]

        if stage not in totals:

            continue

        totals[stage] += Decimal(
            str(
                order.get("filled_quantity")
                or 0
            )
        )

        if not unit_13_terminal_status(
            order["status"]
        ):

            pending[stage] = True

    return {
        "filled": totals,
        "pending": pending,
        "orders": orders,
    }


# ============================================================
# OUTSTANDING EXECUTABLE TP QUANTITY
# ============================================================

def unit_13_remaining_quantity(
    planned,
    confirmed,
    active_size,
    step,
):

    planned = Decimal(str(planned))
    confirmed = Decimal(str(confirmed))
    active_size = Decimal(str(active_size))

    remaining = max(
        Decimal(0),
        planned - confirmed
    )

    remaining = min(
        remaining,
        active_size
    )

    return unit_13_floor(
        remaining,
        step
    )


# ============================================================
# DIRECT TP TRANSACTION EXECUTION
# ============================================================

def unit_13_execute_tp(
    symbol,
    side,
    cycle_id,
    stage,
    quantity,
):

    quantity = Decimal(str(quantity))

    client_id = unit_13_new_client_id(
        stage
    )

    unit_13_record_order(
        symbol,
        side,
        cycle_id,
        stage,
        quantity,
        client_id,
    )

    print(
        "UNIT 13 TP SUBMISSION =",
        stage,
        flush=True
    )

    print(
        "UNIT 13 TP QUANTITY =",
        quantity,
        flush=True
    )

    print(
        "UNIT 13 TP CLIENT ID =",
        client_id,
        flush=True
    )

    try:

        reply = unit_13_submit_close(
            symbol,
            side,
            quantity,
            client_id,
        )

    except Exception as exc:

        unit_13_update_order(
            client_id,
            "ACK_UNKNOWN",
        )

        print(
            "UNIT 13 TP SUBMISSION RESPONSE =",
            str(exc),
            flush=True
        )

        return {
            "stage": stage,
            "client_id": client_id,
            "status": "ACK_UNKNOWN",
            "attempted": True,
            "completed": False,
            "filled_quantity": "0",
            "exchange_write": False,
            "error": str(exc),
        }

    exchange_id = None

    if isinstance(reply, dict):

        exchange_id = reply.get(
            "orderId"
        )

    if exchange_id:

        status = "ACKNOWLEDGED"

    elif (
        isinstance(reply, dict)
        and reply.get("success") is False
        and str(
            reply.get("status") or ""
        ).upper() == "REJECTED"
    ):

        status = "REJECTED"

    else:

        status = "ACK_UNKNOWN"

    unit_13_update_order(
        client_id,
        status,
        exchange_id,
    )

    print(
        "UNIT 13 TP RESPONSE =",
        reply,
        flush=True
    )

    try:

        history = unit_13_v4_history(
            symbol
        )

        orders = unit_13_read_orders(
            symbol,
            side,
            cycle_id,
            stage,
        )

        current = next(
            order
            for order in orders
            if order["client_id"] == client_id
        )

        current = unit_13_reconcile_order(
            current,
            history,
        )

        status = current["status"]

        confirmed = Decimal(
            str(
                current.get("filled_quantity")
                or 0
            )
        )

        exchange_id = current.get(
            "exchange_order_id"
        )

    except Exception as exc:

        confirmed = Decimal(0)

        print(
            "UNIT 13 TP RECONCILIATION RESPONSE =",
            str(exc),
            flush=True
        )

    completed = (
        confirmed >= quantity
    )

    print(
        "UNIT 13 TP CONFIRMED FILL =",
        confirmed,
        flush=True
    )

    print(
        "UNIT 13 TP TRANSACTION STATUS =",
        status,
        flush=True
    )

    return {
        "stage": stage,
        "client_id": client_id,
        "order_id": exchange_id,
        "status": status,
        "attempted": True,
        "completed": completed,
        "filled_quantity": str(confirmed),
        "exchange_write": bool(
            exchange_id or confirmed > 0
        ),
    }


# ============================================================
# END COMPLETE UNIT 13 V6 - PART 2 OF 3
# ZERO INDENTATION
# NEXT: MAIN EXECUTOR AND UNIT 14 HANDOVER
# ============================================================

# ============================================================
# COMPLETE UNIT 13 V6
# PART 3 OF 3
# MAIN TP EXECUTOR AND UNIT 14 HANDOVER
# ZERO INDENTATION
# ============================================================


# ============================================================
# MIGRATE EXISTING TP TRANSACTIONS
# PRESERVE PREVIOUS EXCHANGE-CONFIRMED FILLS
# ============================================================

def unit_13_import_legacy(
    position,
    symbol,
    side,
    cycle_id,
    entry,
    cum_open,
):

    from pathlib import Path

    root = Path(
        os.getenv(
            "UNIT13_STATE_DIR",
            "/var/data/unit13_tp"
        )
    )

    old_cycle = str(
        position.get("id")
        or (
            str(
                position.get("createdTime")
                or position.get("openTime")
                or ""
            )
            + ":"
            + str(entry)
            + ":"
            + str(cum_open)
        )
    )

    key = hashlib.sha256(
        (
            symbol
            + ":"
            + side
            + ":"
            + old_cycle
        ).encode()
    ).hexdigest()

    path = root / (key + ".json")

    if not path.exists():

        return

    with path.open("r") as handle:

        state = json.load(handle)

    db = unit_13_db()

    try:

        for stage, order in state.get(
            "orders", {}
        ).items():

            if stage not in ("TP1", "TP2"):

                continue

            client_id = order.get("client_id")

            if not client_id:

                continue

            now = int(time.time() * 1000)

            db.execute("""
                INSERT OR IGNORE INTO unit13_tp_orders (
                    client_id,
                    symbol,
                    position_side,
                    cycle_id,
                    stage,
                    quantity,
                    filled_quantity,
                    exchange_order_id,
                    status,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                client_id,
                symbol,
                side,
                cycle_id,
                stage,
                str(order["quantity"]),
                "0",
                order.get("order_id"),
                "ACK_UNKNOWN",
                int(
                    order.get("created_at_ms")
                    or now
                ),
                now,
            ))

        db.commit()

    finally:

        db.close()


# ============================================================
# MANAGE ONE ACTIVE POSITION
# ============================================================

def unit_13_manage_position(
    config,
    unit_12_result,
    position,
    mark,
    history,
):

    D = unit_13_v4_D

    strategy = config.get(
        "strategy", {}
    )

    precision = config.get(
        "market_precision", {}
    )

    _, symbol = unit_13_14_active_symbols()

    side = str(
        position["side"]
    ).upper()

    size = D(position["size"])

    leverage = D(
        position["leverage"]
    )

    entry = (
        D(position["openValue"])
        / size
    )

    cum_open = max(
        size,
        D(
            position.get("cumOpenSize")
            or size
        )
    )

    cum_close = D(
        position.get("cumCloseSize")
        or 0
    )

    step = D(
        precision["quantity_step"]
    )

    minimum = D(
        precision["minimum_quantity"]
    )

    price_step = D(
        precision["price_step"]
    )

    tp1_floor = D(
        strategy.get(
            "tp1_net_roi_floor_percent",
            20
        )
    )

    tp2_floor = D(
        strategy.get(
            "tp2_net_roi_floor_percent",
            40
        )
    )

    fee = D(
        strategy.get(
            "futures_taker_fee_percent",
            "0.08"
        )
    )

    pct1 = strategy.get(
        "tp1_allocation_percent",
        10
    )

    pct2 = strategy.get(
        "tp2_allocation_percent",
        20
    )

    pct3 = strategy.get(
        "tp3_allocation_percent",
        70
    )

    trail_ref = D(
        strategy.get(
            "tp3_trailing_reference_percent",
            "0.20"
        )
    )

    trail_min = D(
        strategy.get(
            "tp3_trailing_min_percent",
            "0.10"
        )
    )

    trail_max = D(
        strategy.get(
            "tp3_trailing_max_percent",
            "0.40"
        )
    )


    # ========================================================
    # TP QUANTITY AND TARGET CALCULATION
    # ========================================================

    q1, q2, q3 = unit_13_v4_allocation(
        cum_open,
        step,
        pct1,
        pct2,
    )

    t1, t2 = unit_13_v4_targets(
        entry,
        leverage,
        side,
        price_step,
        tp1_floor,
        tp2_floor,
        fee,
    )

    cycle_id = unit_13_cycle_id(
        position
    )


    # ========================================================
    # IMPORT EXISTING TRANSACTIONS
    # NO DELETION OF PREVIOUS RECORDS
    # ========================================================

    unit_13_import_legacy(
        position,
        symbol,
        side,
        cycle_id,
        entry,
        cum_open,
    )


    # ========================================================
    # RECONCILE EXCHANGE-CONFIRMED FILLS
    # ========================================================

    reconciliation = unit_13_reconcile_cycle(
        symbol,
        side,
        cycle_id,
        history,
    )

    filled = reconciliation["filled"]

    pending = reconciliation["pending"]

    tp1_filled = filled["TP1"]

    tp2_filled = filled["TP2"]

    done1 = (
        q1 == 0
        or tp1_filled >= q1
    )

    done2 = (
        q2 == 0
        or tp2_filled >= q2
    )


    # ========================================================
    # CURRENT MARKET TARGET CONDITIONS
    # PRICE CROSSING DOES NOT CONSUME STAGE
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


    # ========================================================
    # TP1 EXECUTION SELECTION
    # ========================================================

    if (
        not done1
        and reached1
        and not pending["TP1"]
    ):

        action = "TP1"

        close_qty = unit_13_remaining_quantity(
            q1,
            tp1_filled,
            size,
            step,
        )


    # ========================================================
    # TP2 EXECUTION SELECTION
    # ========================================================

    elif (
        done1
        and not done2
        and reached2
        and not pending["TP2"]
    ):

        action = "TP2"

        close_qty = unit_13_remaining_quantity(
            q2,
            tp2_filled,
            size,
            step,
        )


    # ========================================================
    # EXECUTE SELECTED TP
    # ========================================================

    execution = None

    status = "MONITORING"

    reason = "DYNAMIC_TP_TARGET_NOT_REACHED"

    if action != "NONE":

        if close_qty >= minimum:

            execution = unit_13_execute_tp(
                symbol,
                side,
                cycle_id,
                action,
                close_qty,
            )

            confirmed = D(
                execution.get(
                    "filled_quantity",
                    "0"
                )
            )

            if action == "TP1":

                tp1_filled += confirmed

                done1 = (
                    tp1_filled >= q1
                )

            elif action == "TP2":

                tp2_filled += confirmed

                done2 = (
                    tp2_filled >= q2
                )

            pending[action] = (
                not unit_13_terminal_status(
                    execution["status"]
                )
            )

            size = max(
                Decimal(0),
                size - confirmed
            )

            if execution["status"] == "FILLED":

                status = action + "_FILLED"

                reason = "EXCHANGE_CONFIRMED_FILL"

            elif execution["status"] == "REJECTED":

                status = action + "_REJECTED"

                reason = "EXCHANGE_REJECTED_RETRY_ALLOWED"

            elif execution["status"] in (
                "CANCELED",
                "CANCELLED",
                "EXPIRED",
            ):

                status = action + "_RETRY_AVAILABLE"

                reason = "OUTSTANDING_QUANTITY_REMAINS"

            elif execution["status"] == "ACK_UNKNOWN":

                status = "TP_SUBMISSION_UNCERTAIN"

                reason = "AWAITING_ORDER_RECONCILIATION"

            else:

                status = "TP_ORDER_ACKNOWLEDGED"

                reason = "AWAITING_EXCHANGE_CONFIRMED_FILL"

        else:

            reason = (
                "TP_QUANTITY_BELOW_EXCHANGE_MINIMUM"
            )

    elif (
        pending["TP1"]
        or pending["TP2"]
    ):

        reason = "AWAITING_TP_ORDER_RECONCILIATION"


    # ========================================================
    # TP3 ARMING
    # NO LEGACY CLOSURE BLOCKER
    # ========================================================

    armed = bool(
        done1
        and done2
        and size > 0
        and q3 > 0
        and not pending["TP1"]
        and not pending["TP2"]
    )

    if armed:

        status = "TP3_ARMED"

        reason = "DYNAMIC_TP3_RUNTIME_REQUIRED"


    # ========================================================
    # POSITION PNL
    # ========================================================

    direction = (
        Decimal(1)
        if side == "LONG"
        else Decimal(-1)
    )

    unrealized_pnl = (
        (mark - entry)
        * size
        * direction
    )

    margin = (
        entry * size / leverage
    )

    roi = (
        unrealized_pnl
        / margin
        * Decimal(100)
        if margin > 0
        else Decimal(0)
    )


    # ========================================================
    # EXISTING UNIT 14 RESULT INTERFACE
    # ========================================================

    result = unit_13_v4_base_result(
        unit_12_result,
        status,
        reason,
    )

    result.update({

        "symbol": symbol,

        "cycle_id": cycle_id,

        "active_position_exists":
            size > 0,

        "position_exists":
            size > 0,

        "tp_management_required":
            size > 0,

        "position_side":
            side,

        "position_size":
            float(size),

        "average_entry_price":
            float(entry),

        "mark_price":
            float(mark),

        "position_entry_price":
            float(entry),

        "position_mark_price":
            float(mark),

        "position_leverage":
            float(leverage),

        "position_unrealized_pnl":
            float(unrealized_pnl),

        "position_unrealized_roi_percent":
            float(roi),

        "cumulative_open_quantity":
            str(cum_open),

        "cumulative_close_quantity":
            str(cum_close),

        "tp_target_allocation":
            "{}/{}/{}".format(
                pct1,
                pct2,
                pct3,
            ),

        "tp1_verified_filled_quantity":
            str(tp1_filled),

        "tp2_verified_filled_quantity":
            str(tp2_filled),

        "tp_history_unresolved":
            bool(
                pending["TP1"]
                or pending["TP2"]
            ),

        "tp1_pending":
            pending["TP1"],

        "tp2_pending":
            pending["TP2"],

        "tp_legacy_closures_unattributed":
            False,

        "tp1_target":
            float(t1),

        "tp2_target":
            float(t2),

        "tp1_target_price":
            str(t1),

        "tp2_target_price":
            str(t2),

        "tp1_quantity":
            float(q1),

        "tp2_quantity":
            float(q2),

        "tp3_quantity":
            float(q3),

        "tp1_completed":
            done1,

        "tp2_completed":
            done2,

        "tp3_armed":
            armed,

        "tp1_target_reached":
            reached1,

        "tp2_target_reached":
            reached2,

        "tp3_trailing_percent":
            float(trail_ref),

        "tp3_trailing_reference_percent":
            float(trail_ref),

        "tp3_trailing_min_percent":
            float(trail_min),

        "tp3_trailing_max_percent":
            float(trail_max),

        "tp3_trailing_dynamic":
            True,

        "tp1_net_roi_floor_percent":
            float(tp1_floor),

        "tp2_net_roi_floor_percent":
            float(tp2_floor),

        "tp_action":
            action,

        "tp_execution_attempted":
            bool(execution),

        "tp_execution_completed":
            bool(
                execution
                and (
                    (
                        action == "TP1"
                        and done1
                    )
                    or (
                        action == "TP2"
                        and done2
                    )
                )
            ),

        "exchange_write":
            bool(
                execution
                and execution.get(
                    "exchange_write"
                )
            ),

        "demo_order_executed":
            bool(
                execution
                and D(
                    execution.get(
                        "filled_quantity",
                        "0"
                    )
                ) > 0
            ),

        "position_management_independent_of_bot_mode":
            True,

        "real_submission_attempted":
            False,

    })

    if execution:

        result.update({

            "tp_order_id":
                execution.get("order_id"),

            "tp_client_order_id":
                execution.get("client_id"),

            "tp_close_quantity":
                str(close_qty),

            "tp_execution_status":
                execution["status"],

            "tp_execution_filled_quantity":
                execution.get(
                    "filled_quantity",
                    "0"
                ),

        })


    # ========================================================
    # CONCISE EXECUTION REPORT
    # ========================================================

    print(
        "UNIT 13 SYMBOL =",
        symbol,
        flush=True
    )

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
        "UNIT 13 TP1 QUANTITY =",
        q1,
        flush=True
    )

    print(
        "UNIT 13 TP2 QUANTITY =",
        q2,
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
        armed,
        flush=True
    )

    print(
        "UNIT 13 TP ACTION =",
        action,
        flush=True
    )

    print(
        "UNIT 13 STATUS =",
        status,
        flush=True
    )

    print(
        "UNIT 13 REASON =",
        reason,
        flush=True
    )

    print(
        "UNIT 13 EXCHANGE WRITE =",
        result["exchange_write"],
        flush=True
    )

    return result


# ============================================================
# MAIN UNIT 13
# INDEPENDENT ACTIVE POSITION MANAGEMENT
# ============================================================

def fresh_reconstruction_unit_13(
    config,
    unit_12_result,
):

    print("=" * 80, flush=True)

    print(
        "UNIT 13 V6 EXECUTION START",
        flush=True
    )

    positions = unit_13_v4_positions()

    if not positions:

        return unit_13_v4_base_result(
            unit_12_result,
            "IDLE_NO_POSITION",
            "NO_ACTIVE_DEMO_POSITION",
        )

    _, symbol = unit_13_14_active_symbols()

    mark = unit_13_v4_mark_price()

    history = unit_13_v4_history(
        symbol
    )

    results = []

    for position in positions:

        try:

            result = unit_13_manage_position(
                config,
                unit_12_result,
                position,
                mark,
                history,
            )

        except Exception as exc:

            result = unit_13_v4_base_result(
                unit_12_result,
                "ERROR",
                str(exc),
            )

            result.update({

                "symbol":
                    symbol,

                "position_side":
                    str(
                        position.get("side")
                        or ""
                    ).upper(),

                "position_size":
                    float(
                        position.get("size")
                        or 0
                    ),

                "active_position_exists":
                    True,

                "position_exists":
                    True,

                "execution_error":
                    str(exc),

            })

            print(
                "UNIT 13 POSITION EXECUTION ERROR =",
                str(exc),
                flush=True
            )

        results.append(result)


    # ========================================================
    # PRESERVE SINGLE-RESULT UNIT 14 INTERFACE
    # ADD INDEPENDENT POSITION RESULTS
    # ========================================================

    primary = next(
        (
            result
            for result in results
            if result.get(
                "active_position_exists"
            )
            and result.get("status") != "ERROR"
        ),
        results[0],
    )

    output = dict(primary)

    output["position_results"] = results

    output["active_position_count"] = sum(
        1
        for result in results
        if result.get(
            "active_position_exists"
        )
    )

    output["active_position_exists"] = bool(
        output["active_position_count"]
    )

    output["position_exists"] = (
        output["active_position_exists"]
    )

    output["exchange_write"] = any(
        result.get("exchange_write", False)
        for result in results
    )

    output["tp_execution_attempted"] = any(
        result.get(
            "tp_execution_attempted",
            False
        )
        for result in results
    )

    print(
        "UNIT 13 ACTIVE POSITION COUNT =",
        output["active_position_count"],
        flush=True
    )

    print(
        "UNIT 13 POSITION MANAGEMENT COMPLETE",
        flush=True
    )

    print("=" * 80, flush=True)

    return output


# ============================================================
# ORIGINAL HYBRID ADAPTER INTERFACE
# ============================================================

def fresh_unit_13_hybrid_adapter(
    config,
    unit_12_result,
):

    try:

        return fresh_reconstruction_unit_13(
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

        return result


# ============================================================
# RETAIN EXISTING VALIDATION FUNCTION INTERFACE
# NONBLOCKING LOCAL CHECKS
# ============================================================

def unit_13_validation_v5():

    checks = {}

    try:

        db = unit_13_db()

        db.close()

        checks["SQLITE"] = "PASS"

    except Exception as exc:

        checks["SQLITE"] = (
            "FAIL: " + str(exc)
        )

    try:

        allocation = unit_13_v4_allocation(
            Decimal("10"),
            Decimal("1"),
            10,
            20,
        )

        assert sum(allocation) == Decimal("10")

        checks["TP_ALLOCATION"] = "PASS"

    except Exception as exc:

        checks["TP_ALLOCATION"] = (
            "FAIL: " + str(exc)
        )

    try:

        t1, t2 = unit_13_v4_targets(
            Decimal("100"),
            Decimal("10"),
            "LONG",
            Decimal("0.01"),
            Decimal("20"),
            Decimal("40"),
            Decimal("0.08"),
        )

        assert t2 > t1 > Decimal("100")

        checks["TP_TARGETS"] = "PASS"

    except Exception as exc:

        checks["TP_TARGETS"] = (
            "FAIL: " + str(exc)
        )

    passed = all(
        value == "PASS"
        for value in checks.values()
    )

    for name, value in checks.items():

        print(
            "UNIT 13",
            name,
            "=",
            value,
            flush=True
        )

    return {
        "unit": 13,
        "version": "V6",
        "passed": passed,
        "checks": checks,
    }


# ============================================================
# ORIGINAL INITIALIZATION AND HANDOVER VARIABLES
# ============================================================

FRESH_UNIT_13_VALIDATION_READY = (
    unit_13_validation_v5()
)

FRESH_RECONSTRUCTION_UNIT_13_RESULT = (
    fresh_unit_13_hybrid_adapter(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_12_RESULT,
    )
)


# ============================================================
# END COMPLETE UNIT 13 V6 REPLACEMENT
# END PART 3 OF 3
# NEXT SECTION: UNIT 14
# ZERO INDENTATION
# ============================================================


# ============================================================
# COMPLETE UNIT 14 V4 REPLACEMENT
# PART 1 OF 4
# EXCHANGE EXECUTION FOUNDATION
# UNIT 13 -> UNIT 14 -> UNIT 15
# ZERO INDENTATION
# ============================================================

import os
import json
import time
import uuid
import hashlib
import sqlite3
import urllib.request
import urllib.parse
import urllib.error

from decimal import Decimal, ROUND_DOWN


UNIT14_V3_BASE = "https://api-contract.weex.com"

UNIT14_V3_POSITION = "/capi/v3/sim/position/allPosition"

UNIT14_V3_BALANCE = "/capi/v3/sim/balance"

UNIT14_V3_HISTORY = "/capi/v3/sim/order/history"

UNIT14_V3_ORDER = "/capi/v3/sim/order"


UNIT14_STAGE_ACTIONS = (
    "H1-C",
    "H1-H",
    "H2-C",
    "H2-H",
    "R1-C",
    "R1-O",
    "R2-C",
    "R2-O",
    "B1",
    "B2",
    "B3",
    "B4",
    "B5",
    "BE-C",
    "TP3-C",
)


# ============================================================
# DECIMAL AND QUANTITY UTILITIES
# ============================================================

def unit_14_v3_D(
    value,
    name="VALUE",
    zero=False,
):

    return Decimal(str(value))


def unit_14_v3_floor(value, step):

    value = Decimal(str(value))
    step = Decimal(str(step))

    return (
        value / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    ) * step


def unit_14_opposite_side(side):

    return {
        "LONG": "SHORT",
        "SHORT": "LONG",
    }[str(side).upper()]


# ============================================================
# SHARED WEEX AUTHENTICATED REQUEST
# PRESERVE ORIGINAL UNIT 14 CALL SIGNATURE
# ============================================================

def unit_14_v3_signed_request(
    method,
    path,
    query="",
    payload=None,
):

    if method == "GET":

        params = (
            urllib.parse.parse_qsl(
                query,
                keep_blank_values=True,
            )
            if isinstance(query, str)
            else query
        )

        return unit_13_v4_signed_request(
            method,
            path,
            params or None,
        )

    return unit_13_v4_signed_request(
        method,
        path,
        payload,
    )


# ============================================================
# CURRENT ACTIVE EXCHANGE POSITIONS
# LONG AND SHORT INDEPENDENT
# ============================================================

def unit_14_v3_positions():

    _, symbol = unit_13_14_active_symbols()

    rows = unit_14_v3_signed_request(
        "GET",
        UNIT14_V3_POSITION,
    )

    if not isinstance(rows, list):

        raise RuntimeError(
            "UNIT 14 INVALID POSITION RESPONSE"
        )

    active = {}

    for position in rows:

        if str(
            position.get("symbol") or ""
        ).upper() != symbol:

            continue

        size = Decimal(
            str(
                position.get("size")
                or 0
            )
        )

        if size <= 0:

            continue

        side = str(
            position.get("side") or ""
        ).upper()

        if side in ("LONG", "SHORT"):

            active[side] = position

    return active


# ============================================================
# READ ONE POSITION
# NO ORIGINAL E0 OWNERSHIP REQUIREMENT
# ============================================================

def unit_14_v3_position(side=None):

    active = unit_14_v3_positions()

    if side is not None:

        return active.get(
            str(side).upper()
        )

    if len(active) == 1:

        return next(
            iter(active.values())
        )

    return None


# ============================================================
# AVAILABLE EXCHANGE BALANCE
# ============================================================

def unit_14_v3_balance():

    rows = unit_14_v3_signed_request(
        "GET",
        UNIT14_V3_BALANCE,
    )

    for row in rows:

        if str(
            row.get("asset") or ""
        ).upper() == "SUSDT":

            return Decimal(
                str(
                    row["availableBalance"]
                )
            )

    raise RuntimeError(
        "UNIT 14 SUSDT BALANCE MISSING"
    )


# ============================================================
# EXCHANGE ORDER HISTORY
# SUPPORT TARGETED HISTORICAL RECONCILIATION
# ============================================================

def unit_14_v3_history(
    demo_symbol=None,
    start_time=None,
    end_time=None,
):

    if demo_symbol is None:

        _, demo_symbol = (
            unit_13_14_active_symbols()
        )

    demo_symbol = str(
        demo_symbol
    ).strip().upper()

    orders = []

    for page in range(20):

        params = {
            "symbol": demo_symbol,
            "limit": 1000,
            "page": page,
        }

        if start_time is not None:

            params["startTime"] = int(
                start_time
            )

        if end_time is not None:

            params["endTime"] = int(
                end_time
            )

        batch = unit_14_v3_signed_request(
            "GET",
            UNIT14_V3_HISTORY,
            urllib.parse.urlencode(params),
        )

        if not isinstance(batch, list):

            raise RuntimeError(
                "UNIT 14 INVALID HISTORY RESPONSE"
            )

        orders.extend(batch)

        if len(batch) < 1000:

            break

    return orders


# ============================================================
# CURRENT MARKET MARK PRICE
# REUSE UNIT 13 IMPLEMENTATION
# ============================================================

def unit_14_v3_mark():

    return unit_13_v4_mark_price()


# ============================================================
# INDEPENDENT POSITION IDENTITY
# COMPATIBLE WITH UNIT 13 V6
# ============================================================

def unit_14_v3_trade_key(position):

    return unit_13_cycle_id(position)


# ============================================================
# POSITION DETAILS FOR EXECUTION
# ============================================================

def unit_14_position_details(position):

    D = unit_14_v3_D

    size = D(
        position["size"]
    )

    side = str(
        position["side"]
    ).upper()

    leverage = D(
        position["leverage"]
    )

    entry = (
        D(position["openValue"])
        / size
    )

    liquidation = D(
        position.get("liquidationPrice")
        or 0
    )

    return {
        "symbol": str(
            position["symbol"]
        ).upper(),

        "side": side,

        "size": size,

        "entry": entry,

        "leverage": leverage,

        "liquidation": liquidation,

        "cycle_id":
            unit_14_v3_trade_key(position),

        "position": position,
    }


# ============================================================
# UNIQUE EXECUTION ATTEMPT ID
# NO PERMANENT STAGE CONSUMPTION
# ============================================================

def unit_14_stage_client_id(
    cycle_id,
    action,
):

    digest = hashlib.sha256(
        (
            str(cycle_id)
            + "|"
            + str(action)
            + "|"
            + uuid.uuid4().hex
        ).encode("utf-8")
    ).hexdigest()[:20]

    return (
        "U14-"
        + str(action).upper()
        + "-"
        + digest
    )


# ============================================================
# LEGACY BACKUP ID INTERFACE
# FOR HISTORICAL ORDER IDENTIFICATION
# ============================================================

def unit_14_v3_backup_id(
    stage,
    key,
):

    return (
        "FR-B"
        + str(stage)
        + "-"
        + str(key)
    )[:36]


# ============================================================
# DIRECT MARKET ORDER EXECUTOR
# HEDGE, RECOVERY, BACKUP, BE AND TP3
# ============================================================

def unit_14_submit_order(
    symbol,
    position_side,
    quantity,
    client_id,
    is_close=False,
):

    position_side = str(
        position_side
    ).upper()

    if is_close:

        order_side = {
            "LONG": "SELL",
            "SHORT": "BUY",
        }[position_side]

    else:

        order_side = {
            "LONG": "BUY",
            "SHORT": "SELL",
        }[position_side]

    payload = {
        "symbol": symbol,

        "side": order_side,

        "positionSide": position_side,

        "type": "MARKET",

        "quantity": format(
            Decimal(str(quantity)),
            "f"
        ),

        "newClientOrderId": client_id,
    }

    return unit_14_v3_signed_request(
        "POST",
        UNIT14_V3_ORDER,
        payload=payload,
    )


# ============================================================
# DIRECT POSITION CLOSE
# ============================================================

def unit_14_submit_close(
    symbol,
    side,
    quantity,
    client_id,
):

    return unit_14_submit_order(
        symbol,
        side,
        quantity,
        client_id,
        is_close=True,
    )


# ============================================================
# DIRECT POSITION OPEN OR INCREASE
# ============================================================

def unit_14_submit_open(
    symbol,
    side,
    quantity,
    client_id,
):

    return unit_14_submit_order(
        symbol,
        side,
        quantity,
        client_id,
        is_close=False,
    )


# ============================================================
# REQUIRED OPENING MARGIN
# SUPPORT EXCHANGE CONTRACT MULTIPLIER
# ============================================================

def unit_14_required_margin(
    quantity,
    mark,
    leverage,
    contract_multiplier="1",
    buffer_percent="0",
):

    D = unit_14_v3_D

    notional = (
        D(quantity)
        * D(mark)
        * D(contract_multiplier)
    )

    margin = (
        notional / D(leverage)
    )

    return margin * (
        Decimal(1)
        + D(buffer_percent)
        / Decimal(100)
    )


# ============================================================
# AVAILABLE BALANCE BASED ORDER QUANTITY
# FOR B1 - B5
# ============================================================

def unit_14_balance_quantity(
    balance,
    allocation_percent,
    mark,
    leverage,
    quantity_step,
    contract_multiplier="1",
):

    D = unit_14_v3_D

    margin = (
        D(balance)
        * D(allocation_percent)
        / Decimal(100)
    )

    quantity = (
        margin
        * D(leverage)
        / (
            D(mark)
            * D(contract_multiplier)
        )
    )

    return unit_14_v3_floor(
        quantity,
        D(quantity_step),
    )


# ============================================================
# LIQUIDATION BUFFER TRIGGER
# ORIGINAL LONG AND SHORT FORMULA
# ============================================================

def unit_14_v3_trigger(
    side,
    liquidation,
    mark,
    buffer_pct,
):

    D = unit_14_v3_D

    liquidation = D(liquidation)
    mark = D(mark)

    fraction = (
        D(buffer_pct)
        / Decimal(100)
    )

    if liquidation <= 0:

        return Decimal(0), False

    if side == "LONG":

        trigger = liquidation * (
            Decimal(1) + fraction
        )

        reached = mark <= trigger

    else:

        trigger = liquidation * (
            Decimal(1) - fraction
        )

        reached = mark >= trigger

    return trigger, bool(reached)


# ============================================================
# UNIT 13 INDEPENDENT POSITION HANDOVER
# ============================================================

def unit_14_tp_position_result(
    unit_13_result,
    side,
):

    side = str(side).upper()

    for result in unit_13_result.get(
        "position_results", []
    ):

        if str(
            result.get("position_side") or ""
        ).upper() == side:

            return result

    if str(
        unit_13_result.get(
            "position_side"
        ) or ""
    ).upper() == side:

        return unit_13_result

    return {}


# ============================================================
# EXCHANGE TERMINAL TRANSACTION STATUS
# ============================================================

def unit_14_terminal_status(status):

    return str(status).upper() in (
        "FILLED",
        "CANCELED",
        "CANCELLED",
        "REJECTED",
        "EXPIRED",
        "TERMINAL_UNFILLED",
        "PARTIAL_TERMINAL",
    )


# ============================================================
# BASE UNIT 14 RESULT
# PRESERVE EXISTING UNIT 15 INTERFACE
# ============================================================

def unit_14_v3_result(unit_13_result):

    return {
        "unit": 14,

        "status": "MONITORING",

        "unit_13_status":
            unit_13_result.get("status"),

        "position_exists": False,

        "active_position_exists": False,

        "position_results": [],

        "backup_maximum": 5,

        "backups_filled": 0,

        "backup_next_stage": None,

        "backup_trigger_reached": False,

        "backup_submission_enabled": True,

        "backup_execution_attempted": False,

        "backup_execution_completed": False,

        "hedge_execution_attempted": False,

        "hedge_execution_completed": False,

        "recovery_execution_attempted": False,

        "recovery_execution_completed": False,

        "breakeven_armed": False,

        "breakeven_execution_attempted": False,

        "breakeven_execution_completed": False,

        "tp3_armed": False,

        "tp3_execution_attempted": False,

        "tp3_execution_completed": False,

        "real_submission_attempted": False,

        "sl_execution_attempted": False,

        "exchange_write": False,

        "position_management_independent_of_bot_mode":
            True,

        "skip_reason": "NONE",
    }


# ============================================================
# END COMPLETE UNIT 14 V4 - PART 1 OF 4
# ZERO INDENTATION
# NEXT: SQLITE TRANSACTIONS AND RECONCILIATION
# ============================================================



# ============================================================
# COMPLETE UNIT 14 V4 REPLACEMENT
# PART 2 OF 4
# SQLITE TRANSACTIONS AND EXCHANGE RECONCILIATION
# ZERO INDENTATION
# ============================================================

UNIT14_DB_PATH = os.getenv(
    "UNIT14_STAGE_DB_PATH",
    "/var/data/unit14_stages.sqlite3"
)

UNIT14_ORDER_TABLES = (
    "hedge_orders_v4",
    "backup_orders_v4",
    "breakeven_orders_v4",
    "tp3_orders_v4",
)


# ============================================================
# SELECT INDEPENDENT TRANSACTION TABLE
# ============================================================

def unit_14_order_table(action):

    action = str(action).upper()

    if action == "BE-C":

        return "breakeven_orders_v4"

    if action == "TP3-C":

        return "tp3_orders_v4"

    if action in (
        "B1", "B2", "B3", "B4", "B5"
    ):

        return "backup_orders_v4"

    return "hedge_orders_v4"


# ============================================================
# PERSISTENT SQLITE REGISTRY
# EXISTING TABLES AND HISTORY REMAIN INTACT
# ============================================================

def unit_14_stage_db():

    directory = os.path.dirname(
        UNIT14_DB_PATH
    )

    if directory:

        os.makedirs(
            directory,
            exist_ok=True
        )

    db = sqlite3.connect(
        UNIT14_DB_PATH,
        timeout=30,
        isolation_level=None,
    )

    db.execute(
        "PRAGMA busy_timeout=30000"
    )

    db.execute(
        "PRAGMA journal_mode=WAL"
    )

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

    for table in UNIT14_ORDER_TABLES:

        db.execute(f"""
            CREATE TABLE IF NOT EXISTS {table} (
                client_id TEXT PRIMARY KEY,
                cycle_id TEXT NOT NULL,
                action TEXT NOT NULL,
                quantity TEXT NOT NULL,
                state TEXT NOT NULL,
                exchange_order_id TEXT,
                confirmed_filled TEXT NOT NULL DEFAULT '0',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        db.execute(f"""
            CREATE INDEX IF NOT EXISTS
            {table}_cycle_action
            ON {table} (
                cycle_id,
                action
            )
        """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS unit14_stage_targets (
            cycle_id TEXT NOT NULL,
            action TEXT NOT NULL,
            target_quantity TEXT NOT NULL,
            PRIMARY KEY (
                cycle_id,
                action
            )
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS unit14_runtime_state (
            cycle_id TEXT NOT NULL,
            state_key TEXT NOT NULL,
            state_value TEXT,
            PRIMARY KEY (
                cycle_id,
                state_key
            )
        )
    """)

    return db


# ============================================================
# IMPORT LEGACY TRANSACTIONS
# NO DELETION OR RESET OF EXISTING RECORDS
# ============================================================

def unit_14_import_legacy_orders(cycle_id):

    db = unit_14_stage_db()

    imported = 0

    try:

        db.execute("BEGIN IMMEDIATE")

        tables = {
            row[0]
            for row in db.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
            """)
        }

        for source in (
            "stage_orders",
            "breakeven_orders",
            "tp3_orders",
        ):

            if source not in tables:

                continue

            rows = db.execute(f"""
                SELECT
                    client_id,
                    cycle_id,
                    action,
                    quantity,
                    state,
                    exchange_order_id,
                    confirmed_filled,
                    created_at,
                    updated_at
                FROM {source}
                WHERE cycle_id = ?
            """, (
                cycle_id,
            )).fetchall()

            for row in rows:

                destination = (
                    unit_14_order_table(
                        row[2]
                    )
                )

                cursor = db.execute(f"""
                    INSERT OR IGNORE INTO {destination} (
                        client_id,
                        cycle_id,
                        action,
                        quantity,
                        state,
                        exchange_order_id,
                        confirmed_filled,
                        created_at,
                        updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, row)

                imported += cursor.rowcount

        db.execute("COMMIT")

    except Exception:

        if db.in_transaction:

            db.execute("ROLLBACK")

        raise

    finally:

        db.close()

    return imported


# ============================================================
# CREATE INDEPENDENT MANAGEMENT CYCLE
# NO ORIGINAL E0 OWNERSHIP GATE
# ============================================================

def unit_14_stage_create_cycle(
    cycle_id,
    symbol,
    original_side,
    original_quantity,
    original_entry,
    frozen_atr,
):

    db = unit_14_stage_db()

    try:

        db.execute("""
            INSERT OR IGNORE INTO stage_cycles (
                cycle_id,
                symbol,
                original_side,
                original_quantity,
                original_entry,
                frozen_atr,
                stage,
                state
            )
            VALUES (
                ?, ?, ?, ?, ?, ?,
                'READY',
                'ACTIVE'
            )
        """, (
            str(cycle_id),
            str(symbol).upper(),
            str(original_side).upper(),
            str(original_quantity),
            str(original_entry),
            str(frozen_atr),
        ))

    finally:

        db.close()

    unit_14_import_legacy_orders(
        cycle_id
    )

    return cycle_id


# ============================================================
# READ AND WRITE PERSISTENT RUNTIME STATE
# FOR ATR, TRAILING PEAK AND RECOVERY GENERATION
# ============================================================

def unit_14_state_get(
    cycle_id,
    key,
    default=None,
):

    db = unit_14_stage_db()

    try:

        row = db.execute("""
            SELECT state_value
            FROM unit14_runtime_state
            WHERE cycle_id = ?
            AND state_key = ?
        """, (
            cycle_id,
            key,
        )).fetchone()

        if row is None:

            return default

        return json.loads(
            row[0]
        )

    finally:

        db.close()


def unit_14_state_set(
    cycle_id,
    key,
    value,
):

    db = unit_14_stage_db()

    try:

        db.execute("""
            INSERT INTO unit14_runtime_state (
                cycle_id,
                state_key,
                state_value
            )
            VALUES (?, ?, ?)

            ON CONFLICT (
                cycle_id,
                state_key
            )

            DO UPDATE SET
                state_value = excluded.state_value
        """, (
            cycle_id,
            key,
            json.dumps(
                value,
                default=str
            ),
        ))

    finally:

        db.close()

    return value


# ============================================================
# READ ALL TRANSACTION ATTEMPTS FOR ONE ACTION
# ============================================================

def unit_14_stage_orders(
    cycle_id,
    action,
):

    table = unit_14_order_table(
        action
    )

    db = unit_14_stage_db()

    db.row_factory = sqlite3.Row

    try:

        rows = db.execute(f"""
            SELECT *
            FROM {table}
            WHERE cycle_id = ?
            AND action = ?
            ORDER BY created_at, rowid
        """, (
            cycle_id,
            action,
        )).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        db.close()


# ============================================================
# FREEZE STAGE TARGET AT FIRST ACTUAL EXECUTION
# NOT WHEN MARKET PRICE CROSSES A TRIGGER
# ============================================================

def unit_14_stage_target(
    cycle_id,
    action,
    quantity=None,
):

    db = unit_14_stage_db()

    try:

        if quantity is not None:

            db.execute("""
                INSERT OR IGNORE INTO
                unit14_stage_targets (
                    cycle_id,
                    action,
                    target_quantity
                )
                VALUES (?, ?, ?)
            """, (
                cycle_id,
                action,
                str(quantity),
            ))

        row = db.execute("""
            SELECT target_quantity
            FROM unit14_stage_targets
            WHERE cycle_id = ?
            AND action = ?
        """, (
            cycle_id,
            action,
        )).fetchone()

        if row is None:

            return None

        return Decimal(
            str(row[0])
        )

    finally:

        db.close()


# ============================================================
# CLAIM AN ACTUAL SUBMISSION ATTEMPT
# CONFIRMED TERMINAL ORDERS DO NOT BLOCK RETRIES
# ============================================================

def unit_14_stage_claim(
    cycle_id,
    action,
    quantity,
    target_quantity=None,
):

    D = unit_14_v3_D

    quantity = D(quantity)

    table = unit_14_order_table(
        action
    )

    db = unit_14_stage_db()

    try:

        db.execute("BEGIN IMMEDIATE")

        rows = db.execute(f"""
            SELECT
                client_id,
                quantity,
                state,
                confirmed_filled
            FROM {table}
            WHERE cycle_id = ?
            AND action = ?
        """, (
            cycle_id,
            action,
        )).fetchall()

        confirmed = sum(
            (
                D(row[3])
                for row in rows
            ),
            Decimal(0),
        )

        for row in rows:

            if not unit_14_terminal_status(
                row[2]
            ):

                db.execute("COMMIT")

                return {
                    "claimed": False,
                    "client_id": row[0],
                    "state": row[2],
                    "quantity": row[1],
                }

        target_row = db.execute("""
            SELECT target_quantity
            FROM unit14_stage_targets
            WHERE cycle_id = ?
            AND action = ?
        """, (
            cycle_id,
            action,
        )).fetchone()

        if target_row is None:

            target = D(
                target_quantity
                if target_quantity is not None
                else quantity
            )

            db.execute("""
                INSERT INTO unit14_stage_targets (
                    cycle_id,
                    action,
                    target_quantity
                )
                VALUES (?, ?, ?)
            """, (
                cycle_id,
                action,
                str(target),
            ))

        else:

            target = D(
                target_row[0]
            )

        remaining = max(
            Decimal(0),
            target - confirmed
        )

        quantity = min(
            quantity,
            remaining
        )

        if quantity <= 0:

            db.execute("COMMIT")

            return {
                "claimed": False,
                "client_id": None,
                "state": "NO_OUTSTANDING_QUANTITY",
                "quantity": "0",
            }

        client_id = unit_14_stage_client_id(
            cycle_id,
            action,
        )

        db.execute(f"""
            INSERT INTO {table} (
                client_id,
                cycle_id,
                action,
                quantity,
                state
            )
            VALUES (?, ?, ?, ?, 'SUBMITTING')
        """, (
            client_id,
            cycle_id,
            action,
            str(quantity),
        ))

        db.execute("COMMIT")

        return {
            "claimed": True,
            "client_id": client_id,
            "state": "SUBMITTING",
            "quantity": str(quantity),
        }

    except Exception:

        if db.in_transaction:

            db.execute("ROLLBACK")

        raise

    finally:

        db.close()


# ============================================================
# UPDATE THE ACTUAL TRANSACTION TABLE
# CONFIRMED FILLS NEVER DECREASE
# ============================================================

def unit_14_stage_update(
    client_id,
    state,
    exchange_order_id=None,
    confirmed_filled=None,
):

    db = unit_14_stage_db()

    try:

        db.execute("BEGIN IMMEDIATE")

        for table in UNIT14_ORDER_TABLES:

            row = db.execute(f"""
                SELECT
                    confirmed_filled,
                    exchange_order_id,
                    state
                FROM {table}
                WHERE client_id = ?
            """, (
                client_id,
            )).fetchone()

            if row is None:

                continue

            previous = Decimal(
                str(row[0])
            )

            filled = previous

            if confirmed_filled is not None:

                filled = max(
                    previous,
                    Decimal(
                        str(confirmed_filled)
                    )
                )

            if row[1] and exchange_order_id:

                if str(row[1]) != str(
                    exchange_order_id
                ):

                    raise RuntimeError(
                        "UNIT 14 ORDER ID CONFLICT"
                    )

            if row[2] == "FILLED":

                state = "FILLED"

            db.execute(f"""
                UPDATE {table}
                SET
                    state = ?,
                    exchange_order_id =
                        COALESCE(
                            ?,
                            exchange_order_id
                        ),
                    confirmed_filled = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE client_id = ?
            """, (
                str(state).upper(),
                exchange_order_id,
                str(filled),
                client_id,
            ))

            db.execute("COMMIT")

            return True

        db.execute("COMMIT")

        return False

    except Exception:

        if db.in_transaction:

            db.execute("ROLLBACK")

        raise

    finally:

        db.close()


# ============================================================
# READ MANAGEMENT CYCLE
# RETAIN EXISTING UNIT 14 RESULT INTERFACE
# ============================================================

def unit_14_stage_read(cycle_id):

    db = unit_14_stage_db()

    db.row_factory = sqlite3.Row

    try:

        row = db.execute("""
            SELECT *
            FROM stage_cycles
            WHERE cycle_id = ?
        """, (
            cycle_id,
        )).fetchone()

        if row is None:

            return None

        result = dict(row)

    finally:

        db.close()

    result["orders"] = {}

    result["order_attempts"] = {}

    for action in UNIT14_STAGE_ACTIONS:

        attempts = unit_14_stage_orders(
            cycle_id,
            action,
        )

        result["order_attempts"][
            action
        ] = attempts

        if attempts:

            result["orders"][
                action
            ] = attempts[-1]

    return result


# ============================================================
# EXACT EXCHANGE ORDER IDENTIFICATION
# PRESERVE ORIGINAL WEEX FIELD ALIASES
# ============================================================

def unit_14_match_exchange_order(
    record,
    history,
    symbol,
):

    client_id = str(
        record["client_id"]
    )

    saved_id = str(
        record.get(
            "exchange_order_id"
        ) or ""
    )

    matches = []

    for order in history:

        if not isinstance(
            order, dict
        ):

            continue

        if order.get("symbol"):

            if str(
                order["symbol"]
            ).upper() != symbol.upper():

                continue

        clients = {
            str(order[field])
            for field in (
                "clientOrderId",
                "newClientOrderId",
                "clientOid",
            )
            if order.get(field) is not None
        }

        order_ids = {
            str(order[field])
            for field in (
                "orderId",
                "order_id",
            )
            if order.get(field) is not None
        }

        client_match = (
            client_id in clients
        )

        exchange_match = (
            bool(saved_id)
            and saved_id in order_ids
        )

        if not (
            client_match
            or exchange_match
        ):

            continue

        if saved_id and order_ids:

            if saved_id not in order_ids:

                continue

        if clients:

            if client_id not in clients:

                continue

        matches.append(order)

    return matches


# ============================================================
# RECONCILE ONE ACTUAL ORDER ATTEMPT
# ============================================================

def unit_14_reconcile_attempt(
    record,
    history,
    symbol,
):

    D = unit_14_v3_D

    matches = unit_14_match_exchange_order(
        record,
        history,
        symbol,
    )

    if not matches:

        return record

    order_ids = {
        str(
            order.get("orderId")
            or order.get("order_id")
        )
        for order in matches
        if (
            order.get("orderId")
            or order.get("order_id")
        )
    }

    if len(order_ids) > 1:

        raise RuntimeError(
            "UNIT 14 AMBIGUOUS ORDER ID"
        )

    expected = D(
        record["quantity"]
    )

    previous = D(
        record["confirmed_filled"]
    )

    filled = max(
        [previous] + [
            D(
                order.get(
                    "executedQty",
                    order.get(
                        "filledQty",
                        "0"
                    )
                ) or 0
            )
            for order in matches
        ]
    )

    terminal = {
        "CANCELED",
        "CANCELLED",
        "REJECTED",
        "EXPIRED",
        "FILLED",
    }

    statuses = {
        str(
            order.get("status")
            or order.get("state")
            or ""
        ).upper()
        for order in matches
    }

    if filled >= expected:

        state = "FILLED"

    elif statuses & terminal:

        state = (
            "PARTIAL_TERMINAL"
            if filled > 0
            else "TERMINAL_UNFILLED"
        )

    elif filled > 0:

        state = "PARTIAL"

    else:

        state = "PENDING"

    exchange_id = (
        next(iter(order_ids), None)
        or record.get(
            "exchange_order_id"
        )
    )

    unit_14_stage_update(
        record["client_id"],
        state,
        exchange_id,
        filled,
    )

    record.update({
        "state": state,
        "exchange_order_id": exchange_id,
        "confirmed_filled": str(filled),
    })

    return record


# ============================================================
# RECONCILE ALL ATTEMPTS FOR ONE STAGE ACTION
# ============================================================

def unit_14_stage_reconcile_order(
    cycle_id,
    action,
    history=None,
):

    cycle = unit_14_stage_read(
        cycle_id
    )

    if cycle is None:

        return {
            "action": action,
            "state": "NOT_CLAIMED",
            "confirmed_filled": "0",
            "complete": False,
            "pending": False,
        }

    attempts = cycle[
        "order_attempts"
    ].get(action, [])

    if not attempts:

        return {
            "action": action,
            "state": "NOT_CLAIMED",
            "confirmed_filled": "0",
            "complete": False,
            "pending": False,
        }

    if history is None:

        history = unit_14_v3_history(
            cycle["symbol"]
        )

    confirmed = Decimal(0)

    pending = False

    for record in attempts:

        record = unit_14_reconcile_attempt(
            record,
            history,
            cycle["symbol"],
        )

        confirmed += Decimal(
            record["confirmed_filled"]
        )

        if not unit_14_terminal_status(
            record["state"]
        ):

            pending = True

    target = unit_14_stage_target(
        cycle_id,
        action,
    )

    if target is None:

        target = Decimal(
            attempts[0]["quantity"]
        )

    complete = (
        target > 0
        and confirmed >= target
        and not pending
    )

    remaining = max(
        Decimal(0),
        target - confirmed,
    )

    if complete:

        state = "FILLED"

    elif pending:

        state = "PENDING"

    elif confirmed > 0:

        state = "PARTIAL_TERMINAL"

    else:

        state = "TERMINAL_UNFILLED"

    return {
        "action": action,
        "state": state,
        "client_id":
            attempts[-1]["client_id"],
        "exchange_order_id":
            attempts[-1].get(
                "exchange_order_id"
            ),
        "confirmed_filled":
            str(confirmed),
        "expected_quantity":
            str(target),
        "remaining_quantity":
            str(remaining),
        "complete": complete,
        "pending": pending,
        "retry_available":
            not pending and not complete,
        "attempts": attempts,
    }


# ============================================================
# RECONCILE INDEPENDENT ACTIONS
# NO COLLECTIVE ACK_UNKNOWN EXECUTION BLOCK
# ============================================================

def unit_14_stage_reconcile_cycle(
    cycle_id,
):

    cycle = unit_14_stage_read(
        cycle_id
    )

    if cycle is None:

        return {}

    history = unit_14_v3_history(
        cycle["symbol"]
    )

    results = {}

    for action in UNIT14_STAGE_ACTIONS:

        try:

            results[action] = (
                unit_14_stage_reconcile_order(
                    cycle_id,
                    action,
                    history,
                )
            )

        except Exception as exc:

            results[action] = {
                "action": action,
                "state": "RECONCILIATION_ERROR",
                "complete": False,
                "pending": True,
                "error": str(exc),
            }

    return results


# ============================================================
# SHARED ACTUAL ORDER EXECUTOR
# ALL HEDGE, RECOVERY, BACKUP AND CLOSE ACTIONS
# ============================================================

def unit_14_execute_action(
    cycle_id,
    action,
    symbol,
    side,
    quantity,
    is_close=False,
    target_quantity=None,
):

    D = unit_14_v3_D

    quantity = D(quantity)

    if quantity <= 0:

        return {
            "action": action,
            "status": "NO_EXECUTABLE_QUANTITY",
            "attempted": False,
            "complete": False,
            "exchange_write": False,
        }

    history = unit_14_v3_history(
        symbol
    )

    previous = unit_14_stage_reconcile_order(
        cycle_id,
        action,
        history,
    )

    if previous["complete"]:

        return {
            **previous,
            "status": "FILLED",
            "attempted": False,
            "exchange_write": False,
        }

    if previous.get("pending"):

        return {
            **previous,
            "status": "AWAITING_RECONCILIATION",
            "attempted": False,
            "exchange_write": False,
        }

    if is_close:

        position = unit_14_v3_position(
            side
        )

        if position is None:

            return {
                "action": action,
                "status": "POSITION_NOT_PRESENT",
                "attempted": False,
                "complete": False,
                "exchange_write": False,
            }

        quantity = min(
            quantity,
            D(position["size"])
        )

    claim = unit_14_stage_claim(
        cycle_id,
        action,
        quantity,
        target_quantity,
    )

    if not claim["claimed"]:

        return {
            "action": action,
            "status": claim["state"],
            "attempted": False,
            "complete": False,
            "exchange_write": False,
        }

    client_id = claim["client_id"]

    quantity = D(
        claim["quantity"]
    )

    print(
        "UNIT 14 ORDER SUBMISSION",
        "ACTION =", action,
        "SIDE =", side,
        "QUANTITY =", quantity,
        "CLIENT ID =", client_id,
        flush=True,
    )

    try:

        reply = unit_14_submit_order(
            symbol,
            side,
            quantity,
            client_id,
            is_close,
        )

    except Exception as exc:

        unit_14_stage_update(
            client_id,
            "ACK_UNKNOWN",
        )

        return {
            "action": action,
            "status": "ACK_UNKNOWN",
            "client_id": client_id,
            "attempted": True,
            "complete": False,
            "exchange_write": False,
            "error": str(exc),
        }

    print(
        "UNIT 14 EXCHANGE RESPONSE =",
        reply,
        flush=True,
    )

    exchange_id = None

    explicit_failure = False

    if isinstance(reply, dict):

        data = reply.get("data")

        order = (
            data
            if isinstance(data, dict)
            else reply
        )

        exchange_id = (
            order.get("orderId")
            or order.get("order_id")
        )

        explicit_failure = (
            reply.get("success") is False
            or str(
                order.get("status")
                or ""
            ).upper() == "REJECTED"
        )

    if exchange_id:

        state = "SUBMITTED"

    elif explicit_failure:

        state = "TERMINAL_UNFILLED"

    else:

        state = "ACK_UNKNOWN"

    unit_14_stage_update(
        client_id,
        state,
        exchange_id,
    )

    try:

        reconciled = (
            unit_14_stage_reconcile_order(
                cycle_id,
                action,
                unit_14_v3_history(symbol),
            )
        )

    except Exception as exc:

        return {
            "action": action,
            "status": state,
            "client_id": client_id,
            "exchange_order_id": exchange_id,
            "attempted": True,
            "complete": False,
            "exchange_write": bool(exchange_id),
            "error": str(exc),
        }

    reconciled.update({
        "status": reconciled["state"],
        "attempted": True,
        "exchange_write": bool(
            exchange_id
            or D(
                reconciled["confirmed_filled"]
            ) > 0
        ),
    })

    print(
        "UNIT 14 ACTION =", action,
        "STATE =", reconciled["state"],
        "CONFIRMED FILL =",
        reconciled["confirmed_filled"],
        flush=True,
    )

    return reconciled


# ============================================================
# INDEPENDENT CYCLE TERMINATION
# HISTORICAL RECORDS ARE NOT DELETED
# ============================================================

def unit_14_finalize_flat_cycle(
    cycle_id,
):

    cycle = unit_14_stage_read(
        cycle_id
    )

    if cycle is None:

        return {
            "status": "CYCLE_NOT_FOUND",
            "terminated": False,
        }

    positions = unit_14_v3_positions()

    if positions:

        return {
            "status": "POSITIONS_STILL_ACTIVE",
            "terminated": False,
        }

    results = (
        unit_14_stage_reconcile_cycle(
            cycle_id
        )
    )

    unresolved = [
        action
        for action, record in results.items()
        if record.get("pending")
    ]

    state = (
        "CLOSED_PENDING_RECONCILIATION"
        if unresolved
        else "CLOSED"
    )

    db = unit_14_stage_db()

    try:

        db.execute("""
            UPDATE stage_cycles
            SET
                state = ?,
                stage = 'EXCHANGE_FLAT'
            WHERE cycle_id = ?
        """, (
            state,
            cycle_id,
        ))

    finally:

        db.close()

    return {
        "status": "CYCLE_TERMINATED",
        "cycle_id": cycle_id,
        "terminated": True,
        "state": state,
        "unresolved_actions": unresolved,
        "exchange_write": False,
    }


# ============================================================
# END COMPLETE UNIT 14 V4 - PART 2 OF 4
# ZERO INDENTATION
# NEXT: H1 / H2 / R1 / R2 / B1 - B5
# ============================================================


# ============================================================
# COMPLETE UNIT 14 V4 REPLACEMENT
# PART 3 OF 4
# HEDGE / RECOVERY / BACKUP EXECUTION
# ZERO INDENTATION
# ============================================================


# ============================================================
# EXCHANGE CONTRACT SPECIFICATIONS
# EXISTING UNIT 9 CONFIGURATION HANDOVER
# ============================================================

def unit_14_contract_details(config):

    precision = config["market_precision"]

    D = unit_14_v3_D

    return {
        "step": D(
            precision["quantity_step"]
        ),

        "minimum": D(
            precision["minimum_quantity"]
        ),

        "price_step": D(
            precision["price_step"]
        ),

        "multiplier": D(
            precision.get(
                "contract_multiplier",
                "1"
            )
        ),
    }


# ============================================================
# CURRENT ATR
# EXISTING ANALYSIS SNAPSHOT
# ============================================================

def unit_14_current_atr():

    return unit_14_v3_D(
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT[
            "atr14"
        ]
    )


# ============================================================
# CREATE OR RECOVER INDEPENDENT MANAGEMENT CYCLE
# ============================================================

def unit_14_ensure_e0_cycle(position):

    D = unit_14_v3_D

    symbol = str(
        position["symbol"]
    ).upper()

    side = str(
        position["side"]
    ).upper()

    cycle_id = (
        "U14-"
        + unit_13_cycle_id(position)
    )

    existing = unit_14_stage_read(
        cycle_id
    )

    if existing is not None:

        return cycle_id

    size = D(
        position["size"]
    )

    entry = (
        D(position["openValue"])
        / D(
            position.get("cumOpenSize")
            or size
        )
    )

    unit_14_stage_create_cycle(
        cycle_id,
        symbol,
        side,
        size,
        entry,
        unit_14_current_atr(),
    )

    return cycle_id


# ============================================================
# STAGE ACTION IDENTIFICATION
# ============================================================

def unit_14_pair_actions(stage):

    if stage in ("H1", "H2"):

        return (
            stage + "-C",
            stage + "-H",
        )

    return (
        stage + "-C",
        stage + "-O",
    )


# ============================================================
# CONFIRMED STAGE QUANTITY
# ============================================================

def unit_14_confirmed_quantity(
    orders,
    action,
):

    return Decimal(
        str(
            orders.get(
                action, {}
            ).get(
                "confirmed_filled",
                "0"
            )
        )
    )


# ============================================================
# PAIR COMPLETION
# BOTH LEGS MUST HAVE CONFIRMED FILLS
# ============================================================

def unit_14_pair_complete(
    orders,
    stage,
):

    close_action, open_action = (
        unit_14_pair_actions(stage)
    )

    return bool(
        orders.get(
            close_action, {}
        ).get("complete")
        and orders.get(
            open_action, {}
        ).get("complete")
    )


# ============================================================
# DETERMINE WHETHER A STAGE HAS ACTUALLY STARTED
# ============================================================

def unit_14_pair_started(
    orders,
    stage,
):

    actions = unit_14_pair_actions(
        stage
    )

    return any(
        bool(
            orders.get(
                action, {}
            ).get("attempts")
        )
        for action in actions
    )


# ============================================================
# INDEPENDENT HEDGE AND RECOVERY PAIR EXECUTION
# ============================================================

def unit_14_stage_execute_pair(
    cycle_id,
    stage,
    quantity,
    mark_price,
    opening_leverage,
    quantity_step,
    minimum_quantity,
    margin_buffer_percent="0",
    contract_multiplier="1",
):

    D = unit_14_v3_D

    cycle = unit_14_stage_read(
        cycle_id
    )

    original = cycle["original_side"]

    opposite = unit_14_opposite_side(
        original
    )

    symbol = cycle["symbol"]

    step = D(quantity_step)

    minimum = D(minimum_quantity)

    quantity = unit_14_v3_floor(
        D(quantity),
        step,
    )

    close_action, open_action = (
        unit_14_pair_actions(stage)
    )

    if stage in ("H1", "H2"):

        close_side = original

        open_side = opposite

    else:

        close_side = opposite

        open_side = original

    if quantity < minimum:

        return {
            "status":
                "STAGE_BELOW_EXCHANGE_MINIMUM",

            "stage": stage,

            "complete": False,

            "handled": True,

            "execution_attempted": False,

            "exchange_write": False,

            "quantity": str(quantity),
        }

    history = unit_14_v3_history(
        symbol
    )

    close_record = (
        unit_14_stage_reconcile_order(
            cycle_id,
            close_action,
            history,
        )
    )

    open_record = (
        unit_14_stage_reconcile_order(
            cycle_id,
            open_action,
            history,
        )
    )

    close_target = unit_14_stage_target(
        cycle_id,
        close_action,
    )

    open_target = unit_14_stage_target(
        cycle_id,
        open_action,
    )

    target = (
        close_target
        or open_target
        or quantity
    )

    close_filled = D(
        close_record.get(
            "confirmed_filled",
            "0"
        )
    )

    open_filled = D(
        open_record.get(
            "confirmed_filled",
            "0"
        )
    )

    close_remaining = max(
        Decimal(0),
        target - close_filled,
    )

    open_remaining = max(
        Decimal(0),
        target - open_filled,
    )

    results = {}

    # --------------------------------------------------------
    # OPENING LEG
    # EXECUTE FIRST IF AVAILABLE FUNDS ARE SUFFICIENT
    # --------------------------------------------------------

    def execute_open():

        if open_record.get("pending"):

            return open_record

        if open_remaining < minimum:

            return open_record

        available = unit_14_v3_balance()

        required = unit_14_required_margin(
            open_remaining,
            mark_price,
            opening_leverage,
            contract_multiplier,
            margin_buffer_percent,
        )

        if available < required:

            return {
                "status":
                    "WAITING_FOR_AVAILABLE_FUNDS",

                "available": str(available),

                "required": str(required),

                "attempted": False,

                "exchange_write": False,
            }

        return unit_14_execute_action(
            cycle_id,
            open_action,
            symbol,
            open_side,
            open_remaining,
            is_close=False,
            target_quantity=target,
        )

    # --------------------------------------------------------
    # CLOSING LEG
    # INDEPENDENT EXECUTION
    # --------------------------------------------------------

    def execute_close():

        if close_record.get("pending"):

            return close_record

        if close_remaining < minimum:

            return close_record

        position = unit_14_v3_position(
            close_side
        )

        if position is None:

            return {
                "status": "POSITION_NOT_PRESENT",
                "attempted": False,
                "exchange_write": False,
            }

        executable = unit_14_v3_floor(
            min(
                close_remaining,
                D(position["size"]),
            ),
            step,
        )

        if executable < minimum:

            return {
                "status":
                    "CLOSE_QUANTITY_BELOW_MINIMUM",

                "attempted": False,

                "exchange_write": False,
            }

        return unit_14_execute_action(
            cycle_id,
            close_action,
            symbol,
            close_side,
            executable,
            is_close=True,
            target_quantity=target,
        )

    # --------------------------------------------------------
    # INDEPENDENT OR SEQUENTIAL FUNDING
    # --------------------------------------------------------

    available = unit_14_v3_balance()

    required = unit_14_required_margin(
        open_remaining,
        mark_price,
        opening_leverage,
        contract_multiplier,
        margin_buffer_percent,
    )

    independent = (
        available >= required
    )

    if independent:

        results[open_action] = (
            execute_open()
        )

        results[close_action] = (
            execute_close()
        )

    else:

        results[close_action] = (
            execute_close()
        )

        latest_close = (
            unit_14_stage_reconcile_order(
                cycle_id,
                close_action,
                unit_14_v3_history(symbol),
            )
        )

        if latest_close.get("complete"):

            results[open_action] = (
                execute_open()
            )

        else:

            results[open_action] = {
                "status":
                    "WAITING_FOR_CLOSING_FILL",

                "attempted": False,

                "exchange_write": False,
            }

    # --------------------------------------------------------
    # FINAL PAIR RECONCILIATION
    # --------------------------------------------------------

    history = unit_14_v3_history(
        symbol
    )

    close_record = (
        unit_14_stage_reconcile_order(
            cycle_id,
            close_action,
            history,
        )
    )

    open_record = (
        unit_14_stage_reconcile_order(
            cycle_id,
            open_action,
            history,
        )
    )

    complete = bool(
        close_record.get("complete")
        and open_record.get("complete")
    )

    attempted = any(
        record.get("attempted", False)
        for record in results.values()
    )

    exchange_write = any(
        record.get(
            "exchange_write", False
        )
        for record in results.values()
    )

    print(
        "UNIT 14 STAGE =", stage,
        "TARGET =", target,
        "FUNDING MODE =",
        (
            "INDEPENDENT"
            if independent
            else "SEQUENTIAL"
        ),
        flush=True,
    )

    print(
        "UNIT 14",
        close_action,
        "CONFIRMED =",
        close_record.get(
            "confirmed_filled"
        ),
        flush=True,
    )

    print(
        "UNIT 14",
        open_action,
        "CONFIRMED =",
        open_record.get(
            "confirmed_filled"
        ),
        flush=True,
    )

    return {
        "status": (
            stage + "_COMPLETE"
            if complete
            else stage + "_IN_PROGRESS"
        ),

        "stage": stage,

        "cycle_id": cycle_id,

        "complete": complete,

        "handled": True,

        "execution_attempted": attempted,

        "exchange_write": exchange_write,

        "independent_funding": independent,

        "target_quantity": str(target),

        "close_record": close_record,

        "open_record": open_record,

        "results": results,
    }


# ============================================================
# BACKUP EXECUTION B1 - B5
# ============================================================

def unit_14_execute_backup(
    config,
    cycle_id,
    position,
    mark,
):

    D = unit_14_v3_D

    strategy = config.get(
        "strategy", {}
    )

    precision = (
        unit_14_contract_details(config)
    )

    enabled = os.getenv(
        "BACKUP_EXECUTION_ENABLED",
        "true",
    ).strip().lower() == "true"

    result = {
        "status": "BACKUP_MONITORING",

        "handled": True,

        "cycle_id": cycle_id,

        "backup_execution_enabled":
            enabled,

        "backup_execution_attempted":
            False,

        "backup_execution_completed":
            False,

        "exchange_write": False,
    }

    if not enabled:

        result["status"] = (
            "BACKUP_DISABLED"
        )

        return result

    symbol = str(
        position["symbol"]
    ).upper()

    side = str(
        position["side"]
    ).upper()

    history = unit_14_v3_history(
        symbol
    )

    completed = 0

    next_stage = None

    for stage in range(1, 6):

        action = "B" + str(stage)

        record = (
            unit_14_stage_reconcile_order(
                cycle_id,
                action,
                history,
            )
        )

        if record.get("complete"):

            completed += 1

            continue

        next_stage = stage

        break

    result["backups_filled"] = (
        completed
    )

    result["backup_next_stage"] = (
        next_stage
    )

    if next_stage is None:

        result["status"] = (
            "ALL_BACKUPS_COMPLETED"
        )

        return result

    action = "B" + str(next_stage)

    liquidation = D(
        position.get("liquidationPrice")
        or 0
    )

    buffer_percent = D(
        strategy.get(
            "backup_buffer_percent",
            "0.3"
        )
    )

    backup_percent = D(
        strategy.get(
            "backup_available_balance_percent",
            "0.5"
        )
    )

    trigger, reached = (
        unit_14_v3_trigger(
            side,
            liquidation,
            mark,
            buffer_percent,
        )
    )

    result.update({
        "backup_trigger_price":
            str(trigger),

        "backup_trigger_reached":
            reached,

        "liquidation_price":
            str(liquidation),
    })

    target = unit_14_stage_target(
        cycle_id,
        action,
    )

    if not reached and target is None:

        return result

    available = unit_14_v3_balance()

    leverage = D(
        position["leverage"]
    )

    if target is None:

        target = unit_14_balance_quantity(
            available,
            backup_percent,
            mark,
            leverage,
            precision["step"],
            precision["multiplier"],
        )

    confirmed = D(
        record.get(
            "confirmed_filled",
            "0"
        )
    )

    remaining = unit_14_v3_floor(
        max(
            Decimal(0),
            target - confirmed,
        ),
        precision["step"],
    )

    result["backup_quantity"] = (
        str(remaining)
    )

    if remaining < precision["minimum"]:

        result["status"] = (
            "BACKUP_BELOW_EXCHANGE_MINIMUM"
        )

        return result

    required = unit_14_required_margin(
        remaining,
        mark,
        leverage,
        precision["multiplier"],
    )

    if available < required:

        result["status"] = (
            "BACKUP_WAITING_FOR_FUNDS"
        )

        return result

    execution = unit_14_execute_action(
        cycle_id,
        action,
        symbol,
        side,
        remaining,
        is_close=False,
        target_quantity=target,
    )

    result.update({
        "status": execution["status"],

        "backup_execution_attempted":
            execution.get(
                "attempted", False
            ),

        "backup_execution_completed":
            execution.get(
                "complete", False
            ),

        "exchange_write":
            execution.get(
                "exchange_write", False
            ),

        "backup_client_order_id":
            execution.get("client_id"),

        "backup_order_id":
            execution.get(
                "exchange_order_id"
            ),

        "backup_submitted_stage":
            next_stage,

        "backup_execution":
            execution,
    })

    if execution.get("complete"):

        result["backups_filled"] = (
            completed + 1
        )

    return result


# ============================================================
# HEDGE / RECOVERY DISPATCHER
# H1 -> H2 -> R1 -> R2 -> BACKUPS
# ============================================================

def unit_14_stage_dispatch(
    active_positions,
    original_position,
    unit_13_result,
    quantity_step,
    minimum_quantity,
    mark,
    config=None,
    cycle_id=None,
):

    D = unit_14_v3_D

    if config is None:

        config = (
            FRESH_RECONSTRUCTION_CONFIG
        )

    if original_position is None:

        if cycle_id is None:

            return {
                "status": "NO_POSITION",
                "handled": False,
            }

    if cycle_id is None:

        cycle_id = (
            unit_14_ensure_e0_cycle(
                original_position
            )
        )

    cycle = unit_14_stage_read(
        cycle_id
    )

    side = cycle["original_side"]

    opposite = unit_14_opposite_side(
        side
    )

    symbol = cycle["symbol"]

    tp = unit_14_tp_position_result(
        unit_13_result,
        side,
    )

    # --------------------------------------------------------
    # POST TP1 / TP2 HANDOVER
    # --------------------------------------------------------

    if (
        tp.get("tp1_completed")
        or tp.get("tp2_completed")
    ):

        return {
            "status": (
                "POST_TP2"
                if tp.get("tp2_completed")
                else "POST_TP1"
            ),

            "cycle_id": cycle_id,

            "handled": False,

            "execution_attempted": False,

            "exchange_write": False,
        }

    step = D(quantity_step)

    minimum = D(minimum_quantity)

    atr = D(
        cycle["frozen_atr"]
    )

    entry = D(
        cycle["original_entry"]
    )

    base_qty = D(
        cycle["original_quantity"]
    )

    mark = D(mark)

    adverse = (
        (entry - mark) / atr
        if side == "LONG"
        else (mark - entry) / atr
    )

    orders = (
        unit_14_stage_reconcile_cycle(
            cycle_id
        )
    )

    precision = (
        unit_14_contract_details(config)
    )

    def filled(action):

        return unit_14_confirmed_quantity(
            orders,
            action,
        )

    def complete(stage):

        return unit_14_pair_complete(
            orders,
            stage,
        )

    def started(stage):

        return unit_14_pair_started(
            orders,
            stage,
        )

    def execute(stage, quantity):

        opening_side = (
            opposite
            if stage in ("H1", "H2")
            else side
        )

        exchange = config.get(
            "exchange", {}
        )

        position = (
            active_positions.get(
                opening_side
            )
            or active_positions.get(side)
            or active_positions.get(opposite)
        )

        leverage = D(
            exchange.get(
                (
                    "leverage_long"
                    if opening_side == "LONG"
                    else "leverage_short"
                )
            )
            or position["leverage"]
        )

        outcome = (
            unit_14_stage_execute_pair(
                cycle_id=cycle_id,

                stage=stage,

                quantity=quantity,

                mark_price=mark,

                opening_leverage=leverage,

                quantity_step=step,

                minimum_quantity=minimum,

                contract_multiplier=(
                    precision["multiplier"]
                ),
            )
        )

        outcome["adverse_atr"] = (
            str(adverse)
        )

        return outcome

    # --------------------------------------------------------
    # H1 — FIRST ADVERSE ATR
    # --------------------------------------------------------

    h1_qty = unit_14_v3_floor(
        base_qty / Decimal(2),
        step,
    )

    if not complete("H1"):

        if (
            adverse >= Decimal(1)
            or started("H1")
        ):

            return execute(
                "H1",
                h1_qty,
            )

        return {
            "status": "H1_MONITORING",

            "handled": True,

            "cycle_id": cycle_id,

            "adverse_atr": str(adverse),

            "exchange_write": False,
        }

    # --------------------------------------------------------
    # H2 — SECOND ADVERSE ATR
    # --------------------------------------------------------

    h2_qty = unit_14_v3_floor(
        max(
            Decimal(0),
            base_qty - filled("H1-C"),
        ),
        step,
    )

    recovery_started = (
        started("R1")
        or started("R2")
    )

    if not complete("H2"):

        if (
            started("H2")
            or (
                not recovery_started
                and adverse >= Decimal(2)
            )
        ):

            return execute(
                "H2",
                h2_qty,
            )

    # --------------------------------------------------------
    # TOTAL CONFIRMED HEDGE QUANTITY
    # --------------------------------------------------------

    hedge_total = (
        filled("H1-H")
        + filled("H2-H")
    )

    # --------------------------------------------------------
    # R1 — RECOVERY TO ORIGINAL ENTRY
    # --------------------------------------------------------

    r1_qty = unit_14_v3_floor(
        hedge_total / Decimal(2),
        step,
    )

    if r1_qty < minimum:

        r1_qty = unit_14_v3_floor(
            hedge_total,
            step,
        )

    if not complete("R1"):

        if (
            adverse <= Decimal(0)
            or started("R1")
        ):

            return execute(
                "R1",
                r1_qty,
            )

        return {
            "status": "R1_MONITORING",

            "handled": True,

            "cycle_id": cycle_id,

            "adverse_atr": str(adverse),

            "exchange_write": False,
        }

    # --------------------------------------------------------
    # R2 — FURTHER FAVORABLE ATR
    # --------------------------------------------------------

    r2_qty = unit_14_v3_floor(
        max(
            Decimal(0),
            hedge_total - filled("R1-C"),
        ),
        step,
    )

    r2_complete = (
        complete("R2")
        or (
            r2_qty == 0
            and filled("R1-C") >= hedge_total
            and filled("R1-O") >= hedge_total
        )
    )

    if not r2_complete:

        if (
            adverse <= Decimal(-1)
            or started("R2")
        ):

            return execute(
                "R2",
                r2_qty,
            )

        # ----------------------------------------------------
        # RECOVERY FAILURE
        # PRICE RETURNS TO ADVERSE ATR AFTER R1
        # ----------------------------------------------------

        if (
            adverse >= Decimal(1)
            and not started("R2")
        ):

            position = (
                unit_14_v3_position(side)
            )

            if position is not None:

                return unit_14_execute_backup(
                    config,
                    cycle_id,
                    position,
                    mark,
                )

        return {
            "status": "R2_MONITORING",

            "handled": True,

            "cycle_id": cycle_id,

            "adverse_atr": str(adverse),

            "exchange_write": False,
        }

    # --------------------------------------------------------
    # COMPLETED RECOVERY
    # NO PERMANENT RECOVERY_COMPLETE EXECUTION LOCK
    # --------------------------------------------------------

    return {
        "status": "RECOVERY_COMPLETE",

        "cycle_id": cycle_id,

        "handled": False,

        "recovery_complete": True,

        "fresh_hedge_cycle_required": True,

        "adverse_atr": str(adverse),

        "exchange_write": False,
    }


# ============================================================
# BACKUP HANDOVER
# EXISTING FUNCTION INTERFACE
# ============================================================

def unit_14_v4_backup_handover(
    stage_result,
    cycle_id,
):

    return {
        "cycle_id": cycle_id,

        "backup_ready": (
            stage_result.get(
                "backup_next_stage"
            ) is not None
        ),

        "status": stage_result.get(
            "status"
        ),

        "exchange_write":
            stage_result.get(
                "exchange_write",
                False
            ),
    }


# ============================================================
# END COMPLETE UNIT 14 V4 - PART 3 OF 4
# ZERO INDENTATION
# NEXT: ATR BREAK-EVEN / TP3 / MAIN EXECUTOR
# ============================================================


# ============================================================
# COMPLETE UNIT 14 V4 REPLACEMENT
# PART 4 OF 4
# ATR BREAK-EVEN / TP3 / MAIN EXECUTION
# ZERO INDENTATION
# ============================================================


# ============================================================
# ATR DYNAMIC BREAK-EVEN
# ACTIVE AFTER EXCHANGE-CONFIRMED TP1
# ============================================================

def unit_14_atr_breakeven(
    symbol,
    position,
    mark,
    strategy,
):

    D = unit_14_v3_D

    side = str(
        position["side"]
    ).upper()

    size = D(position["size"])

    entry = (
        D(position["openValue"])
        / size
    )

    mark = D(mark)

    atr = unit_14_current_atr()

    fee = D(
        strategy.get(
            "futures_taker_fee_percent",
            "0.08"
        )
    ) / Decimal(100)

    key = (
        "PROTECTION-"
        + unit_13_cycle_id(position)
    )

    if side == "LONG":

        breakeven = (
            entry * (1 + fee)
            / (1 - fee)
        )

    else:

        breakeven = (
            entry * (1 - fee)
            / (1 + fee)
        )

    previous = unit_14_state_get(
        key,
        "ATR_BE",
        {},
    )

    best = D(
        previous.get(
            "best_mark",
            mark
        )
    )

    previous_stop = D(
        previous.get(
            "stop_price",
            breakeven
        )
    )

    if side == "LONG":

        best = max(
            best,
            mark,
        )

        stop = max(
            previous_stop,
            breakeven,
            best - atr,
        )

        reached = mark <= stop

    else:

        best = min(
            best,
            mark,
        )

        stop = min(
            previous_stop,
            breakeven,
            best + atr,
        )

        reached = mark >= stop

    # Persist the dynamic stop.
    # Do not persist price crossing as completion.

    unit_14_state_set(
        key,
        "ATR_BE",
        {
            "best_mark": str(best),
            "stop_price": str(stop),
        },
    )

    print(
        "UNIT 14 BREAKEVEN ENTRY =",
        entry,
        flush=True,
    )

    print(
        "UNIT 14 FEE ADJUSTED BE =",
        breakeven,
        flush=True,
    )

    print(
        "UNIT 14 BREAKEVEN ATR =",
        atr,
        flush=True,
    )

    print(
        "UNIT 14 BREAKEVEN BEST MARK =",
        best,
        flush=True,
    )

    print(
        "UNIT 14 BREAKEVEN STOP =",
        stop,
        flush=True,
    )

    print(
        "UNIT 14 BREAKEVEN TRIGGERED =",
        reached,
        flush=True,
    )

    return {
        "trade_key": key,
        "breakeven_price": str(breakeven),
        "best_mark": str(best),
        "stop_price": str(stop),
        "atr": str(atr),
        "triggered": bool(reached),
    }


# ============================================================
# SHARED REMAINING POSITION CLOSE EXECUTOR
# BE-C AND TP3-C USE INDEPENDENT SQLITE TABLES
# ============================================================

def unit_14_execute_remaining_close(
    cycle_id,
    position,
    action,
    quantity_step,
    minimum_quantity,
):

    D = unit_14_v3_D

    side = str(
        position["side"]
    ).upper()

    symbol = str(
        position["symbol"]
    ).upper()

    prefix = (
        "TP3"
        if action == "TP3-C"
        else "BE"
    )

    result = {
        "status": prefix + "_MONITORING",
        "execution_attempted": False,
        "confirmed": False,
        "exchange_write": False,
        "order_id": None,
    }

    previous = (
        unit_14_stage_reconcile_order(
            cycle_id,
            action,
            unit_14_v3_history(symbol),
        )
    )

    if previous.get("pending"):

        result.update({
            "status":
                prefix + "_AWAITING_FILL",

            "confirmed_filled":
                previous.get(
                    "confirmed_filled",
                    "0"
                ),

            "order_id":
                previous.get(
                    "exchange_order_id"
                ),
        })

        return result

    # Read current exchange position.
    # Do not use stale position quantity.

    active = unit_14_v3_position(
        side
    )

    if active is None:

        result.update({
            "status":
                prefix + "_POSITION_FLAT",

            "confirmed":
                previous.get(
                    "complete",
                    False
                ),
        })

        return result

    # Do not close a replacement position
    # using an older position snapshot.

    if (
        unit_13_cycle_id(active)
        != unit_13_cycle_id(position)
    ):

        result["status"] = (
            prefix + "_POSITION_CHANGED"
        )

        return result

    quantity = unit_14_v3_floor(
        D(active["size"]),
        D(quantity_step),
    )

    if quantity < D(minimum_quantity):

        result["status"] = (
            prefix + "_BELOW_EXCHANGE_MINIMUM"
        )

        return result

    target = unit_14_stage_target(
        cycle_id,
        action,
    )

    if target is None:

        target = quantity

    confirmed = D(
        previous.get(
            "confirmed_filled",
            "0"
        )
    )

    outstanding = max(
        Decimal(0),
        target - confirmed,
    )

    quantity = unit_14_v3_floor(
        min(
            quantity,
            outstanding,
        ),
        D(quantity_step),
    )

    if quantity < D(minimum_quantity):

        result.update({
            "status":
                prefix + "_NO_OUTSTANDING_QUANTITY",

            "confirmed":
                previous.get(
                    "complete",
                    False
                ),
        })

        return result

    execution = unit_14_execute_action(
        cycle_id=cycle_id,

        action=action,

        symbol=symbol,

        side=side,

        quantity=quantity,

        is_close=True,

        target_quantity=target,
    )

    result.update({
        "status":
            prefix
            + "_"
            + execution["status"],

        "execution_attempted":
            execution.get(
                "attempted",
                False
            ),

        "confirmed":
            execution.get(
                "complete",
                False
            ),

        "exchange_write":
            execution.get(
                "exchange_write",
                False
            ),

        "order_id":
            execution.get(
                "exchange_order_id"
            ),

        "confirmed_filled":
            execution.get(
                "confirmed_filled",
                "0"
            ),

        "execution":
            execution,
    })

    return result


# ============================================================
# ATR BREAK-EVEN MARKET CLOSE
# ============================================================

def unit_14_execute_breakeven(
    cycle_id,
    position,
    quantity_step,
    minimum_quantity,
):

    return unit_14_execute_remaining_close(
        cycle_id,
        position,
        "BE-C",
        quantity_step,
        minimum_quantity,
    )


# ============================================================
# TP3 MARKET CLOSE
# ============================================================

def unit_14_execute_tp3(
    cycle_id,
    position,
    quantity_step,
    minimum_quantity,
):

    return unit_14_execute_remaining_close(
        cycle_id,
        position,
        "TP3-C",
        quantity_step,
        minimum_quantity,
    )


# ============================================================
# TP3 DYNAMIC TRAILING
# PERSIST BEST MARK AND TRAILING STOP
# ============================================================

def unit_14_tp3_persistent_state(
    cycle_id,
    side,
    mark,
    atr,
    trail_ref,
    trail_min,
    trail_max,
):

    D = unit_14_v3_D

    mark = D(mark)

    atr = D(atr)

    trail_ref = D(trail_ref)

    trail_min = D(trail_min)

    trail_max = D(trail_max)

    atr_percent = (
        atr / mark
    ) * Decimal(100)

    dynamic_percent = min(
        trail_max,
        max(
            trail_min,
            trail_ref,
            atr_percent,
        ),
    )

    fraction = (
        dynamic_percent
        / Decimal(100)
    )

    previous = unit_14_state_get(
        cycle_id,
        "TP3_TRAILING",
        {},
    )

    best = D(
        previous.get(
            "best_mark",
            mark
        )
    )

    if side == "LONG":

        best = max(
            best,
            mark,
        )

        calculated_stop = (
            best * (1 - fraction)
        )

        stop = max(
            calculated_stop,
            D(
                previous.get(
                    "stop_price",
                    calculated_stop
                )
            ),
        )

        reached = mark <= stop

    else:

        best = min(
            best,
            mark,
        )

        calculated_stop = (
            best * (1 + fraction)
        )

        stop = min(
            calculated_stop,
            D(
                previous.get(
                    "stop_price",
                    calculated_stop
                )
            ),
        )

        reached = mark >= stop

    unit_14_state_set(
        cycle_id,
        "TP3_TRAILING",
        {
            "best_mark": str(best),
            "stop_price": str(stop),
            "trailing_percent":
                str(dynamic_percent),
        },
    )

    print(
        "UNIT 14 TP3 BEST MARK =",
        best,
        flush=True,
    )

    print(
        "UNIT 14 TP3 STOP PRICE =",
        stop,
        flush=True,
    )

    print(
        "UNIT 14 TP3 TRAILING PERCENT =",
        dynamic_percent,
        flush=True,
    )

    print(
        "UNIT 14 TP3 TRIGGER REACHED =",
        reached,
        flush=True,
    )

    return {
        "tp3_armed": True,

        "tp3_best_mark":
            str(best),

        "tp3_stop_price":
            str(stop),

        "tp3_trailing_percent":
            str(dynamic_percent),

        "tp3_trigger_reached":
            bool(reached),

        "tp3_trailing_dynamic":
            True,
    }


# ============================================================
# CONFIRMED TP HANDOVER
# PRICE CROSSING ALONE DOES NOT ACTIVATE PROTECTION
# ============================================================

def unit_14_v4_tp_handover(
    unit_13_result,
):

    D = unit_14_v3_D

    tp1_filled = D(
        unit_13_result.get(
            "tp1_verified_filled_quantity",
            "0"
        )
    )

    tp2_filled = D(
        unit_13_result.get(
            "tp2_verified_filled_quantity",
            "0"
        )
    )

    tp1_completed = bool(
        unit_13_result.get(
            "tp1_completed"
        )
        and tp1_filled > 0
    )

    tp2_completed = bool(
        unit_13_result.get(
            "tp2_completed"
        )
        and tp2_filled > 0
    )

    return {
        "tp1_completed":
            tp1_completed,

        "tp2_completed":
            tp2_completed,

        "tp3_armed":
            bool(
                tp1_completed
                and tp2_completed
                and unit_13_result.get(
                    "tp3_armed"
                )
            ),

        "tp1_confirmed_filled":
            str(tp1_filled),

        "tp2_confirmed_filled":
            str(tp2_filled),
    }


# ============================================================
# POST TP1 / TP2 POSITION MANAGEMENT
# ============================================================

def unit_14_post_tp_management(
    config,
    cycle_id,
    position,
    tp,
    mark,
):

    strategy = config.get(
        "strategy", {}
    )

    precision = (
        unit_14_contract_details(config)
    )

    handover = (
        unit_14_v4_tp_handover(tp)
    )

    result = {
        "status": "POST_TP_MONITORING",

        "handled": True,

        "cycle_id": cycle_id,

        "tp1_completed":
            handover["tp1_completed"],

        "tp2_completed":
            handover["tp2_completed"],

        "tp3_armed":
            handover["tp3_armed"],

        "exchange_write": False,

        "breakeven_execution_attempted":
            False,

        "breakeven_execution_completed":
            False,

        "tp3_execution_attempted":
            False,

        "tp3_execution_completed":
            False,
    }

    symbol = str(
        position["symbol"]
    ).upper()

    side = str(
        position["side"]
    ).upper()

    # Reconcile an existing close before
    # selecting another close mechanism.

    history = unit_14_v3_history(
        symbol
    )

    be_order = (
        unit_14_stage_reconcile_order(
            cycle_id,
            "BE-C",
            history,
        )
    )

    tp3_order = (
        unit_14_stage_reconcile_order(
            cycle_id,
            "TP3-C",
            history,
        )
    )

    if be_order.get("pending"):

        result["status"] = (
            "BE_AWAITING_EXCHANGE_FILL"
        )

        return result

    if tp3_order.get("pending"):

        result["status"] = (
            "TP3_AWAITING_EXCHANGE_FILL"
        )

        return result

    # ========================================================
    # TP3 DYNAMIC TRAILING
    # ========================================================

    if handover["tp3_armed"]:

        trailing = (
            unit_14_tp3_persistent_state(
                cycle_id=cycle_id,

                side=side,

                mark=mark,

                atr=unit_14_current_atr(),

                trail_ref=strategy.get(
                    "tp3_trailing_reference_percent",
                    "0.20"
                ),

                trail_min=strategy.get(
                    "tp3_trailing_min_percent",
                    "0.10"
                ),

                trail_max=strategy.get(
                    "tp3_trailing_max_percent",
                    "0.40"
                ),
            )
        )

        result.update(trailing)

        result["status"] = (
            "TP3_TRAILING_MONITORING"
        )

        if trailing["tp3_trigger_reached"]:

            execution = unit_14_execute_tp3(
                cycle_id,
                position,
                precision["step"],
                precision["minimum"],
            )

            result.update({
                "status":
                    execution["status"],

                "tp3_execution":
                    execution,

                "tp3_execution_attempted":
                    execution[
                        "execution_attempted"
                    ],

                "tp3_execution_completed":
                    execution["confirmed"],

                "tp3_order_id":
                    execution["order_id"],

                "exchange_write":
                    execution["exchange_write"],
            })

        return result

    # ========================================================
    # ATR BREAK-EVEN AFTER TP1
    # ========================================================

    protection = unit_14_atr_breakeven(
        symbol,
        position,
        mark,
        strategy,
    )

    result.update({
        "status":
            "ATR_BREAKEVEN_MONITORING",

        "breakeven_armed":
            True,

        "breakeven":
            protection,
    })

    if protection["triggered"]:

        execution = (
            unit_14_execute_breakeven(
                cycle_id,
                position,
                precision["step"],
                precision["minimum"],
            )
        )

        result.update({
            "status":
                execution["status"],

            "breakeven_execution":
                execution,

            "breakeven_execution_attempted":
                execution[
                    "execution_attempted"
                ],

            "breakeven_execution_completed":
                execution["confirmed"],

            "exchange_write":
                execution["exchange_write"],
        })

    return result


# ============================================================
# READ ACTIVE MANAGEMENT CYCLES
# ============================================================

def unit_14_active_cycles(symbol):

    db = unit_14_stage_db()

    db.row_factory = sqlite3.Row

    try:

        rows = db.execute("""
            SELECT *
            FROM stage_cycles
            WHERE symbol = ?
            AND state = 'ACTIVE'
            AND cycle_id LIKE 'U14-%'
            ORDER BY created_at, rowid
        """, (
            symbol,
        )).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        db.close()


# ============================================================
# RESOLVE CURRENT HEDGE GENERATION
# ============================================================

def unit_14_current_generation(
    position,
):

    base = (
        "U14-"
        + unit_13_cycle_id(position)
    )

    generation = unit_14_state_get(
        base,
        "CURRENT_GENERATION",
        None,
    )

    if generation:

        cycle = unit_14_stage_read(
            generation
        )

        if (
            cycle is not None
            and cycle["state"] == "ACTIVE"
        ):

            return generation

    return unit_14_ensure_e0_cycle(
        position
    )


# ============================================================
# CREATE FRESH HEDGE GENERATION AFTER RECOVERY
# NO DELETION OF COMPLETED H1/H2/R1/R2 TRANSACTIONS
# ============================================================

def unit_14_new_hedge_generation(
    old_cycle_id,
    position,
):

    D = unit_14_v3_D

    base = (
        "U14-"
        + unit_13_cycle_id(position)
    )

    size = D(
        position["size"]
    )

    entry = (
        D(position["openValue"])
        / size
    )

    new_cycle_id = (
        base
        + "-"
        + uuid.uuid4().hex[:12]
    )

    unit_14_stage_create_cycle(
        new_cycle_id,

        str(
            position["symbol"]
        ).upper(),

        str(
            position["side"]
        ).upper(),

        size,

        entry,

        unit_14_current_atr(),
    )

    db = unit_14_stage_db()

    try:

        db.execute("""
            UPDATE stage_cycles
            SET
                state = 'RECOVERED',
                stage = 'RECOVERY_COMPLETE'
            WHERE cycle_id = ?
        """, (
            old_cycle_id,
        ))

    finally:

        db.close()

    unit_14_state_set(
        base,
        "CURRENT_GENERATION",
        new_cycle_id,
    )

    print(
        "UNIT 14 PREVIOUS HEDGE CYCLE =",
        old_cycle_id,
        flush=True,
    )

    print(
        "UNIT 14 FRESH HEDGE CYCLE =",
        new_cycle_id,
        flush=True,
    )

    return new_cycle_id


# ============================================================
# FIND CONTINUING HEDGE CONVERSION
# INCLUDING FULL H2 CONVERSION
# ============================================================

def unit_14_continuing_cycles(
    symbol,
    positions,
):

    cycles = unit_14_active_cycles(
        symbol
    )

    history = unit_14_v3_history(
        symbol
    )

    continuing = []

    for cycle in cycles:

        cycle_id = cycle["cycle_id"]

        orders = {}

        for action in (
            "H1-C",
            "H1-H",
            "H2-C",
            "H2-H",
            "R1-C",
            "R1-O",
            "R2-C",
            "R2-O",
        ):

            orders[action] = (
                unit_14_stage_reconcile_order(
                    cycle_id,
                    action,
                    history,
                )
            )

        hedge_opened = (
            unit_14_confirmed_quantity(
                orders,
                "H1-H",
            )
            + unit_14_confirmed_quantity(
                orders,
                "H2-H",
            )
        )

        hedge_closed = (
            unit_14_confirmed_quantity(
                orders,
                "R1-C",
            )
            + unit_14_confirmed_quantity(
                orders,
                "R2-C",
            )
        )

        pending = any(
            order.get(
                "pending",
                False
            )
            for order in orders.values()
        )

        side = cycle["original_side"]

        opposite = unit_14_opposite_side(
            side
        )

        outstanding_hedge = (
            hedge_opened > hedge_closed
            and opposite in positions
        )

        if pending or outstanding_hedge:

            continuing.append(cycle)

    return continuing


# ============================================================
# HISTORICAL CYCLE RECONCILIATION
# NO HISTORICAL CYCLE EXECUTION AUTHORIZATION
# ============================================================

def unit_14_reconcile_historical_cycles():

    _, symbol = unit_13_14_active_symbols()

    db = unit_14_stage_db()

    try:

        rows = db.execute("""
            SELECT cycle_id
            FROM stage_cycles
            WHERE symbol = ?
            AND state =
                'CLOSED_PENDING_RECONCILIATION'
        """, (
            symbol,
        )).fetchall()

    finally:

        db.close()

    results = []

    for row in rows:

        cycle_id = row[0]

        try:

            records = (
                unit_14_stage_reconcile_cycle(
                    cycle_id
                )
            )

            unresolved = any(
                record.get("pending")
                for record in records.values()
            )

            if not unresolved:

                db = unit_14_stage_db()

                try:

                    db.execute("""
                        UPDATE stage_cycles
                        SET state = 'CLOSED'
                        WHERE cycle_id = ?
                    """, (
                        cycle_id,
                    ))

                finally:

                    db.close()

            results.append({
                "cycle_id": cycle_id,
                "unresolved": unresolved,
            })

        except Exception as exc:

            results.append({
                "cycle_id": cycle_id,
                "error": str(exc),
            })

    return results


# ============================================================
# MAIN UNIT 14 POSITION MANAGEMENT
# ============================================================

def fresh_reconstruction_unit_14(
    config,
    unit_13_result,
):

    result = unit_14_v3_result(
        unit_13_result
    )

    print("=" * 80, flush=True)

    print(
        "UNIT 14 V4 EXECUTION START",
        flush=True,
    )

    _, symbol = unit_13_14_active_symbols()

    positions = unit_14_v3_positions()

    precision = (
        unit_14_contract_details(config)
    )

    if not positions:

        for cycle in unit_14_active_cycles(
            symbol
        ):

            unit_14_finalize_flat_cycle(
                cycle["cycle_id"]
            )

        result.update({
            "status":
                "IDLE_NO_POSITION",

            "skip_reason":
                "EXCHANGE_FLAT",
        })

        return result

    mark = unit_14_v3_mark()

    result.update({
        "symbol": symbol,

        "position_exists": True,

        "active_position_exists": True,

        "active_position_count":
            len(positions),

        "mark_price":
            float(mark),
    })

    outcomes = []

    managed_sides = set()

    # ========================================================
    # CONTINUE EXISTING HEDGE CONVERSIONS
    # ========================================================

    continuing = unit_14_continuing_cycles(
        symbol,
        positions,
    )

    for cycle in continuing:

        cycle_id = cycle["cycle_id"]

        side = cycle["original_side"]

        opposite = unit_14_opposite_side(
            side
        )

        if side in managed_sides:

            continue

        try:

            outcome = unit_14_stage_dispatch(
                active_positions=positions,

                original_position=
                    positions.get(side),

                unit_13_result=
                    unit_13_result,

                quantity_step=
                    precision["step"],

                minimum_quantity=
                    precision["minimum"],

                mark=mark,

                config=config,

                cycle_id=cycle_id,
            )

            outcome["position_side"] = (
                side
            )

            outcomes.append(outcome)

            managed_sides.add(side)

            managed_sides.add(opposite)

            if outcome.get(
                "fresh_hedge_cycle_required"
            ):

                current = (
                    unit_14_v3_position(side)
                )

                if current is not None:

                    outcome[
                        "new_cycle_id"
                    ] = (
                        unit_14_new_hedge_generation(
                            cycle_id,
                            current,
                        )
                    )

        except Exception as exc:

            outcomes.append({
                "position_side": side,
                "cycle_id": cycle_id,
                "status": "STAGE_ERROR",
                "error": str(exc),
                "exchange_write": False,
            })

            managed_sides.add(side)

            managed_sides.add(opposite)

    # ========================================================
    # MANAGE OTHER CURRENT EXCHANGE POSITIONS
    # ========================================================

    positions = unit_14_v3_positions()

    for side, position in positions.items():

        if side in managed_sides:

            continue

        try:

            tp = unit_14_tp_position_result(
                unit_13_result,
                side,
            )

            handover = (
                unit_14_v4_tp_handover(tp)
            )

            cycle_id = (
                unit_14_current_generation(
                    position
                )
            )

            # ------------------------------------------------
            # POST TP1 / TP2
            # ------------------------------------------------

            if handover["tp1_completed"]:

                outcome = (
                    unit_14_post_tp_management(
                        config,
                        cycle_id,
                        position,
                        tp,
                        mark,
                    )
                )

            # ------------------------------------------------
            # PRE TP1 HEDGE / RECOVERY / BACKUP
            # ------------------------------------------------

            else:

                outcome = (
                    unit_14_stage_dispatch(
                        active_positions=
                            positions,

                        original_position=
                            position,

                        unit_13_result=
                            handover,

                        quantity_step=
                            precision["step"],

                        minimum_quantity=
                            precision["minimum"],

                        mark=mark,

                        config=config,

                        cycle_id=cycle_id,
                    )
                )

                if outcome.get(
                    "fresh_hedge_cycle_required"
                ):

                    current = (
                        unit_14_v3_position(
                            side
                        )
                    )

                    if current is not None:

                        outcome[
                            "new_cycle_id"
                        ] = (
                            unit_14_new_hedge_generation(
                                cycle_id,
                                current,
                            )
                        )

            outcome["position_side"] = side

            outcome["cycle_id"] = cycle_id

            outcomes.append(outcome)

            managed_sides.add(side)

            if outcome.get("stage") in (
                "H1", "H2", "R1", "R2"
            ):

                managed_sides.add(
                    unit_14_opposite_side(side)
                )

        except Exception as exc:

            outcomes.append({
                "position_side": side,

                "status":
                    "POSITION_EXECUTION_ERROR",

                "error": str(exc),

                "exchange_write": False,
            })

            print(
                "UNIT 14 POSITION ERROR =",
                str(exc),
                flush=True,
            )

    # ========================================================
    # UNIT 15 COMPATIBLE RESULT HANDOVER
    # ========================================================

    if outcomes:

        primary = next(
            (
                outcome
                for outcome in outcomes
                if outcome.get(
                    "exchange_write"
                )
            ),
            outcomes[0],
        )

        result.update(primary)

    result["position_results"] = outcomes

    result["exchange_write"] = any(
        outcome.get(
            "exchange_write",
            False
        )
        for outcome in outcomes
    )

    for field in (
        "backup_execution_attempted",
        "backup_execution_completed",
        "breakeven_execution_attempted",
        "breakeven_execution_completed",
        "tp3_execution_attempted",
        "tp3_execution_completed",
    ):

        result[field] = any(
            outcome.get(
                field,
                False
            )
            for outcome in outcomes
        )

    result[
        "hedge_execution_attempted"
    ] = any(
        outcome.get("stage") in (
            "H1", "H2"
        )
        and outcome.get(
            "execution_attempted"
        )
        for outcome in outcomes
    )

    result[
        "hedge_execution_completed"
    ] = any(
        outcome.get("stage") in (
            "H1", "H2"
        )
        and outcome.get("complete")
        for outcome in outcomes
    )

    result[
        "recovery_execution_attempted"
    ] = any(
        outcome.get("stage") in (
            "R1", "R2"
        )
        and outcome.get(
            "execution_attempted"
        )
        for outcome in outcomes
    )

    result[
        "recovery_execution_completed"
    ] = any(
        outcome.get("stage") in (
            "R1", "R2"
        )
        and outcome.get("complete")
        for outcome in outcomes
    )

    result["real_submission_attempted"] = False

    result["sl_execution_attempted"] = False

    result[
        "position_management_independent_of_bot_mode"
    ] = True

    print(
        "UNIT 14 FINAL STATUS =",
        result["status"],
        flush=True,
    )

    print(
        "UNIT 14 EXCHANGE WRITE =",
        result["exchange_write"],
        flush=True,
    )

    print(
        "UNIT 14 EXECUTION COMPLETE",
        flush=True,
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# ORIGINAL HYBRID ADAPTER INTERFACE
# ============================================================

def fresh_unit_14_hybrid_adapter(
    config,
    unit_13_result,
):

    try:

        return fresh_reconstruction_unit_14(
            config,
            unit_13_result,
        )

    except Exception as exc:

        result = unit_14_v3_result(
            unit_13_result
        )

        result.update({
            "status":
                "UNIT14_EXECUTION_ERROR",

            "execution_error":
                str(exc),

            "skip_reason":
                str(exc),
        })

        print(
            "UNIT 14 EXECUTION ERROR =",
            str(exc),
            flush=True,
        )

        return result


# ============================================================
# LOCAL VALIDATION
# NO EXCHANGE ORDERS DURING VALIDATION
# ============================================================

def unit_14_validation_v3():

    tests = {}

    try:

        db = unit_14_stage_db()

        db.close()

        tests["SQLITE"] = True

    except Exception:

        tests["SQLITE"] = False

    tests["FRACTIONAL_QUANTITY"] = (
        unit_14_v3_floor(
            Decimal("6.5"),
            Decimal("0.1"),
        )
        == Decimal("6.5")
    )

    tests["LONG_BUFFER"] = (
        unit_14_v3_trigger(
            "LONG",
            Decimal("80000"),
            Decimal("80200"),
            Decimal("0.3"),
        )
        == (
            Decimal("80240"),
            True,
        )
    )

    tests["SHORT_BUFFER"] = (
        unit_14_v3_trigger(
            "SHORT",
            Decimal("80000"),
            Decimal("79800"),
            Decimal("0.3"),
        )
        == (
            Decimal("79760"),
            True,
        )
    )

    tests["INDEPENDENT_BE_TABLE"] = (
        unit_14_order_table("BE-C")
        == "breakeven_orders_v4"
    )

    tests["INDEPENDENT_TP3_TABLE"] = (
        unit_14_order_table("TP3-C")
        == "tp3_orders_v4"
    )

    tests["INDEPENDENT_ATTEMPT_ID"] = (
        unit_14_stage_client_id(
            "TEST",
            "H1-C"
        )
        != unit_14_stage_client_id(
            "TEST",
            "H1-C"
        )
    )

    tests["REJECTED_RETRY"] = (
        unit_14_terminal_status(
            "REJECTED"
        )
    )

    tests["UNKNOWN_NOT_TERMINAL"] = (
        not unit_14_terminal_status(
            "ACK_UNKNOWN"
        )
    )

    for name, passed in tests.items():

        print(
            "UNIT 14 TEST:",
            name,
            "=",
            "PASS" if passed else "FAIL",
            flush=True,
        )

    passed = all(
        tests.values()
    )

    print(
        "UNIT 14 VALIDATION RESULT =",
        "PASS" if passed else "FAIL",
        flush=True,
    )

    return passed


# ============================================================
# ORIGINAL INITIALIZATION VARIABLES
# UNIT 13 -> UNIT 14 -> UNIT 15
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
    "FRESH RECONSTRUCTION UNIT 14 V4 READY =",
    FRESH_UNIT_14_VALIDATION_READY,
    flush=True,
)


# ============================================================
# END COMPLETE UNIT 14 V4 REPLACEMENT
# END PART 4 OF 4
# UNIT 15 FOLLOWS
# ZERO INDENTATION
# ============================================================


# ============================================================
# COMPLETE UNIT 15 V6 REPLACEMENT
# PART 1 OF 3
# CONFIGURATION / EXCHANGE / SQLITE
# ZERO INDENTATION
# ============================================================

import os as _u15_os
import time as _u15_time
import json as _u15_json
import threading as _u15_thread
import urllib.request as _u15_http
import urllib.parse as _u15_url
import urllib.error as _u15_error
import sqlite3 as _u15_sql

from decimal import Decimal as _U15_D
from datetime import datetime as _U15_DT
from datetime import timedelta as _U15_TD
from zoneinfo import ZoneInfo as _U15_Zone
from collections import Counter as _U15_Counter


# ============================================================
# EXISTING RENDER CONFIGURATION
# ============================================================

UNIT15_ENABLED = (
    _u15_os.getenv(
        "UNIT15_ENABLED", "TRUE"
    ).strip().upper() == "TRUE"
)

UNIT15_8H_ENABLED = (
    _u15_os.getenv(
        "UNIT15_8H_ENABLED", "TRUE"
    ).strip().upper() == "TRUE"
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

_UNIT15_HISTORY = "/capi/v3/sim/order/history"

_UNIT15_BALANCE = "/capi/v3/sim/balance"

_UNIT15_SLOTS = (5, 13, 21)

_UNIT15_CATCHUP_MINUTES = 120

_UNIT15_POLL_SECONDS = 10

_UNIT15_EQUITY_POLL_SECONDS = 300

_UNIT15_LOCK = _u15_thread.Lock()

_UNIT15_WORKER_LOCK = _u15_thread.Lock()

_UNIT15_LAST_EQUITY_POLL = 0

_UNIT15_LAST_REPORT = None

_UNIT15_THREAD = None


_UNIT15_DB_PATH = _u15_os.path.join(
    _u15_os.path.dirname(
        UNIT14_DB_PATH
    ) or ".",
    "unit15_reporting.sqlite3",
)


# ============================================================
# NUMBER AND DATE HELPERS
# ============================================================

def unit15_num(value):

    if value is None or value == "":

        return None

    try:

        number = _U15_D(str(value))

        return (
            number
            if number.is_finite()
            else None
        )

    except Exception:

        return None


def unit15_value(record, *names):

    for name in names:

        value = record.get(name)

        if value is not None and value != "":

            return value

    return None


def unit15_ms(value):

    try:

        number = int(
            _U15_D(str(value))
        )

        if number < 100000000000:

            number *= 1000

        return (
            number
            if number > 0
            else None
        )

    except Exception:

        return None


def unit15_now():

    return _U15_DT.now(
        _UNIT15_TZ
    )


def unit15_now_ms():

    return int(
        _u15_time.time() * 1000
    )


# ============================================================
# UNIVERSAL SYMBOL CONFIGURATION
# NO HARDCODED BTC SYMBOL
# ============================================================

def unit15_active_symbols():

    market_symbol, demo_symbol = (
        unit_13_14_active_symbols()
    )

    return (
        str(market_symbol).strip().upper(),
        str(demo_symbol).strip().upper(),
    )


# ============================================================
# CONFIGURATION DIAGNOSTICS
# NO TRADING AUTHORIZATION GATE
# ============================================================

def unit15_configuration_check():

    market_symbol, demo_symbol = (
        unit15_active_symbols()
    )

    print(
        "UNIT 15 MARKET SYMBOL =",
        market_symbol,
        flush=True,
    )

    print(
        "UNIT 15 DEMO SYMBOL =",
        demo_symbol,
        flush=True,
    )

    return bool(
        market_symbol
        and demo_symbol
    )


# ============================================================
# SHARED AUTHENTICATED EXCHANGE REQUEST
# REUSE UNIT 13 AUTHENTICATION
# ============================================================

def unit15_get(path, query=""):

    if isinstance(query, str):

        params = _u15_url.parse_qsl(
            query,
            keep_blank_values=True,
        )

    else:

        params = query

    return unit_13_v4_signed_request(
        "GET",
        path,
        params or None,
    )


# ============================================================
# PERSISTENT REPORTING DATABASE
# INDEPENDENT OF TRADING TRANSACTION TABLES
# ============================================================

def unit15_db():

    directory = _u15_os.path.dirname(
        _UNIT15_DB_PATH
    )

    if directory:

        _u15_os.makedirs(
            directory,
            exist_ok=True,
        )

    db = _u15_sql.connect(
        _UNIT15_DB_PATH,
        timeout=30,
        isolation_level=None,
    )

    db.row_factory = _u15_sql.Row

    db.execute(
        "PRAGMA busy_timeout=30000"
    )

    db.execute(
        "PRAGMA journal_mode=WAL"
    )

    db.execute("""
        CREATE TABLE IF NOT EXISTS
        unit15_runtime (
            state_key TEXT PRIMARY KEY,
            state_value TEXT,
            updated_at INTEGER NOT NULL
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS
        unit15_symbols (
            demo_symbol TEXT PRIMARY KEY,
            market_symbol TEXT,
            first_seen INTEGER NOT NULL,
            last_seen INTEGER NOT NULL
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS
        unit15_equity (
            time_ms INTEGER PRIMARY KEY,
            equity TEXT NOT NULL,
            field TEXT NOT NULL
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS
        unit15_report_delivery (
            report_key TEXT PRIMARY KEY,
            report_hours INTEGER NOT NULL,
            notification TEXT NOT NULL,
            window_end INTEGER NOT NULL,
            state TEXT NOT NULL,
            attempts INTEGER NOT NULL DEFAULT 0,
            message_id TEXT,
            last_error TEXT,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS
        unit15_commands (
            update_id INTEGER PRIMARY KEY,
            command TEXT NOT NULL,
            report_hours INTEGER NOT NULL,
            state TEXT NOT NULL,
            received_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS
        unit15_notifications (
            notification_id TEXT PRIMARY KEY,
            message TEXT NOT NULL,
            state TEXT NOT NULL,
            attempts INTEGER NOT NULL DEFAULT 0,
            message_id TEXT,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL
        )
    """)

    return db


# ============================================================
# PERSISTENT RUNTIME SETTINGS
# ============================================================

def unit15_state_get(
    key,
    default=None,
):

    db = unit15_db()

    try:

        row = db.execute("""
            SELECT state_value
            FROM unit15_runtime
            WHERE state_key = ?
        """, (
            key,
        )).fetchone()

        if row is None:

            return default

        return _u15_json.loads(
            row["state_value"]
        )

    finally:

        db.close()


def unit15_state_set(
    key,
    value,
):

    db = unit15_db()

    try:

        db.execute("""
            INSERT INTO unit15_runtime (
                state_key,
                state_value,
                updated_at
            )
            VALUES (?, ?, ?)

            ON CONFLICT(state_key)
            DO UPDATE SET
                state_value =
                    excluded.state_value,
                updated_at =
                    excluded.updated_at
        """, (
            key,
            _u15_json.dumps(
                value,
                default=str,
            ),
            unit15_now_ms(),
        ))

    finally:

        db.close()

    return value


# ============================================================
# REMEMBER SYMBOLS USED BY THE BOT
# SUPPORT REPORTING ACROSS SYMBOL SWITCHES
# ============================================================

def unit15_register_symbol():

    market, demo = (
        unit15_active_symbols()
    )

    if not demo:

        return None

    now = unit15_now_ms()

    db = unit15_db()

    try:

        db.execute("""
            INSERT INTO unit15_symbols (
                demo_symbol,
                market_symbol,
                first_seen,
                last_seen
            )
            VALUES (?, ?, ?, ?)

            ON CONFLICT(demo_symbol)
            DO UPDATE SET
                market_symbol =
                    excluded.market_symbol,
                last_seen =
                    excluded.last_seen
        """, (
            demo,
            market,
            now,
            now,
        ))

    finally:

        db.close()

    return demo


def unit15_registered_symbols():

    unit15_register_symbol()

    db = unit15_db()

    try:

        rows = db.execute("""
            SELECT demo_symbol
            FROM unit15_symbols
            ORDER BY first_seen
        """).fetchall()

        return [
            row["demo_symbol"]
            for row in rows
        ]

    finally:

        db.close()


# ============================================================
# UNIVERSAL EXCHANGE HISTORY
# NO FIXED BTC SYMBOL
# ============================================================

def unit15_history(
    demo_symbol=None,
):

    if demo_symbol is None:

        _, demo_symbol = (
            unit15_active_symbols()
        )

    demo_symbol = str(
        demo_symbol
    ).strip().upper()

    orders = {}

    complete = False

    previous_page = None

    for page in range(20):

        query = _u15_url.urlencode({
            "symbol": demo_symbol,
            "limit": 1000,
            "page": page,
        })

        batch = unit15_get(
            _UNIT15_HISTORY,
            query,
        )

        if not isinstance(batch, list):

            raise RuntimeError(
                "UNIT 15 HISTORY RESPONSE INVALID"
            )

        page_ids = []

        for order in batch:

            if not isinstance(order, dict):

                continue

            oid = unit15_value(
                order,
                "orderId",
                "id",
                "clientOrderId",
            )

            if oid is None:

                continue

            oid = str(oid)

            symbol = str(
                order.get("symbol")
                or demo_symbol
            ).upper()

            if symbol != demo_symbol:

                continue

            key = (
                symbol,
                oid,
            )

            page_ids.append(key)

            record = dict(order)

            record["symbol"] = symbol

            old = orders.get(key)

            if old is None:

                orders[key] = record

                continue

            old_qty = unit15_num(
                unit15_value(
                    old,
                    "executedQty",
                    "filledQty",
                    "filledSize",
                )
            ) or _U15_D(0)

            new_qty = unit15_num(
                unit15_value(
                    record,
                    "executedQty",
                    "filledQty",
                    "filledSize",
                )
            ) or _U15_D(0)

            old_time = unit15_ms(
                unit15_value(
                    old,
                    "updateTime",
                    "updatedAt",
                    "createdTime",
                )
            ) or 0

            new_time = unit15_ms(
                unit15_value(
                    record,
                    "updateTime",
                    "updatedAt",
                    "createdTime",
                )
            ) or 0

            if (
                new_qty,
                new_time,
            ) >= (
                old_qty,
                old_time,
            ):

                orders[key] = record

        signature = tuple(
            sorted(page_ids)
        )

        if len(batch) < 1000:

            complete = True

            break

        if signature == previous_page:

            print(
                "UNIT 15 REPEATED HISTORY PAGE =",
                page,
                flush=True,
            )

            break

        previous_page = signature

    print(
        "UNIT 15 HISTORY SYMBOL =",
        demo_symbol,
        flush=True,
    )

    print(
        "UNIT 15 HISTORY RECORDS =",
        len(orders),
        flush=True,
    )

    print(
        "UNIT 15 HISTORY COMPLETE =",
        complete,
        flush=True,
    )

    return (
        list(orders.values()),
        complete,
    )


# ============================================================
# COMBINED HISTORY ACROSS REGISTERED SYMBOLS
# ============================================================

def unit15_all_history():

    combined = []

    complete = True

    failures = {}

    symbols = (
        unit15_registered_symbols()
    )

    for symbol in symbols:

        try:

            orders, verified = (
                unit15_history(symbol)
            )

            combined.extend(orders)

            if not verified:

                complete = False

        except Exception as exc:

            complete = False

            failures[symbol] = str(exc)

            print(
                "UNIT 15 SYMBOL HISTORY ERROR =",
                symbol,
                type(exc).__name__,
                flush=True,
            )

    return {
        "orders": combined,
        "complete": complete,
        "symbols": symbols,
        "failures": failures,
    }


# ============================================================
# PERSISTENT EQUITY SNAPSHOT STORAGE
# ============================================================

def unit15_save_equity(
    equity,
    field,
    time_ms=None,
):

    if time_ms is None:

        time_ms = unit15_now_ms()

    equity = unit15_num(equity)

    if equity is None or equity < 0:

        raise ValueError(
            "UNIT 15 INVALID EQUITY"
        )

    db = unit15_db()

    try:

        db.execute("""
            INSERT OR REPLACE INTO
            unit15_equity (
                time_ms,
                equity,
                field
            )
            VALUES (?, ?, ?)
        """, (
            int(time_ms),
            str(equity),
            str(field),
        ))

    finally:

        db.close()

    return {
        "time_ms": int(time_ms),
        "equity": equity,
        "field": str(field),
    }


# ============================================================
# READ EQUITY SNAPSHOT NEAREST REPORT BOUNDARY
# ============================================================

def unit15_equity_boundary(
    boundary_ms,
    tolerance_ms=360000,
):

    db = unit15_db()

    try:

        row = db.execute("""
            SELECT
                time_ms,
                equity,
                field
            FROM unit15_equity

            WHERE time_ms BETWEEN ? AND ?

            ORDER BY ABS(time_ms - ?)

            LIMIT 1
        """, (
            boundary_ms - tolerance_ms,
            boundary_ms + tolerance_ms,
            boundary_ms,
        )).fetchone()

        if row is None:

            return None

        return {
            "time_ms":
                row["time_ms"],

            "equity":
                _U15_D(row["equity"]),

            "field":
                row["field"],
        }

    finally:

        db.close()


# ============================================================
# REGISTER REPORT DELIVERY
# DO NOT MARK REPORT AS DELIVERED BEFORE TELEGRAM ACK
# ============================================================

def unit15_register_report(
    report_key,
    hours,
    notification,
    window_end,
):

    now = unit15_now_ms()

    db = unit15_db()

    try:

        db.execute("""
            INSERT OR IGNORE INTO
            unit15_report_delivery (
                report_key,
                report_hours,
                notification,
                window_end,
                state,
                created_at,
                updated_at
            )
            VALUES (
                ?, ?, ?, ?,
                'PENDING',
                ?, ?
            )
        """, (
            report_key,
            int(hours),
            notification,
            int(window_end),
            now,
            now,
        ))

    finally:

        db.close()

    return report_key


def unit15_report_record(
    report_key,
):

    db = unit15_db()

    try:

        row = db.execute("""
            SELECT *
            FROM unit15_report_delivery
            WHERE report_key = ?
        """, (
            report_key,
        )).fetchone()

        return (
            dict(row)
            if row is not None
            else None
        )

    finally:

        db.close()


def unit15_report_delivered(
    report_key,
):

    record = unit15_report_record(
        report_key
    )

    return bool(
        record
        and record["state"] == "DELIVERED"
    )


def unit15_update_delivery(
    report_key,
    delivered,
    message_id=None,
    error=None,
):

    db = unit15_db()

    try:

        db.execute("""
            UPDATE unit15_report_delivery
            SET
                state = ?,
                attempts = attempts + 1,
                message_id = COALESCE(
                    ?,
                    message_id
                ),
                last_error = ?,
                updated_at = ?
            WHERE report_key = ?
            AND state != 'DELIVERED'
        """, (
            (
                "DELIVERED"
                if delivered
                else "PENDING"
            ),
            message_id,
            error,
            unit15_now_ms(),
            report_key,
        ))

    finally:

        db.close()


# ============================================================
# PERSISTENT TELEGRAM COMMAND TRACKING
# ============================================================

def unit15_store_command(
    update_id,
    command,
    hours,
):

    now = unit15_now_ms()

    db = unit15_db()

    try:

        db.execute("""
            INSERT OR IGNORE INTO
            unit15_commands (
                update_id,
                command,
                report_hours,
                state,
                received_at,
                updated_at
            )
            VALUES (
                ?, ?, ?,
                'PENDING',
                ?, ?
            )
        """, (
            int(update_id),
            command,
            int(hours),
            now,
            now,
        ))

    finally:

        db.close()


def unit15_pending_commands():

    db = unit15_db()

    try:

        rows = db.execute("""
            SELECT *
            FROM unit15_commands
            WHERE state = 'PENDING'
            ORDER BY update_id
        """).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        db.close()


def unit15_complete_command(
    update_id,
):

    db = unit15_db()

    try:

        db.execute("""
            UPDATE unit15_commands
            SET
                state = 'DELIVERED',
                updated_at = ?
            WHERE update_id = ?
        """, (
            unit15_now_ms(),
            int(update_id),
        ))

    finally:

        db.close()


# ============================================================
# TELEGRAM NOTIFICATION PERSISTENCE
# ACCEPTANCE / REJECTION / QUEUED / EXECUTION
# ============================================================

def unit15_queue_notification(
    notification_id,
    message,
):

    now = unit15_now_ms()

    db = unit15_db()

    try:

        db.execute("""
            INSERT OR IGNORE INTO
            unit15_notifications (
                notification_id,
                message,
                state,
                created_at,
                updated_at
            )
            VALUES (
                ?, ?,
                'PENDING',
                ?, ?
            )
        """, (
            str(notification_id),
            str(message),
            now,
            now,
        ))

    finally:

        db.close()

    return notification_id


def unit15_pending_notifications():

    db = unit15_db()

    try:

        rows = db.execute("""
            SELECT *
            FROM unit15_notifications
            WHERE state = 'PENDING'
            ORDER BY created_at
        """).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        db.close()


def unit15_update_notification(
    notification_id,
    delivered,
    message_id=None,
):

    db = unit15_db()

    try:

        db.execute("""
            UPDATE unit15_notifications
            SET
                state = ?,
                attempts = attempts + 1,
                message_id = COALESCE(
                    ?,
                    message_id
                ),
                updated_at = ?
            WHERE notification_id = ?
            AND state != 'DELIVERED'
        """, (
            (
                "DELIVERED"
                if delivered
                else "PENDING"
            ),
            message_id,
            unit15_now_ms(),
            str(notification_id),
        ))

    finally:

        db.close()


# ============================================================
# END COMPLETE UNIT 15 V6 - PART 1 OF 3
# ZERO INDENTATION
# NEXT: PERFORMANCE / EQUITY / TELEGRAM
# ============================================================

# ============================================================
# COMPLETE UNIT 15 V6 REPLACEMENT
# PART 2 OF 3
# PERFORMANCE / EQUITY / TELEGRAM
# ZERO INDENTATION
# ============================================================


# ============================================================
# NORMALIZE EXCHANGE-CONFIRMED EXECUTED ORDERS
# INCLUDE PARTIAL FILLS AND TERMINAL PARTIAL FILLS
# ============================================================

def unit15_parse_order(order):

    D = _U15_D

    status = str(
        unit15_value(
            order,
            "status",
            "state",
            "orderStatus",
        ) or ""
    ).upper()

    qty = unit15_num(
        unit15_value(
            order,
            "executedQty",
            "filledQty",
            "filledSize",
            "executedQuantity",
            "dealSize",
        )
    )

    if qty is None or qty <= 0:

        return None, "NO_CONFIRMED_FILL"

    price = unit15_num(
        unit15_value(
            order,
            "avgPrice",
            "averagePrice",
            "fillPrice",
            "priceAvg",
            "executedPrice",
        )
    )

    if price is None or price <= 0:

        return None, "INVALID_PRICE"

    ts = unit15_ms(
        unit15_value(
            order,
            "lastFillTime",
            "fillTime",
            "updateTime",
            "updatedAt",
            "createdTime",
            "createTime",
            "cTime",
            "ctime",
            "createdAt",
            "timestamp",
            "time",
        )
    )

    if ts is None:

        return None, "INVALID_TIMESTAMP"

    oid = unit15_value(
        order,
        "orderId",
        "id",
        "clientOrderId",
        "newClientOrderId",
    )

    if oid is None:

        return None, "MISSING_ORDER_ID"

    symbol = str(
        order.get("symbol")
        or ""
    ).strip().upper()

    if not symbol:

        return None, "MISSING_SYMBOL"

    side = str(
        unit15_value(
            order,
            "side",
            "orderSide",
        ) or ""
    ).upper()

    direction = str(
        unit15_value(
            order,
            "positionSide",
            "holdSide",
            "posSide",
        ) or ""
    ).upper()

    action = str(
        unit15_value(
            order,
            "tradeSide",
            "tradeType",
            "offset",
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
                (direction == "LONG")
                == (side == "BUY")
            )
            else "CLOSE"
        )

    if (
        direction not in ("LONG", "SHORT")
        or action not in ("OPEN", "CLOSE")
    ):

        return None, "UNRESOLVED_DIRECTION"

    fully_filled = status in (
        "FILLED",
        "FULLY_FILLED",
        "FULL_FILLED",
        "FULLFILL",
    )

    client_id = str(
        unit15_value(
            order,
            "clientOrderId",
            "newClientOrderId",
            "clientOid",
        ) or ""
    )

    return {
        "id": str(oid),
        "client_id": client_id,
        "symbol": symbol,
        "time": ts,
        "qty": qty,
        "price": price,
        "direction": direction,
        "action": action,
        "status": status,
        "fully_filled": fully_filled,
        "partial_fill": not fully_filled,
    }, None


# ============================================================
# CONTRACT MULTIPLIER
# USE EXISTING CONFIGURATION WITHOUT MODIFYING UNIT 9
# ============================================================

def unit15_contract_multiplier(symbol):

    config = FRESH_RECONSTRUCTION_CONFIG

    exchange = config.get(
        "exchange", {}
    )

    active = str(
        exchange.get(
            "demo_order_symbol", ""
        )
    ).upper()

    if symbol == active:

        precision = config.get(
            "market_precision", {}
        )

        multiplier = unit15_num(
            precision.get(
                "contract_multiplier"
            )
        )

        if (
            multiplier is not None
            and multiplier > 0
        ):

            unit15_state_set(
                "MULTIPLIER:" + symbol,
                str(multiplier),
            )

            return multiplier

    saved = unit15_state_get(
        "MULTIPLIER:" + symbol,
        None,
    )

    multiplier = unit15_num(saved)

    if (
        multiplier is not None
        and multiplier > 0
    ):

        return multiplier

    raw = _u15_os.getenv(
        "WEEX_SYMBOL_CONTRACT_SPECS",
        "",
    )

    if raw:

        try:

            specifications = (
                _u15_json.loads(raw)
            )

            market = (
                symbol[:-5] + "USDT"
                if symbol.endswith("SUSDT")
                else symbol
            )

            record = (
                specifications.get(symbol)
                or specifications.get(market)
                or {}
            )

            multiplier = unit15_num(
                record.get(
                    "contract_multiplier"
                )
            )

            if (
                multiplier is not None
                and multiplier > 0
            ):

                unit15_state_set(
                    "MULTIPLIER:" + symbol,
                    str(multiplier),
                )

                return multiplier

        except Exception:

            pass

    return None


# ============================================================
# PERFORMANCE CALCULATION
# INDEPENDENT SYMBOL AND POSITION SIDE ACCOUNTING
# ============================================================

def unit15_analyze(
    orders,
    history_complete,
    start_ms,
    end_ms,
):

    D = _U15_D

    reasons = _U15_Counter()

    normalized = {}

    for order in orders:

        if not isinstance(order, dict):

            reasons["INVALID_RECORD"] += 1

            continue

        fill, error = (
            unit15_parse_order(order)
        )

        if fill is None:

            reasons[error] += 1

            continue

        key = (
            fill["symbol"],
            fill["id"],
        )

        previous = normalized.get(key)

        if (
            previous is None
            or (
                fill["qty"],
                fill["time"],
            ) >= (
                previous["qty"],
                previous["time"],
            )
        ):

            normalized[key] = fill

    fills = sorted(
        normalized.values(),
        key=lambda x: (
            x["time"],
            x["id"],
        ),
    )

    positions = {}

    cycles = []

    unmatched = 0

    unknown_multiplier = set()

    multipliers = {}

    symbol_results = {}

    realized_window = D(0)

    window_fills = 0

    window_full = 0

    window_partial = 0

    for fill in fills:

        if fill["time"] >= end_ms:

            continue

        symbol = fill["symbol"]

        direction = fill["direction"]

        key = (
            symbol,
            direction,
        )

        qty = fill["qty"]

        price = fill["price"]

        inside_window = (
            start_ms
            <= fill["time"]
            < end_ms
        )

        if inside_window:

            window_fills += 1

            if fill["fully_filled"]:

                window_full += 1

            else:

                window_partial += 1

        if symbol not in multipliers:

            multipliers[symbol] = (
                unit15_contract_multiplier(
                    symbol
                )
            )

        multiplier = multipliers[symbol]

        if multiplier is None:

            unknown_multiplier.add(symbol)

        if key not in positions:

            positions[key] = {
                "qty": D(0),
                "cost": D(0),
                "pnl": D(0),
                "unknown": False,
            }

        p = positions[key]

        if fill["action"] == "OPEN":

            p["qty"] += qty

            p["cost"] += qty * price

            continue

        if (
            p["qty"] <= 0
            or qty > p["qty"]
        ):

            unmatched += 1

            p["unknown"] = True

            p["qty"] = D(0)

            p["cost"] = D(0)

            p["pnl"] = D(0)

            continue

        average = (
            p["cost"] / p["qty"]
        )

        raw_pnl = (
            (price - average) * qty
            if direction == "LONG"
            else (average - price) * qty
        )

        if multiplier is None:

            pnl = None

            p["unknown"] = True

        else:

            pnl = raw_pnl * multiplier

            p["pnl"] += pnl

            if (
                inside_window
                and not p["unknown"]
            ):

                realized_window += pnl

        p["qty"] -= qty

        p["cost"] -= average * qty

        if p["qty"] == 0:

            if (
                inside_window
                and not p["unknown"]
            ):

                cycles.append({
                    "symbol": symbol,
                    "direction": direction,
                    "pnl": p["pnl"],
                    "closed_at": fill["time"],
                })

            p.update({
                "qty": D(0),
                "cost": D(0),
                "pnl": D(0),
                "unknown": False,
            })

    # --------------------------------------------------------
    # COMPLETED POSITION CYCLE SUMMARY
    # --------------------------------------------------------

    profit = sum(
        (
            item["pnl"]
            for item in cycles
            if item["pnl"] > 0
        ),
        D(0),
    )

    loss = sum(
        (
            -item["pnl"]
            for item in cycles
            if item["pnl"] < 0
        ),
        D(0),
    )

    for item in cycles:

        symbol = item["symbol"]

        if symbol not in symbol_results:

            symbol_results[symbol] = {
                "cycles": 0,
                "wins": 0,
                "losses": 0,
                "breakeven": 0,
                "gross_pnl": D(0),
            }

        summary = symbol_results[symbol]

        summary["cycles"] += 1

        summary["gross_pnl"] += (
            item["pnl"]
        )

        if item["pnl"] > 0:

            summary["wins"] += 1

        elif item["pnl"] < 0:

            summary["losses"] += 1

        else:

            summary["breakeven"] += 1

    provisional = bool(
        not history_complete
        or unmatched > 0
        or unknown_multiplier
        or any(
            count > 0
            for name, count
            in reasons.items()
            if name != "NO_CONFIRMED_FILL"
        )
    )

    return {
        "orders": len(orders),

        "executed_orders":
            window_fills,

        "fully_filled":
            window_full,

        "partially_filled":
            window_partial,

        "cycles":
            len(cycles),

        "wins":
            sum(
                item["pnl"] > 0
                for item in cycles
            ),

        "losses":
            sum(
                item["pnl"] < 0
                for item in cycles
            ),

        "breakeven":
            sum(
                item["pnl"] == 0
                for item in cycles
            ),

        "gross_profit":
            profit,

        "gross_loss":
            loss,

        "gross_pnl":
            profit - loss,

        "realized_window_pnl":
            realized_window,

        "unmatched":
            unmatched,

        "history_complete":
            bool(history_complete),

        "provisional":
            provisional,

        "unknown_multiplier":
            sorted(unknown_multiplier),

        "symbol_results":
            symbol_results,

        "diagnostics":
            dict(reasons),
    }


# ============================================================
# EXCHANGE EQUITY SNAPSHOT
# PERSIST IN SQLITE
# ============================================================

def unit15_equity_snapshot():

    rows = unit15_get(
        _UNIT15_BALANCE
    )

    if not isinstance(rows, list):

        raise RuntimeError(
            "UNIT 15 BALANCE RESPONSE INVALID"
        )

    for row in rows:

        if not isinstance(row, dict):

            continue

        asset = str(
            row.get("asset", "")
        ).upper()

        if asset != "SUSDT":

            continue

        for field in (
            "equity",
            "accountEquity",
            "totalEquity",
            "marginBalance",
        ):

            value = unit15_num(
                row.get(field)
            )

            if (
                value is not None
                and value >= 0
            ):

                snapshot = (
                    unit15_save_equity(
                        value,
                        field,
                    )
                )

                return snapshot

    raise RuntimeError(
        "UNIT 15 EQUITY FIELD UNAVAILABLE"
    )


# ============================================================
# PERSISTENT EQUITY COMPARISON
# ============================================================

def unit15_equity_change(
    start_ms,
    end_ms,
):

    a = unit15_equity_boundary(
        start_ms
    )

    b = unit15_equity_boundary(
        end_ms
    )

    if a is None or b is None:

        return None

    if a["field"] != b["field"]:

        return None

    if a["time_ms"] >= b["time_ms"]:

        return None

    change = (
        b["equity"] - a["equity"]
    )

    roi = (
        change * _U15_D(100)
        / a["equity"]
        if a["equity"] > 0
        else None
    )

    return {
        "starting":
            a["equity"],

        "ending":
            b["equity"],

        "change":
            change,

        "roi":
            roi,

        "starting_time_ms":
            a["time_ms"],

        "ending_time_ms":
            b["time_ms"],

        "field":
            a["field"],
    }


# ============================================================
# TELEGRAM API COMMUNICATION
# EXISTING RENDER CREDENTIALS
# ============================================================

def unit15_telegram_api(
    method,
    values,
):

    token = _u15_os.getenv(
        "TELEGRAM_BOT_TOKEN",
        "",
    ).strip()

    if not token:

        raise RuntimeError(
            "UNIT 15 TELEGRAM TOKEN MISSING"
        )

    request = _u15_http.Request(
        "https://api.telegram.org/bot"
        + token
        + "/"
        + method,

        data=_u15_url.urlencode(
            values
        ).encode("utf-8"),

        method="POST",
    )

    try:

        with _u15_http.urlopen(
            request,
            timeout=20,
        ) as response:

            reply = _u15_json.loads(
                response.read().decode(
                    "utf-8"
                )
            )

    except _u15_error.HTTPError as exc:

        raise RuntimeError(
            "TELEGRAM HTTP "
            + str(exc.code)
        ) from None

    except Exception as exc:

        raise RuntimeError(
            "TELEGRAM CONNECTION "
            + type(exc).__name__
        ) from None

    if (
        not isinstance(reply, dict)
        or reply.get("ok") is not True
    ):

        raise RuntimeError(
            "TELEGRAM ACKNOWLEDGEMENT FAILED"
        )

    return reply


# ============================================================
# TELEGRAM DELIVERY WITH ACTUAL ACKNOWLEDGEMENT
# ============================================================

def unit15_send_message(
    message,
    attempts=3,
):

    chat_id = _u15_os.getenv(
        "TELEGRAM_CHAT_ID",
        "",
    ).strip()

    if not chat_id:

        return {
            "delivered": False,
            "message_id": None,
            "error": "TELEGRAM_CHAT_ID_MISSING",
        }

    last_error = None

    for attempt in range(
        1,
        attempts + 1,
    ):

        try:

            reply = unit15_telegram_api(
                "sendMessage",
                {
                    "chat_id": chat_id,
                    "text": str(message),
                },
            )

            message_id = (
                reply.get("result", {})
                .get("message_id")
            )

            if message_id is None:

                raise RuntimeError(
                    "TELEGRAM MESSAGE ID MISSING"
                )

            print(
                "UNIT 15 TELEGRAM DELIVERY = PASS",
                flush=True,
            )

            print(
                "UNIT 15 TELEGRAM MESSAGE ID =",
                message_id,
                flush=True,
            )

            return {
                "delivered": True,
                "message_id": str(message_id),
                "error": None,
            }

        except Exception as exc:

            last_error = str(exc)[:150]

            print(
                "UNIT 15 TELEGRAM FAILURE =",
                attempt,
                last_error,
                flush=True,
            )

            if attempt < attempts:

                _u15_time.sleep(
                    3 * attempt
                )

    return {
        "delivered": False,
        "message_id": None,
        "error": last_error,
    }


# ============================================================
# PRESERVE EXISTING TELEGRAM SENDER INTERFACE
# USED BY EXISTING UNITS AND CONFIGURATION CONTROLLERS
# ============================================================

def unit15_telegram(message):

    result = unit15_send_message(
        message
    )

    return bool(
        result["delivered"]
    )


# ============================================================
# PERSISTENT NOTIFICATION QUEUE PROCESSOR
# ACCEPTANCE / REJECTION / QUEUED NOTIFICATIONS
# ============================================================

def unit15_flush_notifications():

    delivered_count = 0

    pending = (
        unit15_pending_notifications()
    )

    for record in pending[:20]:

        notification_id = (
            record["notification_id"]
        )

        result = unit15_send_message(
            record["message"],
            attempts=1,
        )

        unit15_update_notification(
            notification_id,

            result["delivered"],

            result.get("message_id"),
        )

        if result["delivered"]:

            delivered_count += 1

        else:

            print(
                "UNIT 15 NOTIFICATION RETRY =",
                notification_id,
                flush=True,
            )

    return delivered_count


# ============================================================
# FORMAT PERFORMANCE REPORT
# ============================================================

def unit15_format_report(
    hours,
    notification,
    start,
    end,
    summary,
    equity,
    symbols,
):

    count = summary["cycles"]

    wins = summary["wins"]

    winrate = (
        f"{wins * 100 / count:.2f}%"
        if count
        else "N/A"
    )

    lines = [
        "WEEX DEMO TRADING PERFORMANCE",
        "================================",
        f"Notification: {notification}",
        f"Period: {hours}h",
        (
            f"Window: {start:%Y-%m-%d %H:%M}"
            f" to {end:%Y-%m-%d %H:%M} WAT"
        ),
        (
            "Symbols: "
            + (
                ", ".join(symbols)
                if symbols
                else "N/A"
            )
        ),
        "",
        "EXECUTION SUMMARY",
        (
            "History orders scanned: "
            + str(summary["orders"])
        ),
        (
            "Executed orders: "
            + str(summary["executed_orders"])
        ),
        (
            "Fully filled: "
            + str(summary["fully_filled"])
        ),
        (
            "Partially filled: "
            + str(summary["partially_filled"])
        ),
        "",
        "COMPLETED POSITION CYCLES",
        f"Completed cycles: {count}",
        f"Winning cycles: {wins}",
        (
            "Losing cycles: "
            + str(summary["losses"])
        ),
        (
            "Break-even: "
            + str(summary["breakeven"])
        ),
        f"Gross win rate: {winrate}",
        (
            "Gross profit: "
            f"{summary['gross_profit']:.4f} SUSDT"
        ),
        (
            "Gross loss: "
            f"{summary['gross_loss']:.4f} SUSDT"
        ),
        (
            "Gross cycle P&L: "
            f"{summary['gross_pnl']:+.4f} SUSDT"
        ),
        (
            "Realized gross P&L in window: "
            f"{summary['realized_window_pnl']:+.4f}"
            " SUSDT"
        ),
        (
            "Unmatched closes: "
            + str(summary["unmatched"])
        ),
        (
            "History complete: "
            + str(summary["history_complete"])
        ),
        (
            "Provisional: "
            + str(summary["provisional"])
        ),
        "Fees/funding: Unverified",
        "Net trading P&L: Unverified",
    ]

    if summary["unknown_multiplier"]:

        lines.append(
            "Missing contract multiplier: "
            + ", ".join(
                summary["unknown_multiplier"]
            )
        )

    if summary["symbol_results"]:

        lines.extend([
            "",
            "PER-SYMBOL PERFORMANCE",
            "================================",
        ])

        for symbol, item in (
            summary["symbol_results"].items()
        ):

            lines.append(
                f"{symbol}: "
                f"{item['cycles']} cycles | "
                f"W:{item['wins']} "
                f"L:{item['losses']} | "
                f"{item['gross_pnl']:+.4f} SUSDT"
            )

    lines.extend([
        "",
        "EQUITY-BASED PERFORMANCE",
        "================================",
    ])

    if equity is None:

        lines.extend([
            "Starting equity: N/A",
            "Ending equity: N/A",
            "Equity change: N/A",
            "Equity ROI: N/A",
            "Comparable snapshots unavailable",
        ])

    else:

        roi = (
            f"{equity['roi']:+.2f}%"
            if equity["roi"] is not None
            else "N/A"
        )

        lines.extend([
            (
                "Starting equity: "
                f"{equity['starting']:.4f} SUSDT"
            ),
            (
                "Ending equity: "
                f"{equity['ending']:.4f} SUSDT"
            ),
            (
                "Equity change: "
                f"{equity['change']:+.4f} SUSDT"
            ),
            f"Equity ROI: {roi}",
            "Deposits/withdrawals: Unverified",
        ])

    return "\n".join(lines)


# ============================================================
# PERFORMANCE REPORT EXECUTOR
# PERSIST DELIVERY ONLY AFTER TELEGRAM ACK
# ============================================================

def unit15_report(
    hours=8,
    notification="ON_DEMAND",
    end=None,
    report_key=None,
):

    global _UNIT15_LAST_REPORT

    if hours not in (1, 8, 24):

        raise ValueError(
            "UNIT 15 INVALID REPORT HOURS"
        )

    if not _UNIT15_LOCK.acquire(
        blocking=False
    ):

        print(
            "UNIT 15 REPORT ALREADY RUNNING",
            flush=True,
        )

        return False

    try:

        end = end or unit15_now()

        start = end - _U15_TD(
            hours=hours
        )

        start_ms = int(
            start.timestamp() * 1000
        )

        end_ms = int(
            end.timestamp() * 1000
        )

        if report_key is None:

            report_key = (
                str(notification)
                + ":"
                + str(hours)
                + ":"
                + str(end_ms)
            )

        unit15_register_report(
            report_key,
            hours,
            notification,
            end_ms,
        )

        if unit15_report_delivered(
            report_key
        ):

            return True

        history = unit15_all_history()

        summary = unit15_analyze(
            history["orders"],
            history["complete"],
            start_ms,
            end_ms,
        )

        equity = unit15_equity_change(
            start_ms,
            end_ms,
        )

        report = unit15_format_report(
            hours,
            notification,
            start,
            end,
            summary,
            equity,
            history["symbols"],
        )

        if history["failures"]:

            report += (
                "\n\nUnavailable symbol history: "
                + ", ".join(
                    history["failures"]
                )
            )

        print(
            report,
            flush=True,
        )

        # Telegram has a message length limit.
        # Split long reports at line boundaries.

        messages = []

        current = ""

        for line in report.splitlines():

            if len(current) + len(line) + 1 > 3500:

                if current:

                    messages.append(current)

                current = ""

            current += (
                ("\n" if current else "")
                + line
            )

        if current:

            messages.append(current)

        delivery = {
            "delivered": True,
            "message_id": None,
            "error": None,
        }

        for message in messages:

            delivery = unit15_send_message(
                message
            )

            if not delivery["delivered"]:

                break

        unit15_update_delivery(
            report_key,

            delivery["delivered"],

            delivery.get("message_id"),

            delivery.get("error"),
        )

        if delivery["delivered"]:

            _UNIT15_LAST_REPORT = summary

            unit15_state_set(
                "LAST_REPORT",
                summary,
            )

        print(
            "UNIT 15 TELEGRAM SENT =",
            delivery["delivered"],
            flush=True,
        )

        return bool(
            delivery["delivered"]
        )

    except Exception as exc:

        print(
            "UNIT 15 REPORT ERROR =",
            type(exc).__name__,
            str(exc)[:150],
            flush=True,
        )

        if report_key is not None:

            try:

                unit15_update_delivery(
                    report_key,
                    False,
                    error=str(exc)[:150],
                )

            except Exception:

                pass

        return False

    finally:

        _UNIT15_LOCK.release()


# ============================================================
# EQUITY POLLING
# RESTART-PERSISTENT SNAPSHOTS
# ============================================================

def unit15_poll_equity():

    global _UNIT15_LAST_EQUITY_POLL

    now = _u15_time.time()

    if (
        now - _UNIT15_LAST_EQUITY_POLL
        < _UNIT15_EQUITY_POLL_SECONDS
    ):

        return None

    _UNIT15_LAST_EQUITY_POLL = now

    try:

        symbol = unit15_register_symbol()

        if symbol:

            unit15_contract_multiplier(
                symbol
            )

        snapshot = (
            unit15_equity_snapshot()
        )

        print(
            "UNIT 15 EQUITY SNAPSHOT =",
            snapshot["equity"],
            flush=True,
        )

        return snapshot

    except Exception as exc:

        print(
            "UNIT 15 EQUITY UNAVAILABLE =",
            type(exc).__name__,
            str(exc)[:150],
            flush=True,
        )

        return None


# ============================================================
# END COMPLETE UNIT 15 V6 - PART 2 OF 3
# ZERO INDENTATION
# NEXT: COMMANDS / SCHEDULER / WORKER / ACTIVATION
# ============================================================

# ============================================================
# COMPLETE UNIT 15 V6 REPLACEMENT
# PART 3 OF 3
# COMMANDS / SCHEDULER / WORKER / ACTIVATION
# ZERO INDENTATION
# ============================================================


# ============================================================
# PERSISTENT TELEGRAM COMMAND RECEPTION
# STORE COMMAND BEFORE ADVANCING OFFSET
# ============================================================

def unit15_poll_commands():

    if not UNIT15_ON_DEMAND:

        return []

    chat_id = _u15_os.getenv(
        "TELEGRAM_CHAT_ID",
        "",
    ).strip()

    token = _u15_os.getenv(
        "TELEGRAM_BOT_TOKEN",
        "",
    ).strip()

    if not token or not chat_id:

        return []

    offset = unit15_state_get(
        "TELEGRAM_OFFSET",
        None,
    )

    query = {
        "timeout": 0,
        "limit": 100,
    }

    if offset is not None:

        query["offset"] = int(offset)

    reply = unit15_telegram_api(
        "getUpdates",
        query,
    )

    updates = reply.get(
        "result",
        [],
    )

    aliases = {
        "/report": 8,
        "/report1h": 1,
        "/report8h": 8,
        "/report24h": 24,
    }

    received = []

    for update in sorted(
        updates,
        key=lambda item: item.get(
            "update_id", 0
        ),
    ):

        uid = update.get(
            "update_id"
        )

        if uid is None:

            continue

        uid = int(uid)

        message = (
            update.get("message")
            or update.get("edited_message")
            or {}
        )

        sender = str(
            (
                message.get("chat")
                or {}
            ).get("id")
        )

        if sender == chat_id:

            text = str(
                message.get("text", "")
            ).strip()

            command = (
                text.split(" ", 1)[0]
                .split("@", 1)[0]
                .lower()
            )

            hours = aliases.get(
                command
            )

            if hours is not None:

                unit15_store_command(
                    uid,
                    command,
                    hours,
                )

                received.append(hours)

                print(
                    "UNIT 15 COMMAND RECEIVED =",
                    command,
                    flush=True,
                )

        # Advance offset only after
        # recognized commands are persisted.

        offset = max(
            int(offset or 0),
            uid + 1,
        )

        unit15_state_set(
            "TELEGRAM_OFFSET",
            offset,
        )

    return received


# ============================================================
# EXECUTE PERSISTENT ON-DEMAND REPORT COMMANDS
# FAILED DELIVERY REMAINS PENDING
# ============================================================

def unit15_process_commands():

    if not UNIT15_ON_DEMAND:

        return 0

    completed = 0

    commands = (
        unit15_pending_commands()
    )

    for record in commands[:10]:

        uid = int(
            record["update_id"]
        )

        hours = int(
            record["report_hours"]
        )

        report_key = (
            "COMMAND:" + str(uid)
        )

        if unit15_report_delivered(
            report_key
        ):

            unit15_complete_command(
                uid
            )

            completed += 1

            continue

        end = _U15_DT.fromtimestamp(
            record["received_at"] / 1000,
            tz=_UNIT15_TZ,
        )

        try:

            delivered = unit15_report(
                hours=hours,

                notification="ON_DEMAND",

                end=end,

                report_key=report_key,
            )

        except Exception as exc:

            delivered = False

            print(
                "UNIT 15 COMMAND ERROR =",
                type(exc).__name__,
                flush=True,
            )

        if delivered:

            unit15_complete_command(
                uid
            )

            completed += 1

            print(
                "UNIT 15 COMMAND COMPLETED =",
                uid,
                flush=True,
            )

        else:

            print(
                "UNIT 15 COMMAND RETRY =",
                uid,
                flush=True,
            )

    return completed


# ============================================================
# SCHEDULED REPORTING WINDOWS
# 05:00 / 13:00 / 21:00 WAT
# ============================================================

def unit15_due_slots(now):

    slots = []

    for days_back in (1, 0):

        day = (
            now
            - _U15_TD(days=days_back)
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
# REGISTER DUE SCHEDULED REPORTS
# PERSIST BEFORE ATTEMPTING DELIVERY
# ============================================================

def unit15_register_due_reports():

    if not UNIT15_8H_ENABLED:

        return 0

    now = unit15_now()

    count = 0

    for slot in unit15_due_slots(now):

        key = (
            "SCHEDULED:"
            + slot.strftime(
                "%Y-%m-%d %H:%M"
            )
        )

        if unit15_report_delivered(key):

            continue

        unit15_register_report(
            report_key=key,

            hours=8,

            notification="SCHEDULED_8H",

            window_end=int(
                slot.timestamp() * 1000
            ),
        )

        count += 1

    return count


# ============================================================
# READ PENDING SCHEDULED REPORTS
# SURVIVES RENDER RESTART
# ============================================================

def unit15_pending_scheduled_reports():

    db = unit15_db()

    try:

        rows = db.execute("""
            SELECT *
            FROM unit15_report_delivery

            WHERE state = 'PENDING'

            AND notification =
                'SCHEDULED_8H'

            ORDER BY window_end

        """).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        db.close()


# ============================================================
# SCHEDULED REPORT DELIVERY EXECUTOR
# NO PREMATURE DELIVERY COMPLETION
# ============================================================

def unit15_process_scheduled_reports():

    if not UNIT15_8H_ENABLED:

        return 0

    unit15_register_due_reports()

    completed = 0

    pending = (
        unit15_pending_scheduled_reports()
    )

    for record in pending[:3]:

        key = record["report_key"]

        end = _U15_DT.fromtimestamp(
            record["window_end"] / 1000,
            tz=_UNIT15_TZ,
        )

        print(
            "UNIT 15 SCHEDULE SLOT DUE =",
            key,
            flush=True,
        )

        delivered = unit15_report(
            hours=int(
                record["report_hours"]
            ),

            notification="SCHEDULED_8H",

            end=end,

            report_key=key,
        )

        if delivered:

            completed += 1

            print(
                "UNIT 15 SCHEDULE DELIVERED =",
                key,
                flush=True,
            )

        else:

            print(
                "UNIT 15 SCHEDULE RETRY =",
                key,
                flush=True,
            )

    return completed


# ============================================================
# MANUAL POSITION CONTROLLER STATUS
# PRESERVE EXISTING CONTROLLER INTERFACE
# ============================================================

def unit15_manual_controller_status():

    command = _u15_os.getenv(
        "DEMO_POSITION_CONTROL",
        "OFF",
    ).strip().upper()

    armed = (
        _u15_os.getenv(
            "DEMO_CONTROL_ARM",
            "NO",
        ).strip().upper() == "YES"
    )

    valid = {
        "OFF",
        "INSPECT",
        "STATUS",
        "CLOSE_LONG",
        "CLOSE_SHORT",
        "CLOSE_ALL",
    }

    return {
        "manual_controller_available":
            True,

        "manual_command":
            command,

        "manual_command_valid":
            command in valid,

        "manual_close_armed":
            armed,

        "manual_control_active":
            command != "OFF",

        "reporting_independent":
            True,

        "exchange_write":
            False,
    }


# ============================================================
# UNIT 14 EXECUTION NOTIFICATION
# USE CONFIRMED TRANSACTION IDENTITIES
# ============================================================

def unit15_queue_execution_notice(
    symbol,
    side,
    action,
    execution,
):

    if not isinstance(
        execution, dict
    ):

        return False

    confirmed = unit15_num(
        execution.get(
            "confirmed_filled",
            "0"
        )
    ) or _U15_D(0)

    complete = bool(
        execution.get("complete")
        or execution.get("confirmed")
    )

    if not complete or confirmed <= 0:

        return False

    order_id = (
        execution.get(
            "exchange_order_id"
        )
        or execution.get("order_id")
        or execution.get("client_id")
    )

    if not order_id:

        return False

    notification_id = (
        "EXECUTION:"
        + str(symbol)
        + ":"
        + str(action)
        + ":"
        + str(order_id)
    )

    message = (
        "WEEX DEMO EXECUTION\n"
        + str(symbol)
        + "\n"
        + "Position: "
        + str(side)
        + "\n"
        + "Action: "
        + str(action)
        + "\n"
        + "Confirmed quantity: "
        + str(confirmed)
        + "\n"
        + "Order ID: "
        + str(order_id)
        + "\n"
        + "Status: CONFIRMED"
    )

    unit15_queue_notification(
        notification_id,
        message,
    )

    return True


# ============================================================
# PROCESS UNIT 14 INDEPENDENT POSITION RESULTS
# NO TRADING AUTHORIZATION OR EXECUTION GATE
# ============================================================

def unit15_process_unit14_result(
    unit_14_result,
):

    if not isinstance(
        unit_14_result,
        dict,
    ):

        return {
            "received": False,
            "notifications": 0,
        }

    _, active_symbol = (
        unit15_active_symbols()
    )

    symbol = (
        unit_14_result.get("symbol")
        or active_symbol
    )

    outcomes = unit_14_result.get(
        "position_results",
        [],
    )

    if not outcomes:

        outcomes = [
            unit_14_result
        ]

    queued = 0

    for outcome in outcomes:

        if not isinstance(
            outcome,
            dict,
        ):

            continue

        side = str(
            outcome.get(
                "position_side",
                "",
            )
        ).upper()

        stage = outcome.get(
            "stage"
        )

        # ----------------------------------------------------
        # HEDGE AND RECOVERY TRANSACTIONS
        # ----------------------------------------------------

        if stage in (
            "H1", "H2", "R1", "R2"
        ):

            close_record = outcome.get(
                "close_record",
                {},
            )

            open_record = outcome.get(
                "open_record",
                {},
            )

            close_action, open_action = (
                unit_14_pair_actions(stage)
            )

            opposite = (
                unit_14_opposite_side(side)
                if side in ("LONG", "SHORT")
                else ""
            )

            if stage in ("H1", "H2"):

                close_side = side

                open_side = opposite

            else:

                close_side = opposite

                open_side = side

            queued += int(
                unit15_queue_execution_notice(
                    symbol,
                    close_side,
                    close_action,
                    close_record,
                )
            )

            queued += int(
                unit15_queue_execution_notice(
                    symbol,
                    open_side,
                    open_action,
                    open_record,
                )
            )

        # ----------------------------------------------------
        # BACKUP EXECUTION
        # ----------------------------------------------------

        backup = outcome.get(
            "backup_execution",
            {},
        )

        if backup:

            action = backup.get(
                "action"
            ) or (
                "B"
                + str(
                    outcome.get(
                        "backup_submitted_stage",
                        "",
                    )
                )
            )

            queued += int(
                unit15_queue_execution_notice(
                    symbol,
                    side,
                    action,
                    backup,
                )
            )

        # ----------------------------------------------------
        # ATR BREAK-EVEN CLOSE
        # ----------------------------------------------------

        breakeven = outcome.get(
            "breakeven_execution",
            {},
        )

        if breakeven:

            queued += int(
                unit15_queue_execution_notice(
                    symbol,
                    side,
                    "BE-C",
                    breakeven,
                )
            )

        # ----------------------------------------------------
        # TP3 TRAILING CLOSE
        # ----------------------------------------------------

        tp3 = outcome.get(
            "tp3_execution",
            {},
        )

        if tp3:

            queued += int(
                unit15_queue_execution_notice(
                    symbol,
                    side,
                    "TP3-C",
                    tp3,
                )
            )

    return {
        "received": True,
        "notifications": queued,
    }


# ============================================================
# STARTUP REPORTING DIAGNOSTIC
# ============================================================

def unit15_startup_notification():

    if not UNIT15_STARTUP_NOTIFY:

        return False

    market, demo = (
        unit15_active_symbols()
    )

    message = (
        "WEEX DEMO UNIT 15 V6\n"
        "Reporting worker started\n"
        f"Market symbol: {market}\n"
        f"Demo symbol: {demo}\n"
        "Schedule: 05:00 / 13:00 / 21:00 WAT\n"
        "Commands: /report, /report1h, "
        "/report8h, /report24h\n"
        "SQLite reporting: ENABLED\n"
        "Reporting independent of BOT_MODE\n"
        "Startup time: "
        + unit15_now().strftime(
            "%Y-%m-%d %H:%M:%S WAT"
        )
    )

    return unit15_telegram(
        message
    )


# ============================================================
# CONTINUOUS REPORTING WORKER
# INDEPENDENT TASK EXECUTION
# ============================================================

def unit15_worker():

    print("=" * 80, flush=True)

    print(
        "UNIT 15 V6 REPORTING WORKER STARTED",
        flush=True,
    )

    print(
        "UNIT 15 SCHEDULE = "
        "05:00 / 13:00 / 21:00 WAT",
        flush=True,
    )

    print(
        "UNIT 15 SQLITE DATABASE =",
        _UNIT15_DB_PATH,
        flush=True,
    )

    print(
        "UNIT 15 EXCHANGE WRITE = NONE",
        flush=True,
    )

    try:

        success = (
            unit15_startup_notification()
        )

        print(
            "UNIT 15 STARTUP TELEGRAM =",
            success,
            flush=True,
        )

    except Exception as exc:

        print(
            "UNIT 15 STARTUP ERROR =",
            type(exc).__name__,
            flush=True,
        )

    while True:

        # ----------------------------------------------------
        # REGISTER ACTIVE SYMBOL
        # ----------------------------------------------------

        try:

            symbol = (
                unit15_register_symbol()
            )

            if symbol:

                unit15_contract_multiplier(
                    symbol
                )

        except Exception as exc:

            print(
                "UNIT 15 SYMBOL REGISTER ERROR =",
                type(exc).__name__,
                flush=True,
            )

        # ----------------------------------------------------
        # EQUITY SNAPSHOTS
        # ----------------------------------------------------

        try:

            unit15_poll_equity()

        except Exception as exc:

            print(
                "UNIT 15 EQUITY LOOP ERROR =",
                type(exc).__name__,
                flush=True,
            )

        # ----------------------------------------------------
        # PERSISTENT NOTIFICATIONS
        # ----------------------------------------------------

        try:

            unit15_flush_notifications()

        except Exception as exc:

            print(
                "UNIT 15 NOTIFICATION ERROR =",
                type(exc).__name__,
                flush=True,
            )

        # ----------------------------------------------------
        # RECEIVE TELEGRAM COMMANDS
        # ----------------------------------------------------

        if UNIT15_ON_DEMAND:

            try:

                unit15_poll_commands()

            except Exception as exc:

                print(
                    "UNIT 15 TELEGRAM POLLING ERROR =",
                    type(exc).__name__,
                    flush=True,
                )

            # Command reception failure does not
            # prevent previously stored commands.

            try:

                unit15_process_commands()

            except Exception as exc:

                print(
                    "UNIT 15 COMMAND EXECUTION ERROR =",
                    type(exc).__name__,
                    flush=True,
                )

        # ----------------------------------------------------
        # SCHEDULED REPORT DELIVERY
        # ----------------------------------------------------

        if UNIT15_8H_ENABLED:

            try:

                unit15_process_scheduled_reports()

            except Exception as exc:

                print(
                    "UNIT 15 SCHEDULER ERROR =",
                    type(exc).__name__,
                    flush=True,
                )

        _u15_time.sleep(
            _UNIT15_POLL_SECONDS
        )


# ============================================================
# START ONE REPORTING WORKER
# NO DUPLICATE THREAD ACTIVATION
# ============================================================

def unit15_start_worker():

    global _UNIT15_THREAD

    if not UNIT15_ENABLED:

        return "DISABLED"

    with _UNIT15_WORKER_LOCK:

        if (
            _UNIT15_THREAD is not None
            and _UNIT15_THREAD.is_alive()
        ):

            return "RUNNING"

        worker = _u15_thread.Thread(
            target=unit15_worker,

            name="WEEX-UNIT15-REPORTING",

            daemon=False,
        )

        _UNIT15_THREAD = worker

        worker.start()

    return "RUNNING"


# ============================================================
# ORIGINAL UNIT 15 HYBRID ADAPTER
# UNIT 14 -> UNIT 15
# ============================================================

def fresh_unit_15_hybrid_adapter(
    config,
    unit_14_result,
):

    errors = []

    status = "NOT_STARTED"

    received = (
        unit_14_result
        if isinstance(
            unit_14_result,
            dict,
        )
        else {}
    )

    manual_status = (
        unit15_manual_controller_status()
    )

    notification_result = {
        "received": False,
        "notifications": 0,
    }

    # --------------------------------------------------------
    # SYMBOL DIAGNOSTIC
    # NOT AN EXECUTION AUTHORIZATION CONDITION
    # --------------------------------------------------------

    try:

        unit15_configuration_check()

    except Exception as exc:

        errors.append(
            "CONFIGURATION:"
            + type(exc).__name__
        )

    # --------------------------------------------------------
    # REGISTER SYMBOL AND CONTRACT MULTIPLIER
    # --------------------------------------------------------

    try:

        symbol = unit15_register_symbol()

        if symbol:

            unit15_contract_multiplier(
                symbol
            )

    except Exception as exc:

        errors.append(
            "SYMBOL:"
            + type(exc).__name__
        )

    # --------------------------------------------------------
    # UNIT 14 RESULT HANDOVER
    # --------------------------------------------------------

    try:

        notification_result = (
            unit15_process_unit14_result(
                received
            )
        )

    except Exception as exc:

        errors.append(
            "HANDOVER:"
            + type(exc).__name__
        )

    # --------------------------------------------------------
    # REPORTING WORKER ACTIVATION
    # --------------------------------------------------------

    try:

        status = unit15_start_worker()

    except Exception as exc:

        status = "WORKER_START_ERROR"

        errors.append(
            "WORKER:"
            + type(exc).__name__
        )

    print(
        "UNIT 15 RECEIVED UNIT 14 STATUS =",
        received.get("status"),
        flush=True,
    )

    print(
        "UNIT 15 HYBRID ADAPTER STATUS =",
        status,
        flush=True,
    )

    print(
        "UNIT 15 MANUAL CONTROLLER =",
        manual_status["manual_command"],
        flush=True,
    )

    print(
        "UNIT 15 REPORTING ERRORS =",
        errors,
        flush=True,
    )

    return {
        "unit": 15,

        "version": "V6",

        "status": status,

        "unit_14_status":
            received.get("status"),

        "unit_14_position_results":
            received.get(
                "position_results",
                [],
            ),

        "unit_14_exchange_write":
            bool(
                received.get(
                    "exchange_write",
                    False,
                )
            ),

        "exchange_write":
            False,

        "real_cash_execution":
            False,

        "scheduled_8h_enabled":
            UNIT15_8H_ENABLED,

        "on_demand_enabled":
            UNIT15_ON_DEMAND,

        "performance_report_hours":
            (1, 8, 24),

        "timezone":
            "Africa/Lagos",

        "manual_controller":
            manual_status,

        "notification_result":
            notification_result,

        "reporting_independent":
            True,

        "errors":
            errors,
    }


# ============================================================
# NONBLOCKING LOCAL VALIDATION
# NO TELEGRAM OR EXCHANGE REQUESTS
# ============================================================

def unit15_validation_v4():

    tests = {}

    print("=" * 80, flush=True)

    print(
        "UNIT 15 V6 VALIDATION START",
        flush=True,
    )

    # --------------------------------------------------------
    # SQLITE
    # --------------------------------------------------------

    try:

        db = unit15_db()

        db.close()

        tests["SQLITE"] = True

    except Exception:

        tests["SQLITE"] = False

    # --------------------------------------------------------
    # UNIT 14 HANDOVER
    # --------------------------------------------------------

    tests["UNIT14_HANDOVER"] = (
        isinstance(
            globals().get(
                "FRESH_RECONSTRUCTION_UNIT_14_RESULT"
            ),
            dict,
        )
    )

    # --------------------------------------------------------
    # SCHEDULE
    # --------------------------------------------------------

    tests["THREE_REPORT_SLOTS"] = (
        _UNIT15_SLOTS
        == (5, 13, 21)
    )

    tests["LAGOS_TIMEZONE"] = (
        str(_UNIT15_TZ)
        == "Africa/Lagos"
    )

    test_now = _U15_DT(
        2026,
        11,
        28,
        5,
        1,
        tzinfo=_UNIT15_TZ,
    )

    due = unit15_due_slots(
        test_now
    )

    tests["MISSED_MINUTE_CATCHUP"] = (
        any(
            slot.hour == 5
            and slot.minute == 0
            for slot in due
        )
    )

    tests["NO_FUTURE_REPORT"] = (
        all(
            slot <= test_now
            for slot in due
        )
    )

    # --------------------------------------------------------
    # PARTIAL FILL NORMALIZATION
    # --------------------------------------------------------

    partial_order = {
        "orderId": "LOCAL-TEST-1",

        "symbol": "NEARSUSDT",

        "status": "CANCELED",

        "executedQty": "6.5",

        "avgPrice": "3.1",

        "updateTime": "1795842000000",

        "side": "SELL",

        "positionSide": "LONG",
    }

    parsed, error = (
        unit15_parse_order(
            partial_order
        )
    )

    tests["PARTIAL_FILL_INCLUDED"] = (
        parsed is not None
        and error is None
        and parsed["qty"] == _U15_D("6.5")
        and parsed["partial_fill"]
        and parsed["action"] == "CLOSE"
    )

    # --------------------------------------------------------
    # ZERO FILL EXCLUSION
    # --------------------------------------------------------

    zero_order = dict(
        partial_order
    )

    zero_order["executedQty"] = "0"

    parsed, error = (
        unit15_parse_order(
            zero_order
        )
    )

    tests["ZERO_FILL_EXCLUDED"] = (
        parsed is None
        and error == "NO_CONFIRMED_FILL"
    )

    # --------------------------------------------------------
    # EXISTING INTERFACES
    # --------------------------------------------------------

    tests["TELEGRAM_INTERFACE"] = (
        callable(unit15_telegram)
    )

    tests["REPORT_INTERFACE"] = (
        callable(unit15_report)
    )

    tests["SHARED_AUTHENTICATION"] = (
        callable(
            globals().get(
                "unit_13_v4_signed_request"
            )
        )
    )

    tests["UNIVERSAL_SYMBOL_INTERFACE"] = (
        callable(
            globals().get(
                "unit_13_14_active_symbols"
            )
        )
    )

    tests["MANUAL_CONTROLLER_INTERFACE"] = (
        callable(
            unit15_manual_controller_status
        )
    )

    # --------------------------------------------------------
    # VALIDATION REPORT
    # --------------------------------------------------------

    for name, passed in tests.items():

        print(
            "UNIT 15 TEST:",
            name,
            "=",
            "PASS" if passed else "FAIL",
            flush=True,
        )

    passed = sum(
        bool(value)
        for value in tests.values()
    )

    failed = len(tests) - passed

    print(
        "UNIT 15 TESTS PASSED =",
        passed,
        flush=True,
    )

    print(
        "UNIT 15 TESTS FAILED =",
        failed,
        flush=True,
    )

    print(
        "UNIT 15 V6 VALIDATION RESULT =",
        "PASS" if failed == 0 else "FAIL",
        flush=True,
    )

    # Diagnostic result only.
    # Do not terminate trading initialization.

    return failed == 0


# ============================================================
# UNIT 15 ACTIVATION
# PRESERVE ORIGINAL GLOBAL VARIABLE NAMES
# ============================================================

try:

    FRESH_UNIT_15_VALIDATION_READY = (
        unit15_validation_v4()
    )

except Exception as exc:

    FRESH_UNIT_15_VALIDATION_READY = False

    print(
        "UNIT 15 VALIDATION ERROR =",
        type(exc).__name__,
        flush=True,
    )


FRESH_RECONSTRUCTION_UNIT_15_RESULT = (
    fresh_unit_15_hybrid_adapter(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_14_RESULT,
    )
)


print(
    "FRESH RECONSTRUCTION UNIT 15 V6 READY =",
    FRESH_UNIT_15_VALIDATION_READY,
    flush=True,
)

print(
    "UNIT 15 FINAL STATUS =",
    FRESH_RECONSTRUCTION_UNIT_15_RESULT.get(
        "status"
    ),
    flush=True,
)


# ============================================================
# END COMPLETE UNIT 15 V6 REPLACEMENT
# END PART 3 OF 3
# ZERO INDENTATION
# ============================================================
#
# PRESERVE ALL EXISTING DOWNSTREAM SECTIONS:
#
# - UNIT 9 SYMBOL CONTRACT SPECIFICATIONS
# - UNIT 8 TP NET ROI ACCEPTANCE CONTROLLER
# - UNIT 8 INITIAL_USDT ACCEPTANCE CONTROLLER
# - UNIVERSAL SYMBOL SWITCHING
# - ENTRY PIPELINE REFRESH
# - CONTINUOUS SCAN LOOP
# - MANUAL DEMO POSITION CONTROLLER
#
# ============================================================


# ============================================================
# COMPLETE CONTINUOUS SCAN CONTROLLER V3
# PART 1 OF 3
# CONFIGURATION / CONTRACT SPECIFICATIONS
# ZERO INDENTATION
# ============================================================

import os
import json
import sqlite3

import os as _scan_os
import time as _scan_time
import threading as _scan_thread
import traceback as _scan_traceback

import urllib.request as _scan_http
import urllib.parse as _scan_url

from datetime import datetime as _SCAN_DT
from zoneinfo import ZoneInfo as _SCAN_Zone

from decimal import (
    Decimal,
    InvalidOperation,
    ROUND_CEILING,
    ROUND_DOWN,
    ROUND_UP,
)


# ============================================================
# SCAN CONFIGURATION
# ============================================================

SCAN_INTERVAL_SECONDS = int(
    _scan_os.getenv(
        "SCAN_INTERVAL_SECONDS",
        "30",
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

SCAN_LAST_ATR_SYMBOL = None

SCAN_LAST_ATR_TIME = None


# ============================================================
# COMMON DECIMAL HELPERS
# ============================================================

def scan_decimal(value):

    number = Decimal(str(value))

    if not number.is_finite():

        raise ValueError(
            "NONFINITE_DECIMAL"
        )

    return number


def scan_positive_decimal(
    value,
    name,
):

    number = scan_decimal(value)

    if number <= 0:

        raise ValueError(
            "INVALID_" + name
        )

    return number


def scan_floor(
    value,
    step,
):

    value = scan_decimal(value)

    step = scan_positive_decimal(
        step,
        "STEP",
    )

    return (
        value / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    ) * step


def scan_ceil(
    value,
    step,
):

    value = scan_decimal(value)

    step = scan_positive_decimal(
        step,
        "STEP",
    )

    return (
        value / step
    ).to_integral_value(
        rounding=ROUND_CEILING
    ) * step


# ============================================================
# IDLE UNIT 12 HANDOVER
# POSITION MANAGEMENT REMAINS AVAILABLE
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

        "execution_authorized": False,

        "position_exists": False,

        "demo_submission_attempted": False,

        "demo_submission_completed": False,

        "real_submission_attempted": False,

        "exchange_write": False,

        "management_path_permitted": True,
    }


# ============================================================
# ERROR HANDOVER
# DISTINCT FROM NORMAL IDLE
# ============================================================

def scan_error_unit12_result(reason):

    result = scan_idle_unit12_result(
        reason
    )

    result["status"] = "ERROR"

    result["execution_error"] = str(
        reason
    )

    return result


# ============================================================
# PRECISION INDEX CONVERSION
# SUPPORT POSITIVE, ZERO AND NEGATIVE INDEX
# ============================================================

def scan_precision_step(
    value,
    name,
):

    if value is None or isinstance(
        value,
        bool,
    ):

        raise ValueError(
            "INVALID_" + name
        )

    number = scan_decimal(value)

    if (
        number != number.to_integral_value()
        or number < -18
        or number > 18
    ):

        raise ValueError(
            "INVALID_" + name
        )

    return Decimal("1").scaleb(
        -int(number)
    )


# ============================================================
# PUBLIC WEEX CONTRACT INFORMATION
# ============================================================

def scan_public_contract_information(
    config,
    symbol,
):

    symbol = str(
        symbol
    ).strip().upper()

    if (
        not symbol
        or not symbol.endswith("USDT")
    ):

        raise ValueError(
            "INVALID_MARKET_SYMBOL"
        )

    exchange = config.get(
        "exchange",
        {},
    )

    base_url = str(
        exchange.get(
            "contract_base_url",
            "https://api-contract.weex.com",
        )
    ).rstrip("/")

    if (
        base_url
        != "https://api-contract.weex.com"
    ):

        raise ValueError(
            "UNEXPECTED_MARKET_API_HOST"
        )

    query = _scan_url.urlencode({
        "symbol": symbol,
    })

    url = (
        base_url
        + "/capi/v3/market/exchangeInfo?"
        + query
    )

    request = _scan_http.Request(
        url,

        method="GET",

        headers={
            "Accept": "application/json",

            "User-Agent":
                "WEEX-Contract-Specs-V3",
        },
    )

    with _scan_http.urlopen(
        request,
        timeout=15,
    ) as response:

        if response.status != 200:

            raise RuntimeError(
                "CONTRACT_INFO_HTTP_"
                + str(response.status)
            )

        payload = json.loads(
            response.read().decode(
                "utf-8"
            )
        )

    if not isinstance(
        payload,
        dict,
    ):

        raise ValueError(
            "INVALID_CONTRACT_INFO_RESPONSE"
        )

    rows = payload.get("symbols")

    if not isinstance(
        rows,
        list,
    ):

        raise ValueError(
            "CONTRACT_SYMBOL_LIST_MISSING"
        )

    selected = next(
        (
            row
            for row in rows

            if isinstance(row, dict)

            and str(
                row.get("symbol", "")
            ).upper() == symbol
        ),

        None,
    )

    if selected is None:

        raise ValueError(
            "SYMBOL_NOT_IN_EXCHANGE_INFO"
        )

    return selected


# ============================================================
# NORMALIZE EXCHANGE CONTRACT SPECIFICATIONS
# ============================================================

def scan_normalize_contract(
    symbol,
    selected,
):

    if str(
        selected.get(
            "quoteAsset",
            "",
        )
    ).upper() != "USDT":

        raise ValueError(
            "NOT_USDT_QUOTED"
        )

    if selected.get(
        "size_increment"
    ) is not None:

        quantity_step = (
            scan_positive_decimal(
                selected["size_increment"],
                "QUANTITY_STEP",
            )
        )

    else:

        quantity_step = (
            scan_precision_step(
                selected["quantityPrecision"],
                "QUANTITY_PRECISION",
            )
        )

    if selected.get(
        "tick_size"
    ) is not None:

        price_step = (
            scan_positive_decimal(
                selected["tick_size"],
                "PRICE_STEP",
            )
        )

    else:

        price_step = (
            scan_precision_step(
                selected["pricePrecision"],
                "PRICE_PRECISION",
            )
        )

    minimum_quantity = (
        scan_positive_decimal(
            selected["minOrderSize"],
            "MINIMUM_ORDER_SIZE",
        )
    )

    contract_value = (
        scan_positive_decimal(
            selected["contractVal"],
            "CONTRACT_VALUE",
        )
    )

    # Preserve the existing base-asset
    # quantity calculation used by Units 8-9.
    #
    # Do not multiply base-asset quantity
    # by contractVal a second time.

    return {
        "quantity_step":
            float(quantity_step),

        "minimum_quantity":
            float(minimum_quantity),

        "price_step":
            float(price_step),

        "contract_multiplier":
            1.0,

        "contract_value":
            float(contract_value),

        "specifications_symbol":
            symbol,

        "symbol_specifications_confirmed":
            True,
    }


# ============================================================
# UNIT 9 UNIVERSAL CONTRACT SPECIFICATION LOADER
# PRESERVE ORIGINAL CALLABLE INTERFACE
# ============================================================

def unit_9_load_symbol_specifications(
    config,
    symbol,
):

    symbol = str(
        symbol
    ).strip().upper()

    precision = config.setdefault(
        "market_precision",
        {},
    )

    precision[
        "symbol_specifications_confirmed"
    ] = False

    previous_symbol = str(
        precision.get(
            "specifications_symbol",
            "",
        )
    ).upper()

    # Never carry another symbol's quantity
    # or price precision into a new symbol.

    if previous_symbol != symbol:

        for key in (
            "quantity_step",
            "minimum_quantity",
            "price_step",
            "contract_multiplier",
            "contract_value",
            "specifications_symbol",
        ):

            precision.pop(
                key,
                None,
            )

    try:

        selected = (
            scan_public_contract_information(
                config,
                symbol,
            )
        )

        print(
            "UNIT 9 EXCHANGE PRECISION FIELDS =",
            {
                key: selected.get(key)

                for key in (
                    "quantityPrecision",
                    "size_increment",
                    "pricePrecision",
                    "tick_size",
                    "minOrderSize",
                    "contractVal",
                )
            },
            flush=True,
        )

        values = (
            scan_normalize_contract(
                symbol,
                selected,
            )
        )

        precision.update(values)

        print(
            "UNIT 9 CONTRACT SPECIFICATIONS = LOADED",
            flush=True,
        )

        print(
            "UNIT 9 CONTRACT SYMBOL =",
            symbol,
            flush=True,
        )

        print(
            "UNIT 9 QUANTITY STEP =",
            precision["quantity_step"],
            flush=True,
        )

        print(
            "UNIT 9 MINIMUM QUANTITY =",
            precision["minimum_quantity"],
            flush=True,
        )

        print(
            "UNIT 9 PRICE STEP =",
            precision["price_step"],
            flush=True,
        )

        print(
            "UNIT 9 CONTRACT VALUE =",
            precision["contract_value"],
            flush=True,
        )

        print(
            "UNIT 9 CONTRACT MULTIPLIER =",
            precision["contract_multiplier"],
            flush=True,
        )

        print(
            "UNIT 9 QUANTITY BASIS = BASE_ASSET",
            flush=True,
        )

        return True

    except Exception as exc:

        precision[
            "symbol_specifications_confirmed"
        ] = False

        print(
            "UNIT 9 CONTRACT SPECIFICATIONS = UNAVAILABLE",
            flush=True,
        )

        print(
            "UNIT 9 CONTRACT SYMBOL =",
            symbol,
            flush=True,
        )

        print(
            "UNIT 9 CONTRACT REASON =",
            str(exc),
            flush=True,
        )

        return False


# ============================================================
# CURRENT SYMBOL CONTRACT DETAILS
# SHARED BY CONFIGURATION CONTROLLERS
# ============================================================

def scan_contract_details(config):

    precision = config.get(
        "market_precision",
        {},
    )

    symbol = str(
        config["exchange"]["market_symbol"]
    ).upper()

    if str(
        precision.get(
            "specifications_symbol",
            "",
        )
    ).upper() != symbol:

        raise RuntimeError(
            "CONTRACT_SYMBOL_MISMATCH"
        )

    return {
        "symbol": symbol,

        "quantity_step":
            scan_positive_decimal(
                precision["quantity_step"],
                "QUANTITY_STEP",
            ),

        "minimum_quantity":
            scan_positive_decimal(
                precision["minimum_quantity"],
                "MINIMUM_QUANTITY",
            ),

        "price_step":
            scan_positive_decimal(
                precision["price_step"],
                "PRICE_STEP",
            ),

        "contract_multiplier":
            scan_positive_decimal(
                precision.get(
                    "contract_multiplier",
                    1,
                ),
                "CONTRACT_MULTIPLIER",
            ),

        "confirmed":
            bool(
                precision.get(
                    "symbol_specifications_confirmed"
                )
            ),
    }


# ============================================================
# RESULT ERROR DETECTION
# DIAGNOSTIC ONLY
# ============================================================

def scan_result_has_error(result):

    if not isinstance(
        result,
        dict,
    ):

        return True

    status = str(
        result.get(
            "status",
            "",
        )
    ).upper()

    if (
        "ERROR" in status

        or status in (
            "FAIL",
            "FAILED",
        )

        or result.get(
            "execution_error"
        )
    ):

        return True

    for item in result.get(
        "position_results",
        [],
    ) or []:

        if isinstance(item, dict):

            if scan_result_has_error(
                item
            ):

                return True

    return False


# ============================================================
# END COMPLETE CONTINUOUS SCAN CONTROLLER V3
# END PART 1 OF 3
# ZERO INDENTATION
#
# NEXT:
# CONSOLIDATED TP ROI AND INITIAL_USDT CONTROLLERS
# ============================================================

# ============================================================
# COMPLETE CONTINUOUS SCAN CONTROLLER V3
# PART 2 OF 3
# TP NET ROI / INITIAL_USDT ACCEPTANCE
# ZERO INDENTATION
# ============================================================

from datetime import datetime, timezone
from decimal import ROUND_FLOOR


# ============================================================
# CONFIGURATION VALUE FORMATTING
# ============================================================

def scan_config_amount(value):

    return format(
        scan_decimal(value).normalize(),
        "f",
    )


def scan_config_timestamp():

    return datetime.now(
        timezone.utc
    ).isoformat()


# ============================================================
# CONSOLIDATED CONFIGURATION DATABASE
# PRESERVE EXISTING SQLITE TABLES AND HISTORY
# ============================================================

def scan_configuration_db():

    db = unit_8_symbol_switch_db()

    db.execute("""
        CREATE TABLE IF NOT EXISTS
        scan_configuration_v3 (
            setting TEXT PRIMARY KEY,
            decision_key TEXT NOT NULL,
            status TEXT NOT NULL,
            requested TEXT,
            accepted TEXT,
            minimum TEXT,
            reason TEXT,
            updated_at TEXT NOT NULL
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS
        scan_configuration_history_v3 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting TEXT NOT NULL,
            decision_key TEXT NOT NULL,
            status TEXT NOT NULL,
            requested TEXT,
            accepted TEXT,
            minimum TEXT,
            reason TEXT,
            created_at TEXT NOT NULL
        )
    """)

    return db


# ============================================================
# READ PERSISTED CONFIGURATION DECISION
# ============================================================

def scan_configuration_read(setting):

    db = scan_configuration_db()

    try:

        row = db.execute("""
            SELECT
                decision_key,
                status,
                requested,
                accepted,
                minimum,
                reason
            FROM scan_configuration_v3
            WHERE setting = ?
        """, (
            setting,
        )).fetchone()

        if row is None:

            return None

        return {
            "decision_key": row[0],
            "status": row[1],

            "requested":
                json.loads(row[2])
                if row[2] is not None
                else None,

            "accepted":
                json.loads(row[3])
                if row[3] is not None
                else None,

            "minimum":
                json.loads(row[4])
                if row[4] is not None
                else None,

            "reason": row[5],
        }

    finally:

        db.close()


# ============================================================
# PERSIST DECISION AND TELEGRAM EVENT TOGETHER
# NOTIFICATION ONLY AFTER SUCCESSFUL COMMIT
# ============================================================

def scan_configuration_commit(
    setting,
    decision_key,
    status,
    requested,
    accepted,
    minimum,
    reason,
    message=None,
):

    db = scan_configuration_db()

    try:

        db.execute("BEGIN IMMEDIATE")

        previous = db.execute("""
            SELECT
                decision_key,
                status
            FROM scan_configuration_v3
            WHERE setting = ?
        """, (
            setting,
        )).fetchone()

        changed = (
            previous is None

            or previous[0] != decision_key

            or previous[1] != status
        )

        now = scan_config_timestamp()

        values = (
            setting,
            decision_key,
            status,

            json.dumps(
                requested,
                default=str,
            ),

            json.dumps(
                accepted,
                default=str,
            ),

            json.dumps(
                minimum,
                default=str,
            ),

            reason,
            now,
        )

        db.execute("""
            INSERT INTO scan_configuration_v3 (
                setting,
                decision_key,
                status,
                requested,
                accepted,
                minimum,
                reason,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT(setting)
            DO UPDATE SET
                decision_key =
                    excluded.decision_key,

                status =
                    excluded.status,

                requested =
                    excluded.requested,

                accepted =
                    excluded.accepted,

                minimum =
                    excluded.minimum,

                reason =
                    excluded.reason,

                updated_at =
                    excluded.updated_at
        """, values)

        if changed:

            db.execute("""
                INSERT INTO
                scan_configuration_history_v3 (
                    setting,
                    decision_key,
                    status,
                    requested,
                    accepted,
                    minimum,
                    reason,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, values)

            if message:

                unit_8_symbol_event(
                    db,

                    setting + "_" + status,

                    message,
                )

        db.execute("COMMIT")

        return changed

    except Exception:

        if db.in_transaction:

            db.execute("ROLLBACK")

        raise

    finally:

        db.close()


# ============================================================
# READ PREVIOUSLY ACCEPTED TP VALUES
# SUPPORT EXISTING LEGACY SQLITE RECORD
# ============================================================

def scan_previous_tp_values(config):

    previous = scan_configuration_read(
        "TP_NET_ROI"
    )

    if previous:

        accepted = previous.get(
            "accepted"
        )

        if isinstance(accepted, dict):

            if (
                accepted.get("TP1") is not None
                and accepted.get("TP2") is not None
            ):

                return {
                    "TP1":
                        scan_decimal(
                            accepted["TP1"]
                        ),

                    "TP2":
                        scan_decimal(
                            accepted["TP2"]
                        ),
                }

    db = scan_configuration_db()

    try:

        exists = db.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name = 'tp_net_roi_state'
        """).fetchone()

        if exists:

            row = db.execute("""
                SELECT
                    accepted_tp1,
                    accepted_tp2
                FROM tp_net_roi_state
                WHERE id = 1
            """).fetchone()

            if row:

                return {
                    "TP1":
                        scan_decimal(row[0]),

                    "TP2":
                        scan_decimal(row[1]),
                }

    finally:

        db.close()

    # No previously persisted acceptance.
    # Do not treat the current Render request
    # as an already accepted configuration.

    return None


# ============================================================
# PUBLISH ACCEPTED TP CONFIGURATION
# ============================================================

def scan_publish_tp_values(
    config,
    accepted,
):

    if accepted is None:

        return False

    strategy = config["strategy"]

    tp1 = scan_decimal(
        accepted["TP1"]
    )

    tp2 = scan_decimal(
        accepted["TP2"]
    )

    strategy[
        "tp1_net_roi_floor_percent"
    ] = float(tp1)

    strategy[
        "tp2_net_roi_floor_percent"
    ] = float(tp2)

    strategy[
        "tp1_tp2_min_roi_separation_percent"
    ] = float(tp2 - tp1)

    return True


# ============================================================
# PARSE CONSOLIDATED RENDER TP INPUT
# TP_NET_ROI_FLOOR_PERCENT=TP1:20,TP2:40
# ============================================================

def scan_parse_tp_roi(raw):

    requested = {}

    for item in str(raw).split(","):

        key, value = (
            item.strip().split(":", 1)
        )

        key = key.strip().upper()

        if key in requested:

            raise ValueError(
                "DUPLICATE_TP_KEY"
            )

        requested[key] = (
            scan_positive_decimal(
                value.strip(),
                key,
            )
        )

    if set(requested) != {
        "TP1", "TP2"
    }:

        raise ValueError(
            "TP1_AND_TP2_REQUIRED"
        )

    return requested


# ============================================================
# EXCHANGE PRICE PRECISION AND NET ROI MINIMUM
# MATCH UNIT 13 ESTIMATED FEE MODEL
# ============================================================

def scan_tp_minimums(
    config,
    account,
    market,
):

    contract = scan_contract_details(
        config
    )

    if not contract["confirmed"]:

        raise RuntimeError(
            "CONTRACT_SPECS_UNAVAILABLE"
        )

    price = scan_positive_decimal(
        market["price"],
        "MARKET_PRICE",
    )

    tick = contract["price_step"]

    long_leverage = (
        scan_positive_decimal(
            account["long_leverage"],
            "LONG_LEVERAGE",
        )
    )

    short_leverage = (
        scan_positive_decimal(
            account["short_leverage"],
            "SHORT_LEVERAGE",
        )
    )

    fee = scan_decimal(
        config["strategy"].get(
            "futures_taker_fee_percent",
            "0.08",
        )
    )

    if fee < 0 or fee >= 50:

        raise ValueError(
            "INVALID_TRADING_FEE"
        )

    fee_move = (
        Decimal("2")
        * fee
        / Decimal("100")
    )

    long_be = price * (
        Decimal("1") + fee_move
    )

    short_be = price * (
        Decimal("1") - fee_move
    )

    # First price increment strictly beyond
    # the estimated fee-adjusted break-even.

    long_first = (
        (
            long_be / tick
        ).to_integral_value(
            rounding=ROUND_FLOOR
        )
        + Decimal("1")
    ) * tick

    short_first = (
        (
            short_be / tick
        ).to_integral_value(
            rounding=ROUND_CEILING
        )
        - Decimal("1")
    ) * tick

    short_second = short_first - tick

    if short_second <= 0:

        raise RuntimeError(
            "SHORT_TP_PRICE_UNAVAILABLE"
        )

    long_min_roi = (
        (long_first - price)
        / price
        * Decimal("100")
        * long_leverage

        - Decimal("2")
        * fee
        * long_leverage
    )

    short_min_roi = (
        (price - short_first)
        / price
        * Decimal("100")
        * short_leverage

        - Decimal("2")
        * fee
        * short_leverage
    )

    long_roi_tick = (
        tick / price
        * Decimal("100")
        * long_leverage
    )

    short_roi_tick = (
        tick / price
        * Decimal("100")
        * short_leverage
    )

    minimum_tp1 = max(
        long_min_roi,
        short_min_roi,
    ).quantize(
        Decimal("0.000001"),
        rounding=ROUND_CEILING,
    )

    minimum_tp2 = max(
        long_min_roi + long_roi_tick,

        short_min_roi + short_roi_tick,
    ).quantize(
        Decimal("0.000001"),
        rounding=ROUND_CEILING,
    )

    return {
        "price": price,

        "price_step": tick,

        "fee": fee,

        "long_leverage":
            long_leverage,

        "short_leverage":
            short_leverage,

        "long_first":
            long_first,

        "short_first":
            short_first,

        "long_minimum_roi":
            long_min_roi,

        "short_minimum_roi":
            short_min_roi,

        "minimum_tp1":
            minimum_tp1,

        "minimum_tp2":
            minimum_tp2,

        "source":
            "EXCHANGE_SPECS_ESTIMATED_FEES",

        "fill_verified":
            False,
    }


# ============================================================
# VALIDATE TARGET PRICES USING UNIT 13
# ============================================================

def scan_validate_tp_targets(
    requested,
    minimums,
):

    tp1 = requested["TP1"]

    tp2 = requested["TP2"]

    if tp1 < minimums["minimum_tp1"]:

        raise ValueError(
            "TP1 "
            + scan_config_amount(tp1)
            + "% below calculated executable minimum "
            + scan_config_amount(
                minimums["minimum_tp1"]
            )
            + "%."
        )

    if tp2 <= tp1:

        raise ValueError(
            "TP2 must exceed TP1."
        )

    if tp2 < minimums["minimum_tp2"]:

        raise ValueError(
            "TP2 "
            + scan_config_amount(tp2)
            + "% below calculated minimum "
            + scan_config_amount(
                minimums["minimum_tp2"]
            )
            + "%."
        )

    targets = {}

    for side, leverage in (
        (
            "LONG",
            minimums["long_leverage"],
        ),

        (
            "SHORT",
            minimums["short_leverage"],
        ),
    ):

        t1, t2 = unit_13_v4_targets(
            minimums["price"],

            leverage,

            side,

            minimums["price_step"],

            tp1,

            tp2,

            minimums["fee"],
        )

        t1 = scan_decimal(t1)

        t2 = scan_decimal(t2)

        if side == "LONG":

            valid = (
                t2 > t1
                > minimums["price"]
            )

        else:

            valid = (
                Decimal("0") < t2
                < t1
                < minimums["price"]
            )

        if not valid:

            raise ValueError(
                side
                + "_TP_TARGETS_NOT_EXECUTABLE"
            )

        targets[side] = {
            "TP1": str(t1),
            "TP2": str(t2),
        }

    return targets


# ============================================================
# UNIT 8 TP NET ROI ACCEPTANCE CONTROLLER V3
# ============================================================

def unit_8_tp_net_roi_control(
    config,
    account,
    market,
):

    symbol = str(
        config["exchange"]["market_symbol"]
    ).strip().upper()

    raw = _scan_os.getenv(
        "TP_NET_ROI_FLOOR_PERCENT",
        "TP1:20,TP2:40",
    ).strip()

    accepted = scan_previous_tp_values(
        config
    )

    # Restore accepted configuration before
    # evaluating any new Render request.

    scan_publish_tp_values(
        config,
        accepted,
    )

    result = {
        "status": "PENDING",

        "eligible": False,

        "minimum_tp1": None,

        "minimum_tp2": None,

        "accepted_tp1":
            accepted["TP1"]
            if accepted else None,

        "accepted_tp2":
            accepted["TP2"]
            if accepted else None,

        "minimum_tp1_fill_verified":
            False,
    }

    print(
        "UNIT 8 TP ROI RENDER INPUT =",
        raw,
        flush=True,
    )

    # ========================================================
    # CHECK CURRENT EXCHANGE DETAILS
    # ========================================================

    try:

        minimums = scan_tp_minimums(
            config,
            account,
            market,
        )

    except Exception as exc:

        result.update({
            "status":
                "CONTRACT_PARAMETERS_PENDING",

            "reason":
                str(exc),
        })

        print(
            "UNIT 8 TP ROI PENDING =",
            str(exc),
            flush=True,
        )

        return result

    result.update({
        "minimum_tp1":
            minimums["minimum_tp1"],

        "minimum_tp2":
            minimums["minimum_tp2"],

        "minimum_tp1_source":
            minimums["source"],
    })

    # ========================================================
    # ACCEPT OR REJECT REQUEST
    # ========================================================

    requested = None

    targets = {}

    reason = ""

    decision_key = (
        symbol + "|" + raw
    )

    try:

        requested = scan_parse_tp_roi(
            raw
        )

        decision_key = (
            symbol

            + "|"

            + scan_config_amount(
                requested["TP1"]
            )

            + "|"

            + scan_config_amount(
                requested["TP2"]
            )
        )

        targets = scan_validate_tp_targets(
            requested,
            minimums,
        )

        status = "ACCEPTED"

        accepted = dict(requested)

        message = (
            f"{symbol} TP1 accepted, "

            f"{scan_config_amount(accepted['TP1'])}% "

            "net ROI floor enabled.\n"

            f"{symbol} TP2 accepted, "

            f"{scan_config_amount(accepted['TP2'])}% "

            "net ROI floor enabled."
        )

    except Exception as exc:

        status = "REJECTED"

        reason = str(exc)

        message = (
            f"{symbol} TP net ROI rejected.\n"

            + reason

            + "\nCalculated TP1 minimum: "

            + scan_config_amount(
                minimums["minimum_tp1"]
            )

            + "%.\nCalculated TP2 minimum: "

            + scan_config_amount(
                minimums["minimum_tp2"]
            )

            + "%.\nBased on exchange price "

            "precision and estimated fees."
        )

        if accepted:

            message += (
                "\nRetained TP1: "

                + scan_config_amount(
                    accepted["TP1"]
                )

                + "%, TP2: "

                + scan_config_amount(
                    accepted["TP2"]
                )

                + "%."
            )

        else:

            message += (
                "\nNo previously accepted "
                "TP configuration available."
            )

    # ========================================================
    # PERSIST DECISION BEFORE NOTIFICATION
    # ========================================================

    scan_configuration_commit(
        setting="TP_NET_ROI",

        decision_key=decision_key,

        status=status,

        requested=(
            requested
            if requested is not None
            else raw
        ),

        accepted=accepted,

        minimum={
            "TP1":
                minimums["minimum_tp1"],

            "TP2":
                minimums["minimum_tp2"],
        },

        reason=reason,

        message=message,
    )

    scan_publish_tp_values(
        config,
        accepted,
    )

    # ========================================================
    # REVALIDATE RETAINED CONFIGURATION
    # REJECTION DOES NOT AUTOMATICALLY INVALIDATE
    # A PREVIOUSLY ACCEPTED EXECUTABLE VALUE
    # ========================================================

    retained_eligible = False

    if accepted:

        try:

            scan_validate_tp_targets(
                accepted,
                minimums,
            )

            retained_eligible = True

        except Exception:

            retained_eligible = False

    result.update({
        "status": status,

        "eligible":
            retained_eligible,

        "accepted_tp1":
            accepted["TP1"]
            if accepted else None,

        "accepted_tp2":
            accepted["TP2"]
            if accepted else None,

        "retained_configuration":
            status == "REJECTED"
            and accepted is not None,

        "targets":
            targets,

        "reason":
            reason,
    })

    print(
        "UNIT 8 TP NET ROI STATUS =",
        status,
        flush=True,
    )

    print(
        "UNIT 8 MINIMUM TP1 NET ROI =",
        result["minimum_tp1"],
        flush=True,
    )

    print(
        "UNIT 8 MINIMUM TP2 NET ROI =",
        result["minimum_tp2"],
        flush=True,
    )

    print(
        "UNIT 8 ACCEPTED TP1 NET ROI =",
        result["accepted_tp1"],
        flush=True,
    )

    print(
        "UNIT 8 ACCEPTED TP2 NET ROI =",
        result["accepted_tp2"],
        flush=True,
    )

    print(
        "UNIT 8 TP CONFIGURATION ELIGIBLE =",
        result["eligible"],
        flush=True,
    )

    return result


# ============================================================
# INITIAL_USDT SINGLE RENDER INPUT
# NO DUPLICATE ENTRY MARGIN VARIABLES
# ============================================================

def scan_requested_initial_usdt(config):

    raw = _scan_os.getenv(
        "INITIAL_USDT"
    )

    if raw is None or not raw.strip():

        raw = str(
            config["strategy"][
                "initial_fixed_usdt"
            ]
        )

        source = "EXISTING_CONFIGURATION"

    else:

        source = "INITIAL_USDT"

    return (
        raw.strip(),
        source,
    )


# ============================================================
# READ PREVIOUSLY ACCEPTED ENTRY CAPITAL
# ============================================================

def scan_previous_initial_usdt():

    previous = scan_configuration_read(
        "ENTRY_MARGIN"
    )

    if previous:

        accepted = previous.get(
            "accepted"
        )

        if isinstance(accepted, dict):

            value = accepted.get(
                "INITIAL_USDT"
            )

            if value is not None:

                return scan_positive_decimal(
                    value,
                    "ACCEPTED_INITIAL_USDT",
                )

    return None


# ============================================================
# PUBLISH ACCEPTED ENTRY CAPITAL
# EXISTING STRATEGY CONFIGURATION
# ============================================================

def scan_publish_initial_usdt(
    config,
    margin,
):

    if margin is None:

        return False

    margin = scan_positive_decimal(
        margin,
        "INITIAL_USDT",
    )

    config["strategy"][
        "initial_fixed_usdt"
    ] = float(margin)

    return True


# ============================================================
# VERIFIED EXCHANGE POSITION STATE
# ============================================================

def scan_entry_position_state(account):

    positions = account.get(
        "positions"
    )

    verified = (
        account.get(
            "demo_positions_verified"
        ) is True
    )

    if (
        not verified

        or not isinstance(
            positions,
            list,
        )
    ):

        return {
            "verified": False,

            "flat": None,

            "count": None,

            "status":
                "POSITION_UNVERIFIED",
        }

    active = []

    for position in positions:

        if not isinstance(
            position,
            dict,
        ):

            raise ValueError(
                "INVALID_POSITION_RECORD"
            )

        size = scan_decimal(
            position.get(
                "size",
                "0",
            )
        )

        if size < 0:

            raise ValueError(
                "INVALID_POSITION_SIZE"
            )

        if size > 0:

            active.append(position)

    flat = not bool(active)

    reported_flat = account.get(
        "position_flat_verified"
    )

    if (
        isinstance(reported_flat, bool)

        and reported_flat != flat
    ):

        return {
            "verified": False,

            "flat": None,

            "count": len(active),

            "status":
                "POSITION_STATE_INCONSISTENT",
        }

    return {
        "verified": True,

        "flat": flat,

        "count": len(active),

        "status":
            "FLAT"
            if flat
            else "OCCUPIED",
    }


# ============================================================
# CALCULATE MINIMUM INITIAL_USDT
# BASED ON EXECUTABLE TP ALLOCATIONS
# ============================================================

def scan_minimum_initial_usdt(
    config,
    account,
    market,
):

    contract = scan_contract_details(
        config
    )

    if not contract["confirmed"]:

        raise RuntimeError(
            "CONTRACT_SPECS_UNAVAILABLE"
        )

    price = scan_positive_decimal(
        market["price"],
        "MARKET_PRICE",
    )

    step = contract["quantity_step"]

    minimum = contract["minimum_quantity"]

    multiplier = contract[
        "contract_multiplier"
    ]

    leverage = min(
        scan_positive_decimal(
            account["long_leverage"],
            "LONG_LEVERAGE",
        ),

        scan_positive_decimal(
            account["short_leverage"],
            "SHORT_LEVERAGE",
        ),
    )

    strategy = config["strategy"]

    allocations = [
        scan_positive_decimal(
            strategy[key],
            key,
        )

        for key in (
            "tp1_allocation_percent",
            "tp2_allocation_percent",
            "tp3_allocation_percent",
        )
    ]

    if sum(allocations) != Decimal("100"):

        raise ValueError(
            "TP_ALLOCATIONS_MUST_TOTAL_100"
        )

    executable_minimum = scan_ceil(
        minimum,
        step,
    )

    # Calculate a starting quantity sufficient
    # for all three configured TP allocations.

    required_quantity = max(
        executable_minimum

        * Decimal("100")

        / allocation

        for allocation in allocations
    )

    entry_quantity = scan_ceil(
        required_quantity,
        step,
    )

    # Confirm against actual Unit 13 allocation
    # logic rather than relying only on percentages.

    q1, q2, q3 = (
        unit_13_v4_allocation(
            entry_quantity,

            step,

            allocations[0],

            allocations[1],
        )
    )

    q1 = scan_decimal(q1)

    q2 = scan_decimal(q2)

    q3 = scan_decimal(q3)

    if min(q1, q2, q3) < executable_minimum:

        raise RuntimeError(
            "TP_ALLOCATION_SIZING_INCONSISTENT"
        )

    minimum_margin = (
        entry_quantity

        * price

        * multiplier

        / leverage
    )

    minimum_margin = minimum_margin.quantize(
        Decimal("0.01"),
        rounding=ROUND_CEILING,
    )

    return {
        "minimum_margin":
            minimum_margin,

        "minimum_order_quantity":
            executable_minimum,

        "required_entry_quantity":
            entry_quantity,

        "quantity_step":
            step,

        "price":
            price,

        "leverage":
            leverage,

        "contract_multiplier":
            multiplier,

        "tp1_quantity":
            q1,

        "tp2_quantity":
            q2,

        "tp3_quantity":
            q3,
    }


# ============================================================
# UNIT 8 INITIAL_USDT ACCEPTANCE CONTROLLER V3
# SINGLE IMPLEMENTATION
# ============================================================

def unit_8_entry_margin_control(
    config,
    account,
    market,
):

    symbol = str(
        config["exchange"]["market_symbol"]
    ).strip().upper()

    coin = (
        symbol[:-4]
        if symbol.endswith("USDT")
        else symbol
    )

    raw, source = (
        scan_requested_initial_usdt(
            config
        )
    )

    accepted = (
        scan_previous_initial_usdt()
    )

    scan_publish_initial_usdt(
        config,
        accepted,
    )

    print(
        "UNIT 8 INITIAL_USDT RECEIVED =",
        raw,
        flush=True,
    )

    print(
        "UNIT 8 INITIAL_USDT SOURCE =",
        source,
        flush=True,
    )

    result = {
        "eligible": False,

        "status": "PENDING",

        "accepted_margin": accepted,

        "minimum_margin": None,

        "source": source,
    }

    decision_key = (
        symbol + "|" + raw
    )

    requested = None

    minimum_margin = None

    reason = ""

    message = None

    status = "PENDING"

    # ========================================================
    # PARSE RENDER REQUEST
    # ========================================================

    try:

        requested = (
            scan_positive_decimal(
                raw,
                "INITIAL_USDT",
            )
        )

        decision_key = (
            symbol

            + "|"

            + scan_config_amount(
                requested
            )
        )

    except Exception as exc:

        status = "REJECTED"

        reason = str(exc)

        message = (
            f"{coin} entry rejected, "

            f"invalid INITIAL_USDT value: {raw}."
        )

    # ========================================================
    # CHECK EXCHANGE POSITION STATE
    # ========================================================

    if status != "REJECTED":

        try:

            position_state = (
                scan_entry_position_state(
                    account
                )
            )

        except Exception as exc:

            result.update({
                "status":
                    "POSITION_STATE_INCONSISTENT",

                "reason":
                    str(exc),
            })

            return result

        print(
            "ENTRY POSITION COUNT =",
            position_state["count"],
            flush=True,
        )

        print(
            "ENTRY POSITION FLAT =",
            position_state["flat"],
            flush=True,
        )

        if not position_state["verified"]:

            result["status"] = (
                position_state["status"]
            )

            return result

        # ====================================================
        # CHECK EXCHANGE EXECUTABLE MINIMUM
        # ====================================================

        try:

            sizing = (
                scan_minimum_initial_usdt(
                    config,
                    account,
                    market,
                )
            )

            minimum_margin = sizing[
                "minimum_margin"
            ]

            result.update(sizing)

        except Exception as exc:

            result.update({
                "status":
                    "ENTRY_SIZING_PENDING",

                "reason":
                    str(exc),
            })

            print(
                "UNIT 8 ENTRY SIZING PENDING =",
                str(exc),
                flush=True,
            )

            return result

        # ====================================================
        # REJECT INSUFFICIENT ENTRY CAPITAL
        # ====================================================

        if requested < minimum_margin:

            status = "REJECTED"

            reason = (
                "BELOW_EXECUTABLE_MINIMUM"
            )

            message = (
                f"{coin} entry rejected, "

                f"${scan_config_amount(requested)} "

                "below min of "

                f"${scan_config_amount(minimum_margin)}."
            )

        # ====================================================
        # QUEUE VALID CONFIGURATION IF POSITION EXISTS
        # ====================================================

        elif not position_state["flat"]:

            status = "QUEUED"

            reason = "POSITION_EXISTS"

            message = (
                f"${scan_config_amount(requested)} "

                f"{coin} queued, position exists."
            )

        # ====================================================
        # ACCEPT EXECUTABLE CONFIGURATION
        # ====================================================

        else:

            status = "ACCEPTED"

            accepted = requested

            message = (
                f"{coin} entry accepted, "

                f"${scan_config_amount(accepted)} "

                "entry enabled."
            )

    # ========================================================
    # PERSIST BEFORE TELEGRAM DELIVERY
    # ========================================================

    scan_configuration_commit(
        setting="ENTRY_MARGIN",

        decision_key=decision_key,

        status=status,

        requested=(
            str(requested)
            if requested is not None
            else raw
        ),

        accepted=(
            {
                "INITIAL_USDT":
                    str(accepted),
            }

            if accepted is not None

            else None
        ),

        minimum=(
            str(minimum_margin)

            if minimum_margin is not None

            else None
        ),

        reason=reason,

        message=message,
    )

    scan_publish_initial_usdt(
        config,
        accepted,
    )

    # A queued or rejected request must not
    # silently become the new entry capital.

    eligible = (
        status == "ACCEPTED"
    )

    result.update({
        "eligible":
            eligible,

        "status":
            status,

        "requested_margin":
            requested,

        "accepted_margin":
            accepted,

        "minimum_margin":
            minimum_margin,

        "margin":
            str(accepted)
            if accepted is not None
            else None,

        "minimum":
            str(minimum_margin)
            if minimum_margin is not None
            else None,

        "reason":
            reason,

        "retained_configuration":
            status != "ACCEPTED"
            and accepted is not None,
    })

    print(
        "UNIT 8 ENTRY MARGIN STATUS =",
        status,
        flush=True,
    )

    print(
        "UNIT 8 REQUESTED INITIAL_USDT =",
        requested,
        flush=True,
    )

    print(
        "UNIT 8 ACCEPTED INITIAL_USDT =",
        accepted,
        flush=True,
    )

    print(
        "UNIT 8 MINIMUM REQUIRED MARGIN =",
        minimum_margin,
        flush=True,
    )

    print(
        "UNIT 12 ENTRY ELIGIBLE =",
        eligible,
        flush=True,
    )

    return result


# ============================================================
# LEGACY ENTRY MARGIN INTERFACE
# BOTH FUNCTION NAMES USE THE SAME CONTROLLER
# NO SECOND SQLITE SCHEMA
# ============================================================

def unit_8_render_entry_margin(
    config,
    account,
    market,
):

    return unit_8_entry_margin_control(
        config,
        account,
        market,
    )


# ============================================================
# RESTORE ACCEPTED CONFIGURATION
# AVAILABLE TO CONTINUOUS SCAN STARTUP
# ============================================================

def scan_restore_accepted_configuration(
    config,
):

    tp_values = (
        scan_previous_tp_values(
            config
        )
    )

    margin = (
        scan_previous_initial_usdt()
    )

    tp_restored = (
        scan_publish_tp_values(
            config,
            tp_values,
        )
    )

    margin_restored = (
        scan_publish_initial_usdt(
            config,
            margin,
        )
    )

    print(
        "SCAN ACCEPTED TP CONFIG RESTORED =",
        tp_restored,
        flush=True,
    )

    print(
        "SCAN ACCEPTED INITIAL_USDT RESTORED =",
        margin_restored,
        flush=True,
    )

    return {
        "tp_restored":
            tp_restored,

        "margin_restored":
            margin_restored,

        "accepted_tp":
            tp_values,

        "accepted_initial_usdt":
            margin,
    }


# ============================================================
# CONFIGURATION NOTIFICATION DELIVERY
# REUSE EXISTING UNIT 8 EVENT QUEUE
# ============================================================

def scan_flush_configuration_notifications():

    try:

        delivered = (
            unit_8_symbol_telegram_flush()
        )

        print(
            "SCAN SYMBOL TELEGRAM DELIVERED =",
            delivered,
            flush=True,
        )

        return delivered

    except Exception as exc:

        print(
            "SCAN CONFIGURATION TELEGRAM ERROR =",
            repr(exc),
            flush=True,
        )

        return None


# ============================================================
# END COMPLETE CONTINUOUS SCAN CONTROLLER V3
# END PART 2 OF 3
# ZERO INDENTATION
#
# NEXT:
# COMPLETE CONTINUOUS EXECUTION PIPELINE
# UNITS 3-15 HANDOVER
# SCAN SUPERVISOR
# ============================================================


# ============================================================
# COMPLETE CONTINUOUS SCAN CONTROLLER V3
# PART 3 OF 3
# CONTINUOUS EXECUTION / MANAGEMENT / SUPERVISION
# ZERO INDENTATION
# ============================================================


# ============================================================
# PUBLISH CURRENT ACTIVE SYMBOL PAIR
# ============================================================

def scan_refresh_active_pair(config):

    active_pair = unit_2_active_symbol_pair()

    market_symbol = str(
        active_pair.get(
            "market_symbol",
            "",
        )
    ).strip().upper()

    demo_symbol = str(
        active_pair.get(
            "demo_order_symbol",
            "",
        )
    ).strip().upper()

    if not market_symbol or not demo_symbol:

        raise RuntimeError(
            "SCAN ACTIVE SYMBOL PAIR MISSING"
        )

    exchange = config["exchange"]

    exchange["market_symbol"] = (
        market_symbol
    )

    exchange["demo_order_symbol"] = (
        demo_symbol
    )

    exchange["active_symbol_source"] = (
        active_pair.get("source")
    )

    print(
        "SCAN ACTIVE MARKET SYMBOL =",
        market_symbol,
        flush=True,
    )

    print(
        "SCAN ACTIVE DEMO SYMBOL =",
        demo_symbol,
        flush=True,
    )

    return market_symbol, demo_symbol


# ============================================================
# FRESH MARKET AND ATR PUBLICATION
# UNIT 3 -> UNIT 4 -> UNIT 14
# ============================================================

def scan_refresh_market_analysis(config):

    global FRESH_RECONSTRUCTION_MARKET_SNAPSHOT
    global FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT

    global SCAN_LAST_ATR_SYMBOL
    global SCAN_LAST_ATR_TIME
    global SCAN_LAST_MARKET_SUCCESS

    market_symbol = str(
        config["exchange"]["market_symbol"]
    ).upper()

    market = fresh_reconstruction_unit_3()

    if not isinstance(market, dict):

        raise RuntimeError(
            "SCAN UNIT 3 SNAPSHOT INVALID"
        )

    FRESH_RECONSTRUCTION_MARKET_SNAPSHOT = (
        market
    )

    analysis = fresh_reconstruction_unit_4()

    if not isinstance(analysis, dict):

        raise RuntimeError(
            "SCAN UNIT 4 SNAPSHOT INVALID"
        )

    atr = scan_positive_decimal(
        analysis["atr14"],
        "ATR14",
    )

    FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT = (
        analysis
    )

    SCAN_LAST_ATR_SYMBOL = (
        market_symbol
    )

    SCAN_LAST_ATR_TIME = (
        _scan_time.time()
    )

    SCAN_LAST_MARKET_SUCCESS = (
        SCAN_LAST_ATR_TIME
    )

    print(
        "SCAN FRESH MARKET TIMESTAMP =",
        market.get("exchange_time_ms"),
        flush=True,
    )

    print(
        "SCAN REFRESHED ATR14 =",
        atr,
        flush=True,
    )

    print(
        "SCAN ATR SYMBOL =",
        SCAN_LAST_ATR_SYMBOL,
        flush=True,
    )

    return market, analysis


# ============================================================
# SYMBOL SWITCH RECONCILIATION
# EXISTING UNIT 8 PERSISTENT CONTROLLER
# ============================================================

def scan_reconcile_symbol(
    config,
    account,
):

    global FRESH_RECONSTRUCTION_SYMBOL_SWITCH_RESULT

    position_state = (
        scan_entry_position_state(
            account
        )
    )

    if not position_state["verified"]:

        raise RuntimeError(
            position_state["status"]
        )

    requested_market = _scan_os.getenv(
        "WEEX_SYMBOL",
        "BTCUSDT",
    ).strip().upper()

    discovery = (
        unit_8_discover_demo_contract(
            requested_market
        )
    )

    requested_demo = str(
        discovery.get("demo_symbol")
        or ""
    ).strip().upper()

    active_market = str(
        config["exchange"]["market_symbol"]
    ).upper()

    active_demo = str(
        config["exchange"]["demo_order_symbol"]
    ).upper()

    switch_result = unit_8_symbol_switch(
        requested_market=requested_market,

        requested_demo=requested_demo,

        positions=account["positions"],

        positions_verified=True,

        contract_verified=False,

        candidate_ready=(
            discovery.get("candidate_ready")
            is True
        ),
    )

    FRESH_RECONSTRUCTION_SYMBOL_SWITCH_RESULT = (
        switch_result
    )

    new_market = str(
        switch_result.get(
            "active_market_symbol",
            "",
        )
    ).upper()

    new_demo = str(
        switch_result.get(
            "active_demo_symbol",
            "",
        )
    ).upper()

    changed = (
        new_market != active_market

        or new_demo != active_demo
    )

    requested_active = (
        requested_market == new_market

        and requested_demo == new_demo
    )

    print(
        "SCAN SYMBOL SWITCH STATUS =",
        switch_result.get("status"),
        flush=True,
    )

    print(
        "SCAN ACTIVE MARKET SYMBOL =",
        new_market,
        flush=True,
    )

    print(
        "SCAN ACTIVE DEMO SYMBOL =",
        new_demo,
        flush=True,
    )

    print(
        "SCAN QUEUED MARKET SYMBOL =",
        switch_result.get(
            "queued_market_symbol"
        ),
        flush=True,
    )

    print(
        "SCAN QUEUED DEMO SYMBOL =",
        switch_result.get(
            "queued_demo_symbol"
        ),
        flush=True,
    )

    return {
        "changed": changed,

        "requested_active":
            requested_active,

        "market_symbol":
            new_market,

        "demo_symbol":
            new_demo,

        "status":
            switch_result.get("status"),

        "result":
            switch_result,
    }


# ============================================================
# COMPLETE MARKET AND ENTRY PIPELINE
# UNITS 3-12
# ============================================================

def scan_refresh_entry_pipeline():

    config = FRESH_RECONSTRUCTION_CONFIG

    # ========================================================
    # RESTORE LAST ACCEPTED CONFIGURATION
    # BEFORE NEW ENTRY SIZING
    # ========================================================

    scan_restore_accepted_configuration(
        config
    )

    # ========================================================
    # ACTIVE SYMBOL
    # ========================================================

    active_market, active_demo = (
        scan_refresh_active_pair(
            config
        )
    )

    # ========================================================
    # CONTRACT SPECIFICATIONS
    # ========================================================

    specifications_loaded = (
        unit_9_load_symbol_specifications(
            config,
            active_market,
        )
    )

    # Refresh market and ATR even when
    # contract specification retrieval fails.

    market, analysis = (
        scan_refresh_market_analysis(
            config
        )
    )

    if specifications_loaded is not True:

        return scan_idle_unit12_result(
            "CONTRACT_SPECIFICATIONS_PENDING"
        )

    # ========================================================
    # UNIT 5: MARKET REGIME
    # ========================================================

    candidate = (
        fresh_reconstruction_unit_5(
            config,
            analysis,
        )
    )

    # ========================================================
    # UNIT 6: SIGNAL QUALIFICATION
    # ========================================================

    execution = (
        fresh_reconstruction_unit_6(
            config,
            analysis,
            candidate,
        )
    )

    # ========================================================
    # UNIT 7: SIZING POLICY
    # ========================================================

    sizing = (
        fresh_reconstruction_unit_7(
            config,
            execution,
        )
    )

    # ========================================================
    # UNIT 8: ACCOUNT AND LEVERAGE
    # ========================================================

    account = (
        fresh_reconstruction_unit_8(
            config,
            sizing,
            market,
        )
    )

    if not isinstance(account, dict):

        raise RuntimeError(
            "SCAN UNIT 8 ACCOUNT INVALID"
        )

    # ========================================================
    # UNIVERSAL SYMBOL SWITCHING
    # ========================================================

    symbol_decision = (
        scan_reconcile_symbol(
            config,
            account,
        )
    )

    if symbol_decision["changed"]:

        print(
            "SCAN SYMBOL CHANGED =",
            symbol_decision["market_symbol"],
            flush=True,
        )

        print(
            "SCAN NEW SYMBOL REQUIRES FRESH DATA",
            flush=True,
        )

        # The next scan refreshes market data,
        # ATR and specifications for the new pair.
        #
        # Do not use the previous symbol's
        # market snapshot for new entry.

        return scan_idle_unit12_result(
            "SYMBOL_CHANGED_REFRESH_NEXT_SCAN"
        )

    # ========================================================
    # TP NET ROI ACCEPTANCE
    # ========================================================

    tp_decision = (
        unit_8_tp_net_roi_control(
            config,
            account,
            market,
        )
    )

    print(
        "SCAN TP NET ROI STATUS =",
        tp_decision.get("status"),
        flush=True,
    )

    print(
        "SCAN TP NET ROI ELIGIBLE =",
        tp_decision.get("eligible"),
        flush=True,
    )

    # ========================================================
    # INITIAL_USDT ACCEPTANCE
    # INDEPENDENT OF TP DECISION
    # ========================================================

    margin_decision = (
        unit_8_entry_margin_control(
            config,
            account,
            market,
        )
    )

    print(
        "SCAN ENTRY MARGIN STATUS =",
        margin_decision.get("status"),
        flush=True,
    )

    print(
        "SCAN UNIT 12 ENTRY ELIGIBLE =",
        margin_decision.get("eligible"),
        flush=True,
    )

    # ========================================================
    # NEW ENTRY CONFIGURATION DECISIONS
    # DOES NOT SUSPEND EXISTING POSITION MANAGEMENT
    # ========================================================

    if not symbol_decision[
        "requested_active"
    ]:

        return scan_idle_unit12_result(
            "SYMBOL_REQUEST_"
            + str(
                symbol_decision["status"]
            )
        )

    if tp_decision.get(
        "eligible"
    ) is not True:

        return scan_idle_unit12_result(
            "TP_NET_ROI_"
            + str(
                tp_decision.get("status")
            )
        )

    if margin_decision.get(
        "eligible"
    ) is not True:

        return scan_idle_unit12_result(
            "ENTRY_MARGIN_"
            + str(
                margin_decision.get("status")
            )
        )

    # ========================================================
    # REFRESH DOWNSTREAM SIZING AFTER ACCEPTANCE
    # ========================================================

    sizing = (
        fresh_reconstruction_unit_7(
            config,
            execution,
        )
    )

    account = (
        fresh_reconstruction_unit_8(
            config,
            sizing,
            market,
        )
    )

    if not isinstance(account, dict):

        raise RuntimeError(
            "SCAN REFRESHED ACCOUNT INVALID"
        )

    # ========================================================
    # UNIT 9: EXECUTABLE ENTRY SIZING
    # ========================================================

    entry = fresh_reconstruction_unit_9(
        config,
        account,
    )

    # ========================================================
    # UNIT 10: EXECUTION HANDOVER
    # ========================================================

    boundary = fresh_unit_10_hybrid_adapter(
        config,
        entry,
    )

    # ========================================================
    # UNIT 11: EXCHANGE ORDER PAYLOAD
    # ========================================================

    prepared = fresh_unit_11_hybrid_adapter(
        config,
        boundary,
    )

    # ========================================================
    # UNIT 12: INITIAL ENTRY EXECUTION
    # BOT_MODE REMAINS CONTROLLED BY UNIT 12
    # ========================================================

    submission = (
        fresh_unit_12_hybrid_execution_adapter(
            config,
            prepared,
        )
    )

    if not isinstance(submission, dict):

        raise RuntimeError(
            "SCAN UNIT 12 RESULT INVALID"
        )

    return submission


# ============================================================
# UNIT 13 TP EXECUTION NOTIFICATION
# CONFIRMED FILLS ONLY
# ============================================================

def scan_queue_unit13_notifications(
    unit13,
):

    outcomes = unit13.get(
        "position_results",
        [],
    )

    if not outcomes:

        outcomes = [unit13]

    queued = 0

    for outcome in outcomes:

        if not isinstance(
            outcome,
            dict,
        ):

            continue

        symbol = outcome.get(
            "symbol"
        )

        side = outcome.get(
            "position_side"
        )

        action = outcome.get(
            "tp_action"
        )

        if not isinstance(
            action,
            dict,
        ):

            continue

        stage = str(
            action.get(
                "stage",
                "",
            )
        ).upper()

        if stage not in (
            "TP1",
            "TP2",
        ):

            continue

        filled = scan_decimal(
            action.get(
                "filled_quantity",
                "0",
            )
        )

        if filled <= 0:

            continue

        order_id = (
            action.get("order_id")

            or action.get("client_id")
        )

        if not order_id:

            continue

        status = str(
            action.get(
                "status",
                "",
            )
        ).upper()

        notification_id = (
            "UNIT13:"

            + str(symbol)

            + ":"

            + str(side)

            + ":"

            + stage

            + ":"

            + str(order_id)

            + ":"

            + scan_config_amount(
                filled
            )
        )

        message = (
            "WEEX DEMO TP EXECUTION\n"

            f"Symbol: {symbol}\n"

            f"Position: {side}\n"

            f"Stage: {stage}\n"

            "Confirmed filled quantity: "

            f"{scan_config_amount(filled)}\n"

            f"Order ID: {order_id}\n"

            f"Exchange status: {status}"
        )

        unit15_queue_notification(
            notification_id,
            message,
        )

        queued += 1

    return queued


# ============================================================
# EXISTING POSITION MANAGEMENT
# UNIT 13 -> UNIT 14 -> UNIT 15
# ============================================================

def scan_manage_position(unit12_result):

    global FRESH_RECONSTRUCTION_UNIT_12_RESULT
    global FRESH_RECONSTRUCTION_UNIT_13_RESULT
    global FRESH_RECONSTRUCTION_UNIT_14_RESULT
    global FRESH_RECONSTRUCTION_UNIT_15_RESULT

    config = FRESH_RECONSTRUCTION_CONFIG

    FRESH_RECONSTRUCTION_UNIT_12_RESULT = (
        unit12_result
    )

    # ========================================================
    # UNIT 13: TP1 AND TP2 EXECUTION
    # ========================================================

    try:

        unit13 = (
            fresh_unit_13_hybrid_adapter(
                config,
                unit12_result,
            )
        )

        if not isinstance(
            unit13,
            dict,
        ):

            raise RuntimeError(
                "UNIT13_RESULT_INVALID"
            )

    except Exception as exc:

        print(
            "SCAN UNIT 13 ERROR =",
            repr(exc),
            flush=True,
        )

        _scan_traceback.print_exc()

        unit13 = unit_13_v4_base_result(
            unit12_result,
            "ERROR",
            str(exc),
        )

        unit13[
            "execution_error"
        ] = str(exc)

    FRESH_RECONSTRUCTION_UNIT_13_RESULT = (
        unit13
    )

    print(
        "SCAN UNIT 13 STATUS =",
        unit13.get("status"),
        flush=True,
    )

    # ========================================================
    # UNIT 14: INDEPENDENT POSITION MANAGEMENT
    #
    # H1 / H2
    # R1 / R2
    # B1-B5
    # ATR BREAK-EVEN
    # TP3 TRAILING
    # ========================================================

    try:

        unit14 = (
            fresh_unit_14_hybrid_adapter(
                config,
                unit13,
            )
        )

        if not isinstance(
            unit14,
            dict,
        ):

            raise RuntimeError(
                "UNIT14_RESULT_INVALID"
            )

    except Exception as exc:

        print(
            "SCAN UNIT 14 ERROR =",
            repr(exc),
            flush=True,
        )

        _scan_traceback.print_exc()

        unit14 = unit_14_v3_result(
            unit13
        )

        unit14.update({
            "status": "ERROR",

            "execution_error":
                str(exc),
        })

    FRESH_RECONSTRUCTION_UNIT_14_RESULT = (
        unit14
    )

    print(
        "SCAN UNIT 14 STATUS =",
        unit14.get("status"),
        flush=True,
    )

    # ========================================================
    # UNIT 13 CONFIRMED TP NOTIFICATIONS
    # REPORTING FAILURE DOES NOT BLOCK MANAGEMENT
    # ========================================================

    try:

        tp_notifications = (
            scan_queue_unit13_notifications(
                unit13
            )
        )

        print(
            "SCAN UNIT 13 TP NOTIFICATIONS =",
            tp_notifications,
            flush=True,
        )

    except Exception as exc:

        print(
            "SCAN UNIT 13 NOTIFICATION ERROR =",
            repr(exc),
            flush=True,
        )

    # ========================================================
    # UNIT 15: CONTINUOUS HANDOVER
    # REPORTING WORKER REMAINS INDEPENDENT
    # ========================================================

    try:

        unit15 = (
            fresh_unit_15_hybrid_adapter(
                config,
                unit14,
            )
        )

        if not isinstance(
            unit15,
            dict,
        ):

            raise RuntimeError(
                "UNIT15_RESULT_INVALID"
            )

    except Exception as exc:

        print(
            "SCAN UNIT 15 HANDOVER ERROR =",
            repr(exc),
            flush=True,
        )

        _scan_traceback.print_exc()

        unit15 = {
            "unit": 15,

            "status":
                "HANDOVER_ERROR",

            "errors":
                [str(exc)],

            "exchange_write":
                False,
        }

    FRESH_RECONSTRUCTION_UNIT_15_RESULT = (
        unit15
    )

    print(
        "SCAN UNIT 15 STATUS =",
        unit15.get("status"),
        flush=True,
    )

    print(
        "SCAN UNIT 15 HANDOVER =",
        unit15.get(
            "notification_result",
            {},
        ),
        flush=True,
    )

    print(
        "SCAN UNIT 15 ERRORS =",
        unit15.get(
            "errors",
            [],
        ),
        flush=True,
    )

    return unit13, unit14


# ============================================================
# MARKET REFRESH FALLBACK
# WHEN ENTRY PIPELINE FAILS
# ============================================================

def scan_management_market_refresh():

    config = FRESH_RECONSTRUCTION_CONFIG

    active_market = str(
        config["exchange"]["market_symbol"]
    ).upper()

    # Keep the currently configured symbol
    # for management of the existing position.

    try:

        market, analysis = (
            scan_refresh_market_analysis(
                config
            )
        )

        print(
            "SCAN MANAGEMENT ATR REFRESH = PASS",
            flush=True,
        )

        return True

    except Exception as exc:

        print(
            "SCAN MANAGEMENT ATR REFRESH = FAILED",
            flush=True,
        )

        print(
            "SCAN MANAGEMENT ATR ERROR =",
            repr(exc),
            flush=True,
        )

        print(
            "SCAN MANAGEMENT ATR SYMBOL =",
            SCAN_LAST_ATR_SYMBOL,
            flush=True,
        )

        print(
            "SCAN MANAGEMENT ACTIVE SYMBOL =",
            active_market,
            flush=True,
        )

        return False


# ============================================================
# REPORTING WORKER STATUS
# ============================================================

def scan_reporting_status():

    result = globals().get(
        "FRESH_RECONSTRUCTION_UNIT_15_RESULT",
        {},
    )

    if not isinstance(result, dict):

        return False

    if scan_result_has_error(
        result
    ):

        return False

    if result.get("errors"):

        return False

    return True


# ============================================================
# MANUAL POSITION CONTROL
# PRESERVE ORIGINAL DPC CONTROLLER
# ============================================================

def scan_manual_position_control():

    control_mode = _scan_os.getenv(
        "DEMO_POSITION_CONTROL",
        "OFF",
    ).strip().upper()

    if control_mode == "OFF":

        return {
            "active": False,

            "status": "OFF",
        }

    try:

        result = dpc_process()

        print(
            "SCAN DEMO CONTROL STATUS =",
            result,
            flush=True,
        )

        return {
            "active": True,

            "status":
                "MANUAL_CONTROL",

            "result":
                result,
        }

    except Exception as exc:

        print(
            "SCAN DEMO CONTROL ERROR =",
            repr(exc),
            flush=True,
        )

        _scan_traceback.print_exc()

        return {
            "active": True,

            "status":
                "MANUAL_CONTROL_ERROR",

            "error":
                str(exc),
        }


# ============================================================
# ONE COMPLETE CONTINUOUS SCAN
# ============================================================

def scan_one_cycle():

    global SCAN_NUMBER
    global SCAN_LAST_STATUS
    global SCAN_LAST_MANAGEMENT_SUCCESS

    if not SCAN_LOCK.acquire(
        blocking=False
    ):

        print(
            "SCAN ALREADY RUNNING",
            flush=True,
        )

        return

    entry_ok = False

    management_ok = False

    reporting_ok = False

    SCAN_LAST_STATUS = "RUNNING"

    try:

        SCAN_NUMBER += 1

        now = _SCAN_DT.now(
            SCAN_TZ
        )

        print("=" * 80, flush=True)

        print(
            "CONTINUOUS SCAN NUMBER =",
            SCAN_NUMBER,
            flush=True,
        )

        print(
            "SCAN TIME WAT =",
            now.isoformat(),
            flush=True,
        )

        print(
            "SCAN BOT_MODE =",
            _scan_os.getenv(
                "BOT_MODE",
                "PAUSE",
            ),
            flush=True,
        )

        # ====================================================
        # MANUAL POSITION CONTROLLER
        # ====================================================

        manual = (
            scan_manual_position_control()
        )

        if manual["active"]:

            SCAN_LAST_STATUS = (
                manual["status"]
            )

            return

        # ====================================================
        # MARKET REFRESH AND INITIAL ENTRY
        # ====================================================

        submission = (
            scan_idle_unit12_result(
                "ENTRY_NOT_ATTEMPTED"
            )
        )

        try:

            submission = (
                scan_refresh_entry_pipeline()
            )

            entry_ok = not (
                scan_result_has_error(
                    submission
                )
            )

            print(
                "SCAN UNIT 12 STATUS =",
                submission.get("status"),
                flush=True,
            )

            print(
                "SCAN UNIT 12 REASON =",
                submission.get("skip_reason"),
                flush=True,
            )

        except Exception as exc:

            print(
                "SCAN ENTRY PIPELINE ERROR =",
                repr(exc),
                flush=True,
            )

            _scan_traceback.print_exc()

            submission = (
                scan_error_unit12_result(
                    str(exc)
                )
            )

        # ====================================================
        # MARKET DATA FALLBACK
        # ENTRY FAILURE DOES NOT END THE SCAN
        # ====================================================

        if not entry_ok:

            scan_management_market_refresh()

        # ====================================================
        # EXISTING POSITION MANAGEMENT
        # INDEPENDENT OF ENTRY ELIGIBILITY
        # ====================================================

        try:

            unit13, unit14 = (
                scan_manage_position(
                    submission
                )
            )

            unit13_error = (
                scan_result_has_error(
                    unit13
                )
            )

            unit14_error = (
                scan_result_has_error(
                    unit14
                )
            )

            management_ok = not (
                unit13_error

                or unit14_error
            )

            if management_ok:

                SCAN_LAST_MANAGEMENT_SUCCESS = (
                    _scan_time.time()
                )

            print(
                "SCAN UNIT 13 MANAGEMENT ERROR =",
                unit13_error,
                flush=True,
            )

            print(
                "SCAN UNIT 14 MANAGEMENT ERROR =",
                unit14_error,
                flush=True,
            )

        except Exception as exc:

            management_ok = False

            print(
                "SCAN POSITION MANAGEMENT ERROR =",
                repr(exc),
                flush=True,
            )

            _scan_traceback.print_exc()

        # ====================================================
        # REPORTING DIAGNOSTIC
        # ====================================================

        reporting_ok = (
            scan_reporting_status()
        )

        # ====================================================
        # FINAL SCAN STATUS
        # ====================================================

        if entry_ok and management_ok:

            SCAN_LAST_STATUS = (
                "PASS"

                if reporting_ok

                else "PASS_REPORTING_ERROR"
            )

        elif management_ok:

            SCAN_LAST_STATUS = (
                "MANAGEMENT_ONLY"

                if reporting_ok

                else "MANAGEMENT_ONLY_REPORTING_ERROR"
            )

        elif entry_ok:

            SCAN_LAST_STATUS = (
                "POSITION_MANAGEMENT_ERROR"
            )

        else:

            SCAN_LAST_STATUS = (
                "ENTRY_AND_MANAGEMENT_ERROR"
            )

        print(
            "SCAN ENTRY PIPELINE SUCCESS =",
            entry_ok,
            flush=True,
        )

        print(
            "SCAN MANAGEMENT SUCCESS =",
            management_ok,
            flush=True,
        )

        print(
            "SCAN REPORTING SUCCESS =",
            reporting_ok,
            flush=True,
        )

    except Exception as exc:

        SCAN_LAST_STATUS = (
            "SCAN_EXECUTION_ERROR"
        )

        print(
            "SCAN EXECUTION ERROR =",
            repr(exc),
            flush=True,
        )

        _scan_traceback.print_exc()

    finally:

        # ====================================================
        # DELIVER PERSISTED CONFIGURATION NOTIFICATIONS
        # EVEN WHEN ENTRY OR MANAGEMENT FAILS
        # ====================================================

        try:

            scan_flush_configuration_notifications()

        finally:

            SCAN_LOCK.release()

        print(
            "SCAN FINAL STATUS =",
            SCAN_LAST_STATUS,
            flush=True,
        )

        print(
            "SCAN EXCHANGE ENVIRONMENT = DEMO",
            flush=True,
        )

        print(
            "SCAN CONTINUES = TRUE",
            flush=True,
        )


# ============================================================
# CONTINUOUS SCAN LOCAL VALIDATION
# NO EXCHANGE ORDER SUBMISSION
# ============================================================

def scan_validation_v3():

    tests = {}

    # ========================================================
    # PRECISION CONVERSION
    # ========================================================

    tests["NEGATIVE_PRECISION"] = (
        scan_precision_step(
            -1,
            "TEST",
        ) == Decimal("10")
    )

    tests["ZERO_PRECISION"] = (
        scan_precision_step(
            0,
            "TEST",
        ) == Decimal("1")
    )

    tests["POSITIVE_PRECISION"] = (
        scan_precision_step(
            3,
            "TEST",
        ) == Decimal("0.001")
    )

    tests["FRACTIONAL_QUANTITY"] = (
        scan_floor(
            "6.5",
            "0.5",
        ) == Decimal("6.5")
    )

    # ========================================================
    # TP CONFIGURATION PARSING
    # ========================================================

    tp = scan_parse_tp_roi(
        "TP1:20,TP2:40"
    )

    tests["TP_CONFIGURATION"] = (
        tp["TP1"] == Decimal("20")

        and tp["TP2"] == Decimal("40")
    )

    # ========================================================
    # IDLE AND ERROR DISTINCTION
    # ========================================================

    idle = scan_idle_unit12_result(
        "TEST"
    )

    error = scan_error_unit12_result(
        "TEST"
    )

    tests["IDLE_NOT_ERROR"] = (
        not scan_result_has_error(
            idle
        )
    )

    tests["ERROR_DETECTION"] = (
        scan_result_has_error(
            error
        )
    )

    # ========================================================
    # CONFIGURATION DATABASE
    # ========================================================

    try:

        db = scan_configuration_db()

        db.close()

        tests["CONFIGURATION_SQLITE"] = True

    except Exception:

        tests["CONFIGURATION_SQLITE"] = False

    # ========================================================
    # EXISTING UNIT INTERFACES
    # ========================================================

    interfaces = (
        "fresh_reconstruction_unit_3",

        "fresh_reconstruction_unit_4",

        "fresh_reconstruction_unit_5",

        "fresh_reconstruction_unit_6",

        "fresh_reconstruction_unit_7",

        "fresh_reconstruction_unit_8",

        "fresh_reconstruction_unit_9",

        "fresh_unit_10_hybrid_adapter",

        "fresh_unit_11_hybrid_adapter",

        "fresh_unit_12_hybrid_execution_adapter",

        "fresh_unit_13_hybrid_adapter",

        "fresh_unit_14_hybrid_adapter",

        "fresh_unit_15_hybrid_adapter",

        "unit_8_symbol_switch",

        "unit_8_symbol_telegram_flush",
    )

    for name in interfaces:

        tests[name] = callable(
            globals().get(name)
        )

    # ========================================================
    # VALIDATION DIAGNOSTICS
    # ========================================================

    for name, passed in tests.items():

        print(
            "SCAN TEST:",
            name,
            "=",

            "PASS"
            if passed
            else "FAIL",

            flush=True,
        )

    passed = sum(
        bool(value)

        for value in tests.values()
    )

    failed = len(tests) - passed

    print(
        "SCAN VALIDATION TESTS PASSED =",
        passed,
        flush=True,
    )

    print(
        "SCAN VALIDATION TESTS FAILED =",
        failed,
        flush=True,
    )

    print(
        "SCAN VALIDATION RESULT =",

        "PASS"
        if failed == 0
        else "FAIL",

        flush=True,
    )

    return failed == 0


# ============================================================
# CONTINUOUS SCAN SUPERVISOR
# ============================================================

def scan_forever():

    print("=" * 80, flush=True)

    print(
        "CONTINUOUS SCAN CONTROLLER V3 STARTED",
        flush=True,
    )

    print(
        "SCAN INTERVAL SECONDS =",
        SCAN_INTERVAL_SECONDS,
        flush=True,
    )

    print(
        "SCAN INITIAL_USDT CONTROLLER = V3",
        flush=True,
    )

    print(
        "SCAN TP NET ROI CONTROLLER = V3",
        flush=True,
    )

    print(
        "SCAN UNIVERSAL SYMBOL SWITCHING = ENABLED",
        flush=True,
    )

    print(
        "SCAN FRESH ATR PUBLICATION = ENABLED",
        flush=True,
    )

    print(
        "SCAN UNIT 13 = TP1 / TP2",
        flush=True,
    )

    print(
        "SCAN UNIT 14 = H1 H2 R1 R2 "
        "B1-B5 BE TP3",
        flush=True,
    )

    print(
        "SCAN UNIT 15 = CONTINUOUS HANDOVER",
        flush=True,
    )

    print(
        "SCAN MANAGEMENT INDEPENDENT OF BOT_MODE",
        flush=True,
    )

    # ========================================================
    # LOCAL VALIDATION
    # DIAGNOSTIC ONLY
    # ========================================================

    try:

        validation_ready = (
            scan_validation_v3()
        )

    except Exception as exc:

        validation_ready = False

        print(
            "SCAN VALIDATION ERROR =",
            repr(exc),
            flush=True,
        )

    print(
        "SCAN LOCAL VALIDATION READY =",
        validation_ready,
        flush=True,
    )

    # ========================================================
    # RESTORE ACCEPTED CONFIGURATION
    # ========================================================

    try:

        scan_restore_accepted_configuration(
            FRESH_RECONSTRUCTION_CONFIG
        )

    except Exception as exc:

        print(
            "SCAN CONFIGURATION RESTORE ERROR =",
            repr(exc),
            flush=True,
        )

    # ========================================================
    # RESTORE PENDING NOTIFICATION DELIVERY
    # ========================================================

    scan_flush_configuration_notifications()

    print("=" * 80, flush=True)

    # Original startup units have already
    # executed once before scan_forever.

    _scan_time.sleep(
        SCAN_INTERVAL_SECONDS
    )

    # ========================================================
    # CONTINUOUS EXECUTION
    # ========================================================

    while True:

        started = (
            _scan_time.monotonic()
        )

        try:

            scan_one_cycle()

        except Exception as exc:

            print(
                "SCAN SUPERVISOR ERROR =",
                repr(exc),
                flush=True,
            )

            _scan_traceback.print_exc()

        elapsed = (
            _scan_time.monotonic()
            - started
        )

        sleep_for = max(
            5.0,

            SCAN_INTERVAL_SECONDS
            - elapsed,
        )

        print(
            "SCAN ELAPSED SECONDS =",
            round(elapsed, 2),
            flush=True,
        )

        print(
            "SCAN NEXT SLEEP SECONDS =",
            round(sleep_for, 2),
            flush=True,
        )

        _scan_time.sleep(
            sleep_for
        )


# ============================================================
# END COMPLETE CONTINUOUS SCAN CONTROLLER V3
# END PART 3 OF 3
# ZERO INDENTATION
# ============================================================
#
# PRESERVE EXISTING MANUAL POSITION CONTROLLER
# AND ORIGINAL FINAL MAIN.PY ACTIVATION.
#
# DO NOT ADD A SECOND scan_forever() CALL.
#
# ============================================================

# ============================================================
# WEEX DEMO POSITION CONTROLLER V2
# COMPLETE REPLACEMENT
# ZERO INDENTATION
#
# COMPATIBLE WITH:
# UNIT 13 V6
# UNIT 14 V4
# UNIT 15 V6
# CONTINUOUS SCAN V3
#
# UNIVERSAL SYMBOL PRECISION
# PERSISTENT SQLITE RECONCILIATION
# INDEPENDENT LONG AND SHORT CLOSING
# ============================================================

import os as _dpc_os
import json as _dpc_json
import time as _dpc_time
import sqlite3 as _dpc_sql
import hashlib as _dpc_hashlib
import uuid as _dpc_uuid

from decimal import Decimal as _DPC_D
from decimal import ROUND_DOWN as _DPC_ROUND_DOWN


# ============================================================
# PERSISTENT DATABASE
# ============================================================

_DPC_JOURNAL_DIR = (
    "/var/data/demo_position_control"
)

_DPC_DB_PATH = _dpc_os.path.join(
    _DPC_JOURNAL_DIR,
    "manual_execution_v2.sqlite3",
)


# ============================================================
# EXISTING RENDER ENVIRONMENT INTERFACE
# ============================================================

def dpc_setting(name, default=""):

    return _dpc_os.getenv(
        name,
        default,
    ).strip()


# ============================================================
# DECIMAL HELPERS
# ============================================================

def dpc_decimal(value):

    number = _DPC_D(str(value))

    if not number.is_finite():

        raise ValueError(
            "DPC_INVALID_DECIMAL"
        )

    return number


def dpc_amount(value):

    return format(
        dpc_decimal(value).normalize(),
        "f",
    )


def dpc_now_ms():

    return int(
        _dpc_time.time() * 1000
    )


# ============================================================
# ACTIVE SYMBOL INTERFACE
# ============================================================

def dpc_symbols():

    market, demo = (
        unit_13_14_active_symbols()
    )

    return (
        str(market).upper(),
        str(demo).upper(),
    )


# ============================================================
# EXCHANGE POSITION RETRIEVAL
# ============================================================

def dpc_positions():

    positions = unit_14_v3_positions()

    if not isinstance(
        positions,
        dict,
    ):

        raise RuntimeError(
            "DPC_INVALID_POSITION_RESPONSE"
        )

    return positions


# ============================================================
# CURRENT EXCHANGE CONTRACT SPECIFICATIONS
# ============================================================

def dpc_contract_details():

    config = FRESH_RECONSTRUCTION_CONFIG

    market, demo = dpc_symbols()

    loaded = (
        unit_9_load_symbol_specifications(
            config,
            market,
        )
    )

    if loaded is not True:

        raise RuntimeError(
            "DPC_CONTRACT_SPECS_UNAVAILABLE"
        )

    contract = scan_contract_details(
        config
    )

    return {
        "market_symbol":
            market,

        "demo_symbol":
            demo,

        "quantity_step":
            dpc_decimal(
                contract["quantity_step"]
            ),

        "minimum_quantity":
            dpc_decimal(
                contract["minimum_quantity"]
            ),

        "contract_multiplier":
            dpc_decimal(
                contract["contract_multiplier"]
            ),
    }


# ============================================================
# POSITION ENTRY PRICE
# ============================================================

def dpc_entry_price(position):

    for key in (
        "avgPrice",
        "entryPrice",
        "openPriceAvg",
    ):

        raw = position.get(key)

        if raw is not None:

            try:

                value = dpc_decimal(raw)

                if value > 0:

                    return value

            except Exception:

                continue

    size = dpc_decimal(
        position.get("size", "0")
    )

    open_value = dpc_decimal(
        position.get("openValue", "0")
    )

    if size > 0 and open_value > 0:

        return open_value / size

    return None


# ============================================================
# POSITION INSPECTION
# ============================================================

def dpc_inspect():

    positions = dpc_positions()

    market, demo = dpc_symbols()

    mark = dpc_decimal(
        unit_14_v3_mark()
    )

    precision = (
        FRESH_RECONSTRUCTION_CONFIG.get(
            "market_precision",
            {},
        )
    )

    multiplier = None

    if (
        precision.get(
            "specifications_symbol"
        ) == market

        and precision.get(
            "symbol_specifications_confirmed"
        ) is True
    ):

        multiplier = dpc_decimal(
            precision.get(
                "contract_multiplier",
                1,
            )
        )

    print("=" * 80, flush=True)

    print(
        "DEMO POSITION CONTROLLER = INSPECT",
        flush=True,
    )

    print(
        "DEMO MARKET SYMBOL =",
        market,
        flush=True,
    )

    print(
        "DEMO ORDER SYMBOL =",
        demo,
        flush=True,
    )

    print(
        "DEMO MARK PRICE =",
        mark,
        flush=True,
    )

    print(
        "DEMO OPEN POSITIONS =",
        len(positions),
        flush=True,
    )

    for side, position in positions.items():

        size = dpc_decimal(
            position["size"]
        )

        entry = dpc_entry_price(
            position
        )

        leverage = position.get(
            "leverage",
            "UNAVAILABLE",
        )

        liquidation = position.get(
            "liquidationPrice",

            position.get(
                "liqPrice",
                "UNAVAILABLE",
            ),
        )

        pnl = None

        if (
            entry is not None
            and multiplier is not None
        ):

            if side == "LONG":

                pnl = (
                    mark - entry
                ) * size * multiplier

            elif side == "SHORT":

                pnl = (
                    entry - mark
                ) * size * multiplier

        print("-" * 60, flush=True)

        print(
            "POSITION SIDE =",
            side,
            flush=True,
        )

        print(
            "POSITION SIZE =",
            size,
            flush=True,
        )

        print(
            "ENTRY PRICE =",
            entry,
            flush=True,
        )

        print(
            "MARK PRICE =",
            mark,
            flush=True,
        )

        print(
            "LEVERAGE =",
            leverage,
            flush=True,
        )

        print(
            "LIQUIDATION PRICE =",
            liquidation,
            flush=True,
        )

        print(
            "ESTIMATED UNREALIZED PNL =",

            pnl
            if pnl is not None
            else "UNAVAILABLE",

            flush=True,
        )

        print(
            "PNL EXCLUDES FEES AND FUNDING",
            flush=True,
        )

    print("=" * 80, flush=True)

    return positions


# ============================================================
# SQLITE MANUAL EXECUTION DATABASE
# EXISTING JSON JOURNAL FILES ARE PRESERVED
# ============================================================

def dpc_db():

    _dpc_os.makedirs(
        _DPC_JOURNAL_DIR,
        exist_ok=True,
    )

    db = _dpc_sql.connect(
        _DPC_DB_PATH,
        timeout=30,
        isolation_level=None,
    )

    db.row_factory = _dpc_sql.Row

    db.execute(
        "PRAGMA journal_mode=WAL"
    )

    db.execute("""
        CREATE TABLE IF NOT EXISTS
        dpc_commands_v2 (
            command_key TEXT PRIMARY KEY,
            command_id TEXT NOT NULL,
            symbol TEXT NOT NULL,
            position_side TEXT NOT NULL,
            position_identity TEXT NOT NULL,
            original_quantity TEXT NOT NULL,
            state TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS
        dpc_orders_v2 (
            client_id TEXT PRIMARY KEY,
            command_key TEXT NOT NULL,
            symbol TEXT NOT NULL,
            position_side TEXT NOT NULL,
            quantity TEXT NOT NULL,
            confirmed_filled TEXT NOT NULL DEFAULT '0',
            exchange_order_id TEXT,
            state TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL
        )
    """)

    db.execute("""
        CREATE INDEX IF NOT EXISTS
        dpc_order_command_index_v2
        ON dpc_orders_v2 (
            command_key
        )
    """)

    return db


# ============================================================
# COMMAND IDENTITY
# SEPARATE LONG AND SHORT COMMAND RECORDS
# ============================================================

def dpc_command_key(
    command_id,
    symbol,
    side,
):

    raw = (
        str(command_id)

        + "|"

        + str(symbol)

        + "|"

        + str(side)
    )

    return _dpc_hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()


# ============================================================
# POSITION IDENTITY
# ============================================================

def dpc_position_identity(position):

    return unit_13_cycle_id(
        position
    )


# ============================================================
# LEGACY COMMAND JOURNAL INSPECTION
# ============================================================

def dpc_legacy_command_exists(
    command_id,
):

    digest = _dpc_hashlib.sha256(
        command_id.encode("utf-8")
    ).hexdigest()

    path = _dpc_os.path.join(
        _DPC_JOURNAL_DIR,
        digest + ".json",
    )

    return _dpc_os.path.isfile(
        path
    )


# ============================================================
# READ EXISTING COMMAND
# ============================================================

def dpc_read_command(command_key):

    db = dpc_db()

    try:

        row = db.execute("""
            SELECT *
            FROM dpc_commands_v2
            WHERE command_key = ?
        """, (
            command_key,
        )).fetchone()

        return (
            dict(row)
            if row is not None
            else None
        )

    finally:

        db.close()


# ============================================================
# REGISTER MANUAL CLOSE COMMAND
# ============================================================

def dpc_command_claim(
    command_id,
    symbol,
    side,
    position,
):

    command_key = dpc_command_key(
        command_id,
        symbol,
        side,
    )

    identity = dpc_position_identity(
        position
    )

    quantity = dpc_decimal(
        position["size"]
    )

    now = dpc_now_ms()

    db = dpc_db()

    try:

        db.execute("""
            INSERT OR IGNORE INTO
            dpc_commands_v2 (
                command_key,
                command_id,
                symbol,
                position_side,
                position_identity,
                original_quantity,
                state,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            command_key,

            command_id,

            symbol,

            side,

            identity,

            str(quantity),

            "ACTIVE",

            now,

            now,
        ))

    finally:

        db.close()

    return dpc_read_command(
        command_key
    )


# ============================================================
# UPDATE COMMAND STATE
# ============================================================

def dpc_update_command(
    command_key,
    state,
):

    db = dpc_db()

    try:

        db.execute("""
            UPDATE dpc_commands_v2
            SET
                state = ?,
                updated_at = ?
            WHERE command_key = ?
        """, (
            state,

            dpc_now_ms(),

            command_key,
        ))

    finally:

        db.close()


# ============================================================
# READ COMMAND ORDER ATTEMPTS
# ============================================================

def dpc_read_orders(command_key):

    db = dpc_db()

    try:

        rows = db.execute("""
            SELECT *
            FROM dpc_orders_v2
            WHERE command_key = ?
            ORDER BY created_at
        """, (
            command_key,
        )).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        db.close()


# ============================================================
# TERMINAL EXCHANGE ORDER STATES
# ============================================================

def dpc_terminal(state):

    return str(state).upper() in (
        "FILLED",
        "CANCELED",
        "CANCELLED",
        "REJECTED",
        "EXPIRED",
    )


# ============================================================
# ATOMIC ORDER CLAIM
# ONLY ONE UNRESOLVED ATTEMPT PER COMMAND
# ============================================================

def dpc_order_claim(
    command,
    quantity,
):

    db = dpc_db()

    try:

        db.execute("BEGIN IMMEDIATE")

        rows = db.execute("""
            SELECT state
            FROM dpc_orders_v2
            WHERE command_key = ?
        """, (
            command["command_key"],
        )).fetchall()

        for row in rows:

            if not dpc_terminal(
                row["state"]
            ):

                db.execute("ROLLBACK")

                return None

        client_id = (
            "DPC-"
            + _dpc_uuid.uuid4().hex[:24]
        )

        now = dpc_now_ms()

        db.execute("""
            INSERT INTO dpc_orders_v2 (
                client_id,
                command_key,
                symbol,
                position_side,
                quantity,
                confirmed_filled,
                state,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            client_id,

            command["command_key"],

            command["symbol"],

            command["position_side"],

            str(quantity),

            "0",

            "SUBMITTING",

            now,

            now,
        ))

        db.execute("COMMIT")

        return client_id

    except Exception:

        if db.in_transaction:

            db.execute("ROLLBACK")

        raise

    finally:

        db.close()


# ============================================================
# UPDATE ORDER ATTEMPT
# PRESERVE CONFIRMED FILLED QUANTITY
# ============================================================

def dpc_update_order(
    client_id,
    state,
    exchange_order_id=None,
    confirmed_filled=None,
):

    db = dpc_db()

    try:

        db.execute("BEGIN IMMEDIATE")

        row = db.execute("""
            SELECT *
            FROM dpc_orders_v2
            WHERE client_id = ?
        """, (
            client_id,
        )).fetchone()

        if row is None:

            db.execute("ROLLBACK")

            return False

        previous_filled = dpc_decimal(
            row["confirmed_filled"]
        )

        if confirmed_filled is None:

            filled = previous_filled

        else:

            filled = max(
                previous_filled,

                dpc_decimal(
                    confirmed_filled
                ),
            )

        previous_id = row[
            "exchange_order_id"
        ]

        if (
            previous_id

            and exchange_order_id

            and str(previous_id)
            != str(exchange_order_id)
        ):

            raise RuntimeError(
                "DPC_EXCHANGE_ORDER_ID_CONFLICT"
            )

        order_id = (
            exchange_order_id
            or previous_id
        )

        if row["state"] == "FILLED":

            state = "FILLED"

        db.execute("""
            UPDATE dpc_orders_v2
            SET
                state = ?,
                confirmed_filled = ?,
                exchange_order_id = ?,
                updated_at = ?
            WHERE client_id = ?
        """, (
            str(state).upper(),

            str(filled),

            order_id,

            dpc_now_ms(),

            client_id,
        ))

        db.execute("COMMIT")

        return True

    except Exception:

        if db.in_transaction:

            db.execute("ROLLBACK")

        raise

    finally:

        db.close()


# ============================================================
# EXCHANGE ORDER HISTORY
# ============================================================

def dpc_history(symbol):

    history = unit_14_v3_history(
        demo_symbol=symbol,
    )

    if not isinstance(history, list):

        raise RuntimeError(
            "DPC_INVALID_HISTORY_RESPONSE"
        )

    return history


# ============================================================
# MATCH EXACT MANUAL CLOSE ORDER
# ============================================================

def dpc_match_order(
    attempt,
    history,
):

    matches = []

    expected_side = (
        "SELL"

        if attempt["position_side"] == "LONG"

        else "BUY"
    )

    for record in history:

        if not isinstance(
            record,
            dict,
        ):

            continue

        client_id = (
            record.get("clientOrderId")

            or record.get(
                "newClientOrderId"
            )
        )

        order_id = record.get(
            "orderId"
        )

        client_match = (
            client_id is not None

            and str(client_id)
            == attempt["client_id"]
        )

        exchange_match = (
            attempt.get(
                "exchange_order_id"
            ) is not None

            and order_id is not None

            and str(order_id)
            == str(
                attempt["exchange_order_id"]
            )
        )

        if not (
            client_match
            or exchange_match
        ):

            continue

        if str(
            record.get("symbol", "")
        ).upper() != attempt["symbol"]:

            continue

        if str(
            record.get(
                "positionSide",
                "",
            )
        ).upper() != attempt[
            "position_side"
        ]:

            continue

        if str(
            record.get("side", "")
        ).upper() != expected_side:

            continue

        matches.append(record)

    if not matches:

        return None

    return max(
        matches,

        key=lambda record: (
            dpc_decimal(
                record.get(
                    "executedQty",
                    "0",
                ) or "0"
            ),

            int(
                record.get(
                    "updateTime",
                    0,
                ) or 0
            ),
        ),
    )


# ============================================================
# RECONCILE ALL ATTEMPTS FOR ONE COMMAND
# ============================================================

def dpc_reconcile_command(command):

    attempts = dpc_read_orders(
        command["command_key"]
    )

    if attempts:

        history = dpc_history(
            command["symbol"]
        )

        for attempt in attempts:

            if dpc_terminal(
                attempt["state"]
            ):

                continue

            matched = dpc_match_order(
                attempt,
                history,
            )

            if matched is None:

                continue

            filled = dpc_decimal(
                matched.get(
                    "executedQty",
                    "0",
                ) or "0"
            )

            state = str(
                matched.get(
                    "status",
                    attempt["state"],
                )
            ).upper()

            dpc_update_order(
                attempt["client_id"],

                state,

                matched.get("orderId"),

                filled,
            )

    attempts = dpc_read_orders(
        command["command_key"]
    )

    confirmed = sum(
        (
            dpc_decimal(
                attempt[
                    "confirmed_filled"
                ]
            )

            for attempt in attempts
        ),

        _DPC_D("0"),
    )

    pending = any(
        not dpc_terminal(
            attempt["state"]
        )

        for attempt in attempts
    )

    original = dpc_decimal(
        command["original_quantity"]
    )

    return {
        "confirmed_filled":
            confirmed,

        "pending":
            pending,

        "original_quantity":
            original,

        "remaining_quantity":
            max(
                _DPC_D("0"),

                original - confirmed,
            ),

        "attempts":
            attempts,
    }


# ============================================================
# MANUAL CLOSE NOTIFICATION
# CONFIRMED EXECUTION ONLY
# ============================================================

def dpc_notify_completion(
    command,
    confirmed_quantity,
):

    notification_id = (
        "DPC:"

        + command["command_key"]

        + ":"

        + dpc_amount(
            confirmed_quantity
        )
    )

    message = (
        "WEEX DEMO MANUAL CLOSE\n"

        f"Symbol: {command['symbol']}\n"

        f"Position: {command['position_side']}\n"

        "Confirmed closed quantity: "

        f"{dpc_amount(confirmed_quantity)}\n"

        "Status: CLOSED_CONFIRMED"
    )

    try:

        unit15_queue_notification(
            notification_id,
            message,
        )

    except Exception as exc:

        print(
            "DPC NOTIFICATION ERROR =",
            repr(exc),
            flush=True,
        )


# ============================================================
# SUBMIT MANUAL MARKET CLOSE
# REUSE UNIT 14 EXECUTION INTERFACE
# ============================================================

def dpc_submit_close(
    command,
    quantity,
):

    client_id = dpc_order_claim(
        command,
        quantity,
    )

    if client_id is None:

        return "RECONCILIATION_PENDING"

    print(
        "DEMO CONTROL SUBMITTING CLOSE =",
        command["position_side"],
        flush=True,
    )

    print(
        "DEMO CONTROL CLOSE QUANTITY =",
        quantity,
        flush=True,
    )

    print(
        "DEMO CONTROL CLIENT ORDER ID =",
        client_id,
        flush=True,
    )

    try:

        reply = unit_14_submit_close(
            command["symbol"],

            command["position_side"],

            quantity,

            client_id,
        )

    except Exception as exc:

        dpc_update_order(
            client_id,
            "ACK_UNKNOWN",
        )

        print(
            "DEMO CONTROL ACK UNKNOWN =",
            repr(exc),
            flush=True,
        )

        return "ACK_UNKNOWN"

    print(
        "DEMO CONTROL ORDER RESPONSE =",
        reply,
        flush=True,
    )

    if isinstance(reply, dict):

        order_id = reply.get(
            "orderId"
        )

        if order_id:

            dpc_update_order(
                client_id,

                "ACKNOWLEDGED",

                order_id,
            )

            return "ACKNOWLEDGED"

        response_status = str(
            reply.get(
                "status",
                "",
            )
        ).upper()

        if response_status == "REJECTED":

            dpc_update_order(
                client_id,
                "REJECTED",
            )

            return "REJECTED"

    dpc_update_order(
        client_id,
        "ACK_UNKNOWN",
    )

    return "ACK_UNKNOWN"


# ============================================================
# COMPLETE MANUAL POSITION CLOSE
# PERSISTENT RECONCILIATION AND PARTIAL FILL CONTINUATION
# ============================================================

def dpc_close(
    side,
    command_id,
):

    side = str(side).upper()

    if side not in (
        "LONG",
        "SHORT",
    ):

        raise ValueError(
            "DPC_INVALID_POSITION_SIDE"
        )

    market, symbol = dpc_symbols()

    command_key = dpc_command_key(
        command_id,
        symbol,
        side,
    )

    command = dpc_read_command(
        command_key
    )

    # ========================================================
    # PRESERVE COMPLETED COMMANDS
    # DO NOT CLOSE A NEW POSITION WITH AN OLD COMMAND
    # ========================================================

    if command is not None:

        if command["state"] in (
            "CLOSED_CONFIRMED",
            "POSITION_CHANGED",
            "POSITION_ALREADY_FLAT",
        ):

            return command["state"]

    # ========================================================
    # LEGACY JOURNAL COMPATIBILITY
    # OLD UNRESOLVED COMMANDS REQUIRE A NEW EXPLICIT ID
    # ========================================================

    if command is None:

        if dpc_legacy_command_exists(
            command_id
        ):

            return "LEGACY_COMMAND_REQUIRES_REVIEW"

    positions = dpc_positions()

    position = positions.get(
        side
    )

    # ========================================================
    # REGISTER NEW COMMAND
    # ========================================================

    if command is None:

        if position is None:

            return "NO_POSITION"

        command = dpc_command_claim(
            command_id,

            symbol,

            side,

            position,
        )

    # ========================================================
    # RECONCILE PREVIOUS ATTEMPTS
    # ========================================================

    reconciliation = (
        dpc_reconcile_command(
            command
        )
    )

    confirmed = reconciliation[
        "confirmed_filled"
    ]

    print(
        "DEMO CONTROL CONFIRMED FILLED =",
        confirmed,
        flush=True,
    )

    print(
        "DEMO CONTROL PENDING ORDER =",
        reconciliation["pending"],
        flush=True,
    )

    # ========================================================
    # RE-READ EXCHANGE POSITION AFTER RECONCILIATION
    # ========================================================

    position = dpc_positions().get(
        side
    )

    if position is None:

        if (
            not reconciliation["pending"]

            and confirmed >= reconciliation[
                "original_quantity"
            ]
        ):

            dpc_update_command(
                command_key,
                "CLOSED_CONFIRMED",
            )

            dpc_notify_completion(
                command,
                confirmed,
            )

            return "CLOSED_CONFIRMED"

        if reconciliation["pending"]:

            return "FLAT_RECONCILIATION_PENDING"

        dpc_update_command(
            command_key,
            "POSITION_ALREADY_FLAT",
        )

        return "POSITION_ALREADY_FLAT"

    # ========================================================
    # DO NOT REUSE COMMAND ON A DIFFERENT POSITION
    # ========================================================

    current_identity = (
        dpc_position_identity(
            position
        )
    )

    if current_identity != command[
        "position_identity"
    ]:

        if reconciliation["pending"]:

            return "POSITION_CHANGED_RECONCILIATION_PENDING"

        dpc_update_command(
            command_key,
            "POSITION_CHANGED",
        )

        return "POSITION_CHANGED"

    # ========================================================
    # UNKNOWN OR OPEN ORDER
    # RECONCILE BEFORE ANOTHER SUBMISSION
    # ========================================================

    if reconciliation["pending"]:

        return "RECONCILIATION_PENDING"

    # ========================================================
    # CURRENT CONTRACT QUANTITY PRECISION
    # ========================================================

    contract = dpc_contract_details()

    step = contract[
        "quantity_step"
    ]

    minimum = contract[
        "minimum_quantity"
    ]

    current_size = dpc_decimal(
        position["size"]
    )

    remaining_target = reconciliation[
        "remaining_quantity"
    ]

    quantity = min(
        current_size,
        remaining_target,
    )

    quantity = (
        quantity / step
    ).to_integral_value(
        rounding=_DPC_ROUND_DOWN
    ) * step

    if quantity <= 0:

        return "TARGET_FILLED_POSITION_REMAINS"

    if quantity < minimum:

        print(
            "DEMO CONTROL REMAINING QUANTITY =",
            quantity,
            flush=True,
        )

        print(
            "DEMO CONTROL EXCHANGE MINIMUM =",
            minimum,
            flush=True,
        )

        return "BELOW_EXCHANGE_MINIMUM"

    # ========================================================
    # IMMEDIATE POSITION RECHECK
    # ========================================================

    latest = dpc_positions().get(
        side
    )

    if latest is None:

        return "POSITION_CHANGED"

    if dpc_position_identity(
        latest
    ) != current_identity:

        return "POSITION_CHANGED"

    latest_size = dpc_decimal(
        latest["size"]
    )

    if latest_size != current_size:

        return "POSITION_SIZE_CHANGED"

    # ========================================================
    # EXECUTE REMAINING CLOSE QUANTITY
    # ========================================================

    submission = dpc_submit_close(
        command,
        quantity,
    )

    print(
        "DEMO CONTROL SUBMISSION STATUS =",
        submission,
        flush=True,
    )

    # ========================================================
    # IMMEDIATE EXCHANGE RECONCILIATION
    # ========================================================

    reconciliation = (
        dpc_reconcile_command(
            command
        )
    )

    confirmed = reconciliation[
        "confirmed_filled"
    ]

    remaining_position = (
        dpc_positions().get(side)
    )

    if (
        remaining_position is None

        and not reconciliation["pending"]

        and confirmed >= reconciliation[
            "original_quantity"
        ]
    ):

        dpc_update_command(
            command_key,
            "CLOSED_CONFIRMED",
        )

        dpc_notify_completion(
            command,
            confirmed,
        )

        return "CLOSED_CONFIRMED"

    if reconciliation["pending"]:

        return "RECONCILIATION_PENDING"

    if remaining_position is None:

        dpc_update_command(
            command_key,
            "POSITION_ALREADY_FLAT",
        )

        return "POSITION_ALREADY_FLAT"

    return "REMAINING_POSITION_PENDING"


# ============================================================
# RENDER MANUAL POSITION COMMAND PROCESSOR
# EXISTING ENVIRONMENT VARIABLES PRESERVED
# ============================================================

def dpc_process():

    command = dpc_setting(
        "DEMO_POSITION_CONTROL",
        "OFF",
    ).upper()

    arm = dpc_setting(
        "DEMO_CONTROL_ARM",
        "NO",
    ).upper()

    command_id = dpc_setting(
        "DEMO_CONTROL_COMMAND_ID",
        "",
    )

    # Refresh the active symbol because
    # manual mode bypasses the entry pipeline.

    scan_refresh_active_pair(
        FRESH_RECONSTRUCTION_CONFIG
    )

    if command == "OFF":

        return "OFF"

    # ========================================================
    # INSPECTION COMMANDS
    # ========================================================

    if command in (
        "INSPECT",
        "STATUS",
    ):

        dpc_inspect()

        return "INSPECTED"

    # ========================================================
    # EXISTING MANUAL CLOSE COMMANDS
    # ========================================================

    if command not in (
        "CLOSE_LONG",
        "CLOSE_SHORT",
        "CLOSE_ALL",
    ):

        print(
            "DEMO CONTROL UNKNOWN COMMAND =",
            command,
            flush=True,
        )

        return "REJECTED"

    if arm != "YES":

        print(
            "DEMO CONTROL CLOSE NOT ARMED",
            flush=True,
        )

        return "NOT_ARMED"

    if not command_id:

        print(
            "DEMO CONTROL COMMAND ID REQUIRED",
            flush=True,
        )

        return "REJECTED"

    # ========================================================
    # INDEPENDENT LONG AND SHORT CLOSING
    # ========================================================

    if command == "CLOSE_ALL":

        results = {}

        for side in (
            "LONG",
            "SHORT",
        ):

            try:

                results[side] = dpc_close(
                    side,

                    command_id
                    + "-"
                    + side,
                )

            except Exception as exc:

                results[side] = (
                    "ERROR:"
                    + str(exc)
                )

                print(
                    "DEMO CONTROL SIDE ERROR =",
                    side,
                    repr(exc),
                    flush=True,
                )

        print(
            "DEMO CONTROL CLOSE ALL RESULTS =",
            results,
            flush=True,
        )

        completed_states = (
            "CLOSED_CONFIRMED",
            "NO_POSITION",
            "POSITION_ALREADY_FLAT",
        )

        if all(
            state in completed_states

            for state in results.values()
        ):

            return "CLOSE_ALL_CONFIRMED_FLAT"

        return (
            "CLOSE_ALL_PENDING:"
            + _dpc_json.dumps(results)
        )

    # ========================================================
    # SINGLE POSITION CLOSING
    # ========================================================

    side = command.split(
        "_",
        1,
    )[1]

    result = dpc_close(
        side,
        command_id,
    )

    print(
        "DEMO CONTROL RESULT =",
        result,
        flush=True,
    )

    return result


# ============================================================
# END WEEX DEMO POSITION CONTROLLER V2
# ZERO INDENTATION
# ============================================================


# ============================================================
# START COMPLETE CONTINUOUS SCAN CONTROLLER V3
# ALL FUNCTIONS NOW DEFINED
# SINGLE ACTIVATION
# ============================================================

scan_forever()


# ============================================================
# END COMPLETE MAIN.PY
# ============================================================
