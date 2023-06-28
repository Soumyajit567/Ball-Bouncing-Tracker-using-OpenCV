import asyncio
from av import VideoFrame
import numpy as np
from aiortc import RTCPeerConnection, VideoStreamTrack
from aiortc.contrib.signaling import TcpSocketSignaling
import cv2
import random

WIDTH = 640
HEIGHT = 480
BALL_SIZE = 50
BYE = "exit"

class BallBounceTrack(VideoStreamTrack):

    """
    A video track that simulates a bouncing ball.
    """

    def __init__(self):
        super().__init__()
        self.ball_pos = [WIDTH // 2, HEIGHT // 2]
        self.ball_vel = [3, 3]

    async def recv(self):

        """
        Continuously updates the video frames with the new ball position.
        """

        pts, time_base = await self.next_timestamp()

        """
        create an image with all white pixels
        """

        img = np.ones((HEIGHT, WIDTH, 3), dtype=np.uint8) * 255

        """ 
        update ball position
        """
        self.ball_pos[0] += self.ball_vel[0]
        self.ball_pos[1] += self.ball_vel[1]

        """
        if ball hits the wall, change direction
        """
        if self.ball_pos[0] < 0 or self.ball_pos[0] > WIDTH - BALL_SIZE:
            self.ball_vel[0] *= -1
        if self.ball_pos[1] < 0 or self.ball_pos[1] > HEIGHT - BALL_SIZE:
            self.ball_vel[1] *= -1

        """
        draw the ball on the image
        """
        cv2.circle(img, tuple(self.ball_pos), BALL_SIZE, (0, 0, 255), -1)

        frame = VideoFrame.from_ndarray(img, format="bgr24")
        frame.pts = pts
        frame.time_base = time_base

        return frame


async def run(pc, signaling):

    """
    The main function that connects to the peer and starts the ball tracking.
    """

    ball_track = BallBounceTrack()
    pc.addTrack(ball_track)

    async def test_errors():
        
        """
        A function that simulates a continuous stream of position errors. 
        This mimics the scenario of receiving erroneous location updates from an external source.
        """

        while True:
            print(f" Current Location Error: x_error = {random.uniform(-1, 1)}, y_error = {random.uniform(-1, 1)}")
            await asyncio.sleep(1)  

    random_errors_task = None

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():

        """
        Listener for connection state changes. Starts error generation when connected.
        """

        print(f"Connection state is {pc.connectionState}")
        if pc.connectionState == "connected":
            # start the task in the background
            random_errors_task = asyncio.create_task(test_errors())
        elif pc.connectionState == "failed" or pc.connectionState == "disconnected":
            if random_errors_task:
                random_errors_task.cancel()
            await pc.close()

    @pc.on('datachannel')
    def on_datachannel(channel):

        """
        Listener for the data channel. Handles incoming messages.
        """

        print("Data channel opened.")

        @channel.on('message')
        async def on_message(message):

            """
            Handles incoming messages. Calculates and prints the error in ball position.
            """
            print(f"Received coordinates: {message}")
            x, y = map(int, message.split(','))
            try:
                """
                If the error calculation is successful, print the error
                """
                error_x = x - ball_track.ball_pos[0]
                error_y = y - ball_track.ball_pos[1]
                print(f"Current Location Error: x_error = {error_x}, y_error = {error_y})")
            except:
                """ 
                errors are already being generated regularly, so just ignore exceptions here
                """
                asyncio.test_errors()
  
    await signaling.connect()

    await pc.setLocalDescription(await pc.createOffer())
    await signaling.send(pc.localDescription)

    remoteDescription = await signaling.receive()
    await pc.setRemoteDescription(remoteDescription)

    while True:
        message = await signaling.receive()

        if message == BYE:
            print("Exiting...")
            break


if __name__ == "__main__":

    """
    Entry point of the script. Sets up the RTCPeerConnection and TcpSocketSignaling, and starts the run loop.
    """

    pc = RTCPeerConnection()
    signaling = TcpSocketSignaling("", 1234)
    asyncio.run(run(pc, signaling))