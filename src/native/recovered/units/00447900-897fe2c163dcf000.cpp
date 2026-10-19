struct Vec24 {
    unsigned char pad0[4];
    void* begin;
    void* end;
    unsigned int fn_00447900();
};

struct Elem24 {
    unsigned int v0;
    unsigned int v1;
    unsigned int v2;
    unsigned int v3;
    unsigned int v4;
    unsigned int v5;
};

struct DxtInfo {
    unsigned char flag0;
    unsigned char pad0[3];
    unsigned int flags;
    unsigned int fourcc;
    unsigned int field_c;
    unsigned int field_10;
    unsigned int field_14;
    unsigned int field_18;
    unsigned int field_1c;
};

// FUNCTION: DAO 0x00847900
unsigned int Vec24::fn_00447900()
{
    if (begin == 0)
        return 0;
    int diff = (int)((char*)end - (char*)begin);
    return (unsigned int)(diff / 24);
}

// FUNCTION: DAO 0x00847920
void __cdecl fn_00447920(Elem24* dst, Elem24* dst_end, const Elem24* src)
{
    while (dst != dst_end) {
        dst->v0 = src->v0;
        dst->v1 = src->v1;
        dst->v2 = src->v2;
        dst->v3 = src->v3;
        dst->v4 = src->v4;
        dst->v5 = src->v5;
        ++dst;
    }
}

// FUNCTION: DAO 0x00847960
void __cdecl fn_00447960(const Elem24* src, const Elem24* src_end, Elem24* dst)
{
    while (src != src_end) {
        dst->v0 = src->v0;
        dst->v1 = src->v1;
        dst->v2 = src->v2;
        dst->v3 = src->v3;
        dst->v4 = src->v4;
        dst->v5 = src->v5;
        ++src;
        ++dst;
    }
}

// FUNCTION: DAO 0x008479A0
void __cdecl fn_004479a0(const Elem24* src_begin, const Elem24* src_end, Elem24* dst_end)
{
    while (src_end != src_begin) {
        --src_end;
        --dst_end;
        dst_end->v0 = src_end->v0;
        dst_end->v1 = src_end->v1;
        dst_end->v2 = src_end->v2;
        dst_end->v3 = src_end->v3;
        dst_end->v4 = src_end->v4;
        dst_end->v5 = src_end->v5;
    }
}

// FUNCTION: DAO 0x00847A80
void __cdecl fn_00447a80(const Elem24* src, const Elem24* src_end, Elem24* dst)
{
    while (src != src_end) {
        if (dst != 0) {
            dst->v0 = src->v0;
            dst->v1 = src->v1;
            dst->v2 = src->v2;
            dst->v3 = src->v3;
            dst->v4 = src->v4;
            dst->v5 = src->v5;
        }
        ++src;
        ++dst;
    }
}

// FUNCTION: DAO 0x0084AE70
bool __cdecl fn_0044ae70(const DxtInfo* info)
{
    if ((((const unsigned char*)&info->flags)[0] & 4u) == 0)
        return false;
    if (info->fourcc != 0x31545844u)
        return false;
    return true;
}

// FUNCTION: DAO 0x0084AE90
bool __cdecl fn_0044ae90(const DxtInfo* info)
{
    if ((((const unsigned char*)&info->flags)[0] & 4u) == 0)
        return false;
    if (info->fourcc != 0x33545844u)
        return false;
    return true;
}

// FUNCTION: DAO 0x0084AEB0
bool __cdecl fn_0044aeb0(const DxtInfo* info)
{
    if ((((const unsigned char*)&info->flags)[0] & 4u) == 0)
        return false;
    if (info->fourcc != 0x35545844u)
        return false;
    return true;
}

// FUNCTION: DAO 0x0084AED0
bool __cdecl fn_0044aed0(const DxtInfo* info)
{
    if ((((const unsigned char*)&info->flags)[0] & 4u) == 0)
        return false;
    if (info->fourcc != 0x32495441u)
        return false;
    return true;
}

// FUNCTION: DAO 0x0084AF10
bool __cdecl fn_0044af10(const DxtInfo* info)
{
    if ((info->flags & 0x40u) == 0)
        return false;
    if ((info->flags & 1u) == 0)
        return false;
    if (info->field_c != 0x20u)
        return false;
    if (info->field_10 != 0xff0000u)
        return false;
    if (info->field_14 != 0xff00u)
        return false;
    if (info->field_18 != 0xffu)
        return false;
    if (info->field_1c != 0xff000000u)
        return false;
    return true;
}

// FUNCTION: DAO 0x0084AF60
bool __cdecl fn_0044af60(const DxtInfo* info)
{
    if ((info->flags & 0x40u) == 0)
        return false;
    if ((info->flags & 1u) != 0)
        return false;
    if (info->field_c != 0x18u)
        return false;
    if (info->field_10 != 0xff0000u)
        return false;
    if (info->field_14 != 0xff00u)
        return false;
    if (info->field_18 != 0xffu)
        return false;
    return true;
}

// FUNCTION: DAO 0x0084AFA0
bool __cdecl fn_0044afa0(const DxtInfo* info)
{
    if ((info->flags & 0x40u) == 0)
        return false;
    if ((info->flags & 1u) != 0)
        return false;
    if (info->field_c != 0x20u)
        return false;
    if (info->field_10 != 0xff0000u)
        return false;
    if (info->field_14 != 0xff00u)
        return false;
    if (info->field_18 != 0xffu)
        return false;
    return true;
}

// FUNCTION: DAO 0x0084AFE0
bool __cdecl fn_0044afe0(const DxtInfo* info)
{
    if ((info->flags & 0x40u) == 0)
        return false;
    if ((info->flags & 1u) == 0)
        return false;
    if (info->field_c != 0x10u)
        return false;
    if (info->field_10 != 0xf00u)
        return false;
    if (info->field_14 != 0xf0u)
        return false;
    if (info->field_18 != 0xfu)
        return false;
    if (info->field_1c != 0xf000u)
        return false;
    return true;
}

// FUNCTION: DAO 0x0084B020
bool __cdecl fn_0044b020(const DxtInfo* info)
{
    if ((((const unsigned char*)&info->flags)[0] & 4u) == 0)
        return false;
    if ((((const unsigned char*)&info->fourcc)[0] & 0x71u) == 0)
        return false;
    return true;
}

// FUNCTION: DAO 0x0084B040
bool __cdecl fn_0044b040(const DxtInfo* info)
{
    if (info->field_c != 8u)
        return false;
    if (info->field_10 != 0xffu)
        return false;
    if (info->field_14 != 0u)
        return false;
    if (info->field_18 != 0u)
        return false;
    return true;
}

// FUNCTION: DAO 0x0084B070
bool __cdecl fn_0044b070(const DxtInfo* info)
{
    if ((info->flag0 & 8u) == 0)
        return false;
    unsigned int bits = info->flags;
    if ((bits & 0x200u) == 0)
        return false;
    if ((bits & 0x400u) == 0)
        return false;
    if ((bits & 0x800u) == 0)
        return false;
    if ((bits & 0x1000u) == 0)
        return false;
    if ((bits & 0x2000u) == 0)
        return false;
    if ((bits & 0x4000u) == 0)
        return false;
    if ((bits & 0x8000u) == 0)
        return false;
    return true;
}
