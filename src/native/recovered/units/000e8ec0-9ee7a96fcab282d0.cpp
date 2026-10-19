typedef unsigned int uint32;
struct E20 { unsigned char b[20]; };
int fn_000e88c0(...);
int fn_000e84a0(...);
int fn_000e8240(...);
int fn_000e7fe0(...);
int fn_000e8440(...);
int fn_000e8200(...);
int fn_000e82f0(...);
int fn_00146870(...);
int fn_000136c0(...);
int fn_00289d10(...);
int fn_004e11f2(...);
int fn_00369830(...);
int fn_0006c760(...);
int fn_00281930(...);
void* fn_00013660(unsigned int);
int fn_004e0ef7(...);
int fn_004e1202(...);
int fn_000e8550(...);
class Vector20 {
public:
    E20* first;
    E20* last;
    E20* end;
    void fn_000e8990();
    E20* fn_000e89d0(E20*, int, E20*);
    E20* fn_000e8a10(E20*, E20*, E20*);
    Vector20* fn_000e8a40(Vector20*);
    void fn_000e8bc0(E20*, E20*, unsigned int, E20*);
    Vector20* fn_000e8ec0(Vector20*);
    void fn_000e8ee0(E20*, unsigned int, E20*, E20*, E20*, E20*);
    Vector20* fn_000e9300(unsigned int);
};
class TreeNode { public: TreeNode* next; unsigned char pad0[4]; void* val; unsigned char pad1[0x15]; unsigned char flag; };
class Tree { public: void fn_000e92c0(TreeNode*); };
class C68A420 { public: void* f4; void* f8; void* fc; void fn_0068a420(void*); };

// FUNCTION: DAO 0x004e8930
int fn_000e8930(int a1, int a2, int a3) {
    return fn_000e82f0(a1, a2, a3, a3, a3, 0, 0);
}

// FUNCTION: DAO 0x004e8990
void Vector20::fn_000e8990() {
    E20* e = last;
    if (first > e) fn_004e11f2();
    E20* b = first;
    if (b > last) fn_004e11f2();
    E20 tmp;
    fn_000e88c0(this, first, last, e, &tmp);
}

// FUNCTION: DAO 0x004e89d0
E20* Vector20::fn_000e89d0(E20* a, int n, E20* b) {
    fn_000e84a0(a, n, b, this, b, 0);
    return a + n;
}

// FUNCTION: DAO 0x004e8a10
E20* Vector20::fn_000e8a10(E20* a, E20* b, E20* c) {
    return (E20*)fn_000e8240(a, b, c, this, c, c, 0);
}

// FUNCTION: DAO 0x004e8a40
Vector20* Vector20::fn_000e8a40(Vector20* o) {
    if (this == o) return this;
    unsigned n = 0;
    if (o->first && o->last) n = (unsigned)(o->last - o->first);
    if (o->first) {
        fn_000e8440(o->first, o->last, o->first);
        fn_000e8ee0(o->first, n, o->last, o->first, o->last, o->last);
    } else {
        fn_000e8ee0(0, 0, 0, 0, 0, 0);
    }
    return this;
}

// FUNCTION: DAO 0x004e8bc0
void Vector20::fn_000e8bc0(E20* pos, E20* a, unsigned n, E20* val) {
    if (n == 0) return;
    fn_000e8a10(pos, a, val);
    fn_000e8240(a, pos, n, this, val, val, 0);
}

// FUNCTION: DAO 0x004e8ec0
Vector20* Vector20::fn_000e8ec0(Vector20* o) {
    fn_000e8a40(o);
    return this;
}

// FUNCTION: DAO 0x004e8ee0
void Vector20::fn_000e8ee0(E20* a, unsigned n, E20* b, E20* c, E20* d, E20* e) {
    fn_000e8bc0(a, b, n, c);
}

// FUNCTION: DAO 0x004e92c0
void Tree::fn_000e92c0(TreeNode* n) {
    TreeNode* p = n;
    while (p && p->flag == 0) {
        fn_000e92c0((TreeNode*)p->val);
        fn_000e8550(&p->pad0[0]);
        TreeNode* q = p->next;
        fn_000136c0(p);
        p = q;
    }
}

// FUNCTION: DAO 0x004e9300
Vector20* Vector20::fn_000e9300(unsigned n) {
    first = 0; last = 0; end = 0;
    if (n > 0) {
        E20 tmp;
        fn_000e8ee0(&tmp, n, &tmp, &tmp, &tmp, &tmp);
    }
    return this;
}

// FUNCTION: DAO 0x00542b90
void* fn_00142b90(unsigned int count) {
    if (count != 0 && count > 0xFFFFFFFFu / 20) { fn_004e0ef7(); }
    return fn_00013660(count * 20);
}

// FUNCTION: DAO 0x0068a420
void C68A420::fn_0068a420(void* p) {
    f4 = 0; f8 = 0; fc = 0;
    fn_00281930(p);
}
