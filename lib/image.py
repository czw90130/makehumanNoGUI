#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Image class definition
======================

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehumancommunity.org/

**Github Code Home Page:**    https://github.com/makehumancommunity/

**Authors:**           Glynn Clements

**Copyright(c):**      MakeHuman Team 2001-2020

**Licensing:**         AGPL3

    This file is part of MakeHuman Community (www.makehumancommunity.org).

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


Abstract
--------

The image module contains the definition of the Image class, the container
that MakeHuman uses to handle images.

Image only depends on the numpy library, except when image have to be loaded
or saved to disk, in which case one of the back-ends (Qt or PIL) will have to 
be imported (import happens only when needed).
"""

import cv2
import numpy as np
import time

FILTER_NEAREST = cv2.INTER_NEAREST  # Nearest neighbour resize filter
FILTER_BILINEAR = cv2.INTER_LINEAR  # Bi-linear filter
FILTER_BICUBIC = cv2.INTER_CUBIC  # Bi-cubic filter

class Image(object):
    """Container for handling images.

    It is equipped with the necessary methods that one needs for loading
    and saving images and fetching their data, as well as many properties
    providing information about the loaded image.
    """

    def __init__(self, path=None, width=0, height=0, bitsPerPixel=32, components=None, data=None):
        self._is_empty = True  # 默认假设图像为空
        if path is not None:
            self._data = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if self._data is None:
                raise RuntimeError(f"Unable to load image '{path}'")
            self.sourcePath = path
            self._is_empty = False  # 从文件加载数据，图像不为空
        elif data is not None:
            if isinstance(data, Image):
                # 如果 data 是 Image 类型，使用它的 _data 属性
                self._data = data._data.copy()
            else:
                # 否则，直接使用 data 参数作为图像数据
                self._data = data
            self._is_empty = False  # 直接提供数据，图像不为空
        else:
            if components is None:
                components = 4 if bitsPerPixel == 32 else 3 if bitsPerPixel == 24 else None
            if components is None:
                raise NotImplementedError("Unsupported bitsPerPixel value")
            shape = (height, width, components)
            self._data = np.zeros(shape, dtype=np.uint8)
            if np.any(self._data):  # 检查是否所有元素都为0，理论上这里总是False
                self._is_empty = False
            else:
                self._is_empty = True  # 创建一个空图像，但已经指定了大小和通道，视为非空

        self.modified = time.time()

    @property
    def size(self):
        h, w = self._data.shape[:2]
        return (w, h)

    @property
    def width(self):
        return self._data.shape[1]

    @property
    def height(self):
        return self._data.shape[0]

    @property
    def components(self):
        """Return the number of the Image channels."""
        return self._data.shape[2] if len(self._data.shape) > 2 else 1


    @property
    def bitsPerPixel(self):
        return self.components * 8

    @property
    def data(self):
        return self._data

    def save(self, path):
        cv2.imwrite(path, self._data)

    def resized(self, width, height, filter=FILTER_NEAREST):
        resized_data = cv2.resize(self._data, (width, height), interpolation=filter)
        return Image(data=resized_data)

    def resize(self, width, height, filter=FILTER_NEAREST):
        self._data = cv2.resize(self._data, (width, height), interpolation=filter)
        self.modified = time.time()

    def blit(self, other, x, y):
        """Copy the contents of an Image to another.
        The target image may have a different size."""
        dh, dw, dc = self._data.shape
        sh, sw, sc = other._data.shape
        if sc != dc:
            raise ValueError("source image has incorrect format")
        sw = min(sw, dw - x)
        sh = min(sh, dh - y)
        self._data[y: y + sh, x: x + sw, :] = other._data

        self.modified = time.time()

    def flip_vertical(self):
        """Turn the Image upside down."""
        return Image(data=self._data[::-1, :, :])

    def flip_horizontal(self):
        """Flip the Image in the left-right direction."""
        return Image(data=self._data[:, ::-1, :])

    def __getitem__(self, xy):
        """Get the color of a specified pixel by using the
        square brackets operator.

        Example: my_color = my_image[(17, 42)]"""
        if not isinstance(xy, tuple) or len(xy) != 2:
            raise TypeError("tuple of length 2 expected")

        x, y = xy

        if not isinstance(x, int) or not isinstance(y, int):
            raise TypeError("tuple of 2 ints expected")

        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            raise IndexError("element index out of range")

        pix = self._data[y, x, :]
        if self.components == 4:
            return (pix[0], pix[1], pix[2], pix[3])
        elif self.components == 3:
            return (pix[0], pix[1], pix[2], 255)
        elif self.components == 2:
            return (pix[0], pix[0], pix[0], pix[1])
        elif self.components == 1:
            return (pix[0], pix[0], pix[0], 255)
        else:
            return None

    def __setitem__(self, xy, color):
        """Set the color of a pixel using the square brackets
        operator.

        Example: my_image[(17, 42)] = (0, 255, 64, 255)"""
        if not isinstance(xy, tuple) or len(xy) != 2:
            raise TypeError("tuple of length 2 expected")

        x, y = xy

        if not isinstance(x, int) or not isinstance(y, int):
            raise TypeError("tuple of 2 ints expected")

        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            raise IndexError("element index out of range")

        if not isinstance(color, tuple):
            raise TypeError("tuple expected")

        self._data[y, x, :] = color
        self.modified = time.time()

    def convert(self, components):
        if components == self.components:
            return self

        if components == 1:  # Convert to grayscale
            if self.components >= 3:
                # Convert BGR to Grayscale
                gray = cv2.cvtColor(self._data, cv2.COLOR_BGR2GRAY)
                return Image(data=gray.reshape(self.height, self.width, 1))
            else:
                return self  # Already grayscale or cannot be converted directly
        elif components == 3:  # Convert to BGR
            if self.components == 1:
                # Convert Grayscale to BGR
                bgr = cv2.cvtColor(self._data, cv2.COLOR_GRAY2BGR)
                return Image(data=bgr)
            elif self.components == 4:
                # Remove alpha channel
                bgr = self._data[:, :, :3]
                return Image(data=bgr)
        elif components == 4:  # Add alpha channel if not present
            if self.components == 3:
                # Add an alpha channel, fully opaque
                alpha = np.full((self.height, self.width, 1), 255, dtype=np.uint8)
                bgra = np.concatenate((self._data, alpha), axis=-1)
                return Image(data=bgra)
            elif self.components == 1:
                # Convert grayscale to BGRA
                bgr = cv2.cvtColor(self._data, cv2.COLOR_GRAY2BGR)
                alpha = np.full((self.height, self.width, 1), 255, dtype=np.uint8)
                bgra = np.concatenate((bgr, alpha), axis=-1)
                return Image(data=bgra)

        return self  # If conversion is not supported or not necessary

    def markModified(self):
        """Mark the Image as modified."""
        self.modified = time.time()
        self._is_empty = False

    @property
    def isEmpty(self):
        """
        Returns True if the Image is empty or new.
        Returns False if the Image contains data or has been modified.
        """
        return self._is_empty

