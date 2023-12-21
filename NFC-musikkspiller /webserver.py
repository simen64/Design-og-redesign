#Import needed dependencies
from flask import Flask, redirect, render_template, request, url_for, session
import json
import os
from dotenv import load_dotenv

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from pathlib import Path
import re

#If the code is on a raspberry pi include needed pi dependencies
CPUINFO_PATH = Path("/proc/cpuinfo")


def is_raspberry_pi():
    if not CPUINFO_PATH.exists():
        return False
    with open(CPUINFO_PATH) as f:
        cpuinfo = f.read()
    return re.search(r"^Model\s*:\s*Raspberry Pi", cpuinfo, flags=re.M) is not None

is_pi = is_raspberry_pi()
print(is_pi)

if is_pi:
   import RPi.GPIO as GPIO
   from mfrc522 import SimpleMFRC522
   reader = SimpleMFRC522()


app = Flask(__name__)

load_dotenv()

#Set flak secret key
app.secret_key = "4df0d79df5f543ccbc330aecea7d6538"

#Set up authentication for spotify API
client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

#Define function for loading and reading the json database
def load():
   with open("database.json", 'r') as file:
         return json.load(file)
   
#Define the function for turning a link to an ID
def link_to_id(link):
   link = link.replace("https://open.spotify.com/album/", "")
   link = link.replace("https://open.spotify.com/track/", "")
   link = link.split("?")
   print(link)
   link.pop(1)
   id = link[0]
   return id
         
#Define the home page
@app.route('/')
def home():
   data = load()
   return render_template("index.html", data=data)

#Define the url where album uri is sent
@app.route('/send_data',methods = ['POST', 'GET'])
def album_data():
   if request.method == 'POST':

      #Get the URI from the user, and remove the unneeded parts to get the ID
      raw_input = request.form["raw-input"]

      if "https://" in raw_input:
         
         if "album" in raw_input:
            id = link_to_id(raw_input)
            raw_input = "spotify:album:" + id

         elif "track" in raw_input:
            id = link_to_id(raw_input)
            raw_input = "spotify:track:" + id

      if "album" in raw_input:

         album_spotify_id = raw_input.replace("spotify:album:", "")
         print(album_spotify_id)

         #Use spotifys api to get info about the album
         album_info = sp.album(album_spotify_id)

         #Get the album name and cover
         album_link = album_info['images'][0]['url']
         album_name = album_info["name"]

         #Structure the new data
         data = {
            "cover": album_link,
            "name": album_name,
            "uri" : raw_input,
         }

      elif "track" in raw_input:
         track_spotify_id = raw_input.replace("spotify:track:", "")
         print(track_spotify_id)

         # Use Spotify's API to get info about the track
         track_info = sp.track(track_spotify_id)

         # Get the track name and album
         track_name = track_info["name"]
         track_album_cover = track_info["album"]["images"][0]["url"]

         # Structure the new data
         data = {
            "cover":track_album_cover,
            "name":track_name,
            "uri": raw_input
         }

      #Store the data in a session
      session['data'] = data

      return redirect(url_for("scan"))
   
   else:
      return redirect(url_for("home"))
              

@app.route("/scan")
def scan():

   #Scan for a nfc tag, if it isnt a pi, enter an ID manually
   if is_pi:
      id = reader.read()
      print(f"id: {id}")

      id_from_scan = id[0]
      id_from_scan = str(id_from_scan)

      GPIO.cleanup()

   else:
      id_from_scan = input("Manually enter ID: ")

   #load the database and check for ID conflicts
   temp = load()

   for item in temp:
        if 'id' in item and item['id'] == id_from_scan:
            print("Error, cant have two albums / songs with the same ID")
            return redirect(url_for("ID_conflict"))

   data = session.get('data')

   data['id'] = id_from_scan

   #Load the database

   #Append the data to the database
   temp.append(data)
      
   #Write the data to the databse
   with open("database.json", "w") as file:
      json.dump(temp, file, indent=4)

   return redirect(url_for("home"))

@app.route("/ID_conflict")
def ID_conflict():
   return render_template("ID_conflict.html")

#Define the URL for deleting an album
@app.route("/delete",methods = ["POST", "GET"])
def delete():
   if request.method == "POST":
      id = request.form["delete"]

      print(id)

      temp = load()

      for item in temp:
         if 'id' in item and item['id'] == id:
            print(f"Found album / song with ID {item['id']}")

            temp.remove(item)

            with open("database.json", "w") as file:
               json.dump(temp, file, indent=4)

         else:
            pass

      return redirect(url_for("home"))


if __name__ == '__main__':
   app.run(host="0.0.0.0")