import json
from pyson.runtime import Agent as PysonAgent


class Agent(PysonAgent):
    """Default Agent class.

    Attributes:
        malmo_agent (:obj:`MalmoPython.AgentHost`): Malmo Agent
    """

    def __init__(self, env, name, beliefs=None, rules=None, plans=None):
        super().__init__(env, name, beliefs=beliefs, rules=rules, plans=plans)
        self.malmo_agent = None

    
