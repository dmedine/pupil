
import sys; sys.path.append('liblsl-Python')  # make sure that pylsl is found (note: in a normal program you would bundle pylsl with the program)
from glfw import *
from plugin import Plugin

from ctypes import c_int,c_bool,c_float
import atb
from gl_utils import adjust_gl_view,clear_gl_screen,basic_gl_setup

import random
from pylsl import StreamInfo, StreamOutlet, local_clock

# window calbacks
def on_resize(window,w, h):
    active_window = glfwGetCurrentContext()
    glfwMakeContextCurrent(window)
    adjust_gl_view(w,h,window)
    glfwMakeContextCurrent(active_window)

def outlet_setup(self):
    self.stream_on = False
    ruid = str(random.randint(0,9)) + str(random.randint(0,9)) +str(random.randint(0,9)) + str(random.randint(0,9))

    info = StreamInfo('PupilPro', 'EyeTracking', 7, float(self.requested_fps.value), 'float32','world_'+ruid)
    info.desc().append_child_value("manufacturer","Pupil Labs")
    channels = info.desc().append_child("channels")
    for c in ["Confidence", "GazeX", "GazeY", "pupil_size","PupilX","PupilY", "PupilProTimestamp"]:
        channels.append_child("channel").append_child_value("name",c)
        
    self.outlet = StreamOutlet(info, 32, 360)



class LSL_Plugin(Plugin):

    def __init__(self,g_pool,atb_pos=(0,0)):
        Plugin.__init__(self)

      
        atb_label = "LSL Controls"
        # Creating an ATB Bar.
        self._bar = atb.Bar(name =self.__class__.__name__, label=atb_label,
            help="ref detection parameters", color=(50, 50, 50), alpha=100,
            text='light', position=atb_pos,refresh=.3, size=(300, 100))
        self.requested_fps = c_float(24.0)
        self.stream_on = c_bool(False)
        outlet_setup(self)
        self._bar.add_var("Requested fps", self.requested_fps, step=1, readonly=False, help="Set the expected frame rate of the world camera here.")
        self._bar.add_button("reset stream info", outlet_setup, help="You must reset the stream parameters if you have changed the sampling rate.")
        self._bar.add_button("start stream", self.toggle_stream, help="Start/stop the lsl stream.")




    
    def toggle_stream(self):
        if self.stream_on == False :
            outlet_setup(self)
            self.stream_on = True
        else :
            self.stream_on = False
            
    def update(self,frame,recent_pupil_positions,events):

        if self.stream_on == True:
            #print "Streaming...\n"
            for p in recent_pupil_positions:
                sample = []
                #print p
                sample[0] = p['confidence']  
                sample[1] = p['norm_gaze'][0]
                sample[2] = p['norm_gaze'][1]
                sample[3] = p['apparent_pupil_size']
                sample[4] = p['norm_pupil'][0]
                sample[5] = p['norm_pupil'][1]
                sample[6] = p['timestamp']
                #print sample
                stamp = local_clock()
                self.outlet.push_sample(sample, stamp)


    def cleanup(self):
        """gets called when the plugin get terminated.
        This happends either volunatily or forced.
        if you have an atb bar or glfw window destroy it here.
        """
        self._bar.destroy()
