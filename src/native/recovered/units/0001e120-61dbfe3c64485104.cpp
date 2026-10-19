struct C_0041e120 { unsigned char field0; unsigned char* fn_0001e120(); };
struct C_0041e2d0 { unsigned int unknown0; unsigned int unknown1; unsigned int slots[16]; void fn_0001e2d0(unsigned int value); };
struct C_0041e300 { unsigned int unknown0; unsigned int unknown1; unsigned int slots[16]; void fn_0001e300(unsigned int value); };
struct C_0041f8d0 { unsigned int field0; unsigned int field4; unsigned short field8; unsigned char padA[2]; unsigned int fieldC; unsigned int field10; unsigned int field14; unsigned int field18; unsigned int field1C; unsigned int field20; unsigned int field24; unsigned int field28; unsigned char field2C; unsigned char pad2D[3]; unsigned int field30; unsigned int field34; unsigned int field38; unsigned char field3C; unsigned char pad3D[3]; void fn_0001f8d0(const C_0041f8d0* src); };
struct C_0041fce0 { unsigned char pad0[0x20]; unsigned int field20; bool fn_0001fce0() const; };
struct C_00420960 { unsigned char pad0[0x14]; int field14; unsigned char pad18[0x2e40 - 0x18]; unsigned char entries[32][0x2c]; unsigned char* fn_00020960(); };
struct C_00420b10 { unsigned char pad0[0x90]; unsigned int field90; unsigned int field94; void fn_00020b10(unsigned int a, unsigned int b); };
struct C_00420ff0_Entry { unsigned char pad0[4]; unsigned int f4; unsigned int f8; unsigned char padC[0x10]; unsigned int f1C; unsigned int f20; unsigned int f24; unsigned int f28; unsigned int f2C; unsigned int f30; unsigned char pad34[0x18]; };
struct C_00420ff0 { int index; C_00420ff0_Entry entries[10]; bool fn_00020ff0(unsigned int a1, unsigned int a2, unsigned int a3, unsigned int a4, unsigned int a5, unsigned int a6, unsigned int a7, unsigned int a8); };
struct C_00421070 { void* head; void fn_00021070(void* base, unsigned int size, unsigned int blockSize, unsigned int alignment, unsigned int arg5); };
struct TreeNode { TreeNode* field0; TreeNode* field4; TreeNode* field8; unsigned char fieldC; };
struct C_00423df0 { unsigned char pad[0x38]; unsigned char field38; void* fn_00023df0(); };
struct C_00423e70 { unsigned char pad[0x50]; unsigned char field50; void* fn_00023e70(); };
struct C_00424010 { unsigned char pad[0xc]; unsigned short fieldC; unsigned short fn_00024010() const; };
// FUNCTION: DAO 0x0041E120
unsigned char* C_0041e120::fn_0001e120() { this->field0 = 0; return reinterpret_cast<unsigned char*>(this); }
// FUNCTION: DAO 0x0041E2D0
void C_0041e2d0::fn_0001e2d0(unsigned int value) { for (unsigned int i = 0; i < 16; ++i) { if (this->slots[i] == 0) { this->slots[i] = value; return; } } }
// FUNCTION: DAO 0x0041E300
void C_0041e300::fn_0001e300(unsigned int value) { for (unsigned int i = 0; i < 16; ++i) { if (this->slots[i] == value) { this->slots[i] = 0; return; } } }
// FUNCTION: DAO 0x0041F8D0
void C_0041f8d0::fn_0001f8d0(const C_0041f8d0* src) { if (this == src) return; this->field4 = src->field4; this->field8 = src->field8; this->field10 = src->field10; this->field14 = src->field14; this->field18 = src->field18; this->field1C = src->field1C; this->field20 = src->field20; this->field24 = src->field24; this->fieldC = src->fieldC; if (src->field30 != 0) { this->field30 = src->field30; this->field34 = src->field34; this->field38 = src->field38; } else { this->field34 = 0; this->field30 = 0; this->field38 = 1; } this->field38 = src->field38; this->field3C = 0; this->field28 = src->field28; this->field2C = src->field2C; }
// FUNCTION: DAO 0x0041FCE0
bool C_0041fce0::fn_0001fce0() const { return this->field20 != 0; }
// FUNCTION: DAO 0x00420960
unsigned char* C_00420960::fn_00020960() { unsigned char* entry = &this->entries[0][0]; for (unsigned int i = 0; i < 0x20; ++i, entry += 0x2c) { if (*entry == 0) { *entry = 1; int n = (int)(i + 1); if (n > this->field14) this->field14 = n; return entry; } } return 0; }
// FUNCTION: DAO 0x00420B10
void C_00420b10::fn_00020b10(unsigned int a, unsigned int b) { if (this->field90 == 0 && this->field94 == 0) { this->field90 = a; this->field94 = b; } }
// FUNCTION: DAO 0x00420BC0
unsigned __int64 fn_00020bc0(const short* data, unsigned int count) { unsigned int ecx = 0; unsigned int esi = 0; unsigned int n = count - (count & 1u); const short* p = data; while (n != 0) { int word = *p; unsigned int eax = (unsigned int)word; unsigned int edx = (word < 0) ? 0xFFFFFFFFu : 0u; unsigned int old = ecx; ecx = ecx + eax; unsigned int carry = (ecx < old) ? 1u : 0u; esi = esi + edx + carry; if ((ecx & 0xFFFF0000u) != 0) { ecx = ecx & 0xFFFFu; esi = 0; ecx = ecx + 1; unsigned int carry2 = (ecx == 0) ? 1u : 0u; esi = esi + carry2; } ++p; n -= 2; } unsigned __int64 result = (unsigned __int64)(ecx & 0xFFFFu); return ~result; }
// FUNCTION: DAO 0x00420FF0
bool C_00420ff0::fn_00020ff0(unsigned int a1, unsigned int a2, unsigned int a3, unsigned int a4, unsigned int a5, unsigned int a6, unsigned int a7, unsigned int a8) { int i = this->index; if (i == -1) { i = 0; this->index = 0; } else if (i >= 10) { return false; } C_00420ff0_Entry* e = &this->entries[i]; e->f4 = a1; e->f1C = a2; e->f20 = a3; e->f24 = a4; e->f28 = a5; e->f2C = a6; e->f30 = a7; e->f8 = a8; this->index = i + 1; return true; }
// FUNCTION: DAO 0x00421070
void C_00421070::fn_00021070(void* base, unsigned int size, unsigned int blockSize, unsigned int alignment, unsigned int arg5) { if (alignment < 1) alignment = 1; if (blockSize < 4) blockSize = (~(alignment - 1)) & (alignment + 3); unsigned int baseAddr = reinterpret_cast<unsigned int>(base); unsigned char* start = reinterpret_cast<unsigned char*>((baseAddr + alignment - 1) & ~(alignment - 1)); this->head = start; unsigned int count = size / blockSize; unsigned char* end = reinterpret_cast<unsigned char*>(baseAddr + (count - 1) * blockSize); unsigned char* p = start; while (p < end) { unsigned char* next = p + blockSize; *reinterpret_cast<unsigned char**>(p) = next; p = next; } *reinterpret_cast<unsigned char**>(p) = 0; }
// FUNCTION: DAO 0x004210E0
TreeNode* fn_000210e0(TreeNode* n) { TreeNode* eax = n->field0; TreeNode* ecx = n; if (eax != 0) { ecx = eax->field4; while (ecx != 0) { eax = ecx; ecx = eax->field4; } return eax; } eax = ecx->field8; if (ecx == eax->field0) { do { ecx = eax; eax = eax->field8; } while (ecx == eax->field0); } if (ecx->field0 == eax) eax = ecx; return eax; }
// FUNCTION: DAO 0x00421120
TreeNode* fn_00021120(TreeNode* n) { TreeNode* ecx = n; TreeNode* edx = ecx->field8; if (edx->field8 == ecx && ecx->fieldC == 0) return ecx->field0; TreeNode* eax = ecx->field4; if (eax != 0) { ecx = eax->field0; while (ecx != 0) { eax = ecx; ecx = eax->field0; } return eax; } eax = edx; while (ecx == eax->field4) { ecx = eax; eax = eax->field8; } return eax; }
// FUNCTION: DAO 0x00421160
void fn_00021160(TreeNode* x, TreeNode* root) { TreeNode* y = x->field0; TreeNode* b = y->field4; x->field0 = b; if (b != 0) b->field8 = x; TreeNode* parent = x->field8; y->field8 = parent; if (x == root) { y->field4 = x; x->field8 = y; return; } TreeNode* p = x->field8; if (x == p->field4) { p->field4 = y; y->field4 = x; x->field8 = y; return; } p->field0 = y; y->field4 = x; x->field8 = y; }
// FUNCTION: DAO 0x00423DF0
void* C_00423df0::fn_00023df0() { return &this->field38; }
// FUNCTION: DAO 0x00423E70
void* C_00423e70::fn_00023e70() { return &this->field50; }
// FUNCTION: DAO 0x00424010
unsigned short C_00424010::fn_00024010() const { return this->fieldC; }
