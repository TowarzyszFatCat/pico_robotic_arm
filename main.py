import time
import utime
import network
import socket
from machine import Pin, PWM

from pass_data import *

min_duty = 1350
max_duty = 8200

add_remove = 137


servo1 = PWM(Pin(0))
servo1.freq(50)

servo2 = PWM(Pin(1))
servo2.freq(50)

servo3 = PWM(Pin(2))
servo3.freq(50)


act1 = 1350
servo1.duty_u16(act1)

act2 = 4090
servo2.duty_u16(act2)

act3 = 4220
servo3.duty_u16(act3)



led = Pin(15, Pin.OUT)
led.value(0)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)    # From file pass_data.py

page = open("index.html", "r")
html = page.read()
page.close()

# Wait for connect or fail
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)
    
# Handle connection error
if wlan.status() != 3:
    raise RuntimeError('network connection failed')
    led.value(0)

else:
    print('Connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )
    led.value(1)
    
    
# Open socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)
print('listening on', addr)


# Listen for connections, serve client
while True:
    try:
        print(act1, act2, act3)
        cl, addr = s.accept()
        print('client connected from', addr)
        request = cl.recv(1024)
        print("request:")
        print(request)
        request = str(request)
        
        plus1 = request.find('servo1=plus1')
        minus1 = request.find('servo1=minus1')
        
        plus2 = request.find('servo2=plus2')
        minus2 = request.find('servo2=minus2')
        
        plus3 = request.find('servo3=plus3')
        minus3 = request.find('servo3=minus3')
    
        
        #4775 - 90degrees
        
        if plus1 == 8:
            act1 += add_remove
            if act1 >= max_duty:
                act1 = max_duty
            servo1.duty_u16(act1)
        if minus1 == 8:
            act1 -= add_remove
            if act1 <= min_duty:
                act1 = min_duty
            servo1.duty_u16(act1)
            
        if plus2 == 8:
            act2 += add_remove
            if act2 >= max_duty:
                act2 = max_duty
            servo2.duty_u16(act2)
        if minus2 == 8:
            act2 -= add_remove
            if act2 <= min_duty:
                act2 = min_duty
            servo2.duty_u16(act2)
        
        if plus3 == 8:
            act3 += add_remove
            if act3 >= max_duty:
                act3 = max_duty
            servo3.duty_u16(act3)
        if minus3 == 8:
            act3 -= add_remove
            if act3 <= min_duty:
                act3 = min_duty
            servo3.duty_u16(act3)
      
      
      
        actual_duty = str(act1) + " " + str(act2) + " " + str(act3)
        
        response = html % (act1, act2, act3)
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()
        
    except OSError as e:
        led.value(0)
        cl.close()
        print('connection closed')

