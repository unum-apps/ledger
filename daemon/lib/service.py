"""
Module for the Daemon
"""

# pylint: disable=no-self-use

import os
import micro_logger
import json
import redis

import relations_rest

import prometheus_client

import unum.apps.ledger

PROCESS = prometheus_client.Gauge("process_seconds", "Time to complete a processing task")
ORIGINS = prometheus_client.Summary("origins_processed", "Origins processed")

class Daemon: # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """
    Daemon class
    """

    def __init__(self):

        self.name = "ledger-daemon"
        self.unifist = unum.apps.ledger.Base.SOURCE
        self.group = f"daemon-{self.unifist}"
        self.group_id = os.environ["K8S_POD"]

        self.sleep = int(os.environ.get("SLEEP", 5))

        self.logger = micro_logger.getLogger(self.name)

        self.source = relations_rest.Source("ledger-app-unum", url=f"http://api.{self.unifist}")

        self.redis = redis.Redis(host=f'redis.{self.unifist}', encoding="utf-8", decode_responses=True)

        if (
            not self.redis.exists("ledger/origin") or
            self.group  not in [group["name"] for group in self.redis.xinfo_groups("ledger/origin")]
        ):
            self.redis.xgroup_create("ledger/origin", self.group, mkstream=True)

    @PROCESS.time()
    def process(self):
        """
        Reads people off the queue and logs them
        """

        message = self.redis.xreadgroup(self.group, self.group_id, {"ledger/origin": ">"}, count=1, block=1000*self.sleep)

        if not message or "origin" not in message[0][1][0][1]:
            return

        instance = json.loads(message[0][1][0][1]["origin"])
        self.logger.info("origin", extra={"origin": instance})
        ORIGINS.observe(1)

        self.redis.xack("ledger/origin", self.group, message[0][1][0][0])

    def run(self):
        """
        Main loop with sleep
        """

        prometheus_client.start_http_server(80)

        while True:

            self.process()
