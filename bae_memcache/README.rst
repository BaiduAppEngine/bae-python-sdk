Cache
=====
Cache系统采用百度内部开发的分布式cache系统作为后端实现。

服务简介
--------
Cache系统采用百度内部开发的分布式cache系统作为后端实现。为了降低开发门槛，方便开发者进行开发，用户接口采用在业界广泛应用的开源软件系统Memcache的接口。Cache系统采用百度内部开发的分布式cache系统作为后端实现。为了降低开发门槛，方便开发者进行开发，用户接口采用在业界广泛应用的开源软件系统Memcache的接口。详细了解Memcache_

云平台兼容：python-memcached。点击这里了解详情_

BAE3.0中，开发者只需在应用代码中添加requirements.txt，并指定bae_memcache为依赖包；也可以自行从如下地址下载安装使用: http://bcs.duapp.com/baev3-sdk/python-runtime/memcache/bae_memcache-1.0.0.tar.gz；当然也可以github中直接获取使用

使用示例
--------
::

#-*- coding:utf-8 -*-
 
def test_cache():
    ### 开发者可使用给出的下载链接自行安装使用；同样也可以在requirements.txt中指定依赖bae_memcache使用
    from bae_memcache.cache import BaeMemcache
      
    ### 创建一个cache
    ### 其中cache_id，cache_addr，api_key， secret_key均需通过管理控制台获取
    cache_id = "fUqxFBdrJSizQFSqxGUI"
    cache_addr = "cache.duapp.com:20243"
    api_key = "urtgxzMPVigNEtOQF7yzg7C9"
    secret_key = "1e0jDqkZ7fUwNgFD5LzwPY4YAQURFGYM"
    cache = BaeMemcache(cache_id, cache_addr, api_key, secret_key)
  
    body = []
    ### 存放一个key，value对
    if cache.set('key', 'value'):
        body.append("set key => value success!")
     
    ### 获取key对应的value
    body.append("get %s success!"%cache.get('key'))
    return body
      
def app(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/html')]
    start_response(status, headers)
    try:
        return '<br>'.join(test_cache())
    except:
        return 'handle exceptions'
     
     
from bae.core.wsgi import WSGIApplication
application = WSGIApplication(app)

接口列表
-------------
::

   add(self, key, value, time = 0, min_compress_len = 0)
   往cache中添加key关联的值,成功返回True,失败返回False
   key: 存储的key, str类型
   value: 存储的value, mixed类型
   time: 以秒为单位的失效时间, int类型，默认为0，永久保存
   min_compress_len: 用zlib来压缩value, 现在不起作用,int类型

   get(self, key)
   获取cache中存储的key的值,失败或key未找到的时候返回None,成功时返回查询到的value
   key: 要获取的key,str类型

   set(self, key, value, time = 0, min_compress_len = 0)
   设置cache中key的值为value，成功返回True，失败返回False
   key: 存储的key，str类型
   value: 存储的value，mixed类型
   time: 以秒为单位的失效时间，int类型，默认为0，永久保存
   min_compress_len: 用zlib来压缩value，现在不起作用，int类型

   get_multi(self, keys, key_prefix = None)
   获取cache中多个key的value值, 失败或keys未找到的时候返回{},成功时返回查询到的values
   keys: 要获取的key，str类型
   key_prefix: keys的统一前缀，str类型
  
   set_multi(self, mapping, time = 0, key_prefix = None, min_compress_len = 0)
   设置cache中的多个key对应的value值, 返回set失败的key组成的列表, 成功时为[]
   mapping: 存储的key，value对，dict类型
   time: 以秒为单位的失效时间，int类型，默认为0，永久保存
   key_prefix: keys的统一前缀，str类型
   min_compress_len: 用zlib来压缩value，现在不起作用，int类型

   replace(self, key, value, time = 0, min_compress_len = 0)
   替换cache中key的值为value, 成功返回True，失败返回False
   key: 存储的key，str类型
   value: 存储的value，mixed类型
   time: 以秒为单位的失效时间，int类型，默认为0，永久保存
   min_compress_len: 用zlib来压缩value，现在不起作用，int类型    

   incr(self, key, delta = 1)
   增加cache中存储的key的值, 成功时返回新的元素值，失败时返回None
   key: 要操作的key，str类型
   delta: 增加的值，默认为1. 如果指定的key对应的元素不是数值类型并且不能被转换为数值， 会将此值修改为delta，int类型
   
   decr(self, key, delta = 1)
   减小cache中存储的key的值, 成功时返回新的元素值，失败时返回None
   key: 要操作的key，str类型
   delta: 减少的值，默认为1。如果指定的key对应的元素不是数值类型并且不能被转换为数值，会将此值修改为delta，如果运算结果小于0，则返回的结果是0

   delete(self, key, time = 0)
   删除cache中存储的key的值, 成功返回True，失败返回False
   key: 要操作的key，str类型
   time: 延迟删除时间，单位秒，默认为0

服务限制
--------

- 接口中的min_compress_len参数字段不起作用；
- key的最大长度为180字节；
- value最大长度为1M；
- 一次批量操作包含的原子操作数量最大为60；
- 当incr一个value达到int型(64bit)最大值，会以int型最小数继续增加。

异常
----
所有接口均可能抛出异常，主要包括python系统异常和该接口类中的自定义异常，自定义异常如下：

- BaeMemcacheException BaeMemcache异常基类；
- BaeMemcacheInternalError 内部异常类，为网络通信，数据包编解码的异常；
- BaeMemcacheParamsError 参数异常类，为传入参数的类型，长度不符要求的异常。

.. _详细了解Memcache: http://memcached.org/
.. _点击这里了解详情: http://www.tummy.com/Community/software/python-memcached/     
