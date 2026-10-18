"""Composition policy tests; fixtures are not new game evidence."""
import copy,json,shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from tools import incremental_checkpoint as cache, validate_checkpoint as checkpoint
from tools.update_progress import Snapshot
ROOT=Path(__file__).resolve().parents[1]
REGISTRY=json.loads((ROOT/'analysis/functions.json').read_text())

class ThroughputCompositionTests(unittest.TestCase):
    def test_complete_registry_routing_and_checkpoint_plan(self):
        self.assertEqual(len([f for f in REGISTRY['functions'] if f['status'] in cache.ACTIVE]),69)
        selected=[f['id'] for group in cache.required_groups(REGISTRY) for f in cache.selected_entries(REGISTRY,group)]
        self.assertEqual(len(selected),69);self.assertEqual(len(set(selected)),69)
        steps=checkpoint.build_commands(ROOT/'build-incremental-combined',ROOT/'reports/test-plan',2,windows=False)
        for group in cache.required_groups(REGISTRY):
            config=cache.group_execution(steps,group)
            self.assertEqual(config['mode'],'batch' if group in cache.BATCH_IMAGES else 'single')
        positives,negatives=checkpoint.publication_paths(ROOT/'reports/test-plan')
        self.assertEqual((len(positives),len(negatives)),(69,48))
        for mutation in ('missing','unknown','wrong-group'):
            changed=copy.deepcopy(REGISTRY)
            target=next(f for f in changed['functions'] if f.get('backend')=='object-bitfields-001')
            if mutation=='missing':target['status']='contracted'
            elif mutation=='unknown':target['backend']='unknown'
            else:target['recovery_group']='unknown'
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):cache.required_groups(changed)

    def test_mode_size_and_complete_command_argv_are_identity(self):
        def config(size):return cache.group_execution(checkpoint.build_commands(ROOT/'build-incremental-combined',ROOT/'reports/test-plan',2,windows=False,batch_size=size),'indexed_fields')
        self.assertNotEqual(config(128),config(64));self.assertEqual(config(64)['batch_size'],64)
        steps=checkpoint.build_commands(ROOT/'build-incremental-combined',ROOT/'reports/test-plan',2,windows=False)
        altered=copy.deepcopy(steps)
        argv=next(argv for name,argv,_ in altered if name=='indexed_fields_all');argv[argv.index('--execution')+1]='single'
        with self.assertRaises(ValueError):cache.group_execution(altered,'indexed_fields')
        altered=[step for step in steps if step[0]!='indexed_fields_negative']
        with self.assertRaises(ValueError):cache.group_execution(altered,'indexed_fields')
        self.assertNotEqual(cache.digest(config(128)),cache.digest(dict(config(128),mode='single')))

    def test_empty_owned_build_removes_all_stale_images(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);build=root/'build-incremental-test';cache.prepare_build(root,build)
            for group in cache.BATCH_IMAGES:
                for image in cache.execution_images(build,group,{'mode':'batch'}):image.write_bytes(b'stale native image')
            (build/'libobsolete.a').write_bytes(b'stale archive');cache.prepare_build(root,build)
            self.assertEqual({p.name for p in build.iterdir()},{cache.OWNER_FILE})
            for group in cache.BATCH_IMAGES:
                with self.assertRaises(ValueError):cache.files_manifest(cache.execution_images(build,group,{'mode':'batch'}))

    def test_complete_publication_and_v2_updater_reject_partial_inventory(self):
        inventory=cache.publication_inventory()
        self.assertEqual(len(inventory),117)
        records=[dict(function_id=identity,negative_control=negative,status='corpus_pass',artifacts_sha256={'historical':'retained'},report='historical/report.json',report_sha256='retained',repeats_per_side=2,artifacts_unchanged=True,case_counts={'mismatch' if negative else 'corpus_pass':1}) for identity,negative in sorted(inventory)]
        result=dict(schema_version=2,policy=cache.POLICY,status='passed',complete_checkpoint=True,usable_for_progress=True,source={},registry_sha256=cache.file_hash(ROOT/'analysis/functions.json'),groups=[dict(group='fixture',records=records,reused=False,identity_sha256='current')])
        document=cache.publication_document(result)
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'analysis/validation').mkdir(parents=True)
            shutil.copy2(ROOT/'analysis/functions.json',root/'analysis/functions.json')
            path=root/'analysis/validation/checkpoint.json';path.write_text(json.dumps(document))
            self.assertEqual(len(Snapshot(root).document('analysis/validation/checkpoint.json')['records']),117)
            bad=copy.deepcopy(document);bad['records'].pop();unsigned={k:v for k,v in bad.items() if k!='attestation_sha256'};bad['attestation_sha256']=cache.digest(unsigned);path.write_text(json.dumps(bad))
            with self.assertRaises(ValueError):Snapshot(root).document('analysis/validation/checkpoint.json')
        result['groups'][0]['records'].pop()
        with self.assertRaises(ValueError):cache.publication_document(result)

    def test_real_batch_images_and_selected_data_are_exact_inputs(self):
        build=ROOT/'build-incremental-combined'
        if not (build/'libdao_object_bitfield_batch.dylib').is_file():self.skipTest('composition native build not present')
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);b=root/'build-incremental-fixture';b.mkdir()
            (root/'analysis').mkdir();shutil.copy2(ROOT/'analysis/reference-build.json',root/'analysis/reference-build.json')
            (root/'gamedata/bin_ship').mkdir(parents=True);(root/'gamedata/bin_ship/DAOrigins.exe').write_bytes(b'identity unit fixture')
            for group in cache.BATCH_IMAGES:
                fs=cache.selected_entries(REGISTRY,group)
                for f in fs:
                    p=root/f['contract'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/f['contract'],p)
                for src in cache.execution_images(build,group,{'mode':'batch'}):shutil.copy2(src,b/src.name)
                if group=='direct_object_fields':
                    shutil.copytree(ROOT/'corpus',root/'corpus',dirs_exist_ok=True)
                    shutil.copy2(ROOT/'slices.json',root/'slices.json')
                if group=='object_bitfields':
                    shutil.copytree(ROOT/'validation/object_bitfield_corpus',root/'validation/object_bitfield_corpus')
                    shutil.copy2(ROOT/'validation/object_bitfield_specs.json',root/'validation/object_bitfield_specs.json')
                config={'mode':'batch','commands':[],'batch_size':128}
                corpus=cache.actual_corpora(group,fs)
                def identity():return cache.group_identity(root,b,group,REGISTRY,{}, {'provider':'macos-full-python-dyld-v1'},config,corpus)
                original=identity();self.assertEqual(len(original['executables']),3)
                self.assertEqual(set(Path(p).name for p in original['executables'] if p.endswith('.dylib')),{p.name for p in cache.execution_images(b,group,config)})
                image=cache.execution_images(b,group,config)[1];old=image.read_bytes();image.unlink()
                with self.assertRaises(ValueError):identity()
                image.write_bytes(old)
                contract=root/fs[0]['contract'];old=contract.read_bytes();contract.write_bytes(old+b' ')
                self.assertNotEqual(original,identity());contract.write_bytes(old)
                if group=='object_bitfields':
                    path=next((root/'validation/object_bitfield_corpus').glob('*.json'));old=path.read_bytes();path.write_bytes(old+b' ')
                    self.assertNotEqual(original,identity());path.write_bytes(old)
