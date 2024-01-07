from random import choice, randint

from al_world import World, Ball



def main():
    
    world = World()

    max_x, max_y = world.max_coord

    i = 100000
    i -= 1
    while i:
        x = randint(0, max_x)
        y = randint(0, max_y)
        if world.who_is_there((x, y)) is None:
            r = randint(80, 255)
            g = randint(80, 255)
            b = randint(80, 255)
            step_x = choice((1, -1))
            step_y = choice((1, -1))
            ball_id = world.get_id()
            ball = Ball(world, ball_id, (x, y), (r, g, b), step_x, step_y)
            world.add_entity(ball)
            i -= 1
            
    world.loop()


if __name__ == "__main__":
    main()