from app import app, start_bot_automatically

if __name__ == '__main__':
    start_bot_automatically()
    app.run(host='0.0.0.0', port=5000)
