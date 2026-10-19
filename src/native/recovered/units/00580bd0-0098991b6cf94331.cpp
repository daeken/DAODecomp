struct KeyObj1 { char pad[0x10]; unsigned int hash; };
struct Elem1 { int next; KeyObj1* key; int extra; };
struct Table1 { int f0; unsigned int mask; Elem1 elems[1]; };
class C1 { public: Table1* table; int fn_0057c0a0(void** keyPtr, unsigned int start); };

struct Elem2 { int state; char pad[28]; };
struct Table2 { int f0; unsigned int count; Elem2 elems[1]; };
struct Out2 { void* owner; unsigned int index; };
class C2 { public: Table2* table; Out2* fn_0057df10(Out2* out); };

struct KeyObj3 { char pad[0x10]; unsigned int hash; };
struct Elem3 { int next; KeyObj3* key; };
struct Table3 { int count; unsigned int mask; Elem3 elems[1]; };
class C3 { public: Table3* table; void fn_0057ffd0(void** keyPtr); };

class C4 { public: void* p; int f4; unsigned char b; void fn_00580bd0(void* p, unsigned char b); };

class C5 { public: unsigned int value; bool fn_00580cf0(C5* other) const; };

struct C6Control { char pad[8]; unsigned int begin; unsigned int end; unsigned int* blocks; unsigned int blockCount; };
class C6 { public: char pad[0x18]; C6Control* ctrl; char pad2[4]; unsigned int pos; void* fn_00583430(unsigned int index) const; };

struct KeyStr7 { char* str; char pad[0x0c]; unsigned int hash; };
struct Elem7 { int next; KeyStr7* key; char extra[16]; };
struct Table7 { int f0; unsigned int mask; Elem7 elems[1]; };
class C7 { public: Table7* table; int fn_00584160(void** strPtr, unsigned int start); };

struct StrHolder { char pad[0x0c]; char* str; };
class C8 { public: char pad[0x40]; StrHolder* a; StrHolder* b; int f48; int f4c; int f50; unsigned char f54; bool fn_00584db0(C8* other) const; };

class C9 { public: char pad[0x28]; unsigned char f28; unsigned char pad2; unsigned char f2a; bool fn_00584e80() const; };

class C10 { public: unsigned short* data; unsigned int count; unsigned short* fn_00584fc0(unsigned int index) const; };

// FUNCTION: DAO 0x97c0a0
int C1::fn_0057c0a0(void** keyPtr, unsigned int start) {
  Table1* t = table;
  Elem1* e = &t->elems[start];
  if (e->next == -2) return -1;
  if ((e->key->hash & t->mask) != start) return -1;
  unsigned int cur = start;
  for (;;) {
    if ((e->key->hash & t->mask) == start && e->key == (KeyObj1*)*keyPtr) return (int)cur;
    int n = e->next;
    if (n == -1) return -1;
    cur = (unsigned int)n;
    e = &t->elems[cur];
  }
}

// FUNCTION: DAO 0x97df10
Out2* C2::fn_0057df10(Out2* out) {
  Table2* t = table;
  if (!t) {
    out->owner = 0;
    out->index = 0;
    return out;
  }
  unsigned int count = t->count;
  unsigned int i = 0;
  Elem2* e = t->elems;
  while (i <= count) {
    if (e->state != -2) break;
    ++i;
    e = (Elem2*)((char*)e + 0x20);
  }
  out->index = i;
  out->owner = this;
  return out;
}

// FUNCTION: DAO 0x97ffd0
void C3::fn_0057ffd0(void** keyPtr) {
  Table3* t = table;
  if (!t) return;
  KeyObj3* key = (KeyObj3*)*keyPtr;
  unsigned int idx = key->hash & t->mask;
  Elem3* e = &t->elems[idx];
  if (e->next == -2) return;
  if ((e->key->hash & t->mask) != idx) return;
  int prev = -1;
  unsigned int cur = idx;
  for (;;) {
    if ((e->key->hash & t->mask) == idx && e->key == key) {
      int next = e->next;
      if (prev == -1) {
        if (next == -1) {
          e->next = -2;
        } else {
          Elem3* n = &t->elems[next];
          e->next = n->next;
          e->key = n->key;
          e = n;
          e->next = -2;
        }
      } else {
        t->elems[prev].next = next;
        e->next = -2;
      }
      t->count--;
      return;
    }
    prev = (int)cur;
    int next = e->next;
    if (next == -1) return;
    cur = (unsigned int)next;
    e = &t->elems[cur];
  }
}

// FUNCTION: DAO 0x980bd0
void C4::fn_00580bd0(void* p, unsigned char b) {
  this->b = b;
  this->p = p;
  this->f4 = 0;
}

// FUNCTION: DAO 0x980cf0
bool C5::fn_00580cf0(C5* other) const {
  return value != other->value;
}

// FUNCTION: DAO 0x983430
void* C6::fn_00583430(unsigned int index) const {
  unsigned int edx = pos - index;
  C6Control* c = ctrl;
  int esi = ((int)c->begin - (int)c->end) >> 4;
  int edi = (int)c->blockCount - 1;
  esi += edi << 5;
  if (edx > (unsigned int)esi) return 0;
  unsigned int eax = edx >> 5;
  unsigned int off = (edx & 0x1f) << 4;
  return (void*)(c->blocks[eax] + off);
}

// FUNCTION: DAO 0x984160
int C7::fn_00584160(void** strPtr, unsigned int start) {
  Table7* t = table;
  Elem7* e = &t->elems[start];
  if (e->next == -2) return -1;
  if ((e->key->hash & t->mask) != start) return -1;
  unsigned int cur = start;
  for (;;) {
    if ((e->key->hash & t->mask) == start) {
      const char* s1 = e->key->str;
      const char* s2 = (const char*)*strPtr;
      while (*s1 && *s1 == *s2) { ++s1; ++s2; }
      if (*s1 == *s2) return (int)cur;
    }
    int n = e->next;
    if (n == -1) return -1;
    cur = (unsigned int)n;
    e = &t->elems[cur];
  }
}

// FUNCTION: DAO 0x984db0
bool C8::fn_00584db0(C8* other) const {
  const char* s1 = a->str;
  const char* s2 = other->a->str;
  while (*s1 && *s1 == *s2) { ++s1; ++s2; }
  if (*s1 != *s2) return false;
  s1 = b->str;
  s2 = other->b->str;
  while (*s1 && *s1 == *s2) { ++s1; ++s2; }
  if (*s1 != *s2) return false;
  if (f48 != other->f48) return false;
  if (f4c != other->f4c) return false;
  if (f50 != other->f50) return false;
  if (f54 != other->f54) return false;
  return true;
}

// FUNCTION: DAO 0x984e80
bool C9::fn_00584e80() const {
  if ((f2a >> 7) & 1) {
    if (f28 != 0) return true;
  }
  return false;
}

// FUNCTION: DAO 0x984fc0
unsigned short* C10::fn_00584fc0(unsigned int index) const {
  if (data && index < count) return data + index;
  return 0;
}
