import pyautogui
import pyaudio
import audioop
import threading
import time
import win32api
import configparser
import random
import numpy as np
import cv2
import dearpygui.dearpygui as dpg
from windowcapture import WindowCapture
import random

class FishermanBot:
    def __init__(self, bobber, bar, region=None, settings_file='settings.ini'):
        self.bobber = bobber
        self.bar = bar
        self.region = region
        self.settings_file = settings_file
        self.parser = configparser.ConfigParser()
        self.parser.read(self.settings_file)

        # Load settings
        self.debug_mode = self.parser.getboolean('Settings', 'debug')
        self.max_volume = self.parser.getint('Settings', 'Volume_Threshold')
        self.detection_threshold = self.parser.getfloat('Settings', 'detection_threshold')

        screen_area = self.parser.get('Settings', 'tracking_zone').strip('()')
        cordies = screen_area.split(',')
        self.screen_area = tuple(map(int, cordies))

        # Initialize state variables
        self.coords = []
        self.total = 0
        self.STATE = "IDLE"
        self.stop_button = False
        self.state_left = win32api.GetKeyState(0x01)
        self.state_right = win32api.GetKeyState(0x02)
        self.fish_count = 0
        self.bait_counter = 0
        self.food_timer = 0

        # Window capture
        self.wincap = WindowCapture('Albion Online Client')

    def check_volume(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=2, rate=44100, input=True, frames_per_buffer=1024)
        while not self.stop_button:
            self.total = 0
            for _ in range(2):
                data = stream.read(1024)
                reading = audioop.max(data, 2)
                self.total += reading
                if self.total > self.max_volume and self.STATE not in ["SOLVING", "DELAY", "CASTING", "EATING"]:
                    self.do_minigame()

    def get_new_spot(self):
        return random.choice(self.coords)

    def cast_hook(self):
        while not self.stop_button:
            if self.STATE in ["CASTING", "STARTED"]:
                time.sleep(random.uniform(1.2, 3.0))
                if self.fish_count % 10 == 0:
                    pyautogui.press('1')
                    time.sleep(0.2)
                pyautogui.mouseUp()
                x, y = self.get_new_spot()
                pyautogui.moveTo(x, y, tween=pyautogui.linear, duration=0.2)
                time.sleep(0.2)
                pyautogui.mouseDown()
                time.sleep(random.uniform(0.2, 1.5))
                pyautogui.mouseUp()
                self.log_info(f"STATE {self.STATE}")
                time.sleep(2.5)
                self.STATE = "CAST"
            elif self.STATE == "CAST":
                time.sleep(20)
                if self.STATE == "CAST":
                    self.log_info("Seems to be stuck on cast. Recasting")
                    self.STATE = "CASTING"
    def eat_food(self):
        while not self.stop_button:
            time.sleep(1800)
            self.STATE = "EATING"
            if self.STATE == "EATING":
                self.log_info("EATING FOOD")
                pyautogui.press('2')
                self.STATE = "CASTING"
                


                
    def do_minigame(self):
        if self.STATE not in ["CASTING", "STARTED", "EATING"]:
            self.STATE = "SOLVING"
            self.log_info(f"STATE {self.STATE}")
            pyautogui.mouseDown()
            pyautogui.mouseUp()
            time.sleep(0.5)
            valid, location, size = self.detect_bobber()
            if valid == True:
                self.fish_count += 1
                self.bait_counter += 1
                while True:
                    valid, location, size = self.detect_bobber()
                    if valid == True:
                        if location <= int(size[1] / 2):
                            pyautogui.mouseDown()
                        elif location >= int(size[1] / 2):
                            pyautogui.mouseUp()
                            
                    else:
                        if self.STATE != "CASTING":
                            self.STATE = "CASTING"
                            pyautogui.mouseUp()
                            break
            else:
                self.STATE = "CASTING"

    def generate_coords(self):
        amount_of_coords = dpg.get_value("Amount Of Spots")
        if amount_of_coords == 0:
            amount_of_coords = 1
        for n in range(amount_of_coords):
            self.log_info(f"[spot: {n + 1}] | Press Spacebar over the spot you want")
            time.sleep(1)
            while True:
                if win32api.GetKeyState(0x20) < 0:
                    x, y = pyautogui.position()
                    self.coords.append([x, y])
                    self.log_info(f"Position: {n + 1} Saved. | {x, y}")
                    break
                time.sleep(0.001)

    def grab_screen(self):
        image_coords = []
        while True:
            if win32api.GetKeyState(0x20) < 0:
                x, y = pyautogui.position()
                image_coords.append([x, y])
                if len(image_coords) == 2:
                    break
            time.sleep(0.001)
        start_point, end_point = image_coords
        self.screen_area = start_point[0], start_point[1], end_point[0], end_point[1]
        self.log_info(f"Updated tracking area to {self.screen_area}")

    def detect_minigame(self, screenshot, bar):
        result = cv2.matchTemplate(screenshot, bar, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)
        if max_val >= self.detection_threshold:
            return True
        return False
        
    def detect_bobber(self):
        screenshot = self.wincap.get_screenshot(region=self.region)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
        bobber = cv2.imread(self.bobber)
        bar = cv2.imread(self.bar)
        result = cv2.matchTemplate(screenshot, bobber, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        return [self.detect_minigame(screenshot, bar), max_loc[0] + bobber.shape[1] // 2, screenshot.shape]
    
        
    def log_info(self, message):
        current_logs = dpg.get_value("LogWindow")
        updated_logs = f"{current_logs}\n{message}" if current_logs else message
        dpg.set_value("LogWindow", updated_logs)

    def save_settings(self):
        with open(self.settings_file, 'w') as configfile:
            self.parser.set('Settings', 'Volume_Threshold', str(self.max_volume))
            self.parser.set('Settings', 'tracking_zone', str(self.screen_area))
            self.parser.set('Settings', 'detection_threshold', str(self.detection_threshold))
            self.parser.write(configfile)
        self.log_info("Saved New Settings to settings.ini")

    def start_bot(self):
        self.log_info("Bot started successfully.")
        self.stop_button = False
        threading.Thread(target=self.eat_food).start()
        threading.Thread(target=self.check_volume).start()
        threading.Thread(target=self.cast_hook).start()
        time.sleep(1)
        pyautogui.press('q')
        time.sleep(2)
        self.STATE = "STARTED"

    def stop_bot(self):
        self.log_info("Bot stopped.")
        self.stop_button = True
        self.STATE = "STOPPED"

    def init_gui(self):
        dpg.create_context()
        dpg.create_viewport(title="Fisherman", width=700, height=500)

        with dpg.window(label="Fisherman Window", width=684, height=460):
            dpg.add_input_int(label="Amount Of Spots", tag="Amount Of Spots", max_value=10, min_value=1, default_value=1)
            dpg.add_input_int(label="Set Volume Threshold", tag="Set Volume Threshold", max_value=100000, min_value=0, default_value=self.max_volume)
            dpg.add_input_float(label="Set Detection Threshold", tag="Set Detection Threshold", min_value=0.1, max_value=1.0, default_value=self.detection_threshold)
            dpg.add_button(label="Set Fishing Spots", callback=self.generate_coords)
            dpg.add_button(label="Set Tracking Zone", callback=self.grab_screen)
            dpg.add_button(label="Start Bot", callback=self.start_bot)
            dpg.add_button(label="Stop Bot", callback=self.stop_bot)
            dpg.add_button(label="Save Settings", callback=self.save_settings)
            dpg.add_text("Log Messages:")
            dpg.add_input_text(multiline=True, readonly=True, width=650, height=150, tag="LogWindow", default_value="")

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()