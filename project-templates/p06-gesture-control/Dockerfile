FROM osrf/ros:humble-desktop-full

RUN apt-get update && apt-get install -y \
    python3-pip git vim x11-apps mesa-utils libgl1-mesa-glx ros-humble-cv-bridge \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir \
    numpy opencv-python pytest rich loguru \
    mediapipe opencv-python

WORKDIR /workspace
RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc \
 && echo "source /workspace/install/setup.bash 2>/dev/null || true" >> /root/.bashrc

ENV DISPLAY=:0 QT_X11_NO_MITSHM=1
CMD ["/bin/bash"]
