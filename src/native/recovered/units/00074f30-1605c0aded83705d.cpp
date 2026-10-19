class C1 {
public:
    unsigned char pad0[0x3c];
    unsigned int field3c;
    unsigned char pad40[0x14];
    void* field54;
    void fn_0006c740(unsigned int v);
};

class CFlags {
public:
    unsigned char pad0[0x6c];
    unsigned int flags;
    unsigned char fn_0006f0a0();
    unsigned char fn_0006f0d0();
};

struct List45Node {
    List45Node* next;
    unsigned char pad[0x41];
    unsigned char field45;
};

class CRange {
public:
    unsigned char pad0[4];
    int field4;
    int field8;
    int fn_00074f30();
    int fn_00074f50();
    int fn_00074f80();
};

struct HeapNode {
    unsigned char pad0[0x3c];
    int key3c;
    unsigned char pad40[0xe0];
    int key120;
};

// FUNCTION: DAO 0x46c740
void C1::fn_0006c740(unsigned int v) {
    field3c = v;
    if (--v != 0) {
        field54 = (void*)((unsigned char*)this + 8);
    } else {
        field54 = (void*)((unsigned char*)this + 0x44);
    }
}

// FUNCTION: DAO 0x46f0a0
unsigned char CFlags::fn_0006f0a0() {
    return (unsigned char)((flags >> 3) & 1u);
}

// FUNCTION: DAO 0x46f0d0
unsigned char CFlags::fn_0006f0d0() {
    return (unsigned char)((flags >> 4) & 1u);
}

// FUNCTION: DAO 0x474df0
List45Node* __cdecl fn_00074df0(List45Node* p) {
    List45Node* prev = p;
    List45Node* cur = p->next;
    while (cur->field45 == 0) {
        prev = cur;
        cur = prev->next;
    }
    return prev;
}

// FUNCTION: DAO 0x474f30
int CRange::fn_00074f30() {
    if (field4 == 0) {
        return 0;
    }
    return (field8 - field4) / 132;
}

// FUNCTION: DAO 0x474f50
int CRange::fn_00074f50() {
    if (field4 == 0) {
        return 0;
    }
    return (field8 - field4) / 148;
}

// FUNCTION: DAO 0x474f80
int CRange::fn_00074f80() {
    if (field4 == 0) {
        return 0;
    }
    return (field8 - field4) / 292;
}

// FUNCTION: DAO 0x4758c0
void __cdecl fn_000758c0(HeapNode** heap, int index, int stop, HeapNode* item) {
    int parent = (index - 1) / 2;
    if (stop >= index) {
        heap[index] = item;
        return;
    }
    do {
        HeapNode* p = heap[parent];
        if (p->key120 < item->key120 ||
            (p->key120 == item->key120 && p->key3c < item->key3c)) {
            heap[index] = p;
            index = parent;
            parent = (index - 1) / 2;
        } else {
            break;
        }
    } while (stop < index);
    heap[index] = item;
}
