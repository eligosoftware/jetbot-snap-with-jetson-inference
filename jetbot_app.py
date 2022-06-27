import asyncio
import websockets
import traitlets
from traitlets.config.configurable import SingletonConfigurable
from motor import Motor
from robot import Robot

robot=Robot()

async def process(websocket,path):
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
            
            elif message.startswith("setmotors"):
                message_arr=message.split(" ")
                
                robot.set_motors(float(message_arr[1]),float(message_arr[2]))
                
            elif message=="stop":
                robot.stop()                
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

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    
except KeyboardInterrupt:
    print("Keyboard Interrupt")