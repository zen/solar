from subprocess import check_output


nodes = {{nodes}}  # NOQA, it will be replaced by solar/jinja processor

for value in nodes[1:]:
    print value
    cmd = 'riak-admin cluster join %s' % value['value']
    print cmd
    check_output(cmd.split())

cmd = "riak-admin cluster commit"
check_output(cmd.split())
