#
# Author: Julian L. Nicklas
#

import time

class PerfCounter:
	def __init__(self, correction = 0):
		self._lastTime = 0
		self._arrayCounter = 0
		self._arrayTimes = [0,0,0,0,0,0,0,0,0,0]
		self._timeLastPrint = 0
		self._CORRECTION = correction
		
	def setTimeStamp(self):
		if self._lastTime == 0:
			self._lastTime = time.perf_counter()
			self._timeLastPrint = self._lastTime
			
		else:
			self._arrayTimes[self._arrayCounter] = time.perf_counter() - self._lastTime - self._CORRECTION
			
			if time.perf_counter() - self._timeLastPrint > 4:
				print(" ".join(["INFO - PerformanceCounter - Avarage Time =", str(sum(self._arrayTimes) / 10)]))
				self._timeLastPrint = time.perf_counter()
			
			self._arrayCounter = (self._arrayCounter + 1) % 10
			self._lastTime = time.perf_counter()
		
