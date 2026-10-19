typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

struct C_0052fa40 { u8 m0; int fn_0052fa40(); };
struct S_00530c00_Node { u8 pad0[0xa4]; void* m_a4; };
struct C_00530c00 { void* m0; void* m4; C_00530c00* fn_00530c00(S_00530c00_Node* node, void* value); };
struct C_00530d80 { u8 m0; u8* fn_00530d80(); };
struct C_00531870 { u8 pad0[8]; u32 m8; u32 m_c; u32 m10; u32 m14; u32 fn_00531870(); };
struct C_005333b0 { void* m0; u8 m4; u8 pad5[3]; u8* fn_005333b0(); };
struct C_00533850 { u8 pad0[0xd8]; u32* m_d8; u32 m_dc; u32 fn_00533850(u32 idx); };
struct S_00533ac0_Elem { int m0; u8 pad4[20]; };
struct S_00533ac0_Table { u32 m0; u32 m4; };
struct S_00533ac0_Holder { S_00533ac0_Table* m0; };
struct C_00533ac0 { S_00533ac0_Holder* m0; u32 m4; u32 fn_00533ac0(); };
struct C_00533d90 { u8 pad0[8]; u8* m8; u8* m_c; u32 m10; u32 m14; u32* m_18; u32 m_1c; void* fn_00533d90(u32 idx); };
struct S_00533dd0_Sub { u8 pad0[8]; u8* m8; u8* m_c; u32 m10; u32 m14; u32* m_18; u32 m_1c; };
struct C_00533dd0 { u8 pad0[0x20]; S_00533dd0_Sub* m20; u32 m28; void* fn_00533dd0(u32 arg); };
struct S_00535070_Node { u8 pad0[0x10]; u32 m10; };
struct S_00535070_Elem { int m_next; S_00535070_Node* m_node; u8 pad[16]; };
struct S_00535070_Table { u32 m0; u32 m_mask; };
struct C_00535070 { S_00535070_Table* m0; int fn_00535070(void** key, u32 slot); };
struct S_005350e0_Node { u8 pad0[0x10]; u32 m10; };
struct S_005350e0_Elem { int m_next; S_005350e0_Node* m_node; u8 pad[12]; };
struct S_005350e0_Table { u32 m0; u32 m_mask; };
struct C_005350e0 { S_005350e0_Table* m0; int fn_005350e0(void** key, u32 slot); };
struct S_005358d0_Node { u8 pad0[0x10]; u32 m10; };
struct S_005358d0_Elem { int m_next; S_005358d0_Node* m_node; u8 pad[8]; };
struct S_005358d0_Table { u32 m0; u32 m_mask; };
struct C_005358d0 { S_005358d0_Table* m0; int fn_005358d0(void** key, u32 slot); };
struct C_005431c0 { u8 pad0[2]; u16 m2; u8 pad4[2]; u16 m6; void fn_005431c0(int v); };
struct S_00543a50 { u8 pad0[0x10]; u8 m10; u8 m11; u8 m12; u8 m13; u8 m14; u8 m15; u8 m16; u8 pad17[0x1c - 0x17]; u16 m1c; u16 m1e; u32 m20; };
struct C_00543a50 { u8 pad0[7]; u8 m7; u8 m8; u8 m9; u8 ma; u8 padb[0x13 - 0xb]; u8 m13; u8 m14; u8 m15; u8 m16; u8 pad17[0x18 - 0x17]; u32 m18; u16 m1c; u16 m1e; void fn_00543a50(S_00543a50* src); };
struct C_00582910 { u8 m0; int fn_00582910(); };

// FUNCTION: DAO 0x0092FA40
int __thiscall C_0052fa40::fn_0052fa40()
{
    if (m0 == 3 || m0 == 4) return 1;
    return 0;
}

// FUNCTION: DAO 0x00930C00
C_00530c00* __thiscall C_00530c00::fn_00530c00(S_00530c00_Node* node, void* value)
{
    m0 = node;
    m4 = node->m_a4;
    node->m_a4 = value;
    return this;
}

// FUNCTION: DAO 0x00930D80
u8* __thiscall C_00530d80::fn_00530d80()
{
    u8* p = (u8*)this;
    if (*p == 0) return 0;
    for (;;) {
        u8 c = *p;
        if (c == 0x2e) {
            if (p[1] != 0x2e) return p;
            p += 1;
        } else if (c == 0x2f) {
            return p;
        }
        p += 1;
        if (*p == 0) return 0;
    }
}

// FUNCTION: DAO 0x00931870
u32 __thiscall C_00531870::fn_00531870()
{
    u32 v = m8;
    if (v > m_c) return v - 0x10u;
    return m14;
}

// FUNCTION: DAO 0x009333B0
u8* __thiscall C_005333b0::fn_005333b0()
{
    u8* p = (u8*)m0;
    if (!p) return 0;
    if (m4 != 0) return p + 0x10;
    return p + 0x6c;
}

// FUNCTION: DAO 0x00933850
u32 __thiscall C_00533850::fn_00533850(u32 idx)
{
    u32 d = m_dc - idx;
    if (d == 0) return 0;
    return m_d8[d - 1];
}

// FUNCTION: DAO 0x00933AC0
u32 __thiscall C_00533ac0::fn_00533ac0()
{
    S_00533ac0_Table* table = m0->m0;
    u32 idx = m4;
    if (idx > table->m4) return idx;
    idx++;
    m4 = idx;
    table = m0->m0;
    if (idx > table->m4) return idx;
    S_00533ac0_Elem* elem = (S_00533ac0_Elem*)((u8*)table + 8 + idx * 24);
    while (idx <= table->m4 && elem->m0 == -2) {
        idx++;
        m4 = idx;
        table = m0->m0;
        elem = (S_00533ac0_Elem*)((u8*)table + 8 + idx * 24);
    }
    return idx;
}

// FUNCTION: DAO 0x00933D90
void* __thiscall C_00533d90::fn_00533d90(u32 idx)
{
    int delta = (int)((u32)m8 - (u32)m_c);
    delta >>= 4;
    u32 total = (u32)delta + ((m_1c - 1) << 5);
    if (idx > total) return 0;
    u32 x = total - idx;
    u32 block = x >> 5;
    u32 off = (x & 0x1f) << 4;
    return (void*)((u8*)m_18[block] + off);
}

// FUNCTION: DAO 0x00933DD0
void* __thiscall C_00533dd0::fn_00533dd0(u32 arg)
{
    S_00533dd0_Sub* sub = m20;
    int delta = (int)((u32)sub->m8 - (u32)sub->m_c);
    delta >>= 4;
    u32 total = (u32)delta + ((sub->m_1c - 1) << 5);
    u32 x = m28 - arg;
    if (x > total) return 0;
    u32 block = x >> 5;
    u32 off = (x & 0x1f) << 4;
    return (void*)((u8*)sub->m_18[block] + off);
}

// FUNCTION: DAO 0x00935070
int __thiscall C_00535070::fn_00535070(void** key, u32 slot)
{
    S_00535070_Table* table = m0;
    S_00535070_Elem* elem = (S_00535070_Elem*)((u8*)table + 8 + slot * 24);
    if (elem->m_next == -2) return -1;
    u32 mask = table->m_mask;
    S_00535070_Node* node = elem->m_node;
    if ((node->m10 & mask) != slot) return -1;
    int index = (int)slot;
    for (;;) {
        node = elem->m_node;
        if ((node->m10 & mask) == slot && node == (S_00535070_Node*)*key) return index;
        int next = elem->m_next;
        if (next == -1) return -1;
        index = next;
        elem = (S_00535070_Elem*)((u8*)table + 8 + (u32)next * 24);
    }
}

// FUNCTION: DAO 0x009350E0
int __thiscall C_005350e0::fn_005350e0(void** key, u32 slot)
{
    S_005350e0_Table* table = m0;
    S_005350e0_Elem* elem = (S_005350e0_Elem*)((u8*)table + 8 + slot * 20);
    if (elem->m_next == -2) return -1;
    u32 mask = table->m_mask;
    S_005350e0_Node* node = elem->m_node;
    if ((node->m10 & mask) != slot) return -1;
    int index = (int)slot;
    for (;;) {
        node = elem->m_node;
        if ((node->m10 & mask) == slot && node == (S_005350e0_Node*)*key) return index;
        int next = elem->m_next;
        if (next == -1) return -1;
        index = next;
        elem = (S_005350e0_Elem*)((u8*)table + 8 + (u32)next * 20);
    }
}

// FUNCTION: DAO 0x009358D0
int __thiscall C_005358d0::fn_005358d0(void** key, u32 slot)
{
    S_005358d0_Table* table = m0;
    S_005358d0_Elem* elem = (S_005358d0_Elem*)((u8*)table + 8 + slot * 16);
    if (elem->m_next == -2) return -1;
    u32 mask = table->m_mask;
    S_005358d0_Node* node = elem->m_node;
    if ((node->m10 & mask) != slot) return -1;
    int index = (int)slot;
    for (;;) {
        node = elem->m_node;
        if ((node->m10 & mask) == slot && node == (S_005358d0_Node*)*key) return index;
        int next = elem->m_next;
        if (next == -1) return -1;
        index = next;
        elem = (S_005358d0_Elem*)((u8*)table + 8 + (u32)next * 16);
    }
}

// FUNCTION: DAO 0x009431C0
void __thiscall C_005431c0::fn_005431c0(int v)
{
    if (v < 0) {
        m6 = (u16)(m6 | 0x40);
        u32 u = (u32)v;
        u = 0u - u;
        m2 = (u16)u;
    } else {
        m6 = (u16)(m6 & 0xffbf);
        m2 = (u16)v;
    }
}

// FUNCTION: DAO 0x00943A50
void __thiscall C_00543a50::fn_00543a50(S_00543a50* src)
{
    m8 = src->m10;
    m9 = src->m11;
    m7 = 0x80;
    ma = src->m12;
    u8 d = src->m13;
    if (d & 1) return;
    m13 = (u8)(d & 0xfe);
    m14 = src->m14;
    m15 = src->m15;
    m16 = src->m16;
    m18 = src->m20;
    m1c = src->m1c;
    m1e = src->m1e;
}

// FUNCTION: DAO 0x00982910
int __thiscall C_00582910::fn_00582910()
{
    if (m0 == 5 || m0 == 2 || m0 == 1 || m0 == 3 || m0 == 4) return 1;
    return 0;
}
