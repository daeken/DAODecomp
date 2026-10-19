struct C649d70 {
    int f0;
    int f4;
    int f8;
    char padC[8];
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

struct C649e4b0 {
    char pad0[0x30];
    int f30;
    unsigned char fn_0064e4b0(int a, int b, int flags);
};

struct C649e550 {
    char pad0[0x30];
    int f30;
    int fn_0064e550(int arg);
};

struct C653650 {
    char pad0[0x1c];
    int f1c;
    unsigned int fn_00653650(unsigned int v);
};

struct C658d40 {
    char pad0[0x24];
    int f24;
    int fn_00658d40();
};

// FUNCTION: DAO 0x00A49D70
int C649d70::fn_00649d70() {
    int count;
    if (this->p14 != 0) {
        count = (int)(this->p18 - this->p14);
    } else {
        count = 0;
    }
    int product = this->f4 * this->f8;
    if (count == product) {
        return 0;
    }
    int a = this->f4;
    int b = this->f8;
    return ((a + 1) / 2) * ((b - 1) / 2) + ((a - 1) / 2) + 1;
}

// FUNCTION: DAO 0x00A49E00
void __cdecl fn_00649e00(unsigned int* dst, unsigned int count, const unsigned int* src) {
    if (count != 0) {
        do {
            if (dst != 0) {
                *dst = *src;
            }
            --count;
            ++dst;
        } while (count != 0);
    }
}

// FUNCTION: DAO 0x00A4BA70
int __stdcall fn_0064ba70(C649ba70* p, int) {
    int value = p->f3c;
    int diff = value - p->f44;
    if (diff > 5) {
        return 1;
    }
    if (value == p->f30) {
        return 1;
    }
    return 0;
}

// FUNCTION: DAO 0x00A4C4A0
unsigned char __stdcall fn_0064c4a0(C649c4a0_Arg1* a, C649c4a0_Obj** b) {
    if (a->f1 == 0) {
        return 0;
    }
    C649c4a0_Obj* obj = *b;
    if (obj->f8c != 0) {
        return 1;
    }
    int count = obj->f74 ? (obj->f78 - obj->f74) / 6 : 0;
    if (a->f30 < count - 1) {
        return 0;
    }
    count = obj->f74 ? (obj->f78 - obj->f74) / 6 : 0;
    if (a->f3c < count - 1) {
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
    int count = obj->f74 ? (obj->f78 - obj->f74) / 6 : 0;
    return (unsigned char)((count - a->f44) >= 2);
}

// FUNCTION: DAO 0x00A4C580
unsigned char __stdcall fn_0064c580(C649c580_Arg1* a, C649c4a0_Obj** b) {
    int value = a->f30;
    if (value - a->f44 > 2) {
        return 1;
    }
    C649c4a0_Obj* obj = *b;
    int count = obj->f74 ? (obj->f78 - obj->f74) / 6 : 0;
    if (value >= count - 1) {
        return 1;
    }
    return 0;
}

// FUNCTION: DAO 0x00A4CE10
void __cdecl fn_0064ce10(void*, unsigned int* first, unsigned int* last) {
    if (first < last) {
        do {
            unsigned int a = *first;
            unsigned int b = *(last - 1);
            --last;
            *first = b;
            ++first;
            *last = a;
        } while (first < last);
    }
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

// FUNCTION: DAO 0x00A4E4B0
unsigned char C649e4b0::fn_0064e4b0(int a, int b, int flags) {
    int half = (this->f30 + 1) / 2;
    int delta = a - b;
    if (delta == 1) {
        return (unsigned char)(flags | 0x60);
    }
    if (delta == -1) {
        return (unsigned char)(flags | 0x20);
    }
    if (delta == half) {
        return (unsigned char)flags;
    }
    if (delta == -half) {
        return (unsigned char)(flags | 0x40);
    }
    if (delta == half + 1) {
        return (unsigned char)(flags | 0xE0);
    }
    if (delta == half - 1) {
        return (unsigned char)(flags | 0x80);
    }
    if (delta == 1 - half) {
        return (unsigned char)(flags | 0xC0);
    }
    if (delta == -1 - half) {
        return (unsigned char)(flags | 0xA0);
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

// FUNCTION: DAO 0x00A53650
unsigned int C653650::fn_00653650(unsigned int v) {
    unsigned int low = (v >> 4) & 0xFFFu;
    unsigned int high = v >> 20;
    return low * (unsigned int)this->f1c + high;
}

// FUNCTION: DAO 0x00A58D40
int C658d40::fn_00658d40() {
    return this->f24 == 0 ? 1 : 0;
}
