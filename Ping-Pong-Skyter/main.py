from flask import Flask, render_template, request, redirect, url_for
import time
import threading
import random
import RPi.GPIO as GPIO

#Configure stuff for the stepper motor
def load_ball():
   in1 = 17
   in2 = 18
   in3 = 27
   in4 = 22

   direction = True

   step_sleep = 0.002
   step_count = 682

   step_sequence = [[1,0,0,1],
                 [1,0,0,0],
                 [1,1,0,0],
                 [0,1,0,0],
                 [0,1,1,0],
                 [0,0,1,0],
                 [0,0,1,1],
                 [0,0,0,1]]
   
   GPIO.setmode( GPIO.BCM )
   GPIO.setup( in1, GPIO.OUT )
   GPIO.setup( in2, GPIO.OUT )
   GPIO.setup( in3, GPIO.OUT )
   GPIO.setup( in4, GPIO.OUT )

   GPIO.output( in1, GPIO.LOW )
   GPIO.output( in2, GPIO.LOW )
   GPIO.output( in3, GPIO.LOW )
   GPIO.output( in4, GPIO.LOW )

   motor_pins = [in1,in2,in3,in4]
   motor_step_counter = 0

   try:
    i = 0
    for i in range(step_count):
        for pin in range(0, len(motor_pins)):
            GPIO.output( motor_pins[pin], step_sequence[motor_step_counter][pin] )
        if direction==True:
            motor_step_counter = (motor_step_counter - 1) % 8
        elif direction==False:
            motor_step_counter = (motor_step_counter + 1) % 8
        else: # defensive programming
            print( "uh oh... direction should *always* be either True or False" )
            exit( 1 )
        time.sleep( step_sleep )
   except:
      pass

   GPIO.output( in1, GPIO.LOW )
   GPIO.output( in2, GPIO.LOW )
   GPIO.output( in3, GPIO.LOW )
   GPIO.output( in4, GPIO.LOW )
   GPIO.cleanup()

#Set up Flask
app = Flask(__name__)

#Set up variables
static_mode_status = False
random_mode_status = False
trigger_mode_status = False


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
      load_ball()


def random_mode():
   global random_mode_status
   while True:
      if random_mode_status == False:
         print("turning off")
         break
      else:
         pass
      interval = random.randint(1,7)
      time.sleep(interval)
      print("FIRE!")
      load_ball()


@app.route("/")
def home():
   return render_template("index.html")


@app.route("/static_options", methods = ['POST', 'GET'])
def static_mode_activation():
   global static_mode_status, random_mode_status, trigger_mode_status
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

         trigger_mode_status = False
         random_mode_status = False
         static_mode_status = True
         static_mode_thread = threading.Thread(target=static_mode, args=(interval,))
         static_mode_thread.start()
      
   return redirect(url_for("home"))


@app.route("/random_options", methods = ["POST", "GET"])
def random_mode_activation():
   global random_mode_status, static_mode_status, trigger_mode_status
   if request.method == "POST":

      if "stopp" in request.form:
         print("Stopping")
         random_mode_status = False
      else:
         trigger_mode_status = False
         static_mode_status = False
         random_mode_status = True
         random_mode_thread = threading.Thread(target=random_mode)
         random_mode_thread.start()

   return redirect(url_for("home"))

@app.route("/trigger_options", methods = ["POST", "GET"])
def trigger_mode():
   global random_mode_status, static_mode_status, trigger_mode_status
   if request.method == "POST":
      if "stopp" in request.form:
         print("Stopping")
         trigger_mode_status = False
   else:
      static_mode_status = False
      random_mode_status = False
      trigger_mode_status = True
   return redirect(url_for("home"))

@app.route("/fire", methods = ["POST", "GET"])
def fire_post():
   global trigger_mode_status
   if request.method == "POST":
      if trigger_mode_status == True:
         load_ball()
         return "fired"
      else:
         return "not listening"
   else:
      return "not post"


if __name__ == '__main__':
   app.run(debug=True, host="0.0.0.0", port=9000)