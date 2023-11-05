import os
import subprocess

from flask import current_app

from flaskr.arduino.CodeSplitter import extract_sections

arduino_cli = os.getenv("ARDUINO_CLI")
ota_password = os.getenv("OTA_PWD")
wlan_ssid = os.getenv('WLAN_SSID')
wlan_password = os.getenv('WLAN_PWD')

placeholderNames = {
    "init": "/* INIT_CODE_PLACEHOLDER */",
    "setup": "/* SETUP_CODE_PLACEHOLDER */",
    "loop": "/* LOOP_CODE_PLACEHOLDER */",
    "helper": "/* HELPER_CODE_PLACEHOLDER */",
    'ota_password': "/* PASSWORD_PLACEHOLDER */",
    'wlan_ssid': "/* WLAN_SSID_PLACEHOLDER */",
    'wlan_pwd': "/* WLAN_PWD_PLACEHOLDER */"
}


def deploy_locally(code):
    try:
        split_code = extract_sections(code)
    except:
        raise FailedToSplitCodeError

    # with open("arduino_ota_template.ino", "r") as file:
    with current_app.open_resource("arduino/arduino_ota_template.ino", "r") as file:
        template_content = file.read()
        template_content = template_content.replace(placeholderNames['init'], split_code["init"])
        template_content = template_content.replace(placeholderNames['setup'], split_code["setup"])
        template_content = template_content.replace(placeholderNames['loop'], split_code["loop"])
        template_content = template_content.replace(placeholderNames['helper'],
                                                    split_code["inbetween"] + "\n" + (split_code["end"]))
        template_content = template_content.replace(placeholderNames['ota_password'], ota_password)
        template_content = template_content.replace(placeholderNames['wlan_ssid'], wlan_ssid)
        template_content = template_content.replace(placeholderNames['wlan_pwd'], wlan_password)

    codePath = os.path.join("/home/vakem/Software/Sources/LightRainLive", 'LightRainLive.ino')
    with open(codePath, 'w') as output_file:
        output_file.write(template_content)

    subprocess.run([arduino_cli, 'core', "install", "esp8266:esp8266"])
    result = subprocess.run(
        [arduino_cli, 'compile', codePath, "--fqbn", "esp8266:esp8266:d1_mini", "-l", "serial", "-u", "-p",
         "/dev/ttyUSB0"])
    if result.returncode != 0:
        print(f"Fehler: Der Befehl wurde mit dem Statuscode {result.returncode} beendet.")
        raise FailedToExecuteError


class FailedToExecuteError(BaseException):
    pass


class FailedToSplitCodeError(BaseException):
    pass
