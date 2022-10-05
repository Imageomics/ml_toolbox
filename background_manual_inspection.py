import os
import time

import numpy as np
import tkinter as tk
from argparse import ArgumentParser

from PIL import Image, ImageTk
from uniform_background import region_growing_mask

BACKGROUND_COLOR = [210, 210, 210]

"""
Click on the larger image after it has been loaded to remove the background. Continue
to click on other regions afterwards. The image will only save if you click the 'Save Image'
button. If you want to redo, just load the image again.
"""

def get_args():
    parser = ArgumentParser()
    parser.add_argument('--data_dir', type=str, default='C:\\Users\\David\\Downloads\\split')
    return parser.parse_args()

class InspectionApp:
    def __init__(self, paths):
        self.paths = paths
        self.panel = None
        self.panel_larger = None
        self.cur_path = None
        self.cur_img = None
        self.root = tk.Tk()
        self.root.title("Butterfly Background Inspection")
        self.root.geometry("800x800")
        self.lb = self.create_listbox()
        self.status_lbl = self.create_status_lbl()
        self.save_img_btn = self.create_save_img_btn()

    def create_status_lbl(self):
        status_lbl = tk.Label(self.root, text="No activity")
        status_lbl.pack()
        return status_lbl

    def run(self):
        self.root.mainloop()

    def create_listbox(self):
        lb = tk.Listbox(self.root, height=20)
        for i, path in enumerate(img_paths):
            lb.insert(i, path)
        lb.pack(fill='x')
        lb.bind('<<ListboxSelect>>', lambda x: self.load_img())
        return lb

    def create_save_img_btn(self):
        def save_img():
            self.cur_img.save(self.cur_path)
            self.status_lbl.config(text="Image Saved")

        btn = tk.Button(self.root, text="Save Image", command=save_img)
        btn.pack()

        return btn

    def remove_background(self, evt):
        self.status_lbl.config(text="Removing background")
        mask = region_growing_mask(self.cur_path, query_points=[f"{evt.y//4}_{evt.x//4}"])
        new_image = np.array(self.cur_img)
        new_image[mask == 0] = np.array(BACKGROUND_COLOR)
        if self.panel is not None:
            self.panel.destroy()
            self.panel_larger.destroy()
        self.cur_img = Image.fromarray(new_image)
        img_pi = ImageTk.PhotoImage(self.cur_img)
        h, w = np.array(self.cur_img).shape[:2]
        img_pi_larger = ImageTk.PhotoImage(self.cur_img.resize((w*4, h*4), Image.ANTIALIAS))
        self.panel = tk.Label(self.root, image = img_pi)
        self.panel_larger = tk.Label(self.root, image = img_pi_larger)
        self.panel.image = img_pi
        self.panel_larger.image = img_pi_larger
        self.panel_larger.bind('<Button-1>', lambda x: self.remove_background(x))
        self.panel.pack()
        self.panel_larger.pack()
        self.status_lbl.config(text="Background removed")

    def load_img(self):
        self.status_lbl.config(text="Loading Image")
        if len(self.lb.curselection()) == 0:
            self.status_lbl.config(text="Failed to load image")
            return
        self.cur_path = self.lb.get(self.lb.curselection()[0])
        self.cur_img = Image.open(self.cur_path)
        img_pi = ImageTk.PhotoImage(self.cur_img)
        if self.panel is not None:
            self.panel.destroy()
            self.panel_larger.destroy()
        h, w = np.array(self.cur_img).shape[:2]
        img_pi_larger = ImageTk.PhotoImage(self.cur_img.resize((w*4, h*4), Image.ANTIALIAS))
        self.panel = tk.Label(self.root, image = img_pi)
        self.panel_larger = tk.Label(self.root, image = img_pi_larger)
        self.panel.image = img_pi
        self.panel_larger.image = img_pi_larger
        self.panel_larger.bind('<Button-1>', lambda x: self.remove_background(x))
        self.panel.pack()
        self.panel_larger.pack()
        self.status_lbl.config(text=f"Image Loaded: {self.cur_path}")

if __name__ == "__main__":
    args = get_args()
    img_paths = []
    for root, _, files in os.walk(args.data_dir):
        for f in files:
            if f.split(".")[-1].lower() not in ['tif', 'png', 'jpg', 'jpeg']: continue
            img_paths.append(os.path.join(root, f))

    app = InspectionApp(img_paths)
    app.run()
    
    