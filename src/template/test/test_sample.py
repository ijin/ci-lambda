import unittest, sys, commands, os
from mock import Mock, MagicMock, patch
from nose.tools import ok_, eq_, raises

git_root = commands.getoutput('git rev-parse --show-toplevel')
sys.path.insert(0, '%s/src' % git_root)

from template.sample import main as f

class Test(unittest.TestCase):
    def setUp(self):
        pass

    def test_adder(self):
        eq_(f(None, None), 'beta')

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
