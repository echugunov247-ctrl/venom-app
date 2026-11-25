# -*- coding: utf-8 -*-
import threading
import time
import random
import requests
import re
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.graphics import Color, Line
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard

Window.clearcolor = (0, 0, 0, 1)

TEXTS = {
    'ru': {
        'title': 'VENOM', 'btn_settings': 'НАСТРОЙКИ', 'btn_autoreg': 'ГЕНЕРАТОР ПОЧТ',
        'btn_start': 'НАЧАТЬ', 'status': 'Система готова к работе', 'lang_title': 'ВЫБОР ЯЗЫКА',
        'btn_ru': 'РУССКИЙ', 'btn_en': 'АНГЛИЙСКИЙ', 'close': 'ЗАКРЫТЬ',
        'ar_title': 'АВТОРЕГ: ОЖИДАНИЕ КОДА', 'copy_mail': 'КОПИРОВАТЬ ПОЧТУ',
        'new_mail': 'СОЗДАТЬ НОВУЮ', 'check_now': 'ПРОВЕРИТЬ СЕЙЧАС'
    },
    'en': {
        'title': 'VENOM', 'btn_settings': 'SETTINGS', 'btn_autoreg': 'MAIL GENERATOR',
        'btn_start': 'START', 'status': 'System is ready', 'lang_title': 'SELECT LANGUAGE',
        'btn_ru': 'RUSSIAN', 'btn_en': 'ENGLISH', 'close': 'CLOSE',
        'ar_title': 'AUTOREG: WAITING CODE', 'copy_mail': 'COPY EMAIL',
        'new_mail': 'CREATE NEW', 'check_now': 'CHECK NOW'
    }
}

class VenomButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.font_size = dp(14)
        self.bold = True
        with self.canvas.before:
            Color(0, 0, 0, 1)
            self.rect = Line(width=2, rectangle=(self.x, self.y, self.width, self.height))
        self.bind(pos=self.update_rect, size=self.update_rect, state=self.on_state)

    def update_rect(self, *args):
        self.rect.rectangle = (self.x, self.y, self.width, self.height)

    def on_state(self, instance, value):
        self.color = (0.5, 0.5, 0.5, 1) if value == 'down' else (1, 1, 1, 1)

class SettingsModal(ModalView):
    def __init__(self, app_instance, **kwargs):
        super().__init__(size_hint=(0.85, 0.5), background_color=(0, 0, 0, 0.9), **kwargs)
        self.app = app_instance
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        self.title_lbl = Label(font_size=dp(24), bold=True, color=(1, 1, 1, 1))
        layout.add_widget(self.title_lbl)
        self.btn_ru = VenomButton(on_release=lambda x: self.change_lang('ru'))
        self.btn_en = VenomButton(on_release=lambda x: self.change_lang('en'))
        self.btn_close = VenomButton(on_release=lambda x: self.dismiss())
        layout.add_widget(self.btn_ru); layout.add_widget(self.btn_en); layout.add_widget(self.btn_close)
        self.add_widget(layout)
        self.update_texts()

    def change_lang(self, lang):
        self.app.current_lang = lang
        self.app.update_ui()
        self.update_texts()
        self.dismiss()

    def update_texts(self):
        t = TEXTS[self.app.current_lang]
        self.title_lbl.text = t['lang_title']
        self.btn_ru.text = t['btn_ru']
        self.btn_en.text = t['btn_en']
        self.btn_close.text = t['close']

class MailCatcherModal(ModalView):
    def __init__(self, app_instance, **kwargs):
        super().__init__(size_hint=(0.95, 0.9), background_color=(0, 0, 0, 0.9), auto_dismiss=False, **kwargs)
        self.app = app_instance
        self.current_email = None
        self.sid_token = None
        self.is_listening = False
        # Браузерный юзерагент для обхода блокировок
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))
        
        self.title_lbl = Label(font_size=dp(16), bold=True, color=(1, 1, 1, 1), size_hint_y=None, height=dp(25))
        layout.add_widget(self.title_lbl)
        
        self.email_inp = TextInput(
            text="Генерация...", readonly=True, multiline=False, font_size=dp(16),
            background_color=(0.05, 0.05, 0.05, 1), foreground_color=(1, 1, 1, 1),
            size_hint_y=None, height=dp(45), halign='center'
        )
        layout.add_widget(self.email_inp)
        
        self.btn_copy_mail = VenomButton(size_hint_y=None, height=dp(40))
        self.btn_copy_mail.bind(on_release=self.copy_email_only)
        layout.add_widget(self.btn_copy_mail)
        
        self.console_inp = TextInput(
            text="Ожидание...\n", readonly=True, multiline=True, font_size=dp(13),
            background_color=(0.02, 0.02, 0.02, 1), foreground_color=(0.5, 1, 0.5, 1),
            size_hint_y=1
        )
        layout.add_widget(self.console_inp)
        
        self.btn_check = VenomButton(size_hint_y=None, height=dp(45))
        self.btn_check.bind(on_release=lambda x: self.manual_check())
        layout.add_widget(self.btn_check)
        
        self.btn_new = VenomButton(size_hint_y=None, height=dp(45))
        self.btn_new.bind(on_release=lambda x: self.generate_new_mail())
        layout.add_widget(self.btn_new)
        
        self.btn_close = VenomButton(size_hint_y=None, height=dp(40))
        self.btn_close.bind(on_release=lambda x: self.dismiss())
        layout.add_widget(self.btn_close)
        
        self.add_widget(layout)
        self.update_texts()
        self.generate_new_mail()

    def update_texts(self):
        t = TEXTS[self.app.current_lang]
        self.title_lbl.text = t['ar_title']
        self.btn_copy_mail.text = t['copy_mail']
        self.btn_check.text = t['check_now']
        self.btn_new.text = t['new_mail']
        self.btn_close.text = t['close']

    def log(self, text):
        Clock.schedule_once(lambda dt: setattr(self.console_inp, 'text', self.console_inp.text + text + "\n"), 0)
        Clock.schedule_once(lambda dt: setattr(self.console_inp, 'cursor', (0, len(self.console_inp.text))), 0.05)

    def copy_email_only(self, instance):
        if self.current_email:
            Clipboard.copy(self.current_email)
            self.log("[>] Почта скопирована!")

    def generate_new_mail(self):
        self.is_listening = False
        self.email_inp.text = "Генерация..."
        self.console_inp.text = "Запрос к Guerrilla Mail...\n"
        self.current_email = None
        self.sid_token = None
        
        def task():
            try:
                # Guerrilla Mail API (без капчи, через GET)
                url = "https://api.guerrillamail.com/ajax.php?f=get_email_address&lang=en"
                r = requests.get(url, headers=self.headers, timeout=15)
                
                self.log(f"[*] Ответ сервера: {r.status_code}")
                
                if r.status_code == 200:
                    data = r.json()
                    self.current_email = data.get('email_addr')
                    self.sid_token = data.get('sid_token')
                    
                    if self.current_email:
                        Clock.schedule_once(lambda dt: setattr(self.email_inp, 'text', self.current_email), 0)
                        self.log(f"[+] Ящик создан: {self.current_email}")
                        self.log(">>> Введи почту на сайте.")
                        self.log(">>> Ждем код (макс. 120 сек)...")
                        self.start_listening()
                        return
                
                self.log(f"[-] Ошибка сервера. Код: {r.status_code}")
                if r.status_code == 403:
                    self.log("[!] Сервер заблокировал IP. Используй VPN.")
                    
            except Exception as e:
                self.log(f"[-] Ошибка: {str(e)[:50]}")
                
        threading.Thread(target=task, daemon=True).start()

    def start_listening(self):
        self.is_listening = True
        def listen():
            start_time = time.time()
            while self.is_listening and time.time() - start_time < 120:
                self.check_messages()
                time.sleep(3)
                
            if self.is_listening:
                self.log("\n[!] ПИСЬМО НЕ ПРИШЛО ЗА 2 МИНУТЫ.")
                self.log("[!] Сайт регистрации заблокировал домен.")
                self.is_listening = False
            
        threading.Thread(target=listen, daemon=True).start()

    def manual_check(self):
        if self.current_email and self.is_listening:
            self.log("[*] Ручная проверка...")
            threading.Thread(target=self.check_messages, daemon=True).start()

    def check_messages(self):
        if not self.sid_token: return
        try:
            url = f"https://api.guerrillamail.com/ajax.php?f=check_email&seq=0&sid_token={self.sid_token}"
            r = requests.get(url, headers=self.headers, timeout=10)
            
            if r.status_code == 200:
                data = r.json()
                messages = data.get('list', [])
                
                if messages:
                    # Берем ID первого письма
                    mail_id = messages[0].get('mail_id')
                    
                    # Читаем его
                    read_url = f"https://api.guerrillamail.com/ajax.php?f=fetch_email&email_id={mail_id}&sid_token={self.sid_token}"
                    read_r = requests.get(read_url, headers=self.headers, timeout=10)
                    
                    if read_r.status_code == 200:
                        mail_data = read_r.json()
                        text = mail_data.get('mail_body', '')
                        subject = mail_data.get('mail_subject', '')
                        
                        self.log("[*] Письмо найдено! Ищу код...")
                        
                        match = re.search(r'\b\d{4,6}\b', text + subject)
                        if match:
                            code = match.group(0)
                            self.is_listening = False
                            self.log(f"\n[!!!] КОД НАЙДЕН: {code}")
                            Clipboard.copy(code)
                            self.log("[>] Код СКОПИРОВАН в буфер.")
        except Exception:
            pass

class VenomApp(App):
    def build(self):
        self.title = 'VENOM'
        self.current_lang = 'ru'
        root = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(15))
        root.add_widget(Label(size_hint_y=0.05))

        if os.path.exists('venom.png'):
            logo = Image(source='venom.png', size_hint_y=0.3)
        else:
            logo = Label(text='VENOM', font_size=dp(40), bold=True, color=(0.3, 0.3, 0.3, 1), size_hint_y=0.3)

        root.add_widget(logo)
        self.title_lbl = Label(font_size=dp(45), bold=True, color=(1, 1, 1, 1), size_hint_y=None, height=dp(50))
        root.add_widget(self.title_lbl)
        root.add_widget(Label(size_hint_y=0.1))

        self.btn_set = VenomButton(size_hint_y=None, height=dp(60))
        self.btn_set.bind(on_release=self.open_settings)
        root.add_widget(self.btn_set)

        self.btn_autoreg = VenomButton(size_hint_y=None, height=dp(60))
        self.btn_autoreg.bind(on_release=self.open_autoreg)
        root.add_widget(self.btn_autoreg)

        self.btn_start = VenomButton(size_hint_y=None, height=dp(60))
        self.btn_start.bind(on_release=self.start_app)
        root.add_widget(self.btn_start)

        root.add_widget(Label(size_hint_y=0.15))
        self.status = Label(font_size=dp(14), color=(0.7, 0.7, 0.7, 1), size_hint_y=None, height=dp(30))
        root.add_widget(self.status)
        self.update_ui()
        return root

    def update_ui(self):
        t = TEXTS[self.current_lang]
        self.title_lbl.text = t['title']
        self.btn_set.text = t['btn_settings']
        self.btn_autoreg.text = t['btn_autoreg']
        self.btn_start.text = t['btn_start']
        self.status.text = t['status']

    def open_settings(self, instance):
        SettingsModal(self).open()

    def open_autoreg(self, instance):
        MailCatcherModal(self).open()

    def start_app(self, instance):
        self.status.text = "Запуск..." if self.current_lang == 'ru' else "Starting..."
        self.btn_start.disabled = True
        Clock.schedule_once(self.reset_start, 2.0)

    def reset_start(self, dt):
        self.btn_start.disabled = False
        self.status.text = TEXTS[self.current_lang]['status']

if __name__ == '__main__':
    VenomApp().run()main.pymain.py
