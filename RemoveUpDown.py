import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

# 根据设定的阈值和图片直方图，找出波峰，用于分隔字符
def find_waves(threshold, histogram):
    up_point = -1  # 上升点
    is_peak = False
    if histogram[0] > threshold:
        up_point = 0
        is_peak = True
    wave_peaks = []
    for i, x in enumerate(histogram):
        if is_peak and x < threshold:
            if i - up_point > 2:
                is_peak = False
                wave_peaks.append((up_point, i))
        elif not is_peak and x >= threshold:
            is_peak = True
            up_point = i
    if is_peak and up_point != -1 and i - up_point > 4:
        wave_peaks.append((up_point, i))
    return wave_peaks


def remove_plate_upanddown_border(card_img):
    """
    这个函数将截取到的车牌照片转化为灰度图，然后去除车牌的上下无用的边缘部分，确定上下边框
    输入： card_img是从原始图片中分割出的车牌照片
    输出: 在高度上缩小后的字符二值图片
    """
    plate_Arr = card_img
    plate_gray_Arr = cv.cvtColor(plate_Arr, cv.COLOR_BGR2GRAY)
    ret, plate_binary_img = cv.threshold(plate_gray_Arr, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)#二值化
    row_histogram = np.sum(plate_binary_img, axis=1)  # 数组的每一行求和
    row_min = np.min(row_histogram)
    row_average = np.sum(row_histogram) / plate_binary_img.shape[0]
    row_threshold = (row_min + row_average) / 2
    wave_peaks = find_waves(row_threshold, row_histogram)
    # 接下来挑选跨度最大的波峰
    wave_span = 0.0
    #print(wave_peaks)
    for wave_peak in wave_peaks:
        span = wave_peak[1] - wave_peak[0]
        if span > wave_span:
            wave_span = span
            selected_wave = wave_peak
    #print(selected_wave)
    plate_binary_img = plate_binary_img[selected_wave[0]:selected_wave[1], :]
    ##################################################
    # 测试用
    # print( row_histogram )
    # fig = plt.figure()
    # plt.hist( row_histogram )
    # plt.show()
    # # # 其中row_histogram是一个列表，列表当中的每一个元素是车牌二值图像每一行的灰度值之和，列表的长度等于二值图像的高度
    # # 认为在高度方向，跨度最大的波峰为车牌区域
    # cv2.imshow("plate_gray_Arr", plate_binary_img[selected_wave[0]:selected_wave[1], :])
    ##################################################

    return plate_binary_img

if __name__=='__main__':
    img = cv.imdecode(np.fromfile("E:/plate_area/川QK9777.jpg", dtype=np.uint8), -1)
    cv.imshow("raw",img)
    thresh=remove_plate_upanddown_border(img)
    cv.imshow("aferremmove", thresh)
    cv.waitKey(0)



