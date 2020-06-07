#
# sudo python3 LEDSqhere
# Author: Julian L. Nicklas
#


import time
import neopixel
import board
import libJulianLED
import PerformanceCounter
import gamepad
import RPi.GPIO as GPIO

Keypad_PINS = [7,11,13,15,29,31,33,35]

# LED strip configuration:
LED_COUNT_0    = 75 # Amount of LED pixels of Ring0 (outer Ring)
LED_COUNT_1    = 56 # 56 Amount of LED pixels of Ring1 (inner Ring)
LED_COUNT_2    = 65 # 65 Amount of LED pixels of Ring2 (middle Ring)

# the highest LED should be the first LED from the top in the data stream direction
TOP_LED_0      = 0 # highest LED of ring 0
TOP_LED_1      = 0 # highest LED of ring 1
TOP_LED_2      = 0 # highest LED of ring 2

LED_PIN        = board.D18      # GPIO pin connected to the pixels (18 uses PWM!)
 

if __name__ == '__main__':
    
    try:
        LED_count = [LED_COUNT_0, LED_COUNT_1, LED_COUNT_2]
        top_LED = [TOP_LED_0, TOP_LED_1, TOP_LED_2]
        
        strip = libJulianLED.JLEDStripe(LED_count, top_LED, LED_PIN, [50,0,0], [5,5,5])
        GP = gamepad.btGamePad()
        PerfCounter = PerformanceCounter.PerfCounter(correction = 0.002)
        
        tBTconnection = time.perf_counter()
        
        i = 0
        while not GP.tryBTconnect():
            strip.shine(position = i)
            strip.shine(factor = 0, position = i - 3)
            strip.lightUp()
            i += 1
            time.sleep(1)
        
        strip.setColor(color = [50,0,0])
        strip.changeProgram(2,1)
        
        while True:
            # update Axis input from controller
            if GP.updateAxis():
                # when update was successful -> BT controller is connected
                # turn automatic off, if automatic was turned on because of inactiveness
                if time.perf_counter() - tBTconnection > 6000:
                    strip.setAutomatic(0)
                    
                tBTconnection = time.perf_counter()
            else:
                # if BT controller wasn't connected for 2 min change to autmatic mode
                if time.perf_counter() - tBTconnection > 120:
                    strip.setAutomatic(1)
                
            # Frequency
            RightJSY = GP.getAxisStatus(5)
            if RightJSY > 133:
                strip.setSlower((RightJSY - 128) / 128)
            if RightJSY < 123:
                strip.setFaster((128 - RightJSY) / 128)
            # Brightness
            RightJSX = GP.getAxisStatus(2)
            if RightJSX > 133:
                strip.setMoreBright((RightJSX - 128) / 128)
            if RightJSX < 123:
                strip.setLessBright((128 - RightJSX) / 128)
                
            GPinput = GP.getKey()
            # for some Reason GP.getKey() returns None, when L2 or R2 was pressed
            if GPinput is not None:
                # ~ print("GamePad: A/K: " + str(GPinput[0]) +
                    # ~ " - Key: " + str(GPinput[1]) + 
                    # ~ " - Value: " + str(GPinput[2]))
                if (GPinput[0] >= 0):
                    # print(" ".join(["INFO - LEDSphere - Button pressed ", str(GPinput[1])]))
                                            
                    if (GPinput[0] == 305) and (GPinput[1] == 1):
                        strip.setColor(color = [200,0,0], color2 = [40,40,40])
                        strip.changeProgram(1) # change to circling dot
                    
                    if (GPinput[0] == 304) and (GPinput[1] == 1):
                        strip.changeProgram(2, 2) # change to colorful puls
                        
                    if (GPinput[0] == 308) and (GPinput[1] == 1):
                        strip.setColor(color = [100,0,0])
                        strip.changeProgram(2, 1) # change to red puls
                        
                    if (GPinput[0] == 307) and (GPinput[1] == 1):
                        strip.toggleInhibit() # toggle inhibit 
                        
                    if (GPinput[0] == 312) and (GPinput[1] == 1):
                        strip.setColor(color = [200,0,0])
                        strip.changeProgram(3) # change to red rain
                        
                    if (GPinput[0] == 315) and (GPinput[1] == 1):
                        strip.setAutomatic(0,1) # toggle automatic
                        
                    if (GPinput[0] == 310) and (GPinput[1] == 1):
                        strip.setColor(color = [50,200,50], color2 = [200,50,50])
                        strip.changeProgram(4) # change to Obduction
                    
                    
                    
            strip.nextStep()
            PerfCounter.setTimeStamp()
            
            time.sleep(0.002)

    except KeyboardInterrupt:
        strip.shine(factor = 0)
        strip.lightUp()
        GPIO.cleanup()
        
    # ~ except:
        # ~ strip.color = [0,0,0]
        # ~ strip.shine()
        # ~ GPIO.cleanup()
        # ~ print("error =/")
        
    finally:
        strip.shine(factor = 0)
        strip.lightUp()
        GPIO.cleanup()
