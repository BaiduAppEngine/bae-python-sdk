IMAGE
=======

Image服务是云平台为广大开发者提供的图片处理服务，支持图片抓取及用户自定义图片处理功能；其中，图片处理包括图片变换（如：剪切、缩放、旋转、色彩处理等）、二维码、文字水印、验证码及图片合成等功能。

服务简介
--------
为方便开发者使用该服务，我们在BAE中集成了Image SDK，开发者可在BAE中直接调用SDK相关接口即可使用Image服务实现相关功能。最近，Image服务的SDK接口进行了一次升级，在保留原接口的同时，增加了一系列新功能接口，如：文字水印功能（Annotation）、二维码功能（QR code）、图片合成功能（Composition）、验证码功能（VerificationCode）等。新接口在命名上添加功能名字段，如文字水印相关接口，其命名为setAnnotationXXX。
BAE3.0中开发者只需在应用代码中添加requirements.txt，并指定bae_image为依赖包；也可以自行从如下地址下载安装使用: http://bcs.duapp.com/baev3-sdk/python-runtime/image/bae_image-1.0.0.tar.gz；当然也可以从github中直接获取使用

使用示例
--------
*以下是一段示例代码：*

::
        
    ### BAE3.0中使用如下方式导入
    from bae_image import BaeImage
    
    def test_img_transform():
        ### BAE3.0中需注意使用如下方式初始化, 其中api_key， secret_key，image_addr均需通过管理控制台获取
        img = BaeImage("api_key", "secret_key", "image_addr")
        
	### 设置待处理图片
        img.setSource("http://www.baidu.com/img/baidu_sylogo1.gif")
    
        ### 设置目标图片尺寸
        img.setZooming(BaeImage.ZOOMING_TYPE_PIXELS, 100000)
        
        ### 设置裁剪参数
        img.setCropping(0, 0, 2000, 2000)
        
        ### 设置旋转角度
        img.setRotation(10)
        
        ### 设置灰度级别
        img.setHue(100)
        
        ### 设置图片格式
        img.setTranscoding('gif')
        
        ### 执行图片处理
        ret = img.process()
        
        ### 返回图片base64 encoded binary data
        body = ret['response_params']['image_data']
        
        import base64
        return base64.b64decode(body)
    
    def test_img_annotate():
        img = BaeImage("api_key", "secret_key", "image_addr")
        
        ### 设置待处理图片
        img.setSource("http://www.baidu.com/img/baidu_sylogo1.gif")
        
        ### 设置水印文字
        img.setAnnotateText("hello bae")
        
        ### 设置字体信息
        img.setAnnotateFont(3, 25, '0000aa')
        
        ### 执行图片处理
        ret = img.process()
        
        ### 返回图片base64 encoded binary data
        body = ret['response_params']['image_data']
        
        import base64
        return base64.b64decode(body)
    
    def test_img_qrcode():
        img = BaeImage("api_key", "secret_key", "image_addr")
        
        ### 设置二维码文本
        img.setQRCodeText('bae')
        
        ### 设置背景颜色
        img.setQRCodeBackground('ababab')
        
        ### 执行图片处理
        ret = img.process()
        
        ### 返回图片base64 encoded binary data
        body = ret['response_params']['image_data']
        
        import base64
        return base64.b64decode(body)
    
    
    def test_img_composite():
        img = BaeImage("api_key", "secret_key", "image_addr")
        
        ### 设置待处理图片0
        img.setSource("http://www.baidu.com/img/baidu_sylogo1.gif")
        
        ### 设置待处理图片1
        img.setCompositeSource("http://www.baidu.com/img/baidu_sylogo1.gif")
        
        ### 设置图片0的锚点
        img.setCompositeAnchor(0, 3)
        
        ### 设置图片1的透明度
        img.setCompositeOpacity(0.3, 1)
        
        ### 设置合成后画布的长宽
        img.setCompositeCanvas(50, 50)
        
        ### 执行图片处理
        ret = img.process()
        
        ### 返回图片base64 encoded binary data
        body = ret['response_params']['image_data']
        
        import base64
        return base64.b64decode(body)
    
    def test_vcode():
        img = BaeImage("api_key", "secret_key", "image_addr")
        
        ### 生成一个验证码，返回值中可获取密文vcode_str和验证码图片链接imgurl
        ret = img.generateVCode(5, 3)
        
        ### 验证输入是否匹配，返回值中可获取验证结果status和验证信息str_reason
        ret = img.verifyVCode("your_input", "your_vcode_secret")
    
    def app(env, start_response):
        status = "200 OK"
        headers = [('Content-type', 'image/gif')]
        start_response(status, headers)
        test_img_transform()
        test_img_annotate()
        test_img_qrcode()
        test_img_composite()
        return "PASS"
    
    from bae.core.wsgi import WSGIApplication
    application = WSGIApplication(app)

接口列表
--------
:: 

   setSource(self, image_source) 
   设置待处理图片url
   image_source(str): 待处理图片url, 长度不超过2048字节
		      
   setZooming(self, zooming_type, value, height_value = 0)
   设置目标图片尺寸 
   zooming_type(int): 尺寸类型, 包括BaeImage.ZOOMING_TYPE_HEIGHT高度:1, BaeImage.ZOOMING_TYPE_WIDTH宽度:2, BaeImage.ZOOMING_TYPE_PIXELS像素:3, BaeImage.ZOOMING_TYPE_UNRATIO非等比缩放时高度
   value(int): 尺寸大小, 高度、宽度调整范围[0-10000], 像素调整范围[0-100000000]
   height_value(int): 高度值非等比缩放, 高度范围[0-10000]  

   setCropping(self, x, y, width, height)
   设置裁剪参数
   x(int): 裁剪起始像素x坐标（0-10000像素位置）
   y(int): 裁剪起始像素y坐标（0-10000像素位置）
   width(int): 缩放后的宽度（0-10000像素）
   height(int): 缩放后的高度（0-10000像素）

   setRotation(self, degree)
   设置旋转角度（顺时针旋转）
   degree(int): 旋转角度（0-360度）

   setHue(self, hue)
   设置灰度级别
   hue(int): 灰度级别（1-100）

   setLightness(self, lightness)
   设置亮度级别
   lightness(int): 亮度级别（1以上）

   setContrast(self, contrast)
   设置对比度
   contrast(int): 对比度级别（0为降低对比度，1为增强对比度）

   setSharpness(self, sharpness)
   设置锐化级别
   sharpness(int): 锐化级别（1-200，1-100为锐化级别，100-200为模糊级别）

   setSaturation(self, saturation)
   设置色彩饱和度级别
   saturation(int): 色彩饱和度级别（1-100）

   setTranscoding(self, image_type, quality = 60)
   设置目标图片格式
   image_type(str): 目标图片格式，“gif”，“jpg”，“png”, "webp"
   quality(int): 图片压缩质量（0-100，默认60）

   setQuality(self, quality = 60)
   设置图片压缩质量
   quality(int): 图片压缩质量（0-100，默认60）

   setGetGifFirstFrame(self)
   设置获取gif图片第一帧

   setAutoRotate(self)
   设置自动校准

   clearOperations(self)
   清除所有操作, 不包含待处理图片的url

   reset(self)
   清除所有参数, 包含待处理图片的url

   horizontalFlip(self)
   水平翻转

   verticalFlip(self)
   垂直翻转

   setAnnotateText(self, text)
   [水印处理]设置水印文本
   text(basestring): 待添加水印的文字,UTF-8编码,范围:1-500字符

   setAnnotateOpacity(self, opacity)
   [水印处理]设置文字透明度
   opacity(float): 透明度大小,范围:0-1

   setAnnotateFont(self, name, size, color)
   [水印处理]设置水印字体样式
   name(int): 字体样式,支持宋体0、楷体1、黑体2、微软雅黑3、Arial4
   size(int): 字体大小,范围:0-1000,默认为25
   color(basestring):  字体颜色,范围:标准6位RGB色,默认为黑色('000000')

   setAnnotatePos(self, x_offset, y_offset)
   [水印处理]设置水印文字位置
   x_offset(int): X坐标位置,范围:0-图片宽度
   y_offset(int): Y坐标位置,范围:0-图片高度

   setAnnotateOutputCode(self, output_code)
   [水印处理]设置图片输出格式
   output_code(int): 支持JPG0、GIF1、BMP2、PNG3、WEBP4

   setAnnotateQuality(self, quality)
   [水印处理]设置图片压缩质量
   quality(int): 范围:0-100,默认为80

   setQRCodeText(self, text)
   [二维码处理]设置二维码文本信息
   text(basestring): 待生成二维码的文字,UTF-8编码,范围:1-500个字符

   setQRCodeVersion(self, version)
   [二维码处理]设置二维码的版本信息
   version(int): 版本大小, 范围:0-30

   setQRCodeSize(self, size)
   [二维码处理]设置生成二维码的尺寸
   size(int): 尺寸大小,范围:1-100

   setQRCodeLevel(self, level)
   [二维码处理]设置二维码的纠错级别
   level(int): 纠错级别,范围:1-4

   setQRCodeMargin(self, margin)
   [二维码处理]设置二维码的边缘宽度
   margin(int): 边缘大小,范围:1-100

   setQRCodeForeground(self, foreground)
   [二维码处理]设置二维码的背景颜色
   foreground(basestring): 标准6位RGB色,默认是白色('FFFFFF')

   setQRCodeBackground(self, background)
   [二维码处理]设置二维码的前景颜色
   foreground(basestring): 标准6位RGB色,默认是黑色('000000')

   setCompositeSource(self, image_source)
   [图片合成处理]设置需要与setSource指定的待处理图片合成的图片源
   image_source(basestring): 图片的url,长度范围:1-2048.支持http协议

   setCompositePos(self, x_offset, y_offset, img_key = 0)
   [图片合成处理]设置图片相对于锚点的位置
   x_offset(int): 相对于锚点的水平位置,范围:0-图片宽度
   y_offset(int): 相对于锚点的垂直位置,范围:0-图片高度
   img_key(int): 指定操作的图片，目前支持两张图片的合成处理(setSource指定的图片img_key为0，setCompositeSource指定的图片img_key为1)

   setCompositeOpacity(self, opacity, img_key = 0)
   [图片合成处理]设置图片透明度
   opacity(float): 透明度大小,范围:0-1(0表示不透明,1表示完全透明)
   img_key(int): 指定操作的图片，目前支持两张图片的合成处理(setSource指定的图片img_key为0，setCompositeSource指定的图片img_key为1)

   setCompositeAnchor(self, anchor, img_key = 0)
   [图片合成处理]设置图片的锚点位置
   anchor(int): 锚点位置,范围:0-8,对应于"田"字的九个点,默认为0
   img_key(int): 指定操作的图片，目前支持两张图片的合成处理(setSource指定的图片img_key为0，setCompositeSource指定的图片img_key为1)

   setCompositeCanvas(self, canvas_width, canvas_height)
   [图片合成处理]设置合成的画布宽，高
   canvas_width(int): 画布宽度,范围:0-10000,默认为1000
   canvas_height(int): 画布高度,范围:0-10000,默认为1000

   setCompositeOutputCode(self, output_code)
   [图片合成处理]设置合成后图片输出格式
   output_code(int): 图片输出格式,支持JPG0、GIF1、BMP2、PNG3

   setCompositeQuality(self, quality)
   [图片合成处理]设置合成后图片压缩质量
   quality(int): 范围:0-100,默认为80

   generateVCode(self, vcode_len = 4, vcode_pattern = 0)
   [验证码处理]生成验证码操作，成功返回如下格式信息{{u'response_params': {u'status': 0, u'vcode_str': u'验证码密文信息', u'imgurl'：u'验证码url', u'str_reason': u''}, u'request_id': 4205671600}
   vcode_len(int): 验证码的长度，支持4位和5位，默认4位
   vcode_pattern(int): 验证码的类型（干扰程度）,范围：0-3,默认0

   verifyVCode(self, vcode_input, vcode_secret)
   [验证码处理]校验操作(有效时间为120秒)，成功返回如下格式信息{u'response_params': {u'status': 0, u'str_reason': u'验证结果'}, u'request_id': 4205671600})
   vcode_input(basestring): 验证码的输入,支持4位和5位
   vcode_secret(basestring): 验证码的密文

   process(self)
   调用服务执行图片处理操作, 成功返回图片处理响应数据,失败抛出异常. 图片处理响应数据形如:
   {u'response_params': {u'image_data': u'/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAj/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFAEBAAAAAAAAAAAAAAAAAAAAAP/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AKYAB//Z'}, u'request_id': 2441434200} 

   getRequestId(self)
   获取上次调用的request_id


异常
----

- BaeConstructError: 对象初始化错误
- BaeParamError: 参数错误
- BaeValueError: 后端返回的数据格式错误
- BaeOperationFailed: 后端返回结果，但本次操作失败，异常中包含了错误原因
