
from oslo_concurrency import processutils
from mistral.actions import base


class CmdAction(base.Action):

    def __init__(self, cmd):
        self.cmd = cmd

    def run(self):
        result = processutils.execute(self.cmd, shell=True)
        return {'output': result[0], 'error': result[1]}

    def test(self):
        return
