#include <cstdint>
#include <iostream>
#include <limits>
#include "dao/guest.hpp"

struct Counter {
    std::uint32_t value;
    std::uint32_t saturations;
};

std::uint32_t bump(Counter& counter, std::uint32_t delta) {
    const auto previous = counter.value;
    const auto sum = static_cast<std::uint64_t>(previous) + delta;
    constexpr auto maximum = std::numeric_limits<std::uint32_t>::max();
#ifdef DAO_SYNTHETIC_MUTANT
    // Deliberately wrong at the exact upper boundary. The harness must reject it.
    const bool overflow = sum >= maximum;
#else
    const bool overflow = sum > maximum;
#endif
    counter.value = overflow ? maximum : static_cast<std::uint32_t>(sum);
    if (overflow) {
        counter.saturations += std::uint32_t{1};
    }
    return previous;
}

int main() {
    std::uint64_t value{}, saturations{}, delta{};
    constexpr auto maximum = std::numeric_limits<std::uint32_t>::max();
    if (!(std::cin >> value >> saturations >> delta) || value > maximum ||
        saturations > maximum || delta > maximum) {
        return 2;
    }
    Counter counter{static_cast<std::uint32_t>(value), static_cast<std::uint32_t>(saturations)};
    const auto result = bump(counter, static_cast<std::uint32_t>(delta));
    std::cout << result << ' ' << counter.value << ' ' << counter.saturations << '\n';
}

