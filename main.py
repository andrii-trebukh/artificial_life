#!/bin/python3

from random import randint
from al_world import World
from al_entities import Cell, Rock, Geyser


def main():
    world = World((400, 200), scale=4)

    # build the perimeter wall
    max_x, max_y = world.max_coord
    for i in range(max_x + 1):
        for j in (0, max_y):
            rock = Rock(world, world.get_id(), (i, j))
            world.add_entity(rock)

    for i in range(1, max_y):
        for j in (0, max_x):
            rock = Rock(world, world.get_id(), (j, i))
            world.add_entity(rock)

    world.loop()


if __name__ == "__main__":
    main()
