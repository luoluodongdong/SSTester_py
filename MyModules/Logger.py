# coding:UTF-8
import logging
import sys
import os
import time


class MyLogger(object):
    """docstring for MyLogger"""

    def __init__(self, name, path=None, level=logging.DEBUG):
        super(MyLogger, self).__init__()
        self.name = name
        if not path:
            ymStr = time.strftime('%Y%m', time.localtime(time.time()))
            ymdStr = time.strftime('%Y%m%d', time.localtime(time.time()))
            ymdhmStr = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
            logPath = sys.path[0] + '/TerminalLog/' + ymStr + '/' + ymdStr + '/' + ymdhmStr
            self.savePath = logPath
        else:
            self.savePath = path
        self.logger = logging.getLogger(self.name)
        self.level = level
        self.setup()

    def setup(self):
        self.logger.setLevel(level=self.level)
        # log file print out
        if not os.path.exists(self.savePath):
            os.makedirs(self.savePath)
        timeStr = time.strftime('_%Y%m%d%H%M%S_', time.localtime(time.time()))
        fileName = self.savePath + '/' + self.name + timeStr + 'log.txt'
        handler = logging.FileHandler(fileName)
        handler.setLevel(level=self.level)
        formater = logging.Formatter('[%(asctime)s]:[%(name)s] - %(levelname)s - %(message)s')
        handler.setFormatter(formater)
        # log console print out
        console = logging.StreamHandler()
        console.setLevel(self.level)
        console.setFormatter(formater)
        # add handler
        self.logger.addHandler(handler)
        self.logger.addHandler(console)
        # first print
        self.logger.info('----new log.txt creat----')
        self.logger.info('log level:%s' % str(logging.getLevelName(self.logger.level)))
