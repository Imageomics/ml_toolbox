import math

from PIL import Image
import numpy as np
import cv2 as cv

from uniform_background import region_growing_mask

def inverse(im):
    bg = im == 0
    fg = im == 255

    im[bg] = 255
    im[fg] = 0

    return im

if __name__ == "__main__":
    img_path = "example.jpg"
    org_im = Image.open(img_path)
    org_im_np = np.array(org_im)
    org_height, org_width, _ = org_im_np.shape
    org_im.resize((128, 128)).save("example_128x128.png")
    points = ["0_0", "0_127", "80_0", "80_127"]

    mask = region_growing_mask("example_128x128.png", thresh=6, query_points=points)

    Image.fromarray((mask*255)).resize((org_width, org_height)).save("connected_components/full_mask.png")

    analysis = cv.connectedComponentsWithStats(mask, 4, cv.CV_32S)

    (totalLabels, label_ids, values, centroid) = analysis

    bb_max_area_thresh = 3000
    px_min_area_thresh = 50
    
    filtered = []

    for i in range(1, totalLabels):
        area = values[i, cv.CC_STAT_AREA]
        top_y = values[i, cv.CC_STAT_TOP]
        left_x = values[i, cv.CC_STAT_LEFT]
        width = values[i, cv.CC_STAT_WIDTH]
        height = values[i, cv.CC_STAT_HEIGHT]
        x_center = centroid[i][0]
        y_center = centroid[i][1]

        bb_area = width * height

        if area < px_min_area_thresh: continue
        if bb_area > bb_max_area_thresh: continue


        component_mask = label_ids == i
        component_mask = np.zeros_like(mask)
        component_mask[label_ids == i] = 255

        filtered.append([component_mask, y_center, x_center, area])

    assert len(filtered) == 7, "Need to have 7 components"

    filtered = sorted(filtered, key=lambda x: x[1])

    to_save = []

    if filtered[0][2] < filtered[1][2]:
        to_save.append(["upper_left_wing"] + filtered[0])
        to_save.append(["upper_right_wing"] + filtered[1])
    else:
        to_save.append(["upper_left_wing"] + filtered[1])
        to_save.append(["upper_right_wing"] + filtered[0])
    
    if filtered[2][2] < filtered[3][2]:
        to_save.append(["lower_left_wing"] + filtered[2])
        to_save.append(["lower_right_wing"] + filtered[3])
    else:
        to_save.append(["lower_left_wing"] + filtered[3])
        to_save.append(["lower_right_wing"] + filtered[2])

    filtered = filtered[4:]
    filtered = sorted(filtered, key=lambda x: x[2])

    to_save.append(["measure"] + filtered[0])
    to_save.append(["label"] + filtered[1])
    to_save.append(["dish"] + filtered[2])

    for (name, mask, y, x, area) in to_save:
        mask_resize = Image.fromarray(np.array(mask).astype(np.uint8)).resize((org_width, org_height))
        mask_resize.save(f"connected_components/{name}_mask.png")
        mask_resize = np.array(mask_resize)
        extracted_part = np.ones_like(org_im_np) * 255
        extracted_part[mask_resize == 255] = org_im_np[mask_resize == 255]
        Image.fromarray(extracted_part).save(f"connected_components/{name}_part.png")

