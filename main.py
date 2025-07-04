from random import randint

import pygame as pg

game_width = 1536
game_w_o2 = 768
game_w_o4 = 384
car_x = game_w_o4 - 8

game_height = 1280
game_h_o2 = 640
game_h_o4 = 320


def get_sprite(img: str, scale: float) -> pg.surface.Surface:
    return pg.transform.scale_by(pg.image.load(img), scale)


class State:
    def __init__(self, engine):
        self.engine = engine

    def on_draw(self, surface):
        pass

    def on_event(self, event):
        pass

    def on_key(self, keys_list):
        pass

    def on_update(self, delta, ticks):
        pass


class Button(pg.sprite.Sprite):
    def __init__(self, img: str, size: float, pos: tuple[int, int]):
        pg.sprite.Sprite.__init__(self)
        self.sprite = get_sprite(img, size).convert_alpha()
        self.pos = pos
        self.rect = self.sprite.get_rect()
        self.hue = 0
        self.lightness = 0

    def is_clicked(self):
        mx, my = pg.mouse.get_pos()
        return pg.mouse.get_pressed()[0] and self.rect.collidepoint(mx - self.pos[0] + self.rect.centerx, my - self.pos[1] + self.rect.centery)

    def on_draw(self, surface: pg.Surface):
        surface.blit(pg.transform.hsl(self.sprite, self.hue, 0, self.lightness), (self.pos[0] - self.rect.centerx, self.pos[1] - self.rect.centery))


class DisplayEngine:
    def __init__(self, caption: str, width: int, height: int, flags=0):
        pg.display.set_caption(caption)
        self.surface = pg.display.set_mode((width, height), flags)
        self.rect = self.surface.get_rect()
        self.clock = pg.time.Clock()
        self.running = False
        self.delta = 0
        self.fps = 60

        self.state = None
        self.next_state = None

    def main_loop(self, in_state=None):
        if in_state is not None:
            self.state = in_state

        self.running = True
        while self.running:
            if self.next_state is not None:
                self.state = self.next_state
                self.next_state = None

            for ev in pg.event.get():
                if ev.type == pg.QUIT:
                    self.running = False
                    break
                self.state.on_event(ev)

            self.state.on_key(pg.key.get_pressed())

            self.state.on_draw(self.surface)
            self.state.on_update(self.delta, pg.time.get_ticks())
            pg.display.flip()
            self.delta = self.clock.tick(self.fps)


class Intro(State):
    def __init__(self, engine):
        State.__init__(self, engine)
        self.bgcolor = 255
        self.m = -1

    def on_draw(self, surface: pg.Surface):
        surface.fill(pg.Color(self.bgcolor, self.bgcolor, self.bgcolor))
        surface.blit(game_header, (game_w_o2 - game_header_rect.centerx, 50))
        surface.blit(press_any, (game_w_o2 - press_any_rect.centerx, 900))

    def on_event(self, event):
        if event.type == pg.KEYDOWN:
            self.engine.next_state = Menu(self.engine)

    def on_update(self, delta, ticks):
        self.bgcolor = self.bgcolor + self.m * delta / 60

        if not (191 < self.bgcolor < 255):
            self.bgcolor = max(191, min(self.bgcolor, 255))
            self.m *= -1


class Menu(State):
    def __init__(self, engine):
        State.__init__(self, engine)
        self.single_player_button = Button('assets/buttons/1player.png', 16, (game_w_o2 - 350, game_h_o4 + 100))
        self.multi_player_button = Button('assets/buttons/2player.png', 16, (game_w_o2 + 350, game_h_o4 + 100))
        self.quit_button = Button('assets/buttons/quit.png', 8, (game_w_o2, game_h_o2 + 128))

        self.short_game_button = Button('assets/buttons/short_game.png', 8, (game_w_o4 + 100, game_height - 128))
        self.medium_game_button = Button('assets/buttons/medium_game.png', 8, (game_w_o2, game_height - 128))
        self.long_game_button = Button('assets/buttons/long_game.png', 8, (game_w_o2 + game_w_o4 - 100, game_height - 128))

        self.quitting_ticks = 0
        quitting.set_alpha(0)


    def on_draw(self, surface: pg.Surface):
        surface.fill(pg.Color(191, 191, 191))
        surface.blit(game_len, (game_w_o2 - game_len_rect.centerx, game_h_o2 + game_h_o4))
        surface.blit(quitting, (game_w_o2 - quitting_rect.centerx, 8))

        self.single_player_button.on_draw(surface)
        self.multi_player_button.on_draw(surface)
        self.quit_button.on_draw(surface)

        self.short_game_button.on_draw(surface)
        self.medium_game_button.on_draw(surface)
        self.long_game_button.on_draw(surface)

    def on_event(self, event):
        if event.type == pg.KEYDOWN:
            match event.key:
                case pg.K_1:
                    Game.len_memo = 8
                case pg.K_2:
                    Game.len_memo = 16
                case pg.K_3:
                    Game.len_memo = 32
                case pg.K_0:
                    Game.len_memo = 2

    def on_key(self, keys_list):
        self.quitting_ticks = self.quitting_ticks + 1 if keys_list[pg.K_ESCAPE] or self.quit_button.is_clicked() else 0

    def on_update(self, delta, ticks):
        if self.single_player_button.is_clicked():
            self.engine.next_state = Game(self.engine, 1)
        if self.multi_player_button.is_clicked():
            self.engine.next_state = Game(self.engine, 2)

        if self.short_game_button.is_clicked():
            Game.len_memo = 8
        if self.medium_game_button.is_clicked():
            Game.len_memo = 16
        if self.long_game_button.is_clicked():
            Game.len_memo = 32

        match Game.len_memo:
            case 8:
                self.short_game_button.lightness = -0.4
                self.medium_game_button.lightness = 0
                self.long_game_button.lightness = 0
            case 16:
                self.short_game_button.lightness = 0
                self.medium_game_button.lightness = -0.4
                self.long_game_button.lightness = 0
            case 32:
                self.short_game_button.lightness = 0
                self.medium_game_button.lightness = 0
                self.long_game_button.lightness = -0.4
            case _:
                self.short_game_button.lightness = 0
                self.medium_game_button.lightness = 0
                self.long_game_button.lightness = 0

        quitting.set_alpha(min(255, int(self.quitting_ticks / 30 * 255)))
        if self.quitting_ticks >= 60:
            self.engine.running = False


def generate_road(length: int) -> list[int]:
    return [randint(0, 10) for _ in range(length)]


class Game(State):
    len_memo = 2

    def __init__(self, engine, players: int, map: list[int] = None):
        State.__init__(self, engine)
        self.roads = players

        if map is not None:
            self.map = map
        else:
            self.map = generate_road(Game.len_memo)

        match players:
            case 1:
                self.players_list = [Road(self, self.map)]
            case 2:
                self.players_list = [Road(self, self.map, 0), Road(self, self.map, 1)]

        self.finished = False
        self.plr_finished = None
        self.esc_enter_ticks = 0
        self.space_delete_ticks = 0
        self.starting_anim_frame = None
        self.start_anim_frame_rect = None
        self.starting_ticks = 210

        self.restart_button = Button('assets/buttons/restart.png', 16, (game_w_o4, 1000))
        self.menu_button = Button('assets/buttons/menu.png', 16, (game_w_o2 + game_w_o4, 1000))

        quitting.set_alpha(0)
        restarting.set_alpha(0)

    def on_finish(self, plr_no: int):
        self.finished = True
        self.plr_finished = (plr_no, game_finished_screens[plr_no])
        self.restart_button.hue = -plr_no * 120

    def on_draw(self, surface: pg.Surface):
        surface.fill(pg.Color(64, 64, 64))
        match self.roads:
            case 1:
                player = self.players_list[0]
                player.on_draw()
                surface.blit(player.surf, (game_w_o4 + 8, 0))
            case 2:
                for index, player in enumerate(self.players_list):
                    player.on_draw()
                    surface.blit(player.surf, (index * game_w_o2 + 8, 0))

        if 0 < self.starting_ticks < 180:
            surface.blit(self.starting_anim_frame, (game_w_o2 - self.start_anim_frame_rect.centerx, game_h_o2 - self.start_anim_frame_rect.centery))

        if self.finished:
            surface.blit(self.plr_finished[1], (game_w_o2 - game_fin_scr_rect.centerx, 300))
            self.restart_button.on_draw(surface)
            self.menu_button.on_draw(surface)

        surface.blit(quitting, (game_w_o2 - quitting_rect.centerx, 8))
        surface.blit(restarting, (game_w_o2 - restarting_rect.centerx, quitting_rect.bottom + 16))

    def on_key(self, keys_list):
        if not self.starting_ticks:
            self.esc_enter_ticks = self.esc_enter_ticks + 1 if keys_list[pg.K_ESCAPE] or keys_list[pg.K_RETURN] else 0
            self.space_delete_ticks = self.space_delete_ticks + 1 if keys_list[pg.K_SPACE] and keys_list[pg.K_DELETE] else 0

        for player in self.players_list:
            player.on_key(keys_list)

    def on_update(self, delta, ticks):
        if self.esc_enter_ticks >= 100 or (self.finished and self.menu_button.is_clicked()):
            self.engine.next_state = Menu(self.engine)

        for player in self.players_list:
            player.on_update()

        if self.space_delete_ticks >= 60 or (self.finished and self.restart_button.is_clicked()):
            self.engine.next_state = Game(self.engine, self.roads)

        match self.starting_ticks:
            case 180:
                self.starting_anim_frame = ready
                self.start_anim_frame_rect = ready_rect
            case 120:
                self.starting_anim_frame = set
                self.start_anim_frame_rect = set_rect
            case 60:
                self.starting_anim_frame = go
                self.start_anim_frame_rect = go_rect

        quitting.set_alpha(min(255, int(self.esc_enter_ticks / 60 * 255)))
        restarting.set_alpha(min(255, int(self.space_delete_ticks / 30 * 255)))
        self.starting_ticks -= self.starting_ticks > 0


class Road:
    def __init__(self, game_state: Game, road_list: list[int], red_or_blue: int = 2):
        self.state = game_state
        self.plr = red_or_blue
        self.surf = pg.surface.Surface((game_w_o2 - 16, game_height))
        self.car = pg.transform.hsl(car, -102 * self.plr, 0, 0).convert_alpha()

        self.car_rect = self.car.get_rect()
        self.car_rect.topleft = (car_x - self.car_rect.centerx, game_height - car_x - self.car_rect.centerx)

        self.check_wasd = self.plr in {0, 2}
        self.check_arrows = self.plr in {1, 2}

        self.road_list = [11, *road_list, 12]
        self.step = 4
        self.visible_road = self.road_list[0:4:]

        self.min_offset_to_shift = 1024
        self.road_offset = 0
        self.roadx = game_w_o4 - 8 - road_rect.centerx

        self.car_xspeed = 0.2
        self.car_yspeed = 0.2
        self.car_dev_x = 0
        self.car_dev_y = 0

        self.finish_line_pos = None
        self.stun = 150
        self.bump_anim_len = 0
        self.bump_anim_dir = [-1, 1][randint(0, 1)]
        self.is_active = False

    def shift_floor(self):
        self.step += 1
        if self.step < len(self.road_list):
            self.visible_road = self.road_list[self.step - 4:self.step:]
            self.check_for_finish = True
        else:
            self.visible_road = self.road_list[self.step - 4::]

    def on_finish(self):
        self.state.on_finish(self.plr)

    def on_draw(self):
        self.surf.fill(pg.Color(128, 128, 128))

        if self.step > 4:
            self.surf.blit(do_not_turn_back, (self.roadx, game_height - road_rect.centery + self.road_offset))
        for i, block in enumerate(self.visible_road):
            pos = (self.roadx, game_height - road_rect.bottom * (i + 1.5) + self.road_offset)
            if block == 11:
                self.surf.blit(road_start, pos)
                self.surf.blit(road_finish_line, pos)
            elif block == 12:
                self.surf.blit(road_end, pos)
                self.surf.blit(road_finish_line, pos)
                self.finish_line_pos = pos
            else:
                self.surf.blit(road_forward, pos)

            if 1 <= block <= 10:
                self.surf.blit(road_blocks[block - 1], pos)

        car_r = pg.transform.rotate(self.car, self.bump_anim_len * 9 * self.bump_anim_dir - self.car_dev_x * 8 * self.car_dev_y / 6).convert_alpha()

        car_r_rect = car_r.get_rect()
        car_r_rect.center = self.car_rect.center
        self.surf.blit(car_r, car_r_rect.topleft)

    def on_key(self, keys_list):
        go_right = (keys_list[pg.K_d] and self.check_wasd) or (keys_list[pg.K_RIGHT] and self.check_arrows)
        go_left = (keys_list[pg.K_a] and self.check_wasd) or (keys_list[pg.K_LEFT] and self.check_arrows)
        self.car_dev_x += self.car_xspeed * (go_right - go_left) * int(not self.stun) * (not self.state.finished)

        go_up = (keys_list[pg.K_w] and self.check_wasd) or (keys_list[pg.K_UP] and self.check_arrows)
        go_down = (keys_list[pg.K_s] and self.check_wasd) or (keys_list[pg.K_DOWN] and self.check_arrows)
        self.car_dev_y += self.car_yspeed * (go_up - go_down) * int(not self.stun) * (not self.state.finished)

        self.is_x_active = go_right or go_left
        self.is_y_active = go_up or go_down


    def on_update(self):
        self.car_dev_y = max(-2, min(self.car_dev_y, 8))
        self.car_dev_x = max(-3, min(self.car_dev_x, 3))

        if road_forward_mask.overlap(car_mask, (self.car_rect.left - self.roadx, 0)) is not None and self.car_dev_x:
            self.car_dev_x *= -3
            self.car_dev_y /= 2
            self.bump_anim_len = 30
            self.bump_anim_dir = [-1, 1][randint(0, 1)]
            self.stun = 40

        for i, rb in enumerate(self.visible_road):
            if 1 <= rb <= 10:
                if road_blocks_masks[rb-1].overlap(car_mask, (self.car_rect.left - self.roadx, self.car_rect.top - (game_height - road_rect.bottom * (i + 1.5) + self.road_offset))) and (self.car_dev_x or self.car_dev_y):
                    self.car_dev_x *= -2
                    self.car_dev_y *= -2
                    self.bump_anim_len = 30
                    self.bump_anim_dir = [-1, 1][randint(0, 1)]
                    self.stun = 40

        if self.finish_line_pos is not None:
            if road_end_mask.overlap(car_mask, (self.finish_line_pos[0], self.finish_line_pos[1] - road_rect.bottom)):
                self.on_finish()

        self.road_offset += self.car_dev_y
        self.car_rect.left += self.car_dev_x

        if self.road_offset < -56:
            self.road_offset = -56
            self.car_dev_y = 1
        if self.road_offset > self.min_offset_to_shift:
            self.shift_floor()
            self.road_offset = 512

        self.car_dev_x -= self.car_dev_x / 50
        self.car_dev_y -= self.car_dev_y / (20 if self.state.finished else 90)
        self.stun -= self.stun > 0
        self.bump_anim_len -= self.bump_anim_len > 0

        if not self.is_y_active:
            if -1 < self.car_dev_y < 1:
                self.car_dev_y = 0
        if not self.is_x_active:
            if -1 < self.car_dev_x < 1:
                self.car_dev_x = 0


if __name__ == '__main__':
    pg.init()
    engine = DisplayEngine('Divine Racing', game_width, game_height)

    car = get_sprite('assets/car.png', 4)
    car_mask = pg.mask.from_surface(car)

    game_header = get_sprite('assets/texts/divine_racing_header.png', 28).convert_alpha()
    game_header_rect = game_header.get_rect()

    press_any = get_sprite('assets/texts/press_any.png', 8).convert_alpha()
    press_any_rect = press_any.get_rect()

    game_len = get_sprite('assets/texts/game_length.png', 8).convert_alpha()
    game_len_rect = game_len.get_rect()

    ready = get_sprite('assets/texts/ready.png', 8).convert_alpha()
    ready_rect = ready.get_rect()
    set = get_sprite('assets/texts/set.png', 16).convert_alpha()
    set_rect = set.get_rect()
    go = get_sprite('assets/texts/go.png', 24).convert_alpha()
    go_rect = go.get_rect()

    road_forward = get_sprite('assets/road_parts/road_forward.png', 16).convert_alpha()
    road_rect = road_forward.get_rect()
    road_forward_mask = pg.mask.from_surface(road_forward)

    road_edge = get_sprite('assets/road_parts/road_edge.png', 16)
    road_start = road_edge.convert_alpha()
    road_end = pg.transform.rotate(road_edge, 180).convert_alpha()
    road_end_mask = pg.mask.from_surface(get_sprite('assets/road_parts/road_finish.png', 16))
    road_finish_line = get_sprite('assets/road_parts/road_finish_line.png', 16).convert_alpha()

    road_blocks = [get_sprite(f'assets/road_blocks/road_block_{n + 1}.png', 16).convert_alpha() for n in range(10)]
    road_blocks_masks = [pg.mask.from_surface(block) for block in road_blocks]

    game_finished_screens = [get_sprite(n, 16).convert_alpha() for n in ['assets/finishers/plr0.png', 'assets/finishers/plr1.png', 'assets/finishers/plr2.png']]
    game_fin_scr_rect = game_finished_screens[0].get_rect()

    quitting = get_sprite('assets/texts/quitting.png', 8).convert_alpha()
    quitting.set_alpha(0)
    quitting_rect = quitting.get_rect()

    restarting = get_sprite('assets/texts/restarting.png', 8).convert_alpha()
    restarting.set_alpha(0)
    restarting_rect = restarting.get_rect()

    do_not_turn_back = pg.transform.scale(pg.image.load('assets/stawp.jpg'), (512, 256)).convert_alpha()

    engine.main_loop(Intro(engine))

    pg.quit()
