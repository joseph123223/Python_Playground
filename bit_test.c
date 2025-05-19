#include <stdio.h>
#include <stddef.h>

struct test {
    unsigned scan_id: 9;
    signed hangle1: 9;
    signed hangle2: 10;
    signed hangle3: 11;
    signed vangle1: 8;
    signed vangle2: 9;
    signed vangle3: 9;
    unsigned roi: 2;
    unsigned f: 3;
    unsigned reserved: 2;
};

int main() {
    printf("Size of struct test: %lu bytes\n", sizeof(struct test));
    printf("Offset of scan_id: %lu\n", offsetof(struct test, scan_id));
    printf("Offset of hangle1: %lu\n", offsetof(struct test, hangle1));
    printf("Offset of hangle2: %lu\n", offsetof(struct test, hangle2));
    printf("Offset of hangle3: %lu\n", offsetof(struct test, hangle3));
    printf("Offset of vangle1: %lu\n", offsetof(struct test, vangle1));
    return 0;
}
