#!/usr/bin/env python

import socket
import hashlib
import urllib2

class BoxeeRemote:
    
    def __init__(self):
        
        # Boxee will tell us this data when it pings us back
        # if this is not None, it will skip the broadcast phase
        self.BOXEE_ADDRESS = None
        self.BOXEE_PORT = None

        # Debug mode will print things
        # Set to False to avoid printing out messages
        self.DEBUG = False


        # Where we want boxee to ping us back at
        self.UDP_LOCAL_IP = '' # binds to all local interfaces
        self.UDP_LOCAL_PORT = 2563

        # Broadcast port / IP for when we look for Boxee
        self.UDP_BOXEE_BROADCAST = ('<broadcast>', 2562)

        # This is the data we ping Boxee with
        self.BOXEE_APPLICATION = 'iphone_remote' # required for this to work
        self.BOXEE_SHARED_KEY = 'b0xeeRem0tE!'   # required for this to work
        self.BOXEE_CHALLENGE = 'boxee_cmd_client'
        self.BOXEE_VERSION = '0.1' # version of this app, not really used i think
        self.BOXEE_SIGNATURE = hashlib.md5( self.BOXEE_CHALLENGE + self.BOXEE_SHARED_KEY ).hexdigest()

        self.BOXEE_API_URL = "http://%s:%s/xbmcCmds/xbmcHttp?command=%s(%s)"

        self.UDP_MESSAGE_TO_BOXEE = '''<?xml version="1.0"?>
            <BDP1 cmd="discover" 
                  application="%s"
                  version="%s" challenge="%s"
                  signature="%s" />''' % ( self.BOXEE_APPLICATION, self.BOXEE_VERSION, self.BOXEE_CHALLENGE, self.BOXEE_SIGNATURE )
        
    def broadcast_for_boxee_info( self ):
        self.status("Broadcasting for Boxee")
        sock = socket.socket( socket.AF_INET, # Internet
                              socket.SOCK_DGRAM ) # UDP

        sock.setsockopt( socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        sock.sendto( self.UDP_MESSAGE_TO_BOXEE, self.UDP_BOXEE_BROADCAST )
        self.status("Done")

        self.status("Awaiting a response from Boxee")
        while True:

            (buf, address) = sock.recvfrom(2048)

            if not len(buf):
                break

            self.BOXEE_ADDRESS = address[0]

            return buf

    def parse_boxee_response( self, response ):
        """ Parses the discovery response UDP packet XML """
        from xml.dom import minidom

        self.status("Parsing response from Boxee:\n" + response)

        dom = minidom.parseString(response)

        for node in dom.getElementsByTagName('BDP1'):
            self.BOXEE_PORT = node.getAttribute('httpPort')

    def convert_command( self, human ):
        """ Converts a command like 'vol 50' to 'SetVolume(50)' or passes thru"""
        return human

    def run_human_command( self, command ):
        self.run_command( self.convert_command( command ) )

    def run_command( self, command, argument=None ):
        """ Runs a command against the boxee box """
        url = self.BOXEE_API_URL % ( self.BOXEE_ADDRESS, self.BOXEE_PORT, command, argument )
        urllib2.urlopen(url)
    
    def status( self, msg ):
        if self.DEBUG:
            print msg

def main():

    boxee = BoxeeRemote()

    if not boxee.BOXEE_ADDRESS or not boxee.BOXEE_PORT:
        boxee.parse_boxee_response( boxee.broadcast_for_boxee_info() )

    interactive_mode = False

    import sys    
    for arg in sys.argv:
        if arg == '-r':
            pass
        if arg == '-i':
            interactive_mode = True
    
    #boxee.run_command("Pause")
    
    
    if interactive_mode:
        print "Enter commands: "
        print "See http://developer.boxee.tv/Remote_Control_Interface for a full list"
        while True:
            boxee.run_human_command( raw_input('boxee: ') )
    

# RUN
main()
# TODO: cmd line args

