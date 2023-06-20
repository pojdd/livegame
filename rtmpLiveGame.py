from numba import cuda
import numpy as np
import time
import cv2
height = 480
width = 270
import datetime
from rtmpFast import rtmpFast
from dm import DrDanmu
import hashlib
import random

@cuda.jit
def getNextState(A,B):
    i, j = cuda.grid(2)
    #计算数量
    num=A[i-1,j-1]+A[i-1,j]+A[i-1,j+1]+A[i,j-1]+A[i,j+1]+A[i+1,j-1]+A[i+1,j]+A[i+1,j+1]
    if(B[i,j]==0):
        # b规则
        if(num==3 or num==6 or num == 7):
            B[i,j]=1
    else:
        # s规则
        if(num==2 or num==3):
            return
        else:
            B[i,j]=0

np.random.seed(1)
A = np.zeros((width,height))
# A[0:32,0:32]=np.random.randint(0,2,(32,32))
# A = np.random.randint(0,2,(width,height))
B = np.zeros((width,height))
dA = cuda.to_device(A)
dB = cuda.to_device(B)

if __name__=='__main__':
    rtmp=rtmpFast()
    dm=DrDanmu("1")
    while True:
        getNextState[(30,30),(9,16)](dA,dB)
        B = dB.copy_to_host()
        A = B.copy()
        img = np.uint8(B*255)
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                
        if(not dm.isEmpty()):
            info=dm.getdm()
            x=random.randint(1,width-32)
            y=random.randint(1,height-32)
            md5=hashlib.sha3_512(info.encode(encoding='UTF-8')).hexdigest()
            md51=hashlib.sha3_512((info+"5639879").encode(encoding='UTF-8')).hexdigest()
            num=int(md5+md51,16)
            data=[int(x) for x in bin(num)[2:].zfill(1024)]
            data=np.asarray(data)
            data=data.reshape(32,32)
            A[x:x+32,y:y+32]=data
            if(info[:2]=="清屏"):
                A = np.zeros((width,height))
                
        dA = cuda.to_device(A)
        img = cv2.resize(img,None,fx=4,fy=4,interpolation=cv2.INTER_NEAREST)
        # cv2.imshow("game",img)
        # cv2.waitKey(1)
        # now = datetime.datetime.now()
        # cv2.putText(img,str(now),(10,500), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2,cv2.LINE_AA)
        
        rtmp.pushimg(img)
        rtmp.waitNextTime()