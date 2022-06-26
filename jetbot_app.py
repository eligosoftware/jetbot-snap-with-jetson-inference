import asyncio
import websockets
import time
import base64
import json
import traitlets
from traitlets.config.configurable import SingletonConfigurable
from Adafruit_MotorHAT import Adafruit_MotorHAT
from motor import Motor
from robot import Robot
import threading
import cv2
import jetson.inference
import jetson.utils

camera_running=False

frame=None

robot=Robot()
net = jetson.inference.detectNet("ssd-mobilenet-v2")

video_capture=None

def gstreamer_pipeline(
    sensor_id=0,
    capture_width=1920,
    capture_height=1080,
    display_width=960,
    display_height=540,
    framerate=30,
    flip_method=0,
):
    return (
        "nvarguscamerasrc sensor-id=%d !"
        "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            sensor_id,
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )
def record_camera():
    global camera_running
    global frame
    global video_capture
    global net
    
    video_capture = cv2.VideoCapture(gstreamer_pipeline(flip_method=2), cv2.CAP_GSTREAMER)

    while True:
        ret_val, res_frame = video_capture.read()
        if res_frame is not None:
            cuda_image=jetson.utils.cudaFromNumpy(res_frame)
            net.Detect(cuda_image)
        frame=jetson.utils.cudaToNumpy(cuda_image)
        if not camera_running:
            break
    

async def process(websocket,path):
    global camera_running
    global video_capture
    while not websocket.closed:
        async for message in websocket:
            #print(message)
            if message=="left":
                robot.left(speed=1)
            elif message=="right":
                robot.right(speed=1)
            elif message=="forward":
                robot.forward(speed=1)
            elif message=="backward":
                robot.backward(speed=1)
            elif message=="stop":
                robot.stop()
            elif message=="frame":
                retval,buffer = cv2.imencode('.jpg',frame)
                # response = {"image":"data:image/jpeg;base64,"+str((base64.b64encode(buffer)).decode('utf-8'))}
                #response = json.dumps(response)
                response = "data:image/jpeg;base64,"+str((base64.b64encode(buffer)).decode('utf-8'))

                await websocket.send(response)
                
            elif message=="start_camera":
                camera_running=True
                threading.Thread(target=record_camera).start()
            elif message=="stop_camera":
                camera_running=False
            
            
                #response = {"message":"Received command "+message}
                #response = json.dumps(response)

                #await websocket.send(response)
    
async def main ():
    async with websockets.serve(process, "0.0.0.0", 4040, ping_interval=None):
        await asyncio.Future()
        
camera_running=True
threading.Thread(target=record_camera).start()

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
except KeyboardInterrupt:
    print("Keyboard Interrupt")
    camera_running=False
    video_capture.release()