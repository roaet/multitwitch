import os

from paste.deploy import loadapp
from waitress import serve

if __name__ == "__main__":
    dev = bool(os.environ.get("DEV", False))
    port = int(os.environ.get("PORT", 5000 if not dev else 5001))
    conf_name = 'development' if dev else 'production'
    app = loadapp(
        'config:%s.ini' % conf_name, relative_to='../multitwitch_confs')
    serve(app, host='0.0.0.0', port=port)
