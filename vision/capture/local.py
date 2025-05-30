import cv2
import depthai as dai
import time
import os


def capture_image():
    # Create pipeline
    pipeline = dai.Pipeline()

    # Define source and output
    camRgb = pipeline.create(dai.node.ColorCamera)
    xoutVideo = pipeline.create(dai.node.XLinkOut)

    xoutVideo.setStreamName("video")

    # Properties
    camRgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)
    camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    camRgb.initialControl.setAutoFocusMode(dai.CameraControl.AutoFocusMode.AUTO)
    camRgb.setVideoSize(1920, 1080)

    xoutVideo.input.setBlocking(False)
    xoutVideo.input.setQueueSize(1)

    # Linking
    camRgb.video.link(xoutVideo.input)

    # Connect to device and start pipeline
    with dai.Device(pipeline) as device:
        video = device.getOutputQueue(name="video", maxSize=1, blocking=False)  # type: ignore

        print("Warming up camera for 2 seconds...")
        time.sleep(2)  # let autofocus & white balance settle

        # Capture several frames to let the camera stabilize
        for _ in range(10):
            video.tryGet()  # discard initial frames

        # Now capture and save the image
        for i in range(1):
            videoIn = video.get()
            frame = videoIn.getCvFrame()
            filename = os.path.join("assets", f"frame_05{i}.jpg")
            cv2.imwrite(filename, frame)
            print("Frame saved as", filename)
            return f"frame_05{i}.jpg"
        # Optional: Show the frame
        # cv2.imshow("Captured", frame)
        # cv2.waitKey(0)

    cv2.destroyAllWindows()
