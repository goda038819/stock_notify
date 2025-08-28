import yfinance as yf
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

plt.rcParams["font.family"] = "Yu Gothic"
plt.rcParams["axes.unicode_minus"] = False

WEBHOOK_URL = "https://discordapp.com/api/webhooks/1410244506070024242/fmdj2K7PgCvSR1s_ddXj2opzeMw_ndJa0SCHCBFEa7Y0TKJggD4TM_UduQ7Qj15MrNP_"

tickers = {
    "9434.T": "ソフトバンク株式会社",
    "7203.T": "トヨタ",
    "7974.T": "任天堂",
    "^N225": "日経平均"
}

messages = ["【今日の株価まとめ】\n"]

fig, axes = plt.subplots(2, 2, figsize=(12, 8))
axes = axes.flatten()

for i, (code, name) in enumerate(tickers.items()):
    # 過去1年の株価データ
    data = yf.Ticker(code).history(period="1y")
    data['MA5'] = data['Close'].rolling(window=5).mean()
    data['MA20'] = data['Close'].rolling(window=20).mean()

    latest = data.iloc[-1]
    prev = data.iloc[-2]
    diff = latest['Close'] - prev['Close']
    pct_change = (diff / prev['Close']) * 100
    ma5 = latest['MA5'] if not latest['MA5'] != latest['MA5'] else 0
    ma20 = latest['MA20'] if not latest['MA20'] != latest['MA20'] else 0
    trend = "📈" if diff > 0 else "📉" if diff < 0 else "➖"

    messages.append(
        f"{trend} {name} ({code})\n"
        f"終値: {latest['Close']:.2f} 円\n"
        f"前日比: {diff:+.2f} 円 ({pct_change:+.2f}%)\n"
        f"MA5: {ma5:.2f}\n"
        f"MA20: {ma20:.2f}\n"
    )

    ax = axes[i]
    ax.plot(data.index, data['Close'], label="終値", linewidth=1.5)
    ax.plot(data.index, data['MA5'], label="MA5", linestyle="--")
    ax.plot(data.index, data['MA20'], label="MA20", linestyle=":")

    # x軸を1か月ごとの目盛りに設定
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    fig.autofmt_xdate(rotation=45)

    ax.set_title(f"{name}")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig("stocks_summary.png")
plt.close()

requests.post(WEBHOOK_URL, json={"content": "\n".join(messages)})

with open("stocks_summary.png", "rb") as f:
    requests.post(
        WEBHOOK_URL,
        files={"file": f},
        data={"content": "📊 株価推移グラフ（終値＋MA5/MA20）"}
    )
