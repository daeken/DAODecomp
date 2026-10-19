struct Block16_103c00 { unsigned int v0; unsigned int v1; unsigned int v2; unsigned int v3; };
struct Node_110d20 { unsigned char pad_00[8]; Node_110d20* next; unsigned char pad_0c[5]; unsigned char flag_0x11; };

// FUNCTION: DAO 0x503c00
Block16_103c00* __cdecl fn_00103c00(Block16_103c00* first, Block16_103c00* last, Block16_103c00* dest) {
    Block16_103c00* result = dest + (last - first);
    if (first != last) {
        int offset = (int)((char*)dest - (char*)first);
        do {
            Block16_103c00* out = (Block16_103c00*)((char*)first + offset);
            out->v0 = first->v0;
            out->v1 = first->v1;
            out->v2 = first->v2;
            out->v3 = first->v3;
            ++first;
        } while (first != last);
    }
    return result;
}

// FUNCTION: DAO 0x510d20
Node_110d20* __cdecl fn_00110d20(Node_110d20* p) {
    while (p->next->flag_0x11 == 0) {
        p = p->next;
    }
    return p;
}
