# coding:UTF-8
import os

TESTPLAN_COLUMN_COUNT = 16
###
# TestItems----0
INDEX_TESTITEMS = 0
# Group        1
INDEX_GROUP = 1
# Function-----2
INDEX_FUNC = 2
# Command      3
INDEX_CMD = 3
# ResSuffix----4
INDEX_RESSUFFIX = 4
# ValueType    5
INDEX_VALUETYPE = 5
# ValueSave----6
INDEX_VALUESAVE = 6
# Low          7
INDEX_LOW = 7
# ReferValue---8
INDEX_REFERVALUE = 8
# Up-----------9
INDEX_UP = 9
# Unit         10
INDEX_UNIT = 10
# TimeOut------11
INDEX_TIMEOUT = 11
# Delay        12
INDEX_DELAY = 12
# ExitEnable---13
INDEX_EXITENABLE = 13
# Skip         14
INDEX_SKIP = 14
# PDCA
INDEX_PDCA = 15
###


class LoadTestPlan(object):
    """docstring for LoadTestPlan"""

    def __init__(self,file):
        super(LoadTestPlan, self).__init__()
        self.csv=file
        self.data={}
        self.tpList,result=self.getList()
        if not result:
            print('load Testplan error!')
            raise
        # print(self.tpList)
        self.initArray()

    @property
    def context(self):
        '''
        self.data={
            'TestItems':['Waiting for fixture ready', 'Set LED on', 'Set LED off', ...],
            'Group':['SERIAL', 'SERIAL', 'SERIAL', 'STEP',...],
            ...
        }
        '''
        return self.data

    # 载入test plan
    def getList(self):
        r_list = []
        if not os.path.exists(self.csv):
            print('test plan file not exists')
            return r_list, 0

        try:
            stream = open(self.csv, 'r')
            r_list = stream.readlines()
            stream.close()
        except Exception as e:
            print('error:%s' % e)
            return r_list, 0
        else:
            pass
        finally:
            pass
        return r_list, 1

    def initArray(self):
        nameList=self.tpList[0].strip().split(',')
        for k in range(0,len(nameList)):
            self.data[nameList[k]]=[]

        for i in range(1, len(self.tpList)):
            line = self.tpList[i].strip().split(',')
            if len(line) != TESTPLAN_COLUMN_COUNT:
                print('error testplan line:\n' + line)
                raise
            self.data[nameList[INDEX_TESTITEMS]].append(line[INDEX_TESTITEMS])
            self.data[nameList[INDEX_GROUP]].append(line[INDEX_GROUP])
            self.data[nameList[INDEX_FUNC]].append(line[INDEX_FUNC])
            self.data[nameList[INDEX_CMD]].append(line[INDEX_CMD])
            self.data[nameList[INDEX_RESSUFFIX]].append(line[INDEX_RESSUFFIX])
            self.data[nameList[INDEX_VALUETYPE]].append(line[INDEX_VALUETYPE])
            self.data[nameList[INDEX_VALUESAVE]].append(line[INDEX_VALUESAVE])
            self.data[nameList[INDEX_LOW]].append(line[INDEX_LOW])
            self.data[nameList[INDEX_REFERVALUE]].append(line[INDEX_REFERVALUE])
            self.data[nameList[INDEX_UP]].append(line[INDEX_UP])
            self.data[nameList[INDEX_UNIT]].append(line[INDEX_UNIT])
            self.data[nameList[INDEX_TIMEOUT]].append(float(line[INDEX_TIMEOUT]))
            self.data[nameList[INDEX_DELAY]].append(float(line[INDEX_DELAY]))
            self.data[nameList[INDEX_EXITENABLE]].append(int(line[INDEX_EXITENABLE]))
            self.data[nameList[INDEX_SKIP]].append(int(line[INDEX_SKIP]))
            self.data[nameList[INDEX_PDCA]].append(int(line[INDEX_PDCA]))
            # break
