import socket
import hashlib

# Boxee will tell us this data when it pings us back
# if this is not None, it will skip the broadcast phase
BOXEE_ADDRESS = None
BOXEE_PORT = None

# Where we want boxee to ping us back at
UDP_LOCAL_IP = '' # binds to all local interfaces
UDP_LOCAL_PORT = 2563

# Broadcast port / IP for when we look for Boxee
UDP_BOXEE_BROADCAST = ('<broadcast>', 2562)

# This is the data we ping Boxee with
BOXEE_APPLICATION = 'iphone_remote' # required for this to work
BOXEE_SHARED_KEY = 'b0xeeRem0tE!'   # required for this to work
BOXEE_CHALLENGE = 'boxee_cmd_client'
BOXEE_VERSION = '0.1' # version of this app, not really used i think
BOXEE_SIGNATURE = hashlib.md5( BOXEE_CHALLENGE + BOXEE_SHARED_KEY ).hexdigest()

UDP_MESSAGE_TO_BOXEE = '''<?xml version="1.0"?>
	<BDP1 cmd="discover" 
		  application="%s"
		  version="%s" challenge="%s"
	      signature="%s" />''' % ( BOXEE_APPLICATION, BOXEE_VERSION, BOXEE_CHALLENGE, BOXEE_SIGNATURE )

# Debug mode will print things
# Set to False to avoid printing out messages
DEBUG = True

def main():
	
	# If we don't already have 
	if not BOXEE_ADDRESS or not BOXEE_PORT:
		(response, BOXEE_ADDRESS) = broadcast_for_boxee_info()
		parse_boxee_response( response )
	
	#if '-r' command line arg, do command, else loop for commands
	
	# Commands
	while True:
		pass #TODO

def status( msg ):
	if DEBUG: print msg
	
def broadcast_for_boxee_info():
	status("Broadcasting for Boxee")
	sock = socket.socket( socket.AF_INET, # Internet
					      socket.SOCK_DGRAM ) # UDP

	sock.setsockopt( socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

	sock.sendto( UDP_MESSAGE_TO_BOXEE, UDP_BOXEE_BROADCAST )
	status("Done")

	status("Awaiting a response from Boxee")
	while True:

		(buf, address) = sock.recvfrom(2048)

		if not len(buf):
			break

		return (buf, address)

def parse_boxee_response( response ):
	""" Parses the discovery response UDP packet XML """
	from xml.dom import minidom
	
	status("Parsing response from Boxee:\n" + response)
	
	dom = minidom.parse(response)
	
	for node in dom.getElementsByTagName('BDP1'):
	        BOXEE_PORT = node.getAttribute('httpPort')

def convert_command( human, boxee ):
	""" Converts a command like 'vol 50' to 'SetVolume(50)' or passes thru"""
	pass
	
def run_command( command ):
	""" Runs a command against the boxee box """
	pass

# RUN
main()
# TODO: cmd line args

