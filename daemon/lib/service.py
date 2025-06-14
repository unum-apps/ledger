"""
Module for the Daemon
"""

# pylint: disable=no-self-use

import os
import time
import micro_logger
import json
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

class Daemon(unum_base.Source, unum_base.AppSource): # pylint: disable=too-few-public-methods,too-many-instance-attributes
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

        self.app = unum_ledger.App.one(who=WHO).retrieve()

        self.redis = redis.Redis(host=f'redis.{self.unifist}', encoding="utf-8", decode_responses=True)

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
        values = instance["what"].get("values",{})
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
