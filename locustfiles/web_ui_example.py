from common.py_utils import get_userdata_dict
from common.py_utils import get_selenium_grid_address
from common.py_utils import get_headless_selenium
from locust import task, constant, events
from common.browser import BrowserUser
from locust_plugins.listeners import RescheduleTaskOnFail
from browserapp.swag_labs_page import SwagLabsPage
import gevent


class CreateTests(BrowserUser):
    wait_time = constant(2)
    headless = get_headless_selenium()
    command_executor = get_selenium_grid_address()

    def on_start(self):
        self.client.set_window_size(1920, 1080)
        user_data = get_userdata_dict()
        self.username = user_data["username"]
        self.password = user_data["password"]
        self.browser_user = SwagLabsPage(
            self.client, 
            self.host,
            self.username,
            self.password,
            self.request
        )

    @task
    def demo_task(self):
        self._setup()
        self.browser_user.add_item_to_cart('backpack')
        gevent.sleep(10)

    def _setup(self):
        self.clear()
        self.browser_user.login()


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    RescheduleTaskOnFail(environment)
