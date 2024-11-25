#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

#include "rwreg.h"

#define BOARD_ID_ADDR 0x00000008

int main(int argc, char *argv[])
{
    rwreg_init("FPGA1", 0);
    uint32_t rval = getReg(BOARD_ID_ADDR);
    printf("%x", rval);
    return 0;
}
