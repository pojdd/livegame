import asyncio
import zlib
from aiowebsocket.converses import AioWebSocket
import json
import threading
import time

import queue
import threading
import time

class dmThread(threading.Thread):
    remote = 'ws://broadcastlv.chat.bilibili.com:2244/sub'
    
    queueLock = threading.Lock()
    workQueue = queue.Queue(100)
    
    async def startup(self):
        async with AioWebSocket(self.remote) as aws:
            converse = aws.manipulator
            await converse.send(bytes.fromhex(self.data_raw))
            # tasks = [receDM(converse), sendHeartBeat(converse)]
            tasks = [asyncio.create_task(self.receDM(converse)), asyncio.create_task(self.sendHeartBeat(converse))]
            await asyncio.wait(tasks)
        
    hb='00 00 00 10 00 10 00 01  00 00 00 02 00 00 00 01'
    async def sendHeartBeat(self,websocket):
        while True:
            await asyncio.sleep(30)
            await websocket.send(bytes.fromhex(self.hb))
    async def receDM(self,websocket):
        while True:
            recv_text = await websocket.receive()

            if recv_text == None:
                recv_text = b'\x00\x00\x00\x1a\x00\x10\x00\x01\x00\x00\x00\x08\x00\x00\x00\x01{"code":0}'
                
            self.printDM(recv_text)
            
    # 将数据包传入：
    def printDM(self,data):
        # 获取数据包的长度，版本和操作类型
        packetLen = int(data[:4].hex(), 16)
        ver = int(data[6:8].hex(), 16)
        op = int(data[8:12].hex(), 16)

        # 有的时候可能会两个数据包连在一起发过来，所以利用前面的数据包长度判断，
        if (len(data) > packetLen):
            self.printDM(data[packetLen:])
            data = data[:packetLen]

        # 有时会发送过来 zlib 压缩的数据包，这个时候要去解压。
        if (ver == 2):
            data = zlib.decompress(data[16:])
            self.printDM(data)
            return
        
        # op 为5意味着这是通知消息，cmd 基本就那几个了。
        if (op == 5):
            try:
                jd = json.loads(data[16:].decode('utf-8', errors='ignore'))
                if (jd['cmd'] == 'DANMU_MSG'):
                    # print('[弹幕] ', jd['info'][2][0],jd['info'][2][1], ': ', jd['info'][1])
                    self.queueLock.acquire()
                    if self.workQueue.full():
                        self.workQueue.get()
                    self.workQueue.put(jd['info'][1])
                    self.queueLock.release()
                    
                elif (jd['cmd'] == 'SEND_GIFT'):
                    print(jd['data'])
                    print('[礼物]', jd['data']['uname'], ' ', jd['data']['action'], ' ', jd['data']['num'], 'x',
                        jd['data']['giftName'])
            except Exception as e:
                pass
            
    def __init__(self, threadID, name,roomid):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.roomid=roomid
        self.data_raw = '000000{headerLen}0010000100000007000000017b22726f6f6d6964223a{roomid}7d'
        self.data_raw = self.data_raw.format(headerLen=hex(27 + len(roomid))[2:],
                                roomid=''.join(map(lambda x: hex(ord(x))[2:], list(roomid))))
        
    def run(self):
        try:
            # loop = asyncio.get_event_loop()
            loop =  asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.startup())
        except Exception as e:
            print(e)
            print('退出')
        pass

# def process_data(threadName, q):
#     while not False:
#         queueLock.acquire()
#         if not workQueue.empty():
#             data = q.get()
#             queueLock.release()
#             print ("%s processing %s" % (threadName, data))
#         else:
#             queueLock.release()
#         time.sleep(1)

class DrDanmu:
    def __init__(self,roomid="24990544"):
        self.thread1 = dmThread(1, "Thread-1",roomid)
        self.thread1.start()
        
    def isEmpty(self):
        self.thread1.queueLock.acquire()
        re = self.thread1.workQueue.empty()
        self.thread1.queueLock.release()
        return re
    def getdm(self):
        self.thread1.queueLock.acquire()
        if not self.thread1.workQueue.empty():
            data =  self.thread1.workQueue.get()
            self.thread1.queueLock.release()
            return data
        else:
            self.thread1.queueLock.release()

# dm=DrDanmu("5639879")
# while True:
#     if(not dm.isEmpty()):
#         dminfo=dm.getdm()
#         if(dminfo=="创造生命"):
#             print("random")
#         print(dminfo)
#     time.sleep(1)
