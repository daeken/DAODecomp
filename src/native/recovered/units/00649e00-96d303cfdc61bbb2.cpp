struct C649d70 {
    int f0;
    int f4;
    int f8;
    char pad0C[8];
    int* p14;
    int* p18;
    int fn_00649d70();
};

struct C649ba70 {
    char pad0[0x30];
    int f30;
    char pad34[8];
    int f3c;
    char pad40[4];
    int f44;
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

struct C649c520_Container {
    char pad0[4];
    int f4;
    int f8;
};

struct C649c520_Obj {
    char pad0[0x70];
    C649c520_Container f70;
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
    int a = this->f4;
    int b = this->f8;
    if (count != a * b) {
        return ((a + 1) / 2) * ((b - 1) / 2) + ((a - 1) / 2) + 1;
    }
    return 0;
}

// FUNCTION: DAO 0x00A49E00
void __cdecl fn_00649e00(unsigned int* dst, unsigned int count, const unsigned int* src) {
    if (count <= 0) {
        return;
    }
    do {
        if (dst != 0) {
            *dst = *src;
        }
        --count;
        ++dst;
    } while (count > 0);
}

// FUNCTION: DAO 0x00A4BA70
int __stdcall fn_0064ba70(C649ba70* p, int) {
    int value = p->f3c;
    int diff = value - p->f44;
    if (diff <= 5 && value != p->f30) {
        return 0;
    }
    return 1;
}

// FUNCTION: DAO 0x00A4C4A0
unsigned char __stdcall fn_0064c4a0(C649c4a0_Arg1* a, C649c4a0_Obj** b) {
    C649c4a0_Obj* obj;
    if (a->f1 == 0) {
        return 0;
    }
    obj = *b;
    if (obj->f8c != 0) {
        return 1;
    }
    int n = obj->f74;
    if (n != 0) {
        n = (obj->f78 - n) / 6;
    }
    if (a->f30 < n - 1) {
        return 0;
    }
    n = obj->f74;
    if (n != 0) {
        n = (obj->f78 - n) / 6;
    }
    if (a->f3c < n - 1) {
        return 0;
    }
    return 1;
}

// FUNCTION: DAO 0x00A4C520
unsigned char __stdcall fn_0064c520(C649c520_Arg1* a, C649c520_Obj** b) {
    if (a->f1 != 0) {
        return 1;
    }
    C649c520_Obj* obj = *b;
    int n = obj->f70.f4;
    if (n != 0) {
        n = (obj->f70.f8 - n) / 6;
    }
    return (unsigned char)((n - a->f44) >= 2);
}

// FUNCTION: DAO 0x00A4C580
unsigned char __stdcall fn_0064c580(C649c580_Arg1* a, C649c520_Obj** b) {
    int value = a->f30;
    if (value - a->f44 <= 2) {
        C649c520_Obj* obj = *b;
        int n = obj->f70.f4;
        if (n != 0) {
            n = (obj->f70.f8 - n) / 6;
        }
        if (value < n - 1) {
            return 0;
        }
    }
    return 1;
}

// FUNCTION: DAO 0x00A4CE10
void __cdecl fn_0064ce10(void*, unsigned int* first, void*, unsigned int* last) {
    if (first >= last) {
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
    int half = (this->f30 + 1) / 2;
    int q = arg / half;
    int r = arg % half;
    return 2 * (this->f30 * q + r);
}

// FUNCTION: DAO 0x00A58D40
int C658d40::fn_00658d40() {
    int value = this->f24;
    return value == 0 ? 1 : 0;
}
