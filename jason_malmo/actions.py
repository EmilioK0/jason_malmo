"""Custom pyson actions.

This module registers all the base custom actions that can be called from Jason.

Attributes:
    actions (:obj:`pyson.Actions`): Pyson custom actions.
"""

import pyson
import pyson.stdlib

actions = pyson.Actions(pyson.stdlib.actions)


@actions.add(".floor_grid", 1)
def floor_grid(agent, term, intention):
    """Return the 3x3 grid of blocks under the agent.

    Args:
        agent (:obj:`jason_malmo.agent.Agent`): Target agent.
        term: Pyson associated context.
        intention: Pyson associated context.
    """
    observations = agent.get_observations()
    grid = observations.get(u'floor3x3', 0)
    if pyson.unify(tuple(grid), term.args[0], intention.scope, intention.stack):
        yield


@actions.add(".position", 1)
def position(agent, term, intention):
    """Return the agent position.

    Args:
        agent (:obj:`jason_malmo.agent.Agent`): Target agent.
        term: Pyson associated context.
        intention: Pyson associated context.
    """
    pos = agent.get_position()
    if pyson.unify(tuple(pos), term.args[0], intention.scope, intention.stack):
        yield


def _get_value(value):
    def _wrapped_get_value(agent, term, intention):
        if pyson.unify(agent.get_observations_value(value), term.args[0], intention.scope, intention.stack):
            yield
    return _wrapped_get_value


actions.add(".life", 1, _get_value('Life'))
actions.add(".distance_travelled", 1, _get_value('DistanceTravelled'))
actions.add(".time_alive", 1, _get_value('TimeAlive'))
actions.add(".mobs_killed", 1, _get_value('MobsKilled'))
actions.add(".players_killed", 1, _get_value('PlayersKilled'))
actions.add(".damage_taken", 1, _get_value('DamageTaken'))
actions.add(".damage_dealt", 1, _get_value('DamageDealt'))
actions.add(".score", 1, _get_value('Score'))
actions.add(".food", 1, _get_value('Food'))
actions.add(".xp", 1, _get_value('XP'))
actions.add(".air", 1, _get_value('Air'))
actions.add(".pitch", 1, _get_value('Pitch'))
actions.add(".yaw", 1, _get_value('Yaw'))
actions.add(".world_time", 1, _get_value('WorldTime'))
