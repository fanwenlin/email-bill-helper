import unittest
from unittest.mock import patch, MagicMock
from table import search_records_by_unique_ids, client

class TestTableFunctions(unittest.TestCase):

    @patch('table.client.bitable.v1.app_table_record.list')
    def test_search_records_by_unique_ids(self, mock_list):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.data.items = [
            MagicMock(fields={'unique_id': '1920e1f4e7afa7e5_-7280173109224062088', 'other_field': 'value1'}),
            MagicMock(fields={'unique_id': '19208f9449de29b4_268986915717696844', 'other_field': 'value2'})
        ]
        mock_list.return_value = mock_response

        # Test data
        test_ids = ['1920e1f4e7afa7e5_-7280173109224062088', '19208f9449de29b4_268986915717696844', 'non_existent_id']

        # Call the function
        result = search_records_by_unique_ids(test_ids)

        # Assertions
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['unique_id'], '1920e1f4e7afa7e5_-7280173109224062088')
        self.assertEqual(result[1]['unique_id'], '19208f9449de29b4_268986915717696844')
        self.assertEqual(result[0]['other_field'], 'value1')
        self.assertEqual(result[1]['other_field'], 'value2')

        # Check if the API was called with the correct filter
        expected_filter = "OR(CurrentValue.[unique_id] = '1920e1f4e7afa7e5_-7280173109224062088'," \
                          "CurrentValue.[unique_id] = '19208f9449de29b4_268986915717696844'," \
                          "CurrentValue.[unique_id] = 'non_existent_id')"
        mock_list.assert_called_once()
        actual_filter = mock_list.call_args[0][0].filter
        self.assertEqual(actual_filter, expected_filter)

if __name__ == '__main__':
    unittest.main()