"""
Module for the Daemon
"""

# pylint: disable=no-self-use

import os
import time
import micro_logger
import json
import yaml
import redis

import relations_rest

import prometheus_client

import unum_base
import unum_ledger

PROCESS = prometheus_client.Gauge("process_seconds", "Time to complete a processing task")
ORIGINS = prometheus_client.Summary("origins_processed", "Origins processed")
FACTS = prometheus_client.Summary("facts_processed", "Facts processed")
ACTS = prometheus_client.Summary("acts_processed", "Acts processed")

WHO = "ledger"
NAME = f"{WHO}-daemon"
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

class Daemon(unum_base.AppSource): # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """
    Daemon class
    """

    def __init__(self):

        self.name = self.group = NAME
        self.unifist = unum_ledger.Base.SOURCE
        self.group_id = os.environ["K8S_POD"]

        self.sleep = int(os.environ.get("SLEEP", 5))

        self.logger = micro_logger.getLogger(self.name)

        self.source = relations_rest.Source(self.unifist, url=f"http://api.{self.unifist}")

        self.redis = redis.Redis(host=f'redis.{self.unifist}', encoding="utf-8", decode_responses=True)

        if not unum_ledger.Unum.one(who="self").retrieve(False):
            self.journal_change("create", unum_ledger.Unum(who="self"))

        self.app = unum_ledger.App.one(who=WHO).retrieve(False)

        if not self.app:
            self.app = self.journal_change("create", unum_ledger.App(who=WHO))

        self.journal_change("update", self.app, {"meta": yaml.safe_load(META)})

        if (
            not self.redis.exists("ledger/origin") or
            self.group not in [group["name"] for group in self.redis.xinfo_groups("ledger/origin")]
        ):
            self.redis.xgroup_create("ledger/origin", self.group, mkstream=True)

        if (
            not self.redis.exists("ledger/fact") or
            self.group not in [group["name"] for group in self.redis.xinfo_groups("ledger/fact")]
        ):
            self.redis.xgroup_create("ledger/fact", self.group, mkstream=True)

    def command_apps(self, instance):
        """
        Perform the apps
        """

        text = "Current Apps are:"

        for app in unum_ledger.App.many():
            text += f"\n- **{app.who}** - *{app.meta__description}* - {{channel:{app.meta__channel}}}"

        self.create_act(
            entity_id=instance["what"]["entity_id"],
            app_id=self.app.id,
            when=int(time.time()),
            what={
                "base": "statement",
                "text": text
            },
            meta={"ancestor": instance["meta"]}
        )

    def command_origins(self, instance):
        """
        Perform the origins
        """

        text = "Current Origins are:"

        for origin in unum_ledger.Origin.many():
            text += f"\n- **{origin.who}** - *{origin.meta__description}* - {{channel:{origin.meta__channel}}}"

        self.create_act(
            entity_id=instance["what"]["entity_id"],
            app_id=self.app.id,
            when=int(time.time()),
            what={
                "base": "statement",
                "text": text
            },
            meta={"ancestor": instance["meta"]}
        )

    def command_name(self, instance):
        """
        Perform the who
        """

        entity_id = instance["what"]["entity_id"]
        usage = instance["what"]["usage"]
        values = instance["what"].get("values", {})
        base = "statement"
        meme = "*"

        entity = unum_ledger.Entity.one(entity_id)

        if usage == "change":
            meme = "+"
            base = "reaction"

            self.journal_change("update", entity, {"who": values["who"]})

        who = entity.who

        text = f"your name is {who}."

        self.create_act(
            entity_id=entity_id,
            app_id=self.app.id,
            when=int(time.time()),
            what={
                "meme": meme,
                "base": base,
                "text": text
            },
            meta={"ancestor": instance["meta"]}
        )

    def command_talk(self, instance):
        """
        Joins the Unum, Ledger, and Discord Origin
        """

        entity_id = instance["what"]["entity_id"]
        values = instance["what"].get("values", {})
        change = {}
        base = "statement"
        meme = "*"

        entity = unum_ledger.Entity.one(entity_id)

        # Defaults

        if not entity.meta__talk:
            change["meta__talk"] = {
                "after": self.decode_time("8h"),
                "before": self.decode_time("20h"),
                "kind": "public",
                "noise": "loud"
            }

        # Updates

        if values:
            for key, value in values.items():
                change[f"meta__talk__{key}"] = value
            base = "reaction"
            meme = "+"

        # Change if needed

        if change:
            self.journal_change("update", entity, change=change)

        after = self.encode_time(entity.meta__talk__after)
        before = self.encode_time(entity.meta__talk__before)
        kind = entity.meta__talk__kind
        noise = entity.meta__talk__noise

        text = f"I will {kind}ly ping and react {noise}ly to you after {after} and before {before} each day"

        self.create_act(
            entity_id=entity_id,
            app_id=self.app.id,
            when=int(time.time()),
            what={
                "base": base,
                "meme": meme,
                "text": text
            },
            meta={"ancestor": instance["meta"]}
        )

    def do_command(self, instance):
        """
        Perform the who
        """

        name = instance["what"]["command"]

        if name == "apps":
            self.command_apps(instance)
        elif name == "origins":
            self.command_origins(instance)
        elif name == "name":
            self.command_name(instance)
        elif name == "talk":
            self.command_talk(instance)


    @PROCESS.time()
    def process(self):
        """
        Reads people off the queue and logs them
        """

        message = self.redis.xreadgroup(self.group, self.group_id, {
            "ledger/origin": ">",
            "ledger/fact": ">"
        }, count=1, block=1000*self.sleep)

        if not message:
            return

        if "origin" in message[0][1][0][1]:

            instance = json.loads(message[0][1][0][1]["origin"])
            self.logger.info("origin", extra={"origin": instance})
            ORIGINS.observe(1)

            self.redis.xack("ledger/origin", self.group, message[0][1][0][0])

        elif "fact" in message[0][1][0][1]:

            instance = json.loads(message[0][1][0][1]["fact"])
            self.logger.info("fact", extra={"fact": instance})
            FACTS.observe(1)

            if (
                self.is_active(instance["what"].get("entity_id")) and
                not instance["what"].get("error") and
                not instance["what"].get("errors")
            ):

                if (
                    instance["what"].get("command") and
                    WHO in instance["what"].get("apps", [])
                ):
                    self.do_command(instance)

            self.redis.xack("ledger/fact", self.group, message[0][1][0][0])

    def run(self):
        """
        Main loop with sleep
        """

        prometheus_client.start_http_server(80)

        while True:

            self.process()
