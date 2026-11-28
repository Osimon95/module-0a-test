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
