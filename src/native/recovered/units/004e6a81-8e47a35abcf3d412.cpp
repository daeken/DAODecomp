// Provisional deterministic Ghidra seed; signatures/types remain hypotheses.
typedef unsigned int pointer32;
typedef unsigned int code(...);
typedef unsigned char   undefined;
typedef unsigned char    byte;
typedef unsigned int    dword;
typedef unsigned __int64    GUID;
typedef pointer32 ImageBaseOffset32;

typedef __int64    longlong;
typedef unsigned char    uchar;
typedef unsigned int    uint;
typedef unsigned long    ulong;
typedef unsigned __int64    ulonglong;
typedef unsigned char    undefined1;
typedef unsigned short    undefined2;
typedef unsigned int    undefined4;
typedef unsigned __int64    undefined6;
typedef unsigned __int64    undefined8;
typedef unsigned short    ushort;
typedef unsigned short    word;
typedef struct _tiddata _tiddata, *P_tiddata;

typedef struct _tiddata *_ptiddata;

typedef uint uintptr_t;

typedef struct threadmbcinfostruct threadmbcinfostruct, *Pthreadmbcinfostruct;

typedef struct threadmbcinfostruct *pthreadmbcinfo;

typedef struct threadlocaleinfostruct threadlocaleinfostruct, *Pthreadlocaleinfostruct;

typedef struct threadlocaleinfostruct *pthreadlocinfo;

typedef struct setloc_struct setloc_struct, *Psetloc_struct;

typedef struct setloc_struct _setloc_struct;

typedef struct localerefcount localerefcount, *Plocalerefcount;

typedef struct localerefcount locrefcount;

typedef struct lconv lconv, *Plconv;

typedef struct __lc_time_data __lc_time_data, *P__lc_time_data;

typedef int BOOL;

typedef uint UINT;

typedef struct _is_ctype_compatible _is_ctype_compatible, *P_is_ctype_compatible;

struct lconv {
    char *decimal_point;
    char *thousands_sep;
    char *grouping;
    char *int_curr_symbol;
    char *currency_symbol;
    char *mon_decimal_point;
    char *mon_thousands_sep;
    char *mon_grouping;
    char *positive_sign;
    char *negative_sign;
    char int_frac_digits;
    char frac_digits;
    char p_cs_precedes;
    char p_sep_by_space;
    char n_cs_precedes;
    char n_sep_by_space;
    char p_sign_posn;
    char n_sign_posn;
    wchar_t *_W_decimal_point;
    wchar_t *_W_thousands_sep;
    wchar_t *_W_int_curr_symbol;
    wchar_t *_W_currency_symbol;
    wchar_t *_W_mon_decimal_point;
    wchar_t *_W_mon_thousands_sep;
    wchar_t *_W_positive_sign;
    wchar_t *_W_negative_sign;
};

struct _is_ctype_compatible {
    ulong id;
    int is_clike;
};

struct setloc_struct {
    wchar_t *pchLanguage;
    wchar_t *pchCountry;
    int iLocState;
    int iPrimaryLen;
    BOOL bAbbrevLanguage;
    BOOL bAbbrevCountry;
    UINT _cachecp;
    wchar_t _cachein[131];
    wchar_t _cacheout[131];
    struct _is_ctype_compatible _Loc_c[5];
    wchar_t _cacheLocaleName[85];
};

struct threadmbcinfostruct {
    int refcount;
    int mbcodepage;
    int ismbcodepage;
    ushort mbulinfo[6];
    uchar mbctype[257];
    uchar mbcasemap[256];
    wchar_t *mblocalename;
};

struct localerefcount {
    char *locale;
    wchar_t *wlocale;
    int *refcount;
    int *wrefcount;
};

struct threadlocaleinfostruct {
    int refcount;
    uint lc_codepage;
    uint lc_collate_cp;
    uint lc_time_cp;
    locrefcount lc_category[6];
    int lc_clike;
    int mb_cur_max;
    int *lconv_intl_refcount;
    int *lconv_num_refcount;
    int *lconv_mon_refcount;
    struct lconv *lconv;
    int *ctype1_refcount;
    ushort *ctype1;
    ushort *pctype;
    uchar *pclmap;
    uchar *pcumap;
    struct __lc_time_data *lc_time_curr;
    wchar_t *locale_name[6];
};

struct _tiddata {
    ulong _tid;
    uintptr_t _thandle;
    int _terrno;
    ulong _tdoserrno;
    uint _fpds;
    ulong _holdrand;
    char *_token;
    wchar_t *_wtoken;
    uchar *_mtoken;
    char *_errmsg;
    wchar_t *_werrmsg;
    char *_namebuf0;
    wchar_t *_wnamebuf0;
    char *_namebuf1;
    wchar_t *_wnamebuf1;
    char *_asctimebuf;
    wchar_t *_wasctimebuf;
    void *_gmtimebuf;
    char *_cvtbuf;
    uchar _con_ch_buf[5];
    ushort _ch_buf_used;
    void *_initaddr;
    void *_initarg;
    void *_pxcptacttab;
    void *_tpxcptinfoptrs;
    int _tfpecode;
    pthreadmbcinfo ptmbcinfo;
    pthreadlocinfo ptlocinfo;
    int _ownlocale;
    ulong _NLG_dwCode;
    void *_terminate;
    void *_unexpected;
    void *_translator;
    void *_purecall;
    void *_curexception;
    void *_curcontext;
    int _ProcessingThrow;
    void *_curexcspec;
    void *_pFrameInfoChain;
    _setloc_struct _setloc_data;
    void *_reserved1;
    void *_reserved2;
    void *_reserved3;
    void *_reserved4;
    void *_reserved5;
    int _cxxReThrow;
    ulong __initDomain;
    int _initapartment;
};

struct __lc_time_data {
    char *wday_abbr[7];
    char *wday[7];
    char *month_abbr[12];
    char *month[12];
    char *ampm[2];
    char *ww_sdatefmt;
    char *ww_ldatefmt;
    char *ww_timefmt;
    int ww_caltype;
    int refcount;
    wchar_t *_W_wday_abbr[7];
    wchar_t *_W_wday[7];
    wchar_t *_W_month_abbr[12];
    wchar_t *_W_month[12];
    wchar_t *_W_ampm[2];
    wchar_t *_W_ww_sdatefmt;
    wchar_t *_W_ww_ldatefmt;
    wchar_t *_W_ww_timefmt;
    wchar_t *_W_ww_locale_name;
};


extern "C" _ptiddata __cdecl fn_004ee2b8(void);

// FUNCTION: DAO 0x008e6a81
void fn_004e6a81(ulong param_1)
{
  _ptiddata p_Var1;
  
  p_Var1 = fn_004ee2b8();
  p_Var1->_holdrand = param_1;
  return;
}

