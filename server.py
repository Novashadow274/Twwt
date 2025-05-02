application.run_webhook(
    listen="0.0.0.0",
    port=int(os.environ["PORT"]),
    url_path=config.BOT_TOKEN,
    webhook_url=f"{os.environ['RENDER_APP_URL']}/{config.BOT_TOKEN}"
)
