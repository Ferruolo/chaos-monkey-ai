import json
import os
import string
import subprocess
import time
from typing import List
import re
import pydantic
from dotenv import load_dotenv

load_dotenv()


# We use Pydantic to enforce the format of the object.
# Python Errors then allow us to create a basic Chain-of-Thought
# Feedback process which should eventually give us the right type

class ControllerCommand(pydantic.BaseModel):
    command_name: str
    command_inputs: List[int]


def parse_json(x):
    json_pattern = re.compile(
        '\{\s*"command_name"\s*:\s*"(tap|swipe|shutdown|enable-wifi|disable-wifi|get-screen|close-app|do-nothing)"\s*,\s*"command_inputs"\s*:\s*\[((?:\d+(?:\s*,\s*\d+){1,5})?)\]\s*\}')
    json_match = json_pattern.search(x)
    if json_match:
        json_command = json_match.group(0)
        # Print the formatted JSON
        parsed_json = json.loads(json_command)
        return parsed_json
    else:
        raise Exception("JSON command not found in the input text.")


# Main Android Controller Class
# Creates wrapper around ADB shell, preventing us from a situation where we have LLM straight to terminal
# as that could create some major issues
class AndroidController:
    def __init__(self, device_name: string = "Pixel_Fold_API_35"):
        self.android_sdk_path = os.getenv("ANDROID_SDK_PATH")
        self.emulator_path = os.path.join(self.android_sdk_path, "emulator", "emulator")
        self.adb_path = os.path.join(self.android_sdk_path, "platform-tools", "adb")

        emulator_command = f"{self.emulator_path} -avd {device_name}"
        subprocess.Popen(emulator_command, shell=True)
        print(f"Starting emulator for {device_name}...")

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
        wifi_code = subprocess.run(f"{self.adb_path} shell settings get global wifi_on", shell=True)
        print(f"Wifi Code: {wifi_code}")
        # if wifi_code:
        #     file += "Wifi is On"
        # else:
        #     file += "Wifi is off"

        return file

    def disable_wifi(self):
        enable_command = f"{self.adb_path} shell cmd connectivity airplane-mode enable"
        result = subprocess.run(enable_command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Failed to enable Airplane mode. Error: {result.stderr}")

        return True, "Wifi Turned Off."

    def enable_wifi(self):
        disable_command = f"{self.adb_path} shell cmd connectivity airplane-mode disable"
        result = subprocess.run(disable_command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Failed to disable Airplane mode. Error: {result.stderr}")

        return True, "Wifi Turned back On."

    def close_application(self):
        # Todo: make this more flexible with the AI. RN I just need to ship a demo :(
        close_cmd = f"{self.adb_path} shell am force-stop com.example.my_sample_application"
        result = subprocess.run(close_cmd, shell=True, capture_output=True)

        if result.returncode != 0:
            raise Exception("Did not close app")
        return True, ""

    def shutdown(self):
        time.sleep(5)
        print("Shutting Down!")
        subprocess.run(f"{self.adb_path} emu kill", shell=True)
        time.sleep(10)

    def push_app(self, app_path: str, app_filename: str):
        # TODO: This doesn't work, abandoning for now
        if not os.path.exists(app_path):
            raise FileNotFoundError(f"The app file does not exist at path: {app_path}")

        print(f"App Filename: {app_filename}")

        # Push the app to the device
        push_command = f"{self.adb_path} push \"{app_path}\" /data/local/tmp/{app_filename}"
        result = subprocess.run(push_command, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"Failed to push app to device. Error: {result.stderr}")

        print(f"Successfully pushed {app_filename} to the device.")

        # Install the app
        install_command = f"{self.adb_path} shell pm install -r /data/local/tmp/{app_filename}"
        result = subprocess.run(install_command, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"Failed to install app on device. Error: {result.stderr}")

        print(f"Successfully installed {app_filename} on the device.")

        # Clean up the temporary file
        cleanup_command = f"{self.adb_path} shell rm /data/local/tmp/{app_filename}"
        subprocess.run(cleanup_command, shell=True)

        return True, f"App {app_filename} has been successfully pushed and installed on the device."

    def parse(self, command: str) -> (bool, str):
        parsed_json = parse_json(command)
        print(parsed_json)
        command_mod = ControllerCommand(**parsed_json)

        if command_mod.command_name == "get-screen":
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
        elif command_mod.command_name == "enable-wifi":
            return self.enable_wifi()
        elif command_mod.command_name == "disable-wifi":
            return self.disable_wifi()
        elif command_mod.command_name == "close-app":
            return self.close_application()
        elif command_mod.command_name == "do-nothing":
            return True, "Did Nothing!"
        return False, ("Accepted Commands are get-screen, tap, swipe, shutdown, enable-wifi, disable-wifi. Please only "
                       "select from these")
