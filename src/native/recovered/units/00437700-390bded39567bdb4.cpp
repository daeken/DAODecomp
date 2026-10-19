struct S4 { unsigned int a, b, c, d; };

struct DeflateState {
    unsigned char pad0[8];
    unsigned char* pending_buf;
    unsigned int pending_buf_size;
    unsigned char* pending_out;
    unsigned int pending;
    unsigned char pad18[0x14];
    unsigned int w_size;
    unsigned int w_bits;
    unsigned int w_mask;
    unsigned char* window;
    unsigned char pad3c[4];
    unsigned short* prev;
    unsigned char pad44[0x28];
    unsigned int strstart;
    unsigned int match_start;
    unsigned int lookahead;
    unsigned int prev_length;
    unsigned int max_chain_length;
    unsigned char pad80[0x0c];
    unsigned int good_match;
    unsigned int nice_match;
    unsigned int fn_0043bea0(unsigned int cur_match);
};

// FUNCTION: DAO 0x00837700
unsigned int __cdecl fn_00437700(unsigned int* p) {
    switch (*p) {
    case 0: return 0;
    case 1: return 1;
    default: return 0;
    }
}

// FUNCTION: DAO 0x00837720
unsigned int __cdecl fn_00437720(const unsigned int* p) {
    unsigned int v = *p;
    unsigned int r = 0;
    if (v & 1) r = 1;
    if (v & 4) r |= 2;
    if (v & 2) r |= 4;
    return r;
}

// FUNCTION: DAO 0x008377b0
void __cdecl fn_004377b0(unsigned int* dst, const unsigned int* src) {
    *(S4*)dst = *(const S4*)src;
}

// FUNCTION: DAO 0x0083b2e0
void __fastcall fn_0043b2e0(unsigned int value, DeflateState* s) {
    s->pending_buf[s->pending] = (unsigned char)(value >> 8);
    s->pending++;
    s->pending_buf[s->pending] = (unsigned char)value;
    s->pending++;
}

// FUNCTION: DAO 0x0083bd20
unsigned int __fastcall fn_0043bd20(unsigned int cur_match, DeflateState* s) {
    unsigned int chain_length = s->max_chain_length;
    unsigned char* scan_start = s->window + s->strstart;
    unsigned char* scan = scan_start;
    int best_len = (int)s->prev_length;
    int nice_match = (int)s->nice_match;
    unsigned int limit;
    unsigned int wmask = s->w_mask;
    unsigned short* prev = s->prev;
    unsigned char* strend = scan_start + 0x102;
    unsigned char scan_end1 = scan_start[best_len - 1];
    unsigned char scan_end = scan_start[best_len];

    if (s->strstart > s->w_size - 0x106) {
        limit = s->strstart - s->w_size + 0x106;
    } else {
        limit = 0;
    }

    if (s->prev_length >= s->good_match) {
        chain_length >>= 2;
    }
    if ((unsigned int)nice_match > s->lookahead) {
        nice_match = (int)s->lookahead;
    }

    do {
        unsigned char* match = s->window + cur_match;
        if (match[best_len] == scan_end &&
            match[best_len - 1] == scan_end1 &&
            match[0] == scan[0] &&
            match[1] == scan[1]) {
            scan = scan_start + 2;
            match += 2;
            do {
            } while (*++scan == *++match && *++scan == *++match &&
                     *++scan == *++match && *++scan == *++match &&
                     *++scan == *++match && *++scan == *++match &&
                     *++scan == *++match && *++scan == *++match &&
                     scan < strend);
            unsigned int len = (unsigned int)(scan - scan_start);
            scan = scan_start;
            if ((int)len > best_len) {
                s->match_start = cur_match;
                best_len = (int)len;
                if ((int)len >= nice_match) break;
                scan_end1 = scan_start[best_len - 1];
                scan_end = scan_start[best_len];
            }
        }
        cur_match = prev[cur_match & wmask];
    } while (cur_match > limit && --chain_length != 0);

    if ((unsigned int)best_len <= s->lookahead) return (unsigned int)best_len;
    return s->lookahead;
}

// FUNCTION: DAO 0x0083bea0
unsigned int __thiscall DeflateState::fn_0043bea0(unsigned int cur_match) {
    unsigned char* scan_start = window + strstart;
    unsigned char* match = window + cur_match;
    unsigned char* scan = scan_start;
    unsigned char* strend = scan_start + 0x102;
    if (match[0] != scan[0] || match[1] != scan[1]) {
        return 2;
    }
    scan += 2;
    match += 2;
    do {
    } while (*++scan == *++match && *++scan == *++match &&
             *++scan == *++match && *++scan == *++match &&
             *++scan == *++match && *++scan == *++match &&
             *++scan == *++match && *++scan == *++match &&
             scan < strend);
    unsigned int len = (unsigned int)(scan - scan_start);
    if (len < 3) return 2;
    match_start = cur_match;
    if (len <= lookahead) return len;
    return lookahead;
}

// FUNCTION: DAO 0x0083cb80
int __cdecl fn_0043cb80(void* strm_) {
    unsigned char* strm = (unsigned char*)strm_;
    unsigned char* state;
    if (strm != 0 && (state = *(unsigned char**)(strm + 0x1c)) != 0) {
        *(unsigned char**)(state + 0x1c) = 0;
        *(unsigned int*)(strm + 0x14) = 0;
        *(unsigned int*)(strm + 8) = 0;
        *(unsigned int*)(strm + 0x18) = 0;
        *(unsigned int*)(strm + 0x30) = 1;
        *(unsigned int*)(state + 0) = 0;
        *(unsigned int*)(state + 4) = 0;
        *(unsigned int*)(state + 0xc) = 0;
        *(unsigned int*)(state + 0x20) = 0;
        *(unsigned int*)(state + 0x28) = 0;
        *(unsigned int*)(state + 0x2c) = 0;
        *(unsigned int*)(state + 0x30) = 0;
        *(unsigned int*)(state + 0x38) = 0;
        *(unsigned int*)(state + 0x3c) = 0;
        unsigned char* p = state + 0x530;
        *(unsigned int*)(state + 0x14) = 0x8000;
        *(unsigned char**)(state + 0x6c) = p;
        *(unsigned char**)(state + 0x50) = p;
        *(unsigned char**)(state + 0x4c) = p;
        return 0;
    }
    return -2;
}
