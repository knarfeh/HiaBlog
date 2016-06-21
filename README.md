# Hia

学习 Flask + MongoDB 写的多人博客系统， fork from [OctBlog](https://github.com/flyhigher139/OctBlog)

## 后端

* Flask
* MongoDB

## 前端

* [clean blog](https://github.com/BlackrockDigital/startbootstrap-clean-blog)
* jQuery
* highlight.js
* Font Awesome

## 运行

* 解决依赖

```bash
$ pip install -r requirements.txt
```

* 启动 MongoDB  

```bash
$ mongod
```

* 启动服务器

```
$ python manage.py runserver
```

* 创建管理员

改 config.py 的 allow_registration 变量，使得可以注册管理员。 

访问 `http://localhost:5001/auth/registration/su` 注册管理员

访问 `http://localhost:5001/admin` 进行登录


## License

[GPL2](./LICENSE)
