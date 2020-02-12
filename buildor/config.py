import logging, secrets
from .static import img, db
from abc import ABC, ABCMeta
from importlib import resources

class MetaConfiguration(ABCMeta):
    def __new__(cls, name, bases, clsdict):
        clsdict['LOG_LEVEL'] = logging.DEBUG
        clsdict['LOG_FORMAT'] = "%(levelname) %(asctime)s - %(message)s"
        clsdict['ECHO'] = True
        clsdict['DEBUG'] = True
        clsdict['TESTING'] = False
        clsdict['SECRET_KEY'] = secrets.token_hex(16)
        clsdict['CAPTION'] = 'Buildor (Dev)'
        clsdict['SCREEN_SIZE'] = (800, 600)
        clsdict['BACKGROUND_RGB'] = (0, 100, 0)

        if name != 'Configuration':
            with resources.path(db, f'{name}.db') as db_path:
                clsdict['DB_PATH'] = str(db_path)

        with resources.path(img, 'enterprise.png') as icon_path:
            clsdict['ICON_PATH'] = str(icon_path)
        with resources.path(img, 'map1.png') as background_image_path:
            clsdict['BACKGROUND_IMAGE_PATH'] = str(background_image_path)

        return type.__new__(cls, name, bases, clsdict)

class Configuration(ABC, metaclass=MetaConfiguration):
    pass

class Development(Configuration):
    pass
    
class Production(Configuration):
    LOG_LEVEL = logging.INFO
    DEBUG = False
    ECHO = False

class Testing(Configuration):
    LOG_LEVEL = logging.WARNING
    TESTING = True