#!/usr/bin/env python

from __future__ import division
from gimpfu import *
import re
import tempfile

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
    pdb.gimp_image_resize(timg, newWidth + 12, newHeight + 12, 6, 6)
    pdb.gimp_image_select_item(timg, 0, imageLayer)
    pdb.plug_in_sel2path(timg, imageLayer)
    pdb.gimp_selection_none(timg)
    
    strokeLayer = strokeVector(timg, timg.vectors[0], 10)
    
    # Create drop shadow
    pdb.script_fu_drop_shadow(timg, strokeLayer, 5, 5, 10, (0, 0, 0), 25, 1)
    
    # Final resize
    resizeToTargetSize(timg)
    
    # Restore drawing context and end undo group
    pdb.gimp_context_pop()
    timg.undo_group_end()
    
def strokeVector(timg, vector, width):
    newAttributes = {
        'stroke': 'white',
        'stroke-width': width,
        'stroke-linecap': 'round',
        'stroke-linejoin': 'round',
        'stroke-miterlimit': 10,
    }

    svg = pdb.gimp_vectors_export_to_string(timg, vector)
    svg = re.sub(r'(<svg\s[^>]*\swidth\s*=\s*)\S*"', r'\1"%dpx"' % timg.width, svg, flags=re.DOTALL)
    svg = re.sub(r'(<svg\s[^>]*\sheight\s*=\s*)\S*"', r'\1"%dpx"' % timg.height, svg, flags=re.DOTALL)
    svg = re.sub(r'(<path\s[^>]*)\sstroke\s*=\s*"black"', r'\1', svg, flags=re.DOTALL)
    svg = re.sub(r'(<path\s[^>]*)\sstroke-width\s*=\s*"1"', r'\1', svg, flags=re.DOTALL)
    svg = re.sub(r'(<path\s)', r'\1' + ''.join([r'%s="%s" ' % i for i in newAttributes.items()]), svg, flags=re.DOTALL)
    
    tmpfile = tempfile.NamedTemporaryFile(suffix='.svg')
    tmpfile.write(svg)
    tmpfile.flush();

    strokeLayer = pdb.gimp_file_load_layer(timg, tmpfile.name)
    strokeLayer.name = 'stroke'
    tmpfile.close()
    timg.add_layer(strokeLayer, 1)
    
    return strokeLayer
    
def resizeToTargetSize(timg):
    targetSize = 512
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
