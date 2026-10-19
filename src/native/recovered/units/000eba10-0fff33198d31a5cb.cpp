typedef unsigned int u32;
typedef unsigned char u8;

struct __declspec(align(16)) Vec4 { float x, y, z, w; };
struct Vec3 { float x, y, z; };
struct Vec2 { float x, y; };
struct Poly { const Vec4* data; int count; };

extern "C" double g_00ae70f8;
extern "C" double g_00af14c8;
extern "C" float g_00af14d0;
extern "C" float g_00bf4cf0[4];

extern "C" void __cdecl fn_004d4c20(const Vec2*, const Vec2*);
extern "C" int __cdecl fn_004eaf10(const Vec4*, const Vec4*, const Vec4*, float*);
extern "C" Vec3* __cdecl fn_004eae30(Vec3*, float);
extern "C" float __cdecl fn_004ee570(const Vec2*);
extern "C" void* __cdecl fn_005d0ab0(void*);
extern "C" int __cdecl fn_008e34f0(double);
extern "C" float __cdecl fn_00a492d0(int, int);
extern "C" void __cdecl fn_00a49890(Vec3*, void*, int);

extern "C" int __cdecl fn_000eb010(const Vec4*, const Vec4*, float);
extern "C" int __cdecl fn_000eb070(const Vec2*, const Vec2*, const Vec2*, const Vec2*);
extern "C" int __cdecl fn_000eb100(const Vec4*, const Poly*);
extern "C" int __cdecl fn_000eb240(const Vec4*, const Vec4*, const Vec4*, float);
extern "C" int __cdecl fn_000eb340(const Vec4*, float, const Vec4*, float);
extern "C" int __cdecl fn_000eb3b0(const Vec4*, float, const Vec4*, const Vec2*, float, float);
extern "C" unsigned int __stdcall fn_006486a0(void*);

struct C_EBA {
    void fn_000eba10();
    void fn_000eba70();
};

struct C_A494 {
    float v0, v4, v8;
    char pad0[0x14];
    int v20, v24;
    char pad1[8];
    float v30;
    char pad2[4];
    float v38;
    int fn_00649410(float*);
    int fn_00649440(float*);
    Vec3* fn_00649b70(Vec3*, int, int, unsigned char, void*);
};

// FUNCTION: DAO 0x4EB010
extern "C" int __cdecl fn_000eb010(const Vec4* a, const Vec4* b, float r) {
    float dx = a->x - b->x;
    float dy = a->y - b->y;
    float d2 = dx * dx + dy * dy;
    float r2 = r * r;
    return (d2 <= r2) ? 1 : 0;
}

// FUNCTION: DAO 0x4EB070
extern "C" int __cdecl fn_000eb070(const Vec2* a, const Vec2* b, const Vec2* c, const Vec2* d) {
    float abx = b->x - a->x;
    float aby = b->y - a->y;
    float acy = c->y - a->y;
    float acx = c->x - a->x;
    float d1 = abx * acy - aby * acx;
    if (d1 > 0.0f) return 0;
    float adx = d->x - a->x;
    float ady = d->y - a->y;
    float d2 = abx * ady - aby * adx;
    if (d2 < 0.0f) return 0;
    float cbx = b->x - c->x;
    float cby = b->y - c->y;
    float cax = a->x - c->x;
    float cay = a->y - c->y;
    float d3 = cbx * cay - cby * cax;
    if (d3 > 0.0f) return 0;
    float cdx = d->x - c->x;
    float cdy = d->y - c->y;
    float d4 = cbx * cdy - cby * cdx;
    if (d4 < 0.0f) return 0;
    return 1;
}

// FUNCTION: DAO 0x4EB100
extern "C" int __cdecl fn_000eb100(const Vec4* p, const Poly* poly) {
    int n = poly->count;
    if (n < 3) return 0;
    const Vec4* data = poly->data;
    if (data == 0) data = reinterpret_cast<const Vec4*>(g_00bf4cf0);
    float sum = 0.0f;
    for (int i = 0; i < n; ++i) {
        int j = i + 1;
        if (j >= n) j = 0;
        Vec2 va, vb;
        va.x = data[i].x - p->x;
        va.y = data[i].y - p->y;
        vb.x = data[j].x - p->x;
        vb.y = data[j].y - p->y;
        fn_004d4c20(&va, &vb);
        sum += va.x + va.y;
    }
    double limit = g_00af14c8;
    return (static_cast<double>(sum) < limit) ? 1 : 0;
}

// FUNCTION: DAO 0x4EB240
extern "C" int __cdecl fn_000eb240(const Vec4* a, const Vec4* b, const Vec4* c, float r) {
    float out = 0.0f;
    int ok = fn_004eaf10(a, b, c, &out);
    if (!ok) return 0;
    float dx = a->x - b->x;
    float dy = a->y - b->y;
    float d2 = dx * dx + dy * dy;
    return (d2 <= r * r) ? 1 : 0;
}

// FUNCTION: DAO 0x4EB340
extern "C" int __cdecl fn_000eb340(const Vec4* a, float f1, const Vec4* b, float f2) {
    float dx = a->x - b->x;
    float dy = a->y - b->y;
    float d2 = dx * dx + dy * dy;
    float s = f1 + f2;
    return (d2 <= s * s) ? 1 : 0;
}

// FUNCTION: DAO 0x4EB3B0
extern "C" int __cdecl fn_000eb3b0(const Vec4* a, float f1, const Vec4* b, const Vec2* p3, float f4, float f5) {
    if (f5 <= 0.0f) return 0;
    if (f5 > g_00af14d0) return 0;
    if (!fn_000eb340(a, f1, b, f5)) return 0;
    float ang = fn_004ee570(p3);
    Vec3 tmp;
    Vec3* v = fn_004eae30(&tmp, ang * 0.5f);
    Vec4 c;
    c.x = v->x;
    c.y = v->y;
    c.z = v->z;
    c.w = 0.0f;
    if (fn_000eb240(a, b, &c, f5)) return 1;
    if (f4 > 0.0f) {
        Vec4 out;
        out.x = f4;
        out.y = f4;
        out.z = f4;
        out.w = 0.0f;
        if (fn_000eb240(a, b, &out, f5)) return 1;
    }
    return 0;
}

// FUNCTION: DAO 0x4EBA10
void C_EBA::fn_000eba10() {
    *reinterpret_cast<void**>(this) = reinterpret_cast<void*>(0xaf14d8);
}

// FUNCTION: DAO 0x4EBA70
void C_EBA::fn_000eba70() {
    *reinterpret_cast<void**>(this) = reinterpret_cast<void*>(0xaf1528);
    fn_000eba10();
}

// FUNCTION: DAO 0xA486A0
extern "C" unsigned int __stdcall fn_006486a0(void* arg) {
    void* p = fn_005d0ab0(reinterpret_cast<void*>(&arg));
    return *reinterpret_cast<unsigned int*>(p);
}

// FUNCTION: DAO 0xA49410
int C_A494::fn_00649410(float* p) {
    double d = static_cast<double>((p[1] - v38 - v4) / v30) + g_00ae70f8;
    int r = fn_008e34f0(d);
    return (r < 0) ? 0 : r;
}

// FUNCTION: DAO 0xA49440
int C_A494::fn_00649440(float* p) {
    double d = static_cast<double>((p[0] - v38 - v0) / v30) + g_00ae70f8;
    int r = fn_008e34f0(d);
    return (r < 0) ? 0 : r;
}

// FUNCTION: DAO 0xA49B70
Vec3* C_A494::fn_00649b70(Vec3* out, int x, int y, unsigned char flag, void* p) {
    out->x = v0;
    out->y = v4;
    out->z = v8;
    if (x < v24 && y < v20 && x >= 0 && y >= 0) {
        out->x = static_cast<float>(y) * v30 + v38 + out->x;
        out->y = static_cast<float>(x) * v30 + v38 + out->y;
        if (flag == 0) {
            out->z = fn_00a492d0(x, y);
        } else {
            fn_00a49890(out, p, 0);
        }
    }
    return out;
}
