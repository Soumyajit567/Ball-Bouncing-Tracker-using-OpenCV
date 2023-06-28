# Bouncing Ball Tracker

This project demonstrates a client-server application using Python and the aiortc library to track a bouncing ball's coordinates. The server simulates a bouncing ball within a frame, while the client receives the video frames, identifies the ball within each frame, and sends the ball coordinates back to the server. Both server and client communicate using the WebRTC protocol, specifically the aiortc Python library.

**Table of Contents**
* Prerequisites
* Installation
* Implementation Overview
* How to Run
* Understanding the Code
* Unit Tests
* Docker Compose Deployment
* Docker Deployment
* Limitation

**Prerequisites**
* Python 3.8+
* OpenCV library
* aiortc library

**Installation**

Install the required dependencies:

`pip install aiortc opencv-python numpy`


**Implementation Overview**

The implementation adheres to the following requirements:

1. Using aiortc built-in TcpSocketSignaling: The server creates an aiortc offer and sends it to the client. In response, the client generates an aiortc answer.

2. The server generates a continuous 2D image of a ball bouncing across the screen: This is achieved by the BallBounceTrack class in server.py.

3. Transmitting images to the client via aiortc using frame transport: This is implemented in the recv method of BallBounceTrack class. The server sends video frames to the client using the RTCPeerConnection addTrack method.

4. The client displays the received images using opencv: The client receives these video frames and displays them using OpenCV in the process_a function.

5. The client starts a new multiprocessing.Process (process_a): This process handles the image processing task, keeping the main client thread responsive.

6. Sending received frame to process_a using a multiprocessing.Queue: The recv_frames function in client.py receives the frames and puts them in the multiprocessing queue.

7. The client process_a parses the image and determines the current location of the x,y coordinates: This is done in the find_coordinates function, which is called by process_a.

8. Storing the computed x,y coordinate as a multiprocessing.Value: The coordinates are stored in a shared dictionary, which can be accessed from both the process_a and the main client thread.

9. The client opens an aiortc data channel to the server and sends each x,y coordinate to the server: The client creates a data channel in the run function, and the coordinates are sent to the server in the monitor_coordinates function.

10. The server displays the received coordinates and computes the error to the actual location of the ball: The server's on_message function receives the coordinates, calculates the error, and displays it. The actual location of the ball is maintained by the BallBounceTrack class.


**How to Run**

A short video has also been added, which has been as as Soumyajit_Ball Bouncing Track. On the video, it has been shown how you can perform the steps below for excuting the server.py, client.py and test_YOUR_SCRIPT.py files.

To run the application, start the server and client scripts.

for server go to server directory : `cd server`

In one terminal, start the server script:

`python server.py`

for client go to client directory: `cd client`

In a separate terminal, start the client script:

`python client.py`

The client will start receiving the video stream from the server, identify the ball within each frame, and send its coordinates back to the server. The server will calculate and print the difference between the actual and reported ball coordinates.


**Understanding the Code**

`server.py`:

* BallBounceTrack: A video track class that simulates a bouncing ball within a frame.

* run(): The main function that sets up the peer connection, starts the bouncing ball, and handles incoming data from the client.

`client.py`:

* find_coordinates(): Converts the frame to HSV color space to identify red color (the ball) and returns its center coordinates.

* process_a(): Processes each frame from the queue, displays the frame, and finds the ball coordinates.

* monitor_coordinates(): Continuously monitors and sends ball coordinates over the data channel.

* recv_frames(): Receives frames from the video track and puts them into a multiprocessing queue.

* run(): Handles the WebRTC peer connection, signaling, and data channel communication.

* The code can be easily modified to suit your needs. For example, you can adjust the HSV color thresholds to identify a different   color, adjust the ball size and speed, or add more sophisticated image processing to the client.


**Unit Tests**

A suite of unit tests are provided to ensure the correct operation of the ball tracking and communication components of this application. These tests include checking the ball tracking and generation, communication of data between the server and client, as well as the correct parsing of image frames by the client.

You can run these tests using the following command:

`pytest test_YOUR_SCRIPT.py`

Here are brief descriptions of each test function:

1. test_BallBounceTrack_init: Tests the initialization of the BallBounceTrack object.

2. test_BallBounceTrack_recv: Tests the recv method of the BallBounceTrack object.

3. test_find_coordinates_no_contours: Tests the find_coordinates function when no contours are present.

4. test_find_coordinates_with_contours: Tests the find_coordinates function when a contour is present.

5. test_find_coordinates_with_no_dot: Tests the find_coordinates function when no red dot is present.

6. test_find_coordinates_with_multiple_dots: Tests the find_coordinates function when multiple contours are present.

7. test_find_coordinates_with_non_square_frame: Tests the find_coordinates function when the frame is not square.

For more details about these tests, please refer to the docstrings in the test_YOUR_SCRIPT.py file.

Ensure that you have installed the pytest library before running the tests. If not, you can install it using pip:

`pip install pytest`


**Docker Compose Deployment**

To simplify the deployment process, we also provide a docker-compose.yml file that allows you to start both the server and client with a single command.

**Prerequisites**

Ensure you have Docker Compose installed on your machine.

**Using Docker Compose**

Once you have Docker Compose installed, navigate to the directory containing the docker-compose.yml file and run the following command:

`docker-compose up`


This will build and start both the server and the client. The client is set to depend on the server, so the server will start first.

The `docker-compose.yml` file is configured as follows:


version: '3'
services:
  server:
    build: server/
    command: python ./server.py
    ports:
      - "1234:1234"

  client:
    build: client/
    command: python ./client.py
    network_mode: host
    depends_on:
      - server


This configuration indicates that there are two services, server and client. The build context for each is set to their respective directories, and the command to start each service is provided. For the server, port 1234 is exposed and mapped to the host machine. The client is set to use the host's network stack, and it will not start until the server service has been started.

If you wish to stop the services, you can do so by running:

`docker-compose down`


**Docker Deployment**

This project can also be deployed using Docker. We provide two Dockerfiles, one for the client and one for the server. They include all necessary dependencies for running the application.

**Prerequisites**
Make sure you have Docker installed on your machine.

**Building Docker Images**
To build the Docker images for the server and the client, navigate to the respective directories and run the following commands:

For the `server`:

`docker build -t ball_tracker_server:latest .`

For the `client`:

`docker build -t ball_tracker_client:latest .`

**Running Docker Containers**

After building the images, you can start the server and client containers using the following commands:

For the `server`:

`docker run -p 1234:1234 ball_tracker_server:latest`

For the `client`:

`docker run -p 1234:1234 ball_tracker_client:latest`


The Docker images for both the client and server components of the application have been successfully created. For privacy and proprietary reasons, these images have not been pushed to a public repository like Docker Hub.

Instead, the Dockerfiles and the necessary code files to build the images are provided. Users can easily build the Docker images locally on their own systems. Here are the instructions to build the images:

1. Navigate to the project directory where the Dockerfiles are located.

2. Run the following command to build the Docker image for the server:
   
   `docker build -t your_server_image_name ./server/`

3. Then, build the Docker image for the client:
   
   `docker build -t your_client_image_name ./client/`

Replace your_server_image_name and your_client_image_name with names you want to give your Docker images.

Note: It's necessary to have Docker installed on your system to build and run Docker images. 

Once the images are built, you can use the Docker Compose file provided to run the multi-container application. Make sure to replace the image names in the Docker Compose file with the ones you have just created.

Lastly, due to the stipulation that solutions should not be publicly posted, please ensure that the Dockerfiles, code, and other related files remain confidential and are not shared publicly without permission.


**Limitation**

The application was tested and developed on a Windows 11 machine. This allowed the ball tracking video to be successfully displayed when running `client.py` and `server.py` in the terminal.

However, due to the isolation properties of Docker containers, the OpenCV GUI wasn't able to access the host's display server when running the application within Docker. As a result, the ball tracking video couldn't be displayed when running the application within a Docker container on a Windows host.

Moreover, since this application makes use of certain Linux-specific functionalities, it would not run as expected on a non-Linux system. Unfortunately, in this case, a Linux system was not available for testing and thus, this poses a known limitation for the application.

Lastly, this limitation also extends to the deployment on Kubernetes using Minikube as it was not possible to display the video in a container. However, please note that the video generation and computation of coordinates and errors have been verified to work correctly when the application is run directly in the terminal. 

Future work would include finding a solution to these GUI limitations when deploying within Docker containers or on Kubernetes.

The attached images in "Soumyajit" folder shows that the docker deployment for both client and server was successful. 
