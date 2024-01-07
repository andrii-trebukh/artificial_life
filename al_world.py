from time import sleep
from typing import Any
import pygame


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
        
        self.__screen = pygame.display.set_mode(size)
        self.__screen.fill(bg_color)
        pygame.display.flip()
        self.entities = {}
        self.collide_list = {}
        self.__next_entity_id = 0
        self.__bg_color = bg_color
        
        max_x = self.__screen.get_width() - 1
        max_y = self.__screen.get_height() - 1
        self.__max_coord = (max_x, max_y)

    
    # @property
    # def screen(self):
    #     return self.__screen
    
    @property
    def bg_color(self):
        return self.__bg_color
    
    @property
    def max_coord(self):
        return self.__max_coord
    
    def draw_pixel(
            self,
            coords: tuple,
            color: int = 0xFFFFFF
    ):
        pixel_array = pygame.PixelArray(self.__screen)
        x, y = coords
        pixel_array[x, y] = color
        pixel_array.close()
        
    def get_id(self):
        entity_id = self.__next_entity_id
        self.__next_entity_id += 1
        return entity_id
    
    def add_entity(self, new_entity):
        entity_id = new_entity.id
        coord = new_entity.coord
        color = new_entity.color
        self.entities[entity_id] = new_entity
        self.draw_pixel(coord, color)
        self.collide_list[coord] = entity_id
    
    def who_is_there(self, coord: tuple):
        entity_id = self.collide_list.get(coord)
        if entity_id is None:
            return None
        else:
            return self.entities[entity_id]

    def loop(self):

        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
        
            for entity in self.entities.values():
                entity()

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
            genom: tuple | None = None
    ):
        self.__name = name
        self.__id = id
        self.__color = color
        self.__coord = coord
        self.__world = world
        self.__genom = None
    
    @property
    def name(self):
        return self.__name
    
    @property
    def id(self):
        return self.__id
    
    @property
    def color(self):
        return self.__color
    
    @property
    def coord(self):
        return self.__coord
    
    @property
    def world(self):
        return self.__world
    
    @property
    def genom(self):
        return self.__genom
    
    def move_to(self, new_coord):
        coord = self.__coord
        color = self.__color
        bg_color = self.__world.bg_color
        self.__world.draw_pixel(coord, bg_color)
        self.__world.draw_pixel(new_coord, color)
        self.__coord = new_coord
        self.__world.collide_list.pop(coord)
        self.__world.collide_list[new_coord] = self.__id

    def __call__(self):
        pass

# class Rock(Entity):

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
        self.__step_x = step_x
        self.__step_y = step_y
        self.check_boundary()
    
    @property
    def step_x(self):
        return self.__step_x
    
    @property
    def step_y(self):
        return self.__step_y
    
    def reverse_step_x(self):
        self.__step_x *= -1

    def reverse_step_y(self):
        self.__step_y *= -1
    
    def __str__(self) -> str:
        return f"Id:{self.id}, coord:{self.coord}, steps:{self.__step_x}, {self.__step_y}"

    def check_boundary(self):
        x, y = self.coord
        max_x, max_y = self.world.max_coord
        if(
            (x == max_x and self.__step_x == 1)
            or
            (x == 0 and self.__step_x == -1)
        ):
            self.reverse_step_x()
        
        if(
            (y == max_y and self.__step_y == 1)
            or
            (y == 0 and self.__step_y == -1)
        ):
            self.reverse_step_y()

    def __call__(self):
        x, y = self.coord
        x += self.__step_x
        y += self.__step_y
        
        other_ball = self.world.who_is_there((x, y))
        if other_ball:
            step_x = other_ball.step_x
            step_y = other_ball.step_y
            if step_x != self.__step_x:
                other_ball.reverse_step_x()
                self.reverse_step_x()
            if step_y != self.__step_y:
                other_ball.reverse_step_y()
                self.reverse_step_y()
            other_ball.check_boundary()
        else:
            self.move_to((x, y))
        
        self.check_boundary()
        
    
