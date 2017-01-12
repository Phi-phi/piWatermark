import io
import socket
import struct
import time
import picamera


# Connect a client socket to my_server:8000 (change my_server to the
# hostname of your server)
socket = socket.socket()
socket.bind(('0.0.0.0', 8000))
socket.listen(0)

# Make a file-like object out of the connection
connection = socket.accept()[0].makefile('wb')
try:
    with picamera.PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.framerate = 60
        # Start a preview and let the camera warm up for 2 seconds
        camera.start_preview()
        time.sleep(0.1)

        # Note the start time and construct a stream to hold image data
        # temporarily (we could write it directly to connection but in this
        # case we want to find out the size of each capture first to keep
        # our protocol simple)
        stream = io.BytesIO()
        for foo in camera.capture_continuous(stream, 'jpeg'):
            # Write the length of the capture to the stream and flush to
            # ensure it actually gets sent
            connection.write(struct.pack('<L', stream.tell()))
            connection.flush()
            # Rewind the stream and send the image data over the wire
            stream.seek(0)
            connection.write(stream.read())
            # Reset the stream for the next capture
            stream.seek(0)
            stream.truncate()
    # Write a length of zero to the stream to signal we're done
    connection.write(struct.pack('<L', 0))
finally:
    connection.close()
    socket.close()
