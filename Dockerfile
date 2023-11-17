FROM python:3.11

ENV TEST_RUNNER_UID 1001
ENV TEST_RUNNER_GID 1001
ENV PERF_DIR /opt/locust
ENV PERF_WORK_DIR ${PERF_DIR}/temp
ENV PERF_TESTS_DIR ${PERF_DIR}/tests
ENV PYTHONPATH ${PYTHONPATH}:${PERF_TESTS_DIR}
ENV TZ Europe/Helsinki

RUN adduser \
    --disabled-password \
    --uid "${TEST_RUNNER_UID}" \
    "perfuser"

RUN mkdir -p ${PERF_WORK_DIR} \
    && mkdir -p ${PERF_TESTS_DIR} \
    && chown -R ${TEST_RUNNER_UID}:${TEST_RUNNER_GID} ${PERF_DIR} \
    && chmod -R ugo+w ${PERF_DIR}

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo ${TZ} > /etc/timezone

WORKDIR ${PERF_WORK_DIR}

COPY requirements.txt requirements.txt

RUN apt-get update && apt-get install -y --no-install-recommends \
    psmisc

USER perfuser

ENV PATH="/home/perfuser/.local/bin:${PATH}"

RUN pip3 install -r requirements.txt

WORKDIR ${PERF_TESTS_DIR}

CMD [ "locust -f locustfiles/web_user.py" ]
