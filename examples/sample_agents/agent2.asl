tasks([]).

!hello_world.

+!hello_world <-
  .wait(1000);
  .send(agent, achieve, go_there(-5, -5))
.