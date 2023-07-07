# Cocotb Testing

## Guide notes

1. The `Makefile` given has a list of commands to run tests in this directory. Run `make help` to list available commands.
2. Keep tests in this directory. Make sure tests begin with `test_` prefix so that pytest can search and run these tests automatically.
3. The `src_sanity_check` directory is only for testing purposes in CI.
4. By default, all files run using `verilator`. You can change the simulator in each test.


To run tests simply use:
``` bash
make test test_name=path_name
```
For example:
``` bash
make test-log test_name=src_sanity_check/test_sanity_check.py
```
To run multiple tests:
``` bash
make run-all
```

## Test Descriptions

* `test_sanity_check.py` - tests the simple counter in `src_sanity_check` directory. Use this to check and see if cocotb runs properly.


