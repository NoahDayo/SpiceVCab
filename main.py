#!/usr/bin/env python3
import cv2
import random
import math
import tkinter as tk
try:
	from spiceapi import *
except ModuleNotFoundError:
	raise RuntimeError("spiceapi module not installed")

cabframe = cv2.imread("./img/cabframe_light.png", cv2.IMREAD_UNCHANGED)
cablight = cv2.imread("./img/cablight.png", cv2.IMREAD_UNCHANGED)


def remove_transparency(image):
    #make mask of where the transparent bits are
    trans_mask = image[:,:,3] == 0

    #replace areas of transparency with white and not transparent
    image[trans_mask] = [0, 255, 0, 255]

    #new image without alpha channel...
    new_img = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    return new_img

def attach_img(bg, fg, x_offset, y_offset):
    y1, y2 = y_offset, y_offset + fg.shape[0]
    x1, x2 = x_offset, x_offset + fg.shape[1]
    alpha_s = fg[:, :, 3] / 255.0
    alpha_l = 1.0 - alpha_s
    for c in range(0, 3):
        bg[y1:y2, x1:x2, c] = (alpha_s * fg[:, :, c] +
                                alpha_l * bg[y1:y2, x1:x2, c])
    return bg

def split(img):
    # extract alpha channel
    alpha = img[:,:,3] / 1.25
    # extract bgr channels
    bgr = img[:,:,0:3]
    return alpha, bgr

def change_color(bgr, alpha, r, g, b):
    bgr[:] = (b, g, r)
    # put alpha back into bgr_new
    bgra = cv2.cvtColor(bgr, cv2.COLOR_BGR2BGRA)
    bgra[:,:,3] = alpha
    return bgra

def main():
    # attach wing
    height, width, _ = cablight.shape
    cab_light_alpha, cab_light_bgr = split(cablight)
    TitleName = "SpiceVCab"

    #Spice connection
    host = "192.168.9.201"  #SpiceAPI Host
    port = 1234             #SpiceAPI Port
    password = "5678"       #SpiceAPI Password
    spice = Connection(host=host, port=port, password=password) 

    LightR = 0
    LightG = 0
    LightB = 0
    break_program = False
    #get current RGB
    while break_program == False:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break
        
        #get RGB info
        LightsInfo = lights_read(spice)
        for light in LightsInfo:
            #get RGB info
            if light[0] == "Wing Left Up R":
                LightR = math.floor(light[1] * 255)
            elif light[0] == "Wing Left Up G":
                LightG = math.floor(light[1] * 255)
            elif light[0] == "Wing Left Up B":
                tempB = light[1] * 255 + 30
                if tempB >= 255:
                    LightB = 255;
                elif tempB >= 180:
                    LightB = math.floor(tempB) 
                else:
                    LightB = math.floor(light[1] * 255)
            else: continue

        #create image
        bg_copy = cabframe.copy()
        color_cablight = change_color(cab_light_bgr, cab_light_alpha, LightR, LightG, LightB)
        img_with_cablight = attach_img(bg_copy, color_cablight, 0, 0)

        #create window
        cv2.namedWindow(TitleName, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(TitleName, 541, 1080)
        cv2.imshow(TitleName, img_with_cablight)
        #remove_transparency(img_with_cablight)
if __name__ == "__main__":
    main()