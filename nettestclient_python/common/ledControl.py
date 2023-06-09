import os.path
from utility.fileLock import CFileLock

RED_LED_PATH = "/sys/led_control/red_led"
GREEN_LED_PATH = "/sys/led_control/green_led"
YELLOW_LED_PATH = "/sys/led_control/yellow_led"

LED_CONTROL_CMD_TYPE = {
    "online": {"red": "0", "greed": "0", "yellow": "1"},
    "offline": {"red": "0", "greed": "0", "yellow": "0"},
    "testing": {"red": "0", "greed": "2", "yellow": "1"},
    "testStepFail": {"red": "2", "greed": "2", "yellow": "1"},
    "testPass": {"red": "0", "greed": "1", "yellow": "1"},
    "testFail": {"red": "1", "greed": "1", "yellow": "1"}
}


class LedControl:
    @staticmethod
    def isExitPath():
        if os.path.exists(RED_LED_PATH) and os.path.exists(GREEN_LED_PATH) and os.path.exists(YELLOW_LED_PATH):
            return True
        else:
            return False

    @staticmethod
    def echoControlFileValue(path, value):
        with open(path, "w") as f:
            f.write(str(value))
            f.flush()

    @staticmethod
    def online():
        if LedControl.isExitPath():
            print("set led online")
            LedControl.echoControlFileValue(RED_LED_PATH, LED_CONTROL_CMD_TYPE.get("online").get("red"))
            LedControl.echoControlFileValue(GREEN_LED_PATH, LED_CONTROL_CMD_TYPE.get("online").get("greed"))
            LedControl.echoControlFileValue(YELLOW_LED_PATH, LED_CONTROL_CMD_TYPE.get("online").get("yellow"))
            print("online")

    @staticmethod
    def offline():
        if LedControl.isExitPath():
            print("set led offline")
            LedControl.echoControlFileValue(RED_LED_PATH, LED_CONTROL_CMD_TYPE.get("offline").get("red"))
            LedControl.echoControlFileValue(GREEN_LED_PATH, LED_CONTROL_CMD_TYPE.get("offline").get("greed"))
            LedControl.echoControlFileValue(YELLOW_LED_PATH, LED_CONTROL_CMD_TYPE.get("offline").get("yellow"))
            print("offline")

    @staticmethod
    def testing():
        if LedControl.isExitPath():
            print("set led testing")
            LedControl.echoControlFileValue(RED_LED_PATH, LED_CONTROL_CMD_TYPE.get("testing").get("red"))
            LedControl.echoControlFileValue(GREEN_LED_PATH, LED_CONTROL_CMD_TYPE.get("testing").get("greed"))
            LedControl.echoControlFileValue(YELLOW_LED_PATH, LED_CONTROL_CMD_TYPE.get("testing").get("yellow"))
            print("testing")

    @staticmethod
    def testStepFail():
        if LedControl.isExitPath():
            print("set led test step error")
            LedControl.echoControlFileValue(RED_LED_PATH, LED_CONTROL_CMD_TYPE.get("testStepFail").get("red"))
            LedControl.echoControlFileValue(GREEN_LED_PATH, LED_CONTROL_CMD_TYPE.get("testStepFail").get("greed"))
            LedControl.echoControlFileValue(YELLOW_LED_PATH, LED_CONTROL_CMD_TYPE.get("testStepFail").get("yellow"))
            print("test step error")

    @staticmethod
    def testPass():
        if LedControl.isExitPath():
            print("set led test pass")
            LedControl.echoControlFileValue(RED_LED_PATH, LED_CONTROL_CMD_TYPE.get("testPass").get("red"))
            LedControl.echoControlFileValue(GREEN_LED_PATH, LED_CONTROL_CMD_TYPE.get("testPass").get("greed"))
            LedControl.echoControlFileValue(YELLOW_LED_PATH, LED_CONTROL_CMD_TYPE.get("testPass").get("yellow"))
            print("test pass")

    @staticmethod
    def testFail():
         if LedControl.isExitPath():
            print("set led testFail")
            LedControl.echoControlFileValue(RED_LED_PATH, LED_CONTROL_CMD_TYPE.get("testFail").get("red"))
            LedControl.echoControlFileValue(GREEN_LED_PATH, LED_CONTROL_CMD_TYPE.get("testFail").get("greed"))
            LedControl.echoControlFileValue(YELLOW_LED_PATH, LED_CONTROL_CMD_TYPE.get("testFail").get("yellow"))
            print("testFail")

