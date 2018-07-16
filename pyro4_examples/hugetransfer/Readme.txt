This test transfers huge data structures to see how Pyro handles those.
It sets a socket timeout as well to see how Pyro handles that.


A couple of problems could be exposed by this test:

- Some systems don't really seem to like non blocking sockets and large
  data transfers. For instance Mac OS X seems eager to cause EAGAIN errors
  when your data exceeds 'the devils number' number of bytes.
  Note that this problem only occurs when using specific socket code.
  Pyro contains a workaround. More info:
    http://old.nabble.com/The-Devil%27s-Number-td9169165.html
    http://www.cherrypy.org/ticket/598
    
- Other systems seemed to have problems receiving large chunks of data.
  Windows causes memory errors when the receive buffer is too large.
  Pyro's receive loop works with comfortable smaller data chunks,
  to avoid these kind of problems.


Performance numbers with the various serializers on my local network:

serializer | performance (string) | performance (bytes)
-----------+---------------------------------------------
   pickle  |     33260 kb/sec     |   33450 kb/sec
  marshal  |     27900 kb/sec     |   32300 kb/sec
     json  |     23856 kb/sec     |   not supported
  serpent  |     13358 kb/sec     |    9066 kb/sec


Performance of the download via iterator is almost identical to
the normal transfer speed.


Note:
For a possible approach on transferring large amounts of binary data
*efficiently*, see the 'filetransfer' example.  It works with a raw socket
connection and avoids the Pyro protocol and serialization overhead.
