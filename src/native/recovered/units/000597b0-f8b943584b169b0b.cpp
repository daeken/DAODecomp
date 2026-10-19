struct Out456990 { unsigned int p0; unsigned int p4; unsigned int p8; unsigned int pC; };
struct Node456990 { unsigned int f0; unsigned short f4; unsigned short pad6; unsigned int f8; };
struct C456990 { unsigned int f0; unsigned int f4; unsigned int f8; unsigned int fc; void fn_00056990(Out456990*, Node456990*); };
struct TreeNode456a80 { TreeNode456a80* left; unsigned int f4; TreeNode456a80* right; unsigned int fC; union { unsigned int ptr[4]; unsigned short words[8]; } data; unsigned int len; unsigned int cap; unsigned int f28; unsigned int f2c; unsigned char f30; unsigned char is_nil; };
struct Key456a80 { unsigned int f0; union { unsigned int ptr[4]; unsigned short words[8]; } data; unsigned int len; unsigned int cap; };
struct C456a80 { unsigned int f0; unsigned int f4; unsigned int fn_00056a80(Key456a80*); };
struct C4597b0 { unsigned int pad[20]; unsigned int f50; unsigned int f54; unsigned int f58; unsigned int f5c; void fn_000597b0(const unsigned int*); };
struct C45dd80 { unsigned int pad[19]; unsigned int f4c; unsigned int f50; unsigned int f54; void fn_0005dd80(); };
struct C45ed60 { unsigned int pad[19]; unsigned int f4c; unsigned int f50; unsigned int f54; unsigned int f58; unsigned int f5c; unsigned int f60; unsigned int f64; unsigned int f68; unsigned int f6c; void fn_0005ed60(const unsigned int*); };
struct C45f4e0 { unsigned int pad[10]; unsigned int f28; unsigned int f2c; int fn_0005f4e0(); };
struct C461f10 { unsigned int f0; unsigned int f4; void fn_00061f10(unsigned int, unsigned int); };
struct Arg4622c0 { unsigned int pad[10]; unsigned int f28; };
struct C4622c0 { unsigned char pad[0x121]; unsigned char f121; unsigned char pad2[2]; unsigned int f124; unsigned int fn_000622c0(Arg4622c0*); };
struct C46c720 { unsigned int pad[16]; unsigned int f40; void fn_0006c720(); };
struct Node4d52b0 { unsigned int f0; unsigned int f4; unsigned int f8; };
struct C4d52b0 { unsigned int pad[3]; unsigned int fc; void fn_000d52b0(unsigned int*, Node4d52b0*); };
struct Node4d52e0 { unsigned int f0; unsigned int f4; unsigned int f8; };
struct C4d52e0 { unsigned int pad[3]; unsigned int fc; unsigned int fn_000d52e0(Node4d52e0*); };
struct Out4d5310 { unsigned int p0; unsigned int p4; unsigned int p8; unsigned int pC; };
struct Node4d5310 { unsigned int f0; unsigned int f4; unsigned int f8; };
struct C4d5310 { unsigned int f0; unsigned int f4; unsigned int f8; unsigned int fc; void fn_000d5310(Out4d5310*, Node4d5310*); };
struct C702e20 { unsigned int f0; unsigned int f4; unsigned int f8; unsigned int fn_00302e20(); };
struct C741f10 { unsigned short f0; unsigned char f2; unsigned char pad3; unsigned int f4; unsigned int f8; unsigned int fc; unsigned int f10; C741f10* fn_00341f10(); };
struct C811f70 { unsigned int pad[4]; unsigned int f10; unsigned int f14; unsigned int f18; unsigned int fn_00411f70(unsigned int); };
struct C811fa0 { unsigned int pad[4]; unsigned int f10; unsigned int f14; unsigned int f18; unsigned int fn_00411fa0(unsigned int); };
// FUNCTION: DAO 0x456990
void __thiscall C456990::fn_00056990(Out456990* out, Node456990* node)
{
    unsigned int esi = 0;
    if (node == 0) {
        out->p0 = 0;
        out->p4 = 0;
        out->p8 = 0;
        out->pC = 0xffffffff;
        return;
    }
    unsigned int eax = *(unsigned int*)(node->f8 + this->fc);
    if (eax == 0xffffffff) {
        out->p0 = 0;
        out->p4 = 0;
        out->p8 = 0;
        out->pC = 0xffffffff;
        return;
    }
    esi = node->f4;
    unsigned int edx = this->f0;
    unsigned int edi = *(unsigned int*)(edx + 0x18);
    unsigned int ecx = this->f4;
    edi += edx;
    edi += eax;
    out->p0 = edi;
    out->pC = esi;
    out->p4 = edx;
    out->p8 = ecx;
}
// FUNCTION: DAO 0x456a80
unsigned int __thiscall C456a80::fn_00056a80(Key456a80* key)
{
    unsigned int header = this->f4;
    TreeNode456a80* node = *(TreeNode456a80**)(header + 4);
    if (node->is_nil) {
        return header;
    }
    unsigned short* keyData;
    if (key->cap >= 8) {
        keyData = (unsigned short*)key->data.ptr[0];
    } else {
        keyData = key->data.words;
    }
    unsigned int keyLen = key->len;
    unsigned int result = header;
    do {
        unsigned short* nodeData;
        if (node->cap >= 8) {
            nodeData = (unsigned short*)node->data.ptr[0];
        } else {
            nodeData = node->data.words;
        }
        unsigned int nodeLen = node->len;
        unsigned int n = nodeLen < keyLen ? nodeLen : keyLen;
        unsigned int i = 0;
        int cmp = 0;
        while (i < n) {
            unsigned short a = nodeData[i];
            unsigned short b = keyData[i];
            if (a != b) {
                cmp = (a < b) ? -1 : 1;
                break;
            }
            ++i;
        }
        if (i == n) {
            if (nodeLen < keyLen) {
                cmp = -1;
            } else if (nodeLen != keyLen) {
                cmp = 1;
            } else {
                cmp = 0;
            }
        }
        if (cmp < 0) {
            node = node->right;
        } else {
            result = (unsigned int)node;
            node = node->left;
        }
    } while (!node->is_nil);
    return result;
}
// FUNCTION: DAO 0x4597b0
void __thiscall C4597b0::fn_000597b0(const unsigned int* src)
{
    this->f50 = src[0];
    this->f54 = src[1];
    this->f58 = src[2];
    this->f5c = src[3];
}
// FUNCTION: DAO 0x45dd80
void __thiscall C45dd80::fn_0005dd80()
{
    this->f4c = 0;
    this->f50 = 0x1b;
    this->f54 = 0;
}
// FUNCTION: DAO 0x45ed60
void __thiscall C45ed60::fn_0005ed60(const unsigned int* src)
{
    this->f4c |= 0x80;
    this->f60 = src[0];
    this->f64 = src[1];
    this->f68 = src[2];
    this->f6c = src[3];
}
// FUNCTION: DAO 0x45f4e0
int __thiscall C45f4e0::fn_0005f4e0()
{
    int edx = (int)this->f28;
    if (edx == 0) {
        return 0;
    }
    int eax = (int)this->f2c;
    return (eax - edx) >> 2;
}
// FUNCTION: DAO 0x461f10
void __thiscall C461f10::fn_00061f10(unsigned int a, unsigned int b)
{
    this->f4 = a;
    this->f0 = b;
}
// FUNCTION: DAO 0x4622c0
unsigned int __thiscall C4622c0::fn_000622c0(Arg4622c0* arg)
{
    if (this->f121 == 0) {
        return 0;
    }
    unsigned int eax = this->f124;
    if (eax == 0) {
        return 0;
    }
    unsigned int ecx = arg->f28;
    if (ecx == 0xffffffff) {
        return 0;
    }
    unsigned int edx = *(unsigned int*)(eax + 0x4a0);
    return edx + ecx * 8;
}
// FUNCTION: DAO 0x46c720
void __thiscall C46c720::fn_0006c720()
{
    unsigned int eax = this->f40;
    unsigned int edx = (eax + 1) & 0x7fff;
    eax &= 0xffff0000;
    edx |= eax;
    this->f40 = edx;
}
// FUNCTION: DAO 0x4d52b0
void __thiscall C4d52b0::fn_000d52b0(unsigned int* out, Node4d52b0* node)
{
    unsigned int edx = node->f4;
    if ((unsigned short)edx == 0xffff) {
        edx = *(unsigned int*)(node->f8 + this->fc);
    }
    *out = edx;
}
// FUNCTION: DAO 0x4d52e0
unsigned int __thiscall C4d52e0::fn_000d52e0(Node4d52e0* node)
{
    unsigned short edx = (unsigned short)node->f4;
    if (edx == 0xffff) {
        return *(unsigned int*)(node->f8 + this->fc + 4);
    }
    return *(unsigned int*)(node->f8 + this->fc);
}
// FUNCTION: DAO 0x4d5310
void __thiscall C4d5310::fn_000d5310(Out4d5310* out, Node4d5310* node)
{
    if (node == 0) {
        out->pC = 0;
        out->p4 = 0;
        out->p0 = 0;
        return;
    }
    unsigned int edx = this->f0;
    unsigned int ebp = node->f4 & 0xffff;
    unsigned int edi = node->f8;
    unsigned int esi = this->f4;
    unsigned int ecx = this->fc;
    out->p4 = esi;
    ecx += edi;
    esi += edx;
    out->p8 = ebp;
    out->p0 = edx;
    out->pC = ecx;
    if (ecx > esi) {
        out->pC = 0;
        out->p4 = 0;
        out->p0 = 0;
        return;
    }
    if (ecx > edx) {
        return;
    }
    out->pC = 0;
    out->p4 = 0;
    out->p0 = 0;
}
// FUNCTION: DAO 0x702e20
unsigned int __thiscall C702e20::fn_00302e20()
{
    unsigned int eax = this->f0;
    unsigned int edx = *(unsigned int*)(eax + 0x18);
    edx += this->f8;
    return *(unsigned int*)(edx + eax);
}
// FUNCTION: DAO 0x741f10
C741f10* __thiscall C741f10::fn_00341f10()
{
    this->f0 = 0;
    this->f2 = 0;
    this->f4 = 0;
    this->f8 = 1;
    this->fc = 0;
    this->f10 = 0;
    return this;
}
// FUNCTION: DAO 0x811f70
unsigned int __thiscall C811f70::fn_00411f70(unsigned int idx)
{
    unsigned int eax = *(unsigned int*)(this->f18 + idx * 28);
    if (eax == 0xffffffff) {
        return 0;
    }
    return this->f10 + eax + 4;
}
// FUNCTION: DAO 0x811fa0
unsigned int __thiscall C811fa0::fn_00411fa0(unsigned int idx)
{
    unsigned int eax = *(unsigned int*)(this->f18 + idx * 28 + 4);
    if (eax == 0xffffffff) {
        return 0;
    }
    return this->f10 + eax + 4;
}
