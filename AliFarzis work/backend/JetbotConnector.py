from robot import Robot
import time
import asyncio
import websockets

robot = Robot()


async def process(websocket,path):
	while not websocket.closed:
		count = 0
		async for message in websocket:
			controller(message)
			await websocket.send("Done")

def controller(control):
	
	if control == "jetbotleft":
		robot.left(speed=1)
		time.sleep(0.07)
		robot.stop()
	elif control == "jetbotright":
		robot.right(speed=1)
		time.sleep(0.07)
		robot.stop()
	elif control == "jetbotforward":
		robot.forward(speed=1)
	elif control == "jetbotbackward":
		robot.backward(speed=1)

	elif control.startswith("setmotors"):
		message_arr=control.split(" ")
		robot.set_motors(float(message_arr[1]),float(message_arr[2]))
	elif control == "jetbotstop":
		robot.stop()
	else:
		robot.stop()
		print("something wrong")


async def main ():
	async with websockets.serve(process, "0.0.0.0", 4041, ping_interval = None):
		await asyncio.Future()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())	
       
