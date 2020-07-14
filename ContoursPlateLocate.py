# -*- coding:utf-8 -*-
import cv2 as cv
import numpy as np
from BluePlateLocate import *

MinArea=1500

def plate_zone(img):
    ret=False
    # 读取图片
    rawImage = img
    # 高斯模糊，将图片平滑化，去掉干扰的噪声
    image = cv.GaussianBlur(rawImage, (3, 3), 0)
    # 图片灰度化
    image = cv.cvtColor(image, cv.COLOR_RGB2GRAY)
    # Sobel算子（XY方向）
    Sobel_x = cv.Sobel(image, cv.CV_16S, 1, 0)
    Sobel_y = cv.Sobel(image, cv.CV_16S, 0, 1)
    absX = cv.convertScaleAbs(Sobel_x)  # 转回uint8
    absY = cv.convertScaleAbs(Sobel_y)
    dst = cv.addWeighted(absX, 0.8, absY, 0.2, 0)
    image = dst
    # 二值化：图像的二值化，就是将图像上的像素点的灰度值设置为0或255,图像呈现出明显的只有黑和白
    ret, image = cv.threshold(image, 0, 255, cv.THRESH_OTSU)
    # 闭操作：闭操作可以将目标区域连成一个整体，便于后续轮廓的提取。
    kernelX = cv.getStructuringElement(cv.MORPH_RECT, (17, 5))
    image = cv.morphologyEx(image, cv.MORPH_CLOSE, kernelX)
    # 膨胀腐蚀(形态学处理)
    kernelX = cv.getStructuringElement(cv.MORPH_RECT, (20, 1))
    kernelY = cv.getStructuringElement(cv.MORPH_RECT, (1, 19))
    image = cv.dilate(image, kernelX)
    image = cv.erode(image, kernelX)
    image = cv.erode(image, kernelY)
    image = cv.dilate(image, kernelY)
    # 平滑处理，中值滤波
    image = cv.medianBlur(image, 15)
    # 查找轮廓
    contours, w1 = cv.findContours(image, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    points=contours[0]
    for item in contours:
        rect = cv.boundingRect(item)
        x = rect[0]
        y = rect[1]
        width = rect[2]
        height = rect[3]
        aspect_ratio = width / height
        area=cv.contourArea(item)
        #print(aspect_ratio)
        plate=cv.imread("E:/ui_source/null_img.jpg")
        if aspect_ratio > 2 and aspect_ratio < 5 and area>MinArea:
            # 裁剪区域图片
            points=item
            #plate = rawImage[y:y + height, x:x + width]
            ret=True
            break
    if ret :
        if IsNeedFix(points):  # 是否需要调整
            vertices, rect = findVertices(points)
            point_set_0, point_set_1, new_box = tiltCorrection(vertices, rect)
            #img_draw = cv2.drawContours(img.copy(), [new_box], -1, (0,0,255), 3)
            plate = transform(img, point_set_0, point_set_1)
        else:
            plate = rec2img(points, img)
    return ret,plate
