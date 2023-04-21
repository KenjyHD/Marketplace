"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread, Lock
import time

class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        super().__init__(**kwargs)
        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time
        self.kwargs = kwargs
        self.lock = Lock()

    def run(self):
        # Add new cart to marketplace
        cart_id = self.marketplace.new_cart()
        for cart in self.carts:
            for action in cart:
                # Add product to cart
                if action["type"] == "add":
                    for _ in range(action["quantity"]):
                        # Wait until the prduct is published
                        while not self.marketplace.add_to_cart(cart_id, action["product"]):
                            time.sleep(self.retry_wait_time)
                # Remove product from the cart
                else:
                    for _ in range(action["quantity"]):
                        self.marketplace.remove_from_cart(cart_id, action["product"])
        # Place the order and print information
        prod_list = self.marketplace.place_order(cart_id)
        with self.lock:
            for prod in prod_list:
                print(self.name, "bought", prod[0])
