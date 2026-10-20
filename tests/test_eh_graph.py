"""Synthetic graphs: no game bytes, authored contracts or acceptance bypass."""
import ast
import copy
import hashlib
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
import rapid_object
try:
    from rapid_object import eh_graph as graph, symbol_identity as identity
except ImportError:
    rapid_object.__path__.insert(0,str(Path(__file__).resolve().parents[1]/'rapid_object'))
    from rapid_object import eh_graph as graph, symbol_identity as identity

PARENT='?fn_00001000@@YAXXZ'
H='__ehhandler$'+PARENT
D='__ehfuncinfo$'+PARENT
U='__unwindtable$'+PARENT
A='__unwindfunclet$'+PARENT+'$0'


def pe(body):
    data=bytearray(0x200+len(body));data[:2]=b'MZ';struct.pack_into('<I',data,0x3c,0x80);data[0x80:0x84]=b'PE\0\0';struct.pack_into('<HHIIIHH',data,0x84,0x14c,1,0,0,0,224,0);struct.pack_into('<H',data,0x98,0x10b);struct.pack_into('<I',data,0x98+28,0x400000);struct.pack_into('<8sIIIIIIHHI',data,0x178,b'.text',len(body),0x1000,len(body),0x200,0,0,0,0,0x60000020);data[0x200:]=body;return bytes(data)


def coff(sections,symbols):
    strings=bytearray(b'\0'*4);syms=bytearray();ids={}
    for name,value,sec,typ,storage,size in symbols:
        ids[name]=len(syms)//18;raw=name.encode()
        if len(raw)>8:
            off=len(strings);strings.extend(raw+b'\0');raw=struct.pack('<II',0,off)
        aux=[]
        if size is not None:
            a=bytearray(18);struct.pack_into('<I',a,4,size);aux=[a]
        syms.extend(struct.pack('<8sIhHBB',raw,value,sec,typ,storage,len(aux)))
        for a in aux:syms.extend(a)
    header_size=20+40*len(sections);payload=bytearray();headers=[]
    for name,body,rels,flags in sections:
        ptr=header_size+len(payload);payload.extend(body);rp=header_size+len(payload)
        for off,target,kind in rels:payload.extend(struct.pack('<IIH',off,ids[target],kind))
        headers.append(struct.pack('<8sIIIIIIHHI',name.encode(),0,0,len(body),ptr,rp if rels else 0,0,len(rels),0,flags))
    struct.pack_into('<I',strings,0,len(strings));return struct.pack('<HHIIIHH',0x14c,len(sections),0,header_size+len(payload),len(syms)//18,0,0)+b''.join(headers)+payload+syms+strings


def fixture(original_cookie=False,candidate_cookie=False):
    body=bytearray(b'\xcc'*0x700);main=b'\x6a\xff\x68'+struct.pack('<I',0x401100)+bytes.fromhex('64a100000000')+b'\xc3';body[:len(main)]=main
    def rel(site,target):return struct.pack('<i',target-(site+4))
    def handler(cookie,va,descriptor,runtime,original):
        if cookie:
            prefix=bytes.fromhex('8b5424088d42f48b4af033c8e8')+(rel(va+13,0x401600) if original else bytes(4));return prefix+b'\xb8'+struct.pack('<I',descriptor)+b'\xe9'+(rel(va+23,runtime) if original else bytes(4))
        return b'\xb8'+struct.pack('<I',descriptor)+b'\xe9'+(rel(va+6,runtime) if original else bytes(4))
    h=handler(original_cookie,0x401100,0x401208,0x401500,True);body[0x100:0x100+len(h)]=h
    descriptor=struct.pack('<9I',0x19930522,1,0x401200,0,0,0,0,0,1);body[0x208:0x208+36]=descriptor;body[0x200:0x208]=struct.pack('<iI',-1,0x401300)
    body[0x300:0x30b]=b'\x8b\x45\xf0\x50\xe8'+rel(0x401305,0x401400)+b'\x59\xc3';body[0x400]=body[0x500]=body[0x600]=0xc3
    original=pe(body);candidate_main=main[:3]+bytes(4)+main[7:];action=bytes.fromhex('8b45f050e80000000059c3');candidate_handler=handler(candidate_cookie,0,0,0,False);fields=[(1,6),(6,20)] if not candidate_cookie else [(13,20),(18,6),(23,20)];hrel=[]
    for off,kind in fields:
        target=D if kind==6 else '__security_check_cookie' if off==13 else '___CxxFrameHandler3';hrel.append((len(action)+off,target,kind))
    sections=[('.text',candidate_main,[(3,H,6)],0x60000020),('.text$x',action+candidate_handler,[(5,'_fn_00001400',20)]+hrel,0x60000020),('.xdata$x',struct.pack('<iI',-1,0)+struct.pack('<9I',0x19930522,1,0,0,0,0,0,0,1),[(4,A,6),(16,U,6)],0x40000040)]
    symbols=[(PARENT,0,1,32,2,len(main)),(A,0,2,32,3,None),(H,11,2,32,3,None),(U,0,3,0,3,None),(D,8,3,0,3,None),('_fn_00001400',0,0,32,2,None),('___CxxFrameHandler3',0,0,32,2,None),('__security_check_cookie',0,0,32,2,None)]
    requested={0x1000:{'symbol':PARENT,'ranges':[{'start_rva':0x1000,'end_rva_inclusive':0x1000+len(main)-1}],'bytes_sha256':hashlib.sha256(main).hexdigest()}}
    return original,sections,symbols,requested


class IdentityTests(unittest.TestCase):
    def test_anchored_source_names(self):
        for name,kind,rva in [('_fn_00001000','fn',0x1000),('fn_00001000','fn',0x1000),('_fn_00001000@4','fn',0x1000),(PARENT,'fn',0x1000),('?fn_00001000@Receiver@@QAEXXZ','fn',0x1000),('_g_00002000','g',0x2000)]:self.assertEqual(identity.source_identity(name),(kind,rva))
    def test_generated_never_parent_alias(self):
        for name in (H,D,U,A):self.assertIsNone(identity.source_identity(name));self.assertEqual(identity.generated_identity(name)['parent_symbol'],PARENT)
    def test_embedded_import_and_nested_names_refused(self):
        for name in ('__imp__fn_00001000','wrapper_fn_00001000','?member@fn_00001000@@YAXXZ','__unknown$'+PARENT,'fn_00001000junk','g_00002000tail'):self.assertIsNone(identity.source_identity(name))
    def test_no_bad_funclet_ordinal(self):
        self.assertFalse(identity.generated_identity('__unwindfunclet$'+PARENT+'$x')['supported_name'])
    def test_nonstring_names_never_bind(self):
        self.assertIsNone(identity.generated_identity(42));self.assertIsNone(identity.source_identity(None))
    def test_proposed_build_export_callsite_parity(self):
        root=Path(__file__).resolve().parents[1];o,secs,syms,requested=fixture()
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'candidate.obj';p.write_bytes(coff(secs,syms));outputs=[]
            for relative,name in [('rapid_object/build.py','symbol_bindings'),('tools/export_native_sources.py','retained_symbol_bindings')]:
                tree=ast.parse((root/relative).read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name);namespace={'Path':Path};exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),relative,'exec'),namespace);r=copy.deepcopy(requested);outputs.append((namespace[name](p,r,{'fn_00001000':0x401000,'fn_00001400':0x401400}),r))
            self.assertEqual(outputs[0],outputs[1]);self.assertNotIn(H,outputs[0][0])
    def test_pure_binder_ignores_all_four_generated_names(self):
        original,secs,syms,requested=fixture();obj=coff(secs,syms);bound=identity.bind_symbols(obj,requested,{'fn_00001000':0x401000,'fn_00001400':0x401400});self.assertEqual(bound,{PARENT:0x401000,'_fn_00001400':0x401400});self.assertEqual(requested[0x1000]['symbol'],PARENT)


class GraphTests(unittest.TestCase):
    def test_global_comparator_refusals_remain_diagnostic_errors(self):
        for symbols,error in [({PARENT:0x401001},'symbol_identity_conflict'),
                              ({'_fn_00001400':-1},'invalid_symbol_address')]:
            with self.subTest(error=error):
                report=self.diagnose(symbols=symbols)
                self.assertEqual(report['state'],'diagnostic_incomplete')
                self.assertEqual(report['error'],'unchanged_comparator:'+error)
                self.assertEqual(report['legacy_comparator']['error'],error)
                self.assertEqual(report['legacy_comparator']['counts']['inconclusive'],1)
                self.assertEqual(report['functions'],[])
    def test_missing_comparator_function_result_is_incomplete(self):
        with patch.object(graph,'compare_bytes',return_value={'functions':[]}):
            row=self.row()
        self.assertEqual(row['state'],'diagnostic_incomplete')
        self.assertIn('unchanged_comparator:missing_function_result',row['blockers'])
    def diagnose(self,edit=None,original_cookie=False,candidate_cookie=False,symbols=None):
        original,secs,syms,requested=fixture(original_cookie,candidate_cookie)
        if edit:original,secs,syms,requested=edit(original,secs,syms,requested)
        report=graph.diagnose(original,coff(secs,syms),requested,symbols or {'_fn_00001400':0x401400},module_sha256=hashlib.sha256(original).hexdigest());self.assertFalse(report['acceptance_supported']);self.assertTrue(report['diagnostic_only']);return report
    def row(self,**kw):return self.diagnose(**kw)['functions'][0]
    def mutate_section(self,section,offset,blob):
        def edit(original,secs,syms,requested):
            name,body,rels,flags=secs[section];body=body[:offset]+blob+body[offset+len(blob):];secs[section]=(name,body,rels,flags);return original,secs,syms,requested
        return edit
    def test_identical_profiles_are_never_acceptance(self):
        r=self.row();self.assertEqual(r['state'],'diagnostic_identity_still_unresolved');self.assertEqual(r['legacy_comparator']['status'],'inconclusive');self.assertIn('exception_runtime_symbol_identity_unverified',r['blockers']);self.assertEqual(r['original']['action']['size'],11)
    def test_all_supported_node_bytes_retained(self):
        r=self.row()
        for side in ('original','candidate'):
            for name in ('handler','FuncInfo','unwind_map','action'):
                n=r[side][name];raw=bytes.fromhex(n['bytes_hex']);self.assertEqual(len(raw),n['size']);self.assertEqual(hashlib.sha256(raw).hexdigest(),n['sha256'])
    def test_cookie_gap_explicit(self):
        r=self.row(original_cookie=True);self.assertIn('handler_cookie_checked_differs',r['differences'])
    def test_matching_cookie_profiles_still_unknown(self):
        r=self.row(original_cookie=True,candidate_cookie=True);self.assertEqual(r['differences'],[]);self.assertIn('cookie_runtime_symbol_identity_unverified',r['blockers'])
    def test_cookie_frame_offset_corruption(self):
        r=self.row(original_cookie=True,candidate_cookie=True,edit=self.mutate_section(1,11+9,b'\xf4'));self.assertIn('handler_cookie_load_parent_offset_differs',r['differences'])
    def test_action_frame_offset_corruption(self):
        r=self.row(edit=self.mutate_section(1,2,b'\xec'));self.assertIn('unwind_action_form_or_frame_offset_differs',r['differences'])
    def test_action_effect_corruption(self):
        r=self.row(edit=self.mutate_section(1,3,b'\x51'));self.assertEqual(r['state'],'diagnostic_incomplete');self.assertIn('unsupported_or_incomplete_unwind_action',r['blockers'])
    def test_metadata_flags_corruption(self):
        r=self.row(edit=self.mutate_section(2,8+32,struct.pack('<I',0)));self.assertIn('unsupported_FuncInfo_fields',r['blockers'])
    def test_metadata_state_count_corruption(self):
        r=self.row(edit=self.mutate_section(2,8+4,struct.pack('<I',2)));self.assertIn('unsupported_FuncInfo_fields',r['blockers'])
    def test_unwind_transition_corruption(self):
        r=self.row(edit=self.mutate_section(2,0,struct.pack('<i',0)));self.assertIn('unsupported_candidate_unwind_state_transition',r['blockers'])
    def test_nonzero_relocation_addend(self):
        r=self.row(edit=self.mutate_section(2,16,struct.pack('<I',4)));self.assertIn('nonzero_graph_reference_addend',r['blockers'])
    def test_wrong_runtime_address_claim(self):
        r=self.row(symbols={'___CxxFrameHandler3':0x401501});self.assertIn('runtime_target_address_claim_conflict',r['differences'])
    def test_wrong_cleanup_address_claim(self):
        r=self.row(symbols={'_fn_00001400':0x401401});self.assertIn('cleanup_target_address_claim_conflict',r['differences'])
    def test_matching_runtime_claim_not_identity_proof(self):
        r=self.row(symbols={'___CxxFrameHandler3':0x401500});self.assertIn('exception_runtime_symbol_identity_unverified',r['blockers'])
    def test_generated_address_claim_discarded(self):
        r=self.diagnose(symbols={H:0x401000});self.assertEqual(r['discarded_generated_address_claims'],{H:0x401000})
    def test_missing_relocation(self):
        def edit(o,s,y,r):name,b,rels,f=s[2];s[2]=(name,b,rels[:1],f);return o,s,y,r
        self.assertIn('unsupported_or_incomplete_graph_relocations',self.row(edit=edit)['blockers'])
    def test_unsupported_relocation(self):
        def edit(o,s,y,r):name,b,rels,f=s[2];s[2]=(name,b,[(off,t,7 if off==16 else k) for off,t,k in rels],f);return o,s,y,r
        self.assertIn('unsupported_or_incomplete_graph_relocations',self.row(edit=edit)['blockers'])
    def test_wrong_parent_identity(self):
        def edit(o,s,y,r):y[2]=('__ehhandler$?fn_00002000@@YAXXZ',*y[2][1:]);name,b,rels,f=s[0];s[0]=(name,b,[(3,y[2][0],6)],f);return o,s,y,r
        self.assertIn('incomplete_or_extra_parent_generated_inventory',self.row(edit=edit)['blockers'])
    def test_incomplete_metadata_span(self):
        def edit(o,s,y,r):name,b,rels,f=s[2];s[2]=(name,b[:-1],rels,f);return o,s,y,r
        self.assertTrue(any('incomplete_or_overlapping_generated_span' in x for x in self.row(edit=edit)['blockers']))
    def test_extra_handler_bytes_not_dropped(self):
        def edit(o,s,y,r):name,b,rels,f=s[1];s[1]=(name,b+b'\x90',rels,f);return o,s,y,r
        self.assertIn('unsupported_or_incomplete_handler_code',self.row(edit=edit)['blockers'])
    def test_original_main_hash_corruption(self):
        def edit(o,s,y,r):r[0x1000]['bytes_sha256']='0'*64;return o,s,y,r
        self.assertIn('original_main_sha256_mismatch',self.row(edit=edit)['blockers'])
    def test_module_binding_required(self):
        o,s,y,r=fixture();p=graph.diagnose(o,coff(s,y),r,module_sha256='0'*64);self.assertEqual(p['error'],'module_sha256_mismatch')
    def test_original_metadata_corruption(self):
        def edit(o,s,y,r):b=bytearray(o);struct.pack_into('<I',b,0x200+0x208+32,0);return bytes(b),s,y,r
        self.assertIn('unsupported_FuncInfo_fields',self.row(edit=edit)['blockers'])
    def test_original_action_frame_offset_corruption(self):
        def edit(o,s,y,r):b=bytearray(o);b[0x200+0x300+2]=0xec;return bytes(b),s,y,r
        self.assertIn('unwind_action_form_or_frame_offset_differs',self.row(edit=edit)['differences'])
    def test_original_unbacked_runtime_target(self):
        def edit(o,s,y,r):b=bytearray(o);struct.pack_into('<i',b,0x200+0x100+6,0x7fff0000-0x40110a);return bytes(b),s,y,r
        self.assertIn('original_range_not_unique_backed',self.row(edit=edit)['blockers'])
    def test_extra_generated_funclet_not_silently_dropped(self):
        def edit(o,s,y,r):y.append(('__unwindfunclet$'+PARENT+'$1',0,2,32,3,None));return o,s,y,r
        self.assertIn('incomplete_or_extra_parent_generated_inventory',self.row(edit=edit)['blockers'])
    def test_wrong_metadata_edge_target(self):
        def edit(o,s,y,r):name,b,rels,f=s[2];s[2]=(name,b,[(off,D if off==16 else t,k) for off,t,k in rels],f);return o,s,y,r
        self.assertIn('generated_graph_identity_conflict',self.row(edit=edit)['blockers'])
    def test_original_truncated_section(self):
        def edit(o,s,y,r):return o[:-1],s,y,r
        self.assertEqual(self.diagnose(edit=edit)['error'],'PE_section_out_of_bounds')
    def test_whole_main_length_difference(self):
        def edit(o,s,y,r):name,b,rels,f=s[0];s[0]=(name,b+b'\x90',rels,f);y[0]=(*y[0][:-1],y[0][-1]+1);return o,s,y,r
        self.assertIn('complete_main_length_differs',self.row(edit=edit)['differences'])

if __name__=='__main__':unittest.main()
