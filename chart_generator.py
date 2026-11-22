"""Generate dark-mode TradingView-style candlestick charts with beginner TA annotations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd

plt.rcParams["font.sans-serif"] = ["Arial", "Segoe UI", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def _format_price(val: float, is_index: bool) -> str:
    return f"{val:,.2f}" if is_index else f"{val:,.0f}"


def render_annotated_chart(
    stock_data: dict[str, Any],
    output_path: Path,
    subtitle: str = "",
    focus: str = "candle",
) -> Path:
    """Render a 3-panel candlestick chart (Price+MA+S/R, Volume, RSI14) with annotations."""
    df_full: pd.DataFrame = stock_data["_df"]
    df = df_full.tail(50).copy()
    is_index = stock_data["symbol"] == "VNINDEX"

    mc = mpf.make_marketcolors(
        up="#22c55e",
        down="#ef4444",
        edge="inherit",
        wick="inherit",
        volume={"up": "#22c55e88", "down": "#ef444488"},
    )
    style = mpf.make_mpf_style(
        base_mpf_style="nightclouds",
        marketcolors=mc,
        facecolor="#0f172a",
        figcolor="#0b1120",
        gridcolor="#1e293b",
        gridstyle="--",
        rc={"font.sans-serif": ["Arial", "Segoe UI", "DejaVu Sans"], "axes.labelcolor": "#cbd5e1"},
    )

    addplots = []
    if df["MA20"].notna().any():
        addplots.append(mpf.make_addplot(df["MA20"], panel=0, color="#f59e0b", width=1.4, label="MA20"))
    if df["MA50"].notna().any():
        addplots.append(mpf.make_addplot(df["MA50"], panel=0, color="#38bdf8", width=1.4, label="MA50"))

    if df["RSI14"].notna().any():
        addplots.append(
            mpf.make_addplot(
                df["RSI14"],
                panel=2,
                color="#a855f7",
                width=1.4,
                ylabel="RSI (14)",
                ylim=(10, 90),
            )
        )

    title_str = (
        f"{stock_data['symbol']} ({stock_data['name']}) — {_format_price(stock_data['close'], is_index)} "
        f"({stock_data['change_pct']:+.2f}%) | Phiên {stock_data['trade_date_vn']}"
    )

    fig, axes = mpf.plot(
        df,
        type="candle",
        style=style,
        volume=True,
        addplot=addplots if addplots else None,
        panel_ratios=(5, 1.8, 1.8) if df["RSI14"].notna().any() else (5, 2),
        figsize=(11.5, 7.2),
        returnfig=True,
        datetime_format="%d/%m",
        xrotation=15,
        tight_layout=False,
    )

    ax_price = axes[0]
    fig.suptitle(title_str, fontsize=12.5, fontweight="bold", color="#f8fafc", x=0.08, y=0.97, ha="left")
    if subtitle:
        ax_price.set_title(subtitle, fontsize=9.8, color="#94a3b8", loc="left", pad=10)

    # Support & Resistance lines (20-day lookback)
    sup = stock_data["support_20"]
    res = stock_data["resistance_20"]
    n_bars = len(df)
    ax_price.axhline(res, color="#fb7185", linestyle="--", linewidth=1.1, alpha=0.85)
    ax_price.axhline(sup, color="#34d399", linestyle="--", linewidth=1.1, alpha=0.85)

    ax_price.text(
        1,
        res,
        f" Kháng cự (Trần): {_format_price(res, is_index)}",
        color="#fda4af",
        fontsize=8.5,
        va="bottom",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="#1e293b", edgecolor="#fb7185", alpha=0.85),
    )
    ax_price.text(
        1,
        sup,
        f" Hỗ trợ (Sàn): {_format_price(sup, is_index)}",
        color="#6ee7b7",
        fontsize=8.5,
        va="top",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="#1e293b", edgecolor="#34d399", alpha=0.85),
    )

    # Annotate latest candle so beginners know exactly where to look
    last_x = n_bars - 1
    last_close = stock_data["close"]
    last_high = stock_data["high"]
    last_low = stock_data["low"]

    if focus == "wick" and stock_data["candle"]["lower_wick_pct"] >= 30:
        target_y = last_low
        callout = f"Râu dưới dài ({stock_data['candle']['lower_wick_pct']:.0f}%)\nCó lực đỡ giá"
    elif focus == "volume":
        target_y = last_high
        callout = f"Giá hôm nay\nVol = {stock_data['vol_ratio']:.1f}x TB"
    elif focus == "ma20" and stock_data["ma20"]:
        target_y = last_close
        pos = "TRÊN MA20" if stock_data["signals"]["above_ma20"] else "DƯỚI MA20"
        callout = f"Đóng cửa {pos}\nMA20 = {_format_price(stock_data['ma20'], is_index)}"
    else:
        target_y = last_high
        callout = f"Phiên mới nhất\n{stock_data['status_label']}"

    ax_price.annotate(
        callout,
        xy=(last_x, target_y),
        xytext=(max(last_x - 11, 2), target_y),
        textcoords="data",
        color="#fef08a",
        fontsize=8.8,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="#1e293b", edgecolor="#facc15", linewidth=1.2),
        arrowprops=dict(arrowstyle="->", color="#facc15", lw=1.5, connectionstyle="arc3,rad=0.15"),
        va="center",
    )

    # Beginner-friendly note for MA lines
    ax_price.text(
        0.01,
        0.96,
        "MA20 (Vàng): TB 20 ngày   |   MA50 (Xanh): TB 50 ngày",
        transform=ax_price.transAxes,
        color="#cbd5e1",
        fontsize=8.3,
        va="top",
        bbox=dict(boxstyle="round,pad=0.25", facecolor="#0f172a", edgecolor="#334155", alpha=0.85),
    )

    # Add 70 / 30 threshold lines on RSI panel if present
    if len(axes) >= 5 and df["RSI14"].notna().any():
        ax_rsi = axes[4]
        ax_rsi.axhline(70, color="#ef4444", linestyle=":", linewidth=0.9, alpha=0.8)
        ax_rsi.axhline(30, color="#22c55e", linestyle=":", linewidth=0.9, alpha=0.8)
        ax_rsi.text(1, 72, "70 (Quá mua)", color="#fca5a5", fontsize=7.5)
        ax_rsi.text(1, 22, "30 (Quá bán)", color="#86efac", fontsize=7.5)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="#0b1120")
    plt.close(fig)
    return output_path
