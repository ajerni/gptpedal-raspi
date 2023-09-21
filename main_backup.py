from pyo import *
from aifunctions import generateEffect, convert_audio_to_text

from fxchain import fxChain
import ast
from presets import presets

import sys, tty, termios

from eink_menu import makeText

import subprocess
import time
import threading


def getGPTeffect(q):
    sel_dict_string = generateEffect(q)
    sel_dict = ast.literal_eval(sel_dict_string)
    print(sel_dict)
    startServer(sel_dict)


def getPresetEffect(p):
    sel_dict = p
    print(sel_dict)
    startServer(sel_dict)

def startServer(sel_dict):
    s = Server()

    output_devices = pa_get_output_devices() # i.e. (['vc4-hdmi-1: MAI PCM i2s-hifi-0 (hw:2,0)', 'Scarlett 2i2 USB: Audio (hw:3,0)', 'pulse', 'default'], [1, 2, 3, 4])
    print(output_devices)
    soundcard = extract_scarlett_index(output_devices)
    print(soundcard)
    s.setOutputDevice(soundcard) #pa_list_devices() / pa_get_output_devices()/ 0 or 1 or 2 = Scarlett 2i2 USB
    #s.setOutputDevice(2) 
    s.boot()
    s.start()
    startFxChain(sel_dict, s)


def startFxChain(sel_dict, server):
    input = Input()
    output = fxChain(
        input,
        sel_dict,
    )

    stereo = output.mix(2).out()

    server.gui(locals())

def read_ch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def get_usb_pnp_device(devices): # extracts "hw:x,y" for 'USB PnP Sound Device'
    for device in devices[0]:
        if 'USB PnP Sound Device' in device:
            return device.split('(')[-1].split(')')[0].strip()
    return None

def extract_scarlett_index(t):
    for i, element in enumerate(t[0]):
        if "Scarlett" in element:
            return t[1][i]
    return None

if __name__ == "__main__":

    done = makeText("1 - Steroverb", "2 - Chorus", "g - GPT", "x - Exit")
    print(done)

    def read_ch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    while True:
        ch = read_ch()
        if ch == 'x':
            break
        if ch == "1":
            p = presets.STEEREOVERB
            thread = threading.Thread(target=getPresetEffect, args=(p,))
            thread.daemon = True
            thread.start()
            
            
            #p = presets.STEEREOVERB
            #getPresetEffect(p)
        if ch == "2":
            p = presets.CHORUS
            getPresetEffect(p)
        if ch == "g":
            print("recording")
            input_devices = pa_get_input_devices()
            usb_mic = get_usb_pnp_device(input_devices)
            record = f'arecord -D {usb_mic} -d 4 -f S16_LE -r 44100 my_audio.wav'
            #record = 'arecord -D hw:3,0 -d 4 -f S16_LE -r 44100 my_audio.wav'
            #record = 'arecord -d 4 my_audio.wav'
            p = subprocess.Popen(record, shell=True)
            time.sleep(5)
            p.kill()
            print("done recording")
            audio_input = open("my_audio.wav", "rb")
            q = convert_audio_to_text(audio_input)
            print(q)
            getGPTeffect(q)
        print("key is: " + ch)
  
    # filedescriptors = termios.tcgetattr(sys.stdin)
    # tty.setcbreak(sys.stdin)
    # x = 0
    # while 1:    
    #     x=sys.stdin.read(1)[0]
    #     print("You pressed", x)
    #     if x == "1":
    #         p = presets.STEEREOVERB
    #         t = threading.Thread(name='preset process', target=getPresetEffect(p))
    #         t.setDaemon(True)
    #         t.start()
    #         #getPresetEffect(p)
    #     if x == "2":
    #         p = presets.CHORUS
    #         getPresetEffect(p)
    #     if x == "g":
    #         print("recording")
    #         input_devices = pa_get_input_devices()
    #         usb_mic = get_usb_pnp_device(input_devices)
    #         record = f'arecord -D {usb_mic} -d 4 -f S16_LE -r 44100 my_audio.wav'
    #         #record = 'arecord -D hw:3,0 -d 4 -f S16_LE -r 44100 my_audio.wav'
    #         #record = 'arecord -d 4 my_audio.wav'
    #         p = subprocess.Popen(record, shell=True)
    #         time.sleep(5)
    #         p.kill()
    #         print("done recording")
    #         audio_input = open("my_audio.wav", "rb")
    #         q = convert_audio_to_text(audio_input)
    #         print(q)
    #         getGPTeffect(q)
    #     if x == "x":
    #         print("make exit command")
    #         raise KeyboardInterrupt
    # termios.tcsetattr(sys.stdin, termios.TCSADRAIN, filedescriptors)

  