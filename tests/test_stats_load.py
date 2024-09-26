import os

import gevent
import locust
import pytest
from gevent import time
from locust import between
from locust.env import Environment
from locust.stats import stats_history, stats_printer, StatsCSVFileWriter

from config.consts import TEST_SYMBOL, MAX_K_VALUE, MAX_TRADE_POINTS_COUNT
from helpers.generators import generate_values
from main import LOG
from sender import Sender


@pytest.fixture(scope='session', autouse=True)
def generate_data():
    """
    Fixture that generates random trading data for a given `k` value.
    """
    Sender.clear_db()
    num_values = 10 ** MAX_K_VALUE

    # Using a generator to create values
    values = generate_values(num_values)
    LOG.info("Started Test setup")
    Sender.send_add_batch_data_in_chunks(symbol=TEST_SYMBOL, generated_data=values)
    LOG.info("Test setup done")


class UsersTest(locust.TaskSet):
    """
    Define user behavior for load testing. This class contains tasks that simulate
    user interactions with the API endpoints, such as getting statistics and adding batches.
    """

    @locust.task(100)
    def get_stats(self):
        """
        Send GET requests to the /stats endpoint for different values of 'k'.
        The number of requests is based on the weight assigned in the @task decorator.
        """
        self.client.get(f"/stats?symbol={TEST_SYMBOL}&k={MAX_K_VALUE}")
        time.sleep(1)  # Pause to simulate realistic user wait times between requests

    @locust.task(1)
    def add_batch(self):
        """
        Add more data to be sure it doesn't have much impact on performance (avg response time should be pretty stable).
        :return:
        """
        values = generate_values(MAX_TRADE_POINTS_COUNT)
        self.client.post("/add_batch", json={"symbol": TEST_SYMBOL, "values": list(values)})


class LoadTest(locust.HttpUser):
    tasks = [UsersTest]
    host = "http://localhost:8000"
    wait_time = between(1, 3)


@pytest.mark.load
def test_locust_load_stats():
    """
    This test uses Locust to perform a load test on the /stats endpoint. It simulates multiple
    users making requests to the API and tracks how the response time changes as the number of
    requests and data points increases.

    Key points of the test:
    - The test simulates 100 concurrent users interacting with the API, sending requests to the
      /stats endpoint and adding batches of data.
    - The test dynamically spawns users at a rate of 10 new users per second.
    - The simulated user behavior includes sending GET requests to retrieve statistics for a symbol
      and sending POST requests to add new batches of trading data.
    - Each user also add some new data to the system (1 POST request to /add_batch after  10 GET /stats requests)
    - The test collects performance data (such as response times and request rates) and stores it
      in CSV format. This data is periodically saved to disk for analysis.
    - The WebUI is started to monitor real-time statistics during the test.
    - After 30 minutes of testing, the load test automatically stops.

    Test workflow:
    1. Setup the Locust environment, including starting the runner and WebUI.
    2. Simulate user interactions with the API, where the majority of interactions (weight 10)
       involve sending requests to the /stats and /add_batch endpoints (increasing database load).
    3. Collect performance metrics and save them to CSV files.
    4. After 5 minutes, stop the load test and finalize the results.

    This test helps evaluate the scalability of the /stats endpoint and observe how the
    system performs under high load, with special attention to response time as the
    number of data points and concurrent users increases.
    """
    # setup Environment and Runner
    env = Environment(user_classes=[LoadTest], events=locust.events)
    runner = env.create_local_runner()

    stats_path = os.path.join(os.getcwd(), "load_logs")
    csv_writer = StatsCSVFileWriter(
        environment=env,
        base_filepath=stats_path,
        full_history=True,
        percentiles_to_report=[10.0, 90.0]
    )
    gevent.spawn(csv_writer)

    # start a WebUI instance
    web_ui = env.create_web_ui("127.0.0.1", 8089)

    # execute init event handlers (only really needed if you have registered any)
    env.events.init.fire(environment=env, runner=runner, web_ui=web_ui)

    # start a greenlet that periodically outputs the current stats
    gevent.spawn(stats_printer(env.stats))

    # start a greenlet that saves current stats to history
    gevent.spawn(stats_history, env.runner)

    # start the test
    runner.start(user_count=100, spawn_rate=10)

    # in 5 minutes stop the runner
    gevent.spawn_later(300, runner.quit)

    # wait for the greenlets
    runner.greenlet.join()

    # stop the web server for good measure
    # web_ui.stop()
