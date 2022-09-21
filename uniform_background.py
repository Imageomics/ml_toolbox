import os
from argparse import ArgumentParser

import numpy as np
from PIL import Image

def get_args():
    parser = ArgumentParser()
    parser.add_argument("--dataset", type=str, default="/local/scratch/datasets/butterflies")
    parser.add_argument("--output", type=str, default="/local/scratch/datasets/butterflies_norm")
    parser.add_argument("--background_color", type=str, nargs='+', action='append', default=[210,210,210])

    args = parser.parse_args()
    assert len(args.background_color) == 3, "Must provide an RGB color of length 3 for each channel."
    assert args.dataset is not None, "Must provide a dataset"

    return args

def dist(a, b):
    return np.sqrt(((a - b) ** 2).sum())

def region_growing_mask(path, thresh=3):
    """
    NOTE: the 'visited' variable contain the starting points for the region growing algorithm.
          Currently, the four corners are used (for most butterfly image from Cuthil this is okay).
          Modify the variable as needed.

          the 'thresh' variable may also need to be adjusted depending on the data.

          Manual inspection may be needed as this algorithm may 'bleed' into the actual image (into the butterfly).
          The algorithm may also underperform and still leave sections of the image background the same. This is likely
          due to cutoffs such as the butterfly antennae.
    """
    img = np.array(Image.open(path))
    h, w = img.shape[:2]
    visited = ["0_0", f"0_{w-1}", f"{h-1}_{w-1}", f"{h-1}_0"] #! STARTING POINTS
    queue = [(0, 0, img[0, 0]), (0, w-1, img[0, w-1]), (h-1, w-1, img[h-1, w-1]), (h-1, 0, img[h-1, 0])]
    background = np.ones_like(img[:, :, 0]).astype(np.uint8)
    background[0,0] = 0
    background[0,w-1] = 0
    background[h-1,w-1] = 0
    background[h-1,0] = 0
    i = 0

    def get_neighbor_points(row, col):
        points = []
        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                if x == 0 and y == 0: continue
                points.append((max(min(row + y, img.shape[0]-1), 0), max(min(col + x, img.shape[1]-1), 0)))
        return points
    while len(queue) > 0:
        i += 1
        row, col, color = queue.pop(0)
        points = get_neighbor_points(row, col)
        for y, x in points:
            c = img[y, x]
            d = dist(color, c)
            if d < thresh:
                background[y, x] = 0
                if f"{y}_{x}" not in visited:
                    queue.append((y, x, c))
                    visited.append(f"{y}_{x}")

    return background

def uniform_background(dataset, output, background_color=[210, 210, 210]):
    os.makedirs(output, exist_ok=False)
    for root, _, files in os.walk(dataset):
        for f in files:
            path = os.path.join(root, f)
            start_img = Image.open(path)
            mask = region_growing_mask(path)
            new_image = np.array(start_img)
            new_image[mask == 0] = np.array(background_color)

if __name__ == "__main__":
    args = get_args()
    uniform_background(args.dataset, args.output, args.background_color)

