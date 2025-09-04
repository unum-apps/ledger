"""
Module for the Daemon
"""

# pylint: disable=no-self-use,too-many-locals

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
- name: river
  description: Manage Rivers in this Unum
  help: |
    This creates a river, which is like a stream, in an Unum.
  examples:
  - meme: '?'
    description: List all current rivers
  - meme: '!'
    args: |
      dude
      ```yaml
        select:
        - text
        - entity_id
        where:
          channel: unifist-unum
      ```
    description: Create a River for the ledger channel for person and text
  usages:
  - name: create
    meme: '!'
    description: Create a River named {who} with {what}
    args:
    - name: who
      description: Name of the River
    - name: what
      description: The query for the River
      format: remainder
  - name: list
    meme: '?'
    description: List all Rivers
- name: twain
  description: Manage River Twains in this Unum
  help: |
    This creates a Twain, which is like a consumer, in an Unum.
  examples:
  - meme: '?'
    description: List all current twains
  - meme: '!'
    args: dude sweet
    description: Create a Twain for the ledger channel for person and text
  usages:
  - name: create
    meme: '!'
    description: Create a River named {who} with {what}
    args:
    - name: river
      description: Name of the River
    - name: twain
      description: The Twain for the River
  - name: list
    meme: '?'
    description: List all River Twains
- name: mark
  description: Read from River Twains in this Unum
  help: |
    This uses a Twain to get latest from a River
  examples:
  - meme: '!'
    args: dude sweet
    description: Get all the most recent from the sweet Twain from the dude River
  - meme: '!'
    args: dude sweet 5
    description: Get the 5 most recents since last from the sweet Twain
  usages:
  - name: all
    meme: '!'
    description: Get all the most recents from the {river} River {twain} Twain
    args:
    - name: river
    - name: twain
  - name: some
    meme: '!'
    description: Get the {limit} most recents from the {river} River {twain} Twain
    args:
    - name: river
    - name: twain
    - name: limit
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
        Handles the communication
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

    def command_river(self, instance):
        """
        Manages Rivers, a sectional stream of Facts
        """

        entity_id = instance["what"]["entity_id"]
        usage = instance["what"]["usage"]
        values = instance["what"].get("values", {})
        base = "statement"
        meme = "*"
        text = ""

        if usage == "list":

            text = "Current rivers are:"

            for river in unum_ledger.River.many():
                text += f"\n- {river.who}"

        elif usage == "create":

            who = values["who"]
            what = yaml.safe_load(values["what"].split("```yaml")[-1].split("```")[0])

            river = self.journal_change("create", unum_ledger.River(who=who, what=what))

            text = f"Created river: {who}"

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

    def command_twain(self, instance):
        """
        Manages Twains, which indicate read positions on Rivers
        """

        entity_id = instance["what"]["entity_id"]
        usage = instance["what"]["usage"]
        values = instance["what"].get("values", {})
        base = "statement"
        meme = "*"
        text = ""

        if usage == "list":

            text = "Current twains are:"

            for twain in unum_ledger.Twain.many():
                text += f"\n- {twain.river.who} {twain.who}"

        elif usage == "create":

            river_who = values["river"]
            twain_who = values["twain"]

            river = unum_ledger.River.one(who=river_who).retrieve(False)

            if not river:
                text = f"River: {river_who} not found"
            else:
                twain = self.journal_change("create", unum_ledger.Twain(river_id=river.id, who=twain_who))
                text = f"Created Twain: {river_who} {twain_who}"

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

    def command_mark(self, instance):
        """
        Reads a River using the Twain and updates the Twain
        """

        entity_id = instance["what"]["entity_id"]
        usage = instance["what"]["usage"]
        values = instance["what"].get("values", {})
        base = "statement"
        meme = "*"
        text = ""
        data = {}

        river_who = values["river"]
        twain_who = values["twain"]

        twain = unum_ledger.Twain.one(river__who=river_who, who=twain_who).retrieve(False)

        if not twain:
            text = f"Twain {twain_who} not found"
        elif not twain.river.what__select:
            text = f"River {twain.river.who} select not found"
        elif not twain.river.what__where:
            text = f"River {twain.river.who} where not found"
        else:

            facts = unum_ledger.Fact.many(id__gt=twain.what__id or 0, **twain.river.what__where)

            if usage == "some":
                limit = values["limit"]
                facts = facts.limit(limit)

            marks = []

            fact = None

            for fact in facts:
                mark = {}
                for key, value in twain.river__what__select.items():
                    mark[key] = fact[value]
                marks.append(mark)
            data["marks"] = marks

            if fact:
                self.journal_change("update", twain, {"what__id": fact.id})

        self.create_act(
            entity_id=entity_id,
            app_id=self.app.id,
            when=int(time.time()),
            what={
                "base": base,
                "meme": meme,
                "text": text,
                "data": data
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
        elif name == "river":
            self.command_river(instance)
        elif name == "twain":
            self.command_twain(instance)
        elif name == "mark":
            self.command_mark(instance)

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
