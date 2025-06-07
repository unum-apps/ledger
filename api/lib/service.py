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
title: this Unum
channel: unifist-unum
description: Base for this Unum, tracks and records all that's allowed
help: |
  Welcome to this Unum. An Unum is a community Union born of American ideals: of the People, by the People,
  and for the People. We make our own Rules. We build our Infrastructure. We forge our own Destiny.

  I am the Ledger App, the base of this Unum. I track Entities, what Apps and Origins are installed. Here you can
  see all that and control how I talk to you, even what I'll call you.

  I am designed for self service. By simply asking for help, I am aware of you and I have assigned you awards
  to accomplish, mainly learning how to learn. Continue to ask for help, starting with help itself. Below shows how.

  While I am aware of you, I am not tracking everything you say. You need to join for that. Good luck on learning
  how.
commands:
- name: apps
  meme: '?'
  description: List all the installed Apps in this Unum
- name: origins
  meme: '?'
  description: List all the installed Apps in this Unum
- name: name
  description: Manages your overall name in this Unum
  examples:
  - meme: '?'
    description: See what you name is right now
  - meme: '!'
    args: '- Cool Person'
    description: Set you name to Cool Person
  usages:
  - name: current
    meme: '?'
    description: Show yout current name in the Unum
  - name: change
    meme: '!'
    description: Change your name in the Unum to {who}
    args:
    - name: who
      format: remainder
- name: talk
  description: Manage notifications in this Unum
  usages:
  - name: range
    meme: '!'
    description: I will reach out to you after {after} and before {before} each day (assumes ET)
    args:
    - name: after
      description: I will reach out to you after {after} each day
      format: duration
    - name: before
      description: I will reach out to you before {before} each day
      format: duration
  - name: ping
    meme: '!'
    description: I will ping you {kind}ly
    args:
    - name: kind
      description: Where I will ping you
      valids:
      - private: I will ping you in private messages
      - public: I will ping you in public channels
  - name: react
    meme: '!'
    description: I will react {noise}ly
    args:
    - name: noise
      description: How I will react to you
      valids:
      - loud: I will react with comments with you @'d
      - calm: I will react with comments with your name only
      - quiet: I will react with an eomji unless errors
      - silent: I will react only when errors
  - name: current
    meme: '?'
    description: Show current comms
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
