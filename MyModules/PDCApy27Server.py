# coding=utf-8
'''
just with
python2.7

'''
import os
import sys
import json
from py27pudding import *
from LoadTestplan import LoadTestPlan

import zmq
import time
from random import randrange
import ast


class ZMQLogger(object):
    """docstring for ClassName"""

    def __init__(self, port):
        super(ZMQLogger, self).__init__()
        self.cxt = zmq.Context()
        self.socket = self.cxt.socket(zmq.PUB)
        self.socket.bind("tcp://*:%d" % port)
        time.sleep(0.2)
        self.lprint('running logger on port:%d' %port)

    def lprint(self, msg):
        # print(msg)
        self.socket.send(msg.encode("utf8"))

    def destory(self):
        del self.cxt


class PDCAServer(object):
    """docstring for PDCAServer"""

    def __init__(self,index,testplan):
        super(PDCAServer, self).__init__()
        self.index=index
        self.testplan=testplan
        self.zmqLogger=ZMQLogger(1055 +self.index)
        if self.setupServer(5555 +self.index):
            self.runServer()

    def setupServer(self,port):
        try:
            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.REP)
            # port=5555
            self.socket.bind("tcp://*:%d" % port)
            self.myPrint("Running server on port:%s" %port)
        except Exception as err:
            self.myPrint('[ERR]init err:%s' %err)
            return 0
        self.myPrint('init OK')
        return 1

    def runServer(self):
        # serves only 5 request and dies
        while True:
            # Wait for next request from client
            message = self.socket.recv().decode("utf8")
            t1=time.time()
            self.myPrint('[RX]' +message)
            # delta_t=time.time()-t1
            # timer="%.6ss"%delta_t
            # ltimer="duration:%.6ss"%delta_t
            if message.upper() == 'EXIT':
                self.socket.send(('OK,EXIT').encode('utf8'))
                self.destory()
                break
            elif message.startswith('endTest'):
                reply=self.updatePDCA(message)
                self.socket.send((reply).encode('utf8'))

    def updatePDCA(self,message):
        try:
            data_arr=message.split('#')
            jsonData=data_arr[1]
            jsonDict=ast.literal_eval(jsonData)
            self.pdcaAction(jsonDict)

        except Exception as e:
            self.myPrint(str(e))
            return 'NG'
        else:
            return 'OK'

    def pdcaAction(self,jsonDict):
        self.myPrint('instantPudding version:' + pypudding.INSTANT_PUDDING_VERSION)
        gh_station = pypudding.IPGHStation()
        self.myPrint('station number: ' + str(gh_station[pypudding.IP_STATION_NUMBER]))
        self.myPrint('station line number: ' + str(gh_station[pypudding.IP_LINE_NUMBER]))
        self.myPrint('station mac address: ' + str(gh_station[pypudding.IP_MAC]))
        self.myPrint('station spider cap ip:' + str(gh_station[pypudding.IP_SPIDERCAB_IP]))
        del gh_station

        self.myPrint(jsonDict['sn'])
        self.myPrint(jsonDict['result'])
        self.myPrint(jsonDict['softwareName'])
        self.myPrint(jsonDict['softwareVersion'])

        self.myPrint(self.testplan['TestItems'])
        self.myPrint(self.testplan['Up'])
        self.myPrint(self.testplan['Low'])
        self.myPrint(self.testplan['Unit'])
        self.myPrint(self.testplan['PDCA'])

        uut = IPUUT(u'C076535001NHP5L3')
        uut.start()
        uut.add_attribute(pypudding.IP_ATTRIBUTE_STATIONSOFTWARENAME, u"PyPudding")
        uut.add_attribute(pypudding.IP_ATTRIBUTE_STATIONSOFTWAREVERSION, u'1.1')

        # pass fail test passing:
        spec = IPTestSpec('PassingTest')
        result = IPTestResult(pypudding.IP_PASS)
        uut.add_result(spec, result)

        # parametric test pass
        spec = IPTestSpec(u'Parametric data test', subtest_name='pass_test',
                          limits={'low_limit': 0, 'high_limit': 9}, unit=u'ly')
        result = IPTestResult(pypudding.IP_PASS, 4)
        uut.add_result(spec, result)

        # parametric test fail
        spec = IPTestSpec(u'Parametric data test', subtest_name=u'fail_test',
                          limits={'low_limit': 0, 'high_limit': 8}, unit='ly')
        result = IPTestResult(pypudding.IP_FAIL, 11, u'value out of range')
        uut.add_result(spec, result)

        uut.add_attribute(u'VBOOST_LEFT', u'0x01')

        path = os.path.split(__file__)[0] +'/py27pudding'
        plan_path = os.path.join(path, 'pypudding.py')
        self.myPrint(plan_path)
        uut.add_blob_file(u'myself', plan_path)

        uut.done()
        uut.commit(pypudding.IP_PASS)

        #
        #
        #
        #
        #------------------------------------------------

        reply = pypudding.IP_getJsonResultsObj(uut.uut)
        msg = pypudding.IP_reply_getError(reply)
        commit_obj = json.loads(msg)

        self.myPrint(commit_obj)
        blobs = commit_obj['blobs']

        pypudding.IP_reply_destroy(reply)
        del uut
        print('done.')

    def myPrint(self,msg):
        self.zmqLogger.lprint(str(msg))

    def destory(self):
        del self.context
        self.zmqLogger.destory()

# 读取传入的参数
print(sys.argv)
# 参数1：index
index=int(sys.argv[1])
# 加载TestPlan
print(sys.path[0])
#testplanFile = '/Users/weidongcao/Documents/PythonCode/SSTester/Resources/TestPlan.csv'
# 参数2：testplan文件路径
testplanFile=sys.argv[2]
ltp=LoadTestPlan(testplanFile)
testplan=ltp.context
print(testplan)
# 开启pdca服务器，运行在Python2.7环境下
pdcaServer=PDCAServer(index,testplan)



