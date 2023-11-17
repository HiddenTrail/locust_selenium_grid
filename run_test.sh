#!/bin/bash

DATE=$(date +"%Y-%m-%d_%H-%M")
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
locust_file=""
base_url=""
browser="chrome"
delete_test_results=false
log_level="DEBUG"
results_file="results/${DATE}"
iterations=false
iteration_count="0"
headless="True"
xvfb=false
video=false
scale=false
nodes=1
shut_down=false


cd ${SCRIPT_DIR}

function delete_results() {
    echo "Removing testresults folder ${SCRIPT_DIR}/results"
    rm -rf results/*
}

function shutdown() {
  echo "Shutting down all docker containers"
  docker-compose down
  docker-compose -f selenium-grid.yml -p selenium-grid down
}

function run_tests() {
    export LOCUSTFILE=${locust_file}; export BASE_URL=${base_url}; export LOG_LEVEL=${log_level}
    export LOG_FILE_M="${results_file}/master_logfile.log"; export LOG_FILE_W="${results_file}/worker_logfile.log"
    export HEADLESS=${headless}; export START_XVFB=${xvfb}; export SELENIUM_BROWSER=${browser}
    shutdown
    local selenium_service="selenium-grid-chrome"
    if $video && [ "${browser}" == "chrome" ]; then
      selenium_service="chrome_video"
    elif $video && [ "${browser}" == "edge" ]; then
      selenium_service="edge_video"
    elif ! $video && [ "${browser}" == "edge" ]; then
      selenium_service="selenium-grid-edge"
    fi
    if ${scale} ; then
      selenium_service="--scale selenium-node-chrome=${nodes} selenium-node-chrome"
      if [ "${browser}" == "edge" ] ; then
        selenium_service="--scale selenium-node-edge=${nodes} selenium-node-edge"
      fi
    fi
    local locust_variables=""
    if ${iterations} ; then
      locust_variables="${locust_variables} -i ${iteration_count}"
      echo "Running ${iteration_count} iterations"
    fi
    export LOCUST_VARIABLES=${locust_variables}
    echo "Launching Selenium Grid: ${selenium_service} with options: xvfb=${xvfb}, video=${video}"
    docker-compose -f selenium-grid.yml -p selenium-grid up -d ${selenium_service}
    echo "Launching Locust with options: browser=${browser}, headless=${headless}"
    mkdir -p ${results_file} && docker-compose up
}


while getopts "f:u:b:dl:xvi:n:sh" opt; do
  case ${opt} in
    f )
      locust_file="${OPTARG}"
      ;;
    u )
      base_url="${OPTARG}"
      ;;
    b )
      browser="${OPTARG}"
      ;;
    d )
      delete_test_results=true
      ;;
    l )
      log_level="${OPTARG}"
      ;;
    x )
      headless="False"
      xvfb=true
      ;;
    v )
      video=true
      headless="False"
      xvfb=true
      ;;
    i )
      iteration_count="${OPTARG}"
      iterations=true
      ;;
    n )
      nodes="${OPTARG}"
      scale=true
      ;;
    s )
      shut_down=true
      ;;
    \? )
      echo "Invalid Option -${OPTARG}" >&2
      exit 1
      ;;
    : )
      echo "Option ${OPTARG} requires an argument" >&2
      exit 1
      ;;
    h|* )
      echo "Usage:"
      echo "-f    LOCUSTFILE. Default used: ${locust_file}"
      echo "-u    BASE_URL. Default is ${base_url}"
      echo "-b    Browser: chrome, edge. Default is ${browser}"
      echo "-d    Delete results. Default is ${delete_test_results}"
      echo "-l    loglevel. Default is ${log_level}"
      echo "-x    xvfb. Default is ${xvfb}"
      echo "-v    Video recording. Default is ${video}"
      echo "-i    iterations. Default is run until stopped."
      echo "-n    Nodes for selenium."
      echo "-h    Help"
      exit 0
      ;;
    esac
done

if $shut_down ; then
  shutdown
  exit 0
fi

if [ -z "${locust_file}" ] || [ -z "${base_url}" ]; then
  echo "Missing required arguments -f and -u"
  exit 1
fi

if $delete_test_results ; then
  delete_results
fi

run_tests
