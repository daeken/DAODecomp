class MapTiles {
public:
    void fn_006490b0(int row, int col);
    void fn_00649110(int row, int col);
    void fn_006491a0(int row, int col);
    void fn_006491f0(int row, int col);
    int fn_00649240(int row, int col);
    unsigned char fn_00649290(int row, int col);
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

// FUNCTION: DAO 0x00A490B0
void MapTiles::fn_006490b0(int row, int col) {
    unsigned char* base = this->field_3c;
    if (base == 0) return;
    if (row >= this->field_24) return;
    if (col >= this->field_20) return;
    if (row < 0) return;
    if (col < 0) return;
    unsigned int index = (unsigned int)this->field_20 * (unsigned int)row + (unsigned int)col;
    int v = (base[index] >> 4) & 3;
    if (v < 3) ++v;
    base[index] ^= (unsigned char)(((v << 4) ^ base[index]) & 0x30);
}

// FUNCTION: DAO 0x00A49110
void MapTiles::fn_00649110(int row, int col) {
    unsigned char* base = this->field_3c;
    if (base == 0) return;
    if (row >= this->field_24) return;
    if (col >= this->field_20) return;
    if (row < 0) return;
    if (col < 0) return;
    unsigned int index = (unsigned int)this->field_20 * (unsigned int)row + (unsigned int)col;
    int v = (base[index] >> 4) & 3;
    if (v > 0) --v;
    base[index] ^= (unsigned char)(((v << 4) ^ base[index]) & 0x30);
}

// FUNCTION: DAO 0x00A491A0
void MapTiles::fn_006491a0(int row, int col) {
    unsigned char* base = this->field_3c;
    if (base == 0) return;
    if (row >= this->field_24) return;
    if (col >= this->field_20) return;
    if (row < 0) return;
    if (col < 0) return;
    unsigned int index = (unsigned int)this->field_20 * (unsigned int)row + (unsigned int)col;
    int v = base[index] >> 6;
    if (v < 3) ++v;
    base[index] = (unsigned char)((base[index] & 0x3f) | (v << 6));
}

// FUNCTION: DAO 0x00A491F0
void MapTiles::fn_006491f0(int row, int col) {
    unsigned char* base = this->field_3c;
    if (base == 0) return;
    if (row >= this->field_24) return;
    if (col >= this->field_20) return;
    if (row < 0) return;
    if (col < 0) return;
    unsigned int index = (unsigned int)this->field_20 * (unsigned int)row + (unsigned int)col;
    int v = base[index] >> 6;
    if (v > 0) --v;
    base[index] = (unsigned char)((base[index] & 0x3f) | (v << 6));
}

// FUNCTION: DAO 0x00A49240
int MapTiles::fn_00649240(int row, int col) {
    int result = 0;
    unsigned char* base = this->field_3c;
    if (base != 0) {
        if (row < this->field_24 && col < this->field_20 && row >= 0 && col >= 0) {
            unsigned int index = (unsigned int)this->field_20 * (unsigned int)row + (unsigned int)col;
            unsigned char b = base[index];
            if ((unsigned char)(b & 0xc0) > 0x40) result = 1;
            else result = (int)(b >> 6);
        }
    }
    return result;
}

// FUNCTION: DAO 0x00A49290
unsigned char MapTiles::fn_00649290(int row, int col) {
    unsigned char result = 0;
    unsigned char* base = this->field_44;
    if (base != 0) {
        if (row < this->field_24 && col < this->field_20 && row >= 0 && col >= 0) {
            unsigned int index = (unsigned int)this->field_20 * (unsigned int)row + (unsigned int)col;
            result = base[index];
        }
    }
    return result;
}

// FUNCTION: DAO 0x00A49550
void MapTiles::fn_00649550(int row, int col, unsigned char value) {
    if (row >= this->field_24) return;
    if (col >= this->field_20) return;
    if (row < 0) return;
    if (col < 0) return;
    unsigned char* base = this->field_3c;
    unsigned int index = (unsigned int)this->field_20 * (unsigned int)row + (unsigned int)col;
    base[index] ^= (unsigned char)((base[index] ^ value) & 0x0f);
}

// FUNCTION: DAO 0x00A49D10
int ObjectD::fn_00649d10(int value) {
    int count;
    if (this->field_14 == 0) {
        count = 0;
    } else {
        count = (int)(this->field_18 - this->field_14);
    }
    if (count == this->field_8 * this->field_4) return -1;
    int w = this->field_4;
    int q = value / w;
    int r = value % w;
    int halfW = (w + 1) / 2;
    int halfQ = q / 2;
    int halfR = r / 2;
    return halfR + halfW * halfQ;
}
