from flask import Flask
import threading
import forwarder

app = Flask(__name__)

@app.route('/')
def home():
    return "Matrix → Telegram Forwarder is running!"

if __name__ == "__main__":
    # Запускаем форвардер в отдельном потоке
    t = threading.Thread(target=lambda: asyncio.run(forwarder.matrix_poller()), daemon=True)
    t.start()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
