import dicom
import cv2
import os
import tifffile
import numpy as np
from config import *

def canny(img):
    edges = cv2.Canny(img, 0, 50)
    for idx, e in enumerate(edges):
        pos = np.where(e>0)[0]
        e[pos[:2]]=0
        e[pos[-2:]]=0
        edges[idx] = e
    kernel = np.ones((5,5),np.uint8)
    closing = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    return closing

def find_contours(img):
    ret,thresh = cv2.threshold(img,20,255,0)
    thresh= cv2.bitwise_not(thresh)

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    shaped_img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

    for i in range(len(contours)):

        if hierarchy[0][i][3] == -1:        
            cv2.drawContours(shaped_img, contours, i, (0, 255, 0), 2)
        else:
            cv2.drawContours(shaped_img, contours, i, (0, 255, 255), 2)
    return shape_image

def find_limit(c: np.array):
    y1, x1, y2, x2 = 0, 0, c.shape[0]-1, c.shape[1]-1
    for i in range(c.shape[0]):
        if c[i].max() > 0:
            y1 = i
            break
    for i in range(c.shape[0]-1, 0, -1):
        if c[i].max() > 0:
            y2 = i
            break
    for i in range(c.shape[1]):
        if c[:, i].max() > 0:
            x1 = i
            break
    for i in range(c.shape[1]-1, 0, -1):
        if c[:, i].max() > 0:
            x2 = i
            break
    return y1, x1, y2, x2

def onMouse(event, x, y, flag, params):
    wname = params['wname']
    img = params['img']
    points = params['points']
    if event == cv2.EVENT_MOUSEMOVE:
        img2 = np.copy(img)
        h, w = img2.shape[0], img2.shape[1]
        cv2.line(img2, (x, 0), (x, h - 1), (255, 0, 0))
        cv2.line(img2, (0, y), (w - 1, y), (255, 0, 0))
        cv2.imshow(wname, img2)
    elif event == cv2.EVENT_RBUTTONDOWN:
        if len(points) == 0:
            points.append((x, y))
        elif len(points) == 1:
            points.append((x, y))
            x1, x2 = min(points[0][0], points[1][0]), max(points[0][0], points[1][0])
            y1, y2 = min(points[0][1], points[1][1]), max(points[0][1], points[1][1])
            color = (255, 255, 255)
            cv2.line(img, (x1, y1), (x1, y2), color, 3)
            cv2.line(img, (x1, y1), (x2, y1), color, 3)
            cv2.line(img, (x2, y2), (x1, y2), color, 3)
            cv2.line(img, (x2, y2), (x2, y1), color, 3)
        elif len(points) == 2:
            x1, x2 = min(points[0][0], points[1][0]), max(points[0][0], points[1][0])
            y1, y2 = min(points[0][1], points[1][1]), max(points[0][1], points[1][1])
            template = pointout_to_template(params['idx'], x, y, x1, x2, y1, y2, image_start, image_start+image_length, dicom_file_path, template_file_path)
            new_wname = f"{params['idx']}_{x}_{y}"
            template = cv2.resize(template, (template.shape[1] // 2, template.shape[0] // 2))
            cv2.namedWindow(wname, cv2.WINDOW_NORMAL)
            cv2.imshow(new_wname,template)
    elif event == cv2.EVENT_LBUTTONDOWN:
        max_x, max_y = img.shape[1], img.shape[0]
        if params['idx'] < 0:
          pass 
        if x > max_x /2:
            params['idx'] += 1
        else:
            params['idx'] -= 1
        img = read_image(params['idx'])
        params['img'] = img
        params['points'] = []
        cv2.imshow(wname, img)

def pointout_to_template(index, x, y, x1, x2, y1, y2, first=0, last=100, dicom_file_path='', template_file_path=''):
    point_width = 30
    dicom_files = sorted(os.listdir(dicom_file_path))
    d = dicom.read_file(f'{dicom_file_path}/{dicom_files[index]}')
    dicom_img = d.pixel_array
    template_files = sorted(os.listdir(template_file_path))
    template_index = round((index - first) / (last - first) * len(template_files))
    template = tifffile.imread(f'{template_file_path}/{template_files[template_index]}')
    c = canny(template)
    ty1, tx1, ty2, tx2 = find_limit(c)
    _x, _y = round((x - x1) / (x2 - x1) * (tx2 - tx1) + tx1), round((y - y1) / (y2 - y1) * (ty2 - ty1) + ty1)
    template[_y - point_width:_y + point_width, _x - point_width:_x + point_width, 1] =1
    return template

def read_image(idx):
    d = dicom.read_file(f'{dicom_file_path}/{dicom_files[idx]}')
    img = d.pixel_array
    return shape_image(img)

def shape_image(img):
    x0 = img.min()
    x1 = img.max()
    y0 = 0
    y1 = 255.0
    i8 = ((img-x0)*((y1-y0)/(x1-x0)))+y0
    img = i8.astype(np.uint8)
    return img
