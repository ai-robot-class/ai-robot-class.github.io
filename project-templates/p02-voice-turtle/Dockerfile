FROM osrf/ros:humble-desktop-full

RUN apt-get update && apt-get install -y \
    python3-pip git vim wget curl x11-apps mesa-utils libgl1-mesa-glx ros-humble-turtlesim portaudio19-dev libsndfile1 ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir \
    numpy opencv-python pytest rich loguru \
    speech_recognition vosk pyttsx3 gtts librosa imageio[ffmpeg]

WORKDIR /workspace
RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc \
 && echo "source /workspace/install/setup.bash 2>/dev/null || true" >> /root/.bashrc

ENV DISPLAY=:0 QT_X11_NO_MITSHM=1
CMD ["/bin/bash"]
