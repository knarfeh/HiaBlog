#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
from flask_script import Manager, Server
from app.hia import app

sys.path.append(os.path.abspath(os.path.dirname(__file__)))


manager = Manager(app)

# Turn os debugger by default and reloader
manager.add_command("runserver", Server(
    use_debugger=True,
    use_reloader=True,
    host='0.0.0.0',
    port=5001
))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=False)
