import os
import numpy as np
import shutil
from PIL import Image
import matplotlib.pyplot as plt
import threading
import sys

from tqdm import tqdm

# def calculate_image_variance(image_array, alpha=10):
#     variances = []
#     # col/alpha patches
#     for i in range(image_array.shape[1]//alpha):
#         col_variance = np.var(image_array[:, i*alpha:(i+1)*alpha])
#         # slice_variance = np.var(image_array)
#         # print(slice_variance)
#         variances.append(col_variance)

#     if image_array.shape[1] % alpha != 0:
#         col_variance = np.var(image_array[:, i*alpha:image_array.shape[1]])
#         variances.append(col_variance)

#     return variances

# def process_images(input_dir, pruned_dir, beta = 200):
#     """
#     Processes all images in the input directory. Moves highly correlated images to the pruned directory.
#     :param input_dir: directory containing images to process
#     :param pruned_dir: directory to move highly correlated images to
#     :param correlation_threshold: threshold above which correlations are considered high
#     """
#     # Create the pruned directory if it doesn't exist
#     os.makedirs(pruned_dir, exist_ok=True)
   
#     file_variances = {}
#     for filename in sorted(os.listdir(input_dir)):
#         if filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):  # Add other image formats if necessary
#             image_path = os.path.join(input_dir, filename)
#             # import pdb; pdb.set_trace()
#             image = Image.open(image_path).convert('L')  # Convert image to grayscale
#             image_array = np.array(image)
#             # correlations = compute_correlation(image_array)

#             variances = calculate_image_variance(image_array, 8)
#             file_variances[filename] = np.mean(variances)

#     beta = 200
#     variances_list = list(file_variances.values())
#     mean = np.mean(variances_list)
#     min_var = np.min(variances_list)
#     for filename in file_variances:
#         if file_variances[filename] < (((mean+min_var)/2) - beta):
#             shutil.move(os.path.join(input_dir, filename), os.path.join(pruned_dir, filename))
#             # print(f'Eliminate {os.path.join(input_dir, filename)}')

#     return file_variances

# def check_videos(input_label_dir, pruned_label_dir, BETA):
#     video_list = [ name for name in sorted(os.listdir(input_label_dir)) if os.path.isdir(os.path.join(input_label_dir, name)) ]
#     threads = {}
#     for video in sorted(video_list):
#         # print(f'\t{video}')
#         input_video_dir = os.path.join(input_label_dir, video)
#         pruned_video_dir = os.path.join(pruned_label_dir, video)
#         os.makedirs(pruned_video_dir, exist_ok=True)
#         # variances = process_images(input_video_dir, pruned_video_dir, BETA)
#         x = threading.Thread(target=process_images, args=(input_video_dir, pruned_video_dir, BETA,))
#         threads[video] = x
#         x.start()

#     for video_name in threads:
#         threads[video_name].join()
#         # print(f'\tDone checking {video_name}')

# def prune_math(input_directory, pruned_directory, BETA):
#     os.makedirs(os.path.dirname(pruned_directory), exist_ok=True)
#     label_list = [ name for name in sorted(os.listdir(input_directory)) if os.path.isdir(os.path.join(input_directory, name)) ]
#     threads = {}
#     thread_cnt = 0
#     for label in sorted(label_list):
#         # print(label)
#         input_label_dir = os.path.join(input_directory, label)
#         pruned_label_dir = os.path.join(pruned_directory, label)
#         os.makedirs(pruned_label_dir, exist_ok=True)
        
#         x = threading.Thread(target=check_videos, args=(input_label_dir, pruned_label_dir, BETA, ))
#         threads[label] = x
#         x.start()
#         thread_cnt += 1

#         if thread_cnt == 8:
#             for label_name in threads:
#                 threads[label_name].join()
#                 # print(f'Done checking {label_name}')

#             thread_cnt = 0

#     for labels in threads:
#         threads[label_name].join()
#         # print(f'Done checking {label_name}')

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
    class_list = sorted(os.listdir(vid_dir))[start:end]

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