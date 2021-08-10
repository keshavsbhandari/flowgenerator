'''
Adopted from
Tobias Weis work

Author : @Keshav
'''
import cv2
import OpenEXR
import Imath
import array
import numpy as np
import csv
import time
import datetime
import h5py
import matplotlib.pyplot as plt

def exr2depth(exr, maxvalue=1.,normalize=True):
    """ converts 1-channel exr-data to 2D numpy arrays """                                                                    
    file = OpenEXR.InputFile(exr)

    # Compute the size
    dw = file.header()['dataWindow']
    sz = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)

    # Read the three color channels as 32-bit floats
    FLOAT = Imath.PixelType(Imath.PixelType.FLOAT)
    (R) = [array.array('f', file.channel(Chan, FLOAT)).tolist() for Chan in ("R") ]

    # create numpy 2D-array
    img = np.zeros((sz[1],sz[0],3), np.float64)

    # normalize
    data = np.array(R)
    data[data > maxvalue] = maxvalue

    if normalize:
        data /= np.max(data)

    img = np.array(data).reshape(img.shape[0],-1)

    return img


def exr2flow(exr, h ,w):
    file = OpenEXR.InputFile(exr)

    # Compute the size
    dw = file.header()['dataWindow']
    sz = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)

    FLOAT = Imath.PixelType(Imath.PixelType.FLOAT)
    (R,G,B,A) = [array.array('f', file.channel(Chan, FLOAT)).tolist() for Chan in ("R", "G", "B","A") ]

    flows = np.zeros((h,w,4), np.float64)
    flows[:,:,0] = np.array(R).reshape(flows.shape[0],-1)
    flows[:,:,1] = -np.array(G).reshape(flows.shape[0],-1)
    
    flows[:,:,2] = np.array(B).reshape(flows.shape[0],-1)
    flows[:,:,3] = -np.array(A).reshape(flows.shape[0],-1)
    
    
    
    hsvf = np.zeros((h,w,3), np.uint8)
    hsvb = np.zeros((h,w,3), np.uint8)
    hsvf[...,1] = 255

    magf, angf = cv2.cartToPolar(flows[...,0], flows[...,1])
    magb, angb = cv2.cartToPolar(flows[...,1], flows[...,2])
    
    hsvf[...,0] = angf*180/np.pi/2
    hsvf[...,2] = cv2.normalize(magf,None,0,255,cv2.NORM_MINMAX)
    bgrf = cv2.cvtColor(hsvf,cv2.COLOR_HSV2BGR)
    
    hsvb[...,0] = angb*180/np.pi/2
    hsvb[...,2] = cv2.normalize(magb,None,0,255,cv2.NORM_MINMAX)
    bgrb = cv2.cvtColor(hsvb,cv2.COLOR_HSV2BGR)
    
    flowf = flows[:,:,0:2]
    flowb = flows[:,:,2:]

    return (flowf,bgrf, magf, angf), (flowb, bgrb, magb, angb)


def exr2normal(exr):
    """ converts 1-channel exr-data to 2D numpy arrays """                                                                    
    file = OpenEXR.InputFile(exr)

    # Compute the size
    dw = file.header()['dataWindow']
    sz = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)

    # Read the three color channels as 32-bit floats
    FLOAT = Imath.PixelType(Imath.PixelType.FLOAT)
    (R,G,B) = [array.array('f', file.channel(Chan, FLOAT)).tolist() for Chan in ("R","G","B") ]
    
    # create numpy 2D-array
    img = np.zeros((sz[1],sz[0],3), np.float64)
    
    R = np.array(R).reshape(*img.shape[:-1])
    G = np.array(G).reshape(*img.shape[:-1])
    B = np.array(B).reshape(*img.shape[:-1])
    return np.dstack([R,G,B])

def exr2occlusion(exr):
    """ converts 1-channel exr-data to 2D numpy arrays """                                                                    
    file = OpenEXR.InputFile(exr)

    # Compute the size
    dw = file.header()['dataWindow']
    sz = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)

    # Read the three color channels as 32-bit floats
    FLOAT = Imath.PixelType(Imath.PixelType.FLOAT)
    R = [array.array('f', file.channel(Chan, FLOAT)).tolist() for Chan in ("R") ]
    
    # create numpy 2D-array
    img = np.zeros((sz[1],sz[0],3), np.float64)
    
    R = np.array(R).reshape(*img.shape[:-1])
    return R


# Flow visualization code used from https://github.com/tomrunia/OpticalFlow_Visualization


# MIT License
#
# Copyright (c) 2018 Tom Runia
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to conditions.
#
# Author: Tom Runia
# Date Created: 2018-08-03

import numpy as np

def make_colorwheel():
    """
    Generates a color wheel for optical flow visualization as presented in:
        Baker et al. "A Database and Evaluation Methodology for Optical Flow" (ICCV, 2007)
        URL: http://vision.middlebury.edu/flow/flowEval-iccv07.pdf

    Code follows the original C++ source code of Daniel Scharstein.
    Code follows the the Matlab source code of Deqing Sun.

    Returns:
        np.ndarray: Color wheel
    """

    RY = 15
    YG = 6
    GC = 4
    CB = 11
    BM = 13
    MR = 6

    ncols = RY + YG + GC + CB + BM + MR
    colorwheel = np.zeros((ncols, 3))
    col = 0

    # RY
    colorwheel[0:RY, 0] = 255
    colorwheel[0:RY, 1] = np.floor(255*np.arange(0,RY)/RY)
    col = col+RY
    # YG
    colorwheel[col:col+YG, 0] = 255 - np.floor(255*np.arange(0,YG)/YG)
    colorwheel[col:col+YG, 1] = 255
    col = col+YG
    # GC
    colorwheel[col:col+GC, 1] = 255
    colorwheel[col:col+GC, 2] = np.floor(255*np.arange(0,GC)/GC)
    col = col+GC
    # CB
    colorwheel[col:col+CB, 1] = 255 - np.floor(255*np.arange(CB)/CB)
    colorwheel[col:col+CB, 2] = 255
    col = col+CB
    # BM
    colorwheel[col:col+BM, 2] = 255
    colorwheel[col:col+BM, 0] = np.floor(255*np.arange(0,BM)/BM)
    col = col+BM
    # MR
    colorwheel[col:col+MR, 2] = 255 - np.floor(255*np.arange(MR)/MR)
    colorwheel[col:col+MR, 0] = 255
    return colorwheel


def flow_uv_to_colors(u, v, convert_to_bgr=False):
    """
    Applies the flow color wheel to (possibly clipped) flow components u and v.

    According to the C++ source code of Daniel Scharstein
    According to the Matlab source code of Deqing Sun

    Args:
        u (np.ndarray): Input horizontal flow of shape [H,W]
        v (np.ndarray): Input vertical flow of shape [H,W]
        convert_to_bgr (bool, optional): Convert output image to BGR. Defaults to False.

    Returns:
        np.ndarray: Flow visualization image of shape [H,W,3]
    """
    flow_image = np.zeros((u.shape[0], u.shape[1], 3), np.uint8)
    colorwheel = make_colorwheel()  # shape [55x3]
    ncols = colorwheel.shape[0]
    rad = np.sqrt(np.square(u) + np.square(v))
    a = np.arctan2(-v, -u)/np.pi
    fk = (a+1) / 2*(ncols-1)
    k0 = np.floor(fk).astype(np.int32)
    k1 = k0 + 1
    k1[k1 == ncols] = 0
    f = fk - k0
    for i in range(colorwheel.shape[1]):
        tmp = colorwheel[:,i]
        col0 = tmp[k0] / 255.0
        col1 = tmp[k1] / 255.0
        col = (1-f)*col0 + f*col1
        idx = (rad <= 1)
        col[idx]  = 1 - rad[idx] * (1-col[idx])
        col[~idx] = col[~idx] * 0.75   # out of range
        # Note the 2-i => BGR instead of RGB
        ch_idx = 2-i if convert_to_bgr else i
        flow_image[:,:,ch_idx] = np.floor(255 * col)
    return flow_image


def flow_to_image(flow_uv, clip_flow=None, convert_to_bgr=False):
    """
    Expects a two dimensional flow image of shape.

    Args:
        flow_uv (np.ndarray): Flow UV image of shape [H,W,2]
        clip_flow (float, optional): Clip maximum of flow values. Defaults to None.
        convert_to_bgr (bool, optional): Convert output image to BGR. Defaults to False.

    Returns:
        np.ndarray: Flow visualization image of shape [H,W,3]
    """
    assert flow_uv.ndim == 3, 'input flow must have three dimensions'
    assert flow_uv.shape[2] == 2, 'input flow must have shape [H,W,2]'
    if clip_flow is not None:
        flow_uv = np.clip(flow_uv, 0, clip_flow)
    u = flow_uv[:,:,0]
    v = flow_uv[:,:,1]
    rad = np.sqrt(np.square(u) + np.square(v))
    rad_max = np.max(rad)
    epsilon = 1e-5
    u = u / (rad_max + epsilon)
    v = v / (rad_max + epsilon)
    return flow_uv_to_colors(u, v, convert_to_bgr)


def uvzscaler(flow_uvz, clip_flow=None, convert_to_bgr=False):
    """
    Expects a two dimensional flow image of shape.

    Args:
        flow_uv (np.ndarray): Flow UV image of shape [H,W,2]
        clip_flow (float, optional): Clip maximum of flow values. Defaults to None.
        convert_to_bgr (bool, optional): Convert output image to BGR. Defaults to False.

    Returns:
        np.ndarray: Flow visualization image of shape [H,W,3]
    """
    #assert flow_uv.ndim == 3, 'input flow must have three dimensions'
    #assert flow_uv.shape[2] == 2, 'input flow must have shape [H,W,2]'
    #if clip_flow is not None:
    #    flow_uv = np.clip(flow_uv, 0, clip_flow)
    u = flow_uvz[:,:,0]
    v = flow_uvz[:,:,1]
    z = flow_uvz[:,:,2]
    rad = np.sqrt(np.square(u) + np.square(v) + np.square(z))
    rad_max = np.max(rad)
    epsilon = 1e-5
    u = u / (rad_max + epsilon)
    v = v / (rad_max + epsilon)
    z = z / (rad_max + epsilon)
    return np.stack([u,v,z],-1)