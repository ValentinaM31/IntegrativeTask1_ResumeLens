"""Bounded retries for transient Windows locks without hiding persistent failures."""
import unittest
from unittest.mock import patch
from resumelens.workflow import _replace_file


def locked_file(code=32):
    error = PermissionError('Simulated Windows lock')
    error.winerror = code
    return error


class WindowsFileLockTests(unittest.TestCase):
    def test_transient_lock_retries_the_same_replacement(self):
        with patch('resumelens.workflow.os.replace', side_effect=[locked_file(), locked_file(5), None]) as replace:
            with patch('resumelens.workflow.time.sleep') as sleep:
                _replace_file('prepared.json', 'report.json')
        self.assertEqual(replace.call_count, 3)
        self.assertTrue(all(call.args == ('prepared.json', 'report.json') for call in replace.call_args_list))
        self.assertEqual(sleep.call_count, 2)

    def test_persistent_denial_is_bounded_and_raised(self):
        error = locked_file(5)
        with patch('resumelens.workflow.os.replace', side_effect=error) as replace:
            with patch('resumelens.workflow.time.sleep') as sleep:
                with self.assertRaises(PermissionError) as caught:
                    _replace_file('prepared.json', 'report.json')
        self.assertIs(caught.exception, error)
        self.assertEqual(replace.call_count, 6)
        self.assertEqual(sleep.call_count, 5)
        self.assertLess(sum(call.args[0] for call in sleep.call_args_list), 1)

    def test_unrelated_permission_errors_are_not_retried(self):
        with patch('resumelens.workflow.os.replace', side_effect=PermissionError('Persistent platform error')) as replace:
            with patch('resumelens.workflow.time.sleep') as sleep:
                with self.assertRaises(PermissionError):
                    _replace_file('prepared.json', 'report.json')
        self.assertEqual(replace.call_count, 1)
        sleep.assert_not_called()
