import time
import json
import overscore
import unum_ledger

class Service:
    """
    Base Service class for Apps and Origins
    """

    def __init__(self, logger, redis):

        self.logger = logger
        self.redis = redis

    def is_active(self, entity_id):
        """
        Checks to see if an enity is active
        """

        return (
            unum_ledger.Entity.one(
                id=entity_id,
                status="active"
            ).retrieve(False) is not None
            and
            unum_ledger.Narrator.one(
                entity_id=entity_id,
                service_id=self.service.id,
                status="active"
            ).retrieve(False) is not None
        )

    def journal_change(
            self,
            action,
            model,
            change=None
        ):
        """
        Makes a change and journals it
        """

        create = True
        who = f"{action}:{model.NAME}.{model.SOURCE}"
        what = {
            "action": action,
            "service": model.SOURCE,
            "block": model.NAME
        }

        if action == "create":

            model = model.create()
            what["after"] = model.export()

        who += f":{model.id}"
        what["id"] = model.id

        if action == "update":

            what["before"] = model.export()

            for key, value in change.items():

                path = overscore.parse(key)

                current = model

                for place in path[:-1]:
                    current = current[place]

                current[path[-1]] = value

            what["after"] = model.export()

            create = model.update()

        elif action == "delete":

            what["before"] = model.export()

            create = model.delete()

        if create:
            journal = unum_ledger.Journal(
                who=who,
                what=what,
                when=time.time()
            ).create()

            self.logger.info("journal", extra={"journal": {"id": journal.id}})
            self.redis.xadd("ledger/journal", fields={"journal": json.dumps(journal.export())})

        if action == "create":
            return model

        return create

    def on_journal(self):
        """
        Listens for Journal Entries
        """

        message = self.redis.xreadgroup(self.group, self.group_id, {
            "ledger/journal": ">"
        }, count=1, block=500)

        if not message:
            return

        if "journal" in message[0][1][0][1]:

            instance = json.loads(message[0][1][0][1]["journal"])
            self.logger.info("journal", extra={"journal": instance})

            if (
                self.is_active(instance["what"].get("entity_id")) and
                not instance["what"].get("error") and
                not instance["what"].get("errors")
            ):

                if (
                    instance["what"].get("command") and
                    self.service.who OK so in instance["what"].get("apps", [])
                ):
                    self.do_command(instance)

            self.redis.xack("ledger/fact", self.group, message[0][1][0][0])

    def create_act(self, **act):
        """
        Creates an act if needed
        """

        if not self.is_active(act["entity_id"]):
            return

        act = self.journal_change("create", unum_ledger.Act(**act))

        self.logger.info("act", extra={"act": {"id": act.id}})
        self.redis.xadd("ledger/act", fields={"act": json.dumps(act.export())})

    def decode_time(self, arg):
        """
        Decodes 3d2h3m format to seconds

        """

        seconds = 0
        current = ""

        for letter in arg:

            if '0' <= letter and letter <= '9':
                current += letter
            elif current and letter == 'd':
                seconds += int(current) * 24*60*60
                current = ""
            elif current and letter == 'h':
                seconds += int(current) * 60*60
                current = ""
            elif current and letter == 'm':
                seconds += int(current) * 60
                current = ""

        return seconds

    def encode_time(self, seconds):
        """
        Encodes seconds to 3d2h3m format
        """

        # Start with a blank string

        arg = ""

        # Determine and peel off the days, hours, and minutes

        days = int(seconds/(24*60*60))
        seconds -= days * 24*60*60
        hours = int(seconds /(60*60))
        seconds -= hours * 60*60
        mins = int(seconds/(60))

        # If there's a value, add it with its letter

        if days:
            arg += f"{days}d"

        if hours:
            arg += f"{hours}h"

        if mins:
            arg += f"{mins}m"

        return arg

class AsycService(Service):
    """
    Base Service class for Asyc Apps and Origins
    """

    async def journal_change(
            self,
            action,
            model,
            change=None
        ):
        """
        Makes a change and journals it
        """

        create = True
        who = f"{action}:{model.NAME}.{model.SOURCE}"
        what = {
            "action": action,
            "app": model.SOURCE,
            "block": model.NAME
        }

        if action == "create":

            model = model.create()
            what["after"] = model.export()

        who += f":{model.id}"
        what["id"] = model.id

        if action == "update":

            what["before"] = model.export()

            for key in change:
                path = overscore.parse(name)

                for place in path:
                    current = current[place]

                return current

                model[key] = change[key]

            what["after"] = model.export()

            create = model.update()

        elif action == "delete":

            what["before"] = model.export()

            create = model.delete()

        if create:
            journal = unum_ledger.Journal(
                who=who,
                what=what,
                when=time.time()
            ).create()

            self.logger.info("journal", extra={"journal": {"id": journal.id}})
            await self.redis.xadd("ledger/journal", fields={"journal": json.dumps(journal.export())})

        if action == "create":
            return model

        return create



class OriginService(Service):

    KIND = "origin"

    def is_active(self, entity_id):
        """
        Checks to see if an enity is active
        """

        return (
            unum_ledger.Entity.one(
                id=entity_id,
                status="active"
            ).retrieve(False) is not None
            and
            unum_ledger.Witness.one(
                entity_id=entity_id,
                origin_id=self.origin.id,
                status="active"
            ).retrieve(False) is not None
        )


class AppService(Service):

    KIND = "app"

    def is_active(self, entity_id):
        """
        Checks to see if an enity has a Herald
        """

        return (
            unum_ledger.Entity.one(
                id=entity_id,
                status="active"
            ).retrieve(False) is not None
            and
            unum_ledger.Herald.one(
                entity_id=entity_id,
                app_id=self.app.id,
                status="active"
            ).retrieve(False) is not None
        )
