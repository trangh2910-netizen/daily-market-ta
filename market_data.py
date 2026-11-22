"""Fetch accurate daily stock/macro market data and compute beginner-friendly TA indicators."""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
import requests
import yfinance as yf

from config import MACRO_SYMBOLS, VN_TZ, VN_WATCHLIST

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; DailyMarketTA/1.0)"}


def fetch_vndirect_ohlcv(symbol: str, days: int = 160) -> pd.DataFrame:
    """Fetch daily OHLCV bars from VNDirect dchart API (values in VND for stocks, points for index)."""
    now_ts = int(time.time())
    from_ts = now_ts - days * 86400
    resp = requests.get(
        "https://dchart-api.vndirect.com.vn/dchart/history",
        params={"symbol": symbol, "resolution": "D", "from": from_ts, "to": now_ts},
        headers=HEADERS,
        timeout=12,
    )
    resp.raise_for_status()
    payload = resp.json()
    if payload.get("s") != "ok" or not payload.get("t"):
        raise ValueError(f"VNDirect returned empty data for {symbol}: {payload.get('s')}")

    scale = 1.0 if symbol == "VNINDEX" else 1000.0
    df = pd.DataFrame(
        {
            "Open": [float(x) * scale for x in payload["o"]],
            "High": [float(x) * scale for x in payload["h"]],
            "Low": [float(x) * scale for x in payload["l"]],
            "Close": [float(x) * scale for x in payload["c"]],
            "Volume": [float(x) for x in payload["v"]],
        },
        index=pd.to_datetime(payload["t"], unit="s", utc=True).tz_convert(VN_TZ).normalize(),
    )
    df.index.name = "Date"
    df = df[~df.index.duplicated(keep="last")].sort_index()
    return df


def fetch_yfinance_ohlcv(yf_symbol: str, period: str = "6mo") -> pd.DataFrame:
    """Fallback/macro OHLCV fetcher via yfinance."""
    df = yf.Ticker(yf_symbol).history(period=period, auto_adjust=False)
    if df.empty:
        raise ValueError(f"yfinance returned empty data for {yf_symbol}")
    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")
    df.index = df.index.tz_convert(VN_TZ).normalize()
    df = df[~df.index.duplicated(keep="last")].sort_index()
    return df


def get_vn_ohlcv(symbol: str) -> tuple[pd.DataFrame, str]:
    """Fetch Vietnamese market OHLCV with VNDirect primary and yfinance fallback."""
    try:
        df = fetch_vndirect_ohlcv(symbol)
        if len(df) >= 25:
            return df, "VNDirect"
    except Exception:
        pass

    yf_sym = "^VNINDEX" if symbol == "VNINDEX" else f"{symbol}.VN"
    df = fetch_yfinance_ohlcv(yf_sym)
    return df, "Yahoo Finance"


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Wilder's RSI(14)."""
    delta = series.diff()
    gain = delta.clip(lower=0.0)
    loss = (-delta).clip(lower=0.0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    return 100.0 - (100.0 / (1.0 + rs))


def enrich_ta_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add MA20, MA50, RSI14, MACD, Volume MA20, and 20-day support/resistance."""
    out = df.copy()
    out["MA20"] = out["Close"].rolling(20).mean()
    out["MA50"] = out["Close"].rolling(50).mean()
    out["VOL_MA20"] = out["Volume"].rolling(20).mean()
    out["RSI14"] = compute_rsi(out["Close"], 14)

    ema12 = out["Close"].ewm(span=12, adjust=False).mean()
    ema26 = out["Close"].ewm(span=26, adjust=False).mean()
    out["MACD"] = ema12 - ema26
    out["MACD_SIGNAL"] = out["MACD"].ewm(span=9, adjust=False).mean()
    out["MACD_HIST"] = out["MACD"] - out["MACD_SIGNAL"]
    return out


def analyze_symbol(symbol: str, name: str, sector: str) -> dict[str, Any]:
    """Compute latest snapshot, signals, plain-Vietnamese summary, and keep DataFrame for charting."""
    raw_df, source = get_vn_ohlcv(symbol)
    df = enrich_ta_indicators(raw_df)
    if len(df) < 2:
        raise ValueError(f"Insufficient bars for {symbol}")

    last = df.iloc[-1]
    prev = df.iloc[-2]
    lookback = df.iloc[-21:-1] if len(df) >= 22 else df.iloc[:-1]

    close = float(last["Close"])
    prev_close = float(prev["Close"])
    open_p = float(last["Open"])
    high_p = float(last["High"])
    low_p = float(last["Low"])
    vol = float(last["Volume"])
    vol_ma20 = float(last["VOL_MA20"]) if pd.notna(last["VOL_MA20"]) and last["VOL_MA20"] > 0 else vol
    vol_ratio = vol / vol_ma20 if vol_ma20 > 0 else 1.0

    change = close - prev_close
    change_pct = (change / prev_close) * 100.0 if prev_close else 0.0

    ma20 = float(last["MA20"]) if pd.notna(last["MA20"]) else None
    ma50 = float(last["MA50"]) if pd.notna(last["MA50"]) else None
    prev_ma20 = float(prev["MA20"]) if pd.notna(prev["MA20"]) else None
    rsi14 = float(last["RSI14"]) if pd.notna(last["RSI14"]) else 50.0
    macd = float(last["MACD"]) if pd.notna(last["MACD"]) else 0.0
    macd_sig = float(last["MACD_SIGNAL"]) if pd.notna(last["MACD_SIGNAL"]) else 0.0
    prev_macd = float(prev["MACD"]) if pd.notna(prev["MACD"]) else 0.0
    prev_macd_sig = float(prev["MACD_SIGNAL"]) if pd.notna(prev["MACD_SIGNAL"]) else 0.0

    support_20 = float(lookback["Low"].min())
    resistance_20 = float(lookback["High"].max())

    # Candlestick anatomy
    candle_range = max(high_p - low_p, 1e-6)
    body = abs(close - open_p)
    upper_wick = high_p - max(open_p, close)
    lower_wick = min(open_p, close) - low_p

    body_pct = (body / candle_range) * 100.0
    upper_wick_pct = (upper_wick / candle_range) * 100.0
    lower_wick_pct = (lower_wick / candle_range) * 100.0

    is_doji = bool(body_pct <= 16.0)
    candle_color = "doji" if is_doji else ("green" if close >= open_p else "red")
    is_hammer = bool(lower_wick >= max(body * 1.8, candle_range * 0.42) and upper_wick <= candle_range * 0.25)
    is_shooting_star = bool(upper_wick >= max(body * 1.8, candle_range * 0.42) and lower_wick <= candle_range * 0.25)
    is_bullish_engulfing = bool(
        prev["Close"] < prev["Open"]
        and close > open_p
        and close >= prev["Open"]
        and open_p <= prev["Close"]
    )
    is_vol_spike = bool(vol_ratio >= 1.35)
    is_ma20_cross_up = bool(ma20 and prev_ma20 and prev_close <= prev_ma20 and close > ma20)
    is_macd_cross_up = bool(prev_macd <= prev_macd_sig and macd > macd_sig)
    is_near_support = bool(((close - support_20) / support_20) <= 0.025 if support_20 else False)
    is_near_resistance = bool(((resistance_20 - close) / resistance_20) <= 0.025 if resistance_20 else False)

    if rsi14 >= 70:
        rsi_zone = "overbought"
        rsi_plain = f"RSI {rsi14:.0f} (Vùng nóng - nhiều người đang mua đuổi)"
    elif rsi14 <= 30:
        rsi_zone = "oversold"
        rsi_plain = f"RSI {rsi14:.0f} (Vùng quá bán - giá đã giảm khá sâu)"
    elif rsi14 >= 55:
        rsi_zone = "bullish"
        rsi_plain = f"RSI {rsi14:.0f} (Đà tăng đang chiếm ưu thế)"
    elif rsi14 <= 45:
        rsi_zone = "weak"
        rsi_plain = f"RSI {rsi14:.0f} (Lực mua còn yếu)"
    else:
        rsi_zone = "neutral"
        rsi_plain = f"RSI {rsi14:.0f} (Cân bằng, chưa rõ xu hướng)"

    # Beginner-friendly status badge
    if ma20 and close > ma20 and change_pct >= 0 and rsi14 < 70:
        status_label = "Tích cực"
        status_tone = "bullish"
        beginner_note = "Giá nằm trên đường trung bình 20 ngày (MA20), xu hướng ngắn hạn đang khỏe."
    elif rsi14 >= 70:
        status_label = "Tăng nóng"
        status_tone = "caution"
        beginner_note = "Giá tăng tốt nhưng RSI đã vào vùng quá mua (>=70), dễ rung lắc hạ nhiệt."
    elif ma20 and close < ma20 and rsi14 <= 35:
        status_label = "Giảm sâu"
        status_tone = "bearish"
        beginner_note = "Giá dưới MA20 và RSI thấp; chỉ nên quan sát chờ tạo đáy ổn định."
    elif ma20 and close < ma20:
        status_label = "Yếu / Chờ"
        status_tone = "bearish"
        beginner_note = "Giá vẫn nằm dưới đường trung bình 20 ngày, lực hồi chưa mạnh."
    else:
        status_label = "Đi ngang"
        status_tone = "neutral"
        beginner_note = "Biên độ hẹp quanh vùng cân bằng, thị trường đang chờ tín hiệu rõ hơn."

    if is_vol_spike:
        beginner_note += f" Khối lượng hôm nay cao gấp {vol_ratio:.1f}x mức bình thường."

    return {
        "symbol": symbol,
        "name": name,
        "sector": sector,
        "source": source,
        "trade_date": df.index[-1].strftime("%Y-%m-%d"),
        "trade_date_vn": df.index[-1].strftime("%d/%m/%Y"),
        "open": round(open_p, 2),
        "high": round(high_p, 2),
        "low": round(low_p, 2),
        "close": round(close, 2),
        "prev_close": round(prev_close, 2),
        "change": round(change, 2),
        "change_pct": round(change_pct, 2),
        "volume": int(vol),
        "vol_ratio": round(vol_ratio, 2),
        "ma20": round(ma20, 2) if ma20 else None,
        "ma50": round(ma50, 2) if ma50 else None,
        "rsi14": round(rsi14, 1),
        "rsi_zone": rsi_zone,
        "rsi_plain": rsi_plain,
        "macd": round(macd, 2),
        "macd_signal": round(macd_sig, 2),
        "support_20": round(support_20, 2),
        "resistance_20": round(resistance_20, 2),
        "candle": {
            "color": candle_color,
            "body_pct": round(body_pct, 1),
            "upper_wick_pct": round(upper_wick_pct, 1),
            "lower_wick_pct": round(lower_wick_pct, 1),
            "is_doji": is_doji,
            "is_hammer": is_hammer,
            "is_shooting_star": is_shooting_star,
            "is_bullish_engulfing": is_bullish_engulfing,
        },
        "signals": {
            "vol_spike": is_vol_spike,
            "ma20_cross_up": is_ma20_cross_up,
            "macd_cross_up": is_macd_cross_up,
            "above_ma20": bool(ma20 and close > ma20),
            "above_ma50": bool(ma50 and close > ma50),
            "near_support": is_near_support,
            "near_resistance": is_near_resistance,
        },
        "status_label": status_label,
        "status_tone": status_tone,
        "beginner_note": beginner_note,
        "_df": df,
    }


def fetch_macro_snapshot() -> list[dict[str, Any]]:
    """Fetch accurate daily international macro & FX indicators."""
    items = []
    for cfg in MACRO_SYMBOLS:
        sym = cfg["symbol"]
        try:
            df = fetch_yfinance_ohlcv(sym, period="1mo")
            if len(df) < 2:
                continue
            close = float(df["Close"].iloc[-1])
            prev = float(df["Close"].iloc[-2])
            chg_pct = ((close - prev) / prev) * 100.0 if prev else 0.0
            items.append(
                {
                    "symbol": sym,
                    "label": cfg["label"],
                    "unit": cfg["unit"],
                    "decimals": cfg["decimals"],
                    "close": round(close, cfg["decimals"]),
                    "change_pct": round(chg_pct, 2),
                    "date_vn": df.index[-1].strftime("%d/%m/%Y"),
                }
            )
        except Exception as exc:
            items.append(
                {
                    "symbol": sym,
                    "label": cfg["label"],
                    "unit": cfg["unit"],
                    "decimals": cfg["decimals"],
                    "close": None,
                    "change_pct": 0.0,
                    "date_vn": "",
                    "error": str(exc),
                }
            )
    return items


def collect_all_market_data() -> dict[str, Any]:
    """Collect VN-Index, watchlist stocks, and international macro snapshot."""
    vnindex = analyze_symbol("VNINDEX", "Chỉ số VN-Index", "Thị trường chung")
    stocks: list[dict[str, Any]] = []
    for item in VN_WATCHLIST:
        try:
            stocks.append(analyze_symbol(item["symbol"], item["name"], item["sector"]))
        except Exception as exc:
            print(f"[WARN] Skipped {item['symbol']}: {exc}")

    macro = fetch_macro_snapshot()
    now_vn = datetime.now(VN_TZ)
    is_weekend = now_vn.weekday() >= 5

    return {
        "generated_at": now_vn.isoformat(),
        "generated_date_vn": now_vn.strftime("%d/%m/%Y"),
        "generated_time_vn": now_vn.strftime("%H:%M"),
        "market_trade_date_vn": vnindex["trade_date_vn"],
        "is_weekend_or_closed": is_weekend or (vnindex["trade_date_vn"] != now_vn.strftime("%d/%m/%Y")),
        "vnindex": vnindex,
        "stocks": stocks,
        "macro": macro,
    }
