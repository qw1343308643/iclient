import os.path
import subprocess
from enum import Enum


class LED_CONTROL_CMD(Enum):
    # red led control
    red_led_close_cmd = "echo > 0 /sys/led_control/red_led"
    red_led_open_cmd = "echo > 1 /sys/led_control/red_led"
    red_led_light_cmd = "echo > 2 /sys/led_control/red_led"
    # green led control
    green_led_close_cmd = "echo > 0 /sys/led_control/green_led"
    green_led_open_cmd = "echo > 1 /sys/led_control/green_led"
    green_led_light_cmd = "echo > 2 /sys/led_control/green_led"
    # yellow led control
    yellow_led_close_cmd = "echo > 0 /sys/led_control/yellow_led"
    yellow_led_open_cmd = "echo > 1 /sys/led_control/yellow_led"
    yellow_led_light_cmd = "echo > 2 /sys/led_control/yellow_led"

class LedControl:
    @staticmethod
    def connectSuccess():
        if os.path.exists("/sys/led_control/red_led") and os.path.exists(
                    "/sys/led_control/green_led") and os.path.exists("/sys/led_control/yellow_led"):
            subprocess.run(LED_CONTROL_CMD.red_led_close_cmd.value, shell=True, capture_output=True)
            subprocess.run(LED_CONTROL_CMD.green_led_close_cmd.value, shell=True, capture_output=True)
            subprocess.run(LED_CONTROL_CMD.yellow_led_open_cmd.value, shell=True, capture_output=True)
            print("connectSuccess")

    @staticmethod
    def connectFail():
        if os.path.exists("/sys/led_control/red_led") and os.path.exists(
                "/sys/led_control/green_led") and os.path.exists("/sys/led_control/yellow_led"):
            subprocess.run(LED_CONTROL_CMD.red_led_close_cmd.value, shell=True, capture_output=True)
            subprocess.run(LED_CONTROL_CMD.green_led_close_cmd.value, shell=True, capture_output=True)
            subprocess.run(LED_CONTROL_CMD.yellow_led_close_cmd.value, shell=True, capture_output=True)
            print("connectFail")

    @staticmethod
    def testInProcess():
        if os.path.exists("/sys/led_control/red_led") and os.path.exists(
                "/sys/led_control/green_led") and os.path.exists("/sys/led_control/yellow_led"):
            subprocess.run(LED_CONTROL_CMD.red_led_close_cmd.value, shell=True, capture_output=True)
            subprocess.run(LED_CONTROL_CMD.green_led_light_cmd.value, shell=True, capture_output=True)
            subprocess.run(LED_CONTROL_CMD.yellow_led_open_cmd.value, shell=True, capture_output=True)
            print("testInProcess")

    @staticmethod
    def testError():
        if os.path.exists("/sys/led_control/red_led") and os.path.exists(
                "/sys/led_control/green_led") and os.path.exists("/sys/led_control/yellow_led"):
            subprocess.run(LED_CONTROL_CMD.red_led_light_cmd.value, shell=True, capture_output=True)
            subprocess.run(LED_CONTROL_CMD.green_led_light_cmd.value, shell=True, capture_output=True)
            subprocess.run(LED_CONTROL_CMD.yellow_led_open_cmd.value, shell=True, capture_output=True)
            print("testError")

    @staticmethod
    def completedNoFault():
        if os.path.exists("/sys/led_control/red_led") and os.path.exists(
                "/sys/led_control/green_led") and os.path.exists("/sys/led_control/yellow_led"):
            subprocess.run(LED_CONTROL_CMD.red_led_close_cmd.value, shell=True, capture_output=True)
            subprocess.run(LED_CONTROL_CMD.green_led_open_cmd.value, shell=True, capture_output=True)
            subprocess.run(LED_CONTROL_CMD.yellow_led_open_cmd.value, shell=True, capture_output=True)
            print("completedNoFault")

    @staticmethod
    def completedFault():
        if os.path.exists("/sys/led_control/red_led") and os.path.exists(
                "/sys/led_control/green_led") and os.path.exists("/sys/led_control/yellow_led"):
            subprocess.run(LED_CONTROL_CMD.red_led_open_cmd.value, shell=True, capture_output=True)
            subprocess.run(LED_CONTROL_CMD.green_led_open_cmd.value, shell=True, capture_output=True)
            subprocess.run(LED_CONTROL_CMD.yellow_led_open_cmd.value, shell=True, capture_output=True)
            print("completedFault")

