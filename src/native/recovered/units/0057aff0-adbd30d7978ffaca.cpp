struct GColor {
    unsigned char b;
    unsigned char g;
    unsigned char r;
    unsigned char a;
    void __thiscall fn_005782c0(int H, int S, int V);
    void __thiscall fn_005785e0(int* outH, int* outS, int* outV);
};

struct C_57aff0 {
    unsigned char pad[0x8c];
    unsigned short flags;
    void __thiscall fn_0057aff0(bool flag);
};

struct C_57bfc0_Entry {
    int marker;
    int pad[7];
};

struct C_57bfc0_Container {
    void* unk0;
    unsigned int count;
};

struct C_57bfc0 {
    void* field0;
    unsigned int index;
    void __thiscall fn_0057bfc0();
};

struct C_59e950 {
    unsigned char pad[0x20];
    int* ptr;
    int* __thiscall fn_0059e950();
};

// FUNCTION: DAO 0x9782c0
void __thiscall GColor::fn_005782c0(int H, int S, int V) {
    if (S == 0 || H <= -1) {
        b = (unsigned char)V;
        g = (unsigned char)V;
        r = (unsigned char)V;
        return;
    }
    if (H >= 360)
        H %= 360;

    int sector = H / 60;
    int rem = H - sector * 60;

    unsigned int e = (unsigned int)(255 - S) * (unsigned int)V;
    unsigned int p = (2u * e + 255u) / 510u;

    if ((sector & 1) == 0) {
        unsigned int a = (unsigned int)(15300 - (60 - rem) * S) * (unsigned int)V;
        unsigned int x = (2u * a + 15300u) / 30600u;
        switch (sector) {
        case 0:
            b = (unsigned char)p;
            g = (unsigned char)x;
            r = (unsigned char)V;
            break;
        case 2:
            b = (unsigned char)x;
            g = (unsigned char)V;
            r = (unsigned char)p;
            break;
        case 4:
            b = (unsigned char)V;
            g = (unsigned char)p;
            r = (unsigned char)x;
            break;
        }
    } else {
        unsigned int a = (unsigned int)(15300 - rem * S) * (unsigned int)V;
        unsigned int x = (2u * a + 15300u) / 30600u;
        switch (sector) {
        case 1:
            b = (unsigned char)p;
            g = (unsigned char)V;
            r = (unsigned char)x;
            break;
        case 3:
            b = (unsigned char)V;
            g = (unsigned char)x;
            r = (unsigned char)p;
            break;
        case 5:
            b = (unsigned char)x;
            g = (unsigned char)p;
            r = (unsigned char)V;
            break;
        }
    }
}

// FUNCTION: DAO 0x9785e0
void __thiscall GColor::fn_005785e0(int* outH, int* outS, int* outV) {
    int B = (int)b;
    int G = (int)g;
    int R = (int)r;

    int max = R;
    int maxIndex = 0;
    if (G > R) {
        max = G;
        maxIndex = 1;
    }
    if (B > max) {
        max = B;
        maxIndex = 2;
    }

    int min = R;
    if (G < R)
        min = G;
    if (B < min)
        min = B;

    int diff = max - min;
    *outV = max;

    if (max == 0) {
        *outS = 0;
        *outH = 0;
        return;
    }

    unsigned int S = ((unsigned int)diff * 510u + (unsigned int)max) / (2u * (unsigned int)max);
    *outS = (int)S;
    if (S == 0) {
        *outH = 0;
        return;
    }

    int H;
    if (maxIndex == 0) {
        if (G >= B)
            H = (diff + 120 * (G - B)) / (2 * diff);
        else
            H = 300 + (diff + 120 * (diff - B + G)) / (2 * diff);
    } else if (maxIndex == 1) {
        if (B > R)
            H = 120 + (diff + 120 * (B - R)) / (2 * diff);
        else
            H = 60 + (diff + 120 * (diff - R + B)) / (2 * diff);
    } else {
        if (R > G)
            H = 240 + (diff + 120 * (R - G)) / (2 * diff);
        else
            H = 180 + (diff + 120 * (diff - G + R)) / (2 * diff);
    }
    *outH = H;
}

// FUNCTION: DAO 0x97aff0
void __thiscall C_57aff0::fn_0057aff0(bool flag) {
    if (flag)
        flags |= 0x600;
    else
        flags = (unsigned short)((flags & 0xfdff) | 0x400);
}

// FUNCTION: DAO 0x97bfc0
void __thiscall C_57bfc0::fn_0057bfc0() {
    C_57bfc0_Container* c = *(C_57bfc0_Container**)field0;
    C_57bfc0_Entry* entries = (C_57bfc0_Entry*)((unsigned char*)c + 8);
    unsigned int idx = index;
    if (idx > c->count)
        return;
    ++idx;
    index = idx;
    if (idx > c->count)
        return;
    while (entries[idx].marker == -2) {
        ++idx;
        index = idx;
        if (idx > c->count)
            break;
    }
}

// FUNCTION: DAO 0x99e950
int* __thiscall C_59e950::fn_0059e950() {
    int* p = ptr;
    ++*p;
    return ptr;
}
