struct C649d70 {
    int f0;
    int f4;
    int f8;
    char pad0C[8];
    int* p14;
    int* p18;
    int fn_00649d70();
};

struct C649c4a0_Arg1 {
    char f0;
    unsigned char f1;
    char pad2[0x2e];
    int f30;
    char pad34[8];
    int f3c;
};

struct C649c4a0_Obj {
    char pad0[0x74];
    int f74;
    int f78;
    char pad7c[0x10];
    unsigned char f8c;
};

struct C649c520_Arg1 {
    char f0;
    unsigned char f1;
    char pad2[0x42];
    int f44;
};

struct C649c580_Arg1 {
    char pad0[0x30];
    int f30;
    char pad34[0x10];
    int f44;
};

struct C649e450 {
    char pad0[0xc];
    int f0c;
};

struct C649e550 {
    char pad0[0x30];
    int f30;
    int fn_0064e550(int arg);
};

struct C658d40 {
    char pad0[0x24];
    int f24;
    int fn_00658d40();
};

// FUNCTION: DAO 0x00A49D70
int C649d70::fn_00649d70() {
    int count;
    if (this->p14 == 0) {
        count = 0;
    } else {
        count = (int)(this->p18 - this->p14);
    }
    if (count == this->f4 * this->f8) {
        return 0;
    }
    return ((this->f4 + 1) / 2) * ((this->f8 - 1) / 2) + ((this->f4 - 1) / 2) + 1;
}

// FUNCTION: DAO 0x00A4C4A0
unsigned char __stdcall fn_0064c4a0(C649c4a0_Arg1* a, C649c4a0_Obj** b) {
    if (a->f1 == 0) {
        return 0;
    }
    if ((*b)->f8c != 0) {
        return 1;
    }
    int n = (*b)->f74 ? ((*b)->f78 - (*b)->f74) / 6 : 0;
    if (a->f30 < n - 1) {
        return 0;
    }
    n = (*b)->f74 ? ((*b)->f78 - (*b)->f74) / 6 : 0;
    if (a->f3c < n - 1) {
        return 0;
    }
    return 1;
}

// FUNCTION: DAO 0x00A4C520
unsigned char __stdcall fn_0064c520(C649c520_Arg1* a, C649c4a0_Obj** b) {
    if (a->f1 != 0) {
        return 1;
    }
    C649c4a0_Obj* obj = *b;
    int n;
    if (obj->f74 != 0) {
        n = (obj->f78 - obj->f74) / 6;
    } else {
        n = 0;
    }
    return (unsigned char)((n - a->f44) >= 2);
}

// FUNCTION: DAO 0x00A4C580
unsigned char __stdcall fn_0064c580(C649c580_Arg1* a, C649c4a0_Obj** b) {
    int value = a->f30;
    if (value - a->f44 > 2) {
        return 1;
    }
    C649c4a0_Obj* obj = *b;
    int n = obj->f74 ? (obj->f78 - obj->f74) / 6 : 0;
    if (value >= n - 1) {
        return 1;
    }
    return 0;
}

// FUNCTION: DAO 0x00A4CE10
void __cdecl fn_0064ce10(void*, unsigned int* first, void*, unsigned int* last) {
    if (last <= first) {
        return;
    }
    do {
        unsigned int left = *first;
        *first = *--last;
        ++first;
        *last = left;
    } while (first < last);
}

// FUNCTION: DAO 0x00A4E450
unsigned char __fastcall fn_0064e450(int half, C649e450* obj, int value) {
    if (value == -half) {
        return (unsigned char)(obj->f0c | 0x40);
    }
    if (value == half + 1) {
        return (unsigned char)(obj->f0c | 0xE0);
    }
    if (value == half - 1) {
        return (unsigned char)(obj->f0c | 0x80);
    }
    if (value == 1 - half) {
        return (unsigned char)(obj->f0c | 0xC0);
    }
    if (value == -1 - half) {
        return (unsigned char)(obj->f0c | 0xA0);
    }
    return 0;
}

// FUNCTION: DAO 0x00A4E550
int C649e550::fn_0064e550(int arg) {
    int c = this->f30;
    int half = (c + 1) / 2;
    int q = arg / half;
    int r = arg % half;
    return 2 * (c * q + r);
}

// FUNCTION: DAO 0x00A58D40
int C658d40::fn_00658d40() {
    int value = this->f24;
    if (value != 0) {
        return 0;
    }
    return 1;
}
