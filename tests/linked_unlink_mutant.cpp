#include "../validation/linked_unlink_mutant.hpp"
#include <cstdint>
int main() {
    constexpr std::uint32_t list = 71;
    constexpr std::uint32_t measured_predecessor = 0x02000083u;
    const auto corrupted = dao::linked_unlink_mutant_ecx(list, measured_predecessor);
    return corrupted == 0x02000047u && corrupted != measured_predecessor ? 0 : 1;
}
