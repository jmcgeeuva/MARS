import os
import numpy as np
import shutil
from PIL import Image
import matplotlib.pyplot as plt
import threading
import sys

from tqdm import tqdm

def prune_videos(video_list, input_label_dir, pruned_label_dir, alpha):

    for video in tqdm(sorted(video_list)):
        # print(f'\t{video}')
        input_video_dir = os.path.join(input_label_dir, video)
        pruned_video_dir = os.path.join(pruned_label_dir, video)
        os.makedirs(pruned_video_dir, exist_ok=True)
    
        file_variances = {}
        ordered_input_list = sorted(os.listdir(input_video_dir))
        remove_amount = int(len(ordered_input_list)*alpha)
        copy_list = ordered_input_list[remove_amount//2:len(ordered_input_list)-(remove_amount//2)]
        # Copy videos into a folder with the same label name 
        for filename in copy_list:
            source = os.path.join(input_video_dir, filename)
            destination = os.path.join(pruned_video_dir, filename)
            shutil.copy(source, destination)

def prune(input_directory, pruned_directory, start, end, alpha=.3):
    class_list = sorted(os.listdir(input_directory))[start:end]

    os.makedirs(os.path.dirname(pruned_directory), exist_ok=True)
    label_list = [ name for name in sorted(os.listdir(input_directory)) if os.path.isdir(os.path.join(input_directory, name)) ]
    threads = dict()
    for ic,label in enumerate(class_list):
        input_label_dir = os.path.join(input_directory, label)
        pruned_label_dir = os.path.join(pruned_directory, label)
        os.makedirs(pruned_label_dir, exist_ok=True)

        video_list = [ name for name in sorted(os.listdir(input_label_dir)) if os.path.isdir(os.path.join(input_label_dir, name)) ]
        x = threading.Thread(target=prune_videos, args=(video_list, input_label_dir, pruned_label_dir, alpha,))
        threads[label] = x
        x.start()

    for thread in threads:
        threads[thread].join()

if __name__ == '__main__':
    if len(sys.argv) < 4:
        exit(250)

    input_directory = str(sys.argv[1])
    pruned_directory = str(sys.argv[2])
    start     = int(sys.argv[3])
    end       = int(sys.argv[4])
    alpha = float(sys.argv[5])

    prune(input_directory, pruned_directory, start, end, alpha)