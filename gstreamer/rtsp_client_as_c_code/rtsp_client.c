//Display RTSP streaming of video
 //(c) 2011 enthusiasticgeek
 // This code is distributed in the hope that it will be useful,
 // but WITHOUT ANY WARRANTY; without even the implied warranty of
 // MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

#include <string.h>
#include <math.h>
#include <gst/gst.h>
#include <glib.h>

static gboolean bus_call (GstBus *bus,GstMessage *msg, gpointer data){
  GMainLoop *loop = (GMainLoop *) data;

  switch (GST_MESSAGE_TYPE (msg)) {

    case GST_MESSAGE_EOS:
      g_print ("Stream Ends\n");
      g_main_loop_quit (loop);
      break;

    case GST_MESSAGE_ERROR: {
      gchar  *debug;
      GError *error;

      gst_message_parse_error (msg, &error, &debug);
      g_free (debug);

      g_printerr ("Error: %s\n", error->message);
      g_error_free (error);

      g_main_loop_quit (loop);
      break;
    }
    default:
      break;
  }

  return TRUE;
}

static void on_pad_added (GstElement *element, GstPad *pad, gpointer data){

  GstPad *sinkpad;
  GstElement *decoder = (GstElement *) data;

  /* We can now link this pad with the rtsp-decoder sink pad */
  g_print ("Dynamic pad created, linking source/demuxer\n");

  sinkpad = gst_element_get_static_pad (decoder, "sink");

  gst_pad_link (pad, sinkpad);

  gst_object_unref (sinkpad);
}

int main (int argc, char *argv[])
{
  GMainLoop *loop;
  GstBus *bus;
  GstElement *source;
  GstElement *decoder;
  GstElement *sink;
  GstElement *pipeline;
  GstElement *demux;
  GstElement *colorspace;

  /* Initializing GStreamer */
  gst_init (&argc, &argv);
  loop = g_main_loop_new (NULL, FALSE);

 //gst-launch-0.10 rtspsrc location=rtsp://<ip> ! decodebin ! ffmpegcolorspace ! autovideosink
 //gst-launch -v rtspsrc location="rtsp://<ip> ! rtpmp4vdepay ! mpeg4videoparse ! ffdec_mpeg4 ! ffmpegcolorspace! autovideosink
 //gst-launch -v rtspsrc location="rtsp://<ip> ! rtpmp4vdepay ! ffdec_mpeg4 ! ffmpegcolorspace! autovideosink
  /* Create Pipe's Elements */
  pipeline = gst_pipeline_new ("video player");
  g_assert (pipeline);
  source   = gst_element_factory_make ("rtspsrc", "Source");
  g_assert (source);
  demux = gst_element_factory_make ("rtpmp4vdepay", "Depay");
  g_assert (demux);
  decoder = gst_element_factory_make ("ffdec_mpeg4", "Decoder");
  g_assert (decoder);
  colorspace     = gst_element_factory_make ("ffmpegcolorspace",  "Colorspace");
  g_assert(colorspace);
  sink     = gst_element_factory_make ("autovideosink", "Output");
  g_assert (sink);

  /*Make sure: Every elements was created ok*/
  if (!pipeline || !source || !demux || !decoder || !colorspace || !sink) {
    g_printerr ("One of the elements wasn't create... Exiting\n");
    return -1;
  }

  g_printf(" \nPipeline is Part(A) ->(dynamic/runtime link)  Part(B)[ Part(B-1) -> Part(B-2) -> Part(B-3) ]\n\n");
  g_printf(" [source](dynamic)->(dynamic)[demux]->[decoder]->[colorspace]->[videosink] \n\n");

  /* Set video Source */
  g_object_set (G_OBJECT (source), "location", argv[1], NULL);
  //g_object_set (G_OBJECT (source), "do-rtcp", TRUE, NULL);
  g_object_set (G_OBJECT (source), "latency", 0, NULL);

  /* Putting a Message handler */
  bus = gst_pipeline_get_bus (GST_PIPELINE (pipeline));
  gst_bus_add_watch (bus, bus_call, loop);
  gst_object_unref (bus);

  /* Add Elements to the Bin */
  gst_bin_add_many (GST_BIN (pipeline), source, demux, decoder, colorspace, sink, NULL);

  /* Link confirmation */
  if (!gst_element_link_many (demux, decoder, colorspace, sink, NULL)){
     g_warning ("Linking part (B) Fail...");
  }

  g_printf("\nNote that the source will be linked to the demuxer(depayload) dynamically.\n\
     The reason is that rtspsrc may contain various elements (for example\n\
     audio and video). The source pad(s) will be created at run time,\n\
     by the rtspsrc when it detects the amount and nature of elements.\n\
     Therefore we connect a callback function which will be executed\n\
     when the \"pad-added\" is emitted.\n");

  /* Dynamic Pad Creation */
  if(! g_signal_connect (source, "pad-added", G_CALLBACK (on_pad_added),demux))
  {
    g_warning ("Linking part (A) with part (B) Fail...");
  }
  /* Run the pipeline */
  g_print ("Playing: %s\n", argv[1]);
  gst_element_set_state (pipeline, GST_STATE_PLAYING);
  g_main_loop_run (loop);

  /* Ending Playback */
  g_print ("End of the Streaming... ending the playback\n");
  gst_element_set_state (pipeline, GST_STATE_NULL);

  /* Eliminating Pipeline */
  g_print ("Eliminating Pipeline\n");
  gst_object_unref (GST_OBJECT (pipeline));

  return 0;
}