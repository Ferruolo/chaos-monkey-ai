import os
import string
import subprocess
import time


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
