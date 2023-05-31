import logging
import multiprocessing
import os
import time
import pickle
import time
import _thread as thread

from watchdog.observers import Observer
from robot import config, constants, statistic, Player
from robot.ConfigMonitor import ConfigMonitor
from robot.sdk import LED

logger = logging.getLogger(__name__)

LOCAL_REMINDER = os.path.join(constants.TEMP_PATH, "reminder.pkl")


def singleton(cls):
    _instance = {}

    def inner(conversation):
        if cls not in _instance:
            _instance[cls] = cls(conversation)
        return _instance[cls]

    return inner


"""
抽象出来的生命周期，
方便在这里针对 joi 的各个状态做定制
"""


@singleton
class LifeCycleHandler(object):
    def __init__(self, conversation):
        self._observer = Observer()
        self._unihiker = None
        self._wakeup = None
        self._conversation = conversation

    def onInit(self):
        """
        joi 初始化
        """
        config.init()
        statistic.report(0)

        # 初始化配置监听器
        config_event_handler = ConfigMonitor(self._conversation)
        self._observer.schedule(config_event_handler,
                                constants.CONFIG_PATH, False)
        self._observer.schedule(config_event_handler,
                                constants.DATA_PATH, False)
        self._observer.start()

        # 加载历史提醒
        self._read_reminders()

        # LED 灯
        self._init_LED()

    def _read_reminders(self):
        logger.info("重新加载提醒信息")
        if os.path.exists(LOCAL_REMINDER):
            with open(LOCAL_REMINDER, "rb") as f:
                jobs = pickle.load(f)
                for job in jobs:
                    if "repeat" in job.remind_time or int(time.time()) < int(
                        job.job_id
                    ):
                        logger.info(
                            f"加入提醒: {job.describe}, job_id: {job.job_id}")
                        if not (self._conversation.scheduler.has_job(job.job_id)):
                            self._conversation.scheduler.add_job(
                                job.remind_time,
                                job.original_time,
                                job.content,
                                lambda: self.alarm(
                                    job.remind_time, job.content, job.job_id
                                ),
                                job_id=job.job_id,
                            )

    def _init_LED(self):
        if config.get("/LED/enable", False) and config.get("/LED/type") == "aiy":
            thread.start_new_thread(self._aiy_button_event, ())

    def _aiy_button_event(self):
        """
        Google AIY VoiceKit 的监听逻辑
        """
        try:
            from aiy.board import Board
        except ImportError:
            logger.error(
                "错误：请确保当前硬件环境为Google AIY VoiceKit并正确安装了驱动", stack_info=True)
            return
        with Board() as board:
            while True:
                board.button.wait_for_press()
                logger.info("Google AIY Voicekit 触发唤醒")
                self._conversation.interrupt()
                query = self._conversation.activeListen()
                self._conversation.doResponse(query)

    def _beep_hi(self, onCompleted=None):
        Player.play(constants.getData("beep_hi.wav"), onCompleted)

    def _beep_lo(self):
        Player.play(constants.getData("beep_lo.wav"))

    def onWakeup(self, onCompleted=None):
        """
        唤醒并进入录音的状态
        """
        logger.info("onWakeup")
        self._beep_hi(onCompleted=onCompleted)
        if config.get("/LED/enable", False):
            LED.wakeup()
        self._unihiker and self._unihiker.record(1, "我正在聆听...")
        self._unihiker and self._unihiker.wakeup()

    def onThink(self):
        """
        录音结束并进入思考的状态
        """
        logger.info("onThink")
        self._beep_lo()
        self._unihiker and self._unihiker.think()
        self._unihiker and self._unihiker.record(1, "我正在思考...")
        if config.get("/LED/enable", False):
            LED.think()

    def onResponse(self, t=1, text=""):
        """
        思考完成并播放结果的状态
        """
        if t == 1:
            text = text[:60] + "..." if len(text) >= 60 else text
        else:
            text = text[:9] + "..." if len(text) >= 9 else text
        self._unihiker and self._unihiker.record(t, text)
        if config.get("/LED/enable", False):
            LED.off()

    def onRestore(self):
        """
        恢复沉浸式技能的状态
        """
        logger.info("onRestore")

    def onKilled(self):
        logger.info("onKill")
        self._observer.stop()
