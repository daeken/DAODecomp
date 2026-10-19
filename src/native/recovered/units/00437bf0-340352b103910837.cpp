struct C_00437bf0 {
    unsigned int field_0;
    unsigned int field_4;
    void fn_00437bf0(unsigned int v);
};

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

struct C_00444a80 {
    unsigned char data[0x28];
    void* fn_00444a80();
};

struct C_00444f70 {
    unsigned char pad[0xac];
    unsigned int field_ac;
    void fn_00444f70(unsigned int v);
};

// FUNCTION: DAO 0x00837700
unsigned int __cdecl fn_00437700(unsigned int* p) {
    unsigned int v = *p;
    if (v == 0) return 0;
    v -= 1;
    if (v != 0) return 0;
    return 1;
}

// FUNCTION: DAO 0x00837720
unsigned int __cdecl fn_00437720(unsigned int* p) {
    unsigned int v = *p;
    unsigned int r = 0;
    if (v & 1) r = 1;
    if (v & 4) r |= 2;
    if (v & 2) r |= 4;
    return r;
}

// FUNCTION: DAO 0x008377b0
void __cdecl fn_004377b0(unsigned int* dst, const unsigned int* src) {
    dst[0] = src[0];
    dst[1] = src[1];
    dst[2] = src[2];
    dst[3] = src[3];
}

// FUNCTION: DAO 0x00837bf0
void __thiscall C_00437bf0::fn_00437bf0(unsigned int v) {
    field_4 = v;
}

// FUNCTION: DAO 0x0083b2e0
void __fastcall fn_0043b2e0(unsigned int value, DeflateState* s) {
    unsigned char* buf = s->pending_buf;
    unsigned int pos = s->pending;
    buf[pos] = (unsigned char)(value >> 8);
    s->pending = pos + 1;
    buf = s->pending_buf;
    pos = s->pending;
    buf[pos] = (unsigned char)value;
    s->pending = pos + 1;
}

// FUNCTION: DAO 0x0083bd20
unsigned int __fastcall fn_0043bd20(unsigned int cur_match, DeflateState* s) {
    unsigned int chain_length = s->max_chain_length;
    unsigned char* scan_start = s->window + s->strstart;
    unsigned char* scan = scan_start;
    int best_len = (int)s->prev_length;
    unsigned int nice_match = s->nice_match;
    unsigned int limit;
    if (s->strstart > s->w_size - 0x106) {
        limit = s->strstart - s->w_size + 0x106;
    } else {
        limit = 0;
    }
    unsigned char scan_end1 = scan_start[best_len - 1];
    unsigned char scan_end = scan_start[best_len];
    unsigned char* strend = scan_start + 0x102;
    if ((unsigned int)best_len >= s->good_match) {
        chain_length >>= 2;
    }
    if (nice_match > s->lookahead) {
        nice_match = s->lookahead;
    }
    do {
        unsigned char* match = s->window + cur_match;
        if (match[best_len] == scan_end &&
            match[best_len - 1] == scan_end1 &&
            match[0] == scan_start[0] &&
            match[1] == scan_start[1]) {
            scan = scan_start + 2;
            match = s->window + cur_match + 2;
            do {
                scan++;
                match++;
                if (*scan != *match) break;
            } while (scan < strend);
            unsigned int len = (unsigned int)(scan - scan_start);
            if ((int)len > best_len) {
                s->match_start = cur_match;
                best_len = (int)len;
                if ((unsigned int)best_len >= nice_match) break;
                scan_end1 = scan_start[best_len - 1];
                scan_end = scan_start[best_len];
            }
        }
        cur_match = s->prev[cur_match & s->w_mask];
    } while (cur_match > limit && --chain_length != 0);
    if ((unsigned int)best_len <= s->lookahead) return (unsigned int)best_len;
    return s->lookahead;
}

// FUNCTION: DAO 0x0083bea0
unsigned int __thiscall DeflateState::fn_0043bea0(unsigned int cur_match) {
    unsigned char* window = this->window;
    unsigned int strstart = this->strstart;
    unsigned char* scan_start = window + strstart;
    unsigned char* match_start_ptr = window + cur_match;
    unsigned char* scan = scan_start;
    unsigned char* match = match_start_ptr;
    unsigned char* strend = scan_start + 0x102;
    if (match[0] != scan[0] || match[1] != scan[1]) {
        return 2;
    }
    scan = scan_start + 2;
    match = match_start_ptr + 2;
    do {
        scan++;
        match++;
        if (*scan != *match) break;
    } while (scan < strend);
    unsigned int len = (unsigned int)(scan - scan_start);
    if (len < 3) {
        return 2;
    }
    this->match_start = cur_match;
    if (len <= this->lookahead) {
        return len;
    }
    return this->lookahead;
}

// FUNCTION: DAO 0x0083cb80
int __cdecl fn_0043cb80(void* strm_) {
    unsigned char* strm = (unsigned char*)strm_;
    if (strm == 0) return -2;
    unsigned char* state = *(unsigned char**)(strm + 0x1c);
    if (state == 0) return -2;
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

// FUNCTION: DAO 0x0083e6a0
void __fastcall fn_0043e6a0(void* unused, DeflateState* s) {
    unsigned char* base = (unsigned char*)s;
    unsigned short* p = (unsigned short*)(base + 0x94);
    for (unsigned int i = 0; i < 0x11e; ++i) {
        *p = 0;
        p += 2;
    }
    p = (unsigned short*)(base + 0x988);
    for (unsigned int i = 0; i < 0x1e; ++i) {
        *p = 0;
        p += 2;
    }
    p = (unsigned short*)(base + 0xa7c);
    for (unsigned int i = 0; i < 0x13; ++i) {
        *p = 0;
        p += 2;
    }
    *(unsigned int*)(base + 0x16ac) = 0;
    *(unsigned int*)(base + 0x16a8) = 0;
    *(unsigned int*)(base + 0x16b0) = 0;
    *(unsigned int*)(base + 0x16a0) = 0;
    *(unsigned short*)(base + 0x494) = 1;
}

// FUNCTION: DAO 0x00844a80
void* __thiscall C_00444a80::fn_00444a80() {
    return (void*)(data + 0x28);
}

// FUNCTION: DAO 0x00844f70
void __thiscall C_00444f70::fn_00444f70(unsigned int v) {
    if (field_ac != v) {
        field_ac = v;
    }
}

// FUNCTION: DAO 0x008528c0
unsigned int __cdecl fn_004528c0(void* p) {
    return *(unsigned int*)((unsigned char*)p + 0x17c);
}
