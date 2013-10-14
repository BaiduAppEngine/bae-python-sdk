# -*- coding: utf-8 -*-

import re
import base64
import math
try:
   import simplejson as json
except:
   import json

from bae_utils.transf import connectoBackend, handleResponse
from bae_utils.check import checkParamsType, checkParamsLimit
from bae_utils.exceptions import BaeConstructError, BaeOperationFailed, BaeParamError, BaeValueError

class BaeImage(object):
   METHOD = 'method'
   HOST = 'host'
   PRODUCT = 'imageui'
   SIGN = 'sign'
   ACCESS_TOKEN = 'access_token'
   SECRET_KEY = 'client_secret'
   ACCESS_KEY = 'client_id'
   DEFAULT_HOST = 'bus.api.baidu.com'
   TIMESTAMP = 'timestamp'
   EXPIRES = 'expires'
   VERSION = 'v'
   DEFAULT_NAME = 'resource'

   ZOOMING_TYPE_HEIGHT = 1
   ZOOMING_TYPE_WIDTH  = 2
   ZOOMING_TYPE_PIXELS = 3
   ZOOMING_TYPE_UNRATIO = 4  
 
   RGB_PATTERN = re.compile(r'[AaBbCcDdEeFf0123456789]{6}')

   def __init__(self, access_key, secret_key, host, image_source = "http://", debug = False):
      self.__args = {}
      self.__args['src'] = image_source
      self.__ak = access_key 
      self.__sk = secret_key
      self.__host = host
      checkParamsType([(self.__ak, [basestring]), (self.__sk, [basestring]), (debug, [bool]), (self.__args['src'], [basestring]), (self.__host, [basestring])])
      checkParamsLimit([(image_source, ['0<=len(x)<=2048'])])
      if not self.__ak or not self.__sk or not self.__host:
         raise BaeConstructError("Invalid ak, sk, or image host")
      self.__requestId = 0
      self._debug = debug
      self.__strudata = None

   def setSource(self, image_source):
      checkParamsType([(image_source, [basestring])])
      if isinstance(image_source, unicode):
         image_source = image_source.encode('utf-8')
      checkParamsLimit([(image_source, ['0<len(x)<=2048'])])
      if self._isUrl(image_source):
         self.__args['src'] = image_source

   def setZooming(self, zooming_type, value, height_value = 0):
      checkParamsType([(zooming_type, [int]), (value, [int]), (height_value, [int])])
      checkParamsLimit([(zooming_type, ['1<=x<=4'])])
      if zooming_type == BaeImage.ZOOMING_TYPE_HEIGHT:
         checkParamsLimit([(value, ['0<=x<=10000'])])
         self.__args['size'] = 'b0_' + str(value)
      elif zooming_type == BaeImage.ZOOMING_TYPE_WIDTH:
         checkParamsLimit([(value, ['0<=x<=10000'])])
         self.__args['size'] = 'b' + str(value) + '_0'
      elif zooming_type == BaeImage.ZOOMING_TYPE_PIXELS:
         checkParamsLimit([(value, ['0<=x<=100000000'])])
         self.__args['size'] = 'p' + str(value)
      elif zooming_type == BaeImage.ZOOMING_TYPE_UNRATIO:
         checkParamsLimit([(value, ['0<=x<=10000'])]) 
         checkParamsLimit([(height_value, ['0<=x<=10000'])])
         self.__args['size'] = 'u' + str(value) + '_' + str(height_value)
          
   def setCropping(self, x, y, width, height):
      checkParamsType([(x, [int]), (y, [int]), (height, [int]), (width, [int])])
      checkParamsLimit([(x, ['0<=x<=10000']), (y, ['0<=x<=10000']), (height, ['0<=x<=10000']), (width, ['0<=x<=10000'])])
      self.__args['cut_x'] = x
      self.__args['cut_y'] = y
      self.__args['cut_h'] = height
      self.__args['cut_w'] = width

   def setRotation(self, degree):
      checkParamsType([(degree, [int])])
      checkParamsLimit([(degree, ['0<=x<=360'])])
      self.__args['rotate'] = degree
      
   def setHue(self, hue):
      checkParamsType([(hue, [int])])
      checkParamsLimit([(hue, ['1<=x<=100'])])
      self.__args['hue'] = hue
      
   def setLightness(self, lightness):
      checkParamsType([(lightness, [int])])
      checkParamsLimit([(lightness, ['x>=1'])])
      self.__args['lightness'] = lightness

   def setContrast(self, contrast):
      checkParamsType([(contrast, [int])])
      checkParamsLimit([(contrast, ['0<=x<=1'])])
      self.__args['contrast'] = contrast

   def setSharpness(self, sharpness):
      checkParamsType([(sharpness, [int])])
      checkParamsLimit([(sharpness, ['1<=x<=200'])])
      self.__args['sharpen'] = sharpness

   def setSaturation(self, saturation):
      checkParamsType([(saturation, [int])])
      checkParamsLimit([(saturation, ['1<=x<=100'])])
      self.__args['saturation'] = saturation

   def setTranscoding(self, image_type, quality = 60):
      types = {'gif': 2, 'jpg': 1, 'png': 3, 'webp': 4}
      checkParamsType([(image_type, [basestring]), (quality, [int])])
      checkParamsLimit([(quality, ['0<=x<=100'])])
      try:
         self.__args['imgtype'] = types[image_type]
      except KeyError:
         raise BaeParamError('Invalid Image Type[%s]'%image_type)
      if image_type in ['gif', 'jpg']:
         self.__args['quality'] = quality

   def setQuality(self, quality = 60):
      checkParamsType([(quality, [int])])
      checkParamsLimit([(quality, ['0<=x<=100'])])
      self.__args['quality'] = quality

   def setGetGifFirstFrame(self):
      self.__args['tieba'] = 1

   def setAutoRotate(self):
      self.__args['autorotate'] = 1

   def horizontalFlip(self):
      self.__args['flop'] = 1
   
   def verticalFlip(self):
      self.__args['flip'] = 1

   def __clearProcExt(self):
      try:
         self.__strudata = None
         delattr(self, '_%s__composite_canvas_width'%self.__class__.__name__)
         delattr(self, '_%s__composite_canvas_height'%self.__class__.__name__)
         delattr(self, '_%s__composite_canvas_desttype'%self.__class__.__name__)
         delattr(self, '_%s__composite_canvas_quality'%self.__class__.__name__)
      except: pass

   def clearOperations(self):
      if 'src' in self.__args and self.__args['src'] != "http://":
         self.__args = {'src': self.__args['src']}
      else:
         self.__args = {}
      self.__clearProcExt()

   def reset(self):         
      self.__args = {}
      self.__clearProcExt()

   def _type_decorator(process_type):
      def __func_warp(func):
         def __warp(self, *args, **kwargs):
            if self.__strudata is None:
               self.__strudata = {}
               self.__strudata['process_type'] = process_type
               self.__strudata['req_data_num'] = '2' if process_type != '0' else '1'
               self.__strudata['req_data_source'] = []
               self.__req_data_source = {}
               self.__req_data_source['http_reqpack'] = {}
               self.__req_data_source['source_data_type'] = '1' if process_type != '0' else '0'
               self.__operations = self.__req_data_source['operations'] = {}
               self.__strudata['req_data_source'].append(self.__req_data_source)
               if process_type == '1':
                  t = {'sourcemethod': 'BODY', 
                       'source_data_type': '1', 
                       'operations': {},
                       'http_reqpack': {}}
                  self.__strudata['req_data_source'].append(t)
               self.__source_data = self.__strudata['source_data'] = {}
            func(self, *args, **kwargs)
         return __warp
      return __func_warp

   def _checkRGB(self, rgbstr):
      checkParamsType([(rgbstr, [basestring])])
      if isinstance(rgbstr, unicode):
         rgbstr = rgbstr.encode('utf-8')
      checkParamsLimit([(rgbstr, ['len(x)==6'])])
      if not self.RGB_PATTERN.match(rgbstr):
         raise BaeValueError("invalid RGB color", rgbstr)
   
   def _isUrl(self, src):
      if src.startswith("http://"):
         return True
      return False

####水印####
   @_type_decorator('1')
   def setAnnotateText(self, text):
      checkParamsType([(text, [basestring])])
      if isinstance(text, unicode):
         text = text.encode('utf-8')
      checkParamsLimit([(text, ['1<=len(x)<=500'])])
      self.__source_data['data1'] = base64.b64encode(text)
      
   @_type_decorator('1')
   def setAnnotateOpacity(self, opacity):
      checkParamsType([(opacity, [int, float])])
      checkParamsLimit([(opacity, ['0.0<=x<=1.0'])])
      if opacity == 1:
         opacity = '00'
      elif opacity == 0:
         opacity = 'ff'
      else:
         opacity = hex(int(math.ceil(255 - opacity*255)))
         opacity = opacity.replace('0x', '')
      opacity = opacity.upper()
      self.__operations['opacity'] = opacity
      
   @_type_decorator('1')
   def setAnnotateFont(self, name, size, color):    
      checkParamsType([(name, [int])])
      checkParamsLimit([(name, ['0<=x<=4'])])
      checkParamsType([(size, [int])])
      checkParamsLimit([(size, ['0<=x<=100'])])
      checkParamsType([(color, [basestring])])
      if isinstance(color, unicode):
         color = color.encode('utf-8')
      self._checkRGB(color)
      self.__operations['font_name'] = name
      self.__operations['font_size'] = size
      self.__operations['font_color'] = color
       
   @_type_decorator('1')
   def setAnnotatePos(self, x_offset, y_offset):
      checkParamsType([(x_offset, [int])])
      checkParamsLimit([(x_offset, ['x>=0'])])
      checkParamsType([(y_offset, [int])])
      checkParamsLimit([(y_offset, ['x>=0'])])
      self.__operations['x_offset'] = x_offset
      self.__operations['y_offset'] = y_offset
      
   @_type_decorator('1')
   def setAnnotateOutputCode(self, output_code):
      checkParamsType([(output_code, [int])])
      checkParamsLimit([(output_code, ['0<=x<=4'])])
      self.__operations['desttype'] = output_code

   @_type_decorator('1')
   def setAnnotateQuality(self, quality):
      checkParamsType([(quality, [int])])
      checkParamsLimit([(quality, ['0<=x<=100'])])
      self.__operations['quality'] = quality

####图片合成####
   @_type_decorator('2')
   def setCompositeSource(self, image_source):
      checkParamsType([(image_source, [basestring])])
      if isinstance(image_source, unicode):
         image_source = image_source.encode('utf-8')
      checkParamsLimit([(image_source, ['0<=len(x)<=2048'])])
      t = {'http_reqpack': {},
           'source_data_type': '1',
           'operations': {},
          }
      if self._isUrl(image_source):
         t['sourcemethod'] = 'GET'
         t['source_url'] = image_source 
         self.__strudata['req_data_source'].append(t)
      else: pass

   @_type_decorator('2')
   def setCompositePos(self, x_offset, y_offset, img_key = 0):
      checkParamsType([(x_offset, [int])])
      checkParamsType([(y_offset, [int])])
      if img_key >= len(self.__strudata['req_data_source']):
         raise BaeValueError("invalid img_key, image %d isn't exist"%img_key)   
      self.__strudata['req_data_source'][img_key]['operations']['x_offset'] = x_offset
      self.__strudata['req_data_source'][img_key]['operations']['y_offset'] = y_offset
      
   @_type_decorator('2')
   def setCompositeOpacity(self, opacity, img_key = 0):
      checkParamsType([(opacity, [int, float])])
      checkParamsLimit([(opacity, ['0.0<=x<=1.0'])])
      if img_key >= len(self.__strudata['req_data_source']):
         raise BaeValueError("invalid img_key, image %d isn't exist"%img_key)   
      self.__strudata['req_data_source'][img_key]['operations']['opacity'] = opacity

   @_type_decorator('2')
   def setCompositeAnchor(self, anchor, img_key = 0):
      checkParamsType([(anchor, [int])])
      checkParamsLimit([(anchor, ['0<=x<=8'])])
      if img_key >= len(self.__strudata['req_data_source']):
         raise BaeValueError("invalid img_key, image %d isn't exist"%img_key)   
      self.__strudata['req_data_source'][img_key]['operations']['anchor_point'] = anchor

   @_type_decorator('2')
   def setCompositeCanvas(self, canvas_width, canvas_height):
      checkParamsType([(canvas_width, [int])])
      checkParamsLimit([(canvas_width, ['0<=x<=10000'])])
      checkParamsType([(canvas_height, [int])])
      checkParamsLimit([(canvas_height, ['0<=x<=10000'])])
      self.__composite_canvas_width = canvas_width
      self.__composite_canvas_height = canvas_height

   @_type_decorator('2')
   def setCompositeOutputCode(self, output_code):
      checkParamsType([(output_code, [int])])
      checkParamsLimit([(output_code, ['0<=x<4'])])
      self.__composite_desttype = output_code

   @_type_decorator('2')
   def setCompositeQuality(self, quality):
      checkParamsType([(quality, [int])])
      checkParamsLimit([(quality, ['0<=x<=100'])])
      self.__composite_quality = quality

####二维码####
   @_type_decorator('0')
   def setQRCodeText(self, text):
      checkParamsType([(text, [basestring])])
      if isinstance(text, unicode):
         text = text.encode('utf-8')
      checkParamsLimit([(text, ['1<=len(x)<=500'])])
      self.__source_data['data1'] = base64.b64encode(text) 

   @_type_decorator('0')
   def setQRCodeVersion(self, version):          
      checkParamsType([(version, [int])])
      checkParamsLimit([(version, ['0<=x<=30'])])
      self.__operations['version'] = version

   @_type_decorator('0')
   def setQRCodeSize(self, size):          
      checkParamsType([(size, [int])])
      checkParamsLimit([(size, ['0<x<=100'])])
      self.__operations['size'] = size

   @_type_decorator('0')
   def setQRCodeLevel(self, level):          
      checkParamsType([(level, [int])])
      checkParamsLimit([(level, ['1<=x<=4'])])
      self.__operations['level'] = level

   @_type_decorator('0')
   def setQRCodeMargin(self, margin):          
      checkParamsType([(margin, [int])])
      checkParamsLimit([(margin, ['1<=x<=100'])])
      self.__operations['margin'] = margin

   @_type_decorator('0')
   def setQRCodeForeground(self, foreground):          
      self._checkRGB(foreground)
      self.__operations['foreground'] = foreground

   @_type_decorator('0')
   def setQRCodeBackground(self, background):          
      self._checkRGB(background)
      self.__operations['background'] = background

#### 验证码 ####
   def generateVCode(self, vcode_len = 4, vcode_pattern = 0):
      checkParamsType([(vcode_len, [int])])
      checkParamsLimit([(vcode_len, ['4<=x<=5'])])
      checkParamsType([(vcode_pattern, [int])])
      checkParamsLimit([(vcode_pattern, ['0<=x<=3'])])
      self.__args = {}
      self.__args['vcservice'] = 0
      self.__args['len'] = vcode_len
      self.__args['setno'] = vcode_pattern
      return self._common_process(self.__args)

   def verifyVCode(self, vcode_input, vcode_secret):
      checkParamsType([(vcode_input, [basestring])])
      if isinstance(vcode_input, unicode):
         vcode_input = vcode_input.encode('utf-8')
      checkParamsLimit([(vcode_input, ['4<=len(x)<=5'])])
      checkParamsType([(vcode_secret, [basestring])])
      if isinstance(vcode_secret, unicode):
         vcode_secret = vcode_secret.encode('utf-8')
      self.__args = {}
      self.__args['vcservice'] = 1
      self.__args['input'] = vcode_input
      self.__args['vcode'] = vcode_secret
      return self._common_process(self.__args)
 
   def getRequestId(self):
      """获取上次调用的request_id
      参数：
      返回值：
         request_id：int
      """
      return self.__requestId

   def process(self):
      if self.__strudata is not None:
         self.__args['method'] = 'processExt'
         src = self.__args.pop('src', 'http://')
         if self._isUrl(src):
            if self.__strudata['process_type'] == '0':
               self.__req_data_source['sourcemethod'] = 'BODY'
            else:    
               self.__req_data_source['sourcemethod'] = 'GET'
               self.__req_data_source['source_url'] = src
         else: pass

         if self.__strudata['process_type'] == '0':
            self.__operations['version'] = self.__operations.get('version', 0) 
            self.__operations['size'] = self.__operations.get('size', 3)
            self.__operations['level'] = self.__operations.get('level', 2)
            self.__operations['margin'] = self.__operations.get('margin', 4)
            self.__operations['foreground'] = self.__operations.get('foreground', '000000')
            self.__operations['background'] = self.__operations.get('background', 'FFFFFF')

         if self.__strudata['process_type'] == '1':
            self.__operations['font_name'] = self.__operations.get('font_name', 0) 
            self.__operations['font_size'] = self.__operations.get('font_size', 25)
            self.__operations['font_color'] = self.__operations.get('font_color', '000000')
            self.__operations['x_offset'] = self.__operations.get('x_offset', 0)
            self.__operations['y_offset'] = self.__operations.get('y_offset', 0)
            self.__operations['desttype'] = self.__operations.get('desttype', 0)
            self.__operations['quality'] = self.__operations.get('quality', 80)

            if 'font_color' in self.__operations:
               self.__operations['font_color'] = '#' + self.__operations['font_color'].upper()
               if 'opacity' in self.__operations:
                  self.__operations['font_color'] += self.__operations.pop('opacity')
               else:
                  self.__operations['font_color'] += 'FF'
 
         if self.__strudata['process_type'] == '2':
            for i in range(len(self.__strudata['req_data_source'])):
               self.__strudata['req_data_source'][i]['operations']['canvas_width'] = getattr(self, '_%s__composite_canvas_width'%self.__class__.__name__, 0)
               self.__strudata['req_data_source'][i]['operations']['canvas_height'] = getattr(self, '_%s__composite_canvas_height'%self.__class__.__name__, 0)
               self.__strudata['req_data_source'][i]['operations']['desttype'] = getattr(self, '_%s__composite_desttype'%self.__class__.__name__, 0)
               self.__strudata['req_data_source'][i]['operations']['quality'] = getattr(self, '_%s__composite_quality'%self.__class__.__name__, 80)
                
               self.__strudata['req_data_source'][i]['operations']['x_offset'] = self.__strudata['req_data_source'][i]['operations'].get('x_offset', 0)
               self.__strudata['req_data_source'][i]['operations']['y_offset'] = self.__strudata['req_data_source'][i]['operations'].get('y_offset', 0)
               self.__strudata['req_data_source'][i]['operations']['opacity'] = self.__strudata['req_data_source'][i]['operations'].get('opacity', 0.0)
               self.__strudata['req_data_source'][i]['operations']['anchor_point'] = self.__strudata['req_data_source'][i]['operations'].get('anchor_point', 0)

         self.__args['strudata'] = json.dumps(self.__strudata)
         return self._common_process(self.__args)
         
      return self._common_process(self.__args, ['src'])

   def _common_process(self, args, need = []):
      for k in args:
         if isinstance(args[k], unicode):
            args[k] = args[k].encode('utf-8')

      args[self.ACCESS_KEY] = self.__ak
      args[self.SECRET_KEY] = self.__sk
      args[self.HOST]       = self.__host

      if self.METHOD not in args:
          args[self.METHOD] = 'process'

      response = connectoBackend(args, need = need, debug = self._debug, PRODUCT = self.PRODUCT, 
          DEFAULT_NAME = self.DEFAULT_NAME)
      self.__requestId, ret = handleResponse(response, debug = self._debug)
      return ret
