# -*- coding: utf -8-*-

import time
import nest_asyncio
import json
import base64
import urllib.request
import os
from . import config
from robot import logging

from abc import ABCMeta, abstractmethod
from .sdk.did import Did

logger = logging.getLogger(__name__)
nest_asyncio.apply()


def get_engine_by_slug(slug=None):
    """
    Returns:
        A TTV Engine implementation available on the current platform

    Raises:
        ValueError if no speaker implementation is supported on this platform
    """

    if not slug or type(slug) is not str:
        raise TypeError("无效的 TTV slug '%s'", slug)

    selected_engines = list(
        filter(
            lambda engine: hasattr(engine, "SLUG") and engine.SLUG == slug,
            get_engines(),
        )
    )

    if len(selected_engines) == 0:
        raise ValueError(f"错误：找不到名为 {slug} 的 TTV 引擎")
    else:
        if len(selected_engines) > 1:
            logger.warning(f"注意: 有多个 TTV 名称与指定的引擎名 {slug} 匹配")
        engine = selected_engines[0]
        logger.info(f"使用 {engine.SLUG} TTV 引擎")
        return engine.get_instance()


def get_engines():
    def get_subclasses(cls):
        subclasses = set()
        for subclass in cls.__subclasses__():
            subclasses.add(subclass)
            subclasses.update(get_subclasses(subclass))
        return subclasses

    return [
        engine
        for engine in list(get_subclasses(AbstractTTV))
        if hasattr(engine, "SLUG") and engine.SLUG
    ]


class AbstractTTV(object):
    """
    Generic parent class for all TTV engines
    """

    __metaclass__ = ABCMeta

    @classmethod
    def get_config(cls):
        return {}

    @classmethod
    def get_instance(cls):
        # profile = cls.get_config()
        instance = cls()
        return instance

    @abstractmethod
    def get_video(self, phrase):
        pass


class DidTTV(AbstractTTV):
    """
    Did text to video
    """

    SLUG = "did"

    def __init__(
        self
    ) -> None:
        super(self.__class__, self).__init__()

        base_url = config.get('/did/base_url', 'https://api.d-id.com')
        api_key = config.get('/did/api_key')
        bytes_to_encode = api_key.encode("utf-8")
        credentials = 'Basic ' + \
            base64.b64encode(bytes_to_encode).decode("utf-8")
        provider = {
            "type": config.get('/did/provider/type', 'microsoft'),
            "voice_id": config.get('/did/provider/voice_id', 'zh-CN-XiaochenNeural')
        }
        image_url = config.get('/did/image_url', '')
        driver_url = config.get('/did/driver_url')
        self.client = Did(credentials, base_url,
                          provider, image_url, driver_url)
        try:
            self.gen_idle()
        except Exception as e:
            logger.critical(f'idle video generation failed {e}')

    @classmethod
    def get_config(cls):
        # Try to get did config from config
        return config.get("did", {})

    def generate_video(self, text, onGenerateCompleted=lambda: logger.info('d.id 文字转视频请求完成')):
        # """mock api return"""
        # return "tlk_k08Zc-P7t0QuxizuYC6VL"
        response = self.client.create_talk(text)
        result = json.loads(response.text)
        onGenerateCompleted()
        print(f'generate_video result is {result}')
        try:
            if result['status'] == 'created':
                logger.info(f"{self.SLUG} 文字合成视频成功，id: {result['id']}")
                return result['id']
            else:
                logger.critical(f"{self.SLUG} 文字合成视频失败！", stack_info=True)
        except AttributeError as e:
            logger.error('Attribute read error')
        except KeyError as e:
            logger.error('key read error')

    def get_video(self, id):
        response = self.client.get_talk(id)
        result = json.loads(response.text)

        # print(f'get_video result is \n {result}')
        try:
            if result['status'] == 'done':
                logger.info(f'{self.SLUG} 获取视频 {id} 成功')
                return result['result_url']
            elif result['status'] == 'started' or result['status'] == 'created':
                time.sleep(3)
                return self.get_video(id)
            else:
                logger.info(f'{self.SLUG} 获取视频 {id} 失败')
        except AttributeError as e:
            logger.error('Attribute read error')
        except KeyError as e:
            logger.error('key read error')

    def generate_animation(self, onGenerateCompleted=lambda: logger.info('d.id 动作转视频请求完成')):

        response = self.client.create_animation()
        result = json.loads(response.text)
        try:
            if result['status'] == 'created':
                logger.info(f"{self.SLUG} 动作视频成功，id: {result['id']}")
                return result['id']
            else:
                logger.critical(f"{self.SLUG} 动作合成视频失败！", stack_info=True)
        except AttributeError as e:
            logger.error('attr read error')
        onGenerateCompleted()

    def get_animation(self, id):
        response = self.client.get_animation(id)
        result = json.loads(response.text)
        try:
            if result['status'] == 'done':
                logger.info(f'{self.SLUG} 获取动作视频 {id} 成功')
                return result['result_url']
            elif result['status'] == 'started' or result['status'] == 'created':
                time.sleep(3)
                return self.get_animation(id)
            else:
                logger.info(f'{self.SLUG} 获取动作视频 {id} 失败')
        except AttributeError as e:
            logger.error('Attribute read error')
        except KeyError as e:
            logger.error('key read error')

    def download_video(self, url, path='./'):
        urllib.request.urlretrieve(url, path)

    # 生成空闲时的视频
    def gen_idle(self, idle_complete=lambda: logger.info(' idle 视频下载完成')):
        file_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '../static/idle.mp4'
        )
        if os.path.exists(file_path):
            logger.info('idle file exests')
            return
        else:
            logger.info('正在生成 idle 视频')
            animation_id = self.generate_animation()
            animation_url = self.get_animation(animation_id)
            self.download_video(animation_url, file_path)

        idle_complete()
