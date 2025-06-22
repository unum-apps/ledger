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

import unum_base
import unum_ledger

WHO = "ledger"
META = """
title: this Unum
channel: unifist-unum
description: Base for this Unum, tracks and records all that's allowed
help: |
  Welcome to this Unum. An Unum is like a community union, a group of people commited to working together to help each other.

  I am the Ledger App, the base of this Unum. I track Entities, what Apps and Origins are installed. Here you can see all that and control how I talk to you, even what I'll call you.

  While I am aware of you, I am not tracking everything you say. You need to join for that. Good luck on learning how.
commands:
- name: origins
  meme: '?'
  description: List all the installed Apps in this Unum
  help: |
    An Origin is software we wrote that listens and speaks to us through an outside application. For example, the Discord Origin allows us to listen in on a Discord server and sends messages from Apps to those Users.

    Origins are more like mouthpieces than brains if that helps.
- name: apps
  meme: '?'
  description: List all the installed Apps in this Unum
  help: |
    An App is software we wrote that interacts with us. For example, the Feelz App asks us how we're doing and records it.

    Apps are very much like the brains of Unum.
- name: name
  description: Manages your overall name in this Unum
  help: |
    The name I call you by can be controlled here. Totally up to you.
  examples:
  - meme: '?'
    description: See what you name is right now
  - meme: '!'
    args: Cool Person
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
  help: |
    I can interact with you a variety of ways and it's important you control how I do so.

    I will only reach out to between certain times of the day. You determine how much time I should wait in the morning or when is too late at night. You set this right now by the amount of time from or before midnight.

    When I respond to you, I can give you a whole message of what heppened, respond with an emoji, or only let you know if something went wrong.

    I can also only reach out to you privately vs. in a channel. It's up to you.
  examples:
  - meme: '?'
    description: See how I'm talking to you now
  - meme: '!'
    args: 10h 16h
    description: Only let me reach out to you between 10am and 6pm
  - meme: '!'
    args: private
    description: Only let me reach out to you via direct messages
  - meme: '!'
    args: calm
    description: Only let me react to you with your name, no @
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
      - quiet: I will react with an emoji unless errors
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

    unum_source = unum_base.AppSource(app.logger, app.redis)

    if not unum_ledger.Unum.one(who="self").retrieve(False):
        unum_source.journal_change("create", unum_ledger.Unum(who="self"))

    unum_app = unum_ledger.App.one(who=WHO).retrieve(False)

    if not unum_app:
        unum_app = unum_source.journal_change("create", unum_ledger.App(who=WHO))

    unum_source.journal_change("update", unum_app, {"meta": yaml.safe_load(META)})

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
