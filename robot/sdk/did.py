# -*- coding:utf-8 -*-

import requests
from robot import logging

logger = logging.getLogger(__name__)


class Did(object):
    def __init__(self, credentials, base_url, provider, image_url, driver_url):
        self.credentials, self.base_url, self.provider, self.image_url, self.driver_url = credentials, base_url, provider, image_url, driver_url

    def create_talk(self, input):

        url = self.base_url + '/talks'

        payload = {
            "script": {
                "type": "text",
                "subtitles": "false",
                "provider": self.provider,
                "ssml": "false",
                "input": input
            },
            "config": {
                "fluent": "false",
                "pad_audio": "0.0"
            },
            "source_url": self.image_url
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": self.credentials
        }

        response = requests.post(url, json=payload, headers=headers)

        return response

    def get_talk(self, talk_id):
        url = f"{self.base_url}/talks/{talk_id}"
        headers = {
            "accept": "application/json",
            "authorization": self.credentials
        }

        response = requests.get(url, headers=headers)

        return response

    def create_animation(self, driver_url=None):
        url = self.base_url + '/animations'
        d_url = driver_url if driver_url is not None else self.driver_url
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": self.credentials
        }

        payload = {
            "source_url": self.image_url,
            "driver_url": d_url
        }

        response = requests.post(url, json=payload, headers=headers)

        return response

    def get_animation(self, animation_id):

        url = f"{self.base_url}/animations/{animation_id}"
        headers = {
            "accept": "application/json",
            "authorization": self.credentials
        }

        response = requests.get(url, headers=headers)

        return response
