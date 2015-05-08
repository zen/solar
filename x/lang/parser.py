from __future__ import unicode_literals, print_function

import pypeg2
import re


HAPROXY_DEPLOYMENT = """
node1 := ro_node ip=10.0.0.3
node2 := ro_node ip=10.0.0.4
node3 := ro_node ip=10.0.0.5

mariadb_service1 := mariadb_service image=mariadb root_password=mariadb port=3306
keystone_db := mariadb_db db_name=keystone_db
keystone_db_user := mariadb_user new_user_name=keystone new_user_password=keystone

keystone_config1 := keystone_config config_dir=/etc/solar/keystone admin_token=admin
keystone_service1 := keystone_service port=5000 admin_port=35357

keystone_config2 := keystone_config config_dir=/etc/solar/keystone admin_token=admin
keystone_service2 := keystone_service port=5000 admin_port=35357

haproxy_keystone_config := haproxy_config name=keystone_config listen_port=5000
haproxy_config := haproxy
haproxy_service := docker_container image=tutum/haproxy
"""

"""
# 2 types of connections:
#   [A::B] -- overwrite whole mapping
#   {A::B} -- update default mapping with given definition(s)
node1 -> mariadb_service1 -{root_password::login_password port::login_port}-> keystone_db -> keystone_db_user

node1 -> keystone_config1 -> keystone_service1 -[ip::servers port::ports]-> haproxy_keystone_config
mariadb_service1 -[ip::db_host]-> keystone_config1 -[config_dir::config_dir] -> keystone_service1
keystone_db_user -[db_name::db_name new_user_name::db_user new_user_password::db_password]-> keystone_config1

node1 -> keystone_config2 -> keystone_service2 -[ip::servers port::ports]->haproxy_keystone_config
mariadb_service1 -[ip::db_host]-> keystone_config2 -[config_dir::config_dir] -> keystone_service2
keystone_db_user -[db_name::db_name new_user_name::db_user new_user_password::db_password]-> keystone_config2

node1 -> haproxy_config -> haproxy_service
haproxy_keystone_config -[listen_port::listen_ports name::configs_names ports::configs_ports servers::configs]-> haproxy_config
haproxy_config -[listen_ports::ports config_dir::host_binds]-> haproxy_service

# resources
#r1 = Resource(<name>, <template-path>, <destination-path>, <args>)
#r2 = Resource(<name>, <template-path>, <destination-path>, <args>)

# connections
#r1.ip -> r2.servers

# actions
#r1:run >> r2:run
"""


# LANGUAGE DEFINITIONS
class ResourceDefinition(object):
    def __init__(self, name, source, args=None):
        self.name = name
        self.source = source
        self.args = args or {}

    def __unicode__(self):
        return '[{} :: {}] {}'.format(self.name, self.source, self.args)

    def __repr__(self):
        return unicode(self)


class ConnectionDefinition(object):
    def __init__(self, emitter, receiver, mapping=None, mapping_behavior='overwrite'):
        self.emitter = emitter
        self.receiver = receiver
        self.mapping = mapping or {}
        self.mapping_behavior = mapping_behavior

    def __unicode__(self):
        if not self.mapping:
            return '{} -> {}'.format(self.emitter, self.receiver)

        mapping_symbols = '[]'
        if self.mapping_behavior == 'update':
            mapping_symbols = '{}'

        return '{emitter} -{symbol_l}{mapping}{symbol_r}-> {receiver}'.format(
            emitter=self.emitter,
            symbol_l=mapping_symbols[0],
            mapping=' '.join('{}::{}'.format(k, v) for k, v in self.mapping.items()),
            symbol_r=mapping_symbols[1],
            receiver=self.receiver
        )

    def __repr__(self):
        return unicode(self)


# PARSERS
class Comment(str):
    grammar = '#', pypeg2.restline


class ResourceDefinitionOperator(pypeg2.Symbol):
    grammar = re.compile(r':=')


class ResourceName(str):
    grammar = pypeg2.word


class ResourceSource(str):
    grammar = pypeg2.word


class ResourceArg(pypeg2.List):
    grammar = pypeg2.word, "=", re.compile('(\S+)')


class ResourceDefinitionContent(pypeg2.List):
    grammar = ResourceSource, pypeg2.maybe_some(ResourceArg)


class ResourceDefinitionExpression(pypeg2.List):
    grammar = ResourceName, ":=", ResourceDefinitionContent


class Input(pypeg2.List):
    grammar = pypeg2.word#, ".", pypeg2.word


class ConnectionOperator(pypeg2.Symbol):
    regex = re.compile('->')


class ConnectionMappingArguments(pypeg2.List):
    grammar = pypeg2.word, '::', pypeg2.word


class ConnectionOperatorWithUpdateMapping(pypeg2.List):
    grammar = '-{', pypeg2.some(ConnectionMappingArguments), '}->'


class ConnectionOperatorWithOverwriteMapping(pypeg2.List):
    grammar = '-[', pypeg2.some(ConnectionMappingArguments), ']->'


class ConnectionExpression(pypeg2.List):
    grammar = Input, pypeg2.some([ConnectionOperator,
                                  ConnectionOperatorWithUpdateMapping,
                                  ConnectionOperatorWithOverwriteMapping], Input)


class ActionOperator(pypeg2.Symbol):
    regex = re.compile(r'(>>|\|)')


class Action(pypeg2.List):
    grammar = pypeg2.word, ":", pypeg2.word


class ActionExpression(pypeg2.List):
    pass


ActionExpression.grammar = [
    Action,
    ('(', ActionExpression, ')'),
], pypeg2.maybe_some(ActionOperator, ActionExpression)


class Expression(pypeg2.List):
    pass


Expression.grammar = [
    Comment,
    ResourceDefinitionExpression,
    ConnectionExpression,
    ActionExpression,
], pypeg2.maybe_some(pypeg2.endl, Expression)


def unwrap_expressions(c):
    if isinstance(c, Expression):
        ret = []
        for parsed in c:
            ret.extend(unwrap_expressions(parsed))
        return ret
    elif isinstance(c, Comment):
        return []
    else:
        return [c]


def show_action_expression(e):
    if isinstance(e, ActionExpression):
        if len(e) == 1:
            show_action_expression(e[0])
        else:
            action, operator, exp = e
            print(action, operator)
            print('(')
            show_action_expression(exp)
            print(')')
    else:
        print(e)


def print_parsed(c):
    print(c)

    if isinstance(c, ResourceDefinitionExpression):
        print(c)
    elif isinstance(c, ConnectionExpression):
        for i in range(len(c) - 1):
            r1 = c[i]
            r2 = c[i + 1]
            print('Connect {} -> {}'.format(r1, r2))
    elif isinstance(c, ActionExpression):
        show_action_expression(c)


def create_definitions(parsed):
    if isinstance(parsed, ResourceDefinitionExpression):
        args = None
        if len(parsed[1]) >= 2:
            args = dict(parsed[1][1:])

        return ResourceDefinition(
            parsed[0], parsed[1][0], args=args
        )
    elif isinstance(parsed, ConnectionExpression):
        ret = []
        for emitter, connector, receiver in zip(parsed[::2], parsed[1::2], parsed[2::2]):
            emitter = emitter[0]
            receiver = receiver[0]
            if isinstance(connector, ConnectionOperator):
                ret.append(ConnectionDefinition(emitter, receiver))
                continue

            mapping_behavior = 'overwrite'
            if isinstance(connector, ConnectionOperatorWithUpdateMapping):
                mapping_behavior = 'update'

            mapping = dict(connector)
            ret.append(ConnectionDefinition(emitter, receiver, mapping=mapping, mapping_behavior=mapping_behavior))

        return ret


if __name__ == '__main__':
    SAMPLES = """
# resources
node1 := ro_node ip=10.0.0.3 ssh_key=key

# connections
r1 -> r2 -> r3
node1 -> mariadb_service1 -{root_password::login_password port::login_port}-> keystone_db -> keystone_db_user
node1 -[ip::ip]-> keystone_db -> keystone_db_user

# actions
r1:run >> (r2:run | r3:run)
"""

    c = pypeg2.parse(SAMPLES, Expression)
    c = unwrap_expressions(c)
    for parsed in c:
        print(create_definitions(parsed))

    c = pypeg2.parse(HAPROXY_DEPLOYMENT, Expression)
    c = unwrap_expressions(c)
    for parsed in c:
        print(create_definitions(parsed))

