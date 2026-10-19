typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

struct KeyRec { u16 key; u16 pad; };

// FUNCTION: DAO 0x83e710
void __cdecl fn_0043e710(u8* o, KeyRec* keys, int idx)
{
    u32* arr = (u32*)(o + 0xb5c);
    int count = (int)*(u32*)(o + 0x1450);
    u8* flags = o + 0x1458;
    u32 val = arr[idx];
    int child = idx + idx;
    if (child > count) {
        arr[idx] = val;
        return;
    }
    for (;;) {
        if (child < count) {
            u32 left = arr[child];
            u32 right = arr[child + 1];
            u16 rk = keys[right].key;
            u16 lk = keys[left].key;
            if (rk < lk || (rk == lk && flags[right] <= flags[left])) {
                ++child;
            }
        }
        {
            u32 childVal = arr[child];
            u16 vk = keys[val].key;
            u16 ck = keys[childVal].key;
            if (vk < ck) break;
            if (vk == ck && flags[val] <= flags[childVal]) break;
            arr[idx] = childVal;
            idx = child;
            child += child;
            if (child > count) break;
        }
    }
    arr[idx] = val;
}

// FUNCTION: DAO 0x83ea00
void __cdecl fn_0043ea00(u8* obj, int index, u8* ctx)
{
    u16 initial = *(u16*)(obj + 2);
    u16 prev = initial;
    u32 prevprev = 0xffffffffu;
    u32 pos = 0;
    u32 limit;
    u32 threshold;
    u16* ptr;
    int count;

    if (initial != 0) {
        limit = 7;
        threshold = 4;
    } else {
        limit = 0x8a;
        threshold = 3;
    }

    *(u16*)(obj + index * 4 + 6) = 0xffff;
    if (index < 0) return;

    ptr = (u16*)(obj + 6);
    count = index + 1;
    while (count != 0) {
        u16 cur = *ptr;
        pos += 1;
        if (pos >= limit || prev != cur) {
            if (pos < threshold) {
                *(u16*)(ctx + 0xa7c + (u32)prev * 4) += (u16)pos;
            } else {
                if (prev == 0) {
                    if ((int)pos > 0xa) {
                        *(u16*)(ctx + 0xac4) += 1;
                    } else {
                        *(u16*)(ctx + 0xac0) += 1;
                    }
                } else {
                    if ((u32)prev != prevprev) {
                        *(u16*)(ctx + 0xa7c + (u32)prev * 4) += 1;
                    }
                    *(u16*)(ctx + 0xabc) += 1;
                }
            }
            pos = 0;
            prevprev = prev;
            if (cur == 0) {
                limit = 0x8a;
                threshold = 3;
            } else if (prev == cur) {
                limit = 6;
                threshold = 3;
            } else {
                limit = 7;
                threshold = 4;
            }
        }
        prev = cur;
        ptr += 2;
        --count;
    }
}

// FUNCTION: DAO 0x83f760
void __cdecl fn_0043f760(u8* o)
{
    u32 count = *(u32*)(o + 0x16bc);
    if (count == 0x10) {
        *(u8*)(*(u32*)(o + 8) + *(u32*)(o + 0x14)) = *(u8*)(o + 0x16b8);
        (*(u32*)(o + 0x14)) += 1;
        *(u8*)(*(u32*)(o + 8) + *(u32*)(o + 0x14)) = *(u8*)(o + 0x16b9);
        (*(u32*)(o + 0x14)) += 1;
        *(u32*)(o + 0x16bc) = 0;
        *(u16*)(o + 0x16b8) = 0;
    } else if ((int)count >= 8) {
        *(u8*)(*(u32*)(o + 8) + *(u32*)(o + 0x14)) = *(u8*)(o + 0x16b8);
        (*(u32*)(o + 0x14)) += 1;
        *(u32*)(o + 0x16bc) = count - 8;
        *(u16*)(o + 0x16b8) = (u16)*(u8*)(o + 0x16b9);
    }
}

// FUNCTION: DAO 0x83f7e0
void __cdecl fn_0043f7e0(u8* o)
{
    u32 count = *(u32*)(o + 0x16bc);
    if ((int)count > 8) {
        *(u8*)(*(u32*)(o + 8) + *(u32*)(o + 0x14)) = *(u8*)(o + 0x16b8);
        (*(u32*)(o + 0x14)) += 1;
        *(u8*)(*(u32*)(o + 8) + *(u32*)(o + 0x14)) = *(u8*)(o + 0x16b9);
        (*(u32*)(o + 0x14)) += 1;
        *(u16*)(o + 0x16b8) = 0;
        *(u32*)(o + 0x16bc) = 0;
    } else {
        if ((int)count > 0) {
            *(u8*)(*(u32*)(o + 8) + *(u32*)(o + 0x14)) = *(u8*)(o + 0x16b8);
            (*(u32*)(o + 0x14)) += 1;
        }
        *(u16*)(o + 0x16b8) = 0;
        *(u32*)(o + 0x16bc) = 0;
    }
}

struct CmpKey {
    int a;
    int b;
    int c;
    int d;
    int e;
    int __thiscall fn_00447870(const CmpKey* other) const;
};

// FUNCTION: DAO 0x847870
int __thiscall CmpKey::fn_00447870(const CmpKey* other) const
{
    return (a < other->a)
        || (a == other->a && b < other->b)
        || (a == other->a && b == other->b && c < other->c)
        || (a == other->a && b == other->b && c == other->c && d < other->d)
        || (a == other->a && b == other->b && c == other->c && d == other->d && e < other->e);
}
