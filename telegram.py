import requests
import yaml


conf = yaml.load(open("config.yaml"), Loader=yaml.FullLoader)

def get_url(method):
    return 'https://api.telegram.org/bot{0}:{1}/{2}'.format(conf['telegram']['bot_id'], conf['telegram']['token'], method)

def check_if_send_to_telegram():
    if conf['telegram'] == "false" or conf['telegram']['send_nothing'] is True:
        return False
    return True


def send_to_telegram(data):
    if not check_if_send_to_telegram():
        return
    telegram_settings = conf['telegram']

    url = get_url("sendMessage")
    string = str(data).replace(", ", "\n").replace("{", "").replace("}", "")
    if conf['telegram']['send_all'] is False:
        if 'success' not in data and 'time_to_load' not in data:
            return

    requests.post(
        url=url,
        data={'chat_id': telegram_settings['chat_id'], 'text': string}
    )


def send_to_photo(image_filename):
    if not check_if_send_to_telegram():
        return
    conf = yaml.load(open("config.yaml"), Loader=yaml.FullLoader)

    with open('config.yaml', 'w') as f:
        yaml.dump(conf, f)

    telegram_settings = conf['telegram']

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
    print(conf)
