#! /usr/bin/python

# pyrtsp - RTSP test server hack
# Copyright (C) 2013  Robert Swain <robert.swain@gmail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

"""
 https://github.com/superdump/pyrtsp
 sudo apt-get install gir1.2-gst-rtsp-server-1.0
"""


import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, GstVideo, GstRtspServer, GstRtsp

Gst.init(None)

mainloop = GObject.MainLoop()

server = GstRtspServer.RTSPServer()

mounts = server.get_mount_points()

factory = GstRtspServer.RTSPMediaFactory()
factory.set_launch('(videotestsrc is-live=1 ! x264enc speed-preset=ultrafast tune=zerolatency ! rtph264pay name=pay0 pt=96)')

# multicast için aşağıdakini yazdım
# ###########################################################
factory.set_shared(True)
pool = GstRtspServer.RTSPAddressPool()
pool.add_range("224.3.0.0", "224.3.0.10", 5000, 5010, 16)
factory.set_address_pool(pool)
factory.set_protocols(GstRtsp.RTSPLowerTrans.UDP_MCAST)
# ###########################################################

mounts.add_factory("/test", factory)

server.attach(None)

print("stream ready at rtsp://127.0.0.1:8554/test")
mainloop.run()



"""
factory = gst_rtsp_media_factory_new ();
  gst_rtsp_media_factory_set_launch (factory, "( "
      "videotestsrc ! video/x-raw,width=352,height=288,framerate=15/1 ! "
      "x264enc ! rtph264pay name=pay0 pt=96 "
      "audiotestsrc ! audio/x-raw,rate=8000 ! "
      "alawenc ! rtppcmapay name=pay1 pt=97 " ")");

  gst_rtsp_media_factory_set_shared (factory, TRUE);

  /* make a new address pool */
  pool = gst_rtsp_address_pool_new ();
  gst_rtsp_address_pool_add_range (pool,
      "224.3.0.0", "224.3.0.10", 5000, 5010, 16);
  gst_rtsp_media_factory_set_address_pool (factory, pool);
  /* only allow multicast */
  gst_rtsp_media_factory_set_protocols (factory,
      GST_RTSP_LOWER_TRANS_UDP_MCAST);
  g_object_unref (pool);

  /* attach the test factory to the /test url */
  gst_rtsp_mount_points_add_factory (mounts, "/test", factory);


"""