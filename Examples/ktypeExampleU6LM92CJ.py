import u6
import math
from time import sleep

# Coefficients

# See http://srdata.nist.gov/its90/download/type_k.tab

#   -200 C to 0 C
#   -5.891 mV to 0 mV
#   0.0E0
#   2.5173462E1
#   -1.1662878E0
#   -1.0833638E0
#   -8.977354E-1
#   -3.7342377E-1
#   -8.6632643E-2
#   -1.0450598E-2
#   -5.1920577E-4
voltsToTemp1 = (0.0E0,
				2.5173462E1,
				-1.1662878E0,
				-1.0833638E0,
				-8.977354E-1,
				-3.7342377E-1,
				-8.6632643E-2,
				-1.0450598E-2,
				-5.1920577E-4)

#   0 C to 500 C
#   0 mV to 20.644 mV
#   0.0E0
#   2.508355E1
#   7.860106E-2
#   -2.503131E-1
#   8.31527E-2
#   -1.228034E-2
#   9.804036E-4
#   -4.41303E-5
#   1.057734E-6
#    -1.052755E-8
voltsToTemp2 = (0.0E0,
				2.508355E1,
				7.860106E-2,
				-2.503131E-1,
				8.31527E-2,
				-1.228034E-2,
				9.804036E-4,
				-4.41303E-5,
				1.057734E-6,
				-1.052755E-8)

#   500 C to 1372 C
#   20.644 mV to 54.886 mV
#   -1.318058E2
#   4.830222E1
#   -1.646031E0
#   5.464731E-2
#   -9.650715E-4
#   8.802193E-6
#   -3.11081E-8
voltsToTemp3 = (-1.318058E2,
					4.830222E1,
					-1.646031E0,
					5.464731E-2,
					-9.650715E-4,
					8.802193E-6,
					-3.11081E-8)

def voltsToTempConstants(mVolts):
	if mVolts < -5.891 or mVolts > 54.886:
		raise Exception("Invalid range")
	if mVolts < 0:
		return voltsToTemp1
	elif mVolts < 20.644:
		return voltsToTemp2
	else:
		return voltsToTemp3

class ExtendedList(list):
	pass

#   -270 C to 0 C
#   0E0
#   0.39450128025E-1
#   0.23622373598E-4
#   -0.32858906784E-6
#   -0.49904828777E-8
#   -0.67509059173E-10
#   -0.57410327428E-12
#   -0.31088872894E-14
#   -0.10451609365E-16
#   -0.19889266878E-19
#   -0.16322697486E-22
tempToVolts1 = (0.0E0,
				0.39450128025E-1,
				0.23622373598E-4,
				-0.32858906784E-6,
				-0.49904828777E-8,
				-0.67509059173E-10,
				-0.57410327428E-12,
				-0.31088872894E-14,
				-0.10451609365E-16,
				-0.19889266878E-19,
				-0.16322697486E-22)

#   0 C to 1372 C
#   -0.17600413686E-1
#   0.38921204975E-1
#   0.18558770032E-4
#   -0.99457592874E-7
#   0.31840945719E-9
#   -0.56072844889E-12
#   0.56075059059E-15
#   -0.32020720003E-18
#   0.97151147152E-22
#   -0.12104721275E-25
#
#   0.1185976E0
#   -0.1183432E-3
#   0.1269686E3

tempToVolts2 = ExtendedList()
tempToVolts2.append(-0.17600413686E-1)
tempToVolts2.append(0.38921204975E-1)
tempToVolts2.append(0.18558770032E-4)
tempToVolts2.append(-0.99457592874E-7)
tempToVolts2.append(0.31840945719E-9)
tempToVolts2.append(-0.56072844889E-12)
tempToVolts2.append(0.56075059059E-15)
tempToVolts2.append(-0.32020720003E-18)
tempToVolts2.append(0.97151147152E-22)
tempToVolts2.append(-0.12104721275E-25)
tempToVolts2.extended = (0.1185976E0, -0.1183432E-3, 0.1269686E3)

def tempToVoltsConstants(tempC):
	if tempC < -270 or tempC > 1372:
		raise Exception("Invalid range")
	if tempC < 0:
		return tempToVolts1
	else:
		return tempToVolts2

def evaluatePolynomial(coeffs, x):
	sum = 0
	y = 1
	for a in coeffs:
		sum += y * a
		y *= x
	return sum

def tempCToMVolts(tempC):
	coeffs = tempToVoltsConstants(tempC)
	if hasattr(coeffs, "extended"):
		a0, a1, a2 = coeffs.extended
		extendedCalc = a0 * math.exp(a1 * (tempC - a2) * (tempC - a2))
		return evaluatePolynomial(coeffs, tempC) + extendedCalc
	else:
		return evaluatePolynomial(coeffs, tempC)

def mVoltsToTempC(volts):
	coeffs = voltsToTempConstants(volts)
	return evaluatePolynomial(coeffs, volts)

if __name__ == '__main__':
	u6Device = u6.U6(autoOpen = False)
	u6Device.open()
	u6Device.getCalibrationData()
	
	for i in range(1000):
		# The cold junction temperature
		# Important: Must be in Celsius
		data = u6Device.i2c(0x48, [0], NumI2CBytesToReceive = 2, ResetAtStart = True, SDAPinNum = 4, SCLPinNum = 5)
		temp1Bytes = data['I2CBytes']
		temp1 = ((temp1Bytes[0] << 8) | temp1Bytes[1]) >> 3
		
		if temp1 & 0x1000 :
			temp1 = -0x1000 + (temp1 & 0x0fff)
		else:
			temp1 = temp1 & 0x0fff
		
		temp1 = temp1 * 0.0625
		
		data = u6Device.i2c(0x4B, [0], NumI2CBytesToReceive = 2, ResetAtStart = True, SDAPinNum = 4, SCLPinNum = 5)
		temp2Bytes = data['I2CBytes']
		temp2 = ((temp2Bytes[0] << 8) | temp2Bytes[1]) >> 3
		if temp2 & 0x1000 :
			temp2 = -0x1000 + (temp2 & 0x0fff)
		else:
			temp2 = temp2 & 0x0fff
		
		temp2 = temp2 * 0.0625
		
		tempLJ = u6Device.getTemperature() - 273.15 + 1.0
		
		print "Schleife : ", i
		print "Cold Junction TempLeft : ", temp1
		print "Cold Junction TempRigth : ", temp2
		print "LabJack Temperature: ", tempLJ
		print ""
		
		TCmVolts1 = u6Device.getAIN(3, resolutionIndex = 8, gainIndex = 2) * 1000
		TCmVolts2 = u6Device.getAIN(10, resolutionIndex = 8, gainIndex = 2) * 1000
		print "Voltage 1 (in milivolts): ", TCmVolts1
		print "Voltage 2 (in milivolts): ", TCmVolts2
		totalMVolts1 = TCmVolts1 + tempCToMVolts(temp1)
		totalMVolts2 = TCmVolts2 + tempCToMVolts(temp2)
		
		print "Temperature 1: ", mVoltsToTempC(totalMVolts1)
		print "Temperature 2: ", mVoltsToTempC(totalMVolts2)
		print ""
		sleep(1)
	
	u6Device.close()