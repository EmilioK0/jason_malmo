import operator
from types import LambdaType

from jason_malmo.exceptions import TaskNotRegistered
from jason_malmo.math_utils import get_path_value


class TaskManager:
    """Task Manager

    Holds the registered task types, and handles the tasks associated to an Agent.
    """

    def __init__(self):
        self._tasks = {}

        # Check tasks' integrity
        for task in Task.get_subclasses():
            if not task.identifier:
                raise AttributeError('Task identifier must be filled. {}'.format(task))

    def register(self, task):
        """Register task type.

        Args:
            task: :obj:`Task` to register.
        """
        self._tasks[task.identifier] = task

    def handle(self, agent, tasks):
        """Execute agent's most priority task.

        Args:
            agent (:obj:`jason_malmo.agent.Agent`): Agent instance.
            tasks (:obj:`list` of :obj:`pyson.Literal`): List of pyson tasks.
        """
        py_tasks = self.pythonize_tasks(agent, tasks)
        py_tasks.sort(key=operator.attrgetter('priority'), reverse=True)
        if len(py_tasks) > 0:
            current_task = py_tasks[0]
            finished = current_task.run()
            if finished:
                print('Finished task: ', current_task)
                index = py_tasks.index(current_task)
                for (belief, value) in agent.beliefs.items():
                    if belief[0] == 'tasks':
                        tasks_belief = list(value)[0]
                        tasks_belief.args = (tuple([task for i, task in enumerate(tasks_belief.args[0]) if i != index]),)
                        agent.beliefs[belief] = {tasks_belief}

    def pythonize_tasks(self, agent, tasks):
        """Transform pyson tasks into `Task` objects.

        Args:
            agent (:obj:`jason_malmo.agent.Agent`): Agent instance.
            tasks (:obj:`list` of :obj:`pyson.Literal`): List of pyson tasks.

        Returns:
            :obj:`list` of :obj:`Task`: List of `Task` instances.

        Raises:
            :class:`jason_malmo.exceptions.TaskNotRegistered`: Task not registered.\n
                Register the task before running the game::

                    game.tasks.register(CustomTask)
                    game.run()
        """
        py_tasks = []
        for task in tasks:
            priority, task_type, content = task.args
            # Default is a lambda function to suppress the not callable warning
            py_task = self._tasks.get(task_type, lambda: None)
            if isinstance(py_task, LambdaType):
                raise TaskNotRegistered(task_type)
            py_tasks.append(py_task(agent, priority, content))
        return py_tasks


class Task:
    """Base Task class to be extended by custom classes.

    Attributes:
        agent (:obj:`jason_malmo.agent.Agent`): Target agent.
        priority (int): Task priority.
        content (object): Task arguments.
    """

    identifier = None
    """str: Task identifier."""

    def __init__(self, agent, priority, content):
        self.agent = agent
        self.priority = priority
        self.content = self.py_content(content)

    def __repr__(self):
        return '{}: {}'.format(self.identifier, self.content)

    def run(self):
        """Run the task

        Returns:
            bool: Should return True if the task has finished, False if not.
        """
        raise NotImplementedError

    @staticmethod
    def py_content(content):
        """Transform the pyson content to python instances. Should be overridden by the subclasses.

        Args:
            content (:obj:`pyson.Literal`): Pyson instance content.

        Returns:
            :obj:`object`: Python object instance.
        """
        return content.args

    @classmethod
    def get_subclasses(cls):
        for subclass in cls.__subclasses__():
            yield from subclass.get_subclasses()
            yield subclass


class GoToPosition(Task):
    """Addresses the agent to a specified position setting it's move and turn values."""
    identifier = 'GO_TO_POSITION'

    def run(self):
        """Set the next move and turn to address to the destination.

        Returns:
            bool: True if the task has finished, False if not.
        """
        pos = self.agent.get_position()
        if abs(pos[0] - self.content[0]) < 1 and abs(pos[2] - self.content[1]) < 1:
            self.agent.send_command("move 0")
            self.agent.send_command("turn 0")
            return True
        speed, turn = get_path_value(self.agent, self.content)
        self.agent.send_command("move " + str(speed))
        self.agent.send_command("turn " + str(turn))
        return False