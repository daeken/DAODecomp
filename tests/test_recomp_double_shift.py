"""Portable double-shift unknownness and fault-boundary regressions.

Native instruction agreement is recorded separately by experiments/double_shift.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from tools import recomp


class DoubleShiftTests(unittest.TestCase):
    def test_unknown_zero_count_aliases_and_fault_commit(self):
        if not shutil.which('clang++'):
            self.skipTest('requires Clang')
        upstream = recomp.ROOT.parent / 'SharpRetro/Decompiler'
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary)
            (out / 'runtime.hpp').write_bytes((upstream / 'CppRuntime.hpp').read_bytes())
            driver = out / 'control.cpp'
            driver.write_text(r'''
#include "image_memory.hpp"
#include "DoubleShiftRuntime.hpp"
using namespace sharp_retro;
struct Observed : recomp_generated::ImageMemory {
 unsigned loads=0,checks=0,writes=0;bool reject=false;
 Scalar32 load_scalar16(std::uint64_t a)override{++loads;return ImageMemory::load_scalar16(a);}
 Scalar32 load_scalar32(std::uint64_t a)override{++loads;return ImageMemory::load_scalar32(a);}
 void validate_store(std::uint64_t a,unsigned n)override{++checks;if(reject)throw std::runtime_error("write fault");ImageMemory::validate_store(a,n);}
 void store_scalar16(std::uint64_t a,Scalar32 v)override{++writes;ImageMemory::store_scalar16(a,v);}
 void store_scalar32(std::uint64_t a,Scalar32 v)override{++writes;ImageMemory::store_scalar32(a,v);}
};
int main(){
 Observed memory;memory.map_bytes("data",0x8000,4096,true,true);memory.seal();
 for(bool word:{false,true})for(bool right:{false,true}){
  unsigned d=(word?2u:0u)|(right?1u:0u)|(2u<<8);
  State s;invalidate_gprs(s,5);s.defined_flags=0;s.gpr[0]=0x12345678;s.gpr[2]=0xabcdef12;auto before=s;
  double_shift32(s,memory,d,0,32);
  if(std::memcmp(s.gpr,before.gpr,sizeof(s.gpr))||s.defined_gpr!=before.defined_gpr||s.flags!=before.flags||s.defined_flags)return 1;
  memory.store_unknown(0x8040,0xdeadbeef,word?16:32);auto value=word?memory.load_scalar16(0x8040):memory.load_scalar32(0x8040);
  memory.loads=memory.checks=memory.writes=0;
  double_shift32(s,memory,d|4u,0x8040,0);
  if(memory.loads!=1||memory.checks!=1||memory.writes!=1||s.flags!=before.flags||s.defined_flags)return 2;
  auto after=word?memory.load_scalar16(0x8040):memory.load_scalar32(0x8040);
  if(value.value!=after.value||value.known!=after.known||value.origins!=after.origins)return 3;
  memory.reject=true;memory.loads=memory.checks=memory.writes=0;bool fault=false;
  try{double_shift32(s,memory,d|4u,0x8040,0);}catch(const std::runtime_error&){fault=true;}
  if(!fault||memory.loads!=1||memory.checks!=1||memory.writes||s.flags!=before.flags||s.defined_flags)return 4;
  memory.reject=false;memory.store(0x8040,0x81234567,word?16:32);s=State{};s.gpr[2]=0xabcdef12;s.flags=0x602;before=s;memory.reject=true;fault=false;
  try{double_shift32(s,memory,d|4u,0x8040,1);}catch(const std::runtime_error&){fault=true;}
  if(!fault||s.flags!=before.flags||s.defined_flags!=before.defined_flags||std::memcmp(s.gpr,before.gpr,sizeof(s.gpr)))return 5;
  memory.reject=false;
 }
 for(bool right:{false,true}){
  State s;s.gpr[0]=0xaabb8001;s.flags=0x602;
  double_shift32(s,memory,(right?1u:0u)|2u,0,1); // self alias, word destination
  if(s.gpr[0]!=(right?0xaabbc000u:0xaabb0003u)||(s.defined_flags&0x8d5u)!=0x8c5u||(s.flags&0x400u)!=0x400u)return 6;
  s=State{};s.gpr[0]=0x12345678;s.gpr[2]=0x87654321;
  double_shift32<32>(s,memory,2u<<8,0,99);if(s.gpr[0]!=0x12345678)return 7;
  double_shift32(s,memory,(right?1u:0u)|(2u<<8),0,4);
  if(s.gpr[0]!=(right?0x11234567u:0x23456788u)||(s.defined_flags&0x8d5u)!=0xc5u)return 8;
 }
}
''')
            executable = out / 'control'
            built = subprocess.run(['clang++', '-std=c++20', '-O2', '-fsanitize=address,undefined',
                '-fno-sanitize-recover=all', '-I', str(out), '-I', str(upstream),
                '-I', str(recomp.RUNTIME), str(driver), '-o', str(executable)],
                capture_output=True, text=True, timeout=90)
            self.assertEqual(built.returncode, 0, built.stderr)
            result = subprocess.run([str(executable)], capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
