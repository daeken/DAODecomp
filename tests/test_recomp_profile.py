"""Keep the configured runtime profile inside its dedicated Wine prefix."""
from pathlib import Path
import json
import tempfile
import unittest
from tools.recomp_boot import checked_startup_profile


class RuntimeProfileTests(unittest.TestCase):
    def registry(self,prefix,shell=r'C:\users\player\Documents',user=r'%USERPROFILE%\Documents',profile=r'C:\users\player'):
        sections=[(r'Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders','Personal',shell,''),
                  (r'Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\User Shell Folders','Personal',user,'str(2):'),
                  ('Volatile Environment','USERPROFILE',profile,'')]
        text='WINE REGISTRY Version 2\n'
        for section,name,value,kind in sections:
            text+=f'\n[{section}] 1\n{json.dumps(name)}={kind}{json.dumps(value)}\n'
        (prefix/'user.reg').write_text(text)

    def test_optional_contract_and_owned_documents(self):
        with tempfile.TemporaryDirectory() as temporary:
            prefix=Path(temporary)/'prefix';documents=prefix/'drive_c/users/player/Documents';documents.mkdir(parents=True)
            self.registry(prefix)
            self.assertIsNone(checked_startup_profile(prefix,{}))
            state=dict(filesystem_profile=dict(documents_relative='drive_c/users/player/Documents'))
            result=checked_startup_profile(prefix,state)
            self.assertEqual(result['documents_directory'],str(documents.resolve()))
            self.assertEqual(result['wine_prefix'],str(prefix.resolve()))
            self.assertEqual(result['registry_personal_paths']['user'],r'C:\users\player\Documents')

    def test_active_wine_user_route_cannot_hide_behind_inactive_owned_directory(self):
        # Actual CX24 failure: Shell Folders initially names the old owned user,
        # but User Shell Folders expands to crossover's external Documents link.
        with tempfile.TemporaryDirectory() as temporary:
            prefix=Path(temporary)/'prefix';(prefix/'drive_c/users/player/Documents').mkdir(parents=True)
            external=Path(temporary)/'external';external.mkdir()
            active=prefix/'drive_c/users/crossover';active.mkdir();(active/'Documents').symlink_to(external,target_is_directory=True)
            state=dict(filesystem_profile=dict(documents_relative='drive_c/users/player/Documents'))
            self.registry(prefix,profile=r'C:\users\crossover')
            with self.assertRaisesRegex(ValueError,'registry routes differ'):checked_startup_profile(prefix,state)
            self.assertTrue((active/'Documents').is_symlink())
            self.assertEqual(list(external.iterdir()),[])

    def test_both_routes_and_declared_windows_path_must_agree(self):
        with tempfile.TemporaryDirectory() as temporary:
            prefix=Path(temporary)/'prefix';(prefix/'drive_c/users/player/Documents').mkdir(parents=True)
            state=dict(filesystem_profile=dict(documents_relative='drive_c/users/player/Documents'))
            self.registry(prefix,shell=r'C:\users\other\Documents')
            with self.assertRaises(ValueError):checked_startup_profile(prefix,state)
            self.registry(prefix,user=r'C:\users\PLAYER\Documents',profile=r'C:\users\other')
            self.assertIsNotNone(checked_startup_profile(prefix,state))
            state['filesystem_profile']['windows_personal_path']=r'C:\users\other\Documents'
            with self.assertRaises(ValueError):checked_startup_profile(prefix,state)

    def test_missing_ambiguous_and_unknown_registry_routes_cannot_pass(self):
        with tempfile.TemporaryDirectory() as temporary:
            prefix=Path(temporary)/'prefix';(prefix/'drive_c/users/player/Documents').mkdir(parents=True)
            state=dict(filesystem_profile=dict(documents_relative='drive_c/users/player/Documents'))
            with self.assertRaises(ValueError):checked_startup_profile(prefix,state)
            for value in (r'%MISSING%\Documents',r'Z:\external',r'C:\users\player\..\Documents','C:\\bad\nDocuments'):
                self.registry(prefix,user=value)
                with self.subTest(value=value),self.assertRaises(ValueError):checked_startup_profile(prefix,state)
            self.registry(prefix)
            registry=prefix/'user.reg';registry.write_text(registry.read_text()+'"USERPROFILE"="C:\\\\users\\\\other"\n')
            with self.assertRaisesRegex(ValueError,'ambiguous'):checked_startup_profile(prefix,state)

    def test_changed_route_is_detected_without_binding_unrelated_registry_edits(self):
        with tempfile.TemporaryDirectory() as temporary:
            prefix=Path(temporary)/'prefix';(prefix/'drive_c/users/player/Documents').mkdir(parents=True)
            state=dict(filesystem_profile=dict(documents_relative='drive_c/users/player/Documents'))
            self.registry(prefix);before=checked_startup_profile(prefix,state)
            registry=prefix/'user.reg';registry.write_text(registry.read_text()+'\n[Unrelated] 2\n"Option"="changed"\n')
            self.assertEqual(before,checked_startup_profile(prefix,state))
            self.registry(prefix,profile=r'C:\users\crossover')
            with self.assertRaises(ValueError):checked_startup_profile(prefix,state)

    def test_symlinks_and_parent_aliases_are_refused(self):
        with tempfile.TemporaryDirectory() as temporary:
            base=Path(temporary);prefix=base/'prefix';prefix.mkdir();external=base/'external';external.mkdir();inside=prefix/'inside';inside.mkdir()
            state=dict(filesystem_profile=dict(documents_relative='Documents'));link=prefix/'Documents'
            for target in (external,inside):
                link.symlink_to(target,target_is_directory=True)
                with self.assertRaises(ValueError):checked_startup_profile(prefix,state)
                link.unlink()
            (external/'Documents').mkdir();parent=prefix/'user';parent.symlink_to(external,target_is_directory=True)
            with self.assertRaises(ValueError):checked_startup_profile(prefix,dict(filesystem_profile=dict(documents_relative='user/Documents')))
            self.assertTrue((external/'Documents').is_dir())

    def test_missing_and_malformed_profiles_do_not_launch(self):
        with tempfile.TemporaryDirectory() as temporary:
            prefix=Path(temporary)
            for value in ('missing','../outside',str(prefix/'absolute'),'',None):
                with self.subTest(value=value),self.assertRaises(ValueError):
                    checked_startup_profile(prefix,dict(filesystem_profile=dict(documents_relative=value)))


if __name__=='__main__':unittest.main()
