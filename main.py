# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import random as rd


class FestScreen(BoxLayout):
    output = StringProperty("Натисни кнопку, щоб почати святкування")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rests = [
            "ChiliPizza", "ProntoPizza", "McDonald's", "RoyalHamburger",
            "Пельмені&Вареники", "KFC", "Домашня редакція", "New York Street Pizza"
        ]
        self.reset_fest()

    def reset_fest(self):
        self.total = 0
        self.current_step = 0
        self.used_rests = []
        self.dishes_to_enter = []
        self.current_dish_index = 0
        self.rest_mode = rd.choice(["2 на вибір", "1 без вибору", "вільний вибір"])
        self.dish_mode = rd.choice(["вибірково", "всі"])
        self.n_rests = rd.choice([4, 5])
        self.next_restaurant = None
        self.output = (f"Режим закладів: [b]{self.rest_mode}[/b]\n"
                       f"Режим страв: [b]{self.dish_mode}[/b]\n"
                       f"Кількість закладів за день: [b]{self.n_rests}[/b]\n\n"
                       "Натисни 'Наступний заклад' щоб почати.")

    def next_step(self):
        # Якщо зараз ввід цін - не можна переходити далі
        if self.dishes_to_enter and self.current_dish_index < len(self.dishes_to_enter):
            self.output = "Введіть ціну для поточної страви перед переходом далі."
            return

        if self.current_step >= self.n_rests:
            self.output = f"[b]Загальна вартість:[/b] {self.total:.2f} грн\n🎊 Святкування завершено!"
            return

        self.current_step += 1

        available = [r for r in self.rests if r not in self.used_rests]
        if not available:
            self.used_rests = []
            available = self.rests[:]

        if self.rest_mode == "1 без вибору":
            rest = rd.choice(available)
        elif self.rest_mode == "2 на вибір":
            if len(available) >= 2:
                options = rd.sample(available, 2)
            else:
                options = available
            # Виведемо вибір користувачу через popup
            self.show_rest_choice_popup(options)
            return
        else:  # вільний вибір
            self.show_rest_choice_popup(available)
            return

        self.process_restaurant(rest)

    def process_restaurant(self, rest):
        self.next_restaurant = rest
        self.used_rests.append(rest)
        self.show_input_popup(self.get_dish_count, rest)

    def show_rest_choice_popup(self, options):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        label = Label(text="Оберіть заклад:")
        content.add_widget(label)

        for opt in options:
            btn = Button(text=opt, size_hint_y=None, height=40)
            btn.bind(on_release=lambda btn: self.on_rest_choice(btn.text, popup))
            content.add_widget(btn)

        popup = Popup(title="Вибір закладу", content=content,
                      size_hint=(0.7, 0.7), auto_dismiss=False)
        self.rest_choice_popup = popup
        popup.open()

    def on_rest_choice(self, choice, popup):
        popup.dismiss()
        self.process_restaurant(choice)

    def show_input_popup(self, callback, rest_name):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        ti = TextInput(text='', multiline=False, input_filter='int', hint_text='Введіть число')
        btn_ok = Button(text='OK', size_hint_y=None, height=40)

        content.add_widget(Label(text=f"Введіть кількість страв для закладу '{rest_name}':"))
        content.add_widget(ti)
        content.add_widget(btn_ok)

        popup = Popup(title='Кількість страв',
                      content=content,
                      size_hint=(0.7, 0.4),
                      auto_dismiss=False)

        def on_ok(instance):
            try:
                val = int(ti.text)
                if val < 0:
                    raise ValueError()
                popup.dismiss()
                callback(val)
            except:
                ti.text = ''
                self.output = "Будь ласка, введіть правильне число (0 або більше)."

        btn_ok.bind(on_press=on_ok)
        popup.open()

    def get_dish_count(self, n):
        rest_name = self.next_restaurant
        if n == 0:
            self.output = f"У закладі '{rest_name}' нічого не вибрано.\nНатисніть 'Наступний заклад', щоб продовжити."
            return

        if self.dish_mode == "всі":
            dishes = list(range(1, n + 1))
        else:
            n_dish = rd.randint(0, n)
            # Можуть бути повтори, вибір випадкових страв із заміною
            dishes = [rd.randint(1, n) for _ in range(n_dish)]

        self.dishes_to_enter = dishes
        self.current_dish_index = 0

        self.output = (f"Заклад '{rest_name}'\n"
                       f"Обрані страви: {dishes}\n"
                       f"Введіть ціну для страви №{self.dishes_to_enter[self.current_dish_index]}")

        self.show_price_popup(rest_name)

    def show_price_popup(self, rest_name):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        ti = TextInput(text='', multiline=False, input_filter='float', hint_text='Введіть ціну')
        btn_ok = Button(text='OK', size_hint_y=None, height=40)

        current_dish = self.dishes_to_enter[self.current_dish_index]

        content.add_widget(Label(text=f"Ціна для страви №{current_dish} в закладі '{rest_name}':"))
        content.add_widget(ti)
        content.add_widget(btn_ok)

        popup = Popup(title='Введіть ціну',
                      content=content,
                      size_hint=(0.7, 0.4),
                      auto_dismiss=False)

        def on_ok(instance):
            try:
                c = float(ti.text)
                if c < 0:
                    raise ValueError()
                popup.dismiss()
                self.total += c
                self.current_dish_index += 1
                if self.current_dish_index < len(self.dishes_to_enter):
                    self.output = (f"Введіть ціну для страви №{self.dishes_to_enter[self.current_dish_index]} "
                                   f"в закладі '{rest_name}'")
                    self.show_price_popup(rest_name)
                else:
                    self.output = f"Поточна вартість: {self.total:.2f} грн\nНатисніть 'Наступний заклад', щоб продовжити."
                    self.dishes_to_enter = []
                    self.current_dish_index = 0
            except:
                ti.text = ''
                self.output = "Будь ласка, введіть правильну ціну (не від’ємну)."

        btn_ok.bind(on_press=on_ok)
        popup.open()

    def restart(self):
        self.reset_fest()


class FestApp(App):
    def build(self):
        self.title = "Святковий сценарій"
        return FestScreen()


if __name__ == "__main__":
    FestApp().run()
