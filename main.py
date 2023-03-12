###############################################
#
# Autor: Alex Merz
# Date: 16.10.2022
# Software: Bobbycar
# Board: Tiny2040
# Compiler: MicroPython (Raspberry Pi Pico) from Thonny Tool
# Load Code: Push boot button and change interpretor port (Right lower corner)
#            Sometimes Thonny has to be restarted for that
# Load script for autostart: Thonny -> View -> Folder -> coppy your code (main.py) and neopixel.py to IC
#
###############################################
############################ Notes
#pixels.brightness(50)
#pixels.fill(orange) # Set all pixel
#pixels.set_pixel_line_gradient(3, 13, green, blue) # Set gradient
#pixels.set_pixel_line(14, 16, red) # Set defined sector
#pixels.set_pixel(20, (255, 255, 255)) # Individual pixel set
#print("On")

############################ Library
import time
from neopixel import Neopixel
import machine
from machine import Pin
 
############################ Hardware
# Backlight led strip
backLightPixelNbr = 4
backlightStripPin = 4

# Frontlight led strip
frontLightPixelNbr = 16
frontLightStripPin = 5

# Status led
IcLedRed = machine.Pin(18, machine.Pin.OUT)
IcLedGreen = machine.Pin(19, machine.Pin.OUT)
IcLedBlue = machine.Pin(20, machine.Pin.OUT)

# Panel led
panelLedGreen = machine.Pin(6, machine.Pin.OUT)
panelLedRed = machine.Pin(7, machine.Pin.OUT)

# Panel button
#panelButtonRed = machine.Pin(2, machine.Pin.IN) # Button damaged and not usable
panelButtonBlue = machine.Pin(3, machine.Pin.IN)

# Oled display
# It is a SSD1331 Display with ONLY SPI -> Not enough pins for handling it

############################ Constants
# Pixel color scheme
pixelColorBlue = (0, 0, 255) # Green, Red, Blue
pixelColorLightBlue = (0, 0, 50) # Green, Red, Blue
pixelColorRed = (0, 255, 0) # Green, Red, Blue
pixelColorGreen = (255, 0, 0) # Green, Red, Blue
pixelColorWhite = (100, 100, 100) # Green, Red, Blue
pixelColorOff = (0, 0, 0) # Green, Red, Blue

# Statemachine
NORMAL = 1
BOOST = 2
    
# Pixel move direction
FORWARD = 1
BACKWARD = 2

############################ Variable
panelButtonBlueOld = 0
ledStrip = 0
boosterTimer = 0

# FrontLight
frontLightActPixel = 0
frontLightTimer = 0

# BackLight
backLightActPixel = 0
backLightTimer = 0
backLightMoveDirection = FORWARD

# Statemachine handling
stateMachine = NORMAL
stateMachineOld = NORMAL
stateInit = True

############################ Function declaration
######### Change object to backlight setup
def selectBackLight():
    global ledStrip
    ledStrip = Neopixel(backLightPixelNbr, 0, backlightStripPin, "RGB")
  
######### Change object to frontlight setup
def selectFrontLight():
    global ledStrip
    ledStrip = Neopixel(frontLightPixelNbr, 0, frontLightStripPin, "RGB")
    
######### Normal backlight signal
def normalBackLight():
    # Set all pixel to the same color and move a pixel for and back
    global ledStrip
    global stateInit
    global backLightActPixel
    global backLightTimer
    
    selectBackLight()
    
    # Init function
    if stateInit:
        ledStrip.fill(pixelColorBlue) # Set all pixel
        ledStrip.show()
    else: # Move pixel back an for
        # Update pixel after timer has ended
        if backLightTimer > 10:
            ledStrip.fill(pixelColorBlue) # Set all pixel
            
            # Set actual pixel
            ledStrip.set_pixel(backLightActPixel, pixelColorBlue) # Individual pixel set
            
            moveBackLightPixel()
            
            # Set next pixel
            ledStrip.set_pixel(backLightActPixel, pixelColorLightBlue) # Individual pixel set
            
            ledStrip.show()
            
            # Reset timer
            backLightTimer = 0
        else:
            backLightTimer = backLightTimer + 1
            
######### move backlight pixel back and forward      
def moveBackLightPixel():
    global backLightActPixel
    global backLightMoveDirection
    
    # Check if actual pixel is at the beginning
    if backLightActPixel == 0:
        backLightActPixel = backLightActPixel + 1
        backLightMoveDirection = FORWARD
    elif backLightActPixel >= (backLightPixelNbr - 1): # Check if pixel is at the end
        backLightActPixel = backLightActPixel - 1
        backLightMoveDirection = BACKWARD
    else:
        # Select direction
        if backLightMoveDirection == FORWARD:
            backLightActPixel = backLightActPixel + 1
        else: # Backward
            backLightActPixel = backLightActPixel - 1
    
######### Booster backlight signal
def boosterBackLight():
    # Set all pixel to the same color and let some led blinking
    global ledStrip
    global stateInit
    global backLightTimer
    
    selectBackLight()
    
    # Init function
    if stateInit:
        ledStrip.fill(pixelColorRed) # Set all pixel
        ledStrip.show()
    else:
        if backLightTimer > 10:
            ledStrip.fill(pixelColorRed) # Set all pixel
            
            # Set next pixel
            ledStrip.set_pixel(1, pixelColorOff) # Individual pixel set
            ledStrip.set_pixel(2, pixelColorOff) # Individual pixel set
            
            ledStrip.show()
            
            # Reset timer
            backLightTimer = 0
        elif backLightTimer > 5:
            ledStrip.fill(pixelColorRed) # Set all pixel
            
            # Set actual pixel
            ledStrip.set_pixel(1, pixelColorRed) # Individual pixel set
            ledStrip.set_pixel(2, pixelColorRed) # Individual pixel set
            
            ledStrip.show()
        
        backLightTimer = backLightTimer + 1
        
######### Normal front light handling  
def normalfrontLight():
    # Set all pixel to the same color and move a pixel around
    global ledStrip
    global stateInit
    global frontLightActPixel
    global frontLightTimer
    
    selectFrontLight()
    
    # Init function
    if stateInit:
        ledStrip.fill(pixelColorWhite) # Set all pixel
        ledStrip.show()
    else: # Move pixel back an for
        # Update pixel after timer has ended
        if frontLightTimer > 10:
            ledStrip.fill(pixelColorWhite) # Set all pixel
            
            # Set actual pixel
            ledStrip.set_pixel(frontLightActPixel, pixelColorWhite) # Individual pixel set
            
            moveFrontLightPixel()
            
            # Set next pixel
            ledStrip.set_pixel(frontLightActPixel, pixelColorOff) # Individual pixel set
            
            ledStrip.show()
            
            # Reset timer
            frontLightTimer = 0
        else:
            frontLightTimer = frontLightTimer + 1
            
######### Front light pixel moving
def moveFrontLightPixel():
    global frontLightActPixel
    global frontLightPixelNbr
    
    if frontLightActPixel >= (frontLightPixelNbr - 1):
        frontLightActPixel = 0
    else:
        frontLightActPixel = frontLightActPixel + 1
        
######### Button handling
def buttonHandling():
    global panelButtonBlueOld
    global panelButtonBlue
    global stateMachine
    
    # Blue button
    if panelButtonBlue.value() and not panelButtonBlueOld:
        print("Activate Booster")
        stateMachine = BOOST
    panelButtonBlueOld = panelButtonBlue.value()

######### State machine got a change of the state
def stateMachineUpdate():
    # If stateMachine has to be updated, set inital again
    global stateMachine
    global stateMachineOld
    global stateInit
    
    # If statemachine state has changed, do init again
    if stateMachine != stateMachineOld:
        stateInit = True
        stateMachineOld = stateMachine
        resetAllLedStripData()
    else:
        stateInit = False

######### Reset all led handling variable back to inital value
def resetAllLedStripData():
    global backLightActPixel
    global backLightTimer
    global backLightMoveDirection
    global boosterTimer
    
    backLightActPixel = 0
    backLightTimer = 0
    backLightMoveDirection = FORWARD
    boosterTimer = 0
    
######### Reset all led handling variable back to inital value
def timeoutBooster():
    global boosterTimer
    global stateMachine
    
    if boosterTimer >= 1000:
        stateMachine = NORMAL
    else:
        boosterTimer = boosterTimer + 1


############################ Main
print("___________________BobbyCar software started___________________")

# Set status light on board
IcLedRed.high() # Off
IcLedGreen.low() # On
IcLedBlue.high() # Off

# Signal to user, that software is running
panelLedGreen.high() # On

while True:
    #Statemachine
    if stateMachine == NORMAL:
        normalBackLight()
        normalfrontLight()
        panelLedRed.low() # Off
    else: # Booster
        boosterBackLight()
        normalfrontLight()
        panelLedRed.high() # On
        timeoutBooster()
    
    buttonHandling()

    stateMachineUpdate()

    # Definition how fast cycle is
    time.sleep(0.01)
    