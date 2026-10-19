struct C850B0 { unsigned short* data; unsigned int count; void fn_005850b0(); };
struct Inner85140 { unsigned short* data; unsigned int count; };
struct C85140 { unsigned int pad0[6]; Inner85140* p; unsigned int idx; unsigned short* fn_00585140(unsigned int* out); };
struct Inner85180 { unsigned short* data; unsigned int count; };
struct C85180 { Inner85180* p; int idx; int fn_00585180(); };
struct E85200 { unsigned int f0; unsigned int size; unsigned int pad[5]; unsigned int start; };
struct C85200 { E85200** array; };
struct E85290 { unsigned int f0; unsigned int size; unsigned int pad[5]; unsigned int start; };
struct C85290 { E85290** array; int count; };
struct Inner86060 { unsigned short* data; unsigned int count; };
struct C86060 { Inner86060* p; int idx; int fn_00586060(); };
struct C586B30 { unsigned int f0; unsigned int f4; unsigned int f8; unsigned int fc; unsigned int f10; unsigned int f14; unsigned int f18; unsigned int f1c; unsigned int f20; C586B30* fn_00586b30(int a, int b); };
struct E87800 { unsigned int start; unsigned int size; unsigned int pad; };
struct Cont87800 { E87800* array; unsigned int count; };
struct Fallback87800 { int pad0; unsigned int value; };
struct C87800 { unsigned int pad[5]; Cont87800* cont; int idx; Fallback87800* fb; unsigned int current; void fn_00587800(); };
struct Cont879 { E87800* array; unsigned int count; };
struct C879C0 { unsigned int pad[4]; Cont879* c10; int idx14; Cont879* c18; int idx1c; void fn_005879c0(); };
struct Counter58AEE0 { unsigned int pad[6]; unsigned int counter; };
struct C58AEE0 { unsigned int f_0; unsigned int f_4; unsigned int f_8; unsigned int f_c; unsigned int f_10; unsigned int f_14; unsigned int f_18; unsigned int f_1c; unsigned int id_20; unsigned short w_24; C58AEE0* fn_0058aee0(Counter58AEE0* arg); };
struct C590940 { unsigned int flags; unsigned char pad1[0x19]; signed char f1d; unsigned char pad2[10]; signed short f28; int fn_00590940(); };
struct C590970 { unsigned int flags; unsigned char pad1[18]; unsigned short f16; unsigned int f18; unsigned int fn_00590970(); };
struct C5909 { unsigned char pad0[0x20]; unsigned int f20; unsigned char pad1[6]; unsigned char f2a; int fn_005909d0(); int fn_005909f0(); };
struct Target590B20 { unsigned char pad[0x18]; unsigned char flag18; };
struct C590B20 { unsigned char pad[0x1c]; Target590B20* p1c; void fn_00590b20(int, int, int, int); };
struct C590B30 { unsigned char pad[0x14d]; unsigned char f14d; unsigned char f14e; void fn_00590b30(); };

// FUNCTION: DAO 0x009850B0
void C850B0::fn_005850b0() {
    if (count > 0 && data[count - 1] == 0) {
        --count;
    }
}

// FUNCTION: DAO 0x00985140
unsigned short* C85140::fn_00585140(unsigned int* out) {
    if (p == 0 || idx >= p->count) {
        if (out != 0) {
            *out = 0;
        }
        return 0;
    }
    if (out != 0) {
        *out = p->count - idx;
    }
    return p->data + idx;
}

// FUNCTION: DAO 0x00985180
int C85180::fn_00585180() {
    if (p == 0) {
        return 1;
    }
    if (idx < 0) {
        return 1;
    }
    if (idx >= (int)p->count) {
        return 1;
    }
    return 0;
}

// FUNCTION: DAO 0x00985200
int __cdecl fn_00585200(C85200* c, int count, unsigned int* key) {
    int low = 0;
    int high = count - 1;
    if (high > 0) {
        while (low < high) {
            int mid = (low + high) / 2;
            E85200* e = c->array[mid];
            unsigned int k = *key;
            unsigned int start = e->start;
            if (k < start) {
                high = mid - 1;
            } else {
                unsigned int end = start + e->size;
                if (k < end) {
                    return mid;
                }
                if (start == k) {
                    return mid;
                }
                low = mid + 1;
            }
        }
    }
    if (low == high) {
        E85200* e = c->array[low];
        unsigned int k = *key;
        unsigned int start = e->start;
        if (k < start) {
            return -1;
        }
        unsigned int end = start + e->size;
        if (k < end) {
            return low;
        }
        if (start == k) {
            return low;
        }
        return -1;
    }
    return -1;
}

// FUNCTION: DAO 0x00985290
int __cdecl fn_00585290(C85290* c, unsigned int* key) {
    int low = 0;
    int n = c->count;
    while (n > 0) {
        int half = n >> 1;
        int mid = low + half;
        E85290* e = c->array[mid];
        unsigned int k = *key;
        unsigned int start = e->start;
        if (k < start) {
            n = half;
        } else {
            unsigned int end = start + e->size;
            if (k < end) {
                n = half;
            } else {
                low = mid + 1;
                n = n - half - 1;
            }
        }
    }
    return low;
}

// FUNCTION: DAO 0x00986060
int C86060::fn_00586060() {
    if (idx < 0) {
        return 1;
    }
    if ((unsigned int)idx >= p->count) {
        return 1;
    }
    return 0;
}

// FUNCTION: DAO 0x00986B30
C586B30* C586B30::fn_00586b30(int a, int b) {
    f0 = 0;
    f4 = 0;
    f8 = 0;
    fc = 0;
    f10 = (unsigned int)a;
    f14 = (unsigned int)a;
    f18 = 0;
    f1c = (unsigned int)b;
    f20 = 0;
    return this;
}

// FUNCTION: DAO 0x00987800
void C87800::fn_00587800() {
    if (idx < 0 || (unsigned int)idx >= cont->count) {
        current = fb->value;
        return;
    }
    E87800* e = cont->array + idx;
    unsigned int cur = current;
    if (cur < e->start) {
        current = e->start;
        return;
    }
    current = cur + e->size;
    if (idx < (int)cont->count) {
        idx = idx + 1;
    }
}

// FUNCTION: DAO 0x009879C0
void C879C0::fn_005879c0() {
    if (c18 == 0 || (unsigned int)idx1c >= c18->count) {
        idx1c = c18->count;
        return;
    }
    idx1c = idx1c + 1;
    int j = idx14;
    if (j < 0) {
        return;
    }
    Cont879* c2 = c10;
    if ((unsigned int)j >= c2->count) {
        return;
    }
    E87800* e = c2->array + j;
    unsigned int end = e->start + e->size;
    if ((unsigned int)idx1c < end) {
        return;
    }
    if ((unsigned int)j >= c2->count) {
        return;
    }
    idx14 = j + 1;
}

// FUNCTION: DAO 0x0098AEE0
C58AEE0* C58AEE0::fn_0058aee0(Counter58AEE0* arg) {
    f_0 = 0;
    f_4 = 0;
    f_8 = 0;
    f_c = 0;
    f_10 = 0;
    f_14 = 0;
    f_18 = 0;
    f_1c = 0;
    w_24 = 0;
    id_20 = arg->counter;
    arg->counter = id_20 + 1;
    return this;
}

// FUNCTION: DAO 0x00990940
int C590940::fn_00590940() {
    if (flags & 0x80000000u) {
        signed char v = f1d;
        if (v > 0) {
            return (int)v;
        }
        return 0;
    }
    signed short v = f28;
    if (v > 0) {
        return (int)v;
    }
    return 0;
}

// FUNCTION: DAO 0x00990970
unsigned int C590970::fn_00590970() {
    if (flags & 0x80000000u) {
        return f16;
    }
    return f18;
}

// FUNCTION: DAO 0x009909D0
int C5909::fn_005909d0() {
    if ((f2a & 1) != 0 && f20 == 1) {
        return 1;
    }
    return 0;
}

// FUNCTION: DAO 0x009909F0
int C5909::fn_005909f0() {
    if ((f2a & 1) != 0 && f20 == 3) {
        return 1;
    }
    return 0;
}

// FUNCTION: DAO 0x00990B20
void C590B20::fn_00590b20(int, int, int, int) {
    if (p1c != 0) {
        p1c->flag18 = 1;
    }
}

// FUNCTION: DAO 0x00990B30
void C590B30::fn_00590b30() {
    if ((f14d & 1) == 0) {
        unsigned char al = (unsigned char)(f14d | 1);
        f14e = (unsigned char)(f14e | 2);
        f14d = al;
    }
}
