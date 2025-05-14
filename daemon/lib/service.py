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

    def has_herald(self, entity_id):
        """
        Checks to see if an enity has a Herald
        """

        return (
            unum_ledger.Entity.one(
                entity_id=entity_id,
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

        if not self.has_herald(act["entity_id"]):
            return

        act = unum_ledger.Act(**act).create()

        self.logger.info("act", extra={"act": {"id": act.id}})
        ACTS.observe(1)
        self.redis.xadd("ledger/act", fields={"act": json.dumps(act.export())})

    def do_join(self, instance):
        """
        Perform the join
        """

        unum_ledger.Herald(
            entity_id=instance["what"]["entity_id"],
            app_id=self.app.id,
            status="active"
        ).create()

        self.act(
            entity_id=instance["what"]["entity_id"],
            app_id=self.app.id,
            when=int(time.time()),
            what={
                "base": "message",
                "kind": "channel",
                "text": f"Welcome to the Ledger App {{entity:{instance['what']['entity_id']}}}!",
                "channel": self.app.meta__channel
            },
            meta=instance["meta"]
        )

    def do_apps(self, instance):
        """
        Perform the apps
        """

        text = "Current Apps are:"

        for app in unum_ledger.App.many():
            text += f"\n{app.who} - {app.meta__description} - {app.meta__channel} channel"

        self.act(
            entity_id=instance["what"]["entity_id"],
            app_id=self.app.id,
            when=int(time.time()),
            what={
                "base": "message",
                "kind": "channel",
                "text": text,
                "channel": self.app.meta__channel
            },
            meta=instance["meta"]
        )

    def do_origins(self, instance):
        """
        Perform the origins
        """

        text = "Current Origins are:"

        for origin in unum_ledger.Origin.many():
            text += f"\n{origin.who} - {origin.meta__description} - {origin.meta__channel} channel"

        self.act(
            entity_id=instance["what"]["entity_id"],
            app_id=self.app.id,
            when=int(time.time()),
            what={
                "base": "message",
                "kind": "channel",
                "text": text,
                "channel": self.app.meta__channel
            },
            meta=instance["meta"]
        )

    def do_who(self, instance):
        """
        Perform the who
        """

        if instance["what"]["command"].get("args"):
            unum_ledger.Entity.one(instance["what"]["entity_id"]).set(who=" ".join(instance["what"]["command"]["args"])).update()

        who = unum_ledger.Entity.one(instance["what"]["entity_id"]).who

        text = f"{{entity:{instance['what']['entity_id']}}}, your name is {who}."

        self.act(
            entity_id=instance["what"]["entity_id"],
            app_id=self.app.id,
            when=int(time.time()),
            what={
                "base": "message",
                "kind": "channel",
                "text": text,
                "channel": self.app.meta__channel
            },
            meta=instance["meta"]
        )

    def do_command(self, instance):
        """
        Perform the who
        """

        name = instance["what"].get("command", {}).get("name")

        if name != "join" and not self.has_herald(instance["what"].get("entity_id")):
            return

        if name == "join":
            self.do_join(instance)
        elif name == "apps":
            self.do_apps(instance)
        elif name == "origins":
            self.do_origins(instance)
        elif name == "who":
            self.do_who(instance)

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

            if instance["what"].get("command", {}).get("app") == WHO:
                self.do_command(instance)

            self.redis.xack("ledger/fact", self.group, message[0][1][0][0])

    def run(self):
        """
        Main loop with sleep
        """

        prometheus_client.start_http_server(80)

        while True:

            self.process()
