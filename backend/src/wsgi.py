from . import create_app, socketio_app
import os

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get('FLASK_RUN_PORT', 9090))
    socketio_app.run(app, host='0.0.0.0', port=port)