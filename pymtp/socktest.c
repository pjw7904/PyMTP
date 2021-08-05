// Test program to see if the GENI Ubuntu images on the VMs are forwarding dat 
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <linux/if_packet.h>
#include <net/ethernet.h>
#include <net/if.h>
#include <netinet/in.h>
#include <netinet/ether.h>

#define CONTROL_PORT "eth0"

int main(void) 
{   
    struct sockaddr_ll src_addr;
    socklen_t addr_len = sizeof(src_addr);
    uint8_t recvBuffer[1024];
    char* srcbuf;
    char* dstbuf;

    // Create socket, same exact socket options as the Python code
    int s = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_IP));

    if(s == -1)
	{
	    perror("Failed to create socket");
		exit(1);
	}

    printf("Listening for IPv4 traffic...\n");

    while(1)
    {
        // Receive data
        int recvLength = recvfrom(s, recvBuffer, 1024, 0, (struct sockaddr*) &src_addr, &addr_len);

        if(recvLength > 0)
        {
            char recvOnEtherPort[5];
            if_indextoname(src_addr.sll_ifindex, recvOnEtherPort);

            if ((strcmp(recvOnEtherPort, CONTROL_PORT)) == 0)
            {
                continue;
            }

            struct ether_header *ethHdr;
            ethHdr = (struct ether_header *) recvBuffer;

            printf("\n\n***********************Ethernet src + dst*************************\n");
            printf("Ethernet Header\n");
            printf("   |-Source Address: %s\n", ether_ntoa((struct ether_addr *)&ethHdr->ether_shost));
            printf("\n###########################################################");

        }
    }

    return 0;
}