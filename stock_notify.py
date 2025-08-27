import yfinance as yf
import requests

# Discord Webhook URL
WEBHOOK_URL = "https://discordapp.com/api/webhooks/1410244506070024242/fmdj2K7PgCvSR1s_ddXj2opzeMw_ndJa0SCHCBFEa7Y0TKJggD4TM_UduQ7Qj15MrNP_"

# 株価データ取得
data = yf.Ticker("9984.T").history(period="1mo")  # 過去1ヶ月
data['MA5'] = data['Close'].rolling(window=5).mean()
data['MA20'] = data['Close'].rolling(window=20).mean()

# 最新データ
latest = data.iloc[-1]
message = (
    f"📈 ソフトバンク株 9984.T\n"
    f"終値: {latest['Close']:.2f} 円\n"
    f"MA5: {latest['MA5']:.2f}\n"
    f"MA20: {latest['MA20']:.2f}"
)

# Discordに送信
requests.post(WEBHOOK_URL, json={"content": message})