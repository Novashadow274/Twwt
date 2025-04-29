# main.py
from threading import Thread
from server import app
from scheduler import start_bot

def run_flask():
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    start_bot()
