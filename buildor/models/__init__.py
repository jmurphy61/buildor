import math, names, pygame
from .. import APP
from ..static import img
from ..util import *
from importlib import resources
from sqlalchemy import *
from sqlalchemy.orm import relationship, Session, backref, reconstructor

menu_buttons = Table('menu_buttons', Base.metadata,
    Column('menu_guid', String(32), ForeignKey('menu.guid')),
    Column('button_guid', String(32), ForeignKey('button.guid')))

class Button(Base):
    left = Column(Integer, nullable=False)
    top = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    text = Column(String)
    r = Column(Integer, nullable=False, default=255)
    g = Column(Integer, nullable=False, default=255)
    b = Column(Integer, nullable=False, default=255)
    callback_code = Column(Text)
    menu_guid = Column(String(32), ForeignKey('menu.guid'), nullable=False)

    @property
    def clicked(self):
        return self.pressed and not self.app.mouse.clicked

    @property
    def callback(self):
        return compile(self.callback_code, '<string>', 'exec')

    @property
    def color(self):
        return (self.r, self.g, self.b)

    @property
    def rectangle(self):
        return pygame.Rect(self.top, self.left, self.width, self.height)

    def __init__(self, **kwargs):
        self.app = kwargs.get('app')
        kwargs.pop('app')
        super().__init__(**kwargs)
        self.app.session.add(self)
        self.app.session.commit()
        self.pressed = False
    
    @reconstructor
    def init_on_load(self):
        self.pressed = False

class Menu(Base):
    left = Column(Integer, nullable=False)
    top = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    title = Column(String)
    r = Column(Integer, nullable=False, default=255)
    g = Column(Integer, nullable=False, default=255)
    b = Column(Integer, nullable=False, default=255)

    buttons = relationship(
        Button,
        backref=backref(
            'menu',
            uselist=True
        ),
        uselist=True,
        secondary=menu_buttons
    )

    @property
    def color(self):
        return (self.r, self.g, self.b)

    @property
    def rectangle(self):
        return pygame.Rect(self.top, self.left, self.width, self.right)

    def __init__(self, **kwargs):
        self.app = kwargs.get('app')
        kwargs.pop('app')
        super().__init__(**kwargs)
        self.app.session.add(self)
        self.app.session.commit()


character_settings = Table('character_settings', Base.metadata,
    Column('character_guid', String(32), ForeignKey('character.guid')),
    Column('settings_guid', String(32), ForeignKey('settings.guid')))

class Character(Base):
    __tablename__ = 'character'

    sex = Column(String)
    name = Column(String, nullable=False)
    sprite_path = Column(String, nullable=False)
    x_pos = Column(Integer, nullable=False, default=0)
    y_pos = Column(Integer, nullable=False, default=0)
    walking_speed = Column(Integer, nullable=False, default=1)
    speed = Column(Float, nullable=False, default=0)
    facing = Column(Integer, nullable=False, default=3 * math.pi / 2)
    max_stamina = Column(Integer, nullable=False, default=500)
    stamina = Column(Float, nullable=False, default=500)
    stamina_regen = Column(Integer, nullable=False, default=1)
    fatigue = Column(Integer, nullable=False, default=0)

    settings_guid = Column(String(32), ForeignKey('settings.guid'), primary_key=True)

    @property
    def stamina_ratio(self):
        return self.stamina / self.max_stamina

    def __init__(self, speed=0, facing=0, **kwargs):
        kwargs['sprite_path'] = kwargs.get('sprite_path', 'wizard.png')
        with resources.path(img, kwargs['sprite_path']) as sprite_path:
            self.sprite = pygame.image.load(str(sprite_path))
        self.app = kwargs.get('app')
        kwargs.pop('app')
        super().__init__(**kwargs)
        self.name = kwargs.get('name', names.get_full_name(gender=self.sex))
        self.using_stamina = False
        self.app.session.add(self)
        self.app.session.commit()

        self.app.db_engine.execute(
            character_settings.insert().values(
                settings_guid=self.guid,
                character_guid=self.settings_guid
            ))

    def accelerate(self, direction):
        self.facing = direction
        if self.using_stamina and not self.fatigue:
            self.speed = self.walking_speed * 3
            self.stamina -= 10
        else:
            self.speed = self.walking_speed
        
        self.app.logger.debug(f"character speed: {self.speed}, character facing: {self.facing}")
        self.dx = self.speed * math.cos(self.facing)
        self.dy = self.speed * math.sin(self.facing)
        
        self.x_pos += self.dx
        self.y_pos += self.dy
    
    def homeostasis(self):
        """
        Character naturally maintains levels of certain stats
        """
        print(self.stamina_ratio)
        print(1 - math.exp(-self.stamina_ratio))
        if self.stamina_ratio < 0.1:
            self.fatigue = 50
        if self.fatigue:
            self.fatigue -= 1
        self.stamina += -1 - 1 / -self.stamina_ratio

class Substance(Base):
    __tablename__ = 'substance'

    name = Column(String, nullable=False)
    base_color = Column(Binary, nullable=False)
    description = Column(Text)

    def __init__(self, **kwargs):
        self.app = kwargs.get('app')
        kwargs.pop('app')
        super().__init__(**kwargs)
        self.app.session.add(self)
        self.app.session.commit()

class Pixel(Base):
    __tablename__ = 'pixel'

    x_coordinate = Column(Integer, primary_key=True)
    y_coordinate = Column(Integer, primary_key=True)
    height = Column(Float, nullable=False, default=.5)
    temperature = Column(Float, nullable=False, default=20)
    humidity = Column(Float, nullable=False, default=.5)
    substance_guid = Column(String(32), ForeignKey(Substance.guid), nullable=False)

    settings_guid = Column(String(32), ForeignKey('settings.guid'), primary_key=True)

    substance = relationship(
        Substance
    )

    def __init__(self, **kwargs):
        self.app = kwargs.get('app')
        kwargs.pop('app')
        super().__init__(**kwargs)
        self.app.session.add(self)
        self.app.session.commit()

class Skill(Base):
    __tablename__ = 'skill'

    name = Column('name', String, nullable=False)
    description = Column(Text)

# class PlayerSkill(Base):
#     def __init__(self, **kwargs):
#         self.level = kwargs.get('level', 0)

class Settings(Base):
    __tablename__ = 'settings'

    map_side_length = Column(Integer, nullable=False, default=int(1e1))

    zoom = Column(Integer, nullable=False, default=0)

    key_move_south = Column(Integer, nullable=False, default=pygame.K_s)
    key_move_north = Column(Integer, nullable=False, default=pygame.K_w)
    key_move_east = Column(Integer, nullable=False, default=pygame.K_d)
    key_move_west = Column(Integer, nullable=False, default=pygame.K_a)

    key_pan_south = Column(Integer, nullable=False, default=pygame.K_DOWN)
    key_pan_north = Column(Integer, nullable=False, default=pygame.K_UP)
    key_pan_east = Column(Integer, nullable=False, default=pygame.K_RIGHT)
    key_pan_west = Column(Integer, nullable=False, default=pygame.K_LEFT)

    font_name = Column(String, nullable=False, default=pygame.font.get_default_font())
    font_size = Column(Integer, nullable=False, default=20)

    characters = relationship(
        Character,
        backref=backref(
            'player_settings',
            uselist=True
        ),
        uselist=True,
        secondary=character_settings
    )

    pixels = relationship(
        Pixel,
        backref=backref(
            'settings',
            uselist = False
        ),
        uselist=True)

    @property
    def font(self):
        return pygame.font.SysFont(self.font_name, self.font_size)

    def __init__(self, **kwargs):
        self.app = kwargs.get('app')
        kwargs.pop('app')
        super().__init__(**kwargs)
        self.app.session.add(self)
        self.app.session.commit()
    
    @reconstructor
    def init_on_load(self):
        import pdb; pdb.set_trace()
        if not self.pixels:
            from concurrent.futures import ProcessPoolExecutor, as_completed
            with ProcessPoolExecutor() as executor:
                futures = list()
                for i in range(self.map_side_length):
                    for j in range(self.map_side_length):
                        futures.append(
                            executor.submit(
                                Pixel,
                                x_coordinate=i,
                                y_coordinate=j,
                                substance=Substance(
                                    name='Dirt',
                                    base_color=bytes(int(b'634b35', 16))
                                ),
                                settings_guid=self.guid))
            kwargs['app'].session.commit()
    