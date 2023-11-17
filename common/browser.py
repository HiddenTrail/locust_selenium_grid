from locust_plugins.users.webdriver import WebdriverUser
from locust_plugins.users.webdriver import WebdriverClient
from common.py_utils import get_selenium_grid_address
from common.py_utils import get_headless_selenium
from common.py_utils import get_selenium_browser
from selenium import webdriver
from locust import User
from selenium.webdriver.edge.options import Options
import time


class EdgeClient(webdriver.Remote):
    def __init__(self, user: User):
        # Copied from WebdriverClient using chrome options
        self.user = user
        options = Options()
        if self.user.headless:
            options.add_argument('--headless')
        for arg in [
            "--disable-translate",
            "--disable-extensions",
            "--disable-background-networking",
            "--safebrowsing-disable-auto-update",
            "--disable-sync",
            "--metrics-recording-only",
            "--disable-default-apps",
            "--no-first-run",
            "--disable-setuid-sandbox",
            "--hide-scrollbars",
            "--no-sandbox",
            "--no-zygote",
            "--autoplay-policy=no-user-gesture-required",
            "--disable-notifications",
            "--disable-logging",
            "--disable-permissions-api",
            "--ignore-certificate-errors",
        ]:
            options.add_argument(arg)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.capabilities["acceptInsecureCerts"] = True
        options.page_load_strategy = "eager"
        super().__init__(command_executor=self.user.command_executor, options=options)
        self.start_time = None
        time.sleep(1)
        self.command_executor._commands["SEND_COMMAND"] = ("POST", "/session/$sessionId/chromium/send_command")

    locust_find_element = WebdriverClient.locust_find_element


class BrowserUser(WebdriverUser):
    abstract = True
    browser = get_selenium_browser()
    command_executor = get_selenium_grid_address()
    headless = get_headless_selenium()
    instance_count = 0

    def __init__(self, parent):
        BrowserUser.instance_count += 1
        self.instance_number = BrowserUser.instance_count
        if BrowserUser.browser == "chrome":
            super().__init__(parent)
        else:
            super(WebdriverUser, self).__init__(parent)
            self.client = EdgeClient(self)
            time.sleep(1)


class LocalStorage:
    def __init__(self, driver: WebdriverClient) :
        self.driver = driver

    def __len__(self):
        return self.driver.execute_script("return window.localStorage.length;")

    def items(self) :
        return self.driver.execute_script( \
            "var ls = window.localStorage, items = {}; " \
            "for (var i = 0, k; i < ls.length; ++i) " \
            "  items[k = ls.key(i)] = ls.getItem(k); " \
            "return items; ")

    def keys(self) :
        return self.driver.execute_script( \
            "var ls = window.localStorage, keys = []; " \
            "for (var i = 0; i < ls.length; ++i) " \
            "  keys[i] = ls.key(i); " \
            "return keys; ")

    def get(self, key):
        return self.driver.execute_script("return window.localStorage.getItem(arguments[0]);", key)

    def set(self, key, value):
        self.driver.execute_script("window.localStorage.setItem(arguments[0], arguments[1]);", key, value)

    def has(self, key):
        return key in self.keys()

    def remove(self, key):
        self.driver.execute_script("window.localStorage.removeItem(arguments[0]);", key)

    def clear(self):
        self.driver.execute_script("window.localStorage.clear();")

    def __getitem__(self, key) :
        value = self.get(key)
        if value is None :
          raise KeyError(key)
        return value

    def __setitem__(self, key, value):
        self.set(key, value)

    def __contains__(self, key):
        return key in self.keys()

    def __iter__(self):
        return self.items().__iter__()

    def __repr__(self):
        return self.items().__str__()
