#!/usr/bin/env python3
"""
Basic tutorial 9: Media information gathering
https://gstreamer.freedesktop.org/documentation/tutorials/basic/media-information-gathering.html
"""
import sys
import logging
import gi

gi.require_versions({'Gtk': '3.0', 'Gst': '1.0', 'GstApp': '1.0', 'GstPbutils': '1.0'})

from gi.repository import Gst, GLib, Gtk, GstApp, GObject, GstPbutils
from array import array

Gst.init(None)
Gst.debug_set_colored(Gst.DebugColorMode.ON)
Gst.debug_set_active(True)
Gst.debug_set_default_threshold(3)


class CustomData:
    discoverer = None
    main_loop = None


class Main:
    def __init__(self):

        self.data = CustomData()
        self.main()



    # Python version of GST_TIME_ARGS
    def convert_ns(self, t):
        s, ns = divmod(t, 1000000000)
        m, s = divmod(s, 60)

        if m < 60:
            return "0:%02i:%02i.%i" % (m, s, ns)
        else:
            h, m = divmod(m, 60)
            return "%i:%02i:%02i.%i" % (h, m, s, ns)

    def print_tag_foreach(self, tags, depth):
        # if isinstance(val, str):
        #     str = val.dup_string();
        # else:
        #     str = Gst.value_serialize(val)

        for x in range(0, tags.n_tags()):
            print("Tags: {0} {1}".format(tags.nth_tag_name(x),
                                           tags.peek_string_index(
                                               tags.nth_tag_name(x), 0).value))

        # for tkey in tags.keys():
            # print("%s%s: %s" % ((2 * depth) * " ", tkey, tags[tkey]))

    def print_stream_info(self, info, depth):
        caps = info.get_caps()

        if caps:
            if caps.is_fixed():
                desc = GstPbutils.pb_utils_get_codec_description(caps)
            else:
                desc = caps.to_string()

        print('{0}: {1}'.format(2 * depth, info.get_stream_type_nick(), desc))

        tags = info.get_tags()
        if tags:
            print('Tags: {0}'.format(2 * (depth + 1)))

            # print_tag_foreach(tags, depth * 2)
            # tags.foreach(self.print_tag_foreach, depth * 2)

    def print_topology(self, info, depth):
        if not info:
            return

        self.print_stream_info(info, depth);

        next = info.get_next()

        if next:
            self.print_topology(next, depth + 1)
        elif isinstance(info, GstPbutils.DiscovererContainerInfo):
            streams = info.get_streams()
            for tmp in streams:
                self.print_topology(tmp, depth + 1)

    # This function is called every time the discoverer has information regarding
    # one of the URIs we provided.

    def on_discovered_cb(self, discoverer, info, err, data):
        uri = info.get_uri()
        result = info.get_result()

        if result == GstPbutils.DiscovererResult.URI_INVALID:
            print('Invalid URI "{0}"\n'.format(uri))
        elif result == GstPbutils.DiscovererResult.ERROR:
            print('Discoverer error: {0}\n'.format(err.message))
        elif result == GstPbutils.DiscovererResult.TIMEOUT:
            print('Timeout\n')
        elif result == GstPbutils.DiscovererResult.BUSY:
            print('Busy\n')
        elif result == GstPbutils.DiscovererResult.MISSING_PLUGINS:
            print("Missing plugins: {0}\n".format(info.get_misc().to_string()))
        elif result == GstPbutils.DiscovererResult.OK:
            print("Discovered '{0}'\n".format(uri))
            # If we got no error, show the retrieved information
            print("\nDuration: %s" % self.convert_ns(info.get_duration()))

            tags = info.get_tags()
            if tags:
                print("Tags:")
                self.print_tag_foreach(tags, 1)

            print("Seekable: %s" % ("yes" if info.get_seekable() else "no"))
            print("")

            sinfo = info.get_stream_info()
            if sinfo:
                print("Stream information:")
                self.print_topology(sinfo, 1)
                print("")

    def on_finished_cb(self, discoverer, data):
        print("Finished discovering\n")
        self.data.main_loop.quit()

    def main(self):

        uri = 'https://gstreamer.freedesktop.org/data/media/small/sintel.mkv'

        # if a URI was provided, use it instead of the default one
        if len(sys.argv) > 1:
            uri = sys.argv[1]

        print("Discovering '{0}'\n".format(uri))

        self.data.discoverer = GstPbutils.Discoverer.new(5 * Gst.SECOND)
        if not self.data.discoverer:
            print('Error creating discoverer instance: ', file=sys.stderr)
            sys.exit(-1)

        self.data.discoverer.connect('discovered', self.on_discovered_cb, self.data)
        self.data.discoverer.connect('finished', self.on_finished_cb, self.data)

        self.data.discoverer.start()

        if not self.data.discoverer.discover_uri_async(uri):
            print('Failed to start discovering URI "{0}'.format(uri), file=sys.stderr)
            sys.exit(-1)

        self.data.main_loop = GLib.MainLoop()
        self.data.main_loop.run()

        self.data.discoverer.stop()


Main()
