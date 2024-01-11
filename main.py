#!/bin/python3

from random import randint
from al_world import World
from al_entities import Cell, Rock


def main():
        
    # world = World((1900,900))
    world = World((400,200))

    # build the perimeter wall
    max_x, max_y = world.max_coord
    for i in range(max_x + 1):
        for j in (0, max_y):
            rock = Rock(world, world.get_id(), (i, j))
            world.add_entity(rock)
    
    for i in range (1, max_y):
        for j in (0, max_x):
            rock = Rock(world, world.get_id(), (j, i))
            world.add_entity(rock)
    
    i = 10000
    while i:
        x = randint(0, max_x)
        y = randint(0, max_y)
        if world.who_is_there((x, y)) is None:
            r = randint(80, 255)
            g = randint(80, 255)
            b = randint(80, 255)

            orientation = randint(0,7)
            
            startpoint = randint(0, 99)

            genome = []
            

            for j in range(109):
                genome.append(randint(0, 100))
            
            genome[100] = startpoint
            
            cell = Cell(world, world.get_id(), (x, y), (r, g, b), genome, 1000, orientation)
            world.add_entity(cell)
        i -= 1
    
    # genome = []

    # for i in range(108):
    #     # genome.append(randint(0, 100))
    #     genome.append(100)
    
    # genome[101] = 0
    # genome[0] = 7
    # # genome[1] = 10
    # # genome[2] = 0
    # # genome[10] = 1
    # # genome[11] = 1
    # # genome[12] = 0
    # # genome[6] = 0
    # # genome[10] = 0
   
    # genome[102] = 100
    # genome[104] = 100
    # genome[105] = 25
    # genome[106] = 0
    # genome[107] = 50
 
    # cell = Cell(world, world.get_id(), (10, 10), 0x00ff00, genome, 875, 3)
    # world.add_entity(cell)

    # rock = Rock(world, world.get_id(), (13, 10))
    # world.add_entity(rock)
           
    world.loop()


if __name__ == "__main__":
    main()