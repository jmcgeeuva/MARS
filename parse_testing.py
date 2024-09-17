import sys
import re
import matplotlib.pyplot as plt
import numpy
from sklearn import metrics
import os
import glob
import csv

def get_classes(file_path):
    classes = []
    with open(file_path, 'r') as f:
        for line in f:
            label = line.split(' ')[1]
            classes.append(label.strip('\n'))
    return classes

def save_confusion_matrix_csv(confusion_matrix, classes, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        writer.writerow([''] + classes)
        # Write data
        for i, row in enumerate(confusion_matrix):
            writer.writerow([classes[i]] + list(row))

annotation_path = "/scratch/tkg5kq/datasets/ucf-101/UCF101TrainTestSplits-RecognitionTask/ucfTrainTestlist/"
ucf_classes = get_classes(os.path.join(annotation_path, 'classInd.txt'))

filename = sys.argv[1]
actual = []
predicted = []
with open(filename, 'r') as f:
    for line in f:
        if "Video" in line:
            pattern = r'top1 = (\d+)\s+true = (\d+)'
            match = re.search(pattern, line)
    
            if match:
                top1 = int(match.group(1))
                true = int(match.group(2))
                actual.append(true)
                predicted.append(top1)

confusion_matrix = metrics.confusion_matrix(actual, predicted)

save_confusion_matrix_csv(confusion_matrix, ucf_classes, "confusion_matrix2.csv")

cm_display = metrics.ConfusionMatrixDisplay(
                    confusion_matrix = confusion_matrix, 
                    display_labels = ucf_classes
             )

cm_display.plot()
plt.xticks(rotation=45)
plt.yticks(rotation=45)
plt.savefig("confusion.png")