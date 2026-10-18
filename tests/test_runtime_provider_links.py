import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools import incremental_checkpoint as cache


class RuntimeProviderLinksTests(unittest.TestCase):
    def test_runtime_link_is_resolved_and_bound_but_candidate_links_stay_forbidden(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / 'provider'
            target.write_bytes(b'original')
            link = root / 'lookup'
            link.symlink_to(target)
            files, bindings = cache.resolved_provider_files([link])
            self.assertEqual(files, {str(target.resolve()): cache.file_hash(target)})
            self.assertEqual(bindings, {str(link.absolute()): str(target.resolve())})
            with self.assertRaises(ValueError):
                cache.files_manifest([link])
            target.write_bytes(b'changed')
            self.assertNotEqual(files, cache.resolved_provider_files([link])[0])
            other = root / 'other'
            other.write_bytes(b'changed')
            link.unlink()
            link.symlink_to(other)
            self.assertNotEqual(bindings, cache.resolved_provider_files([link])[1])
            other.unlink()
            with self.assertRaises(FileNotFoundError):
                cache.resolved_provider_files([link])

    def test_retarget_during_hashing_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first, second, link = (root / name for name in ('first', 'second', 'lookup'))
            first.write_bytes(b'same')
            second.write_bytes(b'same')
            link.symlink_to(first)
            original_hash = cache.file_hash
            def retarget(path):
                result = original_hash(path)
                link.unlink()
                link.symlink_to(second)
                return result
            with patch.object(cache, 'file_hash', side_effect=retarget):
                with self.assertRaisesRegex(ValueError, 'resolution changed'):
                    cache.resolved_provider_files([link])
