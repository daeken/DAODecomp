"""Synthetic provider-policy tests; not game execution evidence."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools import incremental_checkpoint as cache


class BatchNativeProviderTests(unittest.TestCase):
    def test_declared_self_install_id_is_not_a_dependency(self):
        with tempfile.TemporaryDirectory() as temp:
            image = Path(temp).resolve()/'batch.dylib'
            image.write_bytes(b'unit fixture')
            def otool(argv, text):
                if argv[1] == '-D':
                    return str(image)+':\n@rpath/batch.dylib\n'
                return str(image)+':\n\t@rpath/batch.dylib (compatibility version 0.0.0)\n'
            with patch.object(cache.subprocess, 'check_output', side_effect=otool):
                self.assertEqual(cache.native_dependencies([image]), {'files': {}, 'bindings': {}})

    def test_actual_unresolved_rpath_dependency_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            image = Path(temp).resolve()/'batch.dylib'
            image.write_bytes(b'unit fixture')
            def otool(argv, text):
                if argv[1] == '-D':
                    return str(image)+':\n@rpath/batch.dylib\n'
                return str(image)+':\n\t@rpath/batch.dylib (compatibility version 0.0.0)\n\t@rpath/external.dylib (compatibility version 0.0.0)\n'
            with patch.object(cache.subprocess, 'check_output', side_effect=otool):
                with self.assertRaisesRegex(ValueError, 'unsupported native dependency'):
                    cache.native_dependencies([image])

    def test_unknown_install_identity_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            image = Path(temp).resolve()/'batch.dylib'
            image.write_bytes(b'unit fixture')
            with patch.object(cache.subprocess, 'check_output', return_value=str(image)+':\n'):
                with self.assertRaisesRegex(ValueError, 'unknown Mach-O install identity'):
                    cache.native_dependencies([image])
