import matplotlib.pyplot as plt
import imageio
import os
import sys

from PIL import Image
frames=[]
print(sys.path[0])
filepath=sys.path[0]
# filenames=os.listdir(filepath)
# for filename in os.listdir(filepath):
#     GIF.append(imageio.imread(filepath +"\\" +filename))
frames.append(imageio.imread(filepath +'/App.png'))
imageio.mimsave(filepath +'/result.gif',frames,'GIF',duration=1.0)  # 这个duration是播放速度，数值越小，速度越快
