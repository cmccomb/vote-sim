from votesim import PreferenceProfile, RULES
import unittest


class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        self.P = votesim.PreferenceProfile()
        self.P.set_profile([
            ['a', 'b', 'c', 'd'],
            ['a', 'b', 'd', 'c'],
            ['a', 'b', 'd', 'c'],
            ['a', 'b', 'd', 'c'],
            ['a', 'd', 'c', 'b'],
            ['a', 'd', 'c', 'b'],
            ['a', 'b', 'c', 'd'],
            ['b', 'c', 'd', 'a'],
            ['a', 'b', 'c', 'd'],
            ['a', 'b', 'c', 'd'],
            ['b', 'a', 'c', 'd']
        ])

    def test_good_setup(self):
        self.assertEqual(self.P.m, 4)
        self.assertEqual(self.P.n, 11)

    def test_votes(self):
        for rule in votesim.RULES:
            self.assertEqual(rule(self.P.profile)[0], ['a', 'b', 'c', 'd'])

    def test_unanimity(self):
        for rule in votesim.RULES:
            self.assertEqual(self.P.unanimity(rule), True)

    def test_sp(self):
        for rule in votesim.RULES:
            self.assertEqual(self.P.strategyproof(rule), True)

    def test_random_setup(self):
        P = votesim.PreferenceProfile()
        P.make_random_profile(n=15, m=7)
        self.assertEqual(P.n, 15)
        self.assertEqual(P.m, 7)

if __name__ == "__main__":
    unittest.main()
