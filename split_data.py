import os
from shlex import split
import shutil

from argparse import ArgumentParser

from parse_butterfly_labels import parse_butterfly_labels

def split_butterfly_data(dset_path: str, lbl_path: str, outdir_path: str, view: str = 'D', ratio: float = 0.8) -> None:
    """
    Input:
        dset_path: path to dataset root
        lbl_path: path to labels
        outdir_path: path where split data will be saved
        view: the view of the butterfly that will be considered
        ratio: the split ratio b/w train and test that will be used. Represents % going into the training set

        This function will split the butterfly dataset into a training and testing set based on the ratio given.
        The dataset will be filtered based on the butterfly view givens

        WARNING: if a subspecies only has one image, it will be ignore in the split and not includeds
    """
    
    labels = parse_butterfly_labels(lbl_path, use_specimen_as_key=True)
    
    paths = {}
    for root, _, files in os.walk(dset_path):
        for f in files:
            # Ensure we are only working with image files
            if f.split(".")[-1].lower() not in ["png", "tif", "jpg", "jpeg"]: continue
            # Ensure we are only working with the butterfly view we want
            specimen_id, butterfly_view = f.split("_")[:2]
            if butterfly_view.lower() != view.lower(): continue

            info = labels[specimen_id]
            subspecies = f"{info['species']}_{info['subspecies']}"
            if subspecies not in paths:
                paths[subspecies] = []
            paths[subspecies].append(os.path.join(root, f))

    # Split data
    os.makedirs(outdir_path, exist_ok=True)
    for sub in paths:
        if len(paths[sub]) < 2: continue # Skip subspecies with only one image
        split_idx = int(len(paths[sub]) * ratio)
        if split_idx == 0:
            split_idx += 1 # Need atleast one image
        train_paths = paths[sub][:split_idx]
        test_paths = paths[sub][split_idx:]

        # Copy to train dir
        copy_dir = os.path.join(outdir_path, "train", sub)
        os.makedirs(copy_dir, exist_ok=True)
        for path in train_paths:
            fname = path.split(os.path.sep)[-1]
            shutil.copyfile(path, os.path.join(copy_dir, fname))

        # Copy to test dir
        copy_dir = os.path.join(outdir_path, "test", sub)
        os.makedirs(copy_dir, exist_ok=True)
        for path in test_paths:
            fname = path.split(os.path.sep)[-1]
            shutil.copyfile(path, os.path.join(copy_dir, fname))
            



if __name__ == "__main__":
    """
    Use main for testing
    """
    parser = ArgumentParser()
    parser.add_argument('--path_to_root', type=str, default='data/norm_background')
    parser.add_argument('--path_to_labels', type=str, default='data/Cuthill_GoldStandard/Hoyal_Cuthill_GoldStandard_metadata_cleaned.csv')
    parser.add_argument('--outdir', type=str, default='data/split')
    parser.add_argument('--view', type=str, default='D')
    parser.add_argument('--ratio', type=float, default=0.8)
    args = parser.parse_args()

    split_butterfly_data(args.path_to_root, args.path_to_labels, args.outdir, args.view, args.ratio)
