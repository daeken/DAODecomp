typedef unsigned int u32;

struct Array8;

struct Lock {
    unsigned char opaque[16];
    void fn_0001a980();
    void fn_0001a9c0();
    void fn_0001a8e0(int);
    void fn_0001a840();
};

struct Array8 {
    void *data;
    u32 count;
    u32 cap;
    void fn_000172d0(u32 n);
    void fn_00017370(Array8 *src);
    void fn_00533b10(u32 n);
};

struct HandlerArray {
    u32 refcount;
    Array8 arr;
    Lock lock;
    void fn_000175d0();
    void fn_000176b0();
};

struct GWaitable {
    unsigned char pad[0x10];
    HandlerArray *handlers;
    bool fn_000173c0(void *a, void *b);
    bool fn_00017420(void *a, void *b);
    void fn_00017690();
};

struct GEvent {
    unsigned char pad[0x10];
    HandlerArray *handlers;
    void fn_00018f90();
    bool fn_00019040(int mode);
    void fn_00019020();
    GEvent *fn_00017550(bool createHandlers);
    void fn_000176f0();
};

struct WaitList {
    GWaitable **items;
    u32 count;
    bool fn_000174d0(void *handler);
    void fn_00017520(void *handler);
};

extern "C" unsigned char g_0081d3dc[];
extern "C" unsigned char g_0081d3e0[];
extern "C" unsigned char g_006d52c0[];
extern "C" unsigned char g_006e081c[];
extern "C" int (__stdcall *g_00ada1ec)(void *, int);

extern "C" int __cdecl fn_004e1746(void *);
extern "C" void __stdcall fn_00019240(void *);
extern "C" void * __stdcall fn_00019220(u32);
extern "C" void * __cdecl fn_004e3030(void *, const void *, u32);

// FUNCTION: DAO 0x417290
extern "C" void * fn_00017290(void) {
    if ((*(volatile unsigned char *)g_0081d3e0 & 1) == 0) {
        *(volatile u32 *)g_0081d3e0 |= 1u;
        *(volatile u32 *)g_0081d3dc = (u32)g_006e081c;
        fn_004e1746((void *)g_006d52c0);
    }
    return g_0081d3dc;
}

// FUNCTION: DAO 0x4172d0
void Array8::fn_000172d0(u32 n) {
    u32 capFlags = this->cap;
    u32 oldCount = this->count;
    u32 cap = capFlags & 0x3fffffffu;
    this->count = n;
    if (n == 0) {
        u32 mode = capFlags >> 30;
        if (mode != 0) {
            if (((capFlags >> 31) & 1u) != 0) {
                if (cap > 0) goto done;
            } else {
                if ((mode & 1u) != 0) goto done;
            }
        }
        this->cap = capFlags & 0xc0000000u;
        if (this->data != 0) {
            fn_00019240(this->data);
            this->data = 0;
        }
        goto done;
    }
    if (n > cap) goto realloc;
    if (n > (cap >> 1)) goto done;
realloc:
    this->fn_00533b10(n + (n >> 2));
done:
    if (oldCount < n) {
        u32 i;
        for (i = oldCount; i < n; ++i) {
            u32 *e = (u32 *)((unsigned char *)this->data + i * 8u);
            e[0] = 0;
            e[1] = 0;
        }
    }
}

// FUNCTION: DAO 0x417370
void Array8::fn_00017370(Array8 *src) {
    this->fn_000172d0(src->count);
    u32 n = this->count;
    u32 i;
    for (i = 0; i < n; ++i) {
        u32 *d = (u32 *)((unsigned char *)this->data + i * 8u);
        u32 *s = (u32 *)((unsigned char *)src->data + i * 8u);
        d[0] = s[0];
        d[1] = s[1];
    }
}

// FUNCTION: DAO 0x4173c0
bool GWaitable::fn_000173c0(void *a, void *b) {
    HandlerArray *h = this->handlers;
    if (h == 0) return false;
    h->lock.fn_0001a980();
    u32 n = h->arr.count + 1u;
    h->arr.fn_000172d0(n);
    u32 *e = (u32 *)((unsigned char *)h->arr.data + (n - 1u) * 8u);
    e[0] = (u32)a;
    e[1] = (u32)b;
    h->lock.fn_0001a9c0();
    return true;
}

// FUNCTION: DAO 0x417420
bool GWaitable::fn_00017420(void *a, void *b) {
    HandlerArray *h = this->handlers;
    if (h == 0) return false;
    h->lock.fn_0001a980();
    u32 cnt = h->arr.count;
    u32 i = 0;
    u32 *data = (u32 *)h->arr.data;
    while (i < cnt) {
        u32 *e = data + i * 2u;
        if (e[0] == (u32)a && e[1] == (u32)b) break;
        ++i;
    }
    bool found = false;
    if (i < cnt) {
        if (h->arr.count == 1u) {
            h->arr.fn_000172d0(0);
        } else {
            u32 *dst = (u32 *)h->arr.data + i * 2u;
            u32 rem = h->arr.count - i;
            fn_004e3030(dst, dst + 2, (rem - 1u) * 8u);
            --h->arr.count;
        }
        found = true;
    }
    h->lock.fn_0001a9c0();
    return found;
}

// FUNCTION: DAO 0x4174d0
bool WaitList::fn_000174d0(void *handler) {
    u32 n = this->count;
    if (n == 0) return true;
    u32 i;
    for (i = 0; i < n; ++i) {
        if (!this->items[i]->fn_000173c0(handler, this)) {
            while (i > 0) {
                --i;
                this->items[i]->fn_00017420(handler, this);
            }
            return false;
        }
    }
    return true;
}

// FUNCTION: DAO 0x417520
void WaitList::fn_00017520(void *handler) {
    u32 i;
    for (i = 0; i < this->count; ++i) {
        this->items[i]->fn_00017420(handler, this);
    }
}

// FUNCTION: DAO 0x417550
GEvent * GEvent::fn_00017550(bool createHandlers) {
    this->fn_00018f90();
    *(void **)this = (void *)0x00ae0834u;
    this->fn_00019040(1);
    HandlerArray *h = 0;
    if (createHandlers) {
        h = (HandlerArray *)fn_00019220(0x24u);
        if (h != 0) {
            h->arr.data = 0;
            h->arr.count = 0;
            h->arr.cap = 0;
            h->lock.fn_0001a8e0(0);
            h->refcount = 1;
        }
    }
    this->handlers = h;
    if (h != 0) {
        h->arr.cap = (h->arr.cap & 0x3fffffffu) | 0x40000000u;
    }
    return this;
}

typedef void (__cdecl *WaitHandlerFn)(void *);

// FUNCTION: DAO 0x4175d0
void HandlerArray::fn_000175d0() {
    this->lock.fn_0001a980();
    u32 n = this->arr.count;
    if (n == 0) {
        this->lock.fn_0001a9c0();
        return;
    }
    if (n == 1) {
        u32 *e = (u32 *)this->arr.data;
        WaitHandlerFn fn = (WaitHandlerFn)e[0];
        fn((void *)e[1]);
        this->lock.fn_0001a9c0();
        return;
    }
    {
        Array8 local;
        local.data = 0;
        local.count = 0;
        local.cap = 0;
        local.fn_00017370(&this->arr);
        u32 i;
        for (i = 0; i < local.count; ++i) {
            u32 *e = (u32 *)((unsigned char *)local.data + i * 8u);
            WaitHandlerFn fn = (WaitHandlerFn)e[0];
            fn((void *)e[1]);
        }
        local.fn_000172d0(0);
        if (local.data != 0) fn_00019240(local.data);
    }
    this->lock.fn_0001a9c0();
}

// FUNCTION: DAO 0x417690
void GWaitable::fn_00017690() {
    if (this->handlers != 0) this->handlers->fn_000175d0();
}

// FUNCTION: DAO 0x4176b0
void HandlerArray::fn_000176b0() {
    int old = g_00ada1ec(this, -1);
    if ((old - 1) != 0) return;
    if (this == 0) return;
    this->lock.fn_0001a840();
    this->arr.fn_000172d0(0);
    if (this->arr.data != 0) fn_00019240(this->arr.data);
    fn_00019240(this);
}

// FUNCTION: DAO 0x4176f0
void GEvent::fn_000176f0() {
    HandlerArray *h = this->handlers;
    *(void **)this = (void *)0x00ae0834u;
    if (h != 0) h->fn_000176b0();
    this->fn_00019020();
}
