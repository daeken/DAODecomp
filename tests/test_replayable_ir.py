"""Open typed-IL fixtures exercise generic recovery, not game acceptance."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
DLL = ROOT / 'tools/decompilation-mcp/bin/Release/net10.0/Decompilation.Mcp.dll'
DOTNET = shutil.which('dotnet') or '/usr/local/share/dotnet/dotnet'


def node(kind, **fields):
    return dict(type='LiftIl.' + kind, **fields)


def ty(bits):
    return dict(type='LiftIl.IlType+I', Bits=bits, Signed=False)


def reg(idx):
    return node('IlReadReg', Kind=dict(name='X86'), Idx=idx, Ty=ty(64))


def const(value, bits=32):
    return node('IlConst', Bits=dict(decimal=str(value)), Ty=ty(bits))


def binary(op, left, right):
    return node('IlBin', Op=dict(name=op), L=left, R=right, Ty=ty(64))


def write(idx, val):
    return node('IlWriteReg', Kind=dict(name='X86'), Idx=idx, Val=val)


def tmp(idx, bits):
    return node('IlTmp', Id=idx, Ty=ty(bits))


def fixture(call_width=None):
    bodies = []
    pc = 0x502000
    if call_width:
        bodies += [[node('IlLet', Id=0, Val=const(pc + 1, call_width * 8)),
                    write(4, binary('Sub', reg(4), const(call_width, 64))),
                    node('IlStore', Addr=reg(4), Val=tmp(0, call_width * 8)),
                    node('IlBranch', Kind=dict(name='Call'), Cond=None, Target=const(0x503000, 64))]]
        # Callee clobbers ECX; synthetic saved receiver explicitly survives the call.
        bodies.insert(0, [write(6, reg(1))])
        bodies.insert(0, [node('IlLet', Id=0, Val=reg(6)), write(4, binary('Sub', reg(4), const(4, 64))), node('IlStore', Addr=reg(4), Val=tmp(0, 32))])
        receiver = reg(6)
    else:
        receiver = reg(1)
    bodies += [[node('IlStore', Addr=binary('Add', receiver, const(104, 64)), Val=const(7, 8))], [write(0, receiver)]]
    if call_width:
        bodies += [[node('IlLet', Id=0, Val=node('IlLoad', Addr=reg(4), Ty=ty(32))), write(4, binary('Add', reg(4), const(4, 64))), write(6, tmp(0, 32))]]
    bodies += [[node('IlLet', Id=0, Val=node('IlLoad', Addr=reg(4), Ty=ty(32))), write(4, binary('Add', reg(4), const(4, 64))), node('IlBranch', Kind=dict(name='Ret'), Cond=None, Target=tmp(0, 32))]]
    rows = []
    for body in bodies:
        rows.append(dict(pc=pc, length=1, decoded=dict(P=dict(Lock=False, Rep=False, RepNz=False)), tree=node('IlBlock', Body=body)))
        pc += 1
    # Rewrite CALL return PC after inserting save/setup instructions.
    for row in rows:
        b = row['tree']['Body']
        if b[-1].get('Kind', {}).get('name') == 'Call':
            b[0]['Val']['Bits']['decimal'] = str(row['pc'] + 1)
    return dict(rva=0x2000, image_base=0x500000, image_end=0x600000,
                lift=dict(mode='Bits32', decode_complete=True, lift_errors=0, opaque_instructions=0, instructions=rows))


def tail_fixture():
    payload = fixture()
    payload['lift']['instructions'] = payload['lift']['instructions'][:1]
    payload['lift']['instructions'].append(dict(pc=0x502001, length=5, decoded=dict(P=dict(Lock=False, Rep=False, RepNz=False)), tree=node('IlBlock', Body=[node('IlBranch', Kind=dict(name='Jmp'), Cond=None, Target=const(0x503040, 64))])))
    return payload


@unittest.skipUnless(DLL.exists(), 'build C# component first')
class RecoveredIrTests(unittest.TestCase):
    def recover(self, payload):
        result = subprocess.run([DOTNET, str(DLL), 'recover-ir'], input=json.dumps(payload), text=True, capture_output=True, check=True)
        return json.loads(result.stdout)

    def test_generic_receiver_store_and_return(self):
        result = self.recover(fixture())
        self.assertEqual(result['status'], 'generated')
        self.assertIn('fn_00002000', result['source'])
        self.assertIn('+ 104) = 7u', result['source'])
        self.assertEqual(result['ir']['effects'][0]['value']['value'], 7)
        self.assertFalse(result['proof'])

    def test_correct_call_is_retained_external_dependency(self):
        result = self.recover(fixture(4))
        self.assertEqual(result['status'], 'generated', result)
        self.assertIn('void fn_00003000();', result['source'])
        self.assertIn('fn_00003000();', result['source'])
        self.assertEqual(result['ir']['effects'][0]['kind'], 'call')

    def test_segmented_wrapped_stack_and_captured_call_target(self):
        payload = fixture(4)
        def cast(value, bits, kind):
            return node('IlCast', X=value, Ty=ty(bits), Kind=dict(name=kind))
        def stack_address(value):
            return binary('Add', node('IlReadReg', Kind=dict(name='X86Seg'), Idx=2, Ty=ty(64)), cast(cast(value, 32, 'Trunc'), 64, 'Zext'))
        for row in payload['lift']['instructions']:
            body = row['tree']['Body']
            for effect in body:
                if effect['type'] == 'LiftIl.IlWriteReg' and effect['Idx'] == 4:
                    expression = effect['Val']
                    expression['L'] = cast(expression['L'], 32, 'Trunc')
                    expression['R']['Ty'] = ty(32)
                    expression['Ty'] = ty(32)
                    effect['Val'] = cast(expression, 64, 'Zext')
                if effect['type'] == 'LiftIl.IlStore' and effect['Addr'] == reg(4):
                    effect['Addr'] = stack_address(reg(4))
                if effect['type'] == 'LiftIl.IlLet' and effect['Val']['type'] == 'LiftIl.IlLoad':
                    effect['Val']['Addr'] = stack_address(reg(4))
            if body[-1].get('Kind', {}).get('name') == 'Call':
                target = const(0x503000, 32)
                body[0]['Id'] = 1
                body[2]['Val'] = tmp(1, 32)
                body[-1]['Target'] = tmp(0, 32)
                body.insert(0, node('IlLet', Id=0, Val=target))
        result = self.recover(payload)
        self.assertEqual(result['status'], 'generated', result)
        self.assertIn('SS is never replaced by zero', result['ir']['hypotheses'][0])
        self.assertIn('fn_00003000();', result['source'])
        # Segment state outside the modeled private stack is retained, then refused.
        for row in payload['lift']['instructions']:
            for effect in row['tree']['Body']:
                if effect['type'] == 'LiftIl.IlStore' and effect['Val'].get('Ty', {}).get('Bits') == 8:
                    effect['Addr'] = stack_address(reg(1))
        self.assertEqual(self.recover(payload)['status'], 'unsupported')

    def test_architecture_uses_explicit_abi_contract_without_compiler(self):
        payload = fixture(4)
        payload.update(emit=False, abi=dict(id='open-fixture-abi', return_register=7, argument_registers=[7], volatile_registers=[2], preserved_registers=[6]))
        result = self.recover(payload)
        self.assertEqual(result['status'], 'recovered')
        self.assertEqual(result['ir']['effects'][0]['inputs'], [dict(kind='register_input', index=7)])
        self.assertEqual(result['ir']['return'], dict(kind='register_input', index=7))
        self.assertNotIn('source', result)
        # Preservation is profile policy, not a fixed ECX/EAX/EDX convention.
        payload['abi']['preserved_registers'] = [0]
        self.assertEqual(self.recover(payload)['blocker'], 'profile_preserved_register_not_restored')

    def test_caller_stack_write_is_retained_and_refused_by_emitter(self):
        payload = fixture()
        payload['lift']['instructions'][0]['tree']['Body'][0].update(Addr=binary('Add', reg(4), const(4, 64)), Val=const(9, 32))
        self.assertEqual(self.recover(payload)['blocker'], 'caller_or_unallocated_stack_write_not_emittable')
        payload['emit'] = False
        result = self.recover(payload)
        self.assertEqual(result['status'], 'recovered')
        self.assertEqual(result['ir']['stack_effects'][0]['value']['value'], 9)
        self.assertFalse(result['ir']['stack_effects'][0]['within_allocated_frame'])

    def test_terminal_tail_call_preserves_store_target_inputs_and_unknown_return(self):
        result = self.recover(tail_fixture())
        self.assertEqual(result['status'], 'generated', result)
        ir = result['ir']
        self.assertEqual(ir['exit_kind'], 'tail_call')
        self.assertEqual([e['kind'] for e in ir['effects']], ['store', 'tail_call'])
        self.assertEqual(ir['effects'][0]['value']['value'], 7)
        self.assertEqual(ir['effects'][1]['value']['value'], 0x503040)
        self.assertEqual(ir['effects'][1]['inputs'], [dict(kind='register_input', index=1)])
        self.assertEqual(ir['return']['kind'], 'unknown')
        self.assertIn('void Recovered::fn_00002000()', result['source'])
        self.assertIn('void fn_00003040();', result['source'])
        self.assertNotIn('return this', result['source'])

    def test_tail_call_abi_arguments_are_explicit_policy(self):
        payload = tail_fixture()
        payload.update(emit=False, abi=dict(id='open-tail-abi', return_register=2, argument_registers=[7, 2], volatile_registers=[2], preserved_registers=[6]))
        result = self.recover(payload)
        self.assertEqual(result['status'], 'recovered')
        self.assertEqual(result['ir']['effects'][-1]['inputs'], [dict(kind='register_input', index=7), dict(kind='register_input', index=2)])
        self.assertEqual(result['ir']['return']['kind'], 'unknown')

    def test_tail_call_rejects_internal_conditional_indirect_and_unbalanced_exits(self):
        for target, condition in [(const(0x502000, 64), None), (reg(2), None), (const(0x503040, 64), const(1, 8))]:
            payload = tail_fixture()
            payload['lift']['instructions'][-1]['tree']['Body'][-1].update(Target=target, Cond=condition)
            with self.subTest(target=target, condition=condition):
                self.assertEqual(self.recover(payload)['status'], 'unsupported')
        payload = tail_fixture()
        payload['lift']['instructions'][0]['tree']['Body'].insert(0, write(4, binary('Sub', reg(4), const(4, 64))))
        self.assertEqual(self.recover(payload)['blocker'], 'unbalanced_tail_call_stack')
        payload = tail_fixture()
        payload['lift']['instructions'].append(copy.deepcopy(payload['lift']['instructions'][0]))
        self.assertEqual(self.recover(payload)['status'], 'unsupported')
        payload = tail_fixture()
        payload['lift']['instructions'][0]['tree']['Body'].append(write(6, const(9)))
        self.assertEqual(self.recover(payload)['blocker'], 'profile_preserved_register_not_restored')

    def test_actual_known_register_indirect_refused_and_direct_boundary_preserved(self):
        fixtures = json.loads((ROOT / 'tools/decompilation-mcp/fixtures/open-tail-branches.json').read_text())
        expected = {'open-known-register-indirect': 'unsupported', 'open-direct-external': 'generated', 'open-direct-at-range-end': 'generated'}
        for case in fixtures['cases']:
            payload = dict(lift=case['lift'], rva=0x2000, image_base=0x500000, image_end=0x600000)
            result = self.recover(payload)
            with self.subTest(case=case['input']['id']):
                self.assertEqual(result['status'], expected[case['input']['id']], result)
                if result['status'] == 'unsupported':
                    self.assertEqual(result['blocker'], 'unsupported_indirect_tail_call')
                else:
                    self.assertEqual(result['ir']['exit_kind'], 'tail_call')
        # Also cover symbolic propagation directly: an unknown-register-only test
        # would miss the boundary violation above.
        payload = tail_fixture()
        payload['lift']['instructions'][0]['tree']['Body'].append(write(0, const(0x503040, 32)))
        payload['lift']['instructions'][-1]['tree']['Body'][-1]['Target'] = reg(0)
        self.assertEqual(self.recover(payload)['blocker'], 'unsupported_indirect_tail_call')

    def test_original_sharpretro_wrong_call_width_is_rejected(self):
        self.assertEqual(self.recover(fixture(8))['blocker'], 'incorrect_Bits32_call_stack_width')

    def test_no_unknown_or_dropped_semantics(self):
        changes = [
            lambda p: p['lift'].update(decode_complete=False),
            lambda p: p['lift'].update(opaque_instructions=1),
            lambda p: p['lift']['instructions'][0]['decoded']['P'].update(Lock=True),
            lambda p: p['lift']['instructions'][0]['tree']['Body'][0].update(Val=reg(2)),
            lambda p: p['lift']['instructions'].append(copy.deepcopy(p['lift']['instructions'][0])),
            lambda p: p['lift']['instructions'].pop(),
            lambda p: p['lift']['instructions'][0]['tree']['Body'].append(node('IlUnimpl')),
        ]
        for change in changes:
            payload = fixture()
            change(payload)
            with self.subTest(change=change):
                self.assertEqual(self.recover(payload)['status'], 'unsupported')

    def test_changed_source_values_propagate_without_rva_lookup(self):
        payload = fixture()
        payload['rva'] = 0x4550
        payload['lift']['instructions'][0]['tree']['Body'][0]['Val'] = const(251, 8)
        result = self.recover(payload)
        self.assertIn('fn_00004550', result['source'])
        self.assertIn('251u', result['source'])
        self.assertNotIn('7u', result['source'])
