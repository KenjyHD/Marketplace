"""
This module represents the Producer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
import time

class Producer(Thread):
    """
    Class that represents a producer.
    """

    def __init__(self, products, marketplace, republish_wait_time, **kwargs):
        """
        Constructor.
        @type products: List()
        @param products: a list of products that the producer will produce
        @type marketplace: Marketplace
        @param marketplace: a reference to the marketplace
        @type republish_wait_time: Time
        @param republish_wait_time: the number of seconds that a producer must
        wait until the marketplace becomes available
        @type kwargs:
        @param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)
        self.products = products
        self.marketplace = marketplace
        self.republish_wait_time = republish_wait_time
        self.kwargs = kwargs

    def run(self):
        while True:
            # Register the producer
            producer_id = self.marketplace.register_producer()
            for prod in self.products:
                for _ in range(prod[1]):
                    # Wait until the product is published to markeplace
                    while not self.marketplace.publish(producer_id, prod[0]):
                        time.sleep(self.republish_wait_time)
                    # Wait for product
                    time.sleep(prod[2])
