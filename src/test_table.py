import unittest
from .table import search_records_by_unique_ids

class TestTableFunctions(unittest.TestCase):

    def test_search_records_by_unique_ids(self):
        # Test data
        test_ids = ['1920e1f4e7afa7e5_-7280173109224062088', '19208f9449de29b4_268986915717696844', 'non_existent_id']

        # Call the function
        result = search_records_by_unique_ids(test_ids)

        # Assertions
        self.assertIsInstance(result, list)
        
        for record in result:
            self.assertIn('unique_id', record)
            self.assertIn(record['unique_id'][0]['text'], test_ids)
        
        # Check if we got results for existing IDs
        found_ids = [record['unique_id'][0]['text'] for record in result]
        self.assertIn('1920e1f4e7afa7e5_-7280173109224062088', found_ids)
        self.assertIn('19208f9449de29b4_268986915717696844', found_ids)
        
        # Check that non-existent ID is not in the result
        self.assertNotIn('non_existent_id', found_ids)

        # Print the results for manual verification
        print(f"Found {len(result)} records:")
        for record in result:
            print(f"ID: {record['unique_id']}")
            for key, value in record.items():
                if key != 'unique_id':
                    print(f"  {key}: {value}")
            print()

if __name__ == '__main__':
    unittest.main()