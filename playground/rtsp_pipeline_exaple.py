#!/usr/bin/env python3

"""RTSP restreamer based on GStreamer."""

import gi

gi.require_version('Gst', '1.0')
# gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GObject

loop = GObject.MainLoop()
GObject.threads_init()
Gst.init(None)
Gst.debug_set_colored(Gst.DebugColorMode.ON)
Gst.debug_set_active(True)
Gst.debug_set_default_threshold(3)


class AVPipeline(Gst.Pipeline):

    def __init__(self):
        Gst.Pipeline.__init__(self)

        # rtsp source
        rtspsrc = Gst.ElementFactory.make('rtspsrc', None)
        rtspsrc.set_property('location', 'rtsp://10.0.0.143/media/video1')
        rtspsrc.set_property('latency', 500)
        rtspsrc.set_property('timeout', 2000000)

        self.add(rtspsrc)
        self.link(rtspsrc)
        rtspsrc.connect('pad-added', self.rtspsrc_pad_added)

        # video
        vqueue = Gst.ElementFactory.make('queue', None)
        rtph264depay = Gst.ElementFactory.make('rtph264depay', None)
        # rtph264pay = Gst.ElementFactory.make('rtph264pay', None)
        #
        # rtph264pay.set_property('name', 'pay0')
        # rtph264pay.set_property('pt', 96)

        self.add(vqueue)
        self.add(rtph264depay)
        # self.add(rtph264pay)

        rtspsrc.link(vqueue)

        vqueue.link(rtph264depay)
        # rtph264depay.link(rtph264pay)

        decodebin = Gst.ElementFactory.make("decodebin")
        self.add(decodebin)

        rtph264depay.link(decodebin)

        if decodebin:
            decodebin.connect("pad_added", self.decodebin_pad_added)

        self._tolink_video_elem = vqueue

        converter = Gst.ElementFactory.make("videoconvert")
        self.add(converter)

        videosink = Gst.ElementFactory.make("autovideosink")
        self.add(videosink)

        decodebin.link(converter)
        converter.link(videosink)


    def rtspsrc_pad_added(self, element, pad):
        string = pad.query_caps(None).to_string()
        if string.startswith('application/x-rtp'):
            if 'media=(string)video' in string:
                pad.link(self._tolink_video_elem.get_static_pad('sink'))
                print('Video connected')
            elif 'media=(string)audio' in string:

                # create audio
                # Client doesn't get audio when I add audio elements in this point

                # audio
                aqueue = Gst.ElementFactory.make('queue', None)
                rtppcmudepay = Gst.ElementFactory.make('rtppcmudepay', None)
                rtppcmupay = Gst.ElementFactory.make('rtppcmupay', None)

                rtppcmupay.set_property('name', 'pay1')

                self.add(aqueue)
                self.add(rtppcmudepay)
                self.add(rtppcmupay)

                aqueue.link(rtppcmudepay)
                rtppcmudepay.link(rtppcmupay)

                for elem in (aqueue, rtppcmudepay, rtppcmupay):
                    elem.sync_state_with_parent()

                pad.link(aqueue.get_static_pad('sink'))
                print('Audio connected')

    def decodebin_pad_added(self, decodebin, pad):
        """
        Manually link the decodebin pad with a compatible pad on
        queue elements, when the decodebin "pad-added" signal
        is generated.
        """
        print("decodebin pad added layyynn")

        compatible_pad = None
        caps = pad.query_caps()
        print("caps ney ki?", caps)
        for i in range(caps.get_size()):
            structure = caps.get_structure(i)
            name = structure.get_name()
            print("{0:s}".format(name))
            # print("\n cap name is = ", name)
            if name[:5] == 'video':
                compatible_pad = self._tolink_video_elem.get_compatible_pad(pad, caps)
            elif name[:5] == 'audio':
                compatible_pad = self._tolink_video_elem.get_compatible_pad(pad, caps)

            if compatible_pad:
                pad.link(compatible_pad)


#
# class MyRTSPMediaFactory(GstRtspServer.RTSPMediaFactory):
#     LATENCY = 10000
#
#     def __init__(self):
#         GstRtspServer.RTSPMediaFactory.__init__(self)
#
#         self.set_shared(True)
#         self.set_property('latency', self.LATENCY)
#         self.set_transport_mode(GstRtspServer.RTSPTransportMode.PLAY)
#
#     def do_create_element(self, url):
#         return AVPipeline()
#
#
# class Restreamer(object):
#
#     def __init__(self, host, port):
#         self._server = GstRtspServer.RTSPServer()
#         self._server.set_address(host)
#         self._server.set_service(str(port))
#
#         mount_points = self._server.get_mount_points()
#         factory = MyRTSPMediaFactory()
#         mount_points.add_factory('/test', factory)
#
#         self._server.attach(None)


def main():
    player = AVPipeline()
    player.set_state(Gst.State.PLAYING)

    loop.run()


if __name__ == '__main__':
    main()