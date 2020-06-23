#
# Author: Julian L. Nicklas
#

import time
import neopixel
import board
import random

ORDER = neopixel.GRB # Red Green Blue in reality

class JLEDStripe:    
    def __init__(self, LED_count, top_LED, LED_pin, color, color2):
        total_LED_count = LED_count[0] + LED_count[1] + LED_count[2]
        self._strip = neopixel.NeoPixel(LED_pin, total_LED_count, auto_write = False)
        
        self._TOP_LED = top_LED
        self._LED_COUNT = LED_count
        
        self._color = color
        self._color2 = color2
        self._program = 0
        self._inhibit = False

        self._automatic = False # False = changes between programs only when commanded, True = changes program every 2 min
        self._tAutomatic = 0
        
        self._freq = 100
        self._tSlower = 0
        self._tFaster = 0
        
        self._brightness = 50
        self._tMoreBright = 0
        self._tLessBright = 0
        
        # Circling Dot
        self._tCiDo = 0
        self._iCiDo = 8
        
        # Pulsating
        self._tPuls = 0
        self._iPuls = 0
        self._phasePuls = 1
        self._modePuls = 1
        
        # Rain
        self._tRain = 0
        self._iRain = 0
        self._phaseRain = 0
        
        # Obduction
        self._tObduct = 0
        self._iObduct = 0
        self._phaseObduct = 1

    
    def nextStep(self):
        if not self._inhibit:
            if (self._automatic) and (time.perf_counter() - self._tAutomatic > 120):
                self._tAutomatic = time.perf_counter()
                # time for an automatic program change
                if self._program == 1:
                    self.setColor(color = [100,0,0])
                    self.changeProgram(2, 1) # change to red puls
                elif self._program == 2:
                    self.setColor(color = [200,0,0])
                    self.changeProgram(3) # change to red rain
                else:
                    self.setColor(color = [200,0,0], color2 = [40,40,40])
                    self.changeProgram(1) # change to circling dot
            
            # programs
            if self._program == 1:
                self._circlingDot()
            
            if self._program == 2:
                self._pulsating()
                
            if self._program == 3:
                self._rain()
            
            if self._program == 4:
                self._obduction()
            
            self._strip.show()
            
            
    def lightUp(self):
        self._strip.show()
        
        
    def changeProgram(self, number, mode = 1):
        # 0 - nothing
        # 1 - Circling Dot
        # 2 - Puls ~~~ modes: 1 - breathing | 2 - color-color shift
        # 3 - Rain
        # 4 - Obduction
        
        self._resetPrograms()
        
        if self._program != number:
            self.setFreq(100)
        
        self._program = number
        
        if number == 1:
            print("Circling Dot started *whoop*whoop*")
        
        if number == 2:
            self._modePuls = mode
            self._phasePuls = 1
            self._iPuls = 0
            if mode == 2:
                self._color = [0,0,0]
                self._color2 = [0,100,0]
            print("Pulsating Light - Searching Connection?")
            
        if number == 3:
            print("Rain from the Top to the Bottom")
            
        if number == 4:
            print("Obduction - the aliens are taking you with them")
    
    
    def setFreq(self, newFreq):
        if newFreq > 5000:
            self._freq = 5000
            print("Max Freq reached")
        elif newFreq < 2:
            self._freq = 2
            print("Minimum Freq reached")
        else:
            self._freq = newFreq
            # ~ print("change in Freq")
            
            
    def getFreq(self):
        return self._freq
        
        
    def setSlower(self, factor):
        # input: factor = float between 0 and 1
        #        0 doesnt slow down, 1 slows down a lot
        if (time.perf_counter() - self._tSlower) > 0.1:
            if factor > 1:
                factor = 1
            if factor < 0:
                factor = 0
        #    print("INFO - JulianLED - setSlower")
            self.setFreq((1-factor*0.1)*self.getFreq())
            self._tSlower = time.perf_counter()
    
    
    def setFaster(self, factor):
        # input: factor = float between 0 and 1
        #        0 doesnt speed up, 1 speeds up a lot
        if (time.perf_counter() - self._tFaster) > 0.1:
            if factor > 1:
                factor = 1
            if factor < 0:
                factor = 0
         #   newFreq = (1 + 0.5*factor)*self.getFreq()
            self.setFreq((1 + 0.1*factor)*self.getFreq())
        #   print(" ".join(["INFO - JulianLED - setFaster ", str(newFreq), ", factor:" , str(factor)]))
            
            self._tFaster = time.perf_counter()


    def setMoreBright(self, factor):
        # input: factor = float between 0 and 1
        #        0 doesnt change brightness, 1 makes it brighter a lot
        if (time.perf_counter() - self._tMoreBright) > 0.2:
            if factor > 1:
                factor = 1
            if factor < 0:
                factor = 0
            
            self._brightness = self._brightness + 10*factor
            
            if self._brightness > 100:
                print("Max Brightness reached")
                self._brightness = 100
                
        #   print(" ".join(["INFO - JulianLED - setFaster ", str(newFreq), ", factor:" , str(factor)]))
            self._tMoreBright = time.perf_counter()
            
    def setLessBright(self, factor):
        # input: factor = float between 0 and 1
        #        0 doesnt change brightness, 1 lowers the brightness the most
        if (time.perf_counter() - self._tLessBright) > 0.2:
            if factor > 1:
                factor = 1
            if factor < 0:
                factor = 0
            
            self._brightness = self._brightness - 10*factor
            
            if self._brightness < 20:
                print("Min Brightness reached")
                self._brightness = 20
                
        #   print(" ".join(["INFO - JulianLED - setFaster ", str(newFreq), ", factor:" , str(factor)]))
            self._tLessBright = time.perf_counter()
    
    def getBrightness(self):
        return self._brightness
    
    def setColor(self, color = None, color2 = None):
        if color is not None:
            self._color = color
        if color2 is not None:
            self._color2 = color2
    
    
    def toggleInhibit(self):
    # turn all LEDs off and pause
        if self._inhibit:
            print("INFO - JulianLED - setInhibit - _inhibit = False")
            self._inhibit = False
        else:
            print("INFO - JulianLED - setInhibit - _inhibit = True")
            self._inhibit = True
            self.shine(factor = 0, factor2 = 0)
            self._strip.show()
        
    def setAutomatic(self, automatic, toggle = 0):
        if toggle:
            self._automatic = not self._automatic

        else:
            self._automatic = automatic
            
        print(" ".join(["INFO - JulianLED - setAutomatic - _automatic = ", str(self._automatic)]))
    
    # ~ ~ ~ ~ ~ ~ progams ~ ~ ~ ~ ~ ~
    #  ~ ~ ~ go on until canceled ~ ~  
    
    def _circlingDot(self):
        deltaTime = 5 / self._freq
        
        if ((time.perf_counter() - self._tCiDo) > deltaTime):
            # RING 0
            position = self._iCiDo % (self._LED_COUNT[0] + 1)
            self._tailedDot(0, position)
            
            # RING 1
            position = self._iCiDo % (self._LED_COUNT[1] + 1)
            self._tailedDot(1, position)
            
            # RING 2
            position = self._iCiDo % (self._LED_COUNT[2] + 1)
            self._tailedDot(2, position)
            
            self._iCiDo += 1
            self._tCiDo = time.perf_counter()
    
    
    def _pulsating(self):
        # modePuls 1 = 1 color breathing
        # modePuls 2 = colorful shifts
        
        # deltaTime = 4 / self._freq
        deltaTime = 0.03
        
        if ((time.perf_counter() - self._tPuls) > deltaTime):
            self._tPuls = time.perf_counter()
            
            if self._modePuls == 1: # breathing
                if self._phasePuls == 1: # fade Up
                    if self._iPuls < 21:
                        ifactor    = 0.015*self._iPuls
                        self.shine(factor = ifactor, factor2 = 0)
                        self._iPuls += 1
                    elif self._iPuls < 41:
                        ifactor    = 0.3 + 0.035*(self._iPuls-20)
                        self.shine(factor = ifactor, factor2 = 0)
                        self._iPuls += 1
                    else:
                        self._phasePuls = 2
                        self._iPuls = 0
                
                elif self._phasePuls == 2: # fade Down
                    if self._iPuls < 21: # first fast
                        ifactor    = 1 - 0.035*self._iPuls
                        self.shine(factor = ifactor, factor2 = 0)
                        self._iPuls += 1
                    elif self._iPuls < 41: # second slow
                        ifactor    = 0.3 - 0.015*(self._iPuls-20)
                        self.shine(factor = ifactor, factor2 = 0)
                        self._iPuls += 1
                    elif self._iPuls < 81: # let it be dark for a moment
                        self._iPuls += 1
                    else:
                        self._phasePuls = 1
                        self._iPuls = 0

                else:
                    self._phasePuls = 1
                    self._iPuls = 0
                    
            elif self._modePuls == 2: # color-color shift
                if self._iPuls < 41:
                    startM = 1 - 0.025*self._iPuls
                    endM   = 0.025*self._iPuls
                    self.shine(factor = startM, factor2 = endM)
                    self._iPuls += 1
                elif self._iPuls < 51:
                    self._iPuls += 1
                else:
                    self._color = self._color2
                    self._iPuls = 1
                    if self._phasePuls == 1:
                        self._color2 = [100,0,0]
                        self._phasePuls = 2
                    elif self._phasePuls == 2:
                        self._color2 = [0,0,100]
                        self._phasePuls = 3
                    elif self._phasePuls == 3:
                        self._color2 = [0,100,0]
                        self._phasePuls = 1
                    else:
                        self._color2 = [100,0,0]
                        self._phasePuls = 2
            else:
                self._modePuls = 1
                self._phasePuls = 1
                self._iPuls = 0
                    
    
    def _rain(self):
        deltaTime = 10 / self._freq
        
        if ((time.perf_counter() - self._tRain) > deltaTime):
            # Ring 0
            self._rainPattern(0, self._iRain)
            
            # Ring 1
            self._rainPattern(1, self._iRain)
            
            # Ring 2
            self._rainPattern(2, self._iRain)
            
            self._iRain += 1
            self._tRain = time.perf_counter()
    
    def _obduction(self):
        # _phaseObduct 1: light is rising
        # _phaseObduct 2: trail is fizzeling away
        # _phaseObduct 3: darkness for a second
        
        # _phaseObduct, _iObduct, _tObduct
        
        if (self._phaseObduct == 3) and ((time.perf_counter() - self._tObduct) > 1):
            # ~ print("INFO - JulianLED - obduction - it was dark for 1 sec")
            # after 1 sec of darkness -> start again
            self._phaseObduct = 1
            self._iObduct = 1
            
        elif (self._phaseObduct == 2) and (time.perf_counter() - self._tObduct > 0.05):
            # trail is fizzeling away
            self._oneFizzleStep(0, 40)
            self._oneFizzleStep(1, 40)
            self._oneFizzleStep(2, 40)
            
            self._tObduct = time.perf_counter() 
            self._iObduct += 1
            
            if self._iObduct >= 40:
                # ~ print("INFO - JulianLED - obduction - fizzle finished")
                self.shine(factor = 0, factor2 = 0)
                self._phaseObduct = 3
                
                
        elif (self._phaseObduct == 1):
            deltaTime = 5 / self._freq
            
            if ((time.perf_counter() - self._tObduct) > deltaTime):
                
                relativePos = 100*self._iObduct*self._iObduct/(70*70)
                
                for ring in range(3):
                    maxPosHalfRing = int(self._LED_COUNT[ring] / 2) # if the ring is parted in two halves they would be indexed from 0 to maxPosHalfRing
                    
                    position = int(relativePos*maxPosHalfRing/100)
                    
                    self._mirroredPattern(ring, position, inverted = True, factor = 1.0, factor2 = 0.0)
                    if position >= 1:
                        self._mirroredPattern(ring, position - 1, inverted = True, factor = 0.0, factor2 = 0.5)
                    if position >= 2:
                        self._mirroredPattern(ring, position - 2, inverted = True, factor = 0.0, factor2 = 0.2)
                
                self._tObduct = time.perf_counter() 
                self._iObduct += 1
                
                if self._iObduct >= 70:
                    # ~ print("INFO - JulianLED - obduction - phase 1 finished, let's fizzle")
                    self._phaseObduct = 2
                    self._iObduct = 1         
    
    
    # ~ ~ ~ ~ ~ ~ effects ~ ~ ~ ~ ~ ~
    #  ~ ~ ~ ~ end by them self ~ ~ ~ 
    
         
       
    # ~ ~ ~ ~ ~ ~ methods ~ ~ ~ ~ ~ ~ 
    #  ~ ~ don't have any timings ~ ~
    
    def shine(self, ring = -1, position = -5000, factor = 1, factor2 = 0):
        # input:  ring     = Number of Ring
        #         factor   = factor (between 0 and 1) for brightness of self._color
        #         factor2  = factor (between 0 and 1) for brightness of self._color2
        #         position = Number of LED on ring
        #           [0,x]
        # output: this procedure lights up the LEDs, so no return
        
        # no specific Ring, no specific Position => light up everything
        if (position == -5000) and (ring == -1):
            self._strip.fill((int((self._color[0]*factor + self._color2[0]*factor2)*self._brightness/100),
                              int((self._color[1]*factor + self._color2[1]*factor2)*self._brightness/100),
                              int((self._color[2]*factor + self._color2[2]*factor2)*self._brightness/100)))
        
        # no specific Ring, but specific Position => light this Position on every Ring                       
        elif (position != -5000) and (ring == -1):
            realPos = self._realPos(0, position)
            if realPos != -6000:
                self._strip[realPos] = (
                        int((self._color[0]*factor + self._color2[0]*factor2)*self._brightness/100),
                        int((self._color[1]*factor + self._color2[1]*factor2)*self._brightness/100),
                        int((self._color[2]*factor + self._color2[2]*factor2)*self._brightness/100))
            
            realPos = self._realPos(1, position)
            if realPos != -6000:        
                self._strip[realPos] = (
                        int((self._color[0]*factor + self._color2[0]*factor2)*self._brightness/100),
                        int((self._color[1]*factor + self._color2[1]*factor2)*self._brightness/100),
                        int((self._color[2]*factor + self._color2[2]*factor2)*self._brightness/100))
            
            realPos = self._realPos(2, position)
            if realPos != -6000:          
                self._strip[realPos] = (
                        int((self._color[0]*factor + self._color2[0]*factor2)*self._brightness/100),
                        int((self._color[1]*factor + self._color2[1]*factor2)*self._brightness/100),
                        int((self._color[2]*factor + self._color2[2]*factor2)*self._brightness/100))
        
        # specific Ring, no specific Position => light this whole Ring
        elif (position == -5000) and (ring != -1):
            ring = self._realRing(ring)
    
            for i in range(0, self._LED_COUNT[ring]):
                realPos = self._realPos(ring, i)
                if realPos != -6000:
                    self._strip[realPos] = (
                        int((self._color[0]*factor + self._color2[0]*factor2)*self._brightness/100),
                        int((self._color[1]*factor + self._color2[1]*factor2)*self._brightness/100),
                        int((self._color[2]*factor + self._color2[2]*factor2)*self._brightness/100))
        
        # specific Position on specific Ring => light up only this LED
        else:
            realPos = self._realPos(ring, position)
            if realPos != -6000:
                self._strip[realPos] = (
                        int((self._color[0]*factor + self._color2[0]*factor2)*self._brightness/100),
                        int((self._color[1]*factor + self._color2[1]*factor2)*self._brightness/100),
                        int((self._color[2]*factor + self._color2[2]*factor2)*self._brightness/100))
            
     
    def _realRing(self, ring):
        # makes sure that only ring 0 to 2 are addressed
        if (ring > 2) or (ring < 0):
            print(" ".join(["ERROR - _realRing - Somebody wanted to address ring ", str(ring)]))
        
        realRing = ring % 3
        return realRing
         
        
    def _realPos(self, ring, number):
        # input:  ring = number of ring
        #           [0,2]
        #         number = position on ring
        #           [0,x]
        #
        # output: realPos = number of LED on total consecutive LED stripe
        #           [0,x]

        if number == -6000:
            return number
        else:        
            ring = self._realRing(ring)
            
            if ring == 0:
                realPos = number % self._LED_COUNT[0]
                    
            elif ring == 1:
                realPos = self._LED_COUNT[0] + number % self._LED_COUNT[1]
                    
            elif ring == 2:
                realPos = self._LED_COUNT[0] + self._LED_COUNT[1] + number % self._LED_COUNT[2]
                    
            else:
                print(" ".join(["ERROR - _realPos -  Somebody wanted to address ring", str(ring)]))
                
            return realPos
            
    
    def _resetPrograms(self):
        self.shine(factor = 0, factor2 = 0)
        
        # Cicling Dot
        self._tCiDo = 0
        self._iCiDo = 8 
        
        # Pulsating
        self._tPuls = 0
        self._iPuls = 0
        self._phasePuls = 0
        self._modePuls = 1
        
        # Rain
        self._tRain = 0
        self._iRain = 0
        self._phaseRain = 0
        
        #Obduction
        self._tObduct = 0
        self._iObduct = 0
        self._phaseObduct = 1
        
        
    def _tailedDot(self, ring, position):            
        self.shine(ring = ring, position = self._checkImLED(ring, position - 3), factor = 0, factor2 = 0)
        
        self.shine(ring = ring, position = self._checkImLED(ring, position))
        self.shine(ring = ring, position = self._checkImLED(ring, position - 1), factor = 0, factor2 = 0.7)
        self.shine(ring = ring, position = self._checkImLED(ring, position - 2), factor = 0, factor2 = 0.1)
        #self.shine(factor = 0, factor2 = 0.03, position = position -3)
        
    def _checkImLED(self, ring, position):
        if position == self._LED_COUNT[ring]:
           return -6000
        else:
            return position
        
    def _rainPattern(self, ring, rainPos):
        # pattern: 1 - 0 - 1 - 0 - 1/2 - 0
        self._mirroredPattern(ring, rainPos, factor = 1.0)
        self._mirroredPattern(ring, rainPos - 1, factor = 0.0)
        self._mirroredPattern(ring, rainPos - 2, factor = 0.1)
        self._mirroredPattern(ring, rainPos - 3, factor = 0.0)
        self._mirroredPattern(ring, rainPos - 4, factor = 0.05)
        self._mirroredPattern(ring, rainPos - 5, factor = 0.0)
    
    def _mirroredPattern(self, ring, sidePos, inverted = False, factor = 1, factor2 = 0):
        # input: ring = number of ring
        #        sidePos = position on ring counting from the top LED downwards to the buttom LED on both sides of the ring
        #          [0, x]
        #        inverted = False >> LEDs are counted from top to buttom, inverted = True >> LEDs are counted from buttom to top
        #        factor and factor2 will be just copied to shine()
        # output: command shine on both sides of the ring, so that the animation is mirrored relative to the vertical axis of the ring
        
        maxPosHalfRing = int(self._LED_COUNT[ring] / 2) # if the ring is parted in two halves they would be indexed from 0 to maxPosHalfRing
        
        if inverted:
            position1 = self._TOP_LED[ring] + maxPosHalfRing + sidePos % maxPosHalfRing
            self.shine(ring = ring, position = position1, factor = factor, factor2 = factor2)
            
            position2 = self._TOP_LED[ring] + maxPosHalfRing - 1 - sidePos % maxPosHalfRing
            self.shine(ring = ring, position = position2, factor = factor, factor2 = factor2)
            
        else:
            position1 = self._TOP_LED[ring] + sidePos % maxPosHalfRing
            self.shine(ring = ring, position = position1, factor = factor, factor2 = factor2)
            
            position2 = self._TOP_LED[ring] - 1 - sidePos % maxPosHalfRing
            self.shine(ring = ring, position = position2, factor = factor, factor2 = factor2)


    def _oneFizzleStep(self, ring, iterations):
        # input:    ring        = Number of Ring
        #           iteraions   = after how many iterations should the ring be (statistically) shout off
        # output:   random LEDs will be turned off
        
        # the number of LEDs that are turned off in one Fizzle Step
        number = self._LED_COUNT[ring]*5/iterations
        
        for i in range(int(number) - 1):
            position = int(random.random()*self._LED_COUNT[ring])
            self.shine(ring = ring, position = position, factor = 0, factor2 = 0)
            
