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
    status = [  # Whether to use this one or not
        "active",
        "inactive"
    ]
    meta = dict # any special weird data

class Entity(Base):
    """
    Entity is a person.
    """

    id = int
    unum_id = int   # The Unum this entity is a part of
    who = str       # unique way to identity this entity
    status = [      # Whether to use this one or not
        "active",
        "inactive"
    ]
    meta = dict     # any special weird data

relations.OneToMany(Unum, Entity)

class Scat(Base):
    """
    Scat, a record of what fell through the cracks
    """

    id = int
    entity_id = int # Entity this is directed too
    who  = [        # the related meme in ascii form
        "?",
        "+",
        "*",
        "-",
        "!"
    ]
    when = int      # epoch time this happened
    what = dict     # playload of the entire Act from the App
    meta = dict     # any special weird data

    UNIQUE = False
    INDEX = "when"
    ORDER = "-when"

relations.OneToMany(Entity, Scat)

class Task(Base):
    """
    Task, a record of what's todo and done
    """

    id = int
    entity_id = int   # Entity this is directed too
    who  = str        # General string for reference
    status = [        # Teh status of the feat
        "requested",
        "accepted",
        "completed",
        "rejected",
        "excepted"
    ]
    when = int        # epoch time this happened
    what = dict       # playload of the entire Act from the App
    meta = dict       # any special weird data

    UNIQUE = False
    INDEX = "when"
    ORDER = "-when"

relations.OneToMany(Entity, Task)

class Feat(Base):
    """
    Feat, a record of what was acheived
    """

    id = int
    entity_id = int   # Entity this is directed too
    who  = str        # id for reference
    status = [        # Teh status of the feat
        "requested",
        "accepted",
        "completed",
        "rejected",
        "excepted"
    ]
    when = int        # epoch time this happened
    what = dict       # playload of the entire Act from the App
    meta = dict       # any special weird data

    INDEX = "when"
    ORDER = "-when"

relations.OneToMany(Entity, Feat)

class App(Base):
    """
    App something like TehFeelz, PokeMeme and how to handle it
    """

    id = int
    who = str   # unique way to identity this app, class method in this cases
    status = [  # Whether to use this one or not
        "active",
        "inactive"
    ]
    meta = dict # any special weird data

class Origin(Base):
    """
    Origin something like Discord, BlueSky and how to handle it
    """

    id = int
    who = str   # unique way to identity this origin, class method in this cases
    status = [  # Whether to use this one or not
        "active",
        "inactive"
    ]
    meta = dict # any special weird data

class Act(Base):
    """
    Act, a record of what needs to happen
    """

    id = int
    entity_id = int     # Entity this is directed too
    app_id = int        # App this is referencing
    when = int          # epoch time this happened
    what = dict         # playload of the entire Act from the App
    meta = dict         # any special weird data

    UNIQUE = False
    INDEX = "when"
    ORDER = "-when"

relations.OneToMany(Entity, Act)
relations.OneToMany(App, Act)

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

    UNIQUE = False
    INDEX = "when"
    ORDER = "-when"

relations.OneToMany(Entity, Fact)
relations.OneToMany(Origin, Fact)

class Witness(Base):
    """
    Witness allows an Origin to write Facts
    """

    id = int
    entity_id = int # Entity this is witnessing
    origin_id = int # Origin this is witnessing
    who = str       # unique way to identity this witness, account id, etc
    status = [      # Whether to use this one or not
        "active",
        "inactive"
    ]
    what = dict     # what is allowed from the Origin to the Fact
    meta = dict     # any special weird data

relations.OneToMany(Entity, Witness)
relations.OneToMany(Origin, Witness)

class Herald(Base):
    """
    Narrator allows an App to read Facts
    """

    id = int
    entity_id = int # Entity this is witnessing
    app_id = int    # Origin this is witnessing
    status = [      # Whether to use this one or not
        "active",
        "inactive"
    ]
    what = dict     # what is allowed fom the Fact to the App
    meta = dict     # any special weird data

    UNIQUE = ["entity_id", "app_id"]

relations.OneToMany(Entity, Herald)
relations.OneToMany(App, Herald)
