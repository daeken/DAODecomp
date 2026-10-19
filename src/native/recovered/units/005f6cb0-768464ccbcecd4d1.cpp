#define SWAP_UINT(a,b) do { unsigned int swap_tmp = (a); (a) = (b); (b) = swap_tmp; } while (0)
#define KEY_LESS(x,y) (((table)[(x)>>6][(x)&0x3F].first!=(table)[(y)>>6][(y)&0x3F].first)?((table)[(x)>>6][(x)&0x3F].first<(table)[(y)>>6][(y)&0x3F].first):((table)[(x)>>6][(x)&0x3F].second<(table)[(y)>>6][(y)&0x3F].second))

struct Key_005f23c0 { unsigned int first; unsigned int second; unsigned int third; };
struct SortCtx_005f23c0 { unsigned char pad_00[0xC]; Key_005f23c0** table; };
struct SortObj_005f23c0 { unsigned int count; unsigned int pad_04; unsigned int* arr; };

struct Sub_005f6cb0 { unsigned char pad_00[0xC]; unsigned char field_0C; unsigned char field_0D; unsigned char pad_0E[0x06]; unsigned int field_14; unsigned char pad_18[0x88]; unsigned int field_A0; };
struct Obj_005f6cb0 { unsigned char pad_000[0x7C]; unsigned int field_07C; unsigned char pad_080[0x44]; unsigned int field_0C4; unsigned char pad_0C8[0xB4]; unsigned int field_17C; unsigned char pad_180[0x14]; Sub_005f6cb0* field_194; };

// FUNCTION: DAO 0x9F23C0
void fn_005f23c0(SortObj_005f23c0* self, unsigned int, SortCtx_005f23c0* ctx, unsigned int count)
{
    if (count == 0) count = self->count;
    if ((int)count < 2) return;
    unsigned int* arr = self->arr;
    Key_005f23c0** table = ctx->table;
    struct Range { unsigned int lo; unsigned int hi; };
    Range stack[80];
    Range* sp = stack;
    unsigned int lo = 0;
    unsigned int hi = count;
    for (;;) {
        if ((int)(hi - lo) <= 9) {
            unsigned int i = lo + 1;
            if (i < hi) {
                unsigned int j = lo;
                do {
                    while (KEY_LESS(arr[j + 1], arr[j])) {
                        SWAP_UINT(arr[j], arr[j + 1]);
                        if (j == lo) break;
                        --j;
                    }
                    j = i;
                    ++i;
                } while (i < hi);
            }
            if (sp == stack) break;
            --sp;
            lo = sp->lo;
            hi = sp->hi;
            continue;
        }
        unsigned int mid = lo + (hi - lo) / 2;
        SWAP_UINT(arr[lo], arr[mid]);
        unsigned int i = lo + 1;
        unsigned int j = hi - 1;
        if (KEY_LESS(arr[j], arr[i])) SWAP_UINT(arr[i], arr[j]);
        if (KEY_LESS(arr[lo], arr[i])) SWAP_UINT(arr[i], arr[lo]);
        if (KEY_LESS(arr[j], arr[lo])) SWAP_UINT(arr[lo], arr[j]);
        for (;;) {
            unsigned int pivot = arr[lo];
            do { ++i; } while (KEY_LESS(arr[i], pivot));
            do { --j; } while (KEY_LESS(pivot, arr[j]));
            if ((int)i > (int)j) break;
            SWAP_UINT(arr[i], arr[j]);
        }
        SWAP_UINT(arr[lo], arr[j]);
        unsigned int left = j - lo;
        unsigned int right = hi - i;
        if ((int)left <= (int)right) {
            sp->lo = i; sp->hi = hi; ++sp;
            hi = j;
        } else {
            sp->lo = lo; sp->hi = j; ++sp;
            lo = i;
        }
    }
}

// FUNCTION: DAO 0x9F6CB0
void fn_005f6cb0(Obj_005f6cb0* self)
{
    Sub_005f6cb0* p = self->field_194;
    self->field_0C4 = 0;
    self->field_07C = 0;
    self->field_17C = 0;
    p->field_0C = 0;
    p->field_0D = 0;
    p->field_14 = 0;
    p->field_A0 = 0;
}

// FUNCTION: DAO 0x9FC0E0
int fn_005fc0e0(int a, int b)
{
    int t = a + b - 1;
    int rem = t % b;
    return t - rem;
}

// FUNCTION: DAO 0xA1DF60
unsigned int fn_0061df60(void* self)
{
    return *(unsigned int*)((unsigned char*)self + 0x62E9C);
}
