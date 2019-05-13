# Used for GPIO Pins
import RPi.GPIO as GPIO
#Used for Opening audio processes
import os
import subprocess
from subprocess import call
#Used for connecting to reporting database
import requests
import psycopg2
from psycopg2 import Error
#Used for keypad matrix
from pad4pi import rpi_gpio
from time import sleep
#Used for generating files names
import time

from settings import dbusername, dbpassword, location, jasperURL
######## Set Variables ########
debug = False
###############################

######## Database Connection ########
try:
    connection = psycopg2.connect(user = dbusername, password = dbpassword, host = "localhost",port = "5432", database = "phone")
except:
    print ("Unable to connect to database")

######## Setup GPIO Data ########
FNULL = open(os.devnull, 'w')
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#Turn on green light
GPIO.setup(26, GPIO.OUT)
GPIO.output(26, GPIO.HIGH)

GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)#Handset hook to GPIO23

######## Button Matrix ########
#Set the button matrix
MATRIX = [ ["P","U","0","S"],
           ["9","2","8","7"],
           ["3","","2", "1"],
           ["6","","5","4"]]

ROW = [2,3,4,17] #Row pins
COL = [27,22,10,9] # Column pins

factory = rpi_gpio.KeypadFactory()
keypad = factory.create_keypad(keypad=MATRIX, row_pins=ROW, col_pins=COL)

###############################
#    Button Press Function    #
###############################
def keyPress(key):
    global audioPlay, sessionID
    if debug:
        print(key)
    cursor.execute("SELECT file_name, id FROM phonesetup_button WHERE button_name = %s", (key))
    row = cursor.fetchone()
    fileName = row[0]
    if debug:
        print(fileName)
    sessionParams = {'session': sessionID, 'type': 'addTo', "button": key, "file": fileName }
    r = requests.post(url=jasperURL, data = sessionParams)
    audioPlay.kill()

    if(fileName == 'Recording'):
        if debug:
            audioPlay = subprocess.Popen(['arecord', "/LibraryLine/libraryLine/mediaAssets/" + str(time.time())[0:10] + str(time.time())[11:15]
])
        else:
            audioPlay = subprocess.Popen(['arecord', "/LibraryLine/libraryLine/mediaAssets/" + str(time.time())[0:10] + str(time.time())[11:15]
], stdout=FNULL, stderr=subprocess.STDOUT)
    else:
        if debug:
            audioPlay = subprocess.Popen(["aplay", "/LibraryLine/libraryLine/mediaAssets/" + fileName], stdout=FNULL, stderr=subprocess.STDOUT)
        else:
            audioPlay = subprocess.Popen(["aplay", "/LibraryLine/libraryLine/mediaAssets/" + fileName])
##############################
#        Program Loop        #
##############################
try: #Needed for ctr + c to kill everything
    while(True):
        phone_off_hook = True
        button_state = GPIO.input(24)
        if button_state == False: #Check if the handset is off the hook.
            call(["amixer", "set", "Speaker", "50%"], stdout=FNULL, stderr=subprocess.STDOUT) # Set speaker to 50%

            #Start a session on reporting server
            sessionParams = {'location': location, 'type': 'startSession'}
            r = requests.post(url=jasperURL, data = sessionParams)
            result = r.json()
            sessionID = result['sessionid']
            if debug:
                print( "Play sound start" )
                print(sessionID)
            cursor = connection.cursor()
            cursor.execute("SELECT file_name FROM phonesetup_button WHERE button_name = 'phone'")
            row = cursor.fetchone()
            fileName = row[0]

            #Check if playing a sound or recording
            if(fileName == "Recording"):
                if debug:
                    audioPlay = subprocess.Popen(['arecord', "/LibraryLine/libraryLine/mediaAssets/" + str(time.time())[0:10] + str(time.time())[11:15]
])
                else:
                    audioPlay = subprocess.Popen(['arecord', "/LibraryLine/libraryLine/mediaAssets/" + str(time.time())[0:10] + str(time.time())[11:15]
], stdout=FNULL, stderr=subprocess.STDOUT)
            else:
            #Play the starting sound
                if debug:
                    audioPlay = subprocess.Popen(["aplay", "/LibraryLine/libraryLine/mediaAssets/" + fileName])
                else:
                    audioPlay = subprocess.Popen(["aplay", "/LibraryLine/libraryLine/mediaAssets/" + fileName], stdout=FNULL, stderr=subprocess.STDOUT)

            keypad.registerKeyPressHandler(keyPress)
            while(phone_off_hook):
                sleep(1)
                button_state = GPIO.input(24)
                if(button_state):
                    #Close session on reporting server
                    sessionParams = {'session': sessionID, 'type': 'closeSession'}
                    r = requests.post(url=jasperURL, data = sessionParams)
                    phone_off_hook = False
                    audioPlay.kill()
                    if debug:
                        print("Session " + sessionID + " closed.")


except KeyboardInterrupt:
    keypad.cleanup()
    print("Keypad Closed")
    GPIO.cleanup()
    print("GPIO Cleaned")
    if(connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
