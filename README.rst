Jason Malmo
===========
.. image:: https://readthedocs.org/projects/jason-malmo/badge/?version=latest
    :target: http://jason-malmo.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/github/license/mashape/apistatus.svg
    :alt: license

A Malmo Interface to implement Jason agents in Minecraft.

Requirements
************
- `Malmö <https://github.com/Microsoft/malmo>`_
- `Pyson <https://github.com/niklasf/pyson>`_


Documentation
*************
Check the docs `here <http://jason-malmo.readthedocs.io>`_.

Quickstart
**********
.. code-block:: none
    :caption: agent.asl
    :name: agent.asl

    !hello_world.

    +!hello_world <-
      .position(MyPos);
      .print(MyPos)
    .

.. code-block:: python
    :caption: main.py
    :name: main.py

    from jason_malmo.game import Game

    game = Game('Agent test')
    game.register(os.path.join(os.path.dirname(__file__), 'agent.asl'))

    game.run()

.. code-block:: none
    :caption: Output
    :name: Output

    Calling startMission for role 0
    startMission called okay.
    Waiting for the mission to start . . . . . .
    Mission has started.
    agent [8, 229, 5]