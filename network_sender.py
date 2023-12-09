# -*- coding: utf-8 -*-
"""Network Sender.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1J-waYFWMdprSiO6QGnz0c6CIKyp4qmWy
"""

#Must output 2001:400:a100:3000:f816:3eff:fe7f:c981
!curl icanhazip.com

import socket
import time
import random
import numpy as np
import sys
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure

clients = []

"""# Definitions"""

sendType = 0
def send(times = 1, msg="ThisIsADefaultMessage.ShayanIsWorking!"):
  #Send packets 'times' time. Continue from the seqNumber
  #It adds the thread to clients so later on the ACK would be received
  #It also records the time of sending the packet
  global addr, port, cwnd, ssth, timeout, seqNumber, clients, sendType
  sendType = 0
  for i in range(times):
    clients.append((socket.socket(socket.AF_INET, socket.SOCK_STREAM), time.time(), len(msg)))
    clients[-1][0].connect((addr, port)) #Connect the receiver
    clients[-1][0].send((str(seqNumber)+' '+msg).encode()) #Send with the seqNumber
    seqNumber += 1  #Increment the sequence number

def send2(times = 1, msg="A"):
  #Send packets 'times' time. Continue from the seqNumber
  #It adds the thread to clients so later on the ACK would be received
  #It also records the time of sending the packet
  global addr, port, cwnd, ssth, timeout, seqNumber, clients, sendType
  sendType = 1

  clients.append((socket.socket(socket.AF_INET, socket.SOCK_STREAM), time.time(), times))
  clients[-1][0].connect((addr, port)) #Connect the receiver
  clients[-1][0].send((str(seqNumber)+' '+msg*times).encode()) #Send with the seqNumber
  seqNumber += 1  #Increment the sequence number

def getack(index = 0):
  #Gets the ACK for the package index.
  #This also acts as the proxy i.e. if the ack gets lost
  global addr, port, cwnd, ssth, timeout, seqNumber, clients, sendType

  if index == 'empty' or index == 'delete' or index == 'flush':
    for i in range(len(clients)):
      clients[i][0].close()
    clients = []

  if len(clients) == 0:
    return 0

  if index == 'all' or index == -1:  #Get all ACKs and return the longest RTT
    index = len(clients)-1

  maxRTT = 0
  maxSeq = 0
  for i in range(index+1):
    tmp = clients[i][0].recv(1024).decode()
    clients[i][0].close()
    nowTime = time.time()-clients[i][1]
    maxRTT = max(maxRTT, nowTime)
    maxSeq = max(maxSeq, clients[i][2])

    if sendType == 0:
      rand = random.randrange(100)
      if rand < congProb: #Congestion Occured
        maxRTT = inf
    if sendType == 1:
      rand = random.random()
      if rand < congProb/100*(maxSeq/11534336):
        maxRTT = inf


  clients = clients[index+1:] #Delete the received sequences
  if maxRTT > timeout:
    maxRTT = inf
  return maxRTT

getack('flush')

#Round Trip Time
send()
print(getack())

"""# Reno Simple"""

addr = "localhost"  #Address
port = 9060         #Port for communication
cwnd = 1            #Congestion Window size
ssthresh = 50       #Slow Start Threshold
timeout = 1         #Timeout limit in seconds
linearConst = 3    #Linear Constant for AIMD
cubeConst = 10      #CUBIC Constant
congProb = 1        #Probability of congestion happening
inf = float('inf')  #Infinite constant

seqNumber = 0       #Starting sequence number is 0

getack('flush')

#TCP RENO

history = []

flag = 0  #To mark the last time linearly increased
justBeforeLoss = 0
for i in range(70):
  sys.stdout.write("\r Progress Done: " + str(int(i)))
  sys.stdout.flush()
  print("\r Progress Done: " + str(int(i)), 'cwnd:', cwnd, 'ssthresh:', ssthresh)
  history.append(cwnd)
  send(cwnd)
  tmp = getack('all')
  if tmp == inf:  #Congestion or timeout happened
    print("Congestion Happened")
    if ssthresh == int(justBeforeLoss):
      ssthresh = max(1, int(ssthresh/2))
      cwnd = ssthresh
      continue
    ssthresh = max(1, int(justBeforeLoss))
    cwnd = ssthresh   #TCP Reno
    continue

  if cwnd < ssthresh: #In the Slow Start Phase
    print("Slow start")
    justBeforeLoss = cwnd
    cwnd *= 2

  elif cwnd >= ssthresh:  #AIMD Phase
    print("AIMD")
    justBeforeLoss = cwnd
    cwnd += linearConst

figure(figsize=(14, 6), dpi=200)
plt.plot(range(len(history)), history)
plt.scatter(range(len(history)), history)
#plt.axhline(y=ssthresh, color='r', linestyle='-')
plt.xlabel("time", fontsize=18)
plt.ylabel("Congestion Window", fontsize=18)

"""# CUBIC Simple"""

#Settings for CUBIC. Working.
addr = "localhost"  #Address
port = 9060         #Port for communication
cwnd = 1            #Congestion Window size
ssthresh = 70       #Slow Start Threshold
timeout = 1         #Timeout limit in seconds
linearConst = 1    #LinCubicear Constant for AIMD
cubeConst = 0.05       #CUBIC Constant
congProb = 50        #Probability of congestion happening
inf = float('inf')  #Infinite constant

seqNumber = 0       #Starting sequence number is 0

getack('flush')

#TCP CUBIC. Working. Without packet losses.

history = []

flag = 0  #To mark the last time linearly increased
justBeforeLoss = 0
for i in range(70):
  #sys.stdout.write("\r Progress Done: " + str(int(i))+ " CWND: "+str(cwnd)+ " ssthresh: "+str(ssthresh))
  #sys.stdout.flush()
  ssthresh = 3
  print("\r Progress Done: " + str(int(i))+ " CWND: "+str(cwnd)+ " ssthresh: "+str(ssthresh))
  history.append(cwnd)
  send(cwnd)
  tmp = getack('all')
  if tmp == inf:  #Congestion or timeout happened
    print("Congestion Happened")
    if cwnd == int(justBeforeLoss/2):
      justBeforeLoss = int(justBeforeLoss/2)
      cwnd = max(1, int(cwnd/2))
      continue
    ssthresh = int(justBeforeLoss/2)
    cwnd = max(1, ssthresh)
    continue

  if i < 10: #In the Slow Start Phase
    print("Slow start phase")
    justBeforeLoss = cwnd
    cwnd *= 2

  #elif cwnd >= ssthresh:  #AIMD Phase
  else:
    print("Cubic Phase")
    justBeforeLoss = cwnd
    pred = int(int((ssthresh*2-cwnd)/linearConst)**3)
    pred = (ssthresh*2-cwnd)/2.6/cubeConst
    print("pred:", pred, "incement by:", cubeConst*pred)
    cwnd += int(max(1, cubeConst*pred))

print(history)

figure(figsize=(14, 6), dpi=200)
plt.plot(range(len(history)), history)
plt.scatter(range(len(history)), history)
#plt.axhline(y=ssthresh, color='r', linestyle='-')
plt.xlabel("time", fontsize=18)
plt.ylabel("Congestion Window", fontsize=18)

"""# REALISTIC

# Reno Realistic
"""

#Settings for RENO. REALISTIC.
addr = "localhost"  #Address
port = 9060         #Port for communication
cwnd = 1            #Congestion Window size
ssthresh = inf       #Slow Start Threshold
timeout = 0.33         #Timeout limit in seconds
linearConst = 70000    #LinCubicear Constant for AIMD
cubeConst = 0.1     #CUBIC Constant
congProb = 100        #Probability in Percentage of congestion happening
inf = float('inf')  #Infinite constant

seqNumber = 0       #Starting sequence number is 0

getack('flush')

#TCP RENO REALISTIC

history = []
sshistory = []

startinSS = ssthresh
congestNum = 0

startingTime = time.time()
bTrans = 0 #Bytes Transfered

flag = 0  #To mark the last time linearly increased
justBeforeLoss = 0
for i in range(200):
  print("\r Progress Done: " + str(int(i))+ " CWND: "+str(cwnd)+ " ssthresh: "+str(ssthresh)+ " Running time: "+str(time.time()-startingTime),  " Mega Bytes:", int(bTrans/1024/1024))
  #sys.stdout.flush()
  sshistory.append(ssthresh)
  if time.time()-startingTime > 45:
    break
  history.append(cwnd)
  send2(cwnd)
  tmp = getack('all')
  if tmp == inf:  #Congestion or timeout happened
    print(">>> Congestion Happened")
    congestNum += 1
    if ssthresh == int(justBeforeLoss/2):
      ssthresh = int(ssthresh/2)
      cwnd = ssthresh
      continue
    ssthresh = int(justBeforeLoss/2)
    cwnd = ssthresh   #TCP Reno
    continue

  bTrans += cwnd #Congestion did not happen. Add

  if cwnd < ssthresh: #In the Slow Start Phase
    justBeforeLoss = cwnd
    cwnd *= 2

  elif cwnd >= ssthresh:  #AIMD Phase
    justBeforeLoss = cwnd
    cwnd += linearConst

print("Bytes Transfered:", bTrans, " Kilo Bytes:", int(bTrans/1024), " Mega Bytes:", int(bTrans/1024/1024), " Congest Num:", congestNum)

#Remove startin ssthreshold from plot
tmp = 0
"""
for i in range(len(sshistory)):
  if sshistory[i] != startinSS:
    break
  tmp = i
tmp += 1
"""
figure(figsize=(14, 6), dpi=200)
plt.plot(range(len(history)), history, label="CWND")
plt.scatter(range(len(history)), history)
#plt.axhline(y=ssthresh, color='r', linestyle='-')
plt.scatter(range(len(sshistory[tmp:])), sshistory[tmp:], label="SSThreshold")
plt.xlabel("Iteration", fontsize=18)
plt.legend(loc="upper left")
plt.ylabel("Bytes", fontsize=18)

"""# CUBIC Realistic"""

#Settings for CUBIC. For packet drops.
addr = "localhost"  #Address
port = 9060         #Port for communication
cwnd = 1            #Congestion Window size
ssthresh = inf       #Slow Start Threshold
timeout = 0.33         #Timeout limit in seconds
linearConst = 50000    #LinCubicear Constant for AIMD
cubeConst = 0.1     #CUBIC Constant
congProb = 100        #Probability in Percentage of congestion happening
inf = float('inf')  #Infinite constant

seqNumber = 0       #Starting sequence number is 0

getack('flush')

#TCP CUBIC. Working. Handling packet losses

history = []
sshistory = []

startinSS = ssthresh

flag = 0  #To mark the last time linearly increased
justBeforeLoss = 0

startingTime = time.time()
bTrans = 0 #Bytes Transfered

for i in range(200):
  #sys.stdout.write("\r Progress Done: " + str(int(i))+ " CWND: "+str(cwnd)+ " ssthresh: "+str(ssthresh))
  #sys.stdout.flush()
  print("\r Progress Done: " + str(int(i))+ " CWND: "+str(cwnd)+ " ssthresh: "+str(ssthresh)+ " Running time: "+str(time.time()-startingTime),  " Mega Bytes:", int(bTrans/1024/1024))
  if time.time()-startingTime > 45:
    break
  history.append(cwnd)
  sshistory.append(ssthresh)
  send2(cwnd)

  tmp = getack('all')
  if tmp == inf:  #Congestion or timeout happened
    print(">>> Congestion Happened")
    if ssthresh == int(justBeforeLoss/2):
      ssthresh = int(ssthresh/2)
      cwnd = ssthresh
      continue
    ssthresh = int(justBeforeLoss/2)
    cwnd = ssthresh   #TCP Reno
    continue

  bTrans += cwnd #Congestion did not happen. Add
  if cwnd < ssthresh: #In the Slow Start Phase
    print("Slow start phase")
    justBeforeLoss = cwnd
    cwnd *= 2

  #elif cwnd >= ssthresh:  #AIMD Phase
  else:
    print("Cubic Phase")
    justBeforeLoss = cwnd
    pred = int(int((ssthresh*2-cwnd)/linearConst)**3)
    pred = int(abs(ssthresh*2-cwnd)**1)/2/cubeConst
    print("pred:", pred, "incement by:", cubeConst*pred)
    cwnd += int(max(1, cubeConst*pred))

print("Bytes Transfered:", bTrans, " Kilo Bytes:", int(bTrans/1024), " Mega Bytes:", int(bTrans/1024/1024))

#Remove startin ssthreshold from plot
tmp = 0
"""
for i in range(len(sshistory)):
  if sshistory[i] != startinSS:
    break
  tmp = i
tmp += 1
"""
figure(figsize=(14, 6), dpi=200)
plt.plot(range(len(history)), history, label="CWND")
plt.scatter(range(len(history)), history)
#plt.axhline(y=ssthresh, color='r', linestyle='-')
plt.scatter(range(len(sshistory[tmp:])), sshistory[tmp:], label="SSThreshold")
plt.xlabel("Iteration", fontsize=18)
plt.legend(loc="upper left")
plt.ylabel("Bytes", fontsize=18)

"""# BBR Realistic"""

#Settings for BBR. For packet drops.
addr = "localhost"  #Address
port = 9060         #Port for communication
cwnd = 1            #Congestion Window size
ssthresh = inf       #Slow Start Threshold
timeout = 0.34         #Timeout limit in seconds
linearConst = 100    #LinCubicear Constant for AIMD
cubeConst = 0.1     #CUBIC Constant
congProb = 0        #Probability in Percentage of congestion happening
disRate = 10        #Discovery rate for BBR
disJump = 0.4       #10% for discovery
inf = float('inf')  #Infinite constant

seqNumber = 0       #Starting sequence number is 0

getack('flush')

#TCP BBR

history = []
sshistory = []

sents = []
disCnt = 0  #Discovery Counter

startinSS = ssthresh

flag = False  #Startup phase ended?
disingLower = False   #Is it discovering lower?
disingHigher = False  #Is it discovering higher?
justBeforeLoss = 0

startingTime = time.time()
bTrans = 0 #Bytes Transfered

for i in range(200):
  #sys.stdout.write("\r Progress Done: " + str(int(i))+ " CWND: "+str(cwnd)+ " ssthresh: "+str(ssthresh))
  #sys.stdout.flush()
  print("\r\n Progress Done: " + str(int(i))+ " CWND: "+str(cwnd)+ "justBeforeLoss: "+str(justBeforeLoss)+ " ssthresh: "+str(ssthresh)+ " disCount:"+ str(disCnt)+" Running time: "+str(time.time()-startingTime),  " Mega Bytes:", int(bTrans/1024/1024))
  if time.time()-startingTime > 45:
    break
  history.append(cwnd)
  sshistory.append(ssthresh)
  send2(cwnd)

  tmp = getack('all')
  if tmp == inf:  #Congestion or timeout happened
    print(">>> Congestion Happened")
    flag = True
    if disingHigher:
      print("#1")
      disingHigher = False
      sents.append(cwnd/(1+disJump))
    else:
      print("#2")
      sents.append(cwnd/2)

    if ssthresh == int(justBeforeLoss/2):
      print("#3")
      ssthresh = int(ssthresh/2)
      cwnd = ssthresh
      continue
    print("#4")
    ssthresh = int(justBeforeLoss/2)
    #cwnd = ssthresh   #TCP
    continue

  bTrans += cwnd #Congestion did not happen. Add
  if not disingLower:
    sents.append(cwnd)  #Packets sent and delivered
  if (i < 24) and (not flag): #In the Slow Start Phase
    print("Slow start phase")
    justBeforeLoss = cwnd
    cwnd = int(cwnd*2)

  #elif cwnd >= ssthresh:  #AIMD Phase
  else:
    print("BBR Phase")
    flag = True
    if disCnt >= 0:
      disCnt += 1
    if disCnt < 0:
      disCnt -= 1

    if (disCnt > 0) and (disCnt >= disRate):
      #Discovering higher throughput
      print("Discovering higher")
      disingHigher = True
      disCnt = -1
      cwnd = int(cwnd*(1+disJump))
      continue

    if (disCnt < 0) and (abs(disCnt) >= disRate/2):
      #Discovering the RTT
      print("Discovering RTT")
      disingLower = True
      disCnt = 0
      cwnd = int(cwnd*(1-disJump))
      continue

    if disingLower: #It was discovering lower rates for RRT
      disingLower = False
      cwnd = int(cwnd*1/(1-disJump))
      continue

    justBeforeLoss = cwnd
    cwnd = int(np.mean(sents[max(0, len(sents)-4):]))

print("Bytes Transfered:", bTrans, " Kilo Bytes:", int(bTrans/1024), " Mega Bytes:", int(bTrans/1024/1024))

#Remove startin ssthreshold from plot
tmp = 0
"""
for i in range(len(sshistory)):
  if sshistory[i] != startinSS:
    break
  tmp = i
tmp += 1
"""
figure(figsize=(14, 6), dpi=200)
plt.plot(range(len(history)), history, label="CWND")
plt.scatter(range(len(history)), history)
#plt.axhline(y=ssthresh, color='r', linestyle='-')
plt.scatter(range(len(sshistory[tmp:])), sshistory[tmp:], label="SSThreshold")
plt.xlabel("Iteration", fontsize=18)
plt.legend(loc="upper left")
plt.ylabel("Bytes", fontsize=18)

"""# Westwood+ Realistic"""

#Settings for Westwood Plus. REALISTIC.
addr = "localhost"  #Address
port = 9060         #Port for communication
cwnd = 1            #Congestion Window size
ssthresh = inf       #Slow Start Threshold
timeout = 0.33         #Timeout limit in seconds
linearConst = 30000    #LinCubicear Constant for AIMD
cubeConst = 0.1     #CUBIC Constant
congProb = 0        #Probability in Percentage of congestion happening
inf = float('inf')  #Infinite constant

seqNumber = 0       #Starting sequence number is 0

getack('flush')

#TCP Westwood+ REALISTIC

history = []
sshistory = []

startinSS = ssthresh

sents = [] #For estimating the badwidth after congestion occured

startingTime = time.time()
bTrans = 0 #Bytes Transfered

flag = 0  #To mark the last time linearly increased
justBeforeLoss = 0
for i in range(200):
  print("\r Progress Done: " + str(int(i))+ " CWND: "+str(cwnd)+ " ssthresh: "+str(ssthresh)+ " Running time: "+str(time.time()-startingTime),  " Mega Bytes:", int(bTrans/1024/1024))
  #sys.stdout.flush()
  sshistory.append(ssthresh)
  if time.time()-startingTime > 45:
    break
  history.append(cwnd)
  send2(cwnd)
  tmp = getack('all')
  if tmp == inf:  #Congestion or timeout happened
    print(">>> Congestion Happened")
    justBeforeLoss = int(np.mean(sents[max(0, len(sents)-6):]))
    if ssthresh > cwnd/(1.1) and ssthresh != inf:
      print("Continious")
      ssthresh = int(justBeforeLoss/1.25)
      cwnd = ssthresh
      continue
    print("Not continious")
    ssthresh = int(justBeforeLoss)
    cwnd = ssthresh   #TCP Reno
    continue

  bTrans += cwnd #Congestion did not happen. Add
  sents.append(cwnd)

  if cwnd < ssthresh: #In the Slow Start Phase
    justBeforeLoss = cwnd
    cwnd *= 2

  elif cwnd >= ssthresh:  #AIMD Phase
    justBeforeLoss = cwnd
    cwnd += linearConst

print("Bytes Transfered:", bTrans, " Kilo Bytes:", int(bTrans/1024), " Mega Bytes:", int(bTrans/1024/1024))

#Remove startin ssthreshold from plot
tmp = 0
"""
for i in range(len(sshistory)):
  if sshistory[i] != startinSS:
    break
  tmp = i
tmp += 1
"""
figure(figsize=(14, 6), dpi=200)
plt.plot(range(len(history)), history, label="CWND")
plt.scatter(range(len(history)), history)
#plt.axhline(y=ssthresh, color='r', linestyle='-')
plt.scatter(range(len(sshistory[tmp:])), sshistory[tmp:], label="SSThreshold")
plt.xlabel("time", fontsize=18)
plt.legend(loc="upper left")
plt.ylabel("Congestion Window", fontsize=18)



#Settings for RTT.
addr = "localhost"  #Address
port = 9060         #Port for communication
cwnd = 1            #Congestion Window size
ssthresh = 70       #Slow Start Threshold
timeout = 100         #Timeout limit in seconds
linearConst = 10    #LinCubicear Constant for AIMD
cubeConst = 0.1     #CUBIC Constant
congProb = 0        #Probability in Percentage of congestion happening
inf = float('inf')  #Infinite constant

seqNumber = 0       #Starting sequence number is 0

#RTT based on packet in flight
x, y = [], []
Range = []
for i in range(0, 100, +10):
  Range.append(i)
for i in range(100, 140, +20):
  Range.append(i)
for i in range(140, 400, +20):
  Range.append(i)

Range = []
for i in range(0, 1000, +50):
  Range.append(i)

for i in range(0, 10485760, +104857):
  x.append(i)
  send2(i)
  y.append(getack('all'))
  sys.stdout.write("\r Progress Done: " +str(i)+ ' RTT:' +str(y[-1]))
  sys.stdout.flush()

x[18]

#RTT
figure(figsize=(14, 6), dpi=200)
plt.plot(x, y, label="CWND")
#plt.scatter(range(len(history)), history)
#plt.axhline(y=ssthresh, color='r', linestyle='-')
#plt.scatter(range(len(sshistory[tmp:])), sshistory[tmp:], label="SSThreshold")
plt.xlabel("Packets in flight", fontsize=18)
#plt.legend(loc="upper left")
plt.ylabel("RTT", fontsize=18)

#RTT
figure(figsize=(14, 6), dpi=200)
plt.plot(x, y, label="CWND")
#plt.scatter(range(len(history)), history)
#plt.axhline(y=ssthresh, color='r', linestyle='-')
#plt.scatter(range(len(sshistory[tmp:])), sshistory[tmp:], label="SSThreshold")
plt.xlabel("Packets in flight", fontsize=18)
#plt.legend(loc="upper left")
plt.ylabel("RTT", fontsize=18)

"""**BASE**"""

#Time
start_time = time.time()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 9060))
client.send("1 testToFindTime".encode())
print(client.recv(1024).decode())

print((time.time() - start_time))

