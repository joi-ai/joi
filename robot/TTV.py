# -*- coding: utf -8-*-

import nest_asyncio

import json
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
    Did 文字转视频技术
    """

    SLUG = "did"

    def __init__(
        self
    ) -> None:
        super(self.__class__, self).__init__()

        base_url = config.get('/did/base_url', 'https://api.d-id.com')
        api_key = config.get('/did/api_key')
        provider = {
            "type": config.get('/did/provider/type', 'microsoft'),
            "voice_id": config.get('/did/provider/voice_id', 'en-US-JennyNeural')
        }
        self.client = Did(api_key, base_url, provider)

    @classmethod
    def get_config(cls):
        # Try to get did config from config
        return config.get("did", {})

    def generate_video(self, text, onGenerateCompleted=lambda: logger.info('d.id 视频合成完成')):
        """mock api return"""
        return "tlk_Ha958OH-5kvyw778ZdJOk"
        response = self.client.create_talk(text)
        result = json.loads(response.text)
        onGenerateCompleted()
        try:
            if result['status'] == 'created':
                logger.info(f"{self.SLUG} 文字合成视频成功，id: {result['id']}")
                return result['id']
            else:
                logger.critical(f"{self.SLUG} 文字合成视频失败！", stack_info=True)
        except AttributeError as e:
            logger.error('attr read error')

    def get_video(self, id):
        response = self.client.get_talk(id)
        result = json.loads(response.text)
        return result['result_url']
