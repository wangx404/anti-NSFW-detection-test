#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 5 10:44:19 2019

@author: wangx404
"""

import imageio
from PIL import Image
import argparse
import os

def parseArgs():
    """
    辅助读取命令行参数。
    """
    parser = argparse.ArgumentParser("transform image from jpg into gif format to anti-NSFW-detection algorithm")
    parser.add_argument("--mode", default=1, type=int, help="image transformation mode")
    parser.add_argument("--image", default=None, type=str, help="image path")

    args = parser.parse_args()
    return args


# 两种思路，一是将图片和一张透明的png图片合成为一张gif
# （但是某些平台的算法可以读取帧，并返回帧检测的最大概率）
# 二是将图片剪裁为多个区块，对区块透明填充后进行合成

def get_gif_name(image):
    """
    根据输入的image名称，获取gif的生成路径和名称。
    :parameter image: image path
    :return gif_name: gif file name
    """
    image_path, image_file = os.path.split(image)
    image_prefix, _ = os.path.splitext(image_file)
    gif_name = image_prefix + ".gif"
    gif_name = os.path.join(image_path, gif_name)
    return gif_name


def generate_blank_img(img):
    """
    根据源图片生成同样大小的空白帧(默认为黑色)。
    :parameter img: source image object, imageio.core.util.Image
    :return blank_img: blank image object, imageio.core.util.Image
    """
    # 生成图片
    h, w, _ = img.shape
    blank_img = Image.new(mode="RGBA", size=(w, h))
    blank_img.save("temp.png")
    # 读取成imageio的格式
    blank_img = imageio.imread("temp.png")
    os.remove("temp.png")
    return blank_img


def generate_gif_1(image, duration=[0.01, 9.99]):
    """
    使用添加空白帧的方法生成gif图像。
    :parameter image: 源图片, str
    :parameter duration: 帧间隔，空白帧为0.01，源图片设置为9.99, list of float
    :return None:
    """
    img = imageio.imread(image)
    bk_img = generate_blank_img(img) # background image
    img_list = [bk_img, img] # img object list
    gif_name = get_gif_name(image) # img & target gif file
    imageio.mimsave(gif_name, img_list, 'GIF', duration=duration) # generate gif


def get_stripe_imgs(img, stripe_width=1):
    """
    获取得到两张条纹化的图像对象(此函数用于调试条纹宽度)。
    :parameter img: source image object, numpy.ndarray
    :return [img1, img2]: 条纹图像列表, list of numpy.ndarray
    """
    h, w, _ = img.shape
    stripe_num = h // (stripe_width*2)
    img1 = img.copy()
    img2 = img.copy()
    
    for i in range(stripe_num):
        # 对第一张图片进行处理
        img1[i*2*stripe_width: (i*2+1)*stripe_width, :, :] = 255
        # 对第二章图片进行处理
        img2[(i*2+1)*stripe_width: (i*2+2)*stripe_width, :, :] = 255
    
    return [img1, img2]


def generate_stripe_imgs(image, stripe_width=1):
    """
    生成两个条纹化图像(png格式)
    :parameter image: 源图像，str
    :parameter stripe_width: 条纹的宽度，int
    :return [img1, img2]: 条纹图像列表，list of imageio.core.util.Image
    """
    img = Image.open(image)
    w, h = img.size
    img1 = Image.new(mode="RGBA", size=(w, h), color=(255,255,255))
    img2 = Image.new(mode="RGBA", size=(w, h), color=(255,255,255))
    
    stripe_num = h // (stripe_width*2) # 条纹周期数据
    for i in range(stripe_num):
        img_frag = img.crop((0, i*2*stripe_width, w, (i*2+1)*stripe_width)) # x, y, w, h
        img1.paste(img_frag, box=(0, i*2*stripe_width))
        img_frag = img.crop((0, (i*2+1)*stripe_width, w, (i*2+2)*stripe_width))
        img2.paste(img_frag, box=(0, (i*2+1)*stripe_width))
        
    img1.save("temp.png")
    img1 = imageio.imread("temp.png")
    img2.save("temp.png")
    img2 = imageio.imread("temp.png")
    os.remove("temp.png")
    return [img1, img2]


def generate_gif_2(image):
    """
    使用拼接条纹化图片的形式生成gif图像。
    :parameter image: source image, str
    :return None:
    """
    gif_name = get_gif_name(image)
    img_list = generate_stripe_imgs(image)
    imageio.mimsave(gif_name, img_list, 'GIF', fps=200)


if __name__ == "__main__":
    args = parseArgs()
    image = args.image
    if args.mode == 1:
        generate_gif_1(image)
    elif args.mode == 2:
        generate_gif_2(image)
    
    print("Image transformation finished.")