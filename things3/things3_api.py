#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Simple read-only Things 3 Web Serivce."""

from __future__ import print_function

__author__ = "Alexander Willner"
__copyright__ = "Copyright 2020 Alexander Willner"
__credits__ = ["Alexander Willner"]
__license__ = "Apache License 2.0"
__version__ = "2.5.2"
__maintainer__ = "Alexander Willner"
__email__ = "alex@willner.ws"
__status__ = "Development"

import sys
from os import getcwd
import json
from flask import Flask
from flask import Response
from flask import request
from werkzeug.serving import make_server
from things3.things3 import Things3


class Things3API():
    """API Wrapper for the simple read-only API for Things 3."""

    PATH = getcwd() + '/resources/'
    things3 = None
    test_mode = "task"
    host = 'localhost'
    port = 15000

    def on_get(self, url):
        """Handles other GET requests"""
        status = 200
        filename = self.PATH + url
        content_type = 'application/json'
        if filename.endswith('css'):
            content_type = 'text/css'
        if filename.endswith('html'):
            content_type = 'text/html'
        if filename.endswith('js'):
            content_type = 'text/javascript'
        if filename.endswith('png'):
            content_type = 'image/png'
        if filename.endswith('jpg'):
            content_type = 'image/jpeg'
        if filename.endswith('ico'):
            content_type = 'image/x-ico'
        try:
            with open(filename, 'rb') as source:
                data = source.read()
        except FileNotFoundError:
            data = 'not found'
            content_type = 'text'
            status = 404
        return Response(response=data,
                        content_type=content_type,
                        status=status)

    def mode_selector(self):
        """Switch between project and task mode"""
        try:
            mode = request.args.get('mode')
        except RuntimeError:
            mode = 'task'
        if mode == "project" or self.test_mode == "project":
            self.things3.mode_project()

    def api(self, command):
        """Return database as JSON strings."""
        if command in self.things3.functions:
            func = self.things3.functions[command]
            self.mode_selector()
            data = func(self.things3)
            self.things3.mode_task()
            data = json.dumps(data)
            return Response(response=data, content_type='application/json')

        data = json.dumps(self.things3.get_not_implemented())
        return Response(response=data,
                        content_type='application/json',
                        status=404)

    def api_filter(self, mode, uuid):
        """Filter view by specific modifiers"""
        if mode == "area" and uuid != "":
            self.things3.filter = f"TASK.area = '{uuid}' AND"
        if mode == "project" and uuid != "":
            self.things3.filter = f"""
                (TASK.project = '{uuid}' OR HEADING.project = '{uuid}') AND
                """
        return Response(status=200)

    def api_filter_reset(self):
        """Reset filter modifiers"""
        self.things3.filter = ""
        return Response(status=200)

    def __init__(self, database=None, host=None, port=None):
        cfg = Things3.get_from_config(Things3.config, host, 'KANBANVIEW_HOST')
        self.host = cfg if cfg else self.host
        cfg = Things3.get_from_config(Things3.config, port, 'KANBANVIEW_PORT')
        self.port = cfg if cfg else self.port

        self.things3 = Things3(database=database)
        self.flask = Flask(__name__)
        self.flask.add_url_rule('/api/<command>', view_func=self.api)
        self.flask.add_url_rule(
            '/api/filter/<mode>/<uuid>', view_func=self.api_filter)
        self.flask.add_url_rule('/api/filter/reset',
                                view_func=self.api_filter_reset)
        self.flask.add_url_rule('/<url>', view_func=self.on_get)
        self.flask.app_context().push()
        self.flask_context = None

    def main(self):
        """"Main function."""
        print(f"Serving at http://{self.host}:{self.port} ...")

        try:
            self.flask_context = make_server(
                self.host, self.port, self.flask, True)
            self.flask_context.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down...")
            sys.exit(0)


def main():
    """Main entry point for CLI installation"""
    Things3API().main()


if __name__ == "__main__":
    main()
