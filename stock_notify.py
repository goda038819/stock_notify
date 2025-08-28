import yfinance as yf            # Yahoo Financeから株価データを取得
import requests                  # DiscordにHTTPリクエストを送信
import matplotlib.pyplot as plt  # グラフ描画用

# ===============================
# 日本語フォント設定（警告回避）
# ===============================
plt.rcParams["font.family"] = "Yu Gothic"  # Windowsなら "Yu Gothic" や "Meiryo"
plt.rcParams["axes.unicode_minus"] = False  # マイナス記号を正しく表示

# Discord Webhook URL（通知先）
WEBHOOK_URL = "https://discordapp.com/api/webhooks/1410244506070024242/fmdj2K7PgCvSR1s_ddXj2opzeMw_ndJa0SCHCBFEa7Y0TKJggD4TM_UduQ7Qj15MrNP_"

# 監視する銘柄リスト（コード: 名前）
tickers = {
    "9984.T": "ソフトバンク",
    "7203.T": "トヨタ",
    "7974.T": "任天堂",
    "^N225": "日経平均"  # 日経平均も一緒に監視
}

# Discordに送るテキストメッセージを格納するリスト
messages = ["【今日の株価まとめ】\n"]

# グラフのキャンバスを作成（2行2列で4銘柄分）
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
axes = axes.flatten()  # 2次元配列を1次元に変換して扱いやすくする

# 各銘柄ごとの処理
for i, (code, name) in enumerate(tickers.items()):
    # 過去1ヶ月の株価データを取得
    data = yf.Ticker(code).history(period="1mo")

    # 移動平均線を計算（MA5とMA20）
    data['MA5'] = data['Close'].rolling(window=5).mean()
    data['MA20'] = data['Close'].rolling(window=20).mean()

    # 最新データと前日データを取得
    latest = data.iloc[-1]
    prev = data.iloc[-2]

    # 前日比と騰落率を計算
    diff = latest['Close'] - prev['Close']  # 終値の差
    pct_change = (diff / prev['Close']) * 100  # 前日比のパーセント

    # 移動平均を取得（NaNの場合は0に置換）
    ma5 = latest['MA5'] if not latest['MA5'] != latest['MA5'] else 0  # NaNチェック
    ma20 = latest['MA20'] if not latest['MA20'] != latest['MA20'] else 0

    # 上昇・下降・横ばいのアイコン設定
    trend = "📈" if diff > 0 else "📉" if diff < 0 else "➖"

    # テキストメッセージを作成してリストに追加（丸括弧で囲んで改行OK）
    messages.append((
        f"{trend} {name} ({code})\n"
        f"終値: {latest['Close']:.2f} 円\n"
        f"前日比: {diff:+.2f} 円 ({pct_change:+.2f}%)\n"
        f"MA5: {ma5:.2f}, MA20: {ma20:.2f}\n"
    ))

    # グラフ描画
    ax = axes[i]
    ax.plot(data.index, data['Close'], label="終値", linewidth=1.5)
    ax.plot(data.index, data['MA5'], label="MA5", linestyle="--")
    ax.plot(data.index, data['MA20'], label="MA20", linestyle=":")

    # 5日ごとにx軸ラベルを設定
    xticks = data.index[::5]  # 5日ごとのインデックス
    ax.set_xticks(xticks)
    ax.set_xticklabels([d.strftime("%m/%d") for d in xticks], rotation=45)  # 日付表示を回転

    ax.set_title(f"{name}")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(fontsize=8)

# レイアウトを自動調整して保存
plt.tight_layout()
plt.savefig("stocks_summary.png")  # グラフを画像として保存
plt.close()  # メモリ解放

# Discordにテキストを送信
requests.post(WEBHOOK_URL, json={"content": "\n".join(messages)})

# Discordに画像を送信
with open("stocks_summary.png", "rb") as f:
    requests.post(
        WEBHOOK_URL,
        files={"file": f},
        data={"content": "📊 株価推移グラフ（終値＋MA5/MA20）"}
    )
