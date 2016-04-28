#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from flask_script import Manager, Server

from hia import create_app, db

app = create_app(os.getenv('config') or 'default')
manager = Manager(app)

# Turn os debugger by default and reloader
manager.add_command("runserver", Server(
    use_debugger=True,
    use_reloader=True,
    host='localhost',
    port=5001
))

if __name__ == "__main__":
    manager.run()
