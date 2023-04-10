import os
from argparse import ArgumentParser

import numpy as np
from PIL import Image

def get_args():
    parser = ArgumentParser()
    parser.add_argument("--dataset", type=str, default="data/Cuthill_GoldStandard")
    parser.add_argument("--output", type=str, default="data/norm_background")
    parser.add_argument("--background_color", type=str, nargs='+', action='append', default=[210,210,210])
    parser.add_argument("--img_path", type=str, default=None)

    args = parser.parse_args()
    assert len(args.background_color) == 3, "Must provide an RGB color of length 3 for each channel."
    assert args.dataset is not None, "Must provide a dataset"

    return args

def dist(a, b):
    return np.sqrt(((a - b) ** 2).sum())

def region_growing_mask(path, thresh=3, query_points=None):
    """
    NOTE: the 'visited'/'query_points' variable contain the starting points for the region growing algorithm.
          Currently, the four corners are used (for most butterfly image from Cuthil this is okay).
          Modify the variable as needed.

          the 'thresh' variable may also need to be adjusted depending on the data.

          Manual inspection may be needed as this algorithm may 'bleed' into the actual image (into the butterfly).
          The algorithm may also underperform and still leave sections of the image background the same. This is likely
          due to cutoffs such as the butterfly antennae.
    """
    img = np.array(Image.open(path))
    h, w = img.shape[:2]
    #! STARTING POINTS
    if query_points is None:
        visited = ["0_0", f"0_{w-1}", f"0_{w//2}", f"{h-1}_{w-1}", f"{h-1}_0"] 
    else:
        visited = query_points
    queue = []
    background = np.ones_like(img[:, :, 0]).astype(np.uint8)
    for p in visited:
        y, x = p.split("_")
        x = int(x)
        y = int(y)
        queue.append((y, x, img[y, x]))
        background[y,x] = 0
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

def make_image_background_uniform(path, outdir, background_color=[210, 210, 210]):
    start_img = Image.open(path)
    mask = region_growing_mask(path)
    new_image = np.array(start_img)
    new_image[mask == 0] = np.array(background_color)
    fname = path.split(os.path.sep)[-1]
    Image.fromarray(new_image).save(os.path.join(outdir, fname.split(".")[0] + '.png'))

def uniform_background(dataset, output, background_color=[210, 210, 210]):
    os.makedirs(output, exist_ok=False)
    for root, _, files in os.walk(dataset):
        for f in files:
            if f.split('.')[-1].lower() not in ["png", "tif", "jpeg", "jpg"]: continue
            path = os.path.join(root, f)
            make_image_background_uniform(path, output, background_color)

if __name__ == "__main__":
    args = get_args()
    if args.img_path is None:
        uniform_background(args.dataset, args.output, args.background_color)
    else:
        output_dir = os.path.sep.join(args.img_path.split(os.path.sep)[:-2])
        make_image_background_uniform(args.img_path, output_dir, args.background_color)

