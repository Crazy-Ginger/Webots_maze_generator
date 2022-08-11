#!/usr/bin/env python3
"""
Generates a basic maze with depth first method and can save it to webots wbt format or svg
"""
import argparse
import random
from os import getcwd

# Create a maze using the depth-first algorithm described at
# https://scipython.com/blog/making-a-maze/
# Christian Hill, April 2017.


class Cell:
    """A cell in the maze.

    A maze "Cell" is a point in the grid which may be surrounded by walls to
    the north, east, south or west.

    """

    # A wall separates a pair of cells in the N-S or W-E directions.
    wall_pairs = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}

    def __init__(self, x, y):
        """Initialize the cell at (x,y). At first it is surrounded by walls."""

        self.x, self.y = x, y
        self.walls = {'N': True, 'S': True, 'E': True, 'W': True}

    def has_all_walls(self):
        """Does this cell still have all its walls?"""

        return all(self.walls.values())

    def knock_down_wall(self, other, wall):
        """Knock down the wall between cells self and other."""

        self.walls[wall] = False
        other.walls[Cell.wall_pairs[wall]] = False


class Maze:
    """A Maze, represented as a grid of cells."""
    def __init__(self, width, length, x_start = 0, y_start = 0):
        """Initialize the maze grid.
        The maze consists of width x length cells and will be constructed starting
        at the cell indexed at (ix, iy).

        """

        self.width, self.length = width, length
        self.x_start, self.y_start = x_start, y_start
        self.maze_map = [[Cell(x, y) for y in range(length)] for x in range(width)]

    def cell_at(self, x, y):
        """Return the Cell object at (x,y)."""

        return self.maze_map[x][y]

    def __str__(self):
        """Return a (crude) string representation of the maze."""

        maze_rows = ['-' * self.width * 2]
        for y in range(self.length):
            maze_row = ['|']
            for x in range(self.width):
                if self.maze_map[x][y].walls['E']:
                    maze_row.append(' |')
                else:
                    maze_row.append('  ')
            maze_rows.append(''.join(maze_row))
            maze_row = ['|']
            for x in range(self.width):
                if self.maze_map[x][y].walls['S']:
                    maze_row.append('-+')
                else:
                    maze_row.append(' +')
            maze_rows.append(''.join(maze_row))
        return '\n'.join(maze_rows)

    def write_world(self, filename, scale = 0.1):
        """
        Saves maze to Webots world format

        :param filename: (string) name to save maze to, if file extension isn't specified it will be added
        :param scale: (float) scale of the maze to set
        """

        if not filename.endswith(".wbt"):
            filename += ".wbt"
        # Adds the basic world info
        preamble = """#VRML_SIM R2022a utf8
WorldInfo {
info [
    "Simple e-puck simulation that can be controlled with ROS2."
]
    title "ROS2 simulation of the e-puck robot"
}"""

        # Webots likes the viewpoint data to be second so this information is added after
        post_view = """TexturedBackground {
}

TexturedBackgroundLight {
}

Solid {
    children ["""
        # Add the ending syntax to finish the file
        postamble = "\t]\n}"

        with open(filename, "w", encoding = 'UTF-8') as file:
            print(preamble, file = file)
            print(f"""Viewpoint {{
    orientation 0 2 0 1.52
    position {-((scale * self.width)/2 + 0.2)} {-((scale * self.length)/2)} {(self.width + self.length) * scale}
    follow "e-puck"
}}""",
                  file = file)
            print(post_view, file = file)

            # Add the Arena
            print(f"""
        RectangleArena {{
            translation {-(self.width * scale)/2} {-(self.length * scale)/2} 0
            rotation 1 0 0 0
            floorSize {int(self.width * scale) if (self.width * scale > 1) else 1} {int(self.length * scale) if (self.length * scale > 1) else 1}
        }}""",
                  file = file)

            # Add horizontal walls
            self.x_start, self.y_start = 0, 0
            #  cont_wall = False
            length = 1
            wall_thick = 0.01

            # Translations mean the maze appears in the same coordinate system as the svg but any webots lidar may need altering due to its FLU/ENU coordinate system
            for y_index in range(0, self.length):
                for x_index in range(0, self.width):
                    if y_index < (self.length - 1) and self.cell_at(x_index, y_index).walls["S"]:
                        print(f"""
\t\tWall {{
\t\t\ttranslation {-(scale * x_index + scale/2)} {-(scale * (self.length - y_index) - scale)} 0
\t\t\trotation 1 0 0 0
\t\t\tname "wall_{x_index}_{y_index}_s"
\t\t\tsize {scale} {wall_thick} {scale}
\t\t\tappearance Roughcast {{
\t\t\t\tcolorOverride 1 0 0
\t\t\t}}
\t\t}}""",
                              file = file)
                        length += 1
                    if x_index < (self.width - 1) and self.cell_at(x_index, y_index).walls["E"]:
                        print(f"""
\t\tWall {{
\t\t\ttranslation  {-(scale * x_index + scale)} {-(scale * (self.length - y_index) - scale/2)}  0
\t\t\trotation 1 0 0 0
\t\t\tname "wall_{x_index}_{y_index}_e"
\t\t\tsize {wall_thick} {scale} {scale}
\t\t\tappearance Roughcast {{
\t\t\t\tcolorOverride 0 1 0
\t\t\t}}
\t\t}}""",
                              file = file)

            print(postamble, file = file)
        print(f"Written wbt to {getcwd()}/{filename}")

    def write_svg(self, filename, scale = 10):
        """Write an SVG image of the maze to filename."""

        if not filename.endswith(".svg"):
            filename += ".svg"

        # Pad the maze all around by this amount.
        padding = 10

        # Scaling factors mapping maze coordinates to image coordinates
        def write_wall(file, ww_x1, ww_y1, ww_x2, ww_y2, colour = "black"):
            """Write a single wall to the SVG image file handle f."""

            print(f'<line x1="{ww_x1}" y1="{ww_y1}" x2="{ww_x2}" y2="{ww_y2}" stroke="{colour}"/>', file = file)

        # Write the SVG image file for maze
        with open(filename, 'w', encoding = 'UTF-8') as file:
            # SVG preamble and styles.
            print('<?xml version="1.0" encoding="utf-8"?>', file = file)
            print('<svg xmlns="http://www.w3.org/2000/svg"', file = file)
            print('    xmlns:xlink="http://www.w3.org/1999/xlink"', file = file)
            print(f'    width="{(self.width*scale+ 2 * padding):d}" ' + 'height="{(self.length*scale + 2 * padding):d }" ' +
                  'viewBox="{-padding} {-padding} {width + 2 * padding} {height + 2 * padding}">',
                  file = file)
            print('<defs>\n<style type="text/css"><![CDATA[', file = file)
            print('line {', file = file)
            print('    stroke-width: 2;\n}', file = file)
            print(']]></style>\n</defs>', file = file)

            # Draw the "South" and "East" walls of each cell, if present (these
            # are the "North" and "West" walls of a neighbouring cell in general, of course).
            for x in range(self.width):
                for y in range(self.length):

                    # Writes south wall by getting
                    if self.cell_at(x, y).walls['S']:
                        x1, y1, x2, y2 = x * scale, (y + 1) * scale, (x + 1) * scale, (y + 1) * scale
                        write_wall(file, x1, y1, x2, y2, colour = "red")
                    if self.cell_at(x, y).walls['E']:
                        x1, y1, x2, y2 = (x + 1) * scale, y * scale, (x + 1) * scale, (y + 1) * scale
                        write_wall(file, x1, y1, x2, y2, colour = "green")

            # Draw the North and West maze border, which won't have been drawn by the procedure above.
            print(f'<line x1="0" y1="0" x2="{self.width*scale}" y2="0"/>', file = file)
            print('<line x1="0" y1="0" x2="0" y2="{height}"/>', file = file)
            print('</svg>', file = file)
        print(f"Written svg to {getcwd()}/{filename}")

    def find_valid_neighbours(self, cell):
        """Return a list of unvisited neighbours to cell."""

        delta = [('W', (-1, 0)), ('E', (1, 0)), ('S', (0, 1)), ('N', (0, -1))]
        neighbours = []
        for direction, (d_x, d_y) in delta:
            x_2, y_2 = cell.x + d_x, cell.y + d_y
            if (0 <= x_2 < self.width) and (0 <= y_2 < self.length):
                neighbour = self.cell_at(x_2, y_2)
                if neighbour.has_all_walls():
                    neighbours.append((direction, neighbour))
        return neighbours

    def make_maze(self):
        """Creates a valid maze"""
        # Total number of cells
        size = self.width * self.length

        cell_stack = []
        current_cell = self.cell_at(self.x_start, self.y_start)
        # Total number of visited cells during maze construction.
        count = 1

        while count < size:
            neighbours = self.find_valid_neighbours(current_cell)

            if not neighbours:
                # We've reached a dead end: backtrack.
                current_cell = cell_stack.pop()
                continue

            # Choose a random neighbouring cell and move to it.
            direction, next_cell = random.choice(neighbours)
            current_cell.knock_down_wall(next_cell, direction)
            cell_stack.append(current_cell)
            current_cell = next_cell
            count += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Generate a random maze")
    parser.add_argument("-x", "--width", help = "Number of cells wide the maze will be (default = 10)", default = 10)
    parser.add_argument("-y", "--length", help = "Number of cells long the maze will be (defualt = 10)", default = 10)
    parser.add_argument("--svg", help = "Output svg file")
    parser.add_argument("--wbt", help = "Output wbt (Webots world) file")
    args = parser.parse_args()

    # Maze dimensions (ncols, nrows)
    # Maze entry position
    ix, iy = 0, 0
    maze = Maze(int(args.width), int(args.length), ix, iy)
    maze.make_maze()

    print(maze)
    if args.svg:
        maze.write_svg(args.svg)

    if args.wbt:
        maze.write_world(args.wbt)
