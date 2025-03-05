"""
Simple sanity check test to verify pytest is working.
"""
import unittest


class TestSimple(unittest.TestCase):
    """Simple test cases to verify testing environment."""
    
    def test_addition(self):
        """Test basic addition."""
        self.assertEqual(1 + 1, 2)
    
    def test_string_concatenation(self):
        """Test string concatenation."""
        self.assertEqual("Hello " + "World", "Hello World")
    
    def test_boolean_operations(self):
        """Test boolean operations."""
        self.assertTrue(True)
        self.assertFalse(False)
        self.assertEqual(True and True, True)
        self.assertEqual(True or False, True)


if __name__ == '__main__':
    unittest.main()