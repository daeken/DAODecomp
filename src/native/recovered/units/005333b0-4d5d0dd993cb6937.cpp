typedef unsigned char u8;
typedef unsigned int u32;

struct C_00530d80 { u8 m0; u8* fn_00530d80(); };
struct C_005333b0 { void* m0; u8 m4; u8 pad5[3]; u8* fn_005333b0(); };

struct S_00533ac0_Elem { int m0; u8 pad4[20]; };
struct S_00533ac0_Table { u32 m0; u32 m4; S_00533ac0_Elem m_elems[1]; };
struct S_00533ac0_Holder { S_00533ac0_Table* m0; };
struct C_00533ac0 { S_00533ac0_Holder* m0; u32 m4; u32 fn_00533ac0(); };

struct C_00533d90 { u8 pad0[8]; u8* m8; u8* m_c; u32 m10; u32 m14; u32* m18; u32 m1c; void* fn_00533d90(u32 idx); };

struct S_00533dd0_Fields { u8* m0; u8* m4; u8 pad8[8]; u32* m10; u32 m14; };
struct S_00533dd0_Sub { u8 pad0[8]; S_00533dd0_Fields f; };
struct C_00533dd0 { u8 pad0[0x20]; S_00533dd0_Sub* m20; u8 pad24[4]; u32 m28; void* fn_00533dd0(u32 arg); };

struct S_00535070_Node { u8 pad0[0x10]; u32 m10; };
struct S_00535070_Elem { int m_next; S_00535070_Node* m_node; u8 pad8[16]; };
struct S_00535070_Table { u32 m0; u32 m_mask; S_00535070_Elem m_elems[1]; };
struct C_00535070 { S_00535070_Table* m0; int fn_00535070(void** key, u32 slot); };

struct S_005350e0_Node { u8 pad0[0x10]; u32 m10; };
struct S_005350e0_Elem { int m_next; S_005350e0_Node* m_node; u8 pad8[12]; };
struct S_005350e0_Table { u32 m0; u32 m_mask; S_005350e0_Elem m_elems[1]; };
struct C_005350e0 { S_005350e0_Table* m0; int fn_005350e0(void** key, u32 slot); };

struct S_005358d0_Node { u8 pad0[0x10]; u32 m10; };
struct S_005358d0_Elem { int m_next; S_005358d0_Node* m_node; u8 pad8[8]; };
struct S_005358d0_Table { u32 m0; u32 m_mask; S_005358d0_Elem m_elems[1]; };
struct C_005358d0 { S_005358d0_Table* m0; int fn_005358d0(void** key, u32 slot); };

// FUNCTION: DAO 0x00930D80
u8* __thiscall C_00530d80::fn_00530d80()
{
    u8* p = (u8*)this;
    while (*p != 0) {
        u8 c = *p;
        if (c == 0x2e) {
            if (p[1] != 0x2e) return p;
            ++p;
        } else if (c == 0x2f) {
            return p;
        }
        ++p;
    }
    return 0;
}

// FUNCTION: DAO 0x009333B0
u8* __thiscall C_005333b0::fn_005333b0()
{
    if (m4 != 0) {
        u8* p = (u8*)m0;
        if (p) return p + 0x10;
    } else {
        u8* p = (u8*)m0;
        if (p) return p + 0x6c;
    }
    return 0;
}

// FUNCTION: DAO 0x00933AC0
u32 __thiscall C_00533ac0::fn_00533ac0()
{
    S_00533ac0_Holder* h = m0;
    u32 i = m4;
    if (i > h->m0->m4) return i;
    ++i;
    m4 = i;
    if (i > h->m0->m4) return i;
    do {
        if (h->m0->m_elems[i].m0 != -2) break;
        ++i;
        m4 = i;
    } while (i <= h->m0->m4);
    return i;
}

// FUNCTION: DAO 0x00933D90
void* __thiscall C_00533d90::fn_00533d90(u32 idx)
{
    int delta = (int)((u32)m8 - (u32)m_c);
    u32 total = (u32)(delta >> 4) + ((m1c - 1) << 5);
    if (idx > total) return 0;
    u32 x = total - idx;
    u32 block = x >> 5;
    u32 off = (x & 0x1f) << 4;
    return (void*)((u8*)m18[block] + off);
}

// FUNCTION: DAO 0x00933DD0
void* __thiscall C_00533dd0::fn_00533dd0(u32 arg)
{
    u32 x = m28 - arg;
    S_00533dd0_Sub* sub = m20;
    S_00533dd0_Fields* f = &sub->f;
    int delta = (int)((u32)f->m0 - (u32)f->m4);
    u32 total = (u32)(delta >> 4) + ((f->m14 - 1) << 5);
    if (x > total) return 0;
    u32 block = x >> 5;
    u32 off = (x & 0x1f) << 4;
    return (void*)((u8*)f->m10[block] + off);
}

// FUNCTION: DAO 0x00935070
int __thiscall C_00535070::fn_00535070(void** key, u32 slot)
{
    S_00535070_Table* table = m0;
    u32 i = slot;
    S_00535070_Elem* elem = &table->m_elems[i];
    if (elem->m_next == -2) return -1;
    u32 mask = table->m_mask;
    S_00535070_Node* node = elem->m_node;
    if ((node->m10 & mask) != slot) return -1;
    for (;;) {
        node = elem->m_node;
        if ((node->m10 & mask) == slot && node == (S_00535070_Node*)*key)
            return (int)i;
        int next = elem->m_next;
        if (next == -1) return -1;
        i = (u32)next;
        elem = &table->m_elems[i];
    }
}

// FUNCTION: DAO 0x009350E0
int __thiscall C_005350e0::fn_005350e0(void** key, u32 slot)
{
    S_005350e0_Table* table = m0;
    u32 i = slot;
    S_005350e0_Elem* elem = &table->m_elems[i];
    if (elem->m_next == -2) return -1;
    u32 mask = table->m_mask;
    S_005350e0_Node* node = elem->m_node;
    if ((node->m10 & mask) != slot) return -1;
    for (;;) {
        node = elem->m_node;
        if ((node->m10 & mask) == slot && node == (S_005350e0_Node*)*key)
            return (int)i;
        int next = elem->m_next;
        if (next == -1) return -1;
        i = (u32)next;
        elem = &table->m_elems[i];
    }
}

// FUNCTION: DAO 0x009358D0
int __thiscall C_005358d0::fn_005358d0(void** key, u32 slot)
{
    S_005358d0_Table* table = m0;
    u32 i = slot;
    S_005358d0_Elem* elem = &table->m_elems[i];
    if (elem->m_next == -2) return -1;
    u32 mask = table->m_mask;
    S_005358d0_Node* node = elem->m_node;
    if ((node->m10 & mask) != slot) return -1;
    for (;;) {
        node = elem->m_node;
        if ((node->m10 & mask) == slot && node == (S_005358d0_Node*)*key)
            return (int)i;
        int next = elem->m_next;
        if (next == -1) return -1;
        i = (u32)next;
        elem = &table->m_elems[i];
    }
}
