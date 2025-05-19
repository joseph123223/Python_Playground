%%writefile offsetof_test.c
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
    printf("Offset of scan_id: %lu bytes\n", offsetof(struct test, scan_id));
    printf("Offset of hangle1: %lu bytes\n", offsetof(struct test, hangle1));
    printf("Offset of hangle2: %lu bytes\n", offsetof(struct test, hangle2));
    printf("Offset of hangle3: %lu bytes\n", offsetof(struct test, hangle3));
    printf("Offset of vangle1: %lu bytes\n", offsetof(struct test, vangle1));
    printf("Offset of vangle2: %lu bytes\n", offsetof(struct test, vangle2));
    printf("Offset of vangle3: %lu bytes\n", offsetof(struct test, vangle3));
    printf("Offset of roi: %lu bytes\n", offsetof(struct test, roi));
    printf("Offset of f: %lu bytes\n", offsetof(struct test, f));
    printf("Offset of reserved: %lu bytes\n", offsetof(struct test, reserved));
    return 0;
}
