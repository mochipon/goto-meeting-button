# Go To Meeting Button

This tiny script can turn IoT buttons into useful buttons for starting/ending a meeting.

## Introduction

Since the outbreak of the COVID-19 pandemic, working from home has become the norm for millions of workers. Since our home suddenly became our place of work, many problems have arisen. Here I would like to focus on two problems related to remote conferencing in particular. Those problems happen because we often work in a room that is not our living room, so the rest of the family doesn't know what we are doing.

First, our family may start cleaning/washing unexpectedly without any bad intentions, which may cause a loud noise and create a big problem for the meeting. Secondly, the quality of the video and audio of the meeting can be affected by family watching the video without any bad intentions.

This program allows you to create buttons to press when you want to start and end a meeting. When the Cisco router detects that this button has been pressed, it will first use the smart speaker (Google Home) in the house to notify the family by voice that the meeting has started or ended. In addition to that, during a remote conferencing, the QoS settings of the router wii be changed to limit the bandwidth of non-business related applications.

## Requirement

- Cisco IOS XE Amsterdam 17.3.1 and later releases.
- IoT Button (I personally use [Seeed ReButton](https://seeedjp.github.io/ReButton/), but anything that can be connected to the network is okay).

## Installation

### 1. Enable the Guest Shell
Please refer to the document - [Programmability Configuration Guide, Cisco IOS XE Amsterdam 17.3.x
](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/prog/configuration/173/b_173_programmability_cg/guest_shell.html).

### 2. Setup an environment on the Guest Shell
```shell
[guestshell@guestshell ~]$ sudo yum install -y git
[guestshell@guestshell ~]$ sudo pip3 install virtualenv
[guestshell@guestshell ~]$ git clone https://github.com/mochipon/goto-meeting-button
[guestshell@guestshell ~]$ cd goto-meeting-button
[guestshell@guestshell ~]$ virtualenv --system-site-packages v # Do not forget '--system-site-packages' as we want to use the 'cli' module in our virtual env.
[guestshell@guestshell ~]$ . v/bin/activate
[guestshell@guestshell ~]$ pip install -r requirements.txt
```

Please place `ON.mp3` to be played at the beginning of the meeting and `OFF.mp3` to be played at the end of the meeting in `htdoc`.

### 3. Setup QoS configs 
```shell
router#conf t
Enter configuration commands, one per line.  End with CNTL/Z.
router(config)#class-map match-any scavenger-class
router(config-cmap)#match protocol attribute business-relevance business-irrelevant
router(config-cmap)#policy-map scavenger-police
router(config-pmap)#class scavenger-class
router(config-pmap-c)#police cir 8000 bc 1500 ! Please change these numbers, 8000 and 1500, to meet your goal.
router(config-pmap-c-police)#conform-action transmit
router(config-pmap-c-police)#exceed-action drop
```

### 4. Setup an EEM applet to trigger the python script

Please note that the IoT button's MAC address is `00:00:5e:00:53:00` in this example. Please update the parameters to match your environment.

```shell
router#debug ip dhcp server events
router#conf t
Enter configuration commands, one per line.  End with CNTL/Z.
router(config)#event manager applet qos-button
router(config-applet)#event syslog pattern "DHCPD: htype 1 chaddr 0000\.5e00\.5300"
router(config-applet)#action 100 syslog msg "QoS Button is Pushed!"
router(config-applet)#action 150 cli command "enable"
router(config-applet)#action 200 cli command "guestshell run /home/guestshell/goto-meeting-button/v/bin/python /home/guestshell/goto-meeting-button/main.py --chromecastip 192.168.101.1 --interface Gi0/0/1 --policymap scavenger-police"
```
