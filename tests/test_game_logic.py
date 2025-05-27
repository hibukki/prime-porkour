import unittest
import sys
import os

# Add the parent directory to the Python path to allow importing main
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import is_prime  # Assuming main.py is in the parent directory


class TestIsPrime(unittest.TestCase):
    def test_prime_numbers(self):
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 97]
        for p in primes:
            with self.subTest(prime=p):
                self.assertTrue(is_prime(p), f"{p} should be prime")

    def test_non_prime_numbers(self):
        non_primes = [0, 1, 4, 6, 8, 9, 10, 12, 15, 20, 100]
        for np in non_primes:
            with self.subTest(non_prime=np):
                self.assertFalse(is_prime(np), f"{np} should not be prime")

    def test_negative_numbers(self):
        self.assertFalse(is_prime(-1))
        self.assertFalse(is_prime(-5))


if __name__ == "__main__":
    unittest.main()
