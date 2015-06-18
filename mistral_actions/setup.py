import setuptools


setuptools.setup(
    name='Mistral shell command',
    packages=setuptools.find_packages(),
    entry_points = {'mistral.actions': [
        'solar.cmd = solar_cmd.cmd:CmdAction'
    ]}
    )
