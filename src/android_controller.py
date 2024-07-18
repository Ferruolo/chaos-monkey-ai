import string
import subprocess
import time


class AndroidController:
    def __init__(self, DEVICE_NAME: string = "Pixel_4_API_35"):
        emulator_command = f"emulator -avd {DEVICE_NAME}"
        subprocess.Popen(emulator_command, shell=True)
        print(f"Starting emulator for {DEVICE_NAME}...")

        # Wait for the emulator to boot
        while True:
            result = subprocess.run(["adb", "shell", "getprop", "sys.boot_completed"], capture_output=True, text=True)
            if result.stdout.strip() == "1":
                print("Emulator is ready.")
                break
            time.sleep(1)

    @staticmethod
    def tap_area_on_screen(x: int, y: int):
        tap_command = f"adb shell input tap {x} {y}"
        subprocess.run(tap_command, shell=True)
        time.sleep(1)

    @staticmethod
    def swipe(x_start: int, y_start: int, x_end: int, y_end: int, time: int = 100):
        swipe_command = f"adb shell input swipe {x_start} {y_start} {x_end} {y_end} {time}"
        subprocess.run(swipe_command, shell=True)

    @staticmethod
    def get_screen():
        subprocess.run("adb shell uiautomator dump /sdcard/window_dump.xml", shell=True)
        subprocess.run("adb pull /sdcard/window_dump.xml", shell=True)
        time.sleep(0.5)
        with open("window_dump.xml", "r") as f:
            file = f.read()
        return file

    @staticmethod
    def shutdown():
        time.sleep(5)
        print("Shutting Down!")
        subprocess.run("adb emu kill", shell=True)
        time.sleep(20)

