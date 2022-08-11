# Webots Maze Generator

A basic python script that creates a maze using a depth-first method.
The maze can then be exported as both svg and as a Webot's World file
(.wbt)

The maze generation code is Christian Hill's maze generation code that
can be found [here](https://scipython.com/blog/making-a-maze) and
[here](https://github.com/scipython/scipython-maths/tree/master/maze)

The webots world file is a json description of the simulation
environment. The file is generated by a function that prints formatted
strings to a text file. The walls of the maze are place within a
["Solid" node](https://cyberbotics.com/doc/reference/solid).

Robots or other additions to the environment can be added manually with
any text editor.

The size of maze is set using a single scalar value. The wall colour can
also be configured but has mainly been used for debugging and is
defaulted to white.

## TOOD

Variable wall thickness Optimisation for walls (turn straight connected
wall segments into a single entity) Add more maze variation (loops, non
rectangular walls)
