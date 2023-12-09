import requests

def send_to_telegram(data, send_to_telegram):
    token = "6972984435:AAGeBAFCALEoz2SXhHLX-uyyj0HWbVny9l8"
    string = str(data)
    # add \n after each key-value pair
    string = string.replace(", ", "\n")
    # remove { and }
    string = string.replace("{", "")
    string = string.replace("}", "")
    if send_to_telegram == "false":
        if 'success' not in data and 'time_to_load' not in data:
            return


    requests.post(
        url='https://api.telegram.org/bot{0}/{1}'.format(token, "sendMessage"),
        data={'chat_id': 277499288, 'text': string}
    )