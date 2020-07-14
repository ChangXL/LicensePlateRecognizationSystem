import cv2 as cv
import numpy as np

# 预处理
def imgProcess(img):
    # 统一规定大小
    img = cv.resize(img, (640,480))
    # 高斯模糊
    img_Gas = cv.GaussianBlur(img,(5,5),0)
    # RGB通道分离
    img_B = cv.split(img_Gas)[0]
    img_G = cv.split(img_Gas)[1]
    img_R = cv.split(img_Gas)[2]
    # 读取灰度图和HSV空间图
    img_gray = cv.cvtColor(img_Gas, cv.COLOR_BGR2GRAY)
    img_HSV = cv.cvtColor(img_Gas, cv.COLOR_BGR2HSV)
    return img, img_Gas, img_B, img_G, img_R, img_gray, img_HSV

# 初步颜色识别
def preIdentification(img_gray, img_HSV, img_B, img_R):
    for i in range(480):
        for j in range(640):
            # 普通蓝色车牌，同时排除透明反光物质的干扰
            if ((img_HSV[:, :, 0][i, j]-115)**2 < 15**2) and (img_B[i, j] > 70) and (img_R[i, j] < 40):
                img_gray[i, j] = 255
            else:
                img_gray[i, j] = 0
    # 定义核
    kernel_small = np.ones((3, 3))
    kernel_big = np.ones((7, 7))

    img_gray = cv.GaussianBlur(img_gray, (5, 5), 0) # 高斯平滑
    img_di = cv.dilate(img_gray, kernel_small, iterations=5) # 腐蚀5次
    img_close = cv.morphologyEx(img_di, cv.MORPH_CLOSE, kernel_big) # 闭操作
    img_close = cv.GaussianBlur(img_close, (5, 5), 0) # 高斯平滑
    #_, img_bin = cv.threshold(img_close, 120, 255, cv.THRESH_BINARY) # 二值化
    _, img_bin = cv.threshold(img_close, 0, 255, cv.THRESH_OTSU)  # 二值化
    #print(_)
    return img_bin

# 定位
def fixPosition(img_bin):
    ret=False
    # 检测所有外轮廓，只留矩形的四个顶点
    contours, _ = cv.findContours(img_bin, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    #形状及大小筛选校验
    det_x_max = 0
    det_y_max = 0
    num = 0
    for i in range(len(contours)):
        x_min = np.min(contours[i][ :, :, 0])
        x_max = np.max(contours[i][ :, :, 0])
        y_min = np.min(contours[i][ :, :, 1])
        y_max = np.max(contours[i][ :, :, 1])
        det_x = x_max - x_min
        det_y = y_max - y_min
        area = cv.contourArea(contours[i])#获取区域面积
        if (det_x / det_y > 1.8) and (det_x > det_x_max ) and (det_y > det_y_max ) and area>1500:
            det_y_max = det_y
            det_x_max = det_x
            num = i
            ret=True
    # 获取最可疑区域轮廓点集
    points = np.array(contours[num][:, 0])
    return ret,points


#img_lic_canny = cv2.Canny(img_lic_bin, 100, 200)


def findVertices(points):
    # 获取最小外接矩阵，中心点坐标，宽高，旋转角度
    rect = cv.minAreaRect(points)
    # 获取矩形四个顶点，浮点型
    box = cv.boxPoints(rect)
    # 取整
    box = np.int0(box)
    # 获取四个顶点坐标
    left_point_x = np.min(box[:, 0])
    right_point_x = np.max(box[:, 0])
    top_point_y = np.min(box[:, 1])
    bottom_point_y = np.max(box[:, 1])

    left_point_y = box[:, 1][np.where(box[:, 0] == left_point_x)][0]
    right_point_y = box[:, 1][np.where(box[:, 0] == right_point_x)][0]
    top_point_x = box[:, 0][np.where(box[:, 1] == top_point_y)][0]
    bottom_point_x = box[:, 0][np.where(box[:, 1] == bottom_point_y)][0]
    # 上下左右四个点坐标
    vertices = np.array([[top_point_x, top_point_y], [bottom_point_x, bottom_point_y], [left_point_x, left_point_y], [right_point_x, right_point_y]])
    return vertices, rect

def tiltCorrection(vertices, rect):
    # 畸变情况1
    if rect[2] > -45:
        new_right_point_x = vertices[0, 0]
        new_right_point_y = int(vertices[1, 1] - (vertices[0, 0]- vertices[1, 0]) / (vertices[3, 0] - vertices[1, 0]) * (vertices[1, 1] - vertices[3, 1]))
        new_left_point_x = vertices[1, 0]
        new_left_point_y = int(vertices[0, 1] + (vertices[0, 0] - vertices[1, 0]) / (vertices[0, 0] - vertices[2, 0]) * (vertices[2, 1] - vertices[0, 1]))
        # 校正后的四个顶点坐标
        point_set_1 = np.float32([[440, 0],[0, 0],[0, 140],[440, 140]])
    # 畸变情况2
    elif rect[2] < -45:
        new_right_point_x = vertices[1, 0]
        new_right_point_y = int(vertices[0, 1] + (vertices[1, 0] - vertices[0, 0]) / (vertices[3, 0] - vertices[0, 0]) * (vertices[3, 1] - vertices[0, 1]))
        new_left_point_x = vertices[0, 0]
        new_left_point_y = int(vertices[1, 1] - (vertices[1, 0] - vertices[0, 0]) / (vertices[1, 0] - vertices[2, 0]) * (vertices[1, 1] - vertices[2, 1]))
        # 校正后的四个顶点坐标
        point_set_1 = np.float32([[0, 0],[0, 140],[440,140],[440, 0]])

    # 校正前平行四边形四个顶点坐标
    new_box = np.array([(vertices[0, 0], vertices[0, 1]), (new_left_point_x, new_left_point_y), (vertices[1, 0], vertices[1, 1]), (new_right_point_x, new_right_point_y)])
    point_set_0 = np.float32(new_box)
    return point_set_0, point_set_1, new_box

def transform(img, point_set_0, point_set_1):
    # 变换矩阵
    mat = cv.getPerspectiveTransform(point_set_0, point_set_1)
    # 投影变换
    lic = cv.warpPerspective(img, mat, (440, 140))
    return lic


"""
需要对无需矫正的矩形的区域特殊处理，否则会出现除0报错
box
[[264 308]
 [264 229]
 [507 229]
 [507 308]]

vertices
[[264 229]
 [264 308]
 [264 308]
 [507 229]]

"""
def IsNeedFix(points):#判断是否需要调整
    rect = cv.minAreaRect(points)
    # 获取矩形四个顶点，浮点型
    box = cv.boxPoints(rect)
    # 取整
    box = np.int0(box)
    for i in range(1,4,1):
        if box[i][0]==box[0][0]:
            return False
    return True


def rec2img(points,img):
    rect = cv.boundingRect(points)
    x = rect[0]
    y = rect[1]
    width = rect[2]
    height = rect[3]
    plate = img[y:y + height, x:x + width]
    unFix = cv.resize(plate, (440, 140))
    return unFix


def output_lp(rawImg):
    # 图像预处理
    img, img_Gas, img_B, img_G, img_R, img_gray, img_HSV = imgProcess(rawImg)
    # 初步识别
    img_bin  = preIdentification(img_gray, img_HSV, img_B, img_R)
    ret,points = fixPosition(img_bin)
    if IsNeedFix(points):  # 是否需要调整
        vertices, rect = findVertices(points)
        point_set_0, point_set_1, new_box = tiltCorrection(vertices, rect)
        #img_draw = cv2.drawContours(img.copy(), [new_box], -1, (0,0,255), 3)
        lic = transform(img, point_set_0, point_set_1)
        return ret,lic
    else:
        unFix = rec2img(points, img)
        return ret,unFix


if __name__=='__main__':
    img = cv.imdecode(np.fromfile("E:/license_plates_pic/苏C12345.jpg", dtype=np.uint8), -1)
    cv.imshow("rawImage",img)
    img, img_Gas, img_B, img_G, img_R, img_gray, img_HSV=imgProcess(img)


    # 初步颜色识别
    imgBin=preIdentification(img_gray, img_HSV, img_B, img_R)
    cv.imshow("threshold", imgBin)
    ret,zone=output_lp(img)
    cv.imshow("plate",zone)
    cv.waitKey(0)

