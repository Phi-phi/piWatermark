import io
import sys
import cv2
import socket
import struct
import numpy
from PIL import Image

# Start a socket listening for connections on 0.0.0.0:8000 (0.0.0.0 means
# all interfaces)
addr = sys.argv[1]
port = sys.argv[2]

socket = socket.socket()
socket.connect((addr, int(port)))

# Accept a single connection and make a file-like object out of it
connection = socket.makefile("rb")

try:
    while True:
        # Read the length of the image as a 32-bit unsigned int. If the
        # length is zero, quit the loop
        image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
        if not image_len:
            break
        # Construct a stream to hold the image data and read the image
        # data from the connection
        image_stream = io.BytesIO()
        image_stream.write(connection.read(image_len))
        # Rewind the stream, open it as an image with PIL and do some
        # processing on it
        image_stream.seek(0)
        image = Image.open(image_stream)
        print('Image is %dx%d' % image.size)
        image.verify()
        print('Image is verified')
        cv2.imshow('frame', numpy.asarray(image))
finally:
    connection.close()
    socket.close()
