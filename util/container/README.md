# HWPE Stream Docker Test Container
The dockerfile contains the build instructions for the container. It is compatible for cocotb and Verilator. 

## Alternative docker download
You can download an uploaded build by running: 
``` bash
docker pull rgantonio/cocotb-hwpe-stream
```

## How to use?
- Make sure to download the docker
- Make sure to clone the main hwpe-stream repo:
- Run the container and mount the hwpe-stream repo:
``` bash
docker run -it -v $HWPE_STREAM_ROOT/hwpe-stream:/repo -w repo rgantonio/cocotb-hwpe-stream
```

## TODO: Update the path later!