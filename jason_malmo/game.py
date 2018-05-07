import MalmoPython
import random
import threading
import time

import malmoutils
import pyson.runtime

from jason_malmo.actions import actions
from jason_malmo.agent import JasonAgent
from jason_malmo.exceptions import NoAgentsException
from jason_malmo.tasks import TaskManager


class Game:
    """Game main class.

    This class may be instantiated to run a Malmo Mission using Jason Agents.

    Attributes:
        name (str): Match's name.
        world (str): World's generator string. `Flat world generator`_.
        tasks (:obj:`jason_malmo.tasks.TaskManager`): Tasks Manager.

    .. _Flat world generator:
        http://minecraft.tools/en/flat.php
    """

    def __init__(self, name):
        self.name = name
        self.world = '3;7,220*1,5*3,2;3;,biome_1'
        self.tasks = TaskManager()

        self._my_mission = None
        self._client_pool = None
        self._agents = []
        self._jason_env = pyson.runtime.Environment()

    def register(self, agent_file):
        """Register an Agent to the game.

        Args:
            agent_file (str): Path to the .asl file (Jason text file).
        """
        with open(agent_file) as source:
            agent = self._jason_env.build_agent(source, actions)
            agent.__class__ = JasonAgent
            agent.malmo_agent = MalmoPython.AgentHost()
            self._agents.append(agent)
            
    def _get_mission_xml(self):
        return '''<?xml version="1.0" encoding="UTF-8" ?>
        <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <About>
                <Summary>''' + self.name + '''</Summary>
            </About>
            
            <ModSettings>
                <MsPerTick>50</MsPerTick>
            </ModSettings>

            <ServerSection>
                <ServerInitialConditions>
                    <AllowSpawning>false</AllowSpawning>
                </ServerInitialConditions>
                <ServerHandlers>
                    <FlatWorldGenerator generatorString="''' + self.world + '''" />
                    <ServerQuitWhenAnyAgentFinishes />
                </ServerHandlers>
            </ServerSection>
            
            ''' + self._get_agents_xml() + '''

        </Mission>'''
        
    def _get_agents_xml(self):
        xml = ''
        for agent in self._agents:
            xml += '''<AgentSection mode="Survival">
                        <Name>''' + str(agent.name) + '''</Name>
                        <AgentStart>
                            <Placement x="''' + str(random.randint(0, 10)) + '''" y="229" z="''' + str(random.randint(0, 10)) + '''"/>
                        </AgentStart>
                        <AgentHandlers>
                            <ContinuousMovementCommands turnSpeedDegs="360">
                                <ModifierList type="deny-list"> <!-- Example deny-list: prevent agent from strafing -->
                                    <command>strafe</command>
                                </ModifierList>
                            </ContinuousMovementCommands>
                            <ObservationFromNearbyEntities>
                                <Range name="entities" xrange="40" yrange="2" zrange="40"/>
                            </ObservationFromNearbyEntities>
                            <ObservationFromRay/>
                            <ObservationFromFullStats/>
                            <ObservationFromGrid>
                                <Grid name="floor3x3">
                                    <min x="-1" y="-1" z="-1"/>
                                    <max x="1" y="-1" z="1"/>
                                </Grid>
                            </ObservationFromGrid>
                        </AgentHandlers>
                    </AgentSection>'''
        return xml
        
    def run(self):
        """Runs the game with the registered agents

        Raises:
            :class:`jason_malmo.exceptions.NoAgentsException`: There are not registered agents in the game.\n
                Register an agent before running the game::

                    game.register('/path/to/file.asl')
                    game.run()
        """
        self._client_pool = MalmoPython.ClientPool()

        if not len(self._agents):
            raise NoAgentsException

        for port in range(10000, 10000 + len(self._agents) + 1):
            self._client_pool.add(MalmoPython.ClientInfo('127.0.0.1', port))

        self._my_mission = MalmoPython.MissionSpec(self._get_mission_xml(), True)
        
        for (index, agent) in enumerate(self._agents):
            malmoutils.parse_command_line(agent.malmo_agent)
            self._safe_start_mission(
                agent.malmo_agent,
                self._my_mission,
                self._client_pool,
                malmoutils.get_default_recording_object(agent.malmo_agent, "saved_data"),
                index,
                ''
            )
        self._safe_wait_for_start([agent.malmo_agent for agent in self._agents])
            
        threads = []
        for agent in self._agents:
            thr = threading.Thread(target=self._jason_env.run_agent, args=(agent,), kwargs={})
            thr.start()
            threads.append(thr)
        
        # TODO while mission is running
        while True:
            for agent in self._agents:
                for (belief, value) in agent.beliefs.items():
                    if belief[0] == 'tasks':
                        tasks = []
                        for task in list(value)[0].args[0]:
                            tasks.append(task)
                        self.tasks.handle(agent, tasks)
            time.sleep(0.05)
                    
    @staticmethod
    def _safe_start_mission(agent_host, mission, client_pool, recording, role, experiment_id):
        used_attempts = 0
        max_attempts = 5
        print("Calling startMission for role", role)
        while True:
            try:
                agent_host.startMission(mission, client_pool, recording, role, experiment_id)
                break
            except MalmoPython.MissionException as e:
                error_code = e.details.errorCode
                if error_code == MalmoPython.MissionErrorCode.MISSION_SERVER_WARMING_UP:
                    print("Server not quite ready yet - waiting...")
                    time.sleep(2)
                elif error_code == MalmoPython.MissionErrorCode.MISSION_INSUFFICIENT_CLIENTS_AVAILABLE:
                    print("Not enough available Minecraft instances running.")
                    used_attempts += 1
                    if used_attempts < max_attempts:
                        print("Will wait in case they are starting up.", max_attempts - used_attempts, "attempts left.")
                        time.sleep(2)
                elif error_code == MalmoPython.MissionErrorCode.MISSION_SERVER_NOT_FOUND:
                    print("Server not found - has the mission with role 0 been started yet?")
                    used_attempts += 1
                    if used_attempts < max_attempts:
                        print("Will wait and retry.", max_attempts - used_attempts, "attempts left.")
                        time.sleep(2)
                else:
                    print("Other error:", e.message)
                    print("Waiting will not help here - bailing immediately.")
                    exit(1)
            if used_attempts == max_attempts:
                print("All chances used up - bailing now.")
                exit(1)
        print("startMission called okay.")

    @staticmethod
    def _safe_wait_for_start(agent_hosts):
        print("Waiting for the mission to start", end=' ')
        start_flags = [False for _ in agent_hosts]
        start_time = time.time()
        time_out = 120  # Allow two minutes for mission to start.
        while not all(start_flags) and time.time() - start_time < time_out:
            states = [a.peekWorldState() for a in agent_hosts]
            start_flags = [w.has_mission_begun for w in states]
            errors = [e for w in states for e in w.errors]
            if len(errors) > 0:
                print("Errors waiting for mission start:")
                for e in errors:
                    print(e.text)
                print("Bailing now.")
                exit(1)
            time.sleep(0.1)
            print(".", end=' ')
        print()
        if time.time() - start_time >= time_out:
            print("Timed out waiting for mission to begin. Bailing.")
            exit(1)
        print("Mission has started.")
