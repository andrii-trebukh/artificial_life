from random import shuffle


class Entity():
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

    def __init__(
            self,
            world,
            id: int,
            coord: tuple = (0, 0),
            color: int = 0xFFFFFF,
            name: int | None = None,
            genome: tuple | None = None,
            energy: int = 0
    ):
        self.name = name
        self.id = id
        self.color = color
        self.coord = coord
        self.world = world
        self.genome = genome
        self.inactive = False
        self.energy = energy
        self.max_energy = 1000
        self.orientation = 0

    def move_to(self, new_coord):
        coord = self.coord
        color = self.color
        bg_color = self.world.bg_color
        self.world.draw_pixel(coord, bg_color)
        self.world.draw_pixel(new_coord, color)
        self.coord = new_coord
        self.world.collide_list.pop(coord)
        self.world.collide_list[new_coord] = self.id

    def check_move(self, orientation=None):
        if not orientation:
            orientation = self.orientation
        x, y = self.coord
        dx, dy = self.directions[orientation]
        new_coord = (x + dx, y + dy)
        check = self.world.who_is_there(new_coord)
        name = None
        if check is not None:
            name = check.name
        return (name, check, new_coord)

    def dump_energy(self):
        if self.energy <= self.max_energy:
            return
        delta = self.energy - self.max_energy
        orientation_order = list(range(8))
        shuffle(orientation_order)
        for orientation in orientation_order:
            name, _, coord = self.check_move(orientation)
            if name is None:
                energy = Energy(self.world, self.world.get_id(), coord, delta)
                self.world.add_entity(energy)
                self.energy = self.max_energy
                return
        energy_entities = {}
        for orientation in orientation_order:
            name, check, _ = self.check_move(orientation)
            if name == "Energy":
                energy_entities[check.energy] = check
        if energy_entities:
            _, check = sorted(energy_entities.items())[0]
            check.energy += delta
            self.energy = self.max_energy
            return
        for orientation in orientation_order:
            name, check, coord = self.check_move(orientation)
            if name == "Cell":
                self.world.remove_entity(check)
                energy = Energy(self.world, self.world.get_id(), coord, delta)
                self.world.add_entity(energy)
                self.energy = self.max_energy
                return

    def print_info(self):
        print(self)

    def __call__(self):
        pass

    def __str__(self):
        return f"{self.name}, Id: {self.id}, Energy: {self.energy}"


class Rock(Entity):
    def __init__(
            self,
            world,
            id: int,
            coord: tuple = (0, 0),
    ):
        super().__init__(world, id, coord, 0xff0000, "Rock")


class Geyser(Entity):
    def __init__(
            self,
            world,
            id: int,
            coord: tuple = (0, 0),
            prod_energy: int = 500
    ):
        super().__init__(world, id, coord, 0xff0000, "Geyser")
        self.prod_energy = prod_energy

    def __call__(self):
        if self.world.geyser:
            self.energy += self.prod_energy
        self.dump_energy()


class Energy(Entity):
    def __init__(
            self,
            world,
            id: int,
            coord,
            energy
    ):
        super().__init__(world, id, coord, 0xFFFFFF, "Energy", energy=energy)

    def __call__(self):
        if self.inactive:
            return

        self.dump_energy()

        self.world.total_nolife_objects += 1

        if not self.world.entropy:
            return

        self.energy -= 1
        if self.energy == 0:
            self.world.remove_entity(self)
