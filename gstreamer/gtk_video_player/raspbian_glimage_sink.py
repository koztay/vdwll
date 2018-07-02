#!/usr/bin/env python3

"""
https://gist.github.com/stuaxo/3009b761cba1085ac5730c7485506ee4

Code adapted from these examples:
https://lubosz.wordpress.com/2014/05/27/gstreamer-overlay-opengl-sink-example-in-python-3/
https://github.com/peterderivaz/pyopengles
https://github.com/gasman/shortcrust/
As of 2016-10-31 you need to use gst-uninstalled for set_window_handle to work on raspbian.
Install gst-uninstalled and run:
$ ~/gst/gst-master python raspbian-glimagesink.py
"""
import ctypes

from ctypes import c_int, c_uint, c_int32, c_uint32, c_int16, c_uint16, c_void_p, POINTER

from gi.repository import Gst
from gi.repository import GstVideo  # for sink.set_window_handle()
from gi.repository import GLib

bcm = ctypes.CDLL('libbcm_host.so')


class Alpha_struct(ctypes.Structure):
    """typedef enum {
  /* Bottom 2 bits sets the alpha mode */
  DISPMANX_FLAGS_ALPHA_FROM_SOURCE = 0,
  DISPMANX_FLAGS_ALPHA_FIXED_ALL_PIXELS = 1,
  DISPMANX_FLAGS_ALPHA_FIXED_NON_ZERO = 2,
  DISPMANX_FLAGS_ALPHA_FIXED_EXCEED_0X07 = 3,
  DISPMANX_FLAGS_ALPHA_PREMULT = 1 << 16,
  DISPMANX_FLAGS_ALPHA_MIX = 1 << 17
} DISPMANX_FLAGS_ALPHA_T;
typedef struct {
  DISPMANX_FLAGS_ALPHA_T flags;
  uint32_t opacity;
  VC_IMAGE_T *mask;
} DISPMANX_ALPHA_T;
typedef struct {
  DISPMANX_FLAGS_ALPHA_T flags;
  uint32_t opacity;
  DISPMANX_RESOURCE_HANDLE_T mask;
} VC_DISPMANX_ALPHA_T;  /* for use with vmcs_host */
"""
    _fields_ = [("flags", ctypes.c_long),
                ("opacity", ctypes.c_ulong),
                ("mask", ctypes.c_ulong)]


DISPMANX_PROTECTION_NONE = 0

c_uint32_p = POINTER(c_uint32)
DISPMANX_ELEMENT_HANDLE_T = c_uint32


class EGL_DISPMANX_WINDOW_T(ctypes.Structure):
    _fields_ = [("element", DISPMANX_ELEMENT_HANDLE_T), ("width", c_int), ("height", c_int)]


EGLNativeWindowType = POINTER(EGL_DISPMANX_WINDOW_T)


def c_ints(L):
    # from https://github.com/peterderivaz/pyopengles/blob/master/pyopengles.py#L40
    return (ctypes.c_int * len(L))(*L)


def create_native_window(x, y, width, height, layer=0, screen=0, alpha_flags=0, alpha_opacity=0):
    alpha_s = Alpha_struct(alpha_flags, alpha_opacity, 0)

    dst_rect = c_ints((x, y, width, height))
    src_rect = c_ints((0, 0, width << 16, height << 16))

    dispman_display = bcm.vc_dispmanx_display_open(screen)
    dispman_update = bcm.vc_dispmanx_update_start(screen)
    dispman_element = bcm.vc_dispmanx_element_add(dispman_update, dispman_display,
                                                  layer, ctypes.byref(dst_rect),
                                                  screen, ctypes.byref(src_rect),
                                                  DISPMANX_PROTECTION_NONE,
                                                  alpha_s, 0, 0)  # alpha clamp transform

    bcm.vc_dispmanx_update_submit_sync(dispman_update)
    window = EGL_DISPMANX_WINDOW_T(dispman_element, width, height)

    return window


def get_resolution(screen=0):
    width, height = ctypes.c_int(), ctypes.c_int()
    bcm.graphics_get_display_size(screen, c_uint32_p(width), c_uint32_p(height))
    return width.value, height.value


if __name__ == "__main__":
    assert bcm.bcm_host_init() == 0

    Gst.init([])

    pipeline = Gst.Pipeline()

    # src = Gst.ElementFactory.make("filesrc", None)
    # src.set_property("location", "/opt/vc/src/hello_pi/hello_video/test.h264")
    # # Note test file file ^ is only first few seconds of big buck bunny.

    src = Gst.ElementFactory.make("gltestsrc", None)

    decode = Gst.ElementFactory.make('decodebin', 'decode')
    sink = Gst.ElementFactory.make("glimagesink", None)


    def decode_src_created(element, pad):
        pad.link(sink.get_static_pad('sink'))


    decode.connect('pad-added', decode_src_created)

    if not sink or not src:
        print("GL elements not available.")
        exit()

    mainloop = GLib.MainLoop()

    pipeline.add(src)
    pipeline.add(decode)
    pipeline.add(sink)

    src.link(decode)

    width, height = get_resolution()
    print("get_resolution: %sx%s" % (width, height))

    # Create a window slightly smaller than fullscreen
    nativewindow = create_native_window(100, 100, width - 200, height - 200, alpha_opacity=0)
    win_handle = ctypes.addressof(nativewindow)


    def on_sync_message(bus, msg):
        if msg.get_structure().get_name() == 'prepare-window-handle':
            print('prepare-window-handle')
            sink = msg.src
            sink.set_window_handle(win_handle)
            sink.set_render_rectangle(0, 0, nativewindow.width, nativewindow.height)


    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.enable_sync_message_emission()
    bus.connect('sync-message::element', on_sync_message)

    if pipeline.set_state(Gst.State.PLAYING) == Gst.StateChangeReturn.FAILURE:
        pipeline.set_state(Gst.State.NULL)
        print("Failed")
    else:
        print("Run mainloop")
        mainloop.run()
