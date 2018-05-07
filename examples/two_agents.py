import os

from jason_malmo.game import Game
from jason_malmo.tasks import GoToPosition

game = Game('Agents test')

game.register(os.path.join(os.path.dirname(__file__), 'sample_agents/agent.asl'))
#game.register(os.path.join(os.path.dirname(__file__), 'sample_agents/agent2.asl'))

game.tasks.register(GoToPosition)

game.run()
