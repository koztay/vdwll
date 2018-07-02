# python3 gst_player_decodebin.py --stream_path='/Users/kemal/WorkSpace/Videowall Development/media/pixar.mp4' --output_path=. --sink_type=file rotation="0" --seed="12345"

import os
import gi
import sys
from fractions import Fraction
import time
import threading
import random
import logging
import re

gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst
GObject.threads_init()
Gst.init(None)

'''
Logging info formats
'''
_format = [
           '%(levelname)s',
           '%(threadName)s',
           '%(message)s',
          ]

'''
Logging info basic configuration
'''
# FIXME: logging initialization must be removed later
logging.basicConfig(
    level=logging.DEBUG,
    format='\t'.join(_format),
)

log = logging.getLogger()


def frame_to_nanosecond(frame, framerate):
    '''
    Frame number to nano second convert
    '''
    #assert isinstance(framerate, Fraction)
    try:
        t = frame * Gst.SECOND * framerate.denominator / framerate.numerator
    except:
        t = 0
        pass
    return t


def nanosecond_to_frame(nanosecond, framerate):
    '''
    Nano second to frame number convert
    '''
    #assert isinstance(framerate, Fraction)
    try:
        frame = int(round(nanosecond * framerate / framerate.denominator / Gst.SECOND))
    except:
        frame = 0
        pass
    return frame


class VPlayer(object):
    '''
    Video Player Class with following functionality.
    1. Pipeline construction using decodebin
    2. Play
    3. Pause
    4. Reset
    5. Resume
    6. Frame based seek both forward and backward seek
    7. Muliple seek on random frame number for N numbers of time
    8. Slice - it will play in-between frames of given start and stop count.
    9. Forward, Fast-forward, Fast-reverse
    10. Skip-Frame
    '''
    def __init__(self, stream_path, output_path, sink_type, modifiers):

        log.info('In side the player other options are received')
        # other_opt = ast.literal_eval(other_opt)
        self.stream_path = stream_path
        log.info('in init %s' % self.stream_path)

        self.output_dir = output_path

        self.mainloop = GObject.MainLoop()
        '''
        Initilize the variables
        '''
        self.position = Gst.CLOCK_TIME_NONE
        self.duration = Gst.CLOCK_TIME_NONE
        self.total_duration = Gst.CLOCK_TIME_NONE

        self.framerate = 0
        self.frame_count = 0
        self.Xvimagesink = True  # If want to display video ouput.
        self.is_playing = False
        self.done_event = threading.Event()
        self.decode_n_frames = 0
        self.rotate = 0
        self.x_scale = 0
        self.y_scale = 0
        self.pp_count = 0
        self.exitFlag = ''  # Flag used to monitor pipeline prerolling across threads
        self.flag = False
        CLOCKWISE = 1
        ROTATE_180 = 2
        COUNTER_CLOCKWISE = 3
        '''
        Set all modifiers
        '''
        self.get_set_modifiers(modifiers)
        log.info('After get_set modifiers')
        log.info('decode_n_frames = %d' % self.decode_n_frames)
        log.info('PP_count = %d' % self.pp_count)
        log.info('rotation = %d' % self.rotate)
        log.info('x_scale = %s' % self.x_scale)
        log.info('y scale = %s' % self.y_scale)

        '''
        Construct pipeline
        '''
        # Define the pipeline instance.
        self.pipeline = Gst.Pipeline()

        # Define pipeline elements.
        self.src = Gst.ElementFactory.make('filesrc', None)
        self.dec = Gst.ElementFactory.make('decodebin', None)
        self.vcon = Gst.ElementFactory.make('videoconvert', None)
        self.cap_filter = Gst.ElementFactory.make('capsfilter', 'filter')
        self.vflip = Gst.ElementFactory.make('videoflip', None)

        # Select Sink as requested
        sink_map = {'file': lambda: Gst.ElementFactory.make('filesink', None),
                    'xvimage': lambda: Gst.ElementFactory.make('xvimagesink', None),
                    'frame_crc': lambda: Gst.ElementFactory.make('checksumsink', None),
                    'fake': lambda: Gst.ElementFactory.make('fakesink', None)
                    }
        # self.sink = sink_map[sink_type]()
        self.sink = Gst.ElementFactory.make('fake', None)

        # Add elements to the pipeline.
        for element in (self.src, self.dec, self.vcon, self.cap_filter, self.sink):
            self.pipeline.add(element)
        if self.rotate:
            self.pipeline.add(self.vflip)

        # Link elements in the pipeline.
        self.src.link(self.dec)
        self.vcon.link(self.cap_filter)
        if self.rotate:
            self.cap_filter.link(self.vflip)
            self.vflip.link(self.sink)
        else:
            self.cap_filter.link(self.sink)

        '''
        Connects signals with methods.
        '''
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message::eos', self._on_eos)
        self.bus.connect('message::error', self._on_error)
        self.bus.connect('message::warn', self._on_message)
        self.bus.connect('message::segment-done', self._on_segment_done)
        # self.bus.connect('message::state-changed', self._on_message_state_changed)
        self.bus.connect('message::buffering', self._on_message_buffering)
        # self.bus.connect('message::', self.get_message)

        # Set Properties
        self.src.set_property('location', self.stream_path)
        caps = Gst.caps_from_string('video/x-raw,format=(string)I420')
        self.cap_filter.set_property('caps', caps)
        if self.decode_n_frames:
            self.src.set_property('num_buffers', self.decode_n_frames)
        if sink_type == 'file':
            yuv_file_name = os.path.join(self.output_dir, 'out.yuv')
            log.info('YUV_file_PATH=%s' % yuv_file_name)
            log.info('Test Dir Path=%s' % (os.getcwd()))
            self.sink.set_property('location', yuv_file_name)
        if self.rotate:
            method = {90: COUNTER_CLOCKWISE, 180: ROTATE_180, 270: CLOCKWISE}
            self.vflip.set_property('method', method.get(self.rotate))

        # Connect signal handler
        self.dec.connect('pad-added', self._on_pad_added)
        self.dec.connect('no-more-pads', self._on_no_more_pads)
        self.dec.connect('element-added', self._on_element_added)

    def _on_element_added(self, _, element):
        log.info('_on_element_added')
        element_name = element.get_name()
        if 'omx' in element_name and 'dec' in element_name:
            log.info('%s Element is added in bin' % element_name)
            if self.rotate in [90, 180, 270]:
                element.set_property('rotation', self.rotate)
                log.info('Rotation property is set')
                log.info('Rotation = %d' % element.get_property('rotation'))
            elif self.x_scale and self.y_scale:
                element.set_property('x-scale', eval(self.x_scale))
                element.set_property('y-scale', eval(self.y_scale))
                if element.get_property('x-scale') == eval(self.x_scale) and element.get_property('y-scale') == eval(self.y_scale):
                    log.info('Scaling property is set')
                    log.info('Scaling %sx%s is set' % (self.x_scale, self.y_scale))

    def _on_message_buffering(self, bus, message):
        log.info('_on_message_buffering')
        percent = message.parse_buffering()
        log.info('Buffering percentage = %d' % percent)

    def _on_message_state_changed(self, bus, message):
        log.info('_on_message_buffering')
        old_state, new_state, pending = message.parse_state_changed()
        log.info('OLD state = %s' % old_state)
        log.info('NEW state = %s' % new_state)
        log.info('PENDING = %s' % pending)

    def _on_pad_added(self, element, pad):
        caps = pad.query_caps(None)
        string = pad.query_caps(None).to_string()
        log.info('on_pad_added():%r is found', string)
        if string.startswith('video/'):
            log.info('on_pad_added():%r is linked to sink', string)
            ret = pad.link(self.vcon.get_static_pad('sink'))
            (num, denom) = caps.get_structure(0).get_fraction('framerate')[1:3]
            self.framerate = Fraction(num, denom)
            log.info('framerate : %d found in pads cap', self.framerate)
            log.info(ret)

    def _on_no_more_pads(self, element):
        log.info('on_no_more_pads')
        self.exitFlag = 'prerolled'
        log.info('_on_no_more_pads : exitFlag = %s' % self.exitFlag)
        return 0

    def _on_eos(self, bus, msg):
        log.info('on_eos()')
        self.pipeline.set_state(Gst.State.NULL)
        if self.mainloop.is_running():
            self.mainloop.quit()
        self.kill()
        return 0

    def _on_error(self, bus, msg):
        log.info('on_error')
        err, debug = msg.parse_error()
        log.info('on_error(): %s\n%s' % (err, debug))
        if self.mainloop.is_running():
            self.mainloop.quit()
        self.kill()

    def _on_message(self, bus, msg):
        log.info('_on_message')
        err, debug = msg.parse_error()
        log.info(debug)
        log.info(err)

    def _on_handoff(self, element, buf, pad):
        timestamp = buf.pts
        log.info('_on_handoff : %r', timestamp)

    def _on_segment_done(self, bus, msg):
        log.info('on_segment_done')

    def query_position(self):
        try:
            _, position = self.pipeline.query_position(Gst.Format.TIME)
        except:
            log.info('position query failed')
            position = Gst.CLOCK_TIME_NONE
        try:
            _, duration = self.pipeline.query_duration(Gst.Format.TIME)
        except:
            log.info('duration query failed')
            duration = Gst.CLOCK_TIME_NONE
        return (position, duration)

    def query_buffering(self):
        buffering = Gst.Query.new_buffering(Gst.Format.TIME)
        if self.pipeline.query(buffering):
            _, buf_start, buf_end, _ = buffering.parse_buffering_range()
        else:
            log.info('buffering query failed')
            buf_start = 0
            buf_end = 0
        return (buf_start, buf_end)

    def format_time(self, value):
        seconds = value / Gst.SECOND
        return '%02d:%02d' % (seconds / 60, seconds % 60)

    def stop(self):
            log.info("Stopping pipeline {0}".format(self.pipeline.get_name()))
            self.pipeline.set_state(Gst.State.NULL)

    def play(self):
        ret = self.pipeline.set_state(Gst.State.PLAYING)
        self.is_playing = True
        self.exitFlag = 'prerolling'
        self.flag = True
        log.debug('set_state(Gst.State.PLAYING): %s', ret)

    def pause(self):
        if self.exitFlag != 'killed':
            ret = self.pipeline.set_state(Gst.State.PAUSED)
            self.is_playing = False
            log.debug('set_state(Gst.State.PAUSED): %s', ret)

    def kill(self):
        self.pipeline.set_state(Gst.State.NULL)
        if self.mainloop.is_running():
            self.mainloop.quit()
        log.info('Player Killed!')
        if self.exitFlag == 'hang':
            self.exitFlag = 'hang'
        else:
            self.exitFlag = 'killed'
        return 0

    def resume(self):
        ret = self.pipeline.set_state(Gst.State.PLAYING)
        log.info(ret)

    def reset(self):
        log.info('on _reset(): seeking to start of video')
        ret = self.pipeline.seek_simple(
                         Gst.Format.TIME,
                         Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
                         0)
        log.info(ret)

    def get_total_time(self):
        log.info('Get total time of stream')
        self.play()
        time.sleep(1)
        self.pause()
        self.seek_end()
        _, duration = self.query_position()
        self.total_duration = (duration / 1000000000)
        self.reset()

    def _slice(self, start, stop):
        log.info('configuration slice %r %r', start, stop)
        self.pipeline.seek(
            1.0,  # rate
            Gst.Format.TIME,
            Gst.SeekFlags.FLUSH | Gst.SeekFlags.SEGMENT,
            Gst.SeekType.SET,
            frame_to_nanosecond(start, self.framerate),
            Gst.SeekType.SET,
            frame_to_nanosecond(stop, self.framerate))

    def slice(self, start, stop):
        GObject.idle_add(self._slice, start, stop)

    def seek_frame_no(self, frame):
        log.info('seeking to %r', frame)
        ret = self.pipeline.seek_simple(
                         Gst.Format.TIME,
                         Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
                         frame_to_nanosecond(frame, self.framerate)
                         )
        log.info(ret)

    def seek_simple(self, _seek_time):
        log.info('in seek_simple')
        log.info(_seek_time)
        frame = nanosecond_to_frame(_seek_time, self.framerate)
        log.info('seeking to %r', frame)
        ret = self.pipeline.seek_simple(
                         Gst.Format.TIME,
                         Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
                         _seek_time
                         )
        log.info(ret)

    def seek_end(self):
        log.info('__seek_end')
        res = self.pipeline.seek(1.0, Gst.Format.TIME,
            Gst.SeekFlags.FLUSH | Gst.SeekFlags.ACCURATE,
            Gst.SeekType.END, -1,
            Gst.SeekType.NONE, 0)
        log.info(res)

    def multi_seek(self, count, total_duration, m_seed):
        self.play()
        log.info('Waiting to prerolled!')
        while True:
            if self.exitFlag == 'prerolled' or self.exitFlag != 'killed':
                break
        log.info('multi_seek')
        self.total_duration = total_duration
        log.info('total_time = %d' % self.total_duration)
        #For automated seek
        #sid = random.randint(0, 99999)
        #For Manual seek
        seed = m_seed
        log.info('\nRandom Seed = %d\n' % seed)
        random.seed(seed)
        for _ in range(count):
            if self.exitFlag == 'killed':
                break
            seek_time = random.uniform(0, (self.total_duration * 1000000000))
            log.info('seek_on_time =%.4f' % (seek_time / 1000000000))
            log.info('seek_on_time =%.4f' % (seek_time))
            self.seek_simple(int(seek_time))
            self.play()
            play_time = random.uniform(1, 2)
            time.sleep(int(play_time))
            log.info('pause for %.2f' % play_time)

    def seek_backward(self, frame):
        back_time = frame_to_nanosecond(frame, self.framerate)
        log.debug('back_time: %d', back_time)
        if back_time < 0 and back_time >= self.total_duration:
            log.info('Backward time is wrong %d\n' % (back_time,))
        else:
            self._seek_simple(back_time)

    def play_pause(self, count, total_duration, m_seed):
        log.info('Play_Pause')
        self.play()
        log.info('Waiting to prerolled!')
        while True:
            if self.exitFlag == 'prerolled' or self.exitFlag != 'killed':
                break
        self.total_duration = total_duration
        log.info('in Play Pause total_time = %d' % self.total_duration)
        # For Automated Play-Pause
        #seed = random.randint(0, 99999)
        # For Manual Play-Pause
        seed = m_seed
        log.info('\nRandom Seed = %d\n' % seed)
        random.seed(seed)
        elapsed_time = 0
        s = []

        for _ in range(count):
            s.append(random.uniform(1, (self.total_duration)))
            s.sort()
        log.info(s)
        for random_dur in s:
            log.info('PLAY')
            self.play()
            while (elapsed_time < random_dur) and self.exitFlag != 'killed':
                _, crt_time = self.pipeline.query_position(Gst.Format.TIME)
                elapsed_time = (crt_time / 1000000000)
            log.info('PAUSE')
            self.pause()
            log.info('Pause at time = expected at  %.2f, received at %.2f' % (random_dur, elapsed_time))
            pause_time = random.uniform(1, 2)
            time.sleep(int(pause_time))
            log.info('pause for %.2f' % pause_time)
        log.info('PLAY-PAUSE Done')
        if self.exitFlag != 'killed':
            self.play()
        return 0

    def message_handler(self, bus, msg):
        '''
        Capture the messages on the bus and set the appropriate flag.
        '''
        msgType = msg.type
        log.info(msg)
        if Gst.MESSAGE_ERROR in msgType:
            log.info('on_eos()')
            self.is_playing = False
            self.pipeline.set_state(Gst.State.NULL)
            self.kill()

    def rate_change(self, data_rate):
        log.info('Fast_Forward')
        seek_event = Gst.Event.new_seek(data_rate, Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.ACCURATE,
                                        Gst.SeekType.SET, 0, Gst.SeekType.NONE, 0)
        Gst.Element.send_event(self.pipeline, seek_event)

    def skip_frame(self, skip_frame_count):
        log.info('skip_frame')
        skip_event = Gst.Event.new_step(Gst.Format.BUFFERS, skip_frame_count, 1.0, True, False)
        Gst.Element.send_event(self.pipeline, skip_event)

    def wait_done(self, timeout=None):
        '''
        Waits (up to timeout seconds) for playback to finish
        '''
        self.done_event.wait(timeout)

    def get_set_modifiers(self, modifiers):
        expr = "frame_count=\'[0-9]+"
        if re.search(expr, modifiers, re.IGNORECASE):
            try:
                frames = re.search(expr, modifiers, re.IGNORECASE).group(0)
                self.decode_n_frames = int(re.search('[0-9]+', frames).group(0))
            except:
                self.decode_n_frames = 0
                pass
        expr = "rotation=\'[0-9]+"
        if re.search(expr, modifiers, re.IGNORECASE):
            try:
                rotation = re.search(expr, modifiers, re.IGNORECASE).group(0)
                self.rotate = int(re.search('[0-9]+', rotation).group(0))
            except:
                self.rotate = 0
                pass
        expr = "scaling=\'[0-9]+x[0-9]+"
        if re.search(expr, modifiers, re.IGNORECASE):
            try:
                scaling = re.search(expr, modifiers, re.IGNORECASE).group(0)
                self.x_scale = '0x' + str(re.search('[0-9]+x', scaling).group(0).replace('x', ''))
                self.y_scale = '0x' + str(re.search('x[0-9]+', scaling).group(0).replace('x', ''))
            except:
                self.x_scale = 0
                self.y_scale = 0
                pass
        expr = 'pp=[0-9]+'
        if re.search(expr, modifiers, re.IGNORECASE):
            try:
                pp = re.search(expr, modifiers, re.IGNORECASE).group(0)
                self.pp_count = int(re.search('[0-9]+', pp).group(0))
            except:
                self.pp_count = 0
                pass


def main(args):
    if len(args) <= 2:
        sys.stderr.write("\n\n usage: stream_path = <path>, output_path = <path>, sink_type = <file/frame_crc>, modifiers = <pp='10', seek='100', rotation='90'> seed='12345'\n\n")
        return -1
    else:
        log.info('Here In player main')
        log.info(args)
        # log.info(args[4])
        # other_opts = ast.literal_eval(args[4])
        pp_count = 0
        seek_count = 0
        seed_count = 0
        if 'pp=' in args[4]:
            pp = re.search('pp=[0-9]+', args[4], re.IGNORECASE).group(0)
            log.info(pp)
            pp_count = int(re.search('[0-9]+', pp).group(0))
            log.info('PP_count = %d' % pp_count)
        if 'seek=' in args[4]:
            seek = re.search('seek=[0-9]+', args[4], re.IGNORECASE).group(0)
            log.info(seek)
            seek_count = int(re.search('[0-9]+', seek).group(0))
            log.info('Seek_count = %d' % seek_count)
        if 'seed=' in args[4]:
            seed = re.search('seed=[0-9]+', args[4], re.IGNORECASE).group(0)
            log.info(seed)
            seed_count = int(re.search('[0-9]+', seed).group(0))
            log.info('seed_count = %d' % seed_count)

        # Get the total duration
        if pp_count or seek_count:
            p = VPlayer(args[1], args[2], 'fake', args[4])
            p.get_total_time()
            p.stop()
            total_duration = p.total_duration
            log.info('Inside main total time = %d' % total_duration)
            if not total_duration:
                log.info('Play-Pause Skipped since total duration is not received.')

        # Call Player as per requirement
        p = VPlayer(args[1], args[2], args[3], args[4])
        if pp_count and p.total_duration:
            log.info('play-pause called')
            p.play_pause(int(pp_count), total_duration, seed_count)
        elif seek_count and p.total_duration:
            log.info('multi-seek called')
            p.multi_seek(int(seek_count), total_duration, seed_count)
        else:
            log.info('play called')
            p.play()

        #Look for exit flag till then run mainloop
        while p.exitFlag != 'killed':
            log.info('Running mainloop')
            p.mainloop.run()
        return 0

if __name__ == '__main__':
    log.info('PYGST PLAYER MAIN')
    main(sys.argv)
    log.info('Done!')
