import numpy as np
from PIL import Image
from skimage import io
from tqdm import tqdm

path = "path of the image"

def datagenerator(images,labels,batchsize, mode="train"):
    while True:
        start = 0
        end = batchsize
        while start  < len(images): 
            x = images[start:end] 
            images_list=[]
            for i in x:
                images_list.append(io.imread(path+i))
            y = labels[start:end]
            yield np.array(images_list),np.array(y)

            start += batchsize
            end += batchsize
