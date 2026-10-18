"""Common false-match controls, without per-game-function test artifacts."""
import unittest
from rapid_native.status_rules import classify
class StrictMatchRules(unittest.TestCase):
    def test_complete_exact_result(self):
        self.assertEqual(self.result(),'reccmp_matched')
    def result(self,**changes):
        value=dict(score=1.0,original_size=40,expected_size=40,recompiled_size=40,mapped=True,unknowns=[])
        value.update(changes);return classify(**value)
    def test_mutants_never_accept(self):
        for changes in [dict(score=.99999999),dict(score=None),dict(score=True),dict(original_size=20),dict(original_size=0,expected_size=0),dict(recompiled_size=0),dict(mapped=False),dict(unknowns=['missing_target']),dict(is_stub=True)]:
            with self.subTest(changes=changes):self.assertEqual(self.result(**changes),'retained_unmatched')
if __name__=='__main__':unittest.main()
