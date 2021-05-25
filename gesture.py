import cv2 as cv
import numpy as np
import math
import pyautogui as p
import time as t

cap = cv.VideoCapture(0)


def nothing(x):
    pass


cv.namedWindow("Color Adjustments", cv.WINDOW_NORMAL)
cv.resizeWindow("Color Adjustments", (300, 300))
cv.createTrackbar("Thresh", "Color Adjustments", 0, 255, nothing)

cv.createTrackbar("Lower_H", "Color Adjustments", 0, 255, nothing)
cv.createTrackbar("Lower_S", "Color Adjustments", 0, 255, nothing)
cv.createTrackbar("Lower_V", "Color Adjustments", 0, 255, nothing)
cv.createTrackbar("Upper_H", "Color Adjustments", 255, 255, nothing)
cv.createTrackbar("Upper_S", "Color Adjustments", 255, 255, nothing)
cv.createTrackbar("Upper_V", "Color Adjustments", 255, 255, nothing)

while True:
    _, frame = cap.read()
    frame = cv.flip(frame, 2)
    frame = cv.resize(frame, (600, 500))

    cv.rectangle(frame, (0, 1), (300, 500), (255, 0, 0), 0)
    crop_image = frame[1:500, 0:300]

    hsv = cv.cvtColor(crop_image, cv.COLOR_BGR2HSV)

    l_h = cv.getTrackbarPos("Lower_H", "Color Adjustments")
    l_s = cv.getTrackbarPos("Lower_S", "Color Adjustments")
    l_v = cv.getTrackbarPos("Lower_V", "Color Adjustments")

    u_h = cv.getTrackbarPos("Upper_H", "Color Adjustments")
    u_s = cv.getTrackbarPos("Upper_S", "Color Adjustments")
    u_v = cv.getTrackbarPos("Upper_V", "Color Adjustments")

    lower_bound = np.array([l_h, l_s, l_v])
    upper_bound = np.array([u_h, u_s, u_v])

    mask = cv.inRange(hsv, lower_bound, upper_bound)

    filtr = cv.bitwise_and(crop_image, crop_image, mask=mask)

    mask1 = cv.bitwise_not(mask)
    m_g = cv.getTrackbarPos("Thresh", "Color Adjustments")  # getting track bar value
    ret, thresh = cv.threshold(mask1, m_g, 255, cv.THRESH_BINARY)
    dilata = cv.dilate(thresh, (3, 3), iterations=6)

    cnts, hier = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    try:

        cm = max(cnts, key=lambda x: cv.contourArea(x))

        epsilon = 0.0005 * cv.arcLength(cm, True)
        data = cv.approxPolyDP(cm, epsilon, True)

        hull = cv.convexHull(cm)

        cv.drawContours(crop_image, [cm], -1, (50, 50, 150), 2)
        cv.drawContours(crop_image, [hull], -1, (0, 255, 0), 2)

        hull = cv.convexHull(cm, returnPoints=False)
        defects = cv.convexityDefects(cm, hull)
        count_defects = 0

        for i in range(defects.shape[0]):
            s, e, f, d = defects[i, 0]

            start = tuple(cm[s][0])
            end = tuple(cm[e][0])
            far = tuple(cm[f][0])

            a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
            b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
            c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
            angle = (math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 180) / 3.14

            if angle <= 50:
                count_defects += 1
                cv.circle(crop_image, far, 5, [255, 255, 255], -1)

        print("count==", count_defects)

        if count_defects == 0:

            cv.putText(frame, " ", (50, 50), cv.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
        elif count_defects == 1:

            p.press("space")
            cv.putText(frame, "Play/Pause", (50, 50), cv.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
        elif count_defects == 2:
            p.press("w")

            cv.putText(frame, "Volume UP", (5, 50), cv.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
        elif count_defects == 3:
            p.press("s")

            cv.putText(frame, "Volume Down", (50, 50), cv.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
        elif count_defects == 4:
            p.press("d")

            cv.putText(frame, "Forward", (50, 50), cv.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
        else:
            pass

    except:
        pass

    cv.imshow("Thresh", thresh)

    cv.imshow("filter==", filtr)
    cv.imshow("Result", frame)

    key = cv.waitKey(25) & 0xFF
    if key == 27:
        break
cap.release()
cv.destroyAllWindows()
