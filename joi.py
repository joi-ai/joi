#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import fire
import signal
import hashlib
import urllib3
import threading

from robot.Updater import Updater
from robot.Conversation import Conversation
from robot.LifeCycleHandler import LifeCycleHandler
from robot.Viewer import Viewer
from robot import config, utils, constants, logging, detector
from robot.detector import DetectorThread

from server import server
from tools import make_json, solr_tools

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class Joi(object):

    _profiling = False
    _debug = False

    def init(self):
        self.detector = None
        self.detector_thread = DetectorThread(detector.initDetector, self)
        self.porcupine = None
        self.viewer = Viewer(self)
        self._interrupted = False
        print(
            """
********************************************************
::::::'##::'#######::'####:::::::::::::'###::::'####:
:::::: ##:'##.... ##:. ##:::::::::::::'## ##:::. ##::
:::::: ##: ##:::: ##:: ##::::::::::::'##:. ##::: ##::
:::::: ##: ##:::: ##:: ##::'#######:'##:::. ##:: ##::
'##::: ##: ##:::: ##:: ##::........: #########:: ##::
 ##::: ##: ##:::: ##:: ##::::::::::: ##.... ##:: ##::
. ######::. #######::'####:::::::::: ##:::: ##:'####:
:......::::.......:::....:::::::::::..:::::..::....::
********************************************************
            版本：[{}]
            后台管理端：http://{}:{}
            如需退出，可以按 Ctrl-4 组合键

""".format(
                utils.get_file_content(
                    os.path.join(constants.APP_PATH, "VERSION"), "r"
                ).strip(),
                config.get("/server/host", "0.0.0.0"),
                config.get("/server/port", "5001"),
            )
        )

        self.conversation = Conversation(self._profiling, self)
        if (config.get('/ttv_engine/enable')):
            # todo: generate welcome video
            self.conversation.talk(
                f"{config.get('owner_name', '主人')} {config.get('welcome_statement', '请用唤醒词与我聊天吧')}", True, path=os.path.join(
                    os.path.abspath(os.path.dirname(__file__)),
                    './static/welcome.mp4'
                )
            )

        else:
            self.conversation.say(
                f"{config.get('owner_name', '主人')} {config.get('welcome_statement', '请用唤醒词与我聊天吧')}", True)
        self.lifeCycleHandler = LifeCycleHandler(self.conversation)
        self.lifeCycleHandler.onInit()

    def _signal_handler(self, signal, frame):
        self._interrupted = True
        utils.clean()
        self.lifeCycleHandler.onKilled()

    def _detected_callback(self, is_snowboy=True):
        def _start_record():
            logger.info("开始录音")
            self.conversation.isRecording = True
            utils.setRecordable(True)

        if not utils.is_proper_time():
            logger.warning("勿扰模式开启中")
            return
        if self.conversation.isRecording:
            logger.warning("正在录音中，跳过")
            return
        if is_snowboy:
            self.conversation.interrupt()
            utils.setRecordable(False)
        self.lifeCycleHandler.onWakeup()
        if is_snowboy:
            _start_record()

    def _interrupt_callback(self):
        return self._interrupted

    def run(self):
        self.init()
        # capture SIGINT signal, e.g., Ctrl+C
        signal.signal(signal.SIGINT, self._signal_handler)
        # 后台管理端
        server.run(self.conversation, self, debug=self._debug)
        try:
            # 初始化离线唤醒
            if config.get('/ttv_engine/enable'):
                self.detector_thread.start()
            else:
                detector.initDetector(self)

        except AttributeError:
            logger.error("初始化离线唤醒功能失败", stack_info=True)
            pass
        if config.get('/ttv_engine/enable'):
            self.viewer.exec_app()

    def help(self):
        print(
            """=====================================================================================
    python3 joi.py [命令]
    可选命令：
      md5                      - 用于计算字符串的 md5 值，常用于密码设置
      update                   - 手动更新 joi
      upload [thredNum]        - 手动上传 QA 集语料，重建 solr 索引。
                                 threadNum 表示上传时开启的线程数（可选。默认值为 10）
      profiling                - 运行过程中打印耗时数据
====================================================================================="""
        )

    def md5(self, password):
        """
        计算字符串的 md5 值
        """
        return hashlib.md5(str(password).encode("utf-8")).hexdigest()

    def update(self):
        """
        更新 joi
        """
        updater = Updater()
        return updater.update()

    def fetch(self):
        """
        检测 joi 的更新
        """
        updater = Updater()
        updater.fetch()

    def upload(self, threadNum=10):
        """
        手动上传 QA 集语料，重建 solr 索引
        """
        try:
            qaJson = os.path.join(constants.TEMP_PATH, "qa_json")
            make_json.run(constants.getQAPath(), qaJson)
            solr_tools.clear_documents(
                config.get("/anyq/host", "0.0.0.0"),
                "collection1",
                config.get("/anyq/solr_port", "8900"),
            )
            solr_tools.upload_documents(
                config.get("/anyq/host", "0.0.0.0"),
                "collection1",
                config.get("/anyq/solr_port", "8900"),
                qaJson,
                threadNum,
            )
        except Exception as e:
            logger.error(f"上传失败：{e}", stack_info=True)

    def restart(self):
        """
        重启 joi
        """
        logger.critical("程序重启...")
        try:
            self.detector.terminate()
        except AttributeError:
            pass
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def profiling(self):
        """
        运行过程中打印耗时数据
        """
        logger.info("性能调优")
        self._profiling = True
        self.run()

    def debug(self):
        """
        调试模式启动服务
        """
        logger.info("进入调试模式")
        self._debug = True
        self.run()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        joi = Joi()
        joi.run()
    elif "-h" in (sys.argv):
        joi = Joi()
        joi.help()
    else:
        fire.Fire(Joi)
