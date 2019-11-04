#host_name = socket.gethostbyaddr("1.2.3.4")
import sys
import os
import socket
import time
import struct
import select

def usage():
	print("Usage:")
	print("python tracert.py host")
	os._exit(0)

def ping(dest_addr, my_socket, time_to_live, id):
	# Set the TTL field in the IP section of packet
	my_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, time_to_live)

	my_checksum = 0
	header = struct.pack("bbHHh", 8, 0, my_checksum, id, 1)
	bytesInDouble = struct.calcsize("d")
	data = (192 - bytesInDouble) * "Q"
	#data = struct.pack("d", 1) + data

	#packet = header + data
	my_socket.sendto(header, (dest_addr, 1))
	
	whatReady = select.select([my_socket], [], [], 5)
	if whatReady[0] == []: # Timeout
		print("Timeout")
		return
	recPacket, addr = my_socket.recvfrom(1024)
	print(addr)
	print("done!")

def main():
	# If we don't have a paramter, display usage
	if (len(sys.argv) != 2):
		usage()

	# Get the hostname/IP we wish to Tracert
	host = sys.argv[1]		
	dest_addr = socket.gethostbyname(host)
	
	time_to_live = 1
	id = 1
	while(time_to_live < 20):
		# Create the ICMP protocol
		icmp_proto = socket.getprotobyname("icmp")
		try:
			# Create the socket
			my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp_proto)
		except socket.error as exception:
			print("Error " + exception)
			os._exit(1)
		
		print('Host: {0} TTL: {1}'.format(dest_addr, time_to_live)) 
		ping(dest_addr, my_socket, time_to_live, id)
		time_to_live += 1
		id += 1
		my_socket.close()
	os._exit(0)

if __name__ == "__main__":
    main()

