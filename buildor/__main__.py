import math, pygame
from . import models
from .util import oppose

def choose_settings():
    settings = APP.models.session.query(models.Settings).filter_by(guid=input('settings guid: ')).first()
    try:
        settings.app = APP
    except:
        settings = models.Settings(app=APP)
    return settings

def choose_character():
    return models.Character(app=APP, settings_guid=APP.settings.guid)

def play():
    APP.mouse.x, APP.mouse.y = pygame.mouse.get_pos()
    print(APP.mouse.__dict__)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            APP.stop()
        if event.type == pygame.KEYDOWN:
            APP.keyboard[event.key]['pressed'] = True
            if APP.keyboard[event.key]['opposes']:
                APP.keyboard[APP.keyboard[event.key]['opposes']]['negated'] = True
        if event.type == pygame.KEYUP:
            APP.keyboard[event.key]['pressed'] = False
            if APP.keyboard[event.key]['opposes']:
                APP.keyboard[APP.keyboard[event.key]['opposes']]['negated'] = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            APP.mouse.clicked = True
        if event.type == pygame.MOUSEBUTTONUP:
            APP.mouse.clicked = False
    
    if APP.menu_open and APP.keyboard[pygame.K_ESCAPE]['pressed']:
        for button in APP.main_menu.buttons:
            print(f'looping over {button.text}')
            if button.rectangle.collidepoint((APP.mouse.x, APP.mouse.y)):
                print('mouse over button')
                if APP.mouse.clicked and not button.pressed:
                    print('button pressed but not released')
                    button.pressed = True
                elif button.clicked:
                    print('button fully clicked')
                    button.pressed = False
                    exec(button.callback)
            else: button.pressed = False
    elif any(key['pressed'] for key in APP.keyboard.values()):
        if APP.keyboard[pygame.K_ESCAPE]['pressed']:
            APP.menu_open = True
        else:
            APP.player_character.using_stamina = APP.keyboard[pygame.K_LSHIFT]['pressed']
            y_direction = (
                all((APP.keyboard[APP.settings.key_move_south]['pressed'],
                    not APP.keyboard[APP.settings.key_move_south]['negated'],
                )) - all((
                    APP.keyboard[APP.settings.key_move_north]['pressed'],
                    not APP.keyboard[APP.settings.key_move_north]['negated'])))
            x_direction = (
                all((APP.keyboard[APP.settings.key_move_east]['pressed'],
                    not APP.keyboard[APP.settings.key_move_east]['negated'])
                ) - all((APP.keyboard[APP.settings.key_move_west]['pressed'],
                    not APP.keyboard[APP.settings.key_move_west]['negated'])))
            if x_direction or y_direction:
                direction = math.atan2(y_direction, x_direction)
                APP.player_character.accelerate(direction)

def main():
    APP = App(configuration=Development)
    APP.init_window(models)
    APP.load_settings(choose_settings())
    APP.set_player_character(choose_character())

    while (APP.running):
        # Mechanics
        for character in APP.settings.characters:
            character.homeostasis()
            
        play()

        # Graphics
        # APP.fill_screen(APP.configuration.BACKGROUND_RGB)
        APP.set_background(APP.configuration.BACKGROUND_IMAGE_PATH)
        APP.draw_character(APP.player_character)
        if APP.menu_open:
            APP.draw_menu(APP.main_menu)
        pygame.display.update()
        APP.main_clock.tick(60)

if __name__ == '__main__':
    main()