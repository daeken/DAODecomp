// DAOrigins.exe VC8 x86 reconstruction
class C_00002910 {
public:
    void* fn_00002910();
private:
    unsigned int field0;
    void* field4;
    unsigned int field8;
    unsigned int fieldC;
    unsigned int field10;
    unsigned int field14;
    unsigned int field18;
};

class C_000b94f0 {
public:
    void fn_000b94f0();
private:
    unsigned char pad0[0x54];
    unsigned short field54;
    unsigned char pad56[0xD4 - 0x56];
    unsigned int fieldD4;
    unsigned int fieldD8;
    unsigned int fieldDC;
    unsigned int fieldE0;
    unsigned int fieldE4;
    unsigned int fieldE8;
    unsigned int fieldEC;
    unsigned int fieldF0;
    unsigned int fieldF4;
    unsigned int fieldF8;
    unsigned char fieldFC;
    unsigned char fieldFD;
};

class C_000e7050 {
public:
    unsigned int fn_000e7050();
private:
    unsigned int field00;
    unsigned int field04;
    unsigned int field08;
    unsigned int field0C;
    unsigned int field10;
    unsigned int field14;
    unsigned int field18;
    unsigned int field1C;
    unsigned int field20;
    unsigned int field24;
    unsigned int field28;
    unsigned int field2C;
    unsigned char pad30[0x40 - 0x30];
    unsigned int field40;
    unsigned int field44;
    unsigned int field48;
    unsigned int field4C;
    unsigned int field50;
    unsigned int field54;
    unsigned int field58;
    unsigned int field5C;
};

class C_0014f810 {
public:
    unsigned char fn_0014f810();
private:
    unsigned char pad0[0x270];
    unsigned char field270;
};

struct C_TreeNode {
    C_TreeNode* field0;
    C_TreeNode* field4;
    C_TreeNode* field8;
    unsigned char padC[0x25 - 0x0C];
    unsigned char field25;
};

class C_0027a910 {
public:
    void fn_0027a910(C_TreeNode* node);
private:
    unsigned int pad0;
    C_TreeNode* field4;
};

class C_0047b880 {
public:
    void fn_0047b880(C_TreeNode* node);
private:
    unsigned int pad0;
    C_TreeNode* field4;
};

// FUNCTION: DAO 0x00402910
void* __thiscall C_00002910::fn_00002910()
{
    if (field18 >= 8)
        return field4;
    return (void*)((unsigned char*)this + 4);
}

// FUNCTION: DAO 0x004B94F0
void __thiscall C_000b94f0::fn_000b94f0()
{
    field54 = 0;
    fieldD4 = 0xFFFFFFFFu;
    fieldD8 = 0;
    fieldDC = 0;
    fieldE0 = 0;
    fieldE4 = 0;
    fieldE8 = 4;
    fieldEC = 0x28;
    fieldF8 = 1;
    fieldF0 = 0;
    fieldFC = 1;
    fieldFD = 0;
    fieldF4 = 0;
}

// FUNCTION: DAO 0x004CCD70
void __cdecl fn_000ccd70(unsigned int* dst, unsigned int count, const unsigned int* src)
{
    if (count == 0)
        return;
    do
    {
        if (dst != 0)
        {
            dst[0] = src[0];
            dst[1] = src[1];
        }
        dst += 2;
    } while (--count != 0);
}

// FUNCTION: DAO 0x004E7050
unsigned int __thiscall C_000e7050::fn_000e7050()
{
    unsigned int a0 = field00;
    unsigned int t = ((a0 << field40) ^ a0);
    t = (t >> field20) ^ ((field10 & a0) << field50);

    unsigned int a1 = field04;
    unsigned int u = ((a1 << field44) ^ a1);
    u = (u >> field24) ^ ((field14 & a1) << field54);

    unsigned int a2 = field08;
    unsigned int v = ((a2 << field48) ^ a2);
    v = (v >> field28) ^ ((field18 & a2) << field58);

    unsigned int a3 = field0C;
    unsigned int w = ((a3 << field4C) ^ a3);
    w = (w >> field2C) ^ ((field1C & a3) << field5C);

    field00 = t;
    field04 = u;
    field08 = v;
    field0C = w;

    return w ^ v ^ u ^ t;
}

// FUNCTION: DAO 0x0054F810
unsigned char __thiscall C_0014f810::fn_0014f810()
{
    return field270;
}

// FUNCTION: DAO 0x0061BD30
void __cdecl fn_0021bd30(unsigned int* dst, unsigned int* end, const unsigned int* src)
{
    if (dst == end)
        return;
    do
    {
        *dst = *src;
        ++dst;
    } while (dst != end);
}

// FUNCTION: DAO 0x0067A910
void __thiscall C_0027a910::fn_0027a910(C_TreeNode* node)
{
    C_TreeNode* left = node->field0;
    C_TreeNode* rightOfLeft = left->field8;
    node->field0 = rightOfLeft;
    if (rightOfLeft->field25 == 0)
        rightOfLeft->field4 = node;
    left->field4 = node->field4;

    C_TreeNode* header = this->field4;
    if (node == header->field4)
    {
        header->field4 = left;
        left->field8 = node;
        node->field4 = left;
        return;
    }

    C_TreeNode* parent = node->field4;
    if (node == parent->field8)
    {
        parent->field8 = left;
        left->field8 = node;
        node->field4 = left;
        return;
    }

    parent->field0 = left;
    left->field8 = node;
    node->field4 = left;
}

// FUNCTION: DAO 0x00823430
unsigned int* __stdcall fn_00423430(unsigned int* dst, unsigned int count, const unsigned int* src)
{
    unsigned int* const start = dst;
    if (count != 0)
    {
        unsigned int n = count;
        do
        {
            *dst = *src;
            ++dst;
            --n;
        } while (n != 0);
    }
    return start + count;
}

// FUNCTION: DAO 0x0087B880
void __thiscall C_0047b880::fn_0047b880(C_TreeNode* node)
{
    C_TreeNode* right = node->field8;
    C_TreeNode* leftOfRight = right->field0;
    node->field8 = leftOfRight;
    if (leftOfRight->field25 == 0)
        leftOfRight->field4 = node;
    right->field4 = node->field4;

    C_TreeNode* header = this->field4;
    if (node == header->field4)
    {
        header->field4 = right;
        right->field0 = node;
        node->field4 = right;
        return;
    }

    C_TreeNode* parent = node->field4;
    if (node == parent->field0)
    {
        parent->field0 = right;
        right->field0 = node;
        node->field4 = right;
        return;
    }

    parent->field8 = right;
    right->field0 = node;
    node->field4 = right;
}

// FUNCTION: DAO 0x008FC637
int __cdecl fn_004fc637(unsigned short ch)
{
    if (ch < 0x30)
        return -1;
    if (ch < 0x3A)
        return (int)ch - 0x30;

    if (ch >= 0xFF10)
    {
        if (ch < 0xFF1A)
            return (int)ch - 0xFF10;
        return -1;
    }

    if (ch < 0x660)
        return -1;
    if (ch < 0x66A)
        return (int)ch - 0x660;

    if (ch < 0x6F0)
        return -1;
    if (ch < 0x6FA)
        return (int)ch - 0x6F0;

    if (ch < 0x966)
        return -1;
    if (ch < 0x970)
        return (int)ch - 0x966;

    if (ch < 0x9E6)
        return -1;
    if (ch < 0x9F0)
        return (int)ch - 0x9E6;

    if (ch < 0xA66)
        return -1;
    if (ch < 0xA70)
        return (int)ch - 0xA66;

    if (ch < 0xAE6)
        return -1;
    if (ch < 0xAF0)
        return (int)ch - 0xAE6;

    if (ch < 0xB66)
        return -1;
    if (ch < 0xB70)
        return (int)ch - 0xB66;

    if (ch < 0xC66)
        return -1;
    if (ch < 0xC70)
        return (int)ch - 0xC66;

    if (ch < 0xCE6)
        return -1;
    if (ch < 0xCF0)
        return (int)ch - 0xCE6;

    if (ch < 0xD66)
        return -1;
    if (ch < 0xD70)
        return (int)ch - 0xD66;

    if (ch < 0xE50)
        return -1;
    if (ch < 0xE5A)
        return (int)ch - 0xE50;

    if (ch < 0xED0)
        return -1;
    if (ch < 0xEDA)
        return (int)ch - 0xED0;

    if (ch < 0xF20)
        return -1;
    if (ch < 0xF2A)
        return (int)ch - 0xF20;

    if (ch < 0x1040)
        return -1;
    if (ch < 0x104A)
        return (int)ch - 0x1040;

    if (ch < 0x17E0)
        return -1;
    if (ch < 0x17EA)
        return (int)ch - 0x17E0;

    if (ch < 0x1810)
        return -1;
    if (ch < 0x181A)
        return (int)ch - 0x1810;

    return -1;
}

// FUNCTION: DAO 0x00A523C0
void __cdecl fn_006523c0(const unsigned int* begin, const unsigned int* end, unsigned int* dst)
{
    if (begin == end)
        return;
    do
    {
        if (dst != 0)
        {
            dst[0] = begin[0];
            dst[1] = begin[1];
        }
        begin += 2;
        dst += 2;
    } while (begin != end);
}
