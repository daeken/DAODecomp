"""Lossless typed operand checks alongside reccmp's normalized-text score.

Functions importing Capstone do so lazily; descriptor controls need only stdlib.
"""
INTEGER=set('mov movzx movsx lea add adc sub sbb and or xor not neg inc dec cmp test shl sal shr sar rol ror rcl rcr imul mul idiv div cdq cwd cwde cbw push pop ret nop bswap xchg bt bts btr btc leave'.split())


def operand_key(value):
    kind=value['type'];width=value['width']
    if kind=='reg':return kind,width,value['register']
    if kind=='mem':return kind,width,value['segment'],value['base'],value['index'],value['scale'],value['displacement']
    if kind=='imm':return kind,width,value['value']
    raise ValueError('unsupported_operand')


def instruction_keys(descriptors):
    return [(i['mnemonic'],tuple(i['prefixes']),i['address_size'],tuple(operand_key(o) for o in i['operands'])) for i in descriptors]


def descriptors(instructions):
    from capstone import CS_OP_REG,CS_OP_IMM,CS_OP_MEM,CS_GRP_JUMP
    targets={i.address:n for n,i in enumerate(instructions)};result=[]
    for i in instructions:
        operands=[]
        for o in i.operands:
            value={'width':o.size}
            if o.type==CS_OP_REG:value.update(type='reg',register=i.reg_name(o.reg))
            elif o.type==CS_OP_MEM:value.update(type='mem',segment=i.reg_name(o.mem.segment),base=i.reg_name(o.mem.base),index=i.reg_name(o.mem.index),scale=o.mem.scale,displacement=o.mem.disp)
            elif o.type==CS_OP_IMM:
                immediate=o.imm
                if i.group(CS_GRP_JUMP):
                    if immediate not in targets:raise ValueError('unmapped_branch_target')
                    immediate=('instruction',targets[immediate])
                value.update(type='imm',value=immediate)
            else:raise ValueError('unknown_operand')
            operands.append(value)
        result.append({'mnemonic':i.mnemonic,'prefixes':list(i.prefix),'address_size':i.addr_size,'operands':operands})
    return result


def strict_operand_match(original,recompiled):
    return instruction_keys(descriptors(original))==instruction_keys(descriptors(recompiled))


def scope_reason(instructions,start,size,is_address=lambda value:False):
    from capstone import CS_OP_IMM,CS_OP_MEM,CS_GRP_JUMP
    for i in instructions:
        jump=i.group(CS_GRP_JUMP)
        if not(i.mnemonic in INTEGER or jump or i.mnemonic.startswith(('set','cmov'))):return 'unsupported_instruction'
        if jump and (not i.operands or i.operands[0].type!=CS_OP_IMM or not start<=i.operands[0].imm<start+size):return 'external_or_indirect_branch'
        for o in i.operands:
            if o.type==CS_OP_MEM:
                if o.mem.segment:return 'segmented_or_TLS_memory'
                if not o.mem.base and not o.mem.index:return 'absolute_memory'
                if not o.mem.base and o.mem.disp:return 'indexed_absolute_memory'
                if is_address(o.mem.disp & 0xffffffff):return 'memory_displacement_maps_global'
            if not jump and o.type==CS_OP_IMM and is_address(o.imm & 0xffffffff):return 'potential_unmapped_address_constant'
    return None
