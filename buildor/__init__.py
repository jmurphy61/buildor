import logging, numpy, pygame
from .config import *
from .util import *
from collections import defaultdict
from inspect import getsource

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

class App:

    def __init__(self, configuration):
        logging.basicConfig()
        self.logger = logging.getLogger()
        self.configuration = configuration
        self.db_engine = create_engine(f"sqlite:///{self.configuration.DB_PATH}", echo=self.configuration.ECHO)
        self.Session = sessionmaker()
        self.Session.configure(bind=self.db_engine)
        self.session = Session()
    
    def init_window(self, models):
        print(dir(models))
        Base.metadata.create_all(self.db_engine)

        self.running = True
        self.screen = pygame.display.set_mode(self.configuration.SCREEN_SIZE)
        self.set_caption(self.configuration.CAPTION)
        self.set_icon(self.configuration.ICON_PATH)
        self.set_background(self.configuration.BACKGROUND_IMAGE_PATH)

        self.keyboard = defaultdict(lambda: defaultdict(dict))

        self.mouse = Object()
        self.mouse.clicked = False

        self.main_menu = models.Menu(
            app=self,
            left=.2 * self.configuration.SCREEN_SIZE[0],
            top=.2 * self.configuration.SCREEN_SIZE[1],
            width=.6 * self.configuration.SCREEN_SIZE[0],
            height=.6 * self.configuration.SCREEN_SIZE[1],
            r=0,
            g=0,
            b=0,
            title="Main Menu"
        )

        def callback(self):
            self.app.stop()

        self.db_engine.execute(
            menu_buttons.insert().values(
                menu_guid=self.main_menu.guid,
                button_guid=models.Button(
                    app=self,
                    left=50,
                    top=100,
                    width=200,
                    height=50,
                    r=255,
                    g=0,
                    b=0,
                    text='Quit',
                    callback_code=getsource(callback),
                    menu_guid=self.main_menu.guid
                    ).guid
            )
        )
        self.main_clock = pygame.time.Clock()

        self.menu_open = False

    def load_settings(self, settings):
        self.settings = settings

        self.keyboard[self.settings.key_move_south]['opposes'] = self.settings.key_move_north
        self.keyboard[self.settings.key_move_north]['opposes'] = self.settings.key_move_south
        self.keyboard[self.settings.key_move_east]['opposes'] = self.settings.key_move_west
        self.keyboard[self.settings.key_move_west]['opposes'] = self.settings.key_move_east

        self.keyboard[self.settings.key_pan_south]['opposes'] = self.settings.key_move_north
        self.keyboard[self.settings.key_pan_north]['opposes'] = self.settings.key_move_south
        self.keyboard[self.settings.key_pan_east]['opposes'] = self.settings.key_move_west
        self.keyboard[self.settings.key_pan_west]['opposes'] = self.settings.key_move_east

    def stop(self):
        self.running = False
        print('Attempting to save...')
        self.autosave()
    
    def fill_screen(self, rgb_tuple):
        self.screen.fill(rgb_tuple)
    
    def set_background(self, background_image_path):
        self.background_image = pygame.image.load(background_image_path)
        self.screen.blit(self.background_image, (0, 0))

    def set_icon(self, icon_path):
        self.icon = pygame.image.load(icon_path)
        pygame.display.set_icon(self.icon)
    
    def set_caption(self, caption):
        self.caption = caption
        pygame.display.set_caption(caption)
    
    def set_player_character(self, character):
        self.player_character = character
    
    def draw_character(self, character):
        self.screen.blit(character.sprite, (character.x_pos, character.y_pos))
    
    def draw_text(self, text, font, color, surface, x, y):
        text_object = font.render(text, 1, color)
        text_rectangle = text_object.get_rect()
        text_rectangle.topleft = (x, y)
        surface.blit(text_object, text_rectangle)

    def draw_menu(self, menu):
        self.fill_screen(APP.configuration.BACKGROUND_RGB)
        self.draw_text(
            'Main Menu',
            APP.settings.font,
            menu.color,
            APP.screen, 20, 20)

        for button in menu.buttons:
            pygame.draw.rect(APP.screen, button.color, button.rectangle)
    
    def autosave(self):
        self.session.commit()

pygame.init()