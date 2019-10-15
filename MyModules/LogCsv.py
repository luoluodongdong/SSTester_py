
import sys
import time
import csv
import os
import shutil


class SaveLog(object):
    """docstring for ClassName"""

    def __init__(self, path=None, swName="TEST"):
        super(SaveLog, self).__init__()
        #self.arg = arg
        date = time.strftime('%Y%m', time.localtime(time.time()))
        dateStr = self.GetDate()
        if path == None:
            self.path = sys.path[0] + '/LOG_' + swName + '/' + date + '/' + dateStr
        else:
            self.path = path + '/LOG_' + swName + '/' + date + '/' + dateStr
        self.CreatPath(self.path)
        # log
        self.log = ''
        # csv
        self.InitCsv('OnLine')

    # init csv
    def InitCsv(self, mode):
        # csv
        dateStr = self.GetDate()
        self.csvFile = self.path + '/' + dateStr + '_' + mode + '.csv'

    # creat log path
    def CreatPath(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    # save log file
    def SavePrint(self, sn="NA"):
        self.CreatPath(self.path)

        logPath = self.path + '/log'  # log path
        self.CreatPath(logPath)
        timeStr = self.GetTime()
        logFile = logPath + '/' + sn + '_' + timeStr + '.log'
        try:
            f = open(logFile, 'w')
            f.write(self.log)
        except Exception as e:
            print(e)
        finally:
            f.close()
            print(logFile)

    # creat csv file
    def CreatCsv(self, title):
        self.CreatPath(self.path)
        if os.path.exists(self.csvFile):
            return
        try:
            f = open(self.csvFile, 'w')
            f.write(title)
        except Exception as e:
            print(e)
        finally:
            f.close()

    # save csv log
    def SaveCsv(self, content):
        #content = content.replace('\r','')
        #content = content.replace('\n','')
        try:
            f = open(self.csvFile, 'a')
            f.write(content)
        except Exception as e:
            print(e)
        finally:
            f.close()
            print(self.csvFile)

    # get date:'20190313'
    def GetDate(self):
        return time.strftime('%Y%m%d', time.localtime(time.time()))

    def GetTime(self):
        return time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))


if __name__ == '__main__':
    testSaveLog = SaveLog()
    print(testSaveLog.path)
    print(testSaveLog.GetDate())
    print(testSaveLog.GetTime())
    # log
    testSaveLog.log = '123\n456'
    testSaveLog.SavePrint('sn123')
    # csv mode:OffLine
    testSaveLog.InitCsv('OffLine')
    testSaveLog.CreatCsv('SN,RESULT')
    testSaveLog.SaveCsv('123,PASS')
    # csv mode:OnLine
    testSaveLog.InitCsv('OnLine')
    testSaveLog.CreatCsv('SN,RESULT')
    testSaveLog.SaveCsv('456,FAIL')
