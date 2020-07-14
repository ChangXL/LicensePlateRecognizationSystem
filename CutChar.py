import cv2 as cv
import numpy as np

def deal_license(plate):
    '''
    车牌图片二值化
    '''
    #车牌变为灰度图像
    gray_img=cv.cvtColor(plate,cv.COLOR_BGR2GRAY)

    #均值滤波  去除噪声
    kernel=np.ones((3,3),np.float32)/9
    gray_img=cv.filter2D(gray_img,-1,kernel)
    #cv.imshow("gray",gray_img)
    gmax=int(np.max(gray_img))
    gmin=int(np.min(gray_img))
    gmid=(gmax+gmin)/2+30
    #print(gmid)

    #二值化处理
    ret,thresh=cv.threshold(gray_img,gmid,255,cv.THRESH_BINARY)
    #cv.imshow("tresh",thresh)
    return thresh


def find_end(start,arg,black,white,width,black_max,white_max):
    end=start+1
    for m in range(start+1,width-1):
        if (black[m] if arg else white[m])>(0.9*black_max if arg else 0.9*white_max):
            end=m
            break
    return end


def cutplate(rawThresh):
    # 分割字符
    thresh=cv.resize(rawThresh,(440,140))#统一车牌区域大小
    '''
    判断底色和字色
    '''
    # 记录黑白像素总和
    white = []
    black = []
    height = thresh.shape[0]
    width = thresh.shape[1]
    white_max = 0
    black_max = 0
    # 计算每一列的黑白像素总和
    for i in range(width):
        line_white = 0
        line_black = 0
        for j in range(height):
            if thresh[j][i] == 255:
                line_white += 1
            if thresh[j][i] == 0:
                line_black += 1
        white_max = max(white_max, line_white)
        black_max = max(black_max, line_black)
        white.append(line_white)
        black.append(line_black)
        # print('whitemax:', white_max)
        # print('blackmax:', black_max)
    # arg为true表示黑底白字，False为白底黑字
    arg = True
    if black_max < white_max:
        arg = False
    n=1
    start=1
    end=2
    s_width=28
    s_height=28
    charList=[]
    while n<width-2:
        n+=1
        #判断是白底黑字还是黑底白字  0.05参数对应上面的0.95 可作调整
        if(white[n] if arg else black[n])>(0.01*white_max if arg else 0.01*black_max):
            start=n
            end=find_end(start,arg,black,white,width,black_max,white_max)
            n=end
            if end-start>30:#除1以外的其他字符
                cj=thresh[1:height,start:end]
                charList.append(cj)
            elif start>30 and end<420 and end-start>5 and (np.sum(white[start:end])if arg else np.sum(white[start:end]))>(end-start)*height*0.7:#检测1
                print(end-start)
                cj = thresh[1:height, start-15:end+15]
                end+=15
                charList.append(cj)
    #添加边框
    charList_border=[]
    if arg:
        for i in range(len(charList)):
            cb=cv.copyMakeBorder(charList[i],10,10,10,10,cv.BORDER_CONSTANT,value=0)
            charList_border.append(cb)
    else:
        for i in range(len(charList)):
            cb=cv.copyMakeBorder(charList[i],10,10,10,10,cv.BORDER_CONSTANT,value=255)
            charList_border.append(cb)
    return charList,charList_border

if __name__=='__main__':
    img = cv.imdecode(np.fromfile("E:/plate_area/苏BH2222.jpg", dtype=np.uint8), -1)
    tresh=deal_license(img)
    noBoder,charList=cutplate(tresh)
    print(len(charList))
    for i in range(len(charList)):
        cv.imshow("%s"%i,charList[i])
        print(charList[i].shape[1])
    cv.waitKey(0)
