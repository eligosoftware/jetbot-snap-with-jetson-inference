import asyncio
import websockets
import ast
import base64
import DetectNetConnector as decNet
import json
import time
import cv2
import jetson.inference
import jetson.utils


connector = decNet.DetectNetConnector()
net = jetson.inference.detectNet("ssd-mobilenet-v2")
camera = jetson.utils.videoSource("csi://0")  #"/dev/video0"


async def process(websocket,path):
	while not websocket.closed:
		count = 0
		async for message in websocket:

			image =  camera.Capture()
			pic = jetson.utils.cudaAllocMapped(width = image.width * 0.375, height = image.height * 0.5, format = image.format)
			jetson.utils.cudaResize(image, pic)

			detections = connector.RunInference(pic,net)

			picture = jetson.utils.cudaToNumpy(pic)
			converted_picture = cv2.cvtColor(picture, cv2.COLOR_RGB2BGR)
			retval, buffer = cv2.imencode('.jpg', converted_picture)
			jpg_as_text = base64.b64encode(buffer)
			response = {"image":str(jpg_as_text.decode('utf-8')),"detections":detections}
			response = json.dumps(response)
			

			await websocket.send(response)
	
	print("something went wrong")

async def main ():
	async with websockets.serve(process, "0.0.0.0", 4040, ping_interval = None):
		await asyncio.Future()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

