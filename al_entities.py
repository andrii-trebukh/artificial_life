from random import randint
from termcolor import colored
from al_world import World


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

    def print_info(self):
        print(self)

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
        
        self.world.total_nolife_objects += 1

        if not self.world.entropy:
            return

        self.energy -= 1
        if self.energy == 0:
            self.world.remove_entity(self)
        

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
        self.min_energy_division = 500 + self.genome[106]# 106 - min energy level cell division
        # 107 - mutation probability, %
        self.breed_each = 10 + self.genome[108] + randint(0, 10)# 108 - breed each n move
        self.len_genome = len(self.genome) - 1

        self.breed_cost = 10
        
        self.count_to_breed = 0

        if self.energy > self.max_energy:
            self.energy = self.max_energy

    def consume_energy(self):
        # print(self.energy)
        value = 1 + self.energy // 100
        self.energy -= value
        # print(self.energy)
    
    def eat_entity(self, entity):
        self.energy += entity.energy
        if self.energy > self.max_energy:
            self.energy = self.max_energy
        self.world.remove_entity(entity)
    
    def print_info(self):
        print(f"\n{self.genome}\n")
        avail_commands = self.commands.keys()
        # output = ""
        for i in range(101):
            if i == self.genome_start:
                color = "red"
            elif self.genome[i] in avail_commands:
                color = "yellow"
            else:
                color = "white"
            print(colored(f"{self.genome[i]: >3} ", color), end="")
            if (i + 1) % 10 == 0:
                print()
        print()
        print (
            ", ".join(
                (
                    f"Start: {self.genome_start}",
                    f"Ttl: {self.genome[102] * 10}",
                    f"Max energy: {self.max_energy}",
                    f"Min energy: {self.min_energy}"
                )
            )
        )
        print (
            ", ".join(
                (
                    f"Cell division energy %: {self.genome[105]}",
                    f"Min cell division energy: {self.min_energy_division}",
                    f"mutation probability, %: {self.genome[107]}",
                    f"breed each n move: {self.breed_each}"
                )
            )
        )
        
        
        
        # ", ".join(
        #     (
        #         f"Start: {entity.genome[101]}",
        #         f"Ttl: {entity.genome[102] * 10}",
        #         f"Max energy: {entity.genome[103] * 10}",
        #         f"Min energy: {entity.genome[104] + 10}"
        #     )
        # )
        # self.info_bar.print_text(3, output)
        # output = ", ".join(
        #     (
        #         f"Cell division energy %: {entity.genome[105]}",
        #         f"Min cell division energy: {entity.genome[106]}",
        #         f"mutation probability, %: {entity.genome[107]}",
        #         f"breed each n move: {entity.genome[108]}"
        #     )
        # print(output)
        print(self)

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
        gen_change = randint(0, self.len_genome)
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
        
        name, _, new_coord = self.check_move()

        if name is None:
            self.move_to(new_coord)

        # match name:
        #     case None:
        #         self.move_to(new_coord)
        #     case "Energy":
        #         self.eat_entity(check)
        #         self.move_to(new_coord)
        #     case "Cell":
        #         self.eat_entity(check)
        #         self.move_to(new_coord)
        
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
        if name == "Rock":
            self.gen_addr = self.genome[self.gen_addr] - 1
            if self.gen_addr == -1:
                self.gen_addr = 100
    
    @command_handler(6, commands)
    def check_food(self):
        self.next_gen_addr()
        name, _, _ = self.check_move()
        if name == "Energy":
            self.gen_addr = self.genome[self.gen_addr] - 1
            if self.gen_addr == -1:
                self.gen_addr = 100

    # @command_handler(7, commands)
    def breed(self):
        # print("breed!")
        if self.energy < self.min_energy_division:
            # self.ttl -= 1
            return False
        
        # tries = 10
        # while True:
        breed_direction = randint(0, 7)
        x, y = self.coord
        dx, dy = self.directions[breed_direction]
        new_coord = (x + dx, y + dy)
        check = self.world.who_is_there(new_coord)
        if check is not None:
            # self.ttl -= 1
            return False
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
        # print(self.energy)
        remaining_energy = self.energy * self.genome[105] // 100
        new_energy = self.energy - remaining_energy
        self.energy = remaining_energy
        # print(self.energy)
        # print(new_energy)
        # print()

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
        if self.world.sun:
            self.energy += self.world.sun_level
            if self.energy > self.max_energy:
                self.energy = self.max_energy
        self.ttl -= 1
        return True
    
    @command_handler(9, commands)
    def check_cell(self):
        self.next_gen_addr()
        name, _, _ = self.check_move()
        if name == "Cell":
            self.gen_addr = self.genome[self.gen_addr] - 1
            if self.gen_addr == -1:
                self.gen_addr = 100
    
    @command_handler(10, commands)
    def eat_energy(self):
        name, check, _ = self.check_move()
        if name == "Energy":
            self.eat_entity(check)
        self.ttl -= 1
        return True
    
    @command_handler(11, commands)
    def eat_cell(self):
        name, check, _ = self.check_move()
        if name == "Cell":
            self.eat_entity(check)
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
        
        self.world.total_life_cells += 1
        
        self.count_to_breed += 1
        if self.count_to_breed == self.breed_each:
            self.count_to_breed = 0
            if self.breed():
                # self.consume_energy()
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
        return f"{self.name}, Id: {self.id}, Energy: {self.energy}, ttl: {self.ttl}"
