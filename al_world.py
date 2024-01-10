import gc
from random import randint
from time import sleep
from typing import Any
import pygame
from info_bar import InfoBar
from termcolor import colored


class World():
    def __init__(
            self,
            size: tuple = (640, 480),
            bg_color: tuple | int = 0x000000
    ):

        pygame.init()
        logo = pygame.image.load("logo32x32.png")
        pygame.display.set_icon(logo)
        pygame.display.set_caption("Artificial life simulator")
        
        self.screen = pygame.display.set_mode(size)
        self.screen.fill(bg_color)
        pygame.display.flip()
        self.entities = {}
        self.collide_list = {}
        self.remove_entities = []
        self.next_entity_id = 0
        self.bg_color = bg_color

        self.sun_level = 1

        self.go_life = False
        self.step_by_step = False

        max_x = self.screen.get_width() - 1
        max_y = self.screen.get_height() - 1 - 5 * 14
        self.max_coord = (max_x, max_y)

        self.focus_entity_id = None

        info_bar_height = 5 * 14
        self.info_bar = InfoBar(
            self.screen,
            0,
            self.screen.get_height() - info_bar_height,
            self.screen.get_width(),
            info_bar_height,
            0x808080
        )
        self.info_bar.assign_button(0, "Go", self.start_pause)
        self.info_bar.assign_button(1, "Step", self.step_forward)
        self.info_bar.assign_button(3, "Light off", self.switch_off_the_light)
        
    def draw_pixel(
            self,
            coords: tuple,
            color: int = 0xFFFFFF
    ):
        pixel_array = pygame.PixelArray(self.screen)
        x, y = coords
        pixel_array[x, y] = color
        pixel_array.close()
        
    def get_id(self):
        entity_id = self.next_entity_id
        self.next_entity_id += 1
        return entity_id
    
    def add_entity(self, new_entity):
        entity_id = new_entity.id
        coord = new_entity.coord
        color = new_entity.color
        self.entities[entity_id] = new_entity
        self.draw_pixel(coord, color)
        self.collide_list[coord] = entity_id

    def remove_entity(self, entity):
        entity_id = entity.id
        coord = entity.coord
        entity.inactive = True
        self.remove_entities.append(entity_id)
        self.collide_list.pop(coord)
        self.draw_pixel(coord, self.bg_color)
    
    def who_is_there(self, coord: tuple):
        entity_id = self.collide_list.get(coord)
        if entity_id is None:
            return None
        else:
            return self.entities[entity_id]
        
    def start_pause(self):
        self.go_life = not self.go_life
        text_button = "Pause" if self.go_life else "Go"
        self.info_bar.assign_button(0, text_button, self.start_pause)
        func = None if self.go_life else self.step_forward
        self.info_bar.assign_button(1, "Step", func)
    
    def step_forward(self):
        self.step_by_step = True
        self.go_life = True

    def switch_off_the_light(self):
        self.sun_level = 0
    
    def genom_info(self, entity):
        entity.print_genome()
        output = ", ".join(
            (
                f"Start: {entity.genome[101]}",
                f"Ttl: {entity.genome[102] * 10}",
                f"Max energy: {entity.genome[103] * 10}",
                f"Min energy: {entity.genome[104] + 10}"
            )
        )
        self.info_bar.print_text(3, output)
        output = ", ".join(
            (
                f"Cell division energy %: {entity.genome[105]}",
                f"Min cell division energy: {entity.genome[106]}",
                f"mutation probability, %: {entity.genome[107]}"
            )
        )
        self.info_bar.print_text(4, output)
    
    def loop(self):

        running = True

        mouse_pressed = False
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.info_bar()

            if self.go_life:
                keys = list(self.entities.keys())
                for key in keys:
                    self.entities[key]()
                for remove_entity in self.remove_entities:
                    self.entities.pop(remove_entity)
                self.remove_entities = []
            
            self.info_bar.print_text(0, f"Total objects: {len(self.entities)}")

            if not self.go_life:
                mouse = pygame.mouse.get_pos()
                entity = self.who_is_there(mouse)
                if entity is None:
                    self.info_bar.print_text(1, None)
                else:
                    self.info_bar.print_text(1, str(entity))
                    if pygame.mouse.get_pressed()[0] and not mouse_pressed:
                        mouse_pressed = True
                        self.focus_entity_id = entity.id
                        if entity.genome is not None:
                            self.genom_info(entity)
                        else:
                            self.info_bar.print_text(3, None)
                            self.info_bar.print_text(4, None)
                    elif not pygame.mouse.get_pressed()[0]:
                        mouse_pressed = False
            
            self.info_bar.print_text(0, f"Total objects: {len(self.entities)}")

            if self.focus_entity_id is not None:
                entity = self.entities.get(self.focus_entity_id)
                if entity is None:
                    self.info_bar.print_text(2, None)
                    self.info_bar.print_text(3, None)
                    self.info_bar.print_text(4, None)
                else:
                    self.info_bar.print_text(2, str(entity))                  

            if self.step_by_step:
                self.go_life = False
                self.step_by_step = False


            # sleep(0.005)
            pygame.display.flip()


class Entity():
    def __init__(
            self,
            world: World,
            id: int,
            coord: tuple = (0,0),
            color: int = 0xFFFFFF,
            name: int | None = None,
            genome: tuple | None = None
    ):
        self.name = name
        self.id = id
        self.color = color
        self.coord = coord
        self.world = world
        self.genome = genome
        self.inactive = False
    
    def move_to(self, new_coord):
        coord = self.coord
        color = self.color
        bg_color = self.world.bg_color
        self.world.draw_pixel(coord, bg_color)
        self.world.draw_pixel(new_coord, color)
        self.coord = new_coord
        self.world.collide_list.pop(coord)
        self.world.collide_list[new_coord] = self.id

    def __call__(self):
        pass
    
    def __str__(self):
        return f"{self.name}, Id: {self.id}"

class Rock(Entity):
    def __init__(
            self,
            world: World,
            id: int,
            coord: tuple = (0, 0),
    ):
        super().__init__(world, id, coord, 0xff0000, "Rock")

class Energy(Entity):
    def __init__(
            self,
            world: World,
            id: int,
            coord,
            energy
    ):
        super().__init__(world, id, coord, 0xFFFFFF, "Energy")
        self.energy = energy
    
    def __str__(self):
        return f"{self.name}, Id: {self.id}, Energy: {self.energy}"
    
    def __call__(self):
        if self.inactive:
            return
        self.energy -= 1
        if self.energy == 0:
            self.world.remove_entity(self)
            # print(self)
            

class Cell(Entity):
    
    commands = {}

    directions = {
        0: (-1, -1),
        1: (0, -1),
        2: (1, -1),
        3: (1, 0),
        4: (1, 1),
        5: (0, 1),
        6: (-1, 1),
        7: (-1, 0)
    }

    def __init__(self,
                 world: World,
                 id: int,
                 coord,
                 color,
                 genome,
                 energy,
                 orientation
    ):
        super().__init__(world, id, coord, color, "Cell", genome)
        self.energy = energy
        self.orientation = orientation
        
        # genome: [---instructions index from 0 to 100---] + [cell property]
        # where cel property is:
        self.genome_start = self.genome[101] # genome start address
        self.ttl = self.genome[102] * 10 # cell time to live *10, moves
        self.max_energy = self.genome[103] * 10 # max cell energy *10
        self.min_energy = 10 + self.genome[104] # min cell energy 10 + x
        # 105 - % of energy remaining after cell division
        # 106 - min energy level cell division
        # 107 - mutation probability, %

        self.breed_cost = 10

        if self.energy > self.max_energy:
            self.energy = self.max_energy

    def consume_energy(self):
        value = 1 + self.energy // 100
        self.energy -= value
    
    def eat_entity(self, entity):
        self.energy += entity.energy
        if self.energy > self.max_energy:
            self.energy = self.max_energy
        self.world.remove_entity(entity)
    
    def print_genome(self):
        avail_commands = self.commands.keys()
        output = ""
        for i in range(101):
            if i == self.genome_start:
                color = "red"
            elif self.genome[i] in avail_commands:
                color = "yellow"
            else:
                color = "white"
            output += colored(f"{self.genome[i]: >3} ", color)
            if (i + 1) % 10 == 0:
                output += "\n"
        
        print(output)

    def next_gen_addr(self):
        self.gen_addr += 1
        if self.gen_addr == 101:
            self.gen_addr = 0

    def check_move(self):
        x, y = self.coord
        dx, dy = self.directions[self.orientation]
        new_coord = (x + dx, y + dy)
        check = self.world.who_is_there(new_coord)
        name = None
        if check is not None:
            name = check.name
        return (name, check, new_coord)
    
    def make_mutant(self):
        new_genome = list(self.genome)
        gen_change = randint(0, 107)
        new_gen = randint(0, 100)
        new_genome[gen_change] = new_gen
        return new_genome

    def command_handler(command, commands):
        def wrapper(func):
            def inner(self):
                return func(self)

            commands[command] = inner

            return inner
        return wrapper
    
    @command_handler(0, commands)
    def move(self):
        
        name, check, new_coord = self.check_move()

        match name:
            case None:
                self.move_to(new_coord)
            case "Energy":
                self.eat_entity(check)
                self.move_to(new_coord)
            case "Cell":
                self.eat_entity(check)
                self.move_to(new_coord)
        
        self.consume_energy()
        self.ttl -= 1
        return True

    @command_handler(1, commands)
    def clockwise(self):
        self.orientation += 1
        if self.orientation > 7:
            self.orientation = 0

    @command_handler(2, commands)
    def cclockwise(self):
        self.orientation -= 1
        if self.orientation < 0:
            self.orientation = 7
    
    @command_handler(3, commands)
    def skip_move(self):
        self.ttl -= 1
        return True
    
    @command_handler(4, commands)
    def set_new_start(self):
        self.next_gen_addr()
        self.genome_start = self.genome[self.gen_addr]
    
    @command_handler(5, commands)
    def check_obstacle(self):
        self.next_gen_addr()
        name, _, _ = self.check_move()
        if name in ("Rock", ):
            self.gen_addr = self.genome[self.gen_addr] - 1
            if self.gen_addr == -1:
                self.gen_addr = 100
    
    @command_handler(6, commands)
    def check_food(self):
        self.next_gen_addr()
        name, _, _ = self.check_move()
        if name in ("Energy", "Cell"):
            self.gen_addr = self.genome[self.gen_addr] - 1
            if self.gen_addr == -1:
                self.gen_addr = 100

    @command_handler(7, commands)
    def breed(self):
        if self.energy < self.genome[106]:
            self.ttl -= 1
            return True
        
        # tries = 10
        # while True:
        breed_direction = randint(0, 7)
        x, y = self.coord
        dx, dy = self.directions[breed_direction]
        new_coord = (x + dx, y + dy)
        check = self.world.who_is_there(new_coord)
        if check is not None:
            self.ttl -= 1
            return True
        # if breed_direction != self.orientation and \
        # check is None:
        #     break
            # if tries == 0:
            #     self.ttl -= 1
            #     return True
            # tries -= 1
        
        if randint(0, 100) <= self.genome[107]:
            new_genome = self.make_mutant()
            color = (
                randint(80, 255),
                randint(80, 255),
                randint(80, 255)
            )
        else:
            new_genome = self.genome
            color = self.color

        self.energy -= self.breed_cost
        remaining_energy = self.energy * self.genome[105] // 100
        new_energy = self.energy - remaining_energy
        self.energy = remaining_energy

        cell = Cell(
            self.world,
            self.world.get_id(),
            new_coord,
            color,
            new_genome,
            new_energy,
            breed_direction
        )

        self.world.add_entity(cell)

        self.ttl -= 1
        return True

    @command_handler(8, commands)
    def make_photosynthesis(self):
        self.energy += self.world.sun_level
        if self.energy > self.max_energy:
            self.energy = self.max_energy
        self.ttl -= 1
        return True
    
    
    def __call__(self):

        if self.inactive:
            return

        if self.energy <= self.min_energy or self.ttl == 0:
            self.world.remove_entity(self)
            if self.energy == 0:
                return
            energy = Energy(self.world, self.world.get_id(), self.coord, self.energy)
            self.world.add_entity(energy)
            return

        avail_commands = self.commands.keys()
        self.gen_addr = self.genome_start
        # end_move = None
        for i in range(100):
            gen = self.genome[self.gen_addr]
            if gen in avail_commands:
                if self.commands[gen](self):
                    return
            self.next_gen_addr()
            # self.gen_addr += 1
            # if self.gen_addr == 100:
            #     self.gen_addr = 0
        self.skip_move()
        

    def __str__(self):
        return f"{self.name}, Id: {self.id}, Energy: {self.energy}, ttl: {self.ttl}, Start: {self.genome_start}"
            

            





class Ball(Entity):
    def __init__(
            self,
            world: World,
            id: int,
            coord: tuple = (0, 0),
            color: int = 0xFFFFFF,
            step_x = 1,
            step_y = 1
    ):
        super().__init__(world, id, coord, color, "ball")
        self.step_x = step_x
        self.step_y = step_y
        self.check_boundary()
    
    def reverse_step_x(self):
        self.step_x *= -1

    def reverse_step_y(self):
        self.step_y *= -1
    
    def __str__(self) -> str:
        return f"Id:{self.id}, coord:{self.coord}, steps:{self.step_x}, {self.step_y}"

    def check_boundary(self):
        x, y = self.coord
        max_x, max_y = self.world.max_coord
        if(
            (x == max_x and self.step_x == 1)
            or
            (x == 0 and self.step_x == -1)
        ):
            self.reverse_step_x()
        
        if(
            (y == max_y and self.step_y == 1)
            or
            (y == 0 and self.step_y == -1)
        ):
            self.reverse_step_y()

    def __call__(self):
        x, y = self.coord
        x += self.step_x
        y += self.step_y
        
        other_ball = self.world.who_is_there((x, y))
        if other_ball:
            step_x = other_ball.step_x
            step_y = other_ball.step_y
            if step_x != self.step_x:
                other_ball.reverse_step_x()
                self.reverse_step_x()
            if step_y != self.step_y:
                other_ball.reverse_step_y()
                self.reverse_step_y()
            other_ball.check_boundary()
        else:
            self.move_to((x, y))
        
        self.check_boundary()
        
    
