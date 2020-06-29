sudo find / -name pysmu

/home/mackst/.local/bin/pysmu
/home/mackst/.local/lib/python3.6/site-packages/pysmu-1.0.2-py3.6-linux-x86_64.egg/EGG-INFO/scripts/pysmu
/home/mackst/.local/lib/python3.6/site-packages/pysmu-1.0.2-py3.6-linux-x86_64.egg/pysmu


Bei Python 3 findet der Interpreter pysmu unter ... 

python3
>>> import pysmu
>>> print(pysmu.__file__)
/usr/local/lib/python3.6/dist-packages/pysmu-1.0.2-py3.6-linux-x86_64.egg/pysmu/__init__.py


6.6.20

Pythonbeispiele aus wiki.analog.com/university/tools/python-tutorial/table-of-contents

Direct control over ADALM1000 functionality can be accomplished using the implemented control
transfers, a synchronous and slow communication endpoint accessible regardless of the
configuration of the device.
Note that the higher level functions libpysmu implements on top of LIBSMU make use of many of
the control transfers to configure device state during normal operation. As such, using these
low level control transfers while streaming data may not produce the expected results.

The ALM1000 implements many control transfers, including the following:

    0x17 - read a number of bytes from the ADM1177 hot-swap controller
    0x50 - Set a GPIO pin low
    0x51 - Set a GPIO pin high
    0x91 - Get a GPIO input pin value
    0x53 - Set device Mode
    0x59 - Set potentiometer state

M1000 microcontroller pin mappings are described below.
IO Name	Net Name	Net Description	Pin ID
——-	——--	—————	——
PA0	PIO0	user DIO 0-220Ω	0
PA1	PIO1	user DIO 1-220Ω	1
PA2	PIO2	user DIO 2-220Ω	2
PA3	PIO3	user DIO 3-220Ω	3
PA4	PIO0	user DIO 0-470Ω	4
PA5	PIO1	user DIO 1-470Ω	5
PA6	PIO2	user DIO 2-470Ω	6
PA7	PIO3	user DIO 3-470Ω	7
PB0	UA11-IN0	50Ω from ChA to 2v5	32
PB1	UA11-IN1	50Ω from ChA to GND	33
PB2	UA11-IN2	ChA close voltage sense loop	34
PB3	UA11-IN3	ChA connect output	35
PB5	UB11-IN0	50Ω from ChB to 2v5 	37
PB6	UB11-IN1	50Ω from ChB to GND	38
PB7	UB11-IN2	ChB close voltage sense loop	39
PB8	UB11-IN3	ChB connect output	40
PB17	PWR_ENABLE	turn on power for analog components	49
PB19	SWMODE-A	ChA switch SVMI - SIMV	51
PB20	SWMODE-B	ChB switch SVMI - SIMV	52
Examples:

#
import libpysmu
import pysmu.py

devx = Smu()
DevID = devx.serials[0] # device ID for 1st M1000 in list

# set PIO1 high
devx.ctrl_transfer(DevID, 0x40, 0x51, 1, 0, 0, 0, 100)

# set PIO1 low
devx.ctrl_transfer(DevID, 0x40, 0x50, 1, 0, 0, 0, 100)

# get state of PIO0
print devx.ctrl_transfer(DevID, 0xc0, 0x91, 0, 0, 0, 1, 100)

# get state of PIO1
print devx.ctrl_transfer(DevID, 0xc0, 0x91, 1, 0, 0, 1, 100)

# set CHA 2.5 V switch to open
devx.ctrl_transfer(DevID, 0x40, 0x51, 32, 0, 0, 0, 100)

# set CHA GND switch to open
devx.ctrl_transfer(DevID, 0x40, 0x51, 33, 0, 0, 0, 100)

# set CHB 2.5 V switch to open
devx.ctrl_transfer(DevID, 0x40, 0x51, 37, 0, 0, 0, 100)

# set CHB GND switch to open
devx.ctrl_transfer(DevID, 0x40, 0x51, 38, 0, 0, 0, 100)

# open CHA voltage sense loop
devx.ctrl_transfer(DevID, 0x40, 0x51, 34, 0, 0, 0, 100)

# open CHB voltage sense loop
devx.ctrl_transfer(DevID, 0x40, 0x51, 39, 0, 0, 0, 100) 