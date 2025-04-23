
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

void *memset(void *s, int c, size_t n) {
    unsigned char *p = s;
    while(n--) *p++ = (unsigned char)c;
    return s;
}

void *memcpy(void *dest, const void *src, size_t n) {
    char *d = dest;
    const char *s = src;
    while (n--) *d++ = *s++;
    return dest;
}

int vprintf(const char *fmt, va_list args) {
    return 0; // Dummy
}
