"""
Module for the OPenGUI API
"""

# pylint: disable=no-self-use

import json
import yaml

import micro_logger

import flask
import flask_restx
import prometheus_flask_exporter
import redis

import relations
import relations_pymysql
import relations_restx

import unum_ledger

WHO = "ledger"
META = """
title: the Ledger App
channel: unifist-unum
description: Base for this Unum, tracks and records all that's allowed
commands:
- name: apps
  description: List all the installed Apps in this Unum
- name: origins
  description: List all the installed Apps in this Unum
- name: who
  description: Manages your overall name in the Unum
  usages:
  - description: Show yout overall namein the Unum
  - description: Change your overall name in the Unum to {who}
    args:
    - name: who
      format: remainder
"""

NAME = f"{WHO}-api"

metrics = prometheus_flask_exporter.PrometheusMetrics.for_app_factory()

def build():
    """
    Builds the Flask App
    """

    import service # pylint: disable=import-outside-toplevel

    app = flask.Flask(service.NAME)

    app.logger = micro_logger.getLogger(service.NAME)
    app.unifist = unum_ledger.Base.SOURCE
    app.schema = app.unifist.replace('-', '_')

    metrics.init_app(app)

    api = flask_restx.Api(app)

    app.redis = redis.Redis(host=f'redis.{app.unifist}', encoding="utf-8", decode_responses=True)

    with open("/opt/service/secret/mysql.json", "r") as mysql_file:
        app.source = relations_pymysql.Source(
            app.unifist, schema=app.schema, autocommit=True, **json.loads(mysql_file.read())
        )

    if not unum_ledger.Unum.one(who="self").retrieve(False):
        unum_ledger.Unum(who="self").create()

    if not unum_ledger.App.one(who=WHO).retrieve(False):
        unum_ledger.App(who=WHO).create()

    unum_ledger.App.one(who=WHO).set(meta=yaml.safe_load(META)).update()

    def ping():
        app.source.connection.ping(True)

    app.before_request(ping)

    api.add_resource(Health, '/health')

    relations_restx.attach(api, service, relations.models(unum_ledger, unum_ledger.Base))

    return app

class Health(flask_restx.Resource):
    """
    Class for Health checks
    """

    def get(self):
        """
        Just return ok
        """
        return {"message": "OK"}
