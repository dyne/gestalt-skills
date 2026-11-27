#include <stdint.h>

uint32_t count_byte(const uint8_t *data, uint32_t length, uint32_t needle) {
    uint32_t matches = 0;
    for (uint32_t i = 0; i < length; ++i) {
        if (data[i] == needle) ++matches;
    }
    return matches;
}

#ifdef COUNT_COMMAND
#include <stdio.h>
#include <inttypes.h>

// CLI flavor: count newline bytes in stdin, including binary input.
int main(void) {
    uint8_t block[4096];
    uint64_t total = 0;
    size_t used;
    while ((used = fread(block, 1, sizeof block, stdin)) > 0) {
        total += count_byte(block, (uint32_t)used, 10);
    }
    if (ferror(stdin)) return 1;
    return printf("%" PRIu64 "\n", total) < 0;
}
#endif
