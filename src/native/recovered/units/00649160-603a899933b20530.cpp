struct CInner00649 {
    char pad_00[0x20];
    int field_20;
    int field_24;
};

class MapTiles {
public:
    void fn_006490b0(int row, int col);
    void fn_00649110(int row, int col);
    int fn_00649160(int row, int col);
    void fn_006491a0(int row, int col);
    void fn_006491f0(int row, int col);
    int fn_00649240(int row, int col);
    int fn_00649290(int row, int col);
    void fn_00649550(int row, int col, unsigned char value);
private:
    char pad_00[0x20];
    int field_20;
    int field_24;
    char pad_28[0x14];
    unsigned char* field_3c;
    char pad_40[4];
    unsigned char* field_44;
};

class ObjectC {
public:
    int fn_00649c70(int a, int b);
    int fn_00649cb0();
private:
    int field_0;
    int field_4;
    char pad_8[0x30 - 0x8];
    CInner00649* field_30;
};

class ObjectD {
public:
    int fn_00649d10(int value);
private:
    char pad_0[4];
    int field_4;
    int field_8;
    char pad_c[8];
    int* field_14;
    int* field_18;
};

class ObjectE {
public:
    void fn_00653640(unsigned int bytes);
    unsigned int fn_00653690();
    unsigned char* fn_00658300();
private:
    char pad_0[0x1c];
    unsigned int field_1c;
    char pad_20[0x14];
    unsigned int field_34;
    char pad_38[0x10];
    unsigned char field_48[1];
};

// FUNCTION: DAO 0x00A490B0
void MapTiles::fn_006490b0(int row, int col) {
    unsigned char* base = this->field_3c;
    if (base == 0) return;
    if (row >= this->field_24 || col >= this->field_20 || row < 0 || col < 0) return;
    unsigned int index = (unsigned int)this->field_20 * (unsigned int)row + (unsigned int)col;
    unsigned char b = base[index];
    unsigned int v = (b >> 4) & 3;
    if (v < 3) ++v;
    unsigned char mask = (unsigned char)((b ^ (unsigned char)(v << 4)) & 0x30);
    base[index] = (unsigned char)(b ^ mask);
}

// FUNCTION: DAO 0x00A49110
void MapTiles::fn_00649110(int row, int col) {
    unsigned char* base = this->field_3c;
    if (base == 0) return;
    if (row >= this->field_24 || col >= this->field_20 || row < 0 || col < 0) return;
    unsigned int index = (unsigned int)this->field_20 * (unsigned int)row + (unsigned int)col;
    unsigned char b = base[index];
    unsigned int v = (b >> 4) & 3;
    if (v > 0) --v;
    unsigned char mask = (unsigned char)((b ^ (unsigned char)(v << 4)) & 0x30);
    base[index] = (unsigned char)(b ^ mask);
}

// FUNCTION: DAO 0x00A49160
int MapTiles::fn_00649160(int row, int col) {
    unsigned int result = 0;
    unsigned char* base = this->field_3c;
    if (base != 0) {
        if (row < this->field_24 && col < this->field_20 && row >= 0 && col >= 0) {
            unsigned int index = (unsigned int)this->field_20 * (unsigned int)row + (unsigned int)col;
            result = (unsigned int)((base[index] >> 4) & 3);
        }
    }
    return (int)result;
}

// FUNCTION: DAO 0x00A491A0
void MapTiles::fn_006491a0(int row, int col) {
    unsigned char* base = this->field_3c;
    if (base == 0) return;
    if (row >= this->field_24 || col >= this->field_20 || row < 0 || col < 0) return;
    unsigned int index = (unsigned int)this->field_20 * (unsigned int)row + (unsigned int)col;
    unsigned char b = base[index];
    unsigned int v = b >> 6;
    if (v < 3) ++v;
    base[index] = (unsigned char)((b & 0x3f) | (unsigned char)(v << 6));
}

// FUNCTION: DAO 0x00A491F0
void MapTiles::fn_006491f0(int row, int col) {
    unsigned char* base = this->field_3c;
    if (base == 0) return;
    if (row >= this->field_24 || col >= this->field_20 || row < 0 || col < 0) return;
    unsigned int index = (unsigned int)this->field_20 * (unsigned int)row + (unsigned int)col;
    unsigned char b = base[index];
    unsigned int v = b >> 6;
    if (v > 0) --v;
    base[index] = (unsigned char)((b & 0x3f) | (unsigned char)(v << 6));
}

// FUNCTION: DAO 0x00A49240
int MapTiles::fn_00649240(int row, int col) {
    unsigned int result = 0;
    unsigned char* base = this->field_3c;
    if (base != 0) {
        if (row < this->field_24 && col < this->field_20 && row >= 0 && col >= 0) {
            unsigned int index = (unsigned int)this->field_20 * (unsigned int)row + (unsigned int)col;
            unsigned char b = base[index];
            unsigned char hi = (unsigned char)(b & 0xc0);
            if (hi > 0x40) result = 1;
            else result = (unsigned int)(b >> 6);
        }
    }
    return (int)result;
}

// FUNCTION: DAO 0x00A49290
int MapTiles::fn_00649290(int row, int col) {
    unsigned int result = 0;
    unsigned char* base = this->field_44;
    if (base != 0) {
        if (row < this->field_24 && col < this->field_20 && row >= 0 && col >= 0) {
            unsigned int index = (unsigned int)this->field_20 * (unsigned int)row + (unsigned int)col;
            result = base[index];
        }
    }
    return (int)result;
}

// FUNCTION: DAO 0x00A49550
void MapTiles::fn_00649550(int row, int col, unsigned char value) {
    if (row >= this->field_24 || col >= this->field_20 || row < 0 || col < 0) return;
    unsigned char* base = this->field_3c;
    unsigned int index = (unsigned int)this->field_20 * (unsigned int)row + (unsigned int)col;
    unsigned char b = base[index];
    unsigned char x = (unsigned char)(b ^ value);
    x &= 0x0f;
    base[index] = (unsigned char)(b ^ x);
}

// FUNCTION: DAO 0x00A49C70
int ObjectC::fn_00649c70(int a, int b) {
    if (a < 0 || b < 0) return -1;
    CInner00649* p = this->field_30;
    if (a >= p->field_20 || b >= p->field_24) return -1;
    int qa = a / this->field_0;
    int qb = b / this->field_0;
    return qa + qb * this->field_4;
}

// FUNCTION: DAO 0x00A49CB0
int ObjectC::fn_00649cb0() {
    unsigned int v = (unsigned int)this->field_0;
    return (int)(v + v);
}

// FUNCTION: DAO 0x00A49D10
int ObjectD::fn_00649d10(int value) {
    int count;
    if (this->field_14 == 0) {
        count = 0;
    } else {
        count = (int)(this->field_18 - this->field_14);
    }
    int prod = this->field_8 * this->field_4;
    if (count == prod) return -1;
    int w = this->field_4;
    int q = value / w;
    int r = value % w;
    int halfW = (w + 1) / 2;
    int halfQ = q / 2;
    int halfR = r / 2;
    return halfR + halfW * halfQ;
}

// FUNCTION: DAO 0x00A53640
void ObjectE::fn_00653640(unsigned int bytes) {
    this->field_1c = (bytes + 0x0f) >> 4;
}

// FUNCTION: DAO 0x00A53690
unsigned int ObjectE::fn_00653690() {
    return this->field_34;
}

// FUNCTION: DAO 0x00A58300
unsigned char* ObjectE::fn_00658300() {
    return this->field_48;
}
