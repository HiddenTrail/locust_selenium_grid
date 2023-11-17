from locust_plugins.users.webdriver import WebdriverClient
from common import selenium_utils as s


class SwagLabsPage:
    def __init__(self, client: WebdriverClient, base_url, username, password, request):
        self.client = client
        self.base_url = base_url
        self.username = username
        self.password = password
        self.request = request
    
    def login(self):
        self.client.get(self.base_url)
        s.clear_local_storage(self.client)
        s.find_element_and_send_keys(self.client, '#user-name', self.username)
        s.find_element_and_send_keys(self.client, '#password', self.password)
        s.find_element_and_click(self.client, '#login-button')
        with self.request("login"):
            s.wait_until_element_is_visible(self.client, '#inventory_container')
    
    def add_item_to_cart(self, item):
        s.find_element_and_click(self.client, f'#add-to-cart-sauce-labs-{item}')
        s.find_element_and_click(self.client, '#shopping_cart_container')
        with self.request("add_to_cart"):
            s.wait_until_element_is_visible(self.client, '#cart_contents_container')
        s.find_element_and_click(self.client, '#continue-shopping')
