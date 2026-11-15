"""Host diagnostics cannot silently change the owned execution context."""
import unittest
from tools.recomp_bulk_run import diagnostic_environment


class BulkRunEnvironmentTests(unittest.TestCase):
    def test_explicit_diagnostics_keep_values_without_shell_interpretation(self):
        self.assertEqual(diagnostic_environment(['LIBGL_DEBUG=verbose','LD_DEBUG=files']),
                         {'LIBGL_DEBUG':'verbose','LD_DEBUG':'files'})
        self.assertEqual(diagnostic_environment(['TEST_VALUE=a=b $literal']),{'TEST_VALUE':'a=b $literal'})

    def test_reserved_context_duplicate_and_malformed_settings_refuse(self):
        for values in (['WINEPREFIX=/tmp/other'],['RECOMP_INSTRUCTION_BUDGET=0'],['LD_DEBUG=files','LD_DEBUG=all'],['-e=bad'],['MISSING_EQUALS']):
            with self.assertRaises(ValueError):diagnostic_environment(values)
