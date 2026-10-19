"""Pinned byte-backed allocator-result receiver hypothesis; exact comparison accepts.

This deliberately small rule preserves the existing source argument expression.
It does not infer a constructor contract or implement native SEH. The complete
callee, finite original CFG and a complete target-aware AST must agree first.
"""
import re
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
from capstone.x86 import X86_OP_REG, X86_OP_IMM, X86_OP_MEM
from rapid_object import ast_match as m

class Unsupported(ValueError):
    pass


def decode(f):
    data = bytes.fromhex(f['original_bytes_hex'])
    md = Cs(CS_ARCH_X86, CS_MODE_32); md.detail = True
    xs = list(md.disasm(data, f['original_va']))
    if not xs or sum(i.size for i in xs) != len(data):
        raise Unsupported('incomplete_original_decode')
    if any(any(i.prefix) for i in xs if i.mnemonic not in ('mov',)):
        raise Unsupported('instruction_prefix')
    return xs


def callee_profile(f):
    xs = decode(f)
    if len(xs) != 4 or [i.mnemonic for i in xs] != ['mov', 'mov', 'add', 'ret'] or any(any(i.prefix) for i in xs):
        raise Unsupported('callee_not_complete_observed_constructor')
    a, b, c, d = [i.operands for i in xs]
    reg = lambda o, n: o.type == X86_OP_REG and o.size == 4 and xs[0].reg_name(o.reg) == n
    if not (len(a) == 2 and reg(a[0], 'eax') and reg(a[1], 'ecx')):
        raise Unsupported('callee_receiver_livein')
    if not (len(b) == 2 and b[0].type == X86_OP_MEM and b[0].size == 4 and not b[0].mem.segment and xs[0].reg_name(b[0].mem.base) == 'eax' and not b[0].mem.index and not b[0].mem.disp and b[1].type == X86_OP_IMM):
        raise Unsupported('callee_receiver_store')
    if not (len(c) == 2 and c[0].type == X86_OP_MEM and c[0].size == 4 and not c[0].mem.segment and not c[0].mem.base and not c[0].mem.index and c[1].type == X86_OP_IMM and c[1].imm == 1):
        raise Unsupported('callee_counter_effect')
    cleanup = 0 if not d else d[0].imm if len(d) == 1 and d[0].type == X86_OP_IMM else -1
    if cleanup not in (0, 4):
        raise Unsupported('callee_cleanup')
    # Observed bodies, not RET alone, establish this scoped family.
    expected = {0x4d2070: 0, 0x4d2080: 4}
    if expected.get(f['original_va']) != cleanup:
        raise Unsupported('callee_identity_or_cleanup')
    return {'va': f['original_va'], 'body_sha256': m.sha(bytes.fromhex(f['original_bytes_hex'])),
            'body_bytes': sum(i.size for i in xs), 'return_cleanup_bytes': cleanup,
            'receiver_livein': 'ecx', 'explicit_stack_word_reads': [], 'edx_read': False,
            'nested_calls': [], 'receiver_store_u32': b[1].imm & 0xffffffff,
            'counter_address': c[0].mem.disp & 0xffffffff, 'counter_add_u32': 1,
            'formal_semantics': 'unknown; existing source argument preserved'}


def original_evidence(f, profile, expected_argument, allocation_size=4):
    """Explore every CFG edge; reject cycles, split instructions and unknown calls.

    Values are provenance tags, not an emulator/equivalence proof. Only full word
    MOVs propagate tags. Branches involving the allocator result require the
    explicit zero predicate. All paths reaching the constructor must agree.
    """
    xs = decode(f); by = {i.address: i for i in xs}; end = xs[-1].address + xs[-1].size
    edges = {}; calls = []
    for i in xs:
        n = i.mnemonic; nxt = i.address + i.size
        # LOOP/JCXZ/XBEGIN and interrupt/far transfers are not ordinary
        # fallthrough, including in otherwise unmodeled suffixes.
        if any(g in i.groups for g in (1,2,3,4,5,7)) and n not in ('call','ret','je','jne','jmp'):
            raise Unsupported('unsupported_CFG_control_transfer:' + n)
        if n == 'call':
            if len(i.operands) != 1 or i.operands[0].type != X86_OP_IMM or any(i.prefix):
                raise Unsupported('indirect_or_prefixed_call')
            calls.append((i.address, i.operands[0].imm))
        if n.startswith('j'):
            if n not in ('je', 'jne', 'jmp') or len(i.operands) != 1 or i.operands[0].type != X86_OP_IMM:
                raise Unsupported('unsupported_CFG_edge')
            edges[i.address] = [i.operands[0].imm] + ([] if n == 'jmp' else [nxt])
        elif n == 'ret': edges[i.address] = []
        else: edges[i.address] = [nxt]
        if any(a not in by for a in edges[i.address]):
            raise Unsupported('CFG_outside_range_or_split_instruction')
    if [a for _, a in calls] != [0x413660, profile['va']]:
        raise Unsupported('not_unique_allocator_then_constructor')
    alloc_site, ctor_site = calls[0][0], calls[1][0]
    seen_nodes = set(); reached = []; terminal = 0
    todo = [(xs[0].address, {r: 'entry:' + r for r in ('eax','ecx','edx','ebx','esi','edi','ebp')}, 0, {}, None, None, False, ())]
    steps = 0
    while todo:
        pc, regs, sp, stack, predicate, nonnull, allocated, history = todo.pop()
        steps += 1
        if steps > 512 or len(history) > 128: raise Unsupported('CFG_budget')
        if pc in history: raise Unsupported('CFG_cycle')
        seen_nodes.add(pc); i = by[pc]; ops = i.operands; n = i.mnemonic
        regs = dict(regs); stack = dict(stack); history = history + (pc,)
        # Only receiver-reaching prefixes need value provenance. The complete
        # suffix CFG is retained/visited, including effects this rule does not
        # model. It is never rewritten or assigned equivalence credit.
        if regs.get('constructor_seen'):
            if n == 'ret': terminal += 1
            for dst in edges[pc]: todo.append((dst, regs, sp, stack, None, nonnull, allocated, history))
            continue
        def name(o): return i.reg_name(o.reg)
        def value(o):
            if o.type == X86_OP_REG and o.size == 4:
                return ('sp', sp) if name(o) == 'esp' else regs.get(name(o))
            if o.type == X86_OP_IMM: return o.imm & 0xffffffff
            if o.type == X86_OP_MEM and o.size == 4 and not o.mem.segment and i.reg_name(o.mem.base) == 'esp' and not o.mem.index:
                return stack.get(sp + o.mem.disp)
            return None
        if n == 'call':
            predicate = None
            if pc == alloc_site:
                if allocated or stack.get(sp) != allocation_size: raise Unsupported('allocator_setup_not_one_existing_size_word')
                regs.update(eax='allocation', ecx=None, edx=None); allocated = True
            else:
                if not allocated or nonnull is not True or regs.get('ecx') != 'allocation':
                    raise Unsupported('receiver_not_nonnull_allocator_result_on_all_paths')
                # Allocator leaves its argument word for the existing ADD ESP,4.
                # Constructor setup must have exactly the observed extra word.
                anchor = regs.get('allocator_sp')
                if anchor is None or sp != anchor + 4 - profile['return_cleanup_bytes']:
                    raise Unsupported('constructor_stack_setup_disagrees')
                arg = stack.get(sp) if profile['return_cleanup_bytes'] else None
                if arg != expected_argument: raise Unsupported('existing_argument_dataflow_disagrees')
                reached.append({'site_va': pc, 'receiver': 'allocator_return_eax', 'argument': arg,
                                'argument_words': profile['return_cleanup_bytes'] // 4, 'nonnull': True})
                sp += profile['return_cleanup_bytes']; regs.update(eax='constructor_return', ecx=None, edx=None, constructor_seen=True)
            if pc == alloc_site: regs['allocator_sp'] = sp
        elif n == 'push' and len(ops) == 1 and ops[0].size == 4:
            v = value(ops[0]); sp -= 4; stack[sp] = v
        elif n == 'pop' and len(ops) == 1 and ops[0].type == X86_OP_REG and ops[0].size == 4 and name(ops[0]) != 'esp':
            regs[name(ops[0])] = stack.get(sp); sp += 4
        elif n in ('add', 'sub') and len(ops) == 2 and ops[0].type == X86_OP_REG and name(ops[0]) == 'esp' and ops[0].size == 4 and ops[1].type == X86_OP_IMM:
            sp += ops[1].imm * (1 if n == 'add' else -1); predicate = None
        elif n == 'mov' and len(ops) == 2:
            if ops[0].type == X86_OP_REG:
                if ops[0].size != 4 or name(ops[0]) == 'esp': raise Unsupported('partial_register_or_stack_write')
                regs[name(ops[0])] = value(ops[1])
            elif ops[0].type == X86_OP_MEM:
                mem = ops[0].mem
                if not mem.segment and i.reg_name(mem.base) == 'esp' and not mem.index:
                    if ops[0].size != 4: raise Unsupported('partial_stack_store')
                    stack[sp + mem.disp] = value(ops[1])
                # Other writes are not removed/reordered by this proposal.
            else: raise Unsupported('mov_destination')
        elif n == 'lea' and len(ops) == 2 and ops[0].type == X86_OP_REG and ops[0].size == 4 and name(ops[0]) != 'esp':
            regs[name(ops[0])] = None
        elif n == 'xor' and len(ops) == 2 and ops[0].type == X86_OP_REG and ops[0].size == 4 and name(ops[0]) != 'esp':
            regs[name(ops[0])] = 0 if ops[1].type == X86_OP_REG and ops[0].reg == ops[1].reg else None; predicate = None
        elif n in ('cmp', 'test') and len(ops) == 2:
            a, b = value(ops[0]), value(ops[1])
            predicate = 'allocation_zero' if (n == 'cmp' and ((a == 'allocation' and b == 0) or (a == 0 and b == 'allocation'))) or (n == 'test' and a == b == 'allocation') else None
        elif n in ('je', 'jne'):
            if predicate != 'allocation_zero' or not allocated: raise Unsupported('unknown_branch_predicate')
        elif n == 'jmp': pass
        elif n == 'ret':
            terminal += 1
        else: raise Unsupported('unsupported_instruction:' + n)
        for k, dst in enumerate(edges[pc]):
            constraint = nonnull
            if n in ('je', 'jne'):
                constraint = (n == 'jne') if k == 0 else (n == 'je')
                if nonnull is not None and nonnull != constraint: continue
            todo.append((dst, regs, sp, stack, predicate, constraint, allocated, history))
    if seen_nodes != set(by) or not reached or not terminal:
        raise Unsupported('CFG_incomplete_or_no_constructor_path')
    return {'allocator_call_va': alloc_site, 'constructor_call_va': ctor_site,
            'decoded_instructions': len(xs), 'visited_instructions': len(seen_nodes),
            'paths_reaching_constructor': reached, 'terminal_paths': terminal,
            'callee': profile, 'CFG_complete': True, 'semantic_equivalence_claim': False}


def strip(n):
    while n.get('kind') in ('ImplicitCastExpr','ParenExpr') and len(n.get('inner',[])) == 1: n = n['inner'][0]
    return n


def rewrite(source, ast, report, callees):
    if not source.isascii() or ast.get('kind') != 'TranslationUnitDecl' or len(report.get('functions',[])) != 1:
        raise Unsupported('source_AST_report_identity')
    raw = source.encode(); nodes = list(m.fix.walk(ast)); f = report['functions'][0]
    if report.get('source_sha256') != m.sha(raw) or report.get('module_sha256') != m.PIN: raise Unsupported('bound_source_or_module_identity')
    if any(n.get('isInvalid') or n.get('containsErrors') or n.get('kind') in ('RecoveryExpr','UnresolvedLookupExpr') for n in nodes): raise Unsupported('incomplete_AST')
    own = [n for n in nodes if n.get('kind') == 'FunctionDecl' and n.get('name') == 'fn_%08x' % f['rva'] and any(c.get('kind') == 'CompoundStmt' for c in n.get('inner',[]))]
    if len(own) != 1: raise Unsupported('stable_function_identity')
    fn = own[0]; body = next(c for c in fn['inner'] if c.get('kind') == 'CompoundStmt'); bn = list(m.fix.walk(body))
    if any('spellingLoc' in p or 'expansionLoc' in p for n in [fn]+bn for p in n.get('range',{}).values()): raise Unsupported('macro_source_span')
    aliases = {n['name']: n['type']['qualType'] for n in nodes if n.get('kind') == 'TypedefDecl'}
    def span(n):
        s = m.fix.offsets(n)
        if not s or not (0 <= s[0] < s[1] <= len(raw)): raise Unsupported('invalid_source_span')
        return s
    def text(n):
        a,b = span(n); return raw[a:b].decode()
    off = fn.get('loc',{}).get('offset')
    if type(off) is not int or raw[off:off+len(fn['name'])].decode() != fn['name']: raise Unsupported('function_source_binding')
    calls = []
    for n in bn:
        if n.get('kind') == 'CallExpr' and n.get('inner'):
            d = strip(n['inner'][0]).get('referencedDecl',{})
            if re.fullmatch(r'fn_[0-9a-f]{8}', d.get('name','')): calls.append((n,d))
    calls.sort(key=lambda x: span(x[0]))
    if len(calls) != 2 or calls[0][1]['name'] != 'fn_00013660' or calls[1][1]['name'] not in ('fn_000d2070','fn_000d2080'): raise Unsupported('source_call_sequence')
    alloc, ctor = calls[0][0], calls[1][0]; declref = calls[1][1]; target = 0x400000 + int(declref['name'][3:],16)
    if {v for k,v in report['symbol_addresses'].items() if re.search(r'(?:^|[?_])'+declref['name']+r'(?=@|$)',k)} != {target}: raise Unsupported('target_symbol_binding')
    if {v for k,v in report['symbol_addresses'].items() if re.search(r'(?:^|[?_])fn_00013660(?=@|$)',k)} != {0x413660}: raise Unsupported('allocator_symbol_binding')
    if target not in callees: raise Unsupported('callee_capture_missing')
    profile = callee_profile(callees[target]); args = ctor['inner'][1:]
    allocargs = alloc['inner'][1:]
    if len(allocargs) != 1 or strip(allocargs[0]).get('kind') != 'IntegerLiteral' or not (0 < int(strip(allocargs[0]).get('value','0')) < (1 << 32)): raise Unsupported('existing_allocator_size_not_constant_word')
    allowed = {'fn_00013660', declref['name'], '__readfsdword', '__writefsdword', '_AddressOfReturnAddress'}
    if any(strip(n['inner'][0]).get('referencedDecl',{}).get('name') not in allowed for n in bn if n.get('kind') == 'CallExpr' and n.get('inner')): raise Unsupported('additional_source_call')
    params = [c for c in fn['inner'] if c.get('kind') == 'ParmVarDecl']
    expected = None; argument_type = None
    if profile['return_cleanup_bytes']:
        if len(args) != 1 or len(params) != 1 or '__attribute__((fastcall))' not in fn['type']['qualType']: raise Unsupported('existing_argument_or_entry_ABI_unknown')
        p = params[0]; a = strip(args[0])
        if a.get('kind') != 'DeclRefExpr' or a.get('referencedDecl',{}).get('id') != p['id'] or m.fix.canonical_type(p['type']['qualType'], aliases) not in ('unsigned int', 'int'): raise Unsupported('existing_argument_not_bound_word_parameter')
        if len([n for n in bn if n.get('kind') == 'DeclRefExpr' and n.get('referencedDecl',{}).get('id') == p['id'] and span(n)[0] <= span(ctor)[1]]) != 1: raise Unsupported('parameter_other_uses')
        expected = 'entry:ecx'; argument_type = m.fix.canonical_type(p['type']['qualType'], aliases)
    elif args or params: raise Unsupported('zero_argument_shape')
    # The allocator result must initialize exactly one own pointer local in a
    # direct body assignment; no syntactic/name-only receiver guessing.
    assignments = [n for n in body['inner'] if n.get('kind') == 'BinaryOperator' and n.get('opcode') == '=' and any(x is alloc for x in m.fix.walk(n))]
    if len(assignments) != 1: raise Unsupported('allocator_not_direct_assignment')
    assign = assignments[0]; lhs = strip(assign['inner'][0]); rid = lhs.get('referencedDecl',{}).get('id')
    rhs = assign['inner'][1]
    while rhs.get('kind') in ('CStyleCastExpr','ImplicitCastExpr','ParenExpr') and len(rhs.get('inner',[])) == 1: rhs = rhs['inner'][0]
    if rhs is not alloc or lhs.get('kind') != 'DeclRefExpr': raise Unsupported('allocator_assignment_shape')
    locals_ = [n for n in bn if n.get('kind') == 'VarDecl' and n.get('id') == rid]
    if len(locals_) != 1 or locals_[0].get('init') or m.fix.type_kind(locals_[0]['type']['qualType'],aliases) != 'pointer' or 'volatile' in locals_[0]['type']['qualType']: raise Unsupported('receiver_storage')
    receiver = locals_[0]['name']
    writes = [n for n in bn if n.get('kind') in ('BinaryOperator','CompoundAssignOperator','UnaryOperator') and n.get('opcode') in ('=','+=','-=','++','--','&') and n.get('inner') and strip(n['inner'][0]).get('referencedDecl',{}).get('id') == rid]
    if writes != [assign]: raise Unsupported('receiver_mutation_or_address_escape')
    ifs = [n for n in body['inner'] if n.get('kind') == 'IfStmt' and any(x is ctor for x in m.fix.walk(n))]
    if len(ifs) != 1 or len(ifs[0]['inner']) != 2: raise Unsupported('constructor_not_simple_null_guard')
    cond, then = ifs[0]['inner']; cond = strip(cond)
    if cond.get('kind') != 'BinaryOperator' or cond.get('opcode') != '!=' or len(cond.get('inner',[])) != 2: raise Unsupported('null_guard_condition')
    l,r = cond['inner']
    zero = r
    while zero.get('kind') in ('CStyleCastExpr','ImplicitCastExpr','ParenExpr') and len(zero.get('inner',[])) == 1: zero = zero['inner'][0]
    if strip(l).get('referencedDecl',{}).get('id') != rid or zero.get('kind') != 'IntegerLiteral' or zero.get('value') != '0': raise Unsupported('null_guard_receiver')
    if then.get('kind') != 'CompoundStmt' or not then.get('inner') or then['inner'][0] is not ctor: raise Unsupported('constructor_not_first_guarded_statement')
    if span(assign)[1] >= span(ifs[0])[0]: raise Unsupported('receiver_not_initialized_before_guard')
    # No additional receiver use before the call except the assignment/guard.
    early = [n for n in bn if n.get('kind') == 'DeclRefExpr' and n.get('referencedDecl',{}).get('id') == rid and span(n)[0] < span(ctor)[0]]
    if len(early) != 2: raise Unsupported('receiver_early_use_or_escape')
    declarations = [n for n in nodes if n.get('kind') == 'FunctionDecl' and n.get('id') == declref.get('id')]
    if len(declarations) != 1 or not any(n.get('kind') == 'LinkageSpecDecl' and n.get('language') == 'C' and declarations[0] in n.get('inner',[]) for n in ast.get('inner',[])) or declarations[0]['type']['qualType'] != 'unsigned int (...) __attribute__((cdecl))' or any(c.get('kind') == 'CompoundStmt' for c in declarations[0].get('inner',[])): raise Unsupported('target_not_provisional_declaration')
    if len([n for n in bn if n.get('kind') == 'DeclRefExpr' and n.get('referencedDecl',{}).get('id') == declref.get('id')]) != 1: raise Unsupported('target_other_uses')
    proof = original_evidence(f, profile, expected, int(strip(allocargs[0])['value']))
    a,b = span(ctor); old = raw[a:b].decode(); name = declref['name']
    if not re.fullmatch(re.escape(name)+r'\s*\('+ (re.escape(text(args[0])) if args else r'\s*') +r'\)',old): raise Unsupported('call_source_binding')
    types = 'void *' + (', ' + argument_type if args else '')
    values = '(void *)' + receiver + (', ' + text(args[0]) if args else '')
    replacement = '((unsigned int (__thiscall *)('+types+'))(&'+name+'))('+values+')'
    candidate = raw[:a]+replacement.encode()+raw[b:]
    return candidate.decode(), {'kind':'allocator_result_receiver_hypothesis','status':'UNVALIDATED','source_sha256':m.sha(raw),'candidate_sha256':m.sha(candidate),'edit':{'span':[a,b],'before':old,'replacement':replacement},'receiver_declaration_id':rid,'original':proof,'semantic_preservation_claim':False,'acceptance':'unchanged complete relocation-aware comparator only','remaining_unknowns':['native SEH and frame','callee formal semantics','other provisional inputs/types']}
