# TCP Congestion Control
## Prelude
We want to send packets through the Internet as fast as possible. If we had a direct connection from a `sender` to a `receiver`, then we could send data as fast as both computers/servers can handle. Just like moving data from RAM to hard disk, we would not face any problems.
The problem with sending data from a `sender` to a `receiver` which does not have a direct physical connection, is that there are several components in between this client-server pair. One of the most important problems is that packages can get lost, especially if the sending rate exceeds the buffer size of the routers. Hence, we should come up with algorithms that make the most out of the available bandwidth, and at the same time be able to adjust the sending rate and be equipped with congestion control, in case some packets get lost.
In this project, we are going to implement some of the well-known TCP congestion control algorithms. Of course, are we not going to implement the exact algorithms which are being used on the internet; we are going to implement the general idea behind these algorithms to observe their behaviors in different scenarios/simulations.

## Setup
These tests are implemented in the FABRIC testbed. FABRIC can provide us with virtual private servers (VPS) in different locations. We are using Python to implement these algorithms.
We will enable port forwarding between the sender and the receiver. This way, we can easily use the `socket` package in Python to send TCP packets from the sender to the receiver. This can be done by generating `silver` and `bastion` key-pairs, and using the `-F` option to link these two servers:
```
sudo ssh -F config -i silver -L port:localhost:port user@host
```
For testing the algorithms, especially for the case where the probability of congestion is zero, we need to specify the `timeout` variable. Otherwise, the `cwnd` can increase indefinitely. We should specify the `timeout` variable, otherwise, none of these algorithms make sense in the case of a congestion-free scenario.

## TCP Reno
TCP Reno is responsible for congestion control in the network which uses Additive Increase Multiplicative Decrease (AIMD). Overall, it has three phases described below:

* Slow Start: At first, it will use a small Congestion Window Size (`cwnd`): 1 Maximum Segment Size (`MSS`). It will increase the `cwnd` size exponentially, i.e. it doubles the size of `cwnd`each iteration. In implementation, this is done by incrementing the `cwnd` by `+1` for every `ACK` received.
* Additive Increase: After the `cwnd` size reaches the Slow Start Threshold (`ssthresh`), in other words, half of its value before congestion happened, it will switch to this mode. It will increase the size of the `cwnd` linearly -- basically, to avoid congestion, yet make use of the available bandwidth.
* Multiplicative Decrease: In the case of congestion, it will set the size of the `cwnd` to half its size before congestion happens and goes to the Additive Increase phase again.

The difference between TCP Tahoe and TCP Reno is in the third phase: TCP Tahoe will set the `cwnd` to 1 `MSS` in case of congestion.


### Congestion Probability = 0\%
As mentioned above, we need to set a `timeout` variable. This limits the size of `cwnd`. After running the simulation, we can plot the `cwnd` through time, and observe the behavior of TCP Reno:

![1](https://github.com/ShayanPey/TCP-Congestion-Control/assets/12760574/0a4472fb-6df3-44e9-8668-410ff71c34a3)

This is exactly what we expected to see. The red line indicates the `ssthresh`, and every time the size of `cwnd` gets large enough to cause a `timeout`, the value of the `cwnd` halves.

### Congestion Probability = 1\%
In this scenario and the next subsections, there are two factors that can cause congestion: 1) timeout, and 2) packet loss. This is the probability of {each packet getting lost. This is not realistic and will probably result in unrealistic behaviors too. In a more realistic scenario, the probability of a packet getting lost, is related to the rate at which the packets are getting sent. In the next section ``More Realistic Scenarios'' we will observe how these algorithms will behave in such cases.
The sender can understand that packet loss happened as it gets $3$ duplicate `ACKs`.

![2](https://github.com/ShayanPey/TCP-Congestion-Control/assets/12760574/c27921e0-9c77-46f3-85d9-1bb7b991f801)


We can observe that in this scenario, all of the congestion were caused by packet losses and not timeout.

### Congestion Probability = 5\%, 10\%, 50\%

<p float="left">
  <img src="https://github.com/ShayanPey/TCP-Congestion-Control/assets/12760574/ac342303-6074-4002-b1d5-196d26dc1929" width="250" />
  <img src="https://github.com/ShayanPey/TCP-Congestion-Control/assets/12760574/13f3e0c2-233b-40de-85a7-65840ebb33de" width="250" /> 
  <img src="https://github.com/ShayanPey/TCP-Congestion-Control/assets/12760574/b8324d66-1c97-443c-8e9d-bb8f11e66a11" width="250" /> 
</p>

This is not the behavior we expect from TCP Reno, and that is because we are setting the value of {each sequence getting lost. This is not realistic, hence the unrealistic results. We will explore Reno's behavior in a more realistic setting.

## TCP CUBIC
TCP CUBIC is similar to TCP Reno, but the difference is the way it recovers from congestion, meaning the AIMD part. Reno tries to increase the `cwnd` linearly, but the approach behind CUBIC is simple: The network has not changed dramatically at this time, hence, it will increase the `cwnd` more quickly at first, and when the size of `cwnd` is close to the value the congestion happened before, it will increase it more carefully to prevent congestion. Details:

*  Let $K$ be the point in time where `cwnd` will reach $W_{\max}$. $W_{\max}$ is the sending rate where congestion was detected. ($K$ is also tuneable.)
*  Increase $W$ as a function of the CUBE of the distance between $K$ and the current time.

This will also take into account that when the network has changed, and it could discover higher rates, it will discover it. {We will see this in the section where we discuss more realistic scenarios.

### Congestion Probability = 0\%
![4](https://github.com/ShayanPey/TCP-Congestion-Control/assets/12760574/f03bc074-dc99-46c4-82d1-18b4844c5c13)



We can observe that after the congestion, the `cwnd` will increase more quickly first, and then increases more carefully to avoid congestion.

### Congestion Probability = 1\%
![5](https://github.com/ShayanPey/TCP-Congestion-Control/assets/12760574/82021b3f-a1b3-43cc-9d5b-c6403d981225)

### Congestion Probability = 5\%, 10\%, 50\%

<p float="left">
  <img src="https://github.com/ShayanPey/TCP-Congestion-Control/assets/12760574/a768fbd6-8a33-490e-b5e4-901104d2628c" width="250" />
  <img src="https://github.com/ShayanPey/TCP-Congestion-Control/assets/12760574/4b2e8ea6-5632-4ad7-9bed-633255463047" width="250" /> 
  <img src="https://github.com/ShayanPey/TCP-Congestion-Control/assets/12760574/ffb7dbe7-e874-4a17-9c07-97dc1d05a1a4" width="250" /> 
</p>

Here, we cannot observe the cubic behavior of this congestion control algorithm, and that is because the scale is quite small. For instance, when there is a $50\%$ chance for each sequence to get lost, then the scale is too small for the cubic behavior to appear. Again, this is an unrealistic scenario.

## More Realistic Scenarios
In these scenarios, the probability of each segment is not set individually; instead, the probability of the whole batch of data (`cwnd`) is set to a number. In other words, the probability of the whole batch of data getting lost is a function of the size of `cwnd`.

Additionally, in this section, we will change some of the implementation details so it more represent the real-world implementation.
We will run a few tests on different sender-receiver pairs in different locations and different latency and Round Trip Time (RTT) to observe how much data it can transfer, and average the results. We will run these tests for different congestion probabilities on top of the existing timeout limitation.

\noindent In this section, we will compare the performance of different algorithms and the amount of data it transferred in a $45$ second period. Of course, another limitation we will face is the number of sockets and bandwidth limitation enforced by the servers' network and the `ssh tunnel`.

Note: The congestion probability (CP) mentioned below is a function of the `cwnd` and is not for individual segments. The probability mentioned below is the probability of a $10$MB batch getting lost. Hence, the probability of a $1$MB batch facing packet loss would be $\frac{1}{10}$ of the original CP.


### Reno in a Realistic Scenario
![7](https://github.com/ShayanPey/TCP-Congestion-Control/assets/12760574/6a12a144-b07f-41a4-ae2d-58ad8bba2fab)
Reno CP=0\%. Transferred=118 Megabytes.

![8](https://github.com/ShayanPey/TCP-Congestion-Control/assets/12760574/9be549d2-a3d8-4094-89dd-662eee73759b)
Reno CP=10\%. Transferred=116 Megabytes.

![9](https://github.com/ShayanPey/TCP-Congestion-Control/assets/12760574/c658ae02-dbd7-41b5-b26d-bea1fbfcd184)
Reno CP=100\%. Transferred=90 Megabytes.

### CUBIC in a Realistic Scenario

![11](https://github.com/ShayanPey/TCP-Congestion-Control/assets/12760574/bb9da6aa-083c-4585-8f9b-95f905d764cb)
CUBIC CP=0\%. Transferred=184 Megabytes.;

![10](https://github.com/ShayanPey/TCP-Congestion-Control/assets/12760574/27951199-a6d6-44ab-9526-bab0d4e2f8d2)
CUBIC CP=10\%. Transferred=162 Megabytes.

![13](https://github.com/ShayanPey/TCP-Congestion-Control/assets/12760574/21b15896-d994-4bdf-a1dc-3ed0145b1ce2)
CUBIC CP=100\%. Transferred=149 Megabytes.;


## BBR
I did not use the kernel's BBR nor did I use the GitHub page. Instead, I implemented the overall idea of BBR ground up.

Generally, BBR's congestion control is not based on packet losses; instead, it is based on RTT (Delay). Here is the overall idea behind BBR:

![14](https://github.com/ShayanPey/TCP-Congestion-Control/assets/12760574/fae42b7b-c1b7-46ac-b5ec-f5f77c192aed)
RTT and Delivery rate regarding the number of packets in flight.

As the number of packets in flight increases, at first, the RTT does not increase much. But since there is a limit to how much the link can transfer data, after a threshold, while the number of packets sent increases, the delivery rate stays the same. TCP CUBIC performs at the right-hand side of the graph shown above. BBR instead of words at the left side, just after the blue shade ends. The idea behind it is to have the minimum RTT while keeping the delivery rate to its maximum. It has three stages:


*  STARTUP: It is similar to the slow start in CUBIC and Reno, i.e. it will exponentially increase the packets in flight to figure out the delivery rate (it will well-pass the optimal RTT.)
*  DRAIN: In this stage, it will figure out the number of packets built up in the bottleneck queue, and drain out the packets in the queue to reach the optimal point (left part of the green shade.)
*  PROBE\_BW: During the probe bandwidth state, it will stay at the optimal point, and occasionally increase the packets in flight to explore whether or not the bottleneck bandwidth has increased. If yes, then it will adjust its operating point. If not, it will stay the same.
*  PROBE\_RTT: During the probe Round Trip Time state, it will check whether or not the minimum RTT has decreased, by reducing the packets in flight. If yes, then it will decrease the number of packets in flight.

![15](https://github.com/ShayanPey/TCP-Congestion-Control/assets/12760574/58103f7d-8392-4862-a3f5-a14981d44e04)
BBR CP=0\%. Transferred=212 Megabytes.

## Westwood Plus
In TCP Westwood+, the bandwidth is estimated by properly low-pass filtering the rate of ACKs. The rationale of this strategy is simple: in contrast with TCP Reno, which blindly halves the congestion window after three duplicate ACKs, TCP Westwood+ adaptively sets a slow start threshold and a congestion window that takes into account the bandwidth used at the time congestion is experienced.

![16](https://github.com/ShayanPey/TCP-Congestion-Control/assets/12760574/c8516a4c-7ea8-48b8-aa38-6526a8459b76)
Westwood+ CP=0\%. Transferred=125 Megabytes.

## Postlude
There are many findings and settings to mention with these tools and plethora of different scenarios which are not mentioned here.
With a pair of sender-receivers further away, the latency will naturally increase, and if we do not increase the timeout, we will have less throughput. But when adjusting the timeout due to latency, we should get the same result as before, but obviously, the RTT has increased.
