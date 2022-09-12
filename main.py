from kivy.app import App
from kivy.clock import Clock
from kivy.uix.effectwidget import EffectWidget, VerticalBlurEffect, HorizontalBlurEffect
from kivy.uix.screenmanager import ScreenManager, NoTransition, Screen
from kivy.config import Config
from tkinter.filedialog import asksaveasfile
import tkinter
import datetime as dt

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
time = 60


class DisappearingTextWidget(EffectWidget):
    def __init__(self, **kwargs):
        super(DisappearingTextWidget, self).__init__(**kwargs)
        self.v = 0
        self.h = 0

    def run_effect(self):
        Clock.schedule_interval(self.disappear_effect, 0.2)
        self.v = 0
        self.h = 0

    def stop_effect(self):
        Clock.unschedule(self.disappear_effect)

    def disappear_effect(self):
        self.effects(VerticalBlurEffect(size=self.v), HorizontalBlurEffect(size=self.h))
        self.v += 0.2
        self.h += 0.2


class StartScreen(Screen):
    def update_total_time(self):
        global time
        time = int(self.ids.time_spinner.text) * 60


class WritingScreen(Screen):
    start = False
    typing = False
    timer = False
    words = ''
    last_type_time = dt.datetime.now()
    start_time = dt.datetime.now()

    def start_typing(self):
        if not self.start:
            self.start = True
            self.last_type_time = dt.datetime.now()
            self.typing = Clock.schedule_interval(self.update, 1/60)
            self.timer = Clock.schedule_once(self.completed, time)
            self.start_time = dt.datetime.now()
            print(f'Start typing! You have {time / 60} minutes to go.')

    def restart(self):
        self.start = False
        self.typing = False
        self.ids.text_area.disabled = False
        self.ids.restart_btn.disabled = True
        self.ids.save_btn.disabled = True
        self.ids.text_area.text = ''
        self.ids.effect_widget.effects = (VerticalBlurEffect(size=0), HorizontalBlurEffect(size=0))
        self.ids.timer_rect.canvas.get_group('a')[0].size = (0, self.height * 0.01)

    def reset_time(self):
        if len(self.words) < len(self.ids.text_area.text):
            self.last_type_time = dt.datetime.now()
        self.words = self.ids.text_area.text

    def save_file(self):
        text = self.ids.text_area.text
        files = [('Text Document', '*.txt'),
                 ('All Files', '*.*'),
                 ('Python Files', '*.py')]
        root = tkinter.Tk()
        root.withdraw()
        file = asksaveasfile(filetypes=files, defaultextension=files)
        if file is not None:
            file.write(text)
            file.close()

    def completed(self, t):
        self.ids.restart_btn.disabled = False
        self.ids.save_btn.disabled = False
        self.typing.cancel()
        self.ids.text_area.disabled = True
        self.ids.effect_widget.effects = (VerticalBlurEffect(size=0), HorizontalBlurEffect(size=0))

    # APP LOGIC
    def update(self, t):
        td = dt.datetime.now() - self.last_type_time
        time_since_type = td.total_seconds()
        time_done = (dt.datetime.now() - self.start_time).total_seconds()
        time_percent = time_done / time
        self.ids.timer_rect.canvas.get_group('a')[0].size = (self.width * time_percent, self.height * 0.01)
        if time_since_type <= 2:
            self.ids.effect_widget.effects = (VerticalBlurEffect(size=0), HorizontalBlurEffect(size=0))
        elif time_since_type > 5:
            self.typing.cancel()
            self.ids.text_area.disabled = True
            self.ids.restart_btn.disabled = False
            self.timer.cancel()
            self.ids.effect_widget.effects = (VerticalBlurEffect(size=5), HorizontalBlurEffect(size=5))
        elif time_since_type > 2:
            self.ids.effect_widget.effects = (VerticalBlurEffect(size=2-time_since_type),
                                              HorizontalBlurEffect(size=2-time_since_type))


class DisappearingTextApp(App):
    def build(self):
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(StartScreen(name='start_screen'))
        sm.add_widget(WritingScreen(name='writing_screen'))
        return sm


if __name__ == "__main__":
    DisappearingTextApp().run()
