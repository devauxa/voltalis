import httpx
import json
import os
from unidecode import unidecode


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
    def __init__(self, username, password):
        self.credentials = {
            "username": username,
            "password": password,
            "stayLoggedIn": "true",
        }
        self.cookie_path = '/data/cookies.json' if os.getenv('NODE_ENV') == 'production' else 'cookies.json'
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
            if modulator_info["appliances"]["translationKey"] == "appliances.electricMeter":
                # Bypass compteur
                continue
            yield {
                "csLinkId": modulator_info["csLinkId"],
                "name": unidecode(modulator_info["name"].strip().replace(" ", "_"))
            }

    async def login(self):
        try:
            print("Login on voltalis")
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
        response = await self.api.get(f"/programmationEvent/getOnOffState.json?csLinkId={device_id}")
        response.raise_for_status()
        return response.json()["onOffState"]

    async def switch_turn_on_off_device(self, device_id, turn_on):
        current_status = await self.fetch_switch_device_status(device_id)
        print(f"Ask to switch {device_id}[{current_status}] to {turn_on}")
        if (current_status and not turn_on) or (not current_status and turn_on):
            data = {
                "csLinkList": [
                    {
                        "csLinkId": device_id,
                        "csLinkToCutId": device_id,
                        "modulation": False,
                        "status": turn_on,
                        "isProgrammable": True
                    }
                ]
            }
            response = await self.api.post('/programmationEvent/updateOnOffEvent', data=data)
            print(response.text)
            response.raise_for_status()
            return response.json()

    async def fetch_immediate_consumption_in_kw(self):
        self.ensure_is_logged_in()
        response = await self.api.get('/siteData/immediateConsumptionInkW.json')
        response.raise_for_status()  # Assurez-vous que la requête a réussi
        return response.json()  # Retourne le résultat JSON
