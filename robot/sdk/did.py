# -*- coding:utf-8 -*-

import requests
from robot import logging

logger = logging.getLogger(__name__)


class Did(object):
    def __init__(self, api_key, base_url, provider):
        self.api_key, self.base_url, self.provider = api_key, base_url, provider
        logger.info(api_key, base_url, provider)

    def create_talk(self, input):

        url = self.base_url + '/talks'
        authorization = "Basic " + self.api_key

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
            "source_url": "https://raw.githubusercontent.com/zexiplus/assets/main/image/xolson_chibi_avatar.png"
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": authorization
        }

        response = requests.post(url, json=payload, headers=headers)

        return response

    def get_talk(self, talk_id):
        url = f"https://api.d-id.com/talks/{talk_id}"
        authorization = "Basic " + self.api_key
        headers = {
            "accept": "application/json",
            "authorization": authorization
        }

        response = requests.get(url, headers=headers)

        return response
