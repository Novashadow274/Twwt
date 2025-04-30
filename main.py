from flask import Flask
from scheduler import start_scraping

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running."

if __name__ == '__main__':
    start_scraping()
    app.run(host="0.0.0.0", port=10000)
