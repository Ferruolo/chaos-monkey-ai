import os
import string
import subprocess
import time
import pydantic
import json
from typing import List


class ControllerCommand(pydantic.BaseModel):
    command_name: str
    command_inputs: List[int]


class AndroidController:
    def __init__(self, DEVICE_NAME: string = "Pixel_4_API_35"):
        self.android_sdk_path = "/home/andrewf/Android/Sdk"
        self.emulator_path = os.path.join(self.android_sdk_path, "emulator", "emulator")
        self.adb_path = os.path.join(self.android_sdk_path, "platform-tools", "adb")

        emulator_command = f"{self.emulator_path} -avd {DEVICE_NAME}"
        subprocess.Popen(emulator_command, shell=True)
        print(f"Starting emulator for {DEVICE_NAME}...")

        # Wait for the emulator to boot
        while True:
            result = subprocess.run([self.adb_path, "shell", "getprop", "sys.boot_completed"], capture_output=True,
                                    text=True)
            if result.stdout.strip() == "1":
                print("Emulator is ready.")
                break
            time.sleep(1)

    def tap_area_on_screen(self, x: int, y: int):
        tap_command = f"{self.adb_path} shell input tap {x} {y}"
        print(tap_command)
        subprocess.run(tap_command, shell=True)
        time.sleep(1)

    def swipe(self, x_start: int, y_start: int, x_end: int, y_end: int, duration: int = 100):
        swipe_command = f"{self.adb_path} shell input swipe {x_start} {y_start} {x_end} {y_end} {duration}"
        subprocess.run(swipe_command, shell=True)

    def get_screen(self):
        subprocess.run(f"{self.adb_path} shell uiautomator dump /sdcard/window_dump.xml", shell=True)
        subprocess.run(f"{self.adb_path} pull /sdcard/window_dump.xml", shell=True)
        time.sleep(0.5)
        with open("window_dump.xml", "r") as f:
            file = f.read()
        return file

    def shutdown(self):
        time.sleep(5)
        print("Shutting Down!")
        subprocess.run(f"{self.adb_path} emu kill", shell=True)
        time.sleep(20)

    def parse(self, command: str) -> (bool, str):
        parsed_json = json.loads(command)
        command_mod = ControllerCommand(**parsed_json)

        # TODO: This is a bit verbose, and I don't like hardcoding
        # TODO: Clean it up!! Messy!
        if command_mod.command_name == "get_screen":
            return True, self.get_screen()
        elif command_mod.command_name == "tap":
            if len(command_mod.command_inputs) != 2:
                raise Exception("tap command takes two arguments")
            else:
                [x, y] = command_mod.command_inputs
                self.tap_area_on_screen(x, y)
                return True, ""
        elif command_mod.command_name == "swipe":
            if len(command_mod.command_inputs) < 5:
                raise Exception("swipe command takes 5 arguments")
            else:
                self.swipe(*command_mod.command_inputs)
                return True, ""
        elif command_mod.command_name == "shutdown":
            self.shutdown()
            return True, ""
        return False
