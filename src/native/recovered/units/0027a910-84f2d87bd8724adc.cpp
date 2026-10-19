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

// FUNCTION: DAO 0x0067A910
C_TreeNode* __thiscall C_0027a910::fn_0027a910(C_TreeNode* node)
{
    C_TreeNode* left = node->field0;
    node->field0 = left->field8;
    if (left->field8->field25 == 0)
        left->field8->field4 = node;
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
    unsigned int n = count;
    unsigned int* p = dst;
    if (count <= 0)
        return dst;
    do
    {
        *p = *src;
        ++p;
    } while (--n > 0);
    return dst + count;
}

// FUNCTION: DAO 0x0087B880
C_TreeNode* __thiscall C_0047b880::fn_0047b880(C_TreeNode* node)
{
    C_TreeNode* right = node->field8;
    node->field8 = right->field0;
    if (right->field0->field25 == 0)
        right->field0->field4 = node;
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
    unsigned int base;

    if (ch < 0x30)
        return -1;
    if (ch < 0x3A)
        return (int)ch - 0x30;

    if (ch >= 0xFF10)
    {
        if (ch < 0xFF1A)
        {
            base = 0xFF10;
            goto digit;
        }
        return -1;
    }

    if (ch < 0x660)
        return -1;
    if (ch < 0x66A)
    {
        base = 0x660;
        goto digit;
    }

    if (ch < 0x6F0)
        return -1;
    if (ch < 0x6FA)
    {
        base = 0x6F0;
        goto digit;
    }

    if (ch < 0x966)
        return -1;
    if (ch < 0x970)
    {
        base = 0x966;
        goto digit;
    }

    if (ch < 0x9E6)
        return -1;
    if (ch < 0x9F0)
    {
        base = 0x9E6;
        goto digit;
    }

    if (ch < 0xA66)
        return -1;
    if (ch < 0xA70)
    {
        base = 0xA66;
        goto digit;
    }

    if (ch < 0xAE6)
        return -1;
    if (ch < 0xAF0)
    {
        base = 0xAE6;
        goto digit;
    }

    if (ch < 0xB66)
        return -1;
    if (ch < 0xB70)
    {
        base = 0xB66;
        goto digit;
    }

    if (ch < 0xC66)
        return -1;
    if (ch < 0xC70)
    {
        base = 0xC66;
        goto digit;
    }

    if (ch < 0xCE6)
        return -1;
    if (ch < 0xCF0)
    {
        base = 0xCE6;
        goto digit;
    }

    if (ch < 0xD66)
        return -1;
    if (ch < 0xD70)
    {
        base = 0xD66;
        goto digit;
    }

    if (ch < 0xE50)
        return -1;
    if (ch < 0xE5A)
    {
        base = 0xE50;
        goto digit;
    }

    if (ch < 0xED0)
        return -1;
    if (ch < 0xEDA)
    {
        base = 0xED0;
        goto digit;
    }

    if (ch < 0xF20)
        return -1;
    if (ch < 0xF2A)
    {
        base = 0xF20;
        goto digit;
    }

    if (ch < 0x1040)
        return -1;
    if (ch < 0x104A)
    {
        base = 0x1040;
        goto digit;
    }

    if (ch < 0x17E0)
        return -1;
    if (ch < 0x17EA)
    {
        base = 0x17E0;
        goto digit;
    }

    if (ch < 0x1810)
        return -1;
    if (ch < 0x181A)
    {
        base = 0x1810;
        goto digit;
    }

    return -1;

digit:
    return (int)ch - (int)base;
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
