import requests
import time
import json
import datetime
import colorama
from colorama import Fore, Style

colorama.init()
urlApiMe = 'https://arbuz.betty.games/api/users/me'
urlApiClick = 'https://arbuz.betty.games/api/click/apply'

headers = {
    'Content-Type': 'application/json',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    #'Baggage': 'sentry-environment=production,sentry-public_key=6e836760e898018c6059dfcdba712802,sentry-trace_id=a45d9e2c1596467cb19be6d72ee4c391',
    'accept-language': 'ru-UA,ru;q=0.9,uk-UA;q=0.8,uk;q=0.7,ru-RU;q=0.6,en-US;q=0.5,en;q=0.4',
    'Sec-Ch-Ua': '"Not_A Brand";v="99", "Google Chrome";v="121", Chromium";v="121"',
    'Sec-Ch-Ua-Mobile': '?1',
    'Sec-Ch-Ua-Platform': 'Android',
    #'Sentry-Trace': 'a45d9e2c1596467cb19be6d72ee4c391-83a9f4d27d78842f',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36',
    'X-Telegram-Init-Data': ('')
}
  # в скором времени постараюсь сделать еще более легитимно, посредством получения текущей даты + хеширования ее
# старый вариант
#data = {"count": 7}
#count_as_float =  round(float(data["count"]))
#energyPerClick = count_as_float #1

while True:
    try:
        # Получаем информацию о пользователе
        apiMeResponse = requests.get(urlApiMe, headers=headers, timeout=2)
        apiMeResponseJson = apiMeResponse.json()

        # Проверяем статус ответа
        if apiMeResponse.status_code == 200:
            # разные стринги/зависимости
            username = apiMeResponseJson.get('fullName', 'NO DATA')
            balance = apiMeResponseJson.get('clicks', 'NO DATA')
            rawEnergy = apiMeResponseJson.get('energy', 'NO DATA')
            energyBoostSum = round(apiMeResponseJson.get('energyBoostSum', 'NO DATA')) # сколько можно раз кликнуть чтоб энергия съелась (допустим 1 раз клика равен 7 count в дате, то есть можно 7 раз кликнуть и съестся 1 ячейка энергии)

            # умный рассчет клика с использованием energyBoostSum
            if energyBoostSum >= 20:
                data = {"count": 19}
                energyBoostSum = 19
            else:
                data = {"count": energyBoostSum}

            # Рассчитываем количество возможных кликов
            current_energy = round(apiMeResponseJson.get('energy', 0.0))
            clicksAvailable = current_energy // energyBoostSum # старый вариант energyPerClick

            #print(f'[DEBUG] current_energy: {current_energy} | energyBoostSum: {energyBoostSum}')
            # Выполняем клики в соответствии с доступной энергией
            for _ in range(clicksAvailable):
                apiClickResponse = requests.post(urlApiClick, json=data, headers=headers, timeout=2)
                apiClickResponseJson = apiClickResponse.json()

                # Проверяем статус ответа клика
                if apiClickResponse.status_code == 200:
                    # мусорные просчеты хуеты
                    apiClickArbuzCount = apiClickResponseJson.get('count', 'NO DATA')
                    arbuzPerRequest = energyBoostSum * apiClickArbuzCount # старый вариант count_as_float * apiClickArbuzCount
                    current_time = datetime.datetime.now().strftime("%H:%M:%S")
                    print(f'{Fore.LIGHTYELLOW_EX}[{Fore.LIGHTBLACK_EX}({current_time}){Fore.LIGHTWHITE_EX} {Fore.LIGHTBLUE_EX}CLICKED{Fore.LIGHTYELLOW_EX}]{Fore.LIGHTWHITE_EX} User: {Fore.GREEN}{username}{Style.RESET_ALL} {Fore.LIGHTYELLOW_EX}|{Fore.LIGHTWHITE_EX} Balance: {Fore.GREEN}{balance}{Fore.RED}🍉 {Fore.LIGHTYELLOW_EX}| {Fore.LIGHTWHITE_EX}Energy: {Fore.LIGHTBLUE_EX}{current_energy}{Fore.LIGHTYELLOW_EX}⚡️ | {Fore.LIGHTWHITE_EX}PerClick: {Fore.GREEN}{apiClickArbuzCount}{Fore.RED}🍉  {Fore.LIGHTYELLOW_EX}| {Fore.LIGHTWHITE_EX}PerRequest: {Fore.GREEN}{arbuzPerRequest}{Fore.RED}🍉')
                else:
                    print(f'[ERROR] {apiClickResponse.status_code} {apiClickResponse.text}')
                    break  # Прекращаем клики, если произошла ошибка

        #print(f'{apiMeResponse.text}')
        else:
            print(f'APIMeResponse Error: {apiMeResponse.status_code}')
            print(apiMeResponse.text)

    except json.decoder.JSONDecodeError:
        print(f"[ERROR] The response is not in JSON format.\n{apiMeResponse.text}")
    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out. Trying again.")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] A requests exception occurred: {e}")

    #перезапуск всего цикла
    #time.sleep(0.2)
