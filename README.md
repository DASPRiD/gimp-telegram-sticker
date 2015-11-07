# Telegram Sticker plug-in for GIMP

This is a simple plug-in to ease creation of stickers for telegram.

## Installation
Copy the `telegram-sticker.py` file into GIMP's plug-ins folder. For further instructions, refer to this page:
https://en.wikibooks.org/wiki/GIMP/Installing_Plugins

## Usage
Load up an image in GIMP and if required, edit it to make the background transparent. Don't worry about size, cropping
or layer-merging, as the plug-in will take care of everything else. When the image is cleaned up, run the plug-in via
the filters menu:

`Filters/Generic/Telegram Sticker`

After that, you just have to save it as `.png` or `.webp` file.

## Note
The plug-in currently relies on the image being RGBA (so an RGB image with alpha channel). Grayscale is not supported.

