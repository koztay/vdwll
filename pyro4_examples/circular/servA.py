from __future__ import print_function
import Pyro4.core
import Pyro4.naming
import chain

this_node = "A"
next_node = "B"

servername = "example.chain." + this_node

with Pyro4.core.Daemon() as daemon:
    obj = chain.Chain(this_node, next_node)
    uri = daemon.register(obj)
    with Pyro4.naming.locateNS() as ns:
        ns.register(servername, uri)

    # enter the service loop.
    print("Server started %s" % this_node)
    daemon.requestLoop()
