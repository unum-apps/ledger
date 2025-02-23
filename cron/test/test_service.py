import unittest
import unittest.mock
import micro_logger_unittest
import relations.unittest

import json

import service
import unum.apps.ledger

class MockRedis:

    host = None
    queue = None

    def __init__(self, host, **kwargs):

        self.host = host
        self.queue = {}

    def xadd(self, stream, fields):

        self.queue.setdefault(stream, [])
        self.queue[stream].append({"fields": fields})

class TestCron(micro_logger_unittest.TestCase):

    maxDiff = None

    @unittest.mock.patch.dict('os.environ', {"LOG_LEVEL": "INFO", "UNIFIST_UNUM": "unit"})
    @unittest.mock.patch("micro_logger.getLogger", micro_logger_unittest.MockLogger)
    @unittest.mock.patch('relations_rest.Source', relations.unittest.MockSource)
    @unittest.mock.patch('redis.Redis', MockRedis)
    def setUp(self):

        self.cron = service.Cron()

    @unittest.mock.patch.dict('os.environ', {"LOG_LEVEL": "INFO", "UNIFIST_UNUM": "test"})
    @unittest.mock.patch("micro_logger.getLogger", micro_logger_unittest.MockLogger)
    @unittest.mock.patch('relations_rest.Source', relations.unittest.MockSource)
    @unittest.mock.patch('redis.Redis', MockRedis)
    def test___init__(self):

        cron = service.Cron()

        self.assertEqual(cron.name, "ledger-cron")
        self.assertEqual(cron.unifist, "ledger-app-unum")
        self.assertEqual(cron.unum, "test")
        self.assertEqual(cron.namespace, "ledger-app-unum-test")

        self.assertEqual(cron.logger.name, "ledger-cron")

        self.assertIsInstance(relations.source("ledger-app-unum"), relations.unittest.MockSource)

        self.assertEqual(cron.redis.host, "redis.ledger-app-unum-test")

    def test_process(self):

        origin = unum.apps.ledger.Origin("Tom").create()

        self.cron.process()

        self.assertLogged(self.cron.logger, "info", "origin", extra={"origin": origin.export()})

        self.assertEqual(len(self.cron.redis.queue['ledger/origin']), 1)
        self.assertEqual(json.loads(self.cron.redis.queue['ledger/origin'][0]["fields"]["origin"]), origin.export())

    @unittest.mock.patch('prometheus_client.push_to_gateway')
    def test_run(self, mock_push):

        self.cron.run()

        #mock_push.assert_called_once_with("push.prometheus:9091", "ledger/cron", registry=service.REGISTRY)
