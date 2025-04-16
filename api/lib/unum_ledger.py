"""
Contains the Models for ledger
"""

import relations

class Base(relations.Model):
    """
    Base class for ledger models
    """

    SOURCE = "ledger"

class Unum(Base):
    """
    Stores Unums. For now this one. Others will interface later.
    """

    id = int
    who = str   # unique way to identify
    meta = dict # any special weird data

class Entity(Base):
    """
    Entity is a person. 
    """

    id = int
    unum_id = int   # The Unum this entity is a part of
    who = str       # unique way to identity this entity
    meta = dict     # any special weird data

relations.OneToMany(Unum, Entity)

class Origin(Base):
    """
    Origin something like Discord, BlueSky and how to handle it
    """

    id = int
    who = str   # unique way to identity this origin, class method in this cases
    meta = dict # any special weird data

class Fact(Base):
    """
    Fact, a record of what happened from an Origin
    """

    id = int
    entity_id = int     # Entity of the Fact
    origin_id = int     # Origin of the Fact
    who = str           # unique way to identity the event
    when = int          # epoch time this happened
    what = dict         # playload of the entire fact from the Origin
    meta = dict         # any special weird data

    INDEX = "when"
    ORDER = "-when"

relations.OneToMany(Entity, Fact)
relations.OneToMany(Origin, Fact)

class App(Base):
    """
    App something like TehFeelz, PokeMeme and how to handle it
    """

    id = int
    who = str   # unique way to identity this app, class method in this cases
    meta = dict # any special weird data

class Act(Base):
    """
    Act, a record of what needs to happen
    """

    id = int
    entity_id = int     # Entity this is directed too
    app_id = int        # App this is referencing
    who = str           # unique way to identity this event
    when = int          # epoch time this happened
    what = dict         # playload of the entire Act from the App
    meta = dict         # any special weird data

    INDEX = "when"
    ORDER = "-when"

relations.OneToMany(Entity, Act)
relations.OneToMany(App, Act)

class Witness(Base):
    """
    Witness allows an Origin to write Facts
    """

    id = int
    entity_id = int # Entity this is witnessing
    origin_id = int # Origin this is witnessing
    who = str       # unique way to identity this witness, account id, etc
    what = dict     # what is allowed from the Origin to the Fact
    meta = dict     # any special weird data

relations.OneToMany(Entity, Witness)
relations.OneToMany(Origin, Witness)

class Narrator(Base):
    """
    Narrator allows an App to read Facts
    """

    id = int
    entity_id = int # Entity this is witnessing
    app_id = int    # Origin this is witnessing
    who = str       # unique way to identity this narrator, account id, etc
    what = dict     # what is allowed fom the Fact to the App
    meta = dict     # any special weird data

relations.OneToMany(Entity, Narrator)
relations.OneToMany(App, Narrator)

class Executor(Base):
    """
    Executor allows an App to write Acts
    """

    id = int
    entity_id = int # Entity this is be excuting to
    app_id = int    # App that is executing
    who = str       # unique way to identity this executor, account id, etc
    what = dict     # what is allowed from the App to the Act
    meta = dict     # any special weird data

relations.OneToMany(Entity, Executor)
relations.OneToMany(App, Executor)

class Herald(Base):
    """
    Herald allows an Origin to read Acts (and act on them)
    """

    id = int
    entity_id = int # Entity this is heralding
    origin_id = int # Origin this is heralding
    who = str       # unique way to identity this herald, account id, etc
    what = dict     # what is allowed from the Act to the Origin
    meta = dict     # any special weird data

relations.OneToMany(Entity, Herald)
relations.OneToMany(Origin, Herald)
