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

// FUNCTION: DAO 0x00847960
void __cdecl fn_00447960(const Elem24* src, const Elem24* src_end, Elem24* dst)
{
    const Elem24* s = src;
    const Elem24* e = src_end;
    Elem24* d = dst;
    while (s != e)
    {
        d->v0 = s->v0;
        d->v1 = s->v1;
        d->v2 = s->v2;
        d->v3 = s->v3;
        d->v4 = s->v4;
        d->v5 = s->v5;
        ++s;
        ++d;
    }
}

// FUNCTION: DAO 0x008479A0
void __cdecl fn_004479a0(const Elem24* src_begin, const Elem24* src_end, Elem24* dst_end)
{
    const Elem24* b = src_begin;
    const Elem24* e = src_end;
    Elem24* d = dst_end;
    while (e != b)
    {
        --e;
        (d - 1)->v0 = e->v0;
        --d;
        d->v1 = e->v1;
        d->v2 = e->v2;
        d->v3 = e->v3;
        d->v4 = e->v4;
        d->v5 = e->v5;
    }
}

// FUNCTION: DAO 0x00847A80
void __cdecl fn_00447a80(const Elem24* src, const Elem24* src_end, Elem24* dst)
{
    const Elem24* s = src;
    const Elem24* e = src_end;
    Elem24* d = dst;
    while (s != e)
    {
        if (d != 0)
        {
            d->v0 = s->v0;
            d->v1 = s->v1;
            d->v2 = s->v2;
            d->v3 = s->v3;
            d->v4 = s->v4;
            d->v5 = s->v5;
        }
        ++s;
        ++d;
    }
}

// FUNCTION: DAO 0x0084AE70
bool __cdecl fn_0044ae70(const DxtInfo* info)
{
    if (((((const unsigned char*)&info->flags)[0] & 4u) != 0) &&
        (info->fourcc == 0x31545844u))
        return true;
    return false;
}

// FUNCTION: DAO 0x0084AE90
bool __cdecl fn_0044ae90(const DxtInfo* info)
{
    if (((((const unsigned char*)&info->flags)[0] & 4u) != 0) &&
        (info->fourcc == 0x33545844u))
        return true;
    return false;
}

// FUNCTION: DAO 0x0084AEB0
bool __cdecl fn_0044aeb0(const DxtInfo* info)
{
    if (((((const unsigned char*)&info->flags)[0] & 4u) != 0) &&
        (info->fourcc == 0x35545844u))
        return true;
    return false;
}

// FUNCTION: DAO 0x0084AED0
bool __cdecl fn_0044aed0(const DxtInfo* info)
{
    if (((((const unsigned char*)&info->flags)[0] & 4u) != 0) &&
        (info->fourcc == 0x32495441u))
        return true;
    return false;
}

// FUNCTION: DAO 0x0084AF10
bool __cdecl fn_0044af10(const DxtInfo* info)
{
    if (((info->flags & 0x40u) != 0) &&
        ((info->flags & 1u) != 0) &&
        (info->field_c == 0x20u) &&
        (info->field_10 == 0xff0000u) &&
        (info->field_14 == 0xff00u) &&
        (info->field_18 == 0xffu) &&
        (info->field_1c == 0xff000000u))
        return true;
    return false;
}

// FUNCTION: DAO 0x0084AF60
bool __cdecl fn_0044af60(const DxtInfo* info)
{
    if (((info->flags & 0x40u) != 0) &&
        ((info->flags & 1u) == 0) &&
        (info->field_c == 0x18u) &&
        (info->field_10 == 0xff0000u) &&
        (info->field_14 == 0xff00u) &&
        (info->field_18 == 0xffu))
        return true;
    return false;
}

// FUNCTION: DAO 0x0084AFA0
bool __cdecl fn_0044afa0(const DxtInfo* info)
{
    if (((info->flags & 0x40u) != 0) &&
        ((info->flags & 1u) == 0) &&
        (info->field_c == 0x20u) &&
        (info->field_10 == 0xff0000u) &&
        (info->field_14 == 0xff00u) &&
        (info->field_18 == 0xffu))
        return true;
    return false;
}

// FUNCTION: DAO 0x0084AFE0
bool __cdecl fn_0044afe0(const DxtInfo* info)
{
    if (((info->flags & 0x40u) != 0) &&
        ((info->flags & 1u) != 0) &&
        (info->field_c == 0x10u) &&
        (info->field_10 == 0xf00u) &&
        (info->field_14 == 0xf0u) &&
        (info->field_18 == 0xfu) &&
        (info->field_1c == 0xf000u))
        return true;
    return false;
}

// FUNCTION: DAO 0x0084B020
bool __cdecl fn_0044b020(const DxtInfo* info)
{
    if (((((const unsigned char*)&info->flags)[0] & 4u) != 0) &&
        ((((const unsigned char*)&info->fourcc)[0] & 0x71u) != 0))
        return true;
    return false;
}

// FUNCTION: DAO 0x0084B040
bool __cdecl fn_0044b040(const DxtInfo* info)
{
    if ((info->field_c == 8u) &&
        (info->field_10 == 0xffu) &&
        (info->field_14 == 0u) &&
        (info->field_18 == 0u))
        return true;
    return false;
}

// FUNCTION: DAO 0x0084B070
bool __cdecl fn_0044b070(const DxtInfo* info)
{
    if (((info->flag0 & 8u) != 0) &&
        ((info->flags & 0x200u) != 0) &&
        ((info->flags & 0x400u) != 0) &&
        ((info->flags & 0x800u) != 0) &&
        ((info->flags & 0x1000u) != 0) &&
        ((info->flags & 0x2000u) != 0) &&
        ((info->flags & 0x4000u) != 0) &&
        ((info->flags & 0x8000u) != 0))
        return true;
    return false;
}
