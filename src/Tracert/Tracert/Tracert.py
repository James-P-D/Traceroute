#host_name = socket.gethostbyaddr("1.2.3.4")
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
    os._exit(0)

###############################################
# Checksum Calculation (https://tools.ietf.org/html/rfc1071)
###############################################

def checksum(source_string):
    """
    I'm not too confident that this is right but testing seems
    to suggest that it gives the same answers as in_cksum in ping.c
    """
    sum = 0
    countTo = (len(source_string)/2)*2
    count = 0
    while count<countTo:
        thisVal = source_string[count + 1] * 256
        thisVal += source_string[count]
        sum = sum + thisVal
        sum = sum & 0xffffffff # Necessary?
        count = count + 2

    if countTo<len(source_string):
        sum = sum + ord(source_string[len(source_string) - 1])
        sum = sum & 0xffffffff # Necessary?

    sum = (sum >> 16)  +  (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff

    # Swap bytes. Bugger me if I know why.
    answer = answer >> 8 | (answer << 8 & 0xff00)

    return answer

###############################################
# Send ICMP Ping Packet
###############################################

def ping(dest_addr, my_socket, time_to_live, id):
    # Set the TTL field in the IP section of packet
    my_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, time_to_live)

    initial_checksum = 0
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, initial_checksum, id, 1)        
    calculated_checksum = checksum(header)
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(calculated_checksum), id, 1)

    my_socket.sendto(header, (dest_addr, 1))
    start_time = time.time()
    whatReady = select.select([my_socket], [], [], TIMEOUT)
    if whatReady[0] == []:
        print('{0}\t{1} ms\t???.???.???.???\t(Timeout)'.format(time_to_live, int((time.time() - start_time) * 1000.00)))
        return False

    recvPacket, addr = my_socket.recvfrom(1024)    
    hostname = ''
    try:
        host_details = socket.gethostbyaddr(addr[0])
        if len(host_details) > 0:
            hostname = host_details[0]
    except:
        hostname = 'unknown'
    print('{0}\t{1} ms\t{2}\t{3}'.format(time_to_live, int((time.time() - start_time) * 1000.00), addr[0], hostname))
    
    if addr[0] == dest_addr:
        return True

###############################################
# Main() 
###############################################

def main():
    # If we don't have a paramter, display usage
    if (len(sys.argv) != 2):
        usage()

    # Get the hostname/IP we wish to Tracert
    host = sys.argv[1]        
    dest_addr = socket.gethostbyname(host)

    print("Tracert to {0} over maximum of {1} hops".format(dest_addr, MAX_HOPS))
    
    time_to_live = 1
    id = 1
    while(time_to_live < MAX_HOPS):
        # Create the ICMP protocol
        icmp_proto = socket.getprotobyname("icmp")
        try:
            # Create the socket
            my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp_proto)
        except socket.error as exception:
            print("Error " + exception)
            os._exit(1)
                
        if(ping(dest_addr, my_socket, time_to_live, id)):
            my_socket.close()
            break

        time_to_live += 1
        id += 1
        my_socket.close()

    # Return to OS
    os._exit(0)

###############################################
# Startup
###############################################

if __name__ == "__main__":
    main()

