# HWPE Stream Docker Test Container
The dockerfile contains the build instructions for the container. It is compatible for cocotb and Verilator. 

## Alternative Docker Download
You can download an uploaded build by running: 
``` bash
docker pull rgantonio/cocotb-hwpe-stream
```

## Using the Container
Run interactive container:

``` bash
docker run -it -v $REPO_TOP:/repo -w repo rgantonio/cocotb-hwpe-stream
```
**Note:** the `$REPO_TOP` is the cloned `hwpe-stream` top. For example, `$REPO_TOP=$HOME/hwpe-stream`.

## TODO: Update the path later!