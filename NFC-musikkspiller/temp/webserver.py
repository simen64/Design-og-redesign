from flask import Flask, redirect, render_template, request, url_for
import json
app = Flask(__name__)

@app.route('/')
def home():
   with open("flask/albums.json", 'r') as file:
         albums = json.load(file)
   return render_template("index.html", albums=albums)

@app.route('/album_data',methods = ['POST', 'GET'])
def album_data():
   if request.method == 'POST':
      album_name = request.form['album-name']
      album_link = request.form["album-link"]

      with open("albums.json", 'r') as file:
         temp = json.load(file)
      
      album_data = {
         "album_name": album_name,
         "album_link": album_link,
         "album_id": str(max(int(item['album_id']) for item in temp) + 1)
      }

      temp.append(album_data)
         
      with open("albums.json", "w") as file:
         json.dump(temp, file, indent=4)

      return redirect(url_for("home"))


if __name__ == '__main__':
   app.run(debug = True)