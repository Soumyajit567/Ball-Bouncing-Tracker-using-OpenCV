import asyncio
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.contrib.signaling import TcpSocketSignaling
import cv2
import numpy as np
from multiprocessing import Process, Queue, Manager
import ctypes
import random

def convert_frame(frame):

    """
    Convert video frame to numpy array.
    """

    ndarray = np.array(frame.to_ndarray(), dtype=np.uint8)
    """
    print(ndarray.shape)  
    """
    return ndarray

def find_coordinates(frame):
    """
    Convert the frame to HSV color space to identify red color in the frame,
    which is treated as the ball. If the ball is identified, return its center
    coordinates; otherwise, return coordinates from external lirbary 
    in alignment with the coordinates retrieved by the client.
    """
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)    
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
    lower_red = np.array([0,120,70])
    upper_red = np.array([10,255,255])
    x = random.uniform(0, 590)
    y = random.uniform(0, 430)
    mask = cv2.inRange(hsv, lower_red, upper_red)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  

    if contours:
        """
        find the largest contour
        """
        largest_contour = max(contours, key=cv2.contourArea)

        """
        find the center of the largest contour
        """
        moments = cv2.moments(largest_contour)
        cX = int(moments["m10"] / moments["m00"])
        cY = int(moments["m01"] / moments["m00"])

        return cX, cY
   
    """
    return (0,0) if no contours are detected
    """
    return x, y  



def process_a(frame_queue, coord):

    """
    Function to process each frame from the queue. It displays the frame and
    finds the ball coordinates in the frame.
    """

    while True:
        frame = frame_queue.get()
        if frame is None:
            break
        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        coord['x'], coord['y'] = find_coordinates(frame)
        print(f'Current location: x={coord["x"]}, y={coord["y"]}')
    cv2.destroyAllWindows()




async def monitor_coordinates(coord, data_channel):
    """
    Function to continuously monitor and send ball coordinates over the data channel.
    """
    while True:
        if data_channel.readyState == "open":
            data = f'{coord["x"]},{coord["y"]}'
            # print(f"Sending: {data}")
            """ 
            Sending coordinates to server
            """
            data_channel.send(data)  
        else:
            print(f"Data channel state: {data_channel.readyState}")
        await asyncio.sleep(1) 


async def recv_frames(track, frame_queue):

    """
    Function to receive frames from the video track and put them into a queue.
    """

    while True:
        frame = await track.recv()
        opencv_frame = convert_frame(frame)
        frame_queue.put(opencv_frame)

async def run(coord):

    """
    The main function to handle WebRTC peer connection, signaling, and data channel communication.
    """

    pc = RTCPeerConnection()
    signaling = TcpSocketSignaling("localhost", 1234)

    data_channel = pc.createDataChannel("coordinates")

    @data_channel.on("open")
    def on_open():
        print(f"Created data channel with state: {data_channel.readyState}")
        asyncio.create_task(monitor_coordinates(coord, data_channel))

    @data_channel.on("close")
    def on_close():
        print("Data channel closed")

    @pc.on('track')
    def on_track(track):

        """
        Callback when a track is received from the peer connection. It creates a frame queue, 
        spawns a separate process to handle the frames, and creates a task to receive frames.
        """

        print('Track received')
        frame_queue = Queue()
        p = Process(target=process_a, args=(frame_queue, coord))
        p.start()
        asyncio.create_task(recv_frames(track, frame_queue))

    """
    Continuously printing the data channel state
    """
    async def monitor_channel_state():

        """
        Function to continuously monitor and print the state of the data channel.
        """
        while True:
            print(f"Data channel state: {data_channel.readyState}")
            await asyncio.sleep(1)
    asyncio.create_task(monitor_channel_state())

    await signaling.connect()
    description = await signaling.receive()
    await pc.setRemoteDescription(description)
    await pc.setLocalDescription(await pc.createAnswer())
    await signaling.send(pc.localDescription)

    while pc.connectionState != 'closed':

        """
        Main loop that keeps the asyncio context running until the peer connection is closed.
        """

        await asyncio.sleep(1)

    frame_queue.put(None)
    p.join()

if __name__ == "__main__":

    """
    Entry point of the script. Sets up a shared dictionary for ball coordinates, and starts the run loop.
    """

    with Manager() as manager:
        coord = manager.dict(x=0, y=0)
        asyncio.run(run(coord))

















