import os

import gevent
import locust
import pytest
from gevent import time
from locust import between
from locust.env import Environment
from locust.stats import stats_history, stats_printer, StatsCSVFileWriter

from config.consts import TEST_SYMBOL
from helpers.generators import generate_values
from main import LOG
from sender import Sender


@pytest.fixture(scope='session', autouse=True)
def generate_data():
    """
    Fixture that generates random trading data for a given `k` value.
    """
    Sender.clear_db()
    k = 8  # Retrieve the current k value from the param
    num_values = 10 ** k

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

    @locust.task
    def get_stats(self):
        """
        Send GET requests to the /stats endpoint for different values of 'k'.
        The number of requests is based on the weight assigned in the @task decorator.
        """
        k_value = 8
        self.client.get(f"/stats?symbol={TEST_SYMBOL}&k={k_value}")
        time.sleep(1)  # Pause to simulate realistic user wait times between requests


class LoadTest(locust.HttpUser):
    tasks = [UsersTest]
    host = "http://localhost:8000"
    wait_time = between(1, 3)


def test_locust_load_stats():
    # setup Environment and Runner
    env = Environment(user_classes=[LoadTest], events=locust.events)
    runner = env.create_local_runner()

    stats_path = os.path.join(os.getcwd(), "load_logs")
    csv_writer = StatsCSVFileWriter(
        environment=env,
        base_filepath=stats_path,
        full_history=True,
        percentiles_to_report=[90.0, 95.0]
    )
    gevent.spawn(csv_writer)

    # start a WebUI instance
    web_ui = env.create_web_ui("127.0.0.1", 8089)

    # execute init event handlers (only really needed if you have registered any)
    env.events.init.fire(environment=env, runner=runner, web_ui=web_ui)

    # start a greenlet that periodically outputs the current stats
    gevent.spawn(stats_printer(env.stats))

    # start a greenlet that save current stats to history
    gevent.spawn(stats_history, env.runner)

    # start the test
    runner.start(user_count=100, spawn_rate=10)

    # in 30 seconds stop the runner
    gevent.spawn_later(300, runner.quit)

    # wait for the greenlets
    runner.greenlet.join()

    # stop the web server for good measures
    # web_ui.stop()
