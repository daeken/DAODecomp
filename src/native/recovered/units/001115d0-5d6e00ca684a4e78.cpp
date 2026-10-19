struct Block16_103c00 { unsigned int v0; unsigned int v1; unsigned int v2; unsigned int v3; };
struct Node_110d20 { unsigned char pad_0x00[8]; Node_110d20* next; unsigned char pad_0x0c[5]; unsigned char flag_0x11; };

// FUNCTION: DAO 0x503c00
Block16_103c00* __cdecl fn_00103c00(Block16_103c00* first, Block16_103c00* last, Block16_103c00* dest) {
    Block16_103c00* result = dest + (last - first);
    if (first != last) {
        unsigned int offset = (unsigned int)((char*)dest - (char*)first);
        do {
            Block16_103c00* p = (Block16_103c00*)((char*)first + offset);
            p->v0 = first->v0;
            p->v1 = first->v1;
            p->v2 = first->v2;
            p->v3 = first->v3;
            ++first;
        } while (first != last);
    }
    return result;
}

// FUNCTION: DAO 0x510d20
Node_110d20* __cdecl fn_00110d20(Node_110d20* p) {
    Node_110d20* eax = p;
    Node_110d20* ecx = eax->next;
    if (ecx->flag_0x11 != 0) {
        return eax;
    }
    do {
        Node_110d20* tmp = ecx;
        eax = tmp;
        ecx = tmp->next;
    } while (ecx->flag_0x11 == 0);
    return eax;
}

// FUNCTION: DAO 0x5115d0
unsigned short* __cdecl fn_001115d0(unsigned short* first, unsigned short* last, unsigned short* dest) {
    unsigned short* result = dest + (last - first);
    if (first != last) {
        unsigned int offset = (unsigned int)((char*)dest - (char*)first);
        do {
            unsigned short* p = (unsigned short*)((char*)first + offset);
            *p = *first;
            ++first;
        } while (first != last);
    }
    return result;
}
