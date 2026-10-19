typedef unsigned long DWORD;
typedef unsigned int UINT;
typedef __int64 int64;
typedef unsigned __int64 uint64;

struct tm { int tm_sec; int tm_min; int tm_hour; int tm_mday; int tm_mon; int tm_year; int tm_wday; int tm_yday; int tm_isdst; };

extern "C" __declspec(dllimport) unsigned long __stdcall GetTickCount(void);

int* __cdecl fn_004e37b6(void);
void __cdecl fn_004e11f2(void);
void __cdecl fn_004e11ce(void*, void*, void*, void*, void*);
void* __cdecl fn_004e19e0(void*, int, unsigned int);
void __cdecl fn_004e10d2(void*, void*, void*, void*, void*);
void __cdecl fn_004f0940(int);
void __cdecl fn_004f0a18(int);
void __cdecl fn_004f5b03(void);
void __cdecl fn_004f625d(void);
void __cdecl fn_004ee8b9(void);
void __cdecl fn_004f629e(void);
int __cdecl fn_004f6041(struct tm*);
void* __cdecl fn_004ee241(void);
void* __cdecl fn_004eb4a1(unsigned int);

void __cdecl fn_004f6217(void);
int __cdecl fn_004e491a(struct tm*, const __int64*);
int __cdecl fn_004f6266(struct tm*);
int __cdecl fn_004f62a7(long*);
int __cdecl fn_004f62db(long*);
int __cdecl fn_004f630f(long*);

extern int g_00c3f8f4;
extern int g_00c1629c;
extern int g_00c162a0;
extern int g_00c16298;

static int is_leap_year(int y) { return ((y % 4) == 0 && (y % 100) != 0) || ((y % 400) == 0); }
static int days_in_year(int y) { return is_leap_year(y) ? 366 : 365; }

// FUNCTION: DAO 0x0041e870
DWORD __stdcall fn_0001e870(void)
{
    return GetTickCount();
}

struct C_0040e140 {
    unsigned long m0;
    unsigned long m4;
    bool __thiscall fn_0040e140(const C_0040e140* other);
};

// FUNCTION: DAO 0x0080e140
bool __thiscall C_0040e140::fn_0040e140(const C_0040e140* other)
{
    if (m0 != 0 && m0 != other->m0)
        fn_004e11f2();
    return m4 == other->m4;
}

// FUNCTION: DAO 0x008e4326
int __cdecl fn_004e4326(struct tm* tmout, const __int64* timep)
{
    long dayLight = 0;
    long dstBias = 0;
    long timeZone = 0;
    __int64 work;
    __int64 t;
    int r;

    if (tmout == 0) {
        *fn_004e37b6() = 22;
        fn_004e11ce(0, 0, 0, 0, 0);
        return 22;
    }
    fn_004e19e0(tmout, 0xff, 0x24);
    if (timep == 0) {
        *fn_004e37b6() = 22;
        return 22;
    }
    t = *timep;
    if (t < 0 || t > (((__int64)0x00000007 << 32) + (__int64)0x93406fff)) {
        *fn_004e37b6() = 22;
        return 22;
    }
    fn_004f6217();
    if (fn_004f62a7(&dayLight) != 0)
        fn_004e10d2(0, 0, 0, 0, 0);
    if (fn_004f62db(&dstBias) != 0)
        fn_004e10d2(0, 0, 0, 0, 0);
    if (fn_004f630f(&timeZone) != 0)
        fn_004e10d2(0, 0, 0, 0, 0);

    if (t > 0x3f480) {
        work = t - (__int64)timeZone;
        r = fn_004e491a(tmout, &work);
        if (r != 0)
            return r;
        if (dayLight != 0 && fn_004f6266(tmout) != 0) {
            work -= (__int64)dstBias;
            r = fn_004e491a(tmout, &work);
            if (r != 0)
                return r;
            tmout->tm_isdst = 1;
        }
    } else {
        r = fn_004e491a(tmout, timep);
        if (r != 0)
            return r;
        if (dayLight != 0 && fn_004f6266(tmout) != 0)
            tmout->tm_isdst = 1;
    }
    return 0;
}

// FUNCTION: DAO 0x008e47a1
void __cdecl fn_004e47a1(void)
{
    fn_004f0940(4);
}

// FUNCTION: DAO 0x008e491a
int __cdecl fn_004e491a(struct tm* tmout, const __int64* timep)
{
    static const unsigned char mdays[12] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    __int64 t;
    int sec, min, hour, days, wday, year, mon, md;

    if (tmout == 0) {
        *fn_004e37b6() = 22;
        fn_004e11ce(0, 0, 0, 0, 0);
        return 22;
    }
    fn_004e19e0(tmout, 0xff, 0x24);
    if (timep == 0) {
        *fn_004e37b6() = 22;
        return 22;
    }
    t = *timep;
    if (t < 0 || t > (((__int64)0x00000007 << 32) + (__int64)0x93406fff)) {
        *fn_004e37b6() = 22;
        return 22;
    }

    sec = (int)(t % 60);
    t /= 60;
    min = (int)(t % 60);
    t /= 60;
    hour = (int)(t % 24);
    t /= 24;
    days = (int)t;

    wday = (days + 4) % 7;
    if (wday < 0)
        wday += 7;

    year = 1970;
    while (days >= days_in_year(year)) {
        days -= days_in_year(year);
        ++year;
    }

    tmout->tm_year = year - 1900;
    tmout->tm_yday = days;

    mon = 0;
    while (mon < 11) {
        md = mdays[mon] + (mon == 1 && is_leap_year(year) ? 1 : 0);
        if (days < md)
            break;
        days -= md;
        ++mon;
    }

    tmout->tm_sec = sec;
    tmout->tm_min = min;
    tmout->tm_hour = hour;
    tmout->tm_mday = days + 1;
    tmout->tm_mon = mon;
    tmout->tm_wday = wday;
    tmout->tm_isdst = 0;
    return 0;
}

// FUNCTION: DAO 0x008f6217
void __cdecl fn_004f6217(void)
{
    fn_004f0a18(6);
    if (g_00c3f8f4 == 0) {
        fn_004f5b03();
        ++g_00c3f8f4;
    }
    fn_004f625d();
    fn_004ee8b9();
}

// FUNCTION: DAO 0x008f6266
int __cdecl fn_004f6266(struct tm* p)
{
    int r;
    fn_004f0a18(6);
    r = fn_004f6041(p);
    fn_004f629e();
    fn_004ee8b9();
    return r;
}

// FUNCTION: DAO 0x008f62a7
int __cdecl fn_004f62a7(long* p)
{
    if (p == 0) {
        *fn_004e37b6() = 22;
        fn_004e11ce(0, 0, 0, 0, 0);
        return 22;
    }
    *p = g_00c1629c;
    return 0;
}

// FUNCTION: DAO 0x008f62db
int __cdecl fn_004f62db(long* p)
{
    if (p == 0) {
        *fn_004e37b6() = 22;
        fn_004e11ce(0, 0, 0, 0, 0);
        return 22;
    }
    *p = g_00c162a0;
    return 0;
}

// FUNCTION: DAO 0x008f630f
int __cdecl fn_004f630f(long* p)
{
    if (p == 0) {
        *fn_004e37b6() = 22;
        fn_004e11ce(0, 0, 0, 0, 0);
        return 22;
    }
    *p = g_00c16298;
    return 0;
}

// FUNCTION: DAO 0x008f6360
__int64 __stdcall fn_004f6360(__int64 a, __int64 b)
{
    unsigned __int64 ua, ub, rem;
    bool neg;
    int i;

    if (a < 0) {
        ua = (unsigned __int64)(-(a + 1)) + 1;
        neg = true;
    } else {
        ua = (unsigned __int64)a;
        neg = false;
    }
    if (b < 0)
        ub = (unsigned __int64)(-(b + 1)) + 1;
    else
        ub = (unsigned __int64)b;

    rem = 0;
    for (i = 63; i >= 0; --i) {
        rem = (rem << 1) | ((ua >> i) & 1);
        if (rem >= ub)
            rem -= ub;
    }
    if (neg)
        return -(__int64)rem;
    return (__int64)rem;
}

// FUNCTION: DAO 0x008f6412
void* __cdecl fn_004f6412(void)
{
    void* ptd;
    void** slot;
    void* buf;

    ptd = fn_004ee241();
    if (ptd == 0) {
        *fn_004e37b6() = 12;
        return 0;
    }
    slot = (void**)((char*)ptd + 0x44);
    if (*slot == 0) {
        buf = fn_004eb4a1(0x24);
        if (buf == 0) {
            *fn_004e37b6() = 12;
            return 0;
        }
        *slot = buf;
    }
    return *slot;
}
