#!/usr/bin/env python

"""
Copyright 2011 Thomas Graft, http://thomasgraft.com/. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, this list of
      conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice, this list
      of conditions and the following disclaimer in the documentation and/or other materials
      provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THOMAS GRAFT ``AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THOMAS GRAFT OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the
authors and should not be interpreted as representing official policies, either expressed
or implied, of Thomas Graft.

"""

import socket
import hashlib
import urllib2
import sys    

class BoxeeRemote:
    
    def __init__(self):
        
        # Begin User configurable data
        
        # Boxee will tell us this data when it pings us back
        # if this is not None, it will skip the broadcast phase
        self.BOXEE_ADDRESS = None
        self.BOXEE_PORT = None

        # Debug mode will print things
        # Set to False to avoid printing out messages
        self.DEBUG = False

        # End User configurable data

        


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
        
        
        
        
        # Broadcast for Boxee info if not already set
        if not self.BOXEE_ADDRESS or not self.BOXEE_PORT:
            self.discover();
    
    def discover(self):
        """Discovers and saves info about Boxee device on the network."""
        self._parse_boxee_response( self._broadcast_for_boxee_info() )

    def run_human_command( self, command ):
        """Run a non-formated boxee command, eg "vol 50" """
        self.run_command( self._convert_command( command ) )

    def run_command( self, command, argument=None ):
        """Runs a command against the boxee box. Command must match API syntax, eg SetVolume(50)"""
        url = self.BOXEE_API_URL % ( self.BOXEE_ADDRESS, self.BOXEE_PORT, command, argument )
        urllib2.urlopen(url)

    def _broadcast_for_boxee_info( self ):
        self._status("Broadcasting for Boxee")
        sock = socket.socket( socket.AF_INET, # Internet
                              socket.SOCK_DGRAM ) # UDP

        sock.setsockopt( socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        sock.sendto( self.UDP_MESSAGE_TO_BOXEE, self.UDP_BOXEE_BROADCAST )
        self._status("Done")

        self._status("Awaiting a response from Boxee")
        while True:

            (buf, address) = sock.recvfrom(2048)

            if not len(buf):
                break

            self.BOXEE_ADDRESS = address[0]

            return buf

    def _parse_boxee_response( self, response ):
        """ Parses the discovery response UDP packet XML """
        from xml.dom import minidom

        self._status("Parsing response from Boxee:\n" + response)

        dom = minidom.parseString(response)

        for node in dom.getElementsByTagName('BDP1'):
            self.BOXEE_PORT = node.getAttribute('httpPort')

    def _convert_command( self, human ):
        """ Converts a command like 'vol 50' to 'SetVolume(50)' or passes thru"""
        
        shortcut_map = {
            'm':'mute',
            'p':'pause',
            's':'stop',
            'pn':'PlayNext',
            'pp':'PlayPrev'
        }
        
        if human in shortcut_map.keys():
            return shortcut_map[human]
        
        # Volume
        if human[:3] == 'vol':
            return 'SetVolume(%s)' % human[4:]
        
        return human

    def _status( self, msg ):
        if self.DEBUG:
            print msg

def main():

    """
    TODO impliment these:
    
    GetVolume - Retrieves the current volume setting as a percentage of the maximum possible value.
    GetPercentage - Retrieves the current playing position of the currently playing media as a percentage of the media's length.
    """

    USAGE = """
FROM THE TERMINAL

examples:
boxee vol 50
boxee mute
boxee pn
boxee SeekPercentage(percent)

INTERACTIVE MODE
Commands

shortcut | command - Command description.

   | vol N - Sets the volume as a percentage of the maximum possible, where 0 <= N <= 100 (eg: 'vol 50')
 m | mute - Toggles the sound on/off.

 p | pause - Pauses the currently playing media.
 s | stop - Stops the currently playing media.
pn | playnext - Starts playing/showing the next media/image in the current playlist or, if currently showing a slidshow, the slideshow playlist.
pp | playnext - Starts playing/showing the previous media/image in the current playlist or, if currently showing a slidshow, the slideshow playlist.

   | SeekPercentage(percent) - Sets the playing position of the currently playing media as a percentage of the media's length.
   | SeekPercentageRelative(relative-percentage) - Adds/Subtracts the current percentage on to the current postion in the song

 e | exit - exit this app
 h | help - print this message
    """
    
    boxee = BoxeeRemote()

    # run command line commands
    # ./boxee.py vol 50
    if len(sys.argv) > 1:
        command = ' '.join(sys.argv[1:])
        boxee.run_human_command( command )
        sys.exit()
        
    
    print USAGE

    while True:
        
        command = raw_input('\nenter command: ')
        
        if command in ["e", "exit"]:
            sys.exit()
        
        elif command in ["h", "help"]:
            print USAGE
        
        else:
            boxee.run_human_command( command )
    

if __name__ == '__main__': 
    main()

