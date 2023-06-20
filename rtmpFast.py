import cv2
# subprocess 模块允许我们启动一个新进程，并连接到它们的输入/输出/错误管道，从而获取返回值。
import subprocess
import time
import datetime

class rtmpFast:
    # 推流地址
    rtmp = "rtmp://live-push.bilivideo.com/live-bvc/"
    rtmp+="?streamname=&key=&schedule=rtmp&pflag=1"

    # 推流参数
    command = ['ffmpeg',
        '-y',
        '-f', 'rawvideo',
        '-vcodec','rawvideo',
        '-pix_fmt', 'bgr24',
        '-s', '1920*1080',
        '-r', '60',
        '-i', '-',
        '-c:v', 'h264_nvenc',
        '-pix_fmt', 'yuv420p',
        # '-preset', 'ultrafast',
        '-f', 'flv',
        rtmp]
    
    def __init__(self):
        self.pipe = subprocess.Popen(self.command, stdin=subprocess.PIPE)
        self.tgrtime=1/60.0
        self.start = time.perf_counter()
        pass
    def pushimg(self,img):
        self.pipe.stdin.write(img.tobytes())
    
    def waitNextTime(self):
        while True:
            end = time.perf_counter()
            dt=end-self.start
            ndt=self.tgrtime-dt
            if(ndt>0.025):
                time.sleep(0.015)
            elif(ndt>0.015):
                time.sleep(0.005)
            if dt > self.tgrtime:
                break
        self.start = time.perf_counter()

# frame=cv2.imread("img.png")
# rtmp=rtmpFast()
# 循环读取
# while True:
#     img=frame.copy()
#     now = datetime.datetime.now()
#     cv2.putText(img,str(now),(10,500), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2,cv2.LINE_AA)
#     rtmp.pushimg(img)
#     rtmp.waitNextTime()
    
    

