import httpx
import time
import json
import os
from unidecode import unidecode
import logging

_LOGGER = logging.getLogger(__name__)

def debug_curl(api, response):
    request = response.request

    curl_command = "curl -X {method} '{uri}'".format(
        method=request.method,
        uri=request.url
    )

    # Ajouter les headers à la commande curl.
    for header, value in request.headers.items():
        curl_command += " -H '{header}: {value}'".format(
            header=header,
            value=value.replace("'", "'\\''")
        )

    # Ajouter les cookies à la commande curl.
    if api.cookies:
        cookie_string = '; '.join(['{}={}'.format(k, v) for k, v in api.cookies.items()])
        curl_command += " -b '{cookies}'".format(cookies=cookie_string)

    # Si la requête a un corps, ajoutez-le aussi
    if request.content:
        curl_command += f" --data-raw '{request.content.decode()}'"

    _LOGGER.info(curl_command)

class VoltalisSite:
    def __init__(self, id, is_main, modulator_list):
        self.id = id
        self.is_main = is_main
        self.modulator_list = modulator_list

class VoltalisConsumption:
    def __init__(self, consumption, duration):
        self.consumption = consumption
        self.duration = duration

class Voltalis:
    last_update_consumption = 0
    last_data_consumption = None

    def __init__(self, username, password):
        self.credentials = {
            "username": username,
            "password": password,
            "stayLoggedIn": "true",
        }
        self.cookie_path = '/tmp/voltalis_cookies.json'
        self.user = None
        self.base_url = 'https://classic.myvoltalis.com'
        self.api = httpx.AsyncClient(base_url=self.base_url)

        if os.path.exists(self.cookie_path):
            with open(self.cookie_path, 'r') as f:
                cookies = json.load(f)
                for name, value in cookies.items():
                    self.api.cookies.set(name, value)
    def save_cookie_jar(self):
        with open(self.cookie_path, 'w') as f:
            json.dump(dict(self.api.cookies), f)

    def is_logged_in(self):
        return self.user is not None

    def ensure_is_logged_in(self):
        if not self.is_logged_in():
            raise Exception('Use .login() first')

    def get_main_site(self):
        self.ensure_is_logged_in()
        return next((site for site in self.user['subscriber']['siteList'] if site['isMain']), None)

    def get_modulators(self):
        self.ensure_is_logged_in()
        for modulator in self.get_main_site()["modulatorList"]:
            modulator_info = modulator["values"]["2"]
            if modulator_info["appliances"][0]["translationKey"] == "appliances.electricMeter":
                # Bypass compteur
                continue
            yield {
                "csLinkId": modulator_info["csLinkId"],
                "name": unidecode(modulator_info["name"].strip().replace(" ", "_"))
            }

    async def login(self):
        try:
            _LOGGER.info("Login on voltalis")
            response = await self.api.post('/login', data=self.credentials)
            response.raise_for_status()
            self.user = response.json()
            self.api.headers["User-Site-Id"] = str(self.get_main_site()["id"])

            self.save_cookie_jar()
            return self.user
        except httpx.HTTPStatusError as http_err:
            if http_err.response.status_code == 401:
                raise Exception('Bad Credentials')
            else:
                raise Exception('Unable to login')
        except Exception as err:
            raise Exception('An error occurred during login')


    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.api.aclose()

    async def fetch_switch_device_status(self, device_id):
        _LOGGER.debug(f"Fetch status for {device_id}")
        response = await self.api.get(f"/programmationEvent/getOnOffState.json?csLinkId={device_id}")
        response.raise_for_status()
        status = response.json()["onOffState"]
        _LOGGER.debug(f"{device_id} is {status} state")
        return status

    async def switch_turn_on_off_device(self, device_id, turn_on):
        current_status = await self.fetch_switch_device_status(device_id)
        _LOGGER.debug(f"Ask to switch {device_id}[{current_status}] to {turn_on}")
        if (current_status and not turn_on) or (not current_status and turn_on):
            data = {
                "csLinkList": [
                    {
                        "csLinkId": device_id,
                        "csLinkToCutId": device_id,
                        "isProgrammable": True,
                        "modulation": False,
                        "status": turn_on,
                    }
                ]
            }
            response = await self.api.post('/programmationEvent/updateOnOffEvent', json=data)
            response.raise_for_status()
            return response.json()

    async def fetch_immediate_consumption_in_kw(self):
        # Retourne les datas sauvegardé si nouveau call < 10 min
        if self.last_update_consumption + 60 * 10 >= time.time():
            _LOGGER.debug(f"Fetch consumption from storage")
            return self.last_data_consumption

        self.ensure_is_logged_in()
        _LOGGER.debug(f"Fetch consumption from voltalis")
        response = await self.api.get('/siteData/immediateConsumptionInkW.json')
        response.raise_for_status()  # Assurez-vous que la requête a réussi
        self.last_update_consumption = time.time()
        self.last_data_consumption = response.json()
        return self.last_data_consumption
