# -*- coding: utf-8 -*-
"""Network Receiver.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1xE3fK9X5vU8m9SUVLn4u5x4hXNF27vs0
"""

#Must output 2001:400:a100:3090:f816:3eff:fe99:6f74
!curl icanhazip.com

import socket

conn.close()

!fuser -k 9060/tcp

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("localhost", 9060))

server.listen()
print("Server running and listening")
while True:
  client, addr = server.accept()
  msg = client.recv(11534336).decode()
  tmp = msg.split()
  seq = tmp[0]
  if len(tmp) != 2:
    print("UNEXPECTED:")
    print(msg)
  #print(msg)

  client.send(seq.encode())

seq, txt = "165678 asdlkjashdflkjashdlfkjhasldkjfhalsdjfhlakjsdf".split()
print(int(seq)+2)

server.close()

print(socket.getaddrinfo(socket.gethostname(), 8010, socket.AF_INET6)[0][4][0])



"""# ANOTHER IMPLEMENTATION"""

import socket

host = ''        # Symbolic name meaning all available interfaces
port = 9005     # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
s.bind((host, port))

print(host , port)
s.listen(1)
print("HERE")
conn, addr = s.accept()
print('Connected by', addr)
while True:

    try:
        data = conn.recv(1024)

        if not data: break

        print ("Client Says: "+data)
        conn.sendall("Server Says:hi")

    except socket.error:
        print("Error Occured.")
        break

conn.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("localhost", 9060))

server.listen()
print("Server running and listening")
acks = [False for i in range(int(1e6))]
cnt = 0
while True:
  client, addr = server.accept()
  msg = client.recv(11534336).decode()
  tmp = msg.split()

  seq = tmp[0]
  seq = int(seq)

  if seq == cnt:
    #The sequence number of the packet received matches the expected sequence number
    client.send(str(seq).encode())
    acks[cnt] = True
    cnt += 1

  elif seq < cnt:
    #The ACK was lost. Send the ACK again.
    client.send(str(seq).encode())

  else:
    #Packet was lost. Send the ACK for the last seq received
    acks[seq] = True #Add the packet to the received list
    client.send(str(cnt-1).encode())

  while acks[cnt]: #To dismiss the packages received
    cnt += 1


