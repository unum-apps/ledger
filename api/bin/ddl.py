#!/usr/bin/env python

import relations
import relations_pymysql

import unum.apps.ledger

unifist = unum.apps.ledger.Base.SOURCE

source = relations_pymysql.Source(unifist, schema=unifist.replace('-', '_'), connection=False)

migrations = relations.Migrations()

migrations.generate(relations.models(unum.apps.ledger, unum.apps.ledger.Base))
migrations.convert(unifist)
