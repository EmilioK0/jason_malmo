tasks([]).

!hello_world.

+!hello_world <-
  .position(MyPos);
  .print(MyPos);
  .wait(1000);

  .floor_grid(Floor);
  .print(Floor);
  .wait(1000);

  ?tasks(TaskList);
  .concat(TaskList, [task(1000, "GO_TO_POSITION", pos(40, 20))], NewT);
  -+tasks(NewT);

  !life_loop
.

// To keep the agent running
+!life_loop <-
	.wait(1000);
	!life_loop
.

+!go_there(X, Z)[source(Sender)] <-
  .print(Sender, "told me to go to", X, Z);
  ?tasks(TaskList2);
  .concat(TaskList2, [task(2000, "GO_TO_POSITION", pos(X, Z))], NewT2);
  -+tasks(NewT2)
.