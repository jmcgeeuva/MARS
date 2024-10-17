'''
For HMDB51 and UCF101 datasets:

Code extracts frames from video at a rate of 25fps and scaling the
larger dimension of the frame is scaled to 256 pixels.
After extraction of all frames write a "done" file to signify proper completion
of frame extraction.

Usage:
  python extract_frames.py video_dir frame_dir
  
  video_dir => path of video files
  frame_dir => path of extracted jpg frames

'''

import sys, os, pdb
import numpy as np
import subprocess
from tqdm import tqdm
import threading
from ffmpeg import FFmpeg

def ffmpeg(iteration, input_file, num_frames, resize_str,outdir):
  output_pattern = os.path.join(outdir, f'{iteration:05}.jpg')
  # Set up FFmpeg command using ffmpy
  ffmpeg = (
    FFmpeg()
    .option("y")
    .input(input_file)
    .output(
      output_pattern,
      vf=f"crop=2:ih:{iteration}:0, select=not(mod(n\\,1)), tile={num_frames}x1, scale={resize_str}"
    )
  )

  ffmpeg.execute()
  # os.system(f'ffmpeg -i "{input_file}" -vf "crop=2:ih:{iteration}:0, select=not(mod(n\\,1)), tile={num_frames}x1, scale={resize_str}" "{output_pattern}" -y > /dev/null 2>&1')

def extract(vid_dir, frame_dir, start, end, redo=False):
  class_list = sorted(os.listdir(vid_dir))[start:end]

  print("Classes =", class_list)
  
  for ic,cls in enumerate(class_list): 
    vlist = sorted(os.listdir(vid_dir + cls))
    print(f'Processing {len(vlist)} videos')
    # print("")
    # print(ic+1, len(class_list), cls, len(vlist))
    # print("")
    for v in vlist:
      outdir = os.path.join(frame_dir, cls, v[:-4])

      # Checking if frames already extracted
      if os.path.isfile( os.path.join(outdir, 'done') ) and not redo: continue
      try:  
        os.system('mkdir -p "%s"'%(outdir))
        # check if horizontal or vertical scaling factor
        o = subprocess.check_output('ffprobe -v error -show_entries stream=width,height -of default=noprint_wrappers=1 "%s"'%(os.path.join(vid_dir, cls, v)), shell=True).decode('utf-8')
        lines = o.splitlines()
        width = int(lines[0].split('=')[1])
        height = int(lines[1].split('=')[1])
        
        output = subprocess.check_output(f'ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets,r_frame_rate -of csv=p=0 "{os.path.join(vid_dir, cls, v)}"', shell=True).decode('utf-8')
        output = output.split(',')
        frame_rate = int(output[0].split('/')[0])
        num_frames = int(output[1].replace('\n', '').replace(',', ''))

        # 409 > 240, 52< 240
        resize_str = '-1:256' if num_frames>height else '256:-1'
        # extract frames
        # Define the paths and parameters
        input_file = os.path.join(vid_dir, cls, v)
        # resize_str = "320:240"  # Example resize string, modify as needed
        
        threads = list()
        for iteration in tqdm(range(width)):
          x = threading.Thread(target=ffmpeg, args=(iteration, input_file, num_frames, resize_str,outdir,))
          threads.append(x)
          x.start()

        for thread in threads:
          thread.join()

        os.system('touch "%s"'%(os.path.join(outdir, 'done') ))
      except Exception as e:
        print(f"ERROR {cls}, {v}, {repr(e)}")


if __name__ == '__main__':
  vid_dir   = sys.argv[1]
  frame_dir = sys.argv[2]
  start     = int(sys.argv[3])
  end       = int(sys.argv[4])
  extract(vid_dir, frame_dir, start, end, redo=True)