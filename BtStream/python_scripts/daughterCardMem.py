#!/usr/bin/python
import sys, struct, serial

def wait_for_ack():
   ddata = ""
   ack = struct.pack('B', 0xff)
   while ddata != ack:
      ddata = ser.read(1)
   return


if len(sys.argv) < 5:
   print "no device or arguments specified"
   print "You need to specify the serial port of the device you wish to connect to"
   print "A second argument must be specified to indicate which action to perform:"
   print "   r: Read daughter card memory"
   print "      Must be followed by the length to read and the offset to start"
   print "      reading from"
   print "   w: Write daughter card memory"
   print "      Must be followed by the length to write, the offset to start"
   print "      writing to, and the data to write"
   print "example:"
   print "   daughterCardMem.py Com12 r 50 480"
   print "      i.e. read 50 bytes starting from position 480"
   print "or"
   print "   daughterCardMem.py /dev/rfcomm0 W 3 0 0xAB 0xCD 0xEF"
   print "      i.e. write 3 bytes (0xAB, 0xCD and 0xEF) starting at position 0"
else:
   if (sys.argv[2] == 'r' or sys.argv[2] == 'R') and len(sys.argv) == 5:
      length = int(sys.argv[3], 0)
      offset = int(sys.argv[4], 0)
      if(0<length<=128) and (0<=offset<=2031) and (length+offset<=2032):
         ser = serial.Serial(sys.argv[1], 115200)
         ser.flushInput()
# send get daughtercardmem command
         ser.write(struct.pack('BBH', 0x69, length, offset))
         wait_for_ack()

         ddata = ""
         daughtercardmemresponse = struct.pack('B', 0x68)  #DAUGHTER_CARD_MEM_RESPONSE
         while ddata != daughtercardmemresponse:
            ddata = ser.read(1)

         ddata = ""
         numbytes = 0
         framesize = length+1

         while numbytes < framesize:
            ddata += ser.read(framesize)
            numbytes = len(ddata)

         (readlength,) = struct.unpack('B', ddata[0:1])
         print "%d read bytes:" % (readlength),
         for i in range(length):
            print "0x%02x" % struct.unpack('B', ddata[i+1]),
         print

         ser.close()
         
      else:
         print "Length or offset invalid"
         print "Length must be between 1 and 128"
         print "Offset must be between 0 and 2031"
         print "Length + Offset must not exceed 2032"
   elif (sys.argv[2] == 'w' or sys.argv[2] == 'W') and len(sys.argv) > 5:
      length = int(sys.argv[3], 0)
      offset = int(sys.argv[4], 0)
      if(0<length<=128) and (0<=offset<=2031) and (length+offset<=2032):
         if len(sys.argv) == (5+length):
#send set daughtercardmem command
            packet = struct.pack('BBH', 0x67, length, offset)
            for i in range(length):
               packet += struct.pack('B', int(sys.argv[i+5], 0))
            ser = serial.Serial(sys.argv[1], 115200)
            ser.flushInput()
            ser.write(packet)
            wait_for_ack()
            print "Daughter card memory updated"
            ser.close()
         else:
            print "Invalid number of arguments"

      else:
         print "Length or offset invalid"
         print "Length must be between 1 and 128"
         print "Offset must be between 0 and 2031"
         print "Length + Offset must not exceed 2032"
   else:
      print "Invalid selection or incorrect number of arguments for selection"
      print "Num args: %d" % (len(sys.argv))

   print
   print "All done"
