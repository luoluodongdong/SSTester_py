# coding:UTF-8
import json
import sys
import os


class RWjson(object):
    """docstring for RWjson"""

    def __init__(self, name):
        super(RWjson, self).__init__()
        self.name = name
        self.currentPath=sys.path[0]
        # self.parentPath=os.path.dirname(self.currentPath)
        self.resourceFolder=self.currentPath +'/Resources'
        self.json=self.resourceFolder +'/' +self.name

    def loadJson(self):
        load_dict={}
        try:
            with open(self.json,'r') as load_f:
                load_dict = json.load(load_f)
            return 1,load_dict
        except Exception as e:
            print(str(e))

        return 0,{}

    def saveJson(self,root_dict):
        try:
            with open(self.json,"w") as f:
                f.write(json.dumps(root_dict,indent=4))
            return 1
        except Exception as e:
            print(str(e))
        return 0


if __name__ == '__main__':
    rwJson=RWjson('SlotCfg.json')
    result,load_dict=rwJson.loadJson()
    print(load_dict['Slot-0']['Dev0'])

    print(load_dict['Slot-1'])
