import os
import subprocess
import threading
import time

from flaskr.arduino.ArduinoBoardWatcher import Device
from flaskr.arduino.CodeSplitter import extract_sections

arduino_cli = os.getenv("ARDUINO_CLI")
ota_password = os.getenv("OTA_PWD")
wlan_ssid = os.getenv('WLAN_SSID')
wlan_password = os.getenv('WLAN_PWD')
project_path = os.getenv('ARDUINO_PROJECT_PATH')
project_file_name = os.getenv('ARDUINO_PROJECT_FILE_NAME')

placeholderNames = {
    "init": "/* INIT_CODE_PLACEHOLDER */",
    "setup": "/* SETUP_CODE_PLACEHOLDER */",
    "loop": "/* LOOP_CODE_PLACEHOLDER */",
    "helper": "/* HELPER_CODE_PLACEHOLDER */",
    'ota_password': "/* PASSWORD_PLACEHOLDER */",
    'wlan_ssid': "/* WLAN_SSID_PLACEHOLDER */",
    'wlan_pwd': "/* WLAN_PWD_PLACEHOLDER */"
}

installation_queue: dict


def network_deployment_scheduler():
    while True:
        newly_deployed_devices = []
        for device_label in list(installation_queue.keys()):
            try:
                print(f"Deploying to {device_label}")
                item = installation_queue[device_label]
                _deploy_code_to_device(item['code'], item['device'], item['app'], False)
                newly_deployed_devices.append(device_label)
            except:
                print(f"Retrying deployment to {device_label}")
        for device_label in newly_deployed_devices:
            del installation_queue[device_label]
        time.sleep(1)


def schedule_network_deployment():
    global installation_queue
    installation_queue = {}
    deploy_thread = threading.Thread(target=network_deployment_scheduler)
    deploy_thread.start()


def deploy_code_to_device(code: str, device: Device, current_app, force=False):
    if force and device.is_network_device():
        print(f"Queuing network deployment to {device.label}")
        installation_queue[device.label] = {'code': code, 'device': device, 'app': current_app}
    else:
        _deploy_code_to_device(code, device, current_app, force)


def _deploy_code_to_device(code: str, device: Device, current_app, force: bool):
    try:
        split_code = extract_sections(code)
    except:
        raise FailedToSplitCodeError

    with current_app.open_resource("arduino/arduino_ota_template.ino", "r") as file:
        template_content = file.read()
        template_content = fill_out_template(template_content, split_code)

    code_path = os.path.join(project_path, project_file_name)
    with open(code_path, 'w') as output_file:
        output_file.write(template_content)

    if subprocess.run([arduino_cli, 'compile', code_path, "--fqbn", "esp8266:esp8266:d1_mini"]).returncode != 0:
        raise FailedToCompileError

    args = [arduino_cli, 'upload', code_path, "--fqbn", "esp8266:esp8266:d1_mini", "-l", device.protocol, "-p",
            device.port_name] if device.is_serial_device() else [arduino_cli, 'upload', code_path, "--fqbn",
                                                                 "esp8266:esp8266:d1_mini", "-l", device.protocol, "-p",
                                                                 device.port_name, "--upload-field", "password=geheim"]
    if subprocess.run(args).returncode != 0:
        if force:
            time.sleep(1)
            _deploy_code_to_device(code, device, current_app, True)
            return
        raise FailedToExecuteError


def deploy_code_to_device_threaded(code, device: Device, current_app):
    deploy_thread = threading.Thread(target=deploy_code_to_device, args=(code, device, current_app, True))
    deploy_thread.start()


def fill_out_template(template_content, split_code):
    template_content = template_content.replace(placeholderNames['init'], split_code["init"])
    template_content = template_content.replace(placeholderNames['setup'], split_code["setup"])
    template_content = template_content.replace(placeholderNames['loop'], split_code["loop"]).replace('strip.show();',
                                                                                                      'ArduinoOTA.handle();strip.show();')
    template_content = template_content.replace(placeholderNames['helper'],
                                                (split_code["inbetween"] + "\n" + (split_code["end"]))).replace(
        'strip.show();', 'ArduinoOTA.handle();strip.show();')
    template_content = template_content.replace(placeholderNames['ota_password'], ota_password)
    template_content = template_content.replace(placeholderNames['wlan_ssid'], wlan_ssid)
    template_content = template_content.replace(placeholderNames['wlan_pwd'], wlan_password)
    return template_content


class FailedToExecuteError(BaseException):
    pass


class FailedToSplitCodeError(BaseException):
    pass


class FailedToCompileError(BaseException):
    pass
