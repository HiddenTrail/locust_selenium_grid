# locust_selenium_grid
GUI Performance testing demo with Locust and Selenium Grid

Use https://www.saucedemo.com as the base URL for the tests.

## Installation

Use docker.

1. Install Docker
2. Run test (see below)
    - docker images are build if not already existing and the test is run inside a docker container

## Running the tests

Use the run_test.sh script to run the tests.

Script has a help option to list all the available options:
``` shell
./run_test.sh -h
```

### Example

Run "web_ui_example" web ui performance tests with chrome and iterate test 2 times:
``` shell
./run_test.sh -f locustfiles/web_ui_example.py -u https://www.saucedemo.com -x -i 2
```

Run "web_ui_example" web ui performance tests with edge. Scale selenium nodes to 3 and iterate each node 2 times (equals to 6 itearations):
``` shell
./run_test.sh -f locustfiles/web_ui_example.py -u https://www.saucedemo.com -b edge -x -i 6 -n 3
```
