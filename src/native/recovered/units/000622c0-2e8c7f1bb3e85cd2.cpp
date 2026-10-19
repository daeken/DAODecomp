struct Out456990 { unsigned int p0; unsigned int p4; unsigned int p8; unsigned int pC; };
struct Node456990 { unsigned int f0; unsigned short f4; unsigned short pad6; unsigned int f8; };
struct C456990 { unsigned int f0; unsigned int f4; unsigned int f8; unsigned int fc; void fn_00056990(Out456990*, Node456990*); };
struct Data456a80 { unsigned int ptr[4]; unsigned short words[8]; };
struct Key456a80 { unsigned int f0; Data456a80 data; unsigned int len; unsigned int cap; };
struct TreeNode456a80 { TreeNode456a80* left; unsigned int f4; TreeNode456a80* right; unsigned int fC; Data456a80 data; unsigned int len; unsigned int cap; unsigned int f28; unsigned int f2c; unsigned char f30; unsigned char is_nil; };
struct C456a80 { unsigned int f0; unsigned int f4; TreeNode456a80* fn_00056a80(Key456a80*); };
struct C45ed60 { unsigned int pad[19]; unsigned int f4c; unsigned int f50; unsigned int f54; unsigned int f58; unsigned int f5c; unsigned int f60; unsigned int f64; unsigned int f68; unsigned int f6c; void fn_0005ed60(const unsigned int*); };
struct Arg4622c0 { unsigned int pad[10]; unsigned int f28; };
struct C4622c0 { unsigned char pad[0x121]; unsigned char f121; unsigned char pad2[2]; unsigned int f124; unsigned int fn_000622c0(Arg4622c0*); };
struct Node4d52b0 { unsigned int f0; unsigned int f4; unsigned int f8; };
struct C4d52b0 { unsigned int pad[3]; unsigned int fc; void fn_000d52b0(unsigned int*, Node4d52b0*); };
struct Node4d52e0 { unsigned int f0; unsigned int f4; unsigned int f8; };
struct C4d52e0 { unsigned int pad[3]; unsigned int fc; unsigned int fn_000d52e0(Node4d52e0*); };
struct Out4d5310 { unsigned int p0; unsigned int p4; unsigned int p8; unsigned int pC; };
struct Node4d5310 { unsigned int f0; unsigned int f4; unsigned int f8; };
struct C4d5310 { unsigned int f0; unsigned int f4; unsigned int f8; unsigned int fc; void fn_000d5310(Out4d5310*, Node4d5310*); };
// FUNCTION: DAO 0x456990
void __thiscall C456990::fn_00056990(Out456990* out, Node456990* node)
{
    unsigned int esi = 0;
    unsigned int edx = (unsigned int)node;
    if (edx == 0) goto null_return;
    {
        unsigned int eax = *(unsigned int*)(edx + 8);
        eax = *(unsigned int*)(eax + this->fc);
        if (eax == 0xffffffffu) goto null_return;
        esi = (unsigned int)*(unsigned short*)(edx + 4);
        edx = this->f0;
        unsigned int edi = *(unsigned int*)(edx + 0x18);
        unsigned int ecx = this->f4;
        edi += edx;
        edi += eax;
        out->p0 = edi;
        out->pC = esi;
        out->p4 = edx;
        out->p8 = ecx;
        return;
    }
null_return:
    out->p0 = esi;
    out->p4 = esi;
    out->p8 = esi;
    out->pC = 0xffffffffu;
}
// FUNCTION: DAO 0x456a80
TreeNode456a80* __thiscall C456a80::fn_00056a80(Key456a80* key)
{
    unsigned int header = this->f4;
    TreeNode456a80* node = *(TreeNode456a80**)(header + 4);
    if (node->is_nil != 0) return (TreeNode456a80*)header;
    unsigned int keyCap = key->cap;
    unsigned int keyLen = key->len;
    unsigned int* keyDataBase = (unsigned int*)((char*)key + 4);
    do {
        unsigned short* keyData;
        if (keyCap >= 8) keyData = (unsigned short*)*keyDataBase;
        else keyData = (unsigned short*)keyDataBase;
        unsigned int nodeLen = node->len;
        unsigned short* nodeData;
        if (node->cap >= 8) nodeData = (unsigned short*)node->data.ptr[0];
        else nodeData = (unsigned short*)node->data.words;
        unsigned int n = nodeLen < keyLen ? nodeLen : keyLen;
        unsigned int i = n;
        int cmp = 0;
        unsigned short* nd = nodeData;
        unsigned short* kd = keyData;
        while (i != 0) {
            unsigned short a = *nd;
            unsigned short b = *kd;
            if (a != b) {
                cmp = (a < b) ? -1 : 1;
                break;
            }
            ++nd;
            ++kd;
            --i;
        }
        if (i == 0 && cmp == 0) {
            if (nodeLen < keyLen) cmp = -1;
            else if (nodeLen != keyLen) cmp = 1;
        }
        if (cmp < 0) {
            node = node->right;
        } else {
            header = (unsigned int)node;
            node = node->left;
        }
    } while (node->is_nil == 0);
    return (TreeNode456a80*)header;
}
// FUNCTION: DAO 0x45ed60
void __thiscall C45ed60::fn_0005ed60(const unsigned int* src)
{
    this->f4c |= 0x80u;
    this->f60 = src[0];
    this->f64 = src[1];
    this->f68 = src[2];
    this->f6c = src[3];
}
// FUNCTION: DAO 0x4622c0
unsigned int __thiscall C4622c0::fn_000622c0(Arg4622c0* arg)
{
    if (this->f121 != 0) {
        unsigned int eax = this->f124;
        unsigned int ecx = arg->f28;
        if (eax != 0) {
            if (ecx != 0xffffffffu) {
                unsigned int edx = *(unsigned int*)(eax + 0x4a0);
                return edx + ecx * 8;
            }
        }
    }
    return 0;
}
// FUNCTION: DAO 0x4d52b0
void __thiscall C4d52b0::fn_000d52b0(unsigned int* out, Node4d52b0* node)
{
    unsigned int eax = (unsigned int)node;
    unsigned int edx = *(unsigned int*)(eax + 4);
    unsigned int esi = edx & 0xffffu;
    if (esi == 0xffffu) {
        eax = *(unsigned int*)(eax + 8);
        edx = *(unsigned int*)(eax + this->fc);
    }
    *out = edx;
}
// FUNCTION: DAO 0x4d52e0
unsigned int __thiscall C4d52e0::fn_000d52e0(Node4d52e0* node)
{
    unsigned int eax = (unsigned int)node;
    unsigned int edx = (unsigned int)*(unsigned short*)(eax + 4);
    if (edx == 0xffffu) {
        eax = *(unsigned int*)(eax + 8);
        return *(unsigned int*)(eax + this->fc + 4);
    }
    edx = *(unsigned int*)(eax + 8);
    eax = this->fc;
    return *(unsigned int*)(edx + eax);
}
// FUNCTION: DAO 0x4d5310
void __thiscall C4d5310::fn_000d5310(Out4d5310* out, Node4d5310* node)
{
    unsigned int* eax = (unsigned int*)out;
    unsigned int edi = (unsigned int)node;
    unsigned int ebx = 0;
    if (edi == ebx) goto zero_out;
    {
        unsigned int edx = this->f0;
        unsigned int ebp = (unsigned int)*(unsigned short*)(edi + 4);
        edi = *(unsigned int*)(edi + 8);
        unsigned int esi = this->f4;
        unsigned int ecx = this->fc;
        eax[1] = esi;
        ecx += edi;
        esi += edx;
        eax[2] = ebp;
        eax[0] = edx;
        eax[3] = ecx;
        if (ecx > esi) goto zero_out;
        if (ecx > edx) return;
    }
zero_out:
    eax[3] = ebx;
    eax[1] = ebx;
    eax[0] = ebx;
}
