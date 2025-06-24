import unittest
import unittest.mock

import relations
import relations.unittest

import service
import unum_ledger

import os
import sys

if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

class Testrestx(relations.unittest.TestCase):

    @unittest.mock.patch.dict('os.environ', {"LOG_LEVEL": "INFO"})
    @unittest.mock.patch('service.open', new_callable=unittest.mock.mock_open, read_data='{"host": "%s", "user": "root", "password": "local"}' % os.environ["MYSQL_HOST"])
    def setUp(self, mock_open):

        self.app = service.build()
        self.api = self.app.test_client()

        cursor = self.app.source.connection.cursor()

        migrations = relations.Migrations()

        cursor.execute("CREATE DATABASE IF NOT EXISTS `ledger`")

        migrations.load(self.app.source.name, "definition.sql")

    def tearDown(self):

        cursor = self.app.source.connection.cursor()

        cursor.execute("DROP DATABASE IF EXISTS `ledger`")


class TestAPI(Testrestx):

    @unittest.mock.patch.dict('os.environ', {"LOG_LEVEL": "INFO"})
    @unittest.mock.patch('service.open', new_callable=unittest.mock.mock_open, read_data='{"host": "%s", "user": "root", "password": "local"}' % os.environ["MYSQL_HOST"])
    def test_build(self, mock_open):

        app = service.build()

        self.assertEqual(app.name, "ledger-api")
        self.assertEqual(app.unifist, "ledger")
        self.assertEqual(app.schema, "ledger")

    def test_migrations(self):

        migrations = relations.Migrations()

        cursor = self.app.source.connection.cursor()

        for stamp, pair in migrations.list(self.app.source.name).items():

            cursor.execute("DROP DATABASE IF EXISTS `ledger`")
            cursor.execute("CREATE DATABASE IF NOT EXISTS `ledger`")

            try:
                migrations.load(self.app.source.name, pair["definition"])
                migrations.load(self.app.source.name, pair["migration"])
            except Exception as exception:
                print(stamp)
                raise exception

class TestHealth(Testrestx):

    def test_get(self):

        self.assertStatusValue(self.api.get("/health"), 200, "message", "OK")
