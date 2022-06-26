WORKSPACE=$HOME
JETBOT_CAMERA=${2:-opencv_gst_camera}

# set default swap limit as unlimited
export JETBOT_JUPYTER_MEMORY_SWAP=-1

sudo docker run -it -d \
            --restart always \
	    --runtime nvidia \
	    --network host \
	    --privileged \
	    --device /dev/video* \
	    --volume /dev/bus/usb:/dev/bus/usb \
	    --volume /tmp/argus_socket:/tmp/argus_socket \
	    -p 8888:8888 \
	    -v $WORKSPACE:/workspace \
	    --workdir /workspace \
	    --name=jetbot_inference \
	    --memory-swap=$JETBOT_JUPYTER_MEMORY_SWAP \
	    --env JETBOT_DEFAULT_CAMERA=$JETBOT_CAMERA \
	    jetbot_inference
