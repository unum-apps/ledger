#!/usr/bin/env python

import relations
import relations_pymysql

import unum_ledger

unifist = unum_ledger.Base.SOURCE

source = relations_pymysql.Source(unifist, schema=unifist.replace('-', '_'), connection=False)

migrations = relations.Migrations()

migrations.generate(relations.models(unum_ledger, unum_ledger.Base))
migrations.convert(unifist)
