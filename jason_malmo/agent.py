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

    def send_command(self, command):
        """Send command to the malmo's agent.

        Args:
            command (str): Command to be executed.\n
                Example::

                    agent.send_command('move 1')

        """
        self.malmo_agent.sendCommand(command)

    def get_position(self):
        """Return the agent's current position.

        Returns:
            :obj:`list` of int: Agent's current position.
        """
        observations = self.get_observations()
        return observations[u'XPos'], observations[u'YPos'], observations[u'ZPos']

    def get_observations(self):
        """Return the agent's last world observation.

        Returns:
            :obj:`dict`: Last observation.
        """
        last_observation = None
        while not last_observation:
            world_state = self.malmo_agent.getWorldState()
            observations = world_state.observations
            if len(observations) > 0:
                last_observation = observations[-1]

        msg = last_observation.text
        return json.loads(msg)

    def get_observations_value(self, key):
        """Return a specified value from the agent's last world observation.

        Args:
            key (str): Key of the value to return.

        Returns:
            :obj:`object`: Value.
        """
        observations = self.get_observations()
        return observations.get(key)
