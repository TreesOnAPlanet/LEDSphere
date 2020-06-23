#
# Author: Julian L. Nicklas
# shoutout to https://www.youtube.com/watch?v=F5-dV6ULeg8
#

from evdev import InputDevice, categorize, ecodes

EVENT_LOC = '/dev/input/event4' # the event of your bluetooth device

class btGamePad():
    def __init__(self):
        self._GP = None
        
        self._keyMatrix = [
        # event-Code, Meaning  >> _keyMatrix[5][1] = "Plus"
                305, # A
                304, # B
                308, # X
                307, # Y
                314, # Minus
                315, # Plus
                310, # L1
                312, # L2
                311, # R1
                313, # R2
                317, # LJpress
                318  # RJPress
            ]
        
        self._axisMatrix = [
        # event-Code, Meaning, Default Value, Min Value, Max Value
        # the Dpad can be read as a Key Event and as an Axis Status
                [17, 0],  #       DpadY: Key: -1 = Up,     0 = Default,   1 = Down 
                          #             Axis:  0 = Up,   128 = Default, 255 = Down
                [16, 0],  #       DpadX: Key: -1 = Left,   0 = Default,   1 = Right
                          #             Axis:  0 = Left, 128 = Default, 255 = Right
                [1, 128], #  Left Joystick Y:  0 = Up,   128 = Default, 255 = Down
                [0, 128], #  Left Joystick X:  0 = Left, 128 = Default, 255 = Right
                [5, 128], # Right Joystick Y:  0 = Up,   128 = Default, 255 = Down
                [2, 128]  # Right Joystick X:  0 = Left, 128 = Default, 255 = Right
            ]
        
        
    def tryBTconnect(self):
        if self._GP is None:
            try:
                self._GP = InputDevice(EVENT_LOC)
            except:
                self._GP = None
           #     print("gamepad - tryBTconnect: No BT controller found")
                return False
            else:
            #    print("gamepad - tryBTconnect: BT controller connected")
                return True
        else:
            return True
            
    def tryBTreconnect(self):
        try:
            self._GP = InputDevice(EVENT_LOC)
        except:
            self._GP = None
          #  print("gamepad - tryBTreconnect: No BT controller found")
            return False
        else:
          #  print("gamepad - tryBTreconnect: BT controller connected")
            return True
            
    def getBTstatus(self):
        if self._GP is None:
            return False
        else:
            return True
        
    def getKey(self):
        # reEvent
        # -10 - Disconnected,  -9 - New Connection
        #  -5 - Event is None, -4 - Unknown Key
        
        try:
            event = self._GP.read_one()
            
        except:
            if not self.tryBTreconnect():
                reEvent = [ -10, 0]
                return reEvent
            else:
                reEvent = [ -9, 0]
                return reEvent
            
        else:
            if event is not None:
                #is the event a KeyPress and is the event Code one of the defined Keys?
                if (event.type == ecodes.EV_KEY) and (event.code in self._keyMatrix):
                    # ~ print(" ".join(["INFO - GamePad - KeyPress: ", str(event.code), " - ", str(event.value)]))
                    return [event.code, event.value]
                            
                elif event.type == ecodes.EV_ABS:
                    for i in self._axisMatrix:
                        if (i[0] == event.code) and ((i[0] == 16) or (i[0] == 17)):
                            # ~ print(" ".join(["INFO - GamePad - KeyPress: ", str(event.code), " - ", str(event.value)]))
                            return [event.code, event.value]
                else:
                    return [ -4, 0]
            else:
                return [ -5, 0]
                
    def updateAxis(self):
    # needs to be called on a regular basis to update the Axis Status
        try:
            event = self._GP.read_one()
            
        except:
            if not self.tryBTreconnect():
                return False
        
        else:
            if event is not None:
                if event.type == ecodes.EV_ABS:
                    for i in self._axisMatrix:
                        if i[0] == event.code:
                            if (i[0] == 16):
                                if event.value == -1:
                                    i[1] = 0
                                elif event.value == 1:
                                    i[1] = 255
                                else:
                                    i[1] = 128
                            elif (i[0] == 17):
                                if event.value == -1:
                                    i[1] = 0
                                elif event.value == 1:
                                    i[1] = 255
                                else:
                                    i[1] = 128
                            else:    
                                i[1] = event.value
            return True
                
    def getAxisStatus(self, requestedAxis):
        for i in self._axisMatrix:
            if requestedAxis == i[0]:
                return i[1]
