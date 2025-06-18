"""
Module for the Subnet Queue
"""

# pylint: disable=no-self-use

import json
import redis

import micro_logger
import relations_rest

import unum_ledger

import prometheus_client

REGISTRY = prometheus_client.CollectorRegistry()

PROCESS = prometheus_client.Gauge("process_seconds", "Time to complete a processing task", registry=REGISTRY)
ORIGINS = prometheus_client.Summary("origins_processed", "Origins processed", registry=REGISTRY)

class Cron(unum_base.Source, unum_base.AppSource)): # pylint: disable=too-few-public-methods
    """
    Cron class to run the processing
    """

    def __init__(self):

        self.name = "ledger-cron"
        self.unifist = unum_ledger.Base.SOURCE

        self.logger = micro_logger.getLogger(self.name)

        self.source = relations_rest.Source(self.unifist, url=f"http://api.{self.unifist}")

        self.redis = redis.Redis(host=f'redis.{self.unifist}', encoding="utf-8", decode_responses=True)

    @PROCESS.time()
    def process(self):
        """
        Loads subnets and pushes onto the queue
        """

        for origin in unum_ledger.Origin.many():
            self.logger.info("origin", extra={"origin": origin.export()})
            ORIGINS.observe(1)
            self.redis.xadd("ledger/origin", fields={"origin": json.dumps(origin.export())})

    def run(self):
        """
        Runs through s process
        """

        self.process()

        #prometheus_client.push_to_gateway("push.prometheus:9091", "ledger/cron", registry=REGISTRY)
