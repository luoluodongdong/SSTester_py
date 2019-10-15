# coding:UTF-8
import json
import sys
import os

currentPath=sys.path[0]
parentPath=os.path.dirname(currentPath)
print(currentPath)
print(parentPath)

resourceFolder=parentPath +'//Resources'

slotCfgJson=resourceFolder +"//SlotCfg.json"


with open(slotCfgJson,'r') as load_f:
    load_dict = json.load(load_f)


print(load_dict['Slot-0']['Serial1'])

print(load_dict['Slot-1'])

