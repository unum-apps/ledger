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

    id = int    # Internal id
    who = str   # External id
    status = [  # Whether is using
        "active",
        "inactive"
    ]
    meta = dict # any special weird data

class Entity(Base):
    """
    Entity is a person.
    """

    id = int        # Internal id
    unum_id = int   # The Unum this entity is a part of
    who = str       # External id, name
    status = [      # Whether can use
        "active",
        "inactive"
    ]
    meta = dict     # any special weird data

relations.OneToMany(Unum, Entity)

class Scat(Base):
    """
    Scat, a record of what fell through the cracks
    """

    id = int        # Internal id
    entity_id = int # Entity who scatted
    who = str       # External id, what's being scatted on
    when = int      # epoch time this happened
    what = dict     # payload of the entire Scat
    meta = dict     # any special weird data

    UNIQUE = False
    INDEX = "when"
    ORDER = "-when"

relations.OneToMany(Entity, Scat)

class Task(Base):
    """
    Task, a record of what's todo and done
    """

    id = int            # Internal id
    entity_id = int     # Entity this is directed to
    who  = str          # External id, what's being worked on
    status = [          # The status of the Task
        "blocked",
        "inprogress",
        "done",
        "wontdo",
        "imperiled"
    ]
    when = int        # epoch time this happened
    what = dict       # payload of the entire Task
    meta = dict       # any special weird data

    UNIQUE = False
    INDEX = "when"
    ORDER = "-when"

relations.OneToMany(Entity, Task)

class Award(Base):
    """
    Award, a record of what was achieved
    """

    id = int            # Internal id
    entity_id = int     # Entity this is directed to
    who  = str          # External id, for reference
    when = int          # epoch time this happened
    what = dict         # payload of the entire Act from the App
    meta = dict         # any special weird data

    INDEX = "when"
    ORDER = "-when"

relations.OneToMany(Entity, Award)

class App(Base):
    """
    App something like TehFeelz, PokeMeme and how to handle it
    """

    id = int    # Internal id
    who = str   # External id, how to identify
    status = [  # Whether to use this one or not
        "active",
        "inactive"
    ]
    meta = dict # any special weird data

class Origin(Base):
    """
    Origin something like Discord, BlueSky and how to handle it
    """

    id = int    # Internal id
    who = str   # External id, how to identify
    status = [  # Whether to use this one or not
        "active",
        "inactive"
    ]
    meta = dict # any special weird data

class Act(Base):
    """
    Act, a record of what needs to happen
    """

    id = int            # Internal id
    entity_id = int     # Entity this is directed to
    app_id = int        # App this is referencing
    when = int          # epoch time this happened
    what = dict         # payload of the entire Act from the App
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

    id = int            # Internal id
    entity_id = int     # Entity of the Fact
    origin_id = int     # Origin of the Fact
    who = str           # External id
    when = int          # epoch time this happened
    what = dict         # The general what was said, words, channel, used by Apps
    meta = dict         # The specific info what was said, used by Origins

    UNIQUE = False
    INDEX = "when"
    ORDER = "-when"

relations.OneToMany(Entity, Fact)
relations.OneToMany(Origin, Fact)

class Witness(Base):
    """
    Witness allows an Origin to write Facts and read Acts for an Entity
    """

    id = int
    entity_id = int # Entity this is witnessing
    origin_id = int # Origin this is witnessing
    who = str       # External ID from originating system (e.g., Discord user ID, GitHub handle)
    status = [      # Whether in use
        "active",
        "inactive"
    ]
    what = dict     # Generally what's allowed? Not really used yet.
    meta = dict     # Specifically what's allowed? Not really used yet.

relations.OneToMany(Entity, Witness)
relations.OneToMany(Origin, Witness)

class Herald(Base):
    """
    Herald allows an App to read Facts and Write Acts for an Entity
    """

    id = int
    entity_id = int # Entity this is witnessing
    app_id = int    # Origin this is witnessing
    status = [      # Whether in use
        "active",
        "inactive"
    ]
    what = dict     # Generally what's allowed? Not really used yet.
    meta = dict     # Specifically what's allowed? Not really used yet.

    UNIQUE = ["entity_id", "app_id"]

relations.OneToMany(Entity, Herald)
relations.OneToMany(App, Herald)
