#!/usr/bin/env python

from __future__ import division
from gimpfu import *

def python_telegram_sticker(timg, tdrawable):
    timg.undo_group_start()
    pdb.gimp_context_push()
    
    # Merge all layers
    pdb.gimp_image_merge_visible_layers(timg, 0)

    # Crop and resize image
    imageLayer = timg.layers[0]
    pdb.plug_in_autocrop(timg, imageLayer)

    newWidth, newHeight = resizeToTargetSize(timg)
    pdb.gimp_layer_resize_to_image_size(imageLayer)
    
    # Create white outline
    pdb.gimp_image_resize(timg, newWidth + 10, newHeight + 10, 5, 5)
    
    strokeLayer = gimp.Layer(timg, 'stroke', newWidth + 10, newHeight + 10, RGBA_IMAGE, 100, NORMAL_MODE)
    timg.add_layer(strokeLayer, 1)
    timg.active_layer = strokeLayer
    
    pdb.gimp_image_select_item(timg, 0, imageLayer)
    numBrushes, brushList = pdb.gimp_brushes_list('stickeroutline')

    if numBrushes <> 1:
        copyName = pdb.gimp_brush_duplicate('2. Hardness 100')
        actualName = pdb.gimp_brush_rename(copyName, 'stickeroutline')

    pdb.gimp_brush_set_radius('stickeroutline', 5)
    pdb.gimp_context_set_brush('stickeroutline')
    pdb.gimp_context_set_foreground((255, 255, 255))
    pdb.gimp_context_set_paint_method('gimp-paintbrush')
    pdb.gimp_edit_stroke(strokeLayer)
    
    pdb.gimp_brush_delete('stickeroutline')
    pdb.gimp_selection_none(timg)
    
    # Create drop shadow
    pdb.script_fu_drop_shadow(timg, strokeLayer, 5, 5, 10, (0, 0, 0), 25, 1)
    
    # Final resize
    resizeToTargetSize(timg)

    # Restore drawing context and end undo group
    pdb.gimp_context_pop()
    timg.undo_group_end()
    
def resizeToTargetSize(timg):
    width  = timg.width
    height = timg.height
    
    if (width > height):
        newWidth = 512
        newHeight = int(height / (width / newWidth))
    else:
        newHeight = 512
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
