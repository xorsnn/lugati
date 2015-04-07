# -*- coding: utf-8 -*-
from sorl.thumbnail.engines.pil_engine import Engine
from PIL import Image

class LugatiPilEngine(Engine):

    def _padding(self, image, geometry, options):
        x_image, y_image = self.get_image_size(image)
        left = int((geometry[0] - x_image) / 2)
        top = int((geometry[1] - y_image) / 2)
        color = options.get('padding_color')
#xors 20140704-1124 (
        im = Image.new(image.mode, geometry, color)
        #im = Image.new(image.mode, geometry)
#~xors 20140704-1124 )
        im.paste(image, (left, top))
        return im