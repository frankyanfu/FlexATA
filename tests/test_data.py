import unittest
import pandas as pd
from FlexATA.form_builder import FormBuilder
from FlexATA.utility import read_in_data


class TestData(unittest.TestCase):

    def test_read_in_sample_item_pool(self):
        
        item_pool = read_in_data(data_name="pool")
        self.assertEqual(len(item_pool), 4998)

    def test_read_in_enemy_pair_file(self):
        
        enemy_pairs = read_in_data(data_name="enemy")
        self.assertEqual(len(enemy_pairs), 7296)

if __name__ == '__main__':
    unittest.main()