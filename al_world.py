from time import sleep
from typing import Any
import pygame
from info_bar import InfoBar


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
        self.next_entity_id = 0
        self.bg_color = bg_color

        self.go_life = False

        max_x = self.screen.get_width() - 1
        max_y = self.screen.get_height() - 1 - 5 * 14
        self.max_coord = (max_x, max_y)

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

    def loop(self):

        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.info_bar()

            if self.go_life:
                for entity in self.entities.values():
                    entity()
            
            if not self.go_life:
                mouse = pygame.mouse.get_pos()
                entity = self.who_is_there(mouse)
                if entity is None:
                    self.info_bar.print_text(1, None)
                else:
                    self.info_bar.print_text(1, str(entity))


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
        self.name = name
        self.id = id
        self.color = color
        self.coord = coord
        self.world = world
        self.genom = None
    
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
        
    
