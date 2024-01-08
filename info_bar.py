import pygame


class Button():
    def __init__(
            self,
            screen,
            x,
            y,
            width,
            height,
            onclick_function=None,
            color_normal="#aaaaaa",
            color_hover="#666666",
            color_pressed="#333333",
            color_text="#141414"
    ):
        self.screen = screen
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.onclick_function = onclick_function
        self.already_pressed = False
        self.color_normal = color_normal
        self.color_hover = color_hover
        self.color_pressed = color_pressed
        self.color_text = color_text

        self.button_surface = pygame.Surface((width, height))
        self.button_rect = self.button_surface.get_rect()
        self.button_rect.topleft = (x, y)

        self.font = pygame.font.SysFont("LiberationMono", 14)

    def button_activate(self, button_text, onclick_function):
        self.onclick_function = onclick_function
        self.button_text_render = self.font.render(button_text, True, self.color_text)
        self.button_text_rect = self.button_text_render.get_rect()
        self.button_text_rect.center = self.button_rect.center

    def __call__(self):
        if self.onclick_function is None:
            return
        mouse = pygame.mouse.get_pos()
        if self.button_rect.collidepoint(mouse):
            self.button_surface.fill(self.color_hover)
            if pygame.mouse.get_pressed()[0]:
                self.button_surface.fill(self.color_pressed)
                if not self.already_pressed:
                    self.already_pressed = True
                    self.onclick_function()
            else:
                self.already_pressed = False
        else:
            self.button_surface.fill(self.color_normal)
        self.screen.blit(self.button_surface, self.button_rect)
        self.screen.blit(self.button_text_render, self.button_text_rect)


class TextField():
    def __init__(
            self,
            screen,
            x,
            y,
            width,
            height,
            color_text="#CCCCCC"
    ):
        self.screen = screen
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color_text = color_text
        self.text = None
        self.font = pygame.font.SysFont("LiberationMono", 14)

    def text_set(self, text):
        if text is None:
            self.text = None
            return
        self.text = self.font.render(text, True, self.color_text)
        self.text_rect = self.text.get_rect()
        self.text_rect.topleft = (self.x, self.y)

    def __call__(self):
        if self.text is None:
            return
        self.screen.blit(self.text, self.text_rect)


class InfoBar():
    def __init__(
            self,
            screen,
            x,
            y,
            width,
            height,
            color_bar="#000000"
    ):
        self.screen = screen
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color_bar = color_bar

        self.buttons = []
        self.text = []

        self.bar_surface = pygame.Surface((self.width, self.height))
        self.bar_rect = self.bar_surface.get_rect()
        self.bar_rect.topleft = (x, y)

        self.bar_surface.fill(self.color_bar)

        button_height = 16
        button_width = 100
        text_height = 14
        text_width = self.screen.get_width() - 1 - button_width

        for i in range(4, 0, -1):
            button = Button(
                self.screen,
                self.screen.get_width() - 1 - button_width,
                self.screen.get_height() - (1 + button_height) * i,
                button_width,
                button_height
            )
            self.buttons.append(button)

        for i in range(5, 0, -1):
            text = TextField(
                self.screen,
                0,
                self.screen.get_height() - text_height * i,
                text_width,
                text_height,
            )
            self.text.append(text)

    def assign_button(self, index, button_text, onclick_function):
        button = self.buttons[index]
        button.button_activate(button_text, onclick_function)

    def print_text(self, index, text):
        text_field = self.text[index]
        text_field.text_set(text)

    def __call__(self):
        self.screen.blit(self.bar_surface, self.bar_rect)

        for button in self.buttons:
            button()

        for text in self.text:
            text()
