###############################################
# Libraries
###############################################
import sys
import os
import socket
import time
import struct
import select


###############################################
# Global Constants & Variables
###############################################

ICMP_ECHO_REQUEST = 8
TIMEOUT = 5
MAX_HOPS = 30


###############################################
# Usage()
###############################################

def usage():
    print("Usage:")
    print("python tracert.py host")
    print()
    print("e.g. python tracert.py news.bbc.co.uk")
    print("e.g. python tracert.py 212.58.249.145")
    os._exit(0)


###############################################
# Checksum Calculation (https://tools.ietf.org/html/rfc1071)
###############################################

def calc_checksum(header):
    # Initialise checksum and overflow
    checksum = 0
    overflow = 0

    # For every word (16-bits)
    for i in range(0, len(header), 2):
        word = header[i] + (header[i+1] << 8)

        # Add the current word to the checksum
        checksum = checksum + word
        # Separate the overflow
        overflow = checksum >> 16
        # While there is an overflow
        while overflow > 0:
            # Remove the overflow bits
            checksum = checksum & 0xFFFF
            # Add the overflow bits
            checksum = checksum + overflow
            # Calculate the overflow again
            overflow = checksum >> 16

    # There's always a chance that after calculating the checksum
    # across the header, ther is *still* an overflow, so need to
    # check for that
    overflow = checksum >> 16
    while overflow > 0:
        checksum = checksum & 0xFFFF
        checksum = checksum + overflow
        overflow = checksum >> 16

    # Ones-compliment and return
    checksum = ~checksum
    checksum = checksum & 0xFFFF

    return checksum


###############################################
# Send ICMP Ping Packet
###############################################

def ping(dest_addr, icmp_socket, time_to_live, id):
    # Set initial checksum to zero and create the array
    initial_checksum = 0
    initial_header = struct.pack("bbHHh",
                                 ICMP_ECHO_REQUEST,
                                 0,
                                 initial_checksum,
                                 id,
                                 1)

    # Calculate the actual checksum and the actual array
    calculated_checksum = calc_checksum(initial_header)
    header = struct.pack("bbHHh",
                         ICMP_ECHO_REQUEST,
                         0,
                         calculated_checksum,
                         id,
                         1)

    # Set the TTL field in the IP section of packet
    icmp_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, time_to_live)

    # Send the packet
    icmp_socket.sendto(header, (dest_addr, 1))

    # Get the time so we can calculate time for response
    start_time = time.time()
    # Wait for response on socket, or timeout after TIMEOUT seconds
    socketResponseReady = select.select([icmp_socket], [], [], TIMEOUT)
    if socketResponseReady[0] == []:
        print('{0}\t{1} ms\t???.???.???.???\t(Timeout)'.
              format(time_to_live,
                     int((time.time() - start_time) * 1000.00)))
        return False

    # Read the data from the socket
    recv_packet, addr = icmp_socket.recvfrom(1024)
    hostname = ''
    try:
        # Try and convert the IP to a hostname
        host_details = socket.gethostbyaddr(addr[0])
        if len(host_details) > 0:
            hostname = host_details[0]
    except:
        # if we can't find the hostname, just display 'unknown'
        hostname = 'unknown'

    # Display the time taken to get a response, the ip, and the hostname
    print('{0}\t{1} ms\t{2}\t{3}'.
          format(time_to_live,
                 int((time.time() - start_time) * 1000.00),
                 addr[0],
                 hostname))

    # If the packet we received back is from the final-destinaton host,
    # then our work is done!
    if addr[0] == dest_addr:
        return True

    # ..in all other cases, return False
    return False


###############################################
# Main()
###############################################

def main():
    # If we don't have a paramter, display usage
    if (len(sys.argv) != 2):
        usage()

    # Get the hostname/IP we wish to Tracert
    dest_host = sys.argv[1]
    dest_addr = socket.gethostbyname(dest_host)

    print("Tracert to {0} ({1}) over maximum of {2} hops".
          format(dest_addr,
                 dest_host,
                 MAX_HOPS))

    # Set the initial id and time_to_live values
    time_to_live = 1
    id = 1
    while(time_to_live < MAX_HOPS):
        # Create the ICMP protocol
        icmp_proto = socket.getprotobyname("icmp")
        try:
            # Create the socket
            icmp_socket = socket.socket(socket.AF_INET,
                                        socket.SOCK_RAW,
                                        icmp_proto)
        except socket.error as exception:
            # On error, display it and exit
            print("Error " + exception)
            os._exit(1)

        # Ping the host, and if function returns true, exit, since complete
        if(ping(dest_addr, icmp_socket, time_to_live, id)):
            icmp_socket.close()
            break

        # ..if ping() returned false, then increase the time_to_live and
        # id fields, and do it all over again
        time_to_live += 1
        id += 1
        icmp_socket.close()

    # Return to OS
    os._exit(0)


###############################################
# Startup
###############################################

if __name__ == "__main__":
    main()
