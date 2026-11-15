#pragma once
#ifdef _WIN32
#ifndef NOMINMAX
#define NOMINMAX
#endif
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
namespace recomp_generated {
struct NativeErrorContext {DWORD value=::GetLastError();};
inline thread_local NativeErrorContext native_error_context;
}
#endif
