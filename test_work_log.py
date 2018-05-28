import unittest
from unittest.mock import patch
# (see: https://dev.to/patrnk/how-to-test-input-processing-in-python-3)

import work_log


class MenuTests(unittest.TestCase):

    # Helper Methods
    # --------------

    # Setup and Teardown
    # ------------------
    def setUp(self):
        self.menu = work_log.Menu(load_menu=False)
    
    def tearDown(self):
        pass
    
    # Example Tests
    # -------------
    def test_five_plus_five(self):
        assert 5 + 5 == 10
    
    def test_one_plus_one(self):
        assert not 1 + 1 == 3

    # Actual Tests
    # ------------

    # main_menu
    def test_main_menu_add_entry_returns_add_entry(self):
        """Ensure that the main menu loads the correct menu in response to
        user input."""
        user_inputs = {
            'a': self.menu.add_entry,
            's': self.menu.search_entries,
            'o': self.menu.options,
            'q': self.menu.quit_program,
        }
        results = []
        expected_results = []
        for key, value in user_inputs.items():
            expected_results.append(value)
            with patch('builtins.input', side_effect=key):
                results.append(self.menu.main_menu())
        
        self.assertEqual(expected_results, results)

    # add_entry

    # options

    # search_entries

    # quit_program

    # present_results

    # present_next_result

    # search_employee

    # search_employee_text

    # search_exact_date

    # search_date_range

    # search_time_spent

    # search_text_search

    # edit_record

    # edit_current_record

    # select_detail

    # delete_record

    # delete_current_record

    # display_entry

    # previous_result

    # next_result

    # previous_page

    # next_page

    # validate_date_entry

    # date_entry

    # date_to_string

# ------------------------

if __name__ == "__main__":
    unittest.main()