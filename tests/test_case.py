from tests.crud_functions import *
from mongoengine.connection import get_connection
import unittest
import sure

class MongoTestRunner(unittest.TestCase):
    
    def tearDown(self):
        connection = get_connection()
        connection.drop_database('tsunapper')
