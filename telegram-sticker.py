#!/usr/bin/env python

from __future__ import division
from gimpfu import *
import re
import tempfile
import math
from array import array

def python_telegram_sticker(timg, tdrawable):
    timg.undo_group_start()
    
    # Merge all layers
    pdb.gimp_image_merge_visible_layers(timg, 0)

    # Crop and resize image
    imageLayer = timg.layers[0]
    pdb.plug_in_autocrop(timg, imageLayer)

    newWidth, newHeight = resizeToTargetSize(timg)
    pdb.gimp_image_resize(timg, newWidth + 30, newHeight + 30, 10, 10)
    pdb.gimp_layer_resize_to_image_size(imageLayer)
    
    # Create white outline
    renderer = strokeRenderer()
    strokeLayer = renderer.renderStroke(timg, imageLayer, (255, 255, 255), 5)
    
    # Create drop shadow
    pdb.script_fu_drop_shadow(timg, strokeLayer, 5, 5, 10, (0, 0, 0), 25, 0)
    
    # Restore drawing context and end undo group
    timg.undo_group_end()
    
class strokeRenderer:
    def renderStroke(self, timg, tdrawable, color, size):
        strokeLayer = gimp.Layer(timg, 'stroke', tdrawable.width, tdrawable.height, RGBA_IMAGE, 100, NORMAL_MODE)
        timg.add_layer(strokeLayer, 1)
    
        self.radius = size
        self.radiusSquared = (self.radius * self.radius * 65536)
        self.radiusPlusOneSquared = ((self.radius + 1) * (self.radius + 1) * 65536)
        self.width = strokeLayer.width
        self.height = strokeLayer.height
        
        region = strokeLayer.get_pixel_rgn(0, 0, self.width, self.height, True, True)
        self.pixels = array('B', [color[0], color[1], color[2], 0] * (self.width * self.height))

        self.calculateAntiAliased(self.layerToPixels(tdrawable))
        
        region[0:self.width, 0:self.height] = self.pixels.tostring()
        strokeLayer.merge_shadow()
        
        return strokeLayer
        
    def layerToPixels(self, layer):
        region = layer.get_pixel_rgn(0, 0, layer.width, layer.height, False, False)
        return array('B', region[0:layer.width, 0:layer.height])
    
    def draw(self, x, y, distanceSquared):
        if distanceSquared <= 0 or distanceSquared >= self.radiusPlusOneSquared:
            alpha = 0
        elif distanceSquared < self.radiusSquared:
            alpha = 255
        else:
            distance = math.sqrt(distanceSquared / 65536) - self.radius
            alpha = 255 - int(255 * distance + 0.5)

        self.pixels[(x + self.width * y) * 4 + 3] = alpha

    def calculateAntiAliased(self, pixels):
        m = self.width
        n = self.height

        scale = 256
        g = [0] * (m * n)
        inf = scale * (m + n)

        for x in range(0, m):
            a = 255 - pixels[x * 4 + 3]

            if a == 0:
                g[x] = 0
            elif a == 255:
                g[x] = inf
            else:
                g[x] = a
                
            for y in range(1, n):
                idx = x + y * m

                a = 255 - pixels[(x + m * y) * 4 + 3]

                if a == 0:
                    g[idx] = 0
                elif a == 255:
                    g[idx] = scale + g[idx - m]
                else:
                    g[idx] = a
                    
            for y in range(n - 2, -1, -1):
                idx = x + y * m
                d = scale + g[idx + m]
                
                if g[idx] > d:
                    g[idx] = d
                    
        s = [0] * max(m, n)
        t = [0] * max(m, n)
        
        for y in range(0, n):
            q = 0
            s[0] = 0
            t[0] = 0
            
            ym = y * m
            
            for u in range(1, m):
                while (
                    q >= 0 and self.f(self.floorFixed8(t[q]) - scale * s[q], g[s[q] + ym]) >
                    self.f(self.floorFixed8(t[q]) - scale * u, g[u + ym])
                ):
                    q -= 1
                    
                if q < 0:
                    q = 0
                    s[0] = u
                else:
                    w = scale + self.sep(scale * s[q], scale * u, g[s[q] + ym], g[u + ym], inf)
                    
                    if w < scale * m:
                        q += 1
                        s[q] = u
                        t[q] = w
                        
            for u in range(m - 1, -1, -1):
                d = self.f(scale * (u - s[q]), g[s[q] + ym])

                self.draw(u, y, d)
                
                if u == t[q] // scale:
                    q -= 1

    def floorFixed8(self, x):
        return x & (~0xff)
        
    def f(self, xi, gi):
        return (xi * xi) + gi * gi
        
    def sep(self, i, u, gi, gu, inf):
        return (u * u - i * i + gu * gu - gi * gi) // (2 * (u - i))
    
def resizeToTargetSize(timg):
    targetSize = 512 - 30 # 10 for the outline and 20 for the shadow
    width      = timg.width
    height     = timg.height
    
    if (width > height):
        newWidth = targetSize
        newHeight = int(height / (width / newWidth))
    else:
        newHeight = targetSize
        newWidth = int(width / (height / newHeight))
    
    pdb.gimp_image_scale(timg, newWidth, newHeight)
    
    return (newWidth, newHeight)
    
register(
        "python_fu_telegram_sticker",
        "Makes a telegram sticker out of the current image",
        "Makes a telegram sticker out of the current image",
        "Ben Scholzen 'DASPRiD'",
        "Ben Scholzen 'DASPRiD'",
        "2015",
        "<Image>/Filters/Generic/Telegram Sticker",
        "RGB*, GRAY*",
        [],
        [],
        python_telegram_sticker)

main()
