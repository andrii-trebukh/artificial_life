from random import randint
from termcolor import colored
from al_entities import Entity, Energy


commands = {}


def command_handler(command):
    def wrapper(func):
        def inner(self):
            return func(self)

        commands[command] = inner

        return inner
    return wrapper


class Cell(Entity):
    def __init__(
            self,
            world,
            id: int,
            coord,
            color,
            genome,
            energy,
            orientation,
            genome_start=None
    ):
        super().__init__(world, id, coord, color, "Cell", genome)
        self.orientation = orientation

        # genome: [---instructions index from 0 to 100---] + [cell property]
        # where cel property is:

        # genome start address
        self.genome_start = genome_start if genome_start else self.genome[101]

        # cell time to live *10, moves
        self.ttl = self.genome[102] * 10

        # max cell energy *10
        self.max_energy = self.genome[103] * 10

        # min cell energy 10 + x
        self.min_energy = 10 + self.genome[104]

        # 105 - % of energy remaining after cell division

        # 106 - min energy level cell division
        self.min_energy_division = 500 + self.genome[106]

        # 107 - mutation probability, %

        self.energy = self.max_energy if energy is None else energy
        self.len_genome = len(self.genome) - 1

        self.breed_cost = self.min_energy_division // 3

        self.internal_counter = 0
        self.internal_counter_criteria = 100

    def eat_entity(self, entity):
        self.energy += entity.energy
        self.world.remove_entity(entity)

    def print_info(self):
        genome_stat = {n: 0 for n in commands}
        for entity in self.world.entities.values():
            if entity.name == "Cell":
                for gen in entity.genome[:101]:
                    if gen in genome_stat:
                        genome_stat[gen] += 1
        total = sum(genome_stat.values())

        print("\n".join(f"{n: >2} {((m * 100) // total): >3}%  {m}"
                        for n, m in genome_stat.items()))
        print(f"\n{self.genome}\n")
        for i in range(101):
            if i == self.genome_start:
                color = "red"
            elif self.genome[i] in commands.keys():
                color = "yellow"
            else:
                color = "white"
            print(colored(f"{self.genome[i]: >3} ", color), end="")
            if (i + 1) % 10 == 0:
                print()
        print()
        print(
            ", ".join(
                (
                    f"Start: {self.genome_start}",
                    f"Ttl: {self.genome[102] * 10}",
                    f"Max energy: {self.max_energy}",
                    f"Min energy: {self.min_energy}"
                )
            )
        )
        print(
            ", ".join(
                (
                    f"Cell division energy, %: {self.genome[105]}",
                    f"Min cell division energy: {self.min_energy_division}",
                    f"mutation probability, %: {self.genome[107]}",
                    # f"breed each n move: {self.breed_each}"
                )
            )
        )
        print(self)

    def next_gen_addr(self):
        self.gen_addr += 1
        if self.gen_addr == 101:
            self.gen_addr = 0

    def make_mutant(self):
        new_genome = list(self.genome)
        gen_change = randint(0, self.len_genome)
        new_gen = randint(0, 100)
        new_genome[gen_change] = new_gen
        return new_genome

    def breed(self):
        if self.energy < self.min_energy_division:
            return False

        breed_direction = randint(0, 7)
        x, y = self.coord
        dx, dy = self.directions[breed_direction]
        new_coord = (x + dx, y + dy)
        check = self.world.who_is_there(new_coord)
        if check is not None:
            return False

        if randint(1, 100) <= self.genome[107]:
            new_genome = self.make_mutant()
            color = list(self.color)
            change_color = randint(0, 2)
            change_color_val = randint(
                color[change_color] - 40,
                color[change_color] + 40
            )
            if change_color_val > 255:
                change_color_val = 255
            elif change_color_val < 0:
                change_color_val = 0
            color[change_color] = change_color_val
            color = tuple(color)
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

    def skip_move(self):
        self.ttl -= 1
        return True

    def go_to_genome_addr(self):
        self.gen_addr = self.genome[self.gen_addr] - 1
        if self.gen_addr == -1:
            self.gen_addr = 100

    @command_handler(0)
    def move(self):
        name, _, new_coord = self.check_move()
        if name is None:
            self.move_to(new_coord)
        self.energy -= 1 + self.energy // 100
        self.ttl -= 1
        return True

    @command_handler(1)
    def clockwise(self):
        self.orientation += 1
        if self.orientation > 7:
            self.orientation = 0
        self.energy -= 1

    @command_handler(2)
    def cclockwise(self):
        self.orientation -= 1
        if self.orientation < 0:
            self.orientation = 7
        self.energy -= 1

    @command_handler(3)
    def set_new_start(self):
        self.next_gen_addr()
        self.genome_start = self.genome[self.gen_addr]

    @command_handler(4)
    def check_obstacle(self):
        self.next_gen_addr()
        name, _, _ = self.check_move()
        if name not in ("Energy", "Cell", None):
            self.go_to_genome_addr()
        self.energy -= 1

    @command_handler(5)
    def check_food(self):
        self.next_gen_addr()
        name, _, _ = self.check_move()
        if name == "Energy":
            self.go_to_genome_addr()
        self.energy -= 1

    @command_handler(6)
    def check_cell(self):
        self.next_gen_addr()
        name, _, _ = self.check_move()
        if name == "Cell":
            self.go_to_genome_addr()
        self.energy -= 1

    @command_handler(7)
    def check_empty(self):
        self.next_gen_addr()
        name, _, _ = self.check_move()
        if name is None:
            self.go_to_genome_addr()
        self.energy -= 1

    @command_handler(8)
    def check_relative(self):
        self.next_gen_addr()
        name, check, _ = self.check_move()
        if name != "Cell":
            return
        diff = 0
        for gen1, gen2 in zip(self.genome, check.genome):
            if gen1 != gen2:
                diff += 1
                if diff > 2:
                    return
        self.go_to_genome_addr()
        self.energy -= 1

    @command_handler(9)
    def eat_energy(self):
        if self.energy < self.max_energy:
            name, check, _ = self.check_move()
            if name == "Energy":
                self.eat_entity(check)
        self.energy -= 1 + self.energy // 100
        self.ttl -= 1
        return True

    @command_handler(10)
    def eat_cell(self):
        if self.energy < self.max_energy:
            name, check, _ = self.check_move()
            if name == "Cell":
                self.eat_entity(check)
        self.energy -= 1 + self.energy // 100
        self.ttl -= 1
        return True

    @command_handler(11)
    def make_photosynthesis(self):
        if self.world.sun and self.energy < self.max_energy:
            self.energy += self.world.sun_level
        self.ttl -= 1
        return True

    @command_handler(12)
    def check_internall_counter(self):
        if self.internal_counter >= self.internal_counter_criteria:
            self.next_gen_addr()
            self.go_to_genome_addr()
            self.internal_counter = 0

    @command_handler(13)
    def set_internall_counter(self):
        self.next_gen_addr()
        self.internal_counter_criteria = self.genome[self.gen_addr]

    @command_handler(14)
    def go_to(self):
        self.next_gen_addr()
        self.go_to_genome_addr()

    def __call__(self):

        if self.inactive:
            return

        self.dump_energy()

        if self.energy <= self.min_energy \
                or self.ttl == 0 or self.energy > self.max_energy:
            self.world.remove_entity(self)
            if self.energy <= 0:
                return
            energy = Energy(
                self.world,
                self.world.get_id(),
                self.coord,
                self.energy
            )
            self.world.add_entity(energy)
            return

        self.world.total_life_cells += 1

        if self.internal_counter < self.internal_counter_criteria:
            self.internal_counter += 1

        if self.breed():
            return

        self.gen_addr = self.genome_start

        for i in range(102):
            gen = self.genome[self.gen_addr]
            if gen in commands.keys():
                if commands[gen](self):
                    return
            self.next_gen_addr()
        self.skip_move()

    def __str__(self):
        return f"{self.name}, Id: {self.id}, Energy: {self.energy}, "\
            f"ttl: {self.ttl}"
