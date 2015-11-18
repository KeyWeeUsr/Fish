__author__ = "KeyWeeUsr"
__version__ = "1.0"

import os
from kivy.app import App
from kivy.clock import Clock
from functools import partial
from kivy.utils import platform
from kivy.uix.image import Image
from kivy.uix.button import Button
from random import randint, choice
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.graphics import *

class PlayerFish(Image):
    eaten = 0
    fishd = {}
    active = 1
    body_size = 5
    direction = 'left'
    default_size = [10, 5]
    rotation = 0

    def __init__(self, **kwargs):
        super(PlayerFish, self).__init__(**kwargs)
        Clock.schedule_interval(self.collision, 1/60.0)

    def collision(self, dt):
        if self.active:
            for i in self.fishd.values():
                if self.collide_widget(i):
                    if self.body_size >= i.multiply:
                        i.collision = 1
                        i.destroy()
                        self.eaten += 1
                        self.parent.parent.parent.ids.score.text = str(int(self.parent.parent.parent.ids.score.text) + i.multiply * 36)
                        self.parent.parent.parent.ids.flit.add_widget(Image(source='fish_s.png', size_hint_x=None, width=0.2*self.parent.parent.parent.ids.flit.size[0]))
                        if self.eaten % 5 == 0:
                            self.body_size += 1
                            self.size = map(lambda x: x * self.body_size, self.default_size)
                            self.pos[0] = self.pos[0] - self.size[0]/8.0
                            self.pos[1] = self.pos[1] - self.size[1]/8.0
                            if len(self.parent.parent.parent.ids.flit.children) > 4:
                                self.parent.parent.parent.ids.flit.clear_widgets()
                                self.parent.parent.parent.ids.fmed.add_widget(Image(source='fish_m.png', size_hint_x=None, width=0.2*self.parent.parent.parent.ids.fmed.size[0]))
                        elif self.eaten % 25 == 0:
                            if len(self.parent.parent.parent.ids.fmed.children) > 4:
                                self.parent.parent.parent.ids.fmed.clear_widgets()
                                self.parent.parent.parent.ids.fbig.add_widget(Image(source='fish_l.png', size_hint_x=None, width=0.2*self.parent.parent.parent.ids.fbig.size[0]))
                        if self.body_size == 25:
                            self.parent.parent.parent.parent.ids.highscore.text = self.parent.parent.parent.ids.score.text
                            self.finish()
                    else:
                        Clock.schedule_interval(self.death,1/60.0)
        else:
            Clock.unschedule(self.collision)
            Clock.schedule_interval(self.collision, 1/60.0)
            self.active = 1

    def death(self, dt):
        if self.rotation < 360:
            self.rotation+=10
            with self.canvas.before:
                PushMatrix()
                Rotate(angle=10, axis=(0,0,1), origin=self.center)
            with self.canvas.after:
                PopMatrix()
        else:
            Clock.unschedule(self.death)
            self.parent.parent.parent.parent.ids.highscore.text = self.parent.parent.parent.ids.score.text
            self.parent.parent.parent.parent.pause_game(1)
    def finish(self):
        self.parent.parent.parent.parent.pause_game(2)
class Fish(Image):
    multiply = 0
    collision = 0
    delfish = None

    def __init__(self, **kwargs):
        super(Fish, self).__init__(**kwargs)
        self.size_hint = [None, None]
        self.area = kwargs['area']
        self.t = kwargs['t']
        self.multiply = kwargs['multiply']
        if self.pos[0] < self.area[2]/2.0:
            self.direction = 1
            self.source = 'enemyR.png'
        else:
            self.direction = 0
            self.source = 'enemyL.png'
        Clock.schedule_interval(self.animate, 1/30.0)

    def destroy(self):
        if self.pos[0] < -400 or self.pos[0] > self.area[2] + 400 or self.collision:
            tempdict = self.t.parent.parent.ids.player.fishd.copy()
            for key, value in tempdict.iteritems():
                if value == self:
                    self.delfish = key
                    break
            tempdict.pop(self.delfish, None)
            self.t.parent.parent.ids.player.fishd.clear()
            self.t.parent.parent.ids.player.fishd = tempdict.copy()
            del tempdict
            self.t.remove_widget(self)

    def animate(self, dt):
        self.destroy()
        if self.direction:
            self.pos[0] += 1
        else:
            self.pos[0] -= 1


class GameScreen(Screen):
    one = 0
    two = 0
    func = None
    player_speed = 0.01
    path = os.path.dirname(os.path.abspath(__file__))

    def use(self, direction, active):
        if active and self.manager.current == 'game':
            Clock.unschedule(self.func)
            self.func = partial(self.move, direction)
            Clock.schedule_interval(self.func, self.player_speed)
        else:
            Clock.unschedule(self.func)

    def move(self, direction, dt):
        if (self.ids.player.pos[0] > 0 and
            self.ids.player.pos[0] < Window.width - self.ids.player.size[0] and
            self.ids.player.pos[1] > self.parent.botheight and
            self.ids.player.pos[1] < Window.height - self.ids.player.size[1]):
            if direction == 'up':
                self.ids.player.pos[1] += self.ids.player.body_size - 2
            elif direction == 'down':
                self.ids.player.pos[1] -= self.ids.player.body_size - 2
            elif direction == 'left':
                self.ids.player.source = 'playerL.png'
                self.ids.player.pos[0] -= self.ids.player.body_size - 2
            elif direction == 'right':
                self.ids.player.source = 'playerR.png'
                self.ids.player.pos[0] += self.ids.player.body_size - 2
        elif self.ids.player.pos[0] <= 0:
            self.ids.player.pos[0] += self.ids.player.body_size - 2
        elif self.ids.player.pos[0] >= Window.width - self.ids.player.size[0]:
            self.ids.player.pos[0] -= self.ids.player.body_size - 2
        elif self.ids.player.pos[1] <= self.parent.botheight:
            self.ids.player.pos[1] += self.ids.player.body_size - 2
        elif self.ids.player.pos[1] >= Window.height - self.ids.player.size[1]:
            self.ids.player.pos[1] -= self.ids.player.body_size - 2


class Body(ScreenManager):
    area = []
    paused = 0
    running = 0
    fishcount = 0
    botheight = 0
    spawn_time = 2
    fish_size = [10, 5]
    path = os.path.dirname(os.path.abspath(__file__))

    def __init__(self, **kwargs):
        super(Body, self).__init__(**kwargs)
        Clock.schedule_interval(self.is_running, 1/60.0)
        if platform != 'android':
            self.keyboard = Window.request_keyboard(self.keyboard_close, self)
            self.keyboard.bind(on_key_down=self.on_keyboard_down)
            self.keyboard.bind(on_key_up=self.on_key_up)
            self.ids.game.ids.controls.size_hint_y=None
            self.ids.game.ids.controls.size[1] = 0

    def keyboard_close(self):
        self.keyboard.unbind(on_key_down=on_keyboard_down)
        self.keyboard = None

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'up':
            self.ids.game.use('up', 1)
        elif keycode[1] == 'down':
            self.ids.game.use('down', 1)
        elif keycode[1] == 'left':
            self.ids.game.use('left', 1)
        elif keycode[1] == 'right':
            self.ids.game.use('right', 1)
        elif keycode[1] == 'w':
            self.ids.game.use('up', 1)
        elif keycode[1] == 'a':
            self.ids.game.use('left', 1)
        elif keycode[1] == 's':
            self.ids.game.use('down', 1)
        elif keycode[1] == 'd':
            self.ids.game.use('right', 1)
        elif keycode[1] == 'escape':
            exit()
        elif keycode[1] == 'pause':
            self.pause_game()
        return True

    def on_key_up(self, keyboard, keycode):
        if keycode[1] == 'up':
            self.ids.game.use('up', 0)
        elif keycode[1] == 'down':
            self.ids.game.use('down', 0)
        elif keycode[1] == 'left':
            self.ids.game.use('left', 0)
        elif keycode[1] == 'right':
            self.ids.game.use('right', 0)
        elif keycode[1] == 'w':
            self.ids.game.use('up', 0)
        elif keycode[1] == 'a':
            self.ids.game.use('left', 0)
        elif keycode[1] == 's':
            self.ids.game.use('down', 0)
        elif keycode[1] == 'd':
            self.ids.game.use('right', 0)

    def is_running(self, dt):
        if(self.running):
            self.area.append(int(self.ids.game.ids.water.pos[0]))
            self.area.append(int(self.ids.game.ids.water.pos[1]))
            self.area.append(round(self.ids.game.ids.water.size[0]))
            self.area.append(round(self.ids.game.ids.water.size[1]))
            self.botheight = self.ids.game.ids.controls.size[1]
            self.ids.game.ids.player.pos = [self.area[2]/2.0 - 25, self.area[3]/2.0 - 12.5 + self.botheight]
            Clock.schedule_interval(self.spawn, self.spawn_time)
            Clock.unschedule(self.is_running)

    def spawn(self, dt):
        if len(self.ids.game.ids.player.fishd) <= 13:
            multiply = randint(1, 20)
            if len(self.ids.game.ids.player.fishd) == 0 and self.fishcount == 0:
                i = 0
                self.fishcount = 1
            elif len(self.ids.game.ids.player.fishd) != 0:
                i = self.fishcount
                self.fishcount += 1
            else:
                i = self.fishcount
            self.ids.game.ids.player.fishd['fish%s' % str(i)] = Fish(t=self.ids.game.ids.water, area=self.area, multiply=multiply, size=map(lambda x: x * multiply, self.fish_size),
                                                                    pos=[choice([self.area[0] - self.fish_size[0] * multiply, self.area[2] + self.fish_size[0] * multiply]),
                                                                        randint(self.area[1], self.area[3] - self.fish_size[1] + int(self.botheight))])
            self.ids.game.ids.water.add_widget(self.ids.game.ids.player.fishd['fish%s' % str(i)])
            self.ids.game.ids.player.active = 0

    def pause_game(self, over=0):
        if not self.paused:
            Clock.unschedule(self.spawn)
            for child in self.ids.game.ids.water.children:
                if 'PlayerFish' not in str(child) and 'BoxVert' not in str(child) and 'Label' not in str(child):
                    Clock.unschedule(child.animate)
                elif 'PlayerFish' in str(child):
                    Clock.unschedule(child.collision)
            self.show_buttons(True)
            self.paused = 1
            if over:
                tempchildren = []
                for child in self.ids.game.ids.water.children:
                    if 'PlayerFish' not in str(child) and 'BoxVert' not in str(child) and 'Label' not in str(child):
                        tempchildren.append(child)
                self.ids.game.ids.water.clear_widgets(tempchildren)
                del tempchildren
                self.ids.game.ids.player.fishd.clear()
                self.ids.game.ids.player.active = 1
                self.ids.game.ids.player.eaten = 0
                self.ids.game.ids.fbig.clear_widgets()
                self.ids.game.ids.fmed.clear_widgets()
                self.ids.game.ids.flit.clear_widgets()
                self.ids.game.ids.player.body_size = 5
                self.ids.game.ids.player.size = map(lambda x: x * self.ids.game.ids.player.body_size, self.ids.game.ids.player.default_size)
                self.running = 0
                self.area = []
                self.paused = 0
                self.ids.game.ids.score.text = '0'
                if over!=2:
                    self.current = 'highscore'
                else:
                    self.current = 'endgame'
        else:
            Clock.schedule_interval(self.spawn, self.spawn_time)
            for child in self.ids.game.ids.water.children:
                if 'PlayerFish' not in str(child) and 'BoxVert' not in str(child) and 'Label' not in str(child):
                    Clock.schedule_interval(child.animate, 1/30.0)
                elif 'PlayerFish' in str(child):
                    Clock.schedule_interval(child.collision, 1/60.0)
            self.show_buttons()
            self.paused = 0

    def restart(self):
        self.ids.highscore.text = ''
        self.running = 1
        Clock.schedule_interval(self.is_running, 1/60.0)
        Clock.schedule_interval(self.ids.game.ids.player.collision, 1/60.0)
        self.show_buttons()
        self.current = 'game'

    def show_buttons(self, disabled=False):
        self.ids.game.ids.arru.disabled = disabled
        self.ids.game.ids.arrd.disabled = disabled
        self.ids.game.ids.arrl.disabled = disabled
        self.ids.game.ids.arrr.disabled = disabled


class FishGame(App):
    def build(self):
        return Body()

    def on_pause(self): return True

    def on_resume(self): pass
if __name__ == '__main__':
    FishGame().run()
