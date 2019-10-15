# coding:UTF-8


class CheckSn(object):
    """docstring for CheckSn"""

    def __init__(self,logger):
        super(CheckSn, self).__init__()
        self.logger=logger

    def isOK(self,sn):
        self.logger.debug("this is CheckSn.isOK func")
        return True

