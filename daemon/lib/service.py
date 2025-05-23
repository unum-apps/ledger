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

import unum_ledger

PROCESS = prometheus_client.Gauge("process_seconds", "Time to complete a processing task")
ORIGINS = prometheus_client.Summary("origins_processed", "Origins processed")
FACTS = prometheus_client.Summary("facts_processed", "Facts processed")
ACTS = prometheus_client.Summary("acts_processed", "Acts processed")

WHO = "ledger"
NAME = f"{WHO}-daemon"

class Daemon: # pylint: disable=too-few-public-methods,too-many-instance-attributes
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

    def is_active(self, entity_id):
        """
        Checks to see if an enity has a Herald
        """

        return (
            unum_ledger.Entity.one(
                id=entity_id,
                status="active"
            ).retrieve(False) is not None
            and
            unum_ledger.Herald.one(
                entity_id=entity_id,
                app_id=self.app.id,
                status="active"
            ).retrieve(False) is not None
        )

    def act(self, **act):
        """
        Creates an act if needed
        """

        if not self.is_active(act["entity_id"]):
            return

        act = unum_ledger.Act(**act).create()

        self.logger.info("act", extra={"act": {"id": act.id}})
        ACTS.observe(1)
        self.redis.xadd("ledger/act", fields={"act": json.dumps(act.export())})

    def decode_time(self, arg):
        """
        Decodes 3d2h3m format to seconds

        """

        seconds = 0
        current = ""

        for letter in arg:

            if '0' <= letter and letter <= '9':
                current += letter
            elif current and letter == 'd':
                seconds += int(current) * 24*60*60
                current = ""
            elif current and letter == 'h':
                seconds += int(current) * 60*60
                current = ""
            elif current and letter == 'm':
                seconds += int(current) * 60
                current = ""

        return seconds

    def encode_time(self, seconds):
        """
        Encodes seconds to 3d2h3m format
        """

        # Start with a blank string

        arg = ""

        # Determine and peel off the days, hours, and minutes

        days = int(seconds/(24*60*60))
        seconds -= days * 24*60*60
        hours = int(seconds /(60*60))
        seconds -= hours * 60*60
        mins = int(seconds/(60))

        # If there's a value, add it with its letter

        if days:
            arg += f"{days}d"

        if hours:
            arg += f"{hours}h"

        if mins:
            arg += f"{mins}m"

        return arg

    def command_apps(self, instance):
        """
        Perform the apps
        """

        text = "Current Apps are:"

        for app in unum_ledger.App.many():
            text += f"\n- **{app.who}** - *{app.meta__description}* - {{channel:{app.meta__channel}}}"

        self.act(
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

        self.act(
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

        if usage == "change":
            meme = "+"
            base = "reaction"
            unum_ledger.Entity.one(entity_id).set(who=values["who"]).update()

        who = unum_ledger.Entity.one(entity_id).who

        text = f"your name is {who}."

        self.act(
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
        change = False
        base = "statement"
        meme = "*"

        entity = unum_ledger.Entity.one(entity_id)

        # Defaults

        if not entity.meta__talk:
            entity.meta__talk = {
                "after": self.decode_time("8h"),
                "before": self.decode_time("20h"),
                "kind": "public",
                "noise": "loud"
            }
            change = True

        # Updates

        if values:
            entity.meta["talk"].update(values)
            base = "reaction"
            meme = "+"
            change = True

        # Change if needed

        if change:
            entity.update()

        after = self.encode_time(entity.meta__talk__after)
        before = self.encode_time(entity.meta__talk__before)
        kind = entity.meta__talk__kind
        noise = entity.meta__talk__noise

        text = f"I will {kind}ly ping and react {noise}ly to you after {after} and before {before} each day"

        self.act(
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

    def do_feats(self, instance):
        """
        Complete feats if so
        """

        entity_id = instance["what"]["entity_id"]

        for feat in unum_ledger.Feat.many(entity_id=entity_id, status__in=["requested", "accepted"]):

            # Oh yes this is horribly inefficient but it's like no code

            if unum_ledger.Fact.one(id=instance["id"], **feat.what).retrieve(False):
                feat.status = "completed"
                feat.update()

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
                    WHO in instance["what"].get("apps", []) and
                ):
                    self.do_command(instance)

                self.do_feats(instance)

            self.redis.xack("ledger/fact", self.group, message[0][1][0][0])

    def run(self):
        """
        Main loop with sleep
        """

        prometheus_client.start_http_server(80)

        while True:

            self.process()
