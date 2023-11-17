from datetime import datetime
from pathlib import Path
from typing import Literal
from locust_plugins.users.webdriver import WebdriverClient
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from typing import List
import logging
import gevent


default_timeout = 10
default_poll_frequency = 0.5


def take_screenshot(client, name, level=logging.DEBUG):
    if logging.root.level == level:
        now = datetime.now()
        screenshot_time = now.strftime("%Y-%m-%d_%H%M%S")
        filename = Path(__file__).parent.parent.absolute() / 'results' / f'{name}_{screenshot_time}.png'
        logging.debug(f'Taking screenshot to : {filename}')
        client.save_screenshot(filename)


def find_element_and_click(
        client: WebdriverClient,
        selector: str,
        selector_type: Literal['xpath', 'css']='css'
    ) -> WebElement:
    selector_model = _get_selector_model(selector_type)
    _wait_for_element(client, selector_model, selector)
    selenium_object = client.find_element(selector_model, selector).click()
    return selenium_object


def find_element_and_send_keys(
        client: WebdriverClient,
        selector: str,
        keys,
        clear=False,
        submit=False,
        selector_type: Literal['xpath', 'css']='css'
    ) -> WebElement:
    selector_model = _get_selector_model(selector_type)
    _wait_for_element(client, selector_model, selector)
    selenium_object = client.find_element(selector_model, selector)
    if clear:
        selenium_object.clear()
    selenium_object.send_keys(keys)
    if submit:
        selenium_object.submit()
    return selenium_object


def find_and_get_element(
        client: WebdriverClient,
        selector: str,
        selector_type: Literal['xpath', 'css']='css'
    ) -> WebElement:
    selector_model = _get_selector_model(selector_type)
    _wait_for_element(client, selector_model, selector)
    element = client.find_element(selector_model, selector)
    return element


def find_and_get_list_of_elements(
        client: WebdriverClient,
        selector: str,
        selector_type: Literal['xpath', 'css']='css'
    ) -> List[WebElement]:
    selector_model = _get_selector_model(selector_type)
    _wait_for_element(client, selector_model, selector)
    elements = client.find_elements(selector_model, selector)
    return elements


def select_option_by(
        client: WebdriverClient,
        selector: str,
        attribute: Literal['id', 'value', 'text'],
        value,
        selector_type: Literal['xpath', 'css']='css'
    ):
    selector_model = _get_selector_model(selector_type)
    _wait_for_element(client, selector_model, selector)
    select = Select(client.find_element(selector_model, selector))
    if attribute == 'id':
        select.select_by_index(value)
    if attribute == 'value':
        select.select_by_value(value)
    if attribute == 'text':
        select.select_by_visible_text(value)


def wait_until_element_is_visible(
    client: WebdriverClient,
    selector: str,
    timeout: float=5,
    poll_frequency: float=0.2,
    selector_type: Literal['xpath', 'css']='css',
    message=""
    ):
    selector_model = _get_selector_model(selector_type)
    wait = WebDriverWait(client, timeout=timeout, poll_frequency=poll_frequency)
    try:
        wait.until(EC.visibility_of_element_located((selector_model, selector)), message)
    except TimeoutException:
        take_screenshot(client, "Element_not_visible")
        raise TimeoutException(message)


def wait_until_element_is_not_visible(
    client: WebdriverClient,
    selector: str,
    timeout: float=5,
    poll_frequency: float=0.2,
    selector_type: Literal['xpath', 'css']='css',
    message=""
    ):
    selector_model = _get_selector_model(selector_type)
    wait = WebDriverWait(client, timeout=timeout, poll_frequency=poll_frequency)
    try:
        wait.until_not(EC.visibility_of_element_located((selector_model, selector)), message)
    except TimeoutException:
        take_screenshot(client, "Element_still_visible")
        raise TimeoutException(message)


def check_if_element_exists(client: WebdriverClient, selector, selector_type: Literal['xpath', 'css']='css'):
    selector_model = _get_selector_model(selector_type)
    try_time = 2
    poll_frequency = 0.1
    element_found = False
    loop_time = 0.0
    while loop_time < try_time and not element_found:
        try:
            client.find_element(selector_model, selector)
            element_found = True
        except NoSuchElementException:
            loop_time += poll_frequency
            gevent.sleep(poll_frequency)
    return element_found


def get_element_text(client: WebdriverClient, selector, selector_type: Literal['xpath', 'css']='css'):
    selector_model = _get_selector_model(selector_type)
    _wait_for_element(client, selector_model, selector)
    element_text = client.find_element(selector_model, selector).text
    return element_text


def clear_local_storage(client: WebdriverClient):
    client.execute_script("window.localStorage.clear();")


def _wait_for_element(client, selector_model, selector):
    wait = WebDriverWait(client, timeout=default_timeout, poll_frequency=default_poll_frequency)
    try:
        wait.until(EC.visibility_of_element_located((selector_model, selector)),
            f'Element {selector} did not appear within {default_timeout}')
    except TimeoutException:
        take_screenshot(client, "Could_not_find_element")
        raise TimeoutException(f'Element {selector} did not appear within {default_timeout}')


def _get_selector_model(selector_type):
    if selector_type == 'xpath':
        return By.XPATH
    if selector_type == 'css':
        return By.CSS_SELECTOR
