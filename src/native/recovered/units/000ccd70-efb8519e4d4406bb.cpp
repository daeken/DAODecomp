// DAOrigins.exe VC8 x86 reconstruction
struct C_TreeNode {
    C_TreeNode* field0;
    C_TreeNode* field4;
    C_TreeNode* field8;
    unsigned char padC[0x25 - 0x0C];
    unsigned char field25;
};

class C_0027a910 {
public:
    C_TreeNode* fn_0027a910(C_TreeNode* node);
private:
    unsigned int pad0;
    C_TreeNode* field4;
};

class C_0047b880 {
public:
    C_TreeNode* fn_0047b880(C_TreeNode* node);
private:
    unsigned int pad0;
    C_TreeNode* field4;
};

// FUNCTION: DAO 0x004CCD70
void __cdecl fn_000ccd70(unsigned int* dst, unsigned int count, const unsigned int* src)
{
    for (; count > 0; --count, dst += 2)
    {
        if (dst != 0)
        {
            dst[0] = src[0];
            dst[1] = src[1];
        }
    }
}

// FUNCTION: DAO 0x0067A910
C_TreeNode* __thiscall C_0027a910::fn_0027a910(C_TreeNode* node)
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
        return left;
    }

    C_TreeNode* parent = node->field4;
    if (node == parent->field8)
    {
        parent->field8 = left;
        left->field8 = node;
        node->field4 = left;
        return left;
    }

    parent->field0 = left;
    left->field8 = node;
    node->field4 = left;
    return left;
}

// FUNCTION: DAO 0x00823430
unsigned int* __stdcall fn_00423430(unsigned int* dst, unsigned int count, const unsigned int* src)
{
    unsigned int* p = dst;
    for (unsigned int n = count; n != 0; --n, ++p)
    {
        *p = *src;
    }
    return dst + count;
}

// FUNCTION: DAO 0x0087B880
C_TreeNode* __thiscall C_0047b880::fn_0047b880(C_TreeNode* node)
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
        return right;
    }

    C_TreeNode* parent = node->field4;
    if (node == parent->field0)
    {
        parent->field0 = right;
        right->field0 = node;
        node->field4 = right;
        return right;
    }

    parent->field8 = right;
    right->field0 = node;
    node->field4 = right;
    return right;
}

// FUNCTION: DAO 0x008FC637
int __cdecl fn_004fc637(unsigned short ch)
{
    if (ch < 0x30)
        return -1;
    if (ch < 0x3A)
        return (int)ch - 0x30;

    if (ch >= 0xFF10)
        goto fullwidth;

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

fullwidth:
    if (ch < 0xFF1A)
        return (int)ch - 0xFF10;
    return -1;
}

// FUNCTION: DAO 0x00A523C0
void __cdecl fn_006523c0(const unsigned int* begin, const unsigned int* end, unsigned int* dst)
{
    unsigned int* d = dst;
    const unsigned int* b = begin;
    if (b == end)
        return;
    do
    {
        if (d != 0)
        {
            d[0] = b[0];
            d[1] = b[1];
        }
        b += 2;
        d += 2;
    } while (b != end);
}
