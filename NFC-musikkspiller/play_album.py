#Import dependencies
import json
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time
from dotenv import load_dotenv
import os
import requests
import board
import neopixel
import threading

#NFC reader config
reader = SimpleMFRC522()

# NeoPixel configuration
pixel_pin = board.D18  # Change this to the appropriate pin connected
num_pixels = 24  # Change this to the number of pixels in your ring
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.1, auto_write=False, pixel_order=ORDER)

#Define function for loading the database
def load():
   with open("database.json", 'r') as file:
         return json.load(file)

#Define all variables
load_dotenv()

Token = os.getenv("HA_TOKEN")

headers = {
    "Authorization": str("Bearer " + Token),
    "content-type": "application/json",
}

HA_URL = os.getenv("HA_URL")

helper_id = os.getenv("HELPER_ID")

script_id = os.getenv("SCRIPT_ID")

spotify_id = "media_player.spotify_simen"

current_tag_id = None

tag_countdown = -1

on_pause = False

id_played = None

STEP_DELAY = 0.005

#Define the color animations
def green_pulse():
    for i in range(0, 256, 5):
        # Set all pixels to green with varying brightness
        for j in range(len(pixels)):
            pixels[j] = (0, i, 0)
        pixels.show()
        time.sleep(STEP_DELAY)

    for i in range(255, 0, -5):
        # Set all pixels to green with varying brightness
        for j in range(len(pixels)):
            pixels[j] = (0, i, 0)
        pixels.show()
        time.sleep(STEP_DELAY)

def wipe_to_green():
    for i in range(len(pixels)):
        pixels[i] = (0,255,0)
        pixels.show()
        time.sleep(0.05)
    for i in range(len(pixels)):
        pixels[i] = (0,0,0)
        pixels.show()
        time.sleep(0.05)

def wipe_to_yellow():
    for i in range(len(pixels)):
        pixels[i] = (200,100,0)
        pixels.show()
        time.sleep(0.05)

#Update helper function
def update_helper(Spotify_URI):
    global helper_id, HA_URL, headers
    print("updating helper")

    #set the data
    data = {
    'state': Spotify_URI,
    }

    #send data
    response = requests.post(f'{HA_URL}/api/states/{helper_id}', headers=headers, json=data)

    if response.status_code == 200:
        print(f'Successfully updated the value of {helper_id}')
    else:
        print(f'Failed to update the value. Status code: {response.status_code}, Response: {response.text}')

#Run script function
def run_script():
    global script_id, HA_URL
    print("running script")

    #set data
    data = {
    'entity_id': script_id,
    }

    url = f'{HA_URL}/api/services/script/turn_on'

    #send data
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        print(f'Successfully activated the script: {script_id}')
    else:
        print(f'Failed to activate the script. Status code: {response.status_code}, Response: {response.text}')

#play album function
def play_album(id):
    global Spotify_URI, id_played
    print("playing album")

    #find matching URI with ID
    data = load()

    for item in data:
        if 'id' in item and item['id'] == id:
            print(f"Found album with ID {item['id']}")
            Spotify_URI = item["uri"]
            id_played = id

            # Run the functions
            update_helper(Spotify_URI)

            run_script()

            print("Made green with play_album function")
            wipe_to_green()
            break
    else:
        print("no albums with matchind IDs were found")


#Function for scanning
def scanning():
    global current_tag_id
    #do the canning
    try:
        while True:
            print("Hold a tag near the reader")
            id = reader.read()
            id = id[0]
            id = str(id)
            print(id)

            #Check if its the same tag
            if id != current_tag_id:
                play_album(id)
            else:
                print("same tag")

            current_tag_id = id
            time.sleep(10) 

    except KeyboardInterrupt:
        GPIO.cleanup()
        raise

#Function for pausing or playing
def music_control(pause_or_play):
    global spotify_id

    data = {
    "entity_id": spotify_id
    }

    response = requests.post(f'{HA_URL}/api/services/media_player/media_{pause_or_play}', headers=headers, json=data)

    if response.status_code == 200:
        print(f'Successfully paused or played')
    else:
        print(f'Failed to update the value. Status code: {response.status_code}, Response: {response.text}')

#Tag detect function
def tag_detect():
    global tag_countdown, on_pause, id_played
    #continuerly check for a tag
    while True:
        id = reader.read()
        id = id[0]
        id = str(id)
        print("tag is there")
        #reset countdown
        tag_countdown = 3
        #play music if it is on pause
        if on_pause:
            if id == id_played:
                print(f"ID: {id}, id_played: {id_played}")
                music_control("play")
                on_pause = False
                print("Made green with tag_detect function")
                t = threading.Thread(target=wipe_to_green)
                t.start()
            else:
                on_pause = False
        
#countodwn for tag_detect
def tag_detect_countdown():
    global tag_countdown
    while True:
        tag_countdown = tag_countdown - 1
        if tag_countdown <= -1:
            tag_countdown = -1
        if tag_countdown == 0:
            tag_not_there()

        #print(tag_countdown)
        time.sleep(1)

#countdown for inactivity
def pause_countdown():
    global on_pause, current_tag_id, countdown
    countdown = 60
    while True:
        if on_pause:
            countdown = countdown - 1
            if countdown == 0:
                print("COUNT REACHED 0")
                on_pause = False
                current_tag_id = None
                pixels.fill((0,0,0))
                pixels.show()
                print("TURNED OFF PIXELS")
            time.sleep(1)
        else:
            pass


#Function for when the tag isnt there
def tag_not_there():
    global on_pause, countdown
    print("tag not there anymore")
    music_control("pause")
    countdown = 60
    on_pause = True
    print("Made lights yellow")
    wipe_to_yellow()


#Do all the threading stuff
scan_thread = threading.Thread(target=scanning)
tag_detect_thread = threading.Thread(target=tag_detect)
tag_countdown_thread = threading.Thread(target=tag_detect_countdown)
pause_countdown_thread = threading.Thread(target=pause_countdown)

scan_thread.start()
tag_detect_thread.start()
tag_countdown_thread.start()
pause_countdown_thread.start()

scan_thread.join()
tag_detect_thread.join()
tag_countdown_thread.join()
pause_countdown_thread.join()
    
