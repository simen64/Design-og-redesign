from flask import Flask, render_template, request, redirect, url_for
import time
import threading
import random

app = Flask(__name__)


static_mode_status = False
random_mode_status = False


def static_mode(interval):
   global static_mode_status
   while True:
      if static_mode_status == False:
         print("turning off")
         break
      else:
         pass
      time.sleep(interval)
      print("FIRE!")
      print(static_mode_status)


def random_mode():
   global random_mode_status
   while True:



@app.route("/")
def home():
   return render_template("index.html")


@app.route("/static_options", methods = ['POST', 'GET'])
def static_mode_activation():
   global static_mode_status
   if request.method == 'POST':

      if "stopp" in request.form:
         print("Stopping")
         static_mode_status = False

      else:
         interval = request.form["interval"]
         
         try:
            interval = int(interval)
         except:
            interval = 5

         static_mode_status = True
         static_mode_thread = threading.Thread(target=static_mode, args=(interval,))
         static_mode_thread.start()
      
   return redirect(url_for("home"))


if __name__ == '__main__':
   app.run(debug=True, host="0.0.0.0", port=9000)