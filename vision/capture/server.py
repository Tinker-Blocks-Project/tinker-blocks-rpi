from flask import Flask, jsonify, send_file
import cv2
import depthai as dai
import time
import os

app = Flask(__name__)
SAVE_DIR = "assets"
os.makedirs(SAVE_DIR, exist_ok=True)


def capture_image():
    pipeline = dai.Pipeline()

    camRgb = pipeline.create(dai.node.ColorCamera)
    xoutVideo = pipeline.create(dai.node.XLinkOut)
    xoutVideo.setStreamName("video")

    camRgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)
    camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    camRgb.initialControl.setAutoFocusMode(dai.CameraControl.AutoFocusMode.AUTO)
    camRgb.setVideoSize(1920, 1080)

    xoutVideo.input.setBlocking(False)
    xoutVideo.input.setQueueSize(1)
    camRgb.video.link(xoutVideo.input)

    with dai.Device(pipeline) as device:
        video = device.getOutputQueue(name="video", maxSize=1, blocking=False)  # type: ignore
        time.sleep(2)

        for _ in range(10):
            video.tryGet()

        videoIn = video.get()
        frame = videoIn.getCvFrame()

        filename = os.path.join(SAVE_DIR, "captured_frame.jpg")
        cv2.imwrite(filename, frame)
        return filename


@app.route("/capture", methods=["GET"])
def capture():
    try:
        img_path = capture_image()
        return send_file(img_path, mimetype="image/jpeg")
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
