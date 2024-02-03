import requests
import yaml

import utils


def get_url(method):
    return 'https://api.telegram.org/bot{0}:{1}/{2}'.format(utils.conf['telegram']['bot_id'], utils.conf['telegram']['token'], method)

def check_if_send_to_telegram():
    if utils.conf['telegram'] == "false" or utils.conf['telegram']['send_nothing'] is True:
        return False
    return True


def send_to_telegram(data):
    if not check_if_send_to_telegram():
        return
    telegram_settings = utils.conf['telegram']

    url = get_url("sendMessage")
    string = str(data).replace(", ", "\n").replace("{", "").replace("}", "")
    if utils.conf['telegram']['send_all'] is False:
        if 'success' not in data and 'time_to_load' not in data:
            return

    requests.post(
        url=url,
        data={'chat_id': telegram_settings['chat_id'], 'text': string}
    )


def send_to_photo(image_filename):
    if not check_if_send_to_telegram():
        return

    # with open('../config.yaml', 'w') as f:
    #     yaml.dump(utils.conf, f)

    telegram_settings = utils.conf['telegram']

    url = get_url("sendPhoto")

    files = {'photo': open(image_filename, 'rb')}
    data = {'chat_id': telegram_settings['chat_id']}
    requests.post(
        url=url,
        data=data,
        files=files
    )

if __name__ == '__main__':
    print("Hello from telegram.py")
    print(utils.conf)
