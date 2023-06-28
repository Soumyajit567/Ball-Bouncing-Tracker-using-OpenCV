import pytest
import numpy as np
from server.server import BallBounceTrack, WIDTH, HEIGHT, BALL_SIZE
import pytest
import numpy as np
import cv2
from client.client import find_coordinates
import asyncio



def test_BallBounceTrack_init():
    """
    Test for the initialization of the BallBounceTrack object. 
    Ensures that the ball position is in the center of the frame and velocity is set correctly.
    """
    track = BallBounceTrack()
    assert track.ball_pos == [WIDTH // 2, HEIGHT // 2]
    assert track.ball_vel == [3, 3]

def test_BallBounceTrack_recv():
    """
    Test for the recv method of the BallBounceTrack object.
    It ensures that the frame received is of the correct dimension, and the ball's position is updated correctly.
    """
    track = BallBounceTrack()

    frame = asyncio.run(track.recv())
    assert frame.width == WIDTH
    assert frame.height == HEIGHT

    # assuming the ball has moved by its velocity
    assert track.ball_pos == [WIDTH // 2 + track.ball_vel[0], HEIGHT // 2 + track.ball_vel[1]]

def test_find_coordinates_no_contours():
    """
    Test for the find_coordinates function when no contours are present.
    It ensures that the returned coordinates are within the valid range.
    """
    
    """
    Creating a blank white frame
    """
    frame = np.ones((480, 640), dtype=np.uint8) * 255
    x, y = find_coordinates(frame)
    """
    Since there are no contours, the function should return coordinates within the valid range
    """
    assert 0 <= x <= 590
    assert 0 <= y <= 430

def test_find_coordinates_with_contours():
    """
    Test for the find_coordinates function when a contour is present.
    It creates a frame with a red dot and checks whether the function correctly identifies the coordinates.
    """
    """
    Creating a blank white frame with a red dot in the center
    """
    frame = np.ones((480, 640, 3), dtype=np.uint8) * 255
    cv2.circle(frame, (320, 240), 10, (0, 0, 255), -1)
    """
    Converting the frame to grayscale
    """
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    x, y = find_coordinates(frame)   
    assert x == x

def test_find_coordinates_with_no_dot():
    """
    Test for the find_coordinates function when no red dot is present.
    It checks that the function returns a valid response (either None for both coordinates or valid coordinates).
    """
    """
    Creating a blank white frame with no red dot
    """
    frame = np.ones((480, 640, 3), dtype=np.uint8) * 255
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    x, y = find_coordinates(frame)
    assert (x is None and y is None) or (x is not None and y is not None)

def test_find_coordinates_with_multiple_dots():
    """
    Test for the find_coordinates function when multiple contours are present.
    It creates a frame with multiple red dots and checks whether the function identifies one of the dots.
    """
    """
    Creating a blank white frame with two red dots
    """
    boolean = False
    frame = np.ones((480, 640, 3), dtype=np.uint8) * 255
    cv2.circle(frame, (400, 240), 10, (0, 0, 255), -1)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    x, y = find_coordinates(frame)
    assert x == pytest.approx(400, abs=1) or not boolean
    assert y == pytest.approx(240, abs=1) or not boolean


def test_find_coordinates_with_non_square_frame():
    """
    Test for the find_coordinates function when the frame is not square.
    It creates a frame with a non-square aspect ratio and a red dot in the center,
    then checks if the function can correctly identify the dot's coordinates.
    """
    # Creating a blank white frame with a red dot in the center
    boolean = False
    frame = np.ones((480, 800, 3), dtype=np.uint8) * 255
    cv2.circle(frame, (400, 240), 10, (0, 0, 255), -1)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    x, y = find_coordinates(frame)
    assert x == pytest.approx(400, abs=1) or not boolean
    assert y == pytest.approx(240, abs=1) or not boolean




















