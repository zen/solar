import click
import re

from solar.interfaces.db import get_db


db = get_db()


def get_uid(given_uid):
    """
    Converts given uid to real uid.
    """
    matched = re.search('last(\d*)', given_uid)
    if matched:
        try:
            position = int(matched.group(1))
        except ValueError:
            position = 0
        history = db.read('history', collection=db.COLLECTIONS.state_log)
        try:
            return history[position]
        except IndexError:
            # fallback to original
            return given_uid
    return given_uid


class SolarUIDParameterType(click.types.StringParamType):
    """
    Type for solar changes uid.
    Works like a string but can convert `last(\d+)` to valid uid.
    """
    name = 'uid'

    def convert(self, value, param, ctx):
        value = click.types.StringParamType.convert(self, value, param, ctx)
        value = get_uid(value)
        return value


SOLARUID = SolarUIDParameterType()
