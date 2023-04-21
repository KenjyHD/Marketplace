"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Lock
import logging.handlers
import time
import unittest

class TestStringMethods(unittest.TestCase):
    """
    Class that tests Marketplace class methods
    """
    def setUp(self):
        """
        Method to set up data for tests
        """
        self.market = Marketplace(10)
        self.prod1 = "Coffee(name='Brasil', price=7, acidity=5.09, roast_level='MEDIUM')"
        self.prod2 = "Tea(name='Wild Cherry', price=5, type='Black')"

    def test_register_producer(self):
        """
        Method to test register_producer method
        """
        self.assertEqual(self.market.register_producer(), 0)
        self.assertEqual(self.market.register_producer(), 1)

    def test_publish(self):
        """
        Method to test publish method
        """
        producer_id = self.market.register_producer()
        self.assertEqual(self.market.publish(producer_id, self.prod1), True)
        self.assertEqual(self.market.producers[producer_id][0], self.prod1)
        self.assertEqual(self.market.publish(producer_id, self.prod2), True)
        self.assertEqual(self.market.producers[producer_id][1], self.prod2)

        producer_id = self.market.register_producer()
        self.assertEqual(self.market.publish(producer_id, self.prod1), True)
        self.assertEqual(self.market.producers[producer_id][0], self.prod1)
        self.assertEqual(self.market.publish(producer_id, self.prod2), True)
        self.assertEqual(self.market.producers[producer_id][1], self.prod2)

    def test_new_cart(self):
        """
        Method to test new_cart method
        """
        self.assertEqual(self.market.new_cart(), 0)
        self.assertEqual(self.market.new_cart(), 1)

    def test_add_to_cart(self):
        """
        Method to test add_to_cart method
        """
        cart_id = self.market.new_cart()
        self.market.publish(self.market.register_producer(), self.prod1)
        self.market.publish(self.market.register_producer(), self.prod2)

        self.assertEqual(self.market.add_to_cart(cart_id, self.prod1), True)
        self.assertEqual(len(self.market.producers[0]), 0)
        self.assertEqual(self.market.carts[cart_id][0][0], self.prod1)

        self.assertEqual(self.market.add_to_cart(cart_id, self.prod2), True)
        self.assertEqual(len(self.market.producers[1]), 0)
        self.assertEqual(self.market.carts[cart_id][1][0], self.prod2)

    def test_remove_from_cart(self):
        """
        Method to test remove_from_cart method
        """
        cart_id = self.market.new_cart()
        self.market.publish(self.market.register_producer(), self.prod1)
        self.market.publish(self.market.register_producer(), self.prod2)
        self.market.add_to_cart(cart_id, self.prod1)
        self.market.add_to_cart(cart_id, self.prod2)

        self.market.remove_from_cart(cart_id, self.prod1)
        self.assertEqual(self.market.producers[0][0], self.prod1)
        self.assertEqual(len(self.market.carts[cart_id]), 1)

        self.market.remove_from_cart(cart_id, self.prod2)
        self.assertEqual(self.market.producers[1][0], self.prod2)
        self.assertEqual(len(self.market.carts[cart_id]), 0)

    def test_place_order(self):
        """
        Method to test place_order method
        """
        cart_id = self.market.new_cart()
        self.market.publish(self.market.register_producer(), self.prod1)
        self.market.publish(self.market.register_producer(), self.prod2)
        self.market.add_to_cart(cart_id, self.prod1)
        self.market.add_to_cart(cart_id, self.prod2)

        self.assertEqual(self.market.place_order(cart_id), self.market.carts[cart_id])

class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """
    def __init__(self, queue_size_per_producer):
        """
        Constructor
        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        self.queue_size_per_producer = queue_size_per_producer
        # Dictionary for the producers to keep track of what they produce
        self.producers = {}
        # Dictionary for carts to keep track of what consumers want to buy
        self.carts = {}
        # Locks used for each needed method respectively
        self.lock_add_cart = Lock()
        self.lock_publish = Lock()
        self.lock_reg_prod = Lock()
        self.lock_new_cart = Lock()
        # Format the logger output
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        formatter.convertor = time.gmtime
        # Set RotatingFileHandler for logger
        rfh = logging.handlers.RotatingFileHandler('maketplace.log')
        rfh.setFormatter(formatter)
        rfh.backupCount = 5
        rfh.maxBytes = 1000000
        # Set the logger
        self.logger = logging.getLogger('marketplace_log')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(rfh)

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        # Register a single producer at the same time
        with self.lock_reg_prod:
            producer_id = len(self.producers)
            # Expand the dictionary of producers
            self.producers[producer_id] = []

        self.logger.info("New producer with id: %d", producer_id)
        return producer_id

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace
        :type producer_id: String
        :param producer_id: producer id
        :type product: Product
        :param product: the Product that will be published in the Marketplace
        :returns True or False. If the caller receives False, it should wait and then try again.
        """
        self.logger.info("Producer %d published %s", producer_id, product)
        # A single producer publish at same time
        with self.lock_publish:
            # Verify the len for the producer queue
            if len(self.producers[producer_id]) < self.queue_size_per_producer:
                self.producers[producer_id].append(product)
                return True
        return False

    def new_cart(self):
        """
        Creates a new cart for the consumer
        :returns an int representing the cart_id
        """
        # Register a single new cart at the same time
        with self.lock_new_cart:
            # Expand the carts' dictionary
            cart_id = len(self.carts)
            self.carts[cart_id] = []
        self.logger.info("New cart with id: %d", cart_id)
        return cart_id

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns
        :type cart_id: Int
        :param cart_id: id cart
        :type product: Product
        :param product: the product to add to cart
        :returns True or False. If the caller receives False, it should wait and then try again
        """
        self.logger.info("%s added to cart %d", product, cart_id)
        # A single consumer adds to cart at the same time
        with self.lock_add_cart:
            for key in sorted(self.producers):
                for prod in self.producers[key]:
                    # Found the desired product, add to cart
                    if prod == product:
                        self.producers[key].remove(prod)
                        self.carts[cart_id].append([prod, key])
                        return True
        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.
        :type cart_id: Int
        :param cart_id: id cart
        :type product: Product
        :param product: the product to remove from cart
        """
        self.logger.info("%s removed from cart %d", product, cart_id)
        for prod, id_prod in self.carts[cart_id]:
            # Found the product, remove it from cart
            if prod == product:
                self.carts[cart_id].remove([product, id_prod])
                self.producers[id_prod].append(product)
                return

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.
        :type cart_id: Int
        :param cart_id: id cart
        """
        self.logger.info("Cart %d placed order", cart_id)
        return self.carts[cart_id]
