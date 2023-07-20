# Cocotb Testing

## Guide notes

The cocotb tests uses pytest to run simulations and tests.

To run a specific test simply use:
``` bash
pytest <path_to_test_directory>/test.py
```
For example, the command below runs the split test.
``` bash
pytest basic/test/test_hwpe_stream_split.py
```
**Note:** If you switch the simulator from Verilator to Modelsim (or vice versa, or to any other simulator), make sure to remove the `__pycache__`, `.pytest_cache`, and `sim_build` directories. Just be sure to check the correct paths.

``` bash
rm -rf sim_build
rm -rf __pycache__
rm -rf .pytest_cache
```

## Test Descriptions

* `basic` - this directory consists of tests for the RTL files under `/rtl/basic`

    * `test_hwpe_stream_merge.py` - tests the `hwpe_stream_merge` module. Checks if the multiple inputs merge into a wider bus output. 
    * `test_hwpe_stream_split.py` - tests the `hwpe_stream_split` module. This is the opposite of merge. Checks if a wide bus input can be split evenly into multiple outputs.


