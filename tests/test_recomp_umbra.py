"""Guard the bounded Umbra experiment's observation and fixture domain."""
import importlib.util
from pathlib import Path
import unittest
from tools import recomp

SCRIPT=recomp.ROOT / 'recompiler/experiments/compare_umbra.py'
spec=importlib.util.spec_from_file_location('compare_umbra',SCRIPT)
experiment=importlib.util.module_from_spec(spec); spec.loader.exec_module(experiment)


class UmbraExperimentTests(unittest.TestCase):
    def test_complete_observations_reject_missing_extra_malformed_and_narrowed_results(self):
        row=' '.join(['4294967295']*10+['00'*1024])+'\n'
        result=experiment.observations(row,1)
        self.assertEqual(result[0][0],0xffffffff)
        self.assertEqual(len(result[0][-1]),2048)
        for text,count in (('',1),(row,0),(row+row,1),(row.replace('4294967295','4294967296',1),1),
                           (row.replace('4294967295','-1',1),1),(row[:-4]+'\n',1),(row.replace('00','gg'),1)):
            with self.assertRaises(ValueError): experiment.observations(text,count)

    def test_cases_cover_every_entry_both_layout_paths_sentinels_and_store_alias(self):
        contract=recomp.load(experiment.CONTRACT); cases=experiment.cases_for(contract)
        self.assertEqual(cases,experiment.cases_for(contract))
        self.assertEqual(len({c['kind'] for c in cases}),len(contract['functions']))
        for kind,function in enumerate(contract['functions']):
            selected=[c for c in cases if c['kind']==kind]
            self.assertTrue({0,1,0xffffffff} <= {c['word'] for c in selected})
            self.assertTrue(any(c['object']%4 for c in selected))
            self.assertTrue(any(c['object']==c['inner'] for c in selected))
            if function['rva'] in (0x5e270,0x5e2c0,0x5e430,0x5e490):
                self.assertEqual({c['mode'] for c in selected},{0,1,0xffffffff})
            if function['rva']==0x5e400:
                aliases=[c for c in selected if c['inner']+4==c['object']]
                self.assertTrue({0,1,2,255} <= {c['first'] for c in aliases})
                # The byte write changes the pointer reloaded by the next store.
                for case in aliases:
                    changed=(case['inner']&~255)|(case['first']&255)
                    self.assertTrue(0<=changed and changed+12<=1024)
            for case in selected:
                for key in ('object','inner','nested'): self.assertTrue(0<=case[key]<=960)


if __name__=='__main__': unittest.main()
