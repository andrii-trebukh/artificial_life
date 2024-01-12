import gc
from random import randint
from time import sleep
from typing import Any
import pygame
from info_bar import InfoBar


class World():
    def __init__(
            self,
            size: tuple = (640, 480),
            bg_color: tuple | int = 0x000000,
            sun_level: int = 1,
            scale: int = 1
    ):

        pygame.init()
        logo = pygame.image.load("logo32x32.png")
        pygame.display.set_icon(logo)
        pygame.display.set_caption("Artificial life simulator")
        
        self.scale = scale
        info_bar_height = 5 * 14
        width, height = size
        width *= scale
        height = height * scale + info_bar_height
        self.screen = pygame.display.set_mode((width, height))
        self.screen.fill(bg_color)
        pygame.display.flip()
        self.entities = {}
        self.collide_list = {}
        self.remove_entities = []
        self.next_entity_id = 0
        self.bg_color = bg_color

        self.sun_level = sun_level
        self.sun = False        
        self.entropy = True

        self.go_life = False
        self.step_by_step = False

        max_x = size[0] - 1
        max_y = size[1] - 1
        self.max_coord = (max_x, max_y)

        self.total_life_cells = 0
        self.total_nolife_objects = 0

        self.pixel_surface = pygame.Surface((scale, scale))

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

        self.entropy_toggle()
        self.sun_toggle()
        
    def draw_pixel(
            self,
            coords: tuple,
            color: int = 0xFFFFFF
    ): 
        x, y = coords
        x *= self.scale
        y *= self.scale
        # pixel_array = pygame.PixelArray(self.screen)
        # pixel_array[x, y] = color
        # pixel_array.close()
        self.pixel_surface.fill(color)
        self.screen.blit(self.pixel_surface, (x, y))
        
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

    def sun_toggle(self):
        self.sun = not self.sun
        msg = "Off sun" if self.sun else "On sun"
        self.info_bar.assign_button(3, msg, self.sun_toggle)

    def entropy_toggle(self):
        self.entropy = not self.entropy
        msg = "Off entropy" if self.entropy else "On entropy"
        self.info_bar.assign_button(2, msg, self.entropy_toggle)
    
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
            
                self.info_bar.print_text(0, f"Total objects: {self.total_life_cells + self.total_nolife_objects}")
                self.info_bar.print_text(2, f"Total life cells: {self.total_life_cells}")
                self.info_bar.print_text(3, f"No life objects: {self.total_nolife_objects}")
                self.total_life_cells = 0
                self.total_nolife_objects = 0

            if not self.go_life:
                x, y = pygame.mouse.get_pos()
                x //= self.scale
                y //= self.scale
                entity = self.who_is_there((x, y))
                if entity is None:
                    self.info_bar.print_text(1, None)
                else:
                    self.info_bar.print_text(1, str(entity))
                    if pygame.mouse.get_pressed()[0] and not mouse_pressed:
                        entity.print_info()
                        mouse_pressed = True
                    elif not pygame.mouse.get_pressed()[0]:
                        mouse_pressed = False
            
            if self.step_by_step:
                self.go_life = False
                self.step_by_step = False

            pygame.display.flip()
