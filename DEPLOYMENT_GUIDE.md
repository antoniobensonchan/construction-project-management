# 建筑项目管理系统 - 完整部署指南

## 📦 导出完成信息

**导出时间**: 2025-08-25 23:42:51
**导出文件**: `project_export_20250825_234251.zip` (3.02 MB)

**包含数据**:
- 项目: 7个
- 图纸: 5个  
- 任务: 9个
- 标注: 12个
- 媒体文件: 13个

---

## 🚀 在新电脑上部署步骤

### 方法1: 自动部署（推荐）

1. **复制文件到新电脑**
   ```bash
   # 将 project_export_20250825_234251.zip 复制到新电脑
   # 解压缩到任意目录，例如: C:\Projects\ConstructionPM\
   ```

2. **安装Python环境**
   - 下载并安装 Python 3.8+ (推荐3.11)
   - 确保勾选 "Add Python to PATH"

3. **运行自动部署脚本**
   ```bash
   # 打开命令行，进入解压后的目录
   cd C:\Projects\ConstructionPM\
   
   # 创建虚拟环境
   python -m venv venv
   
   # 激活虚拟环境
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   
   # 复制代码文件
   xcopy /E /I code\* .\
   
   # 运行自动设置脚本
   python setup_project.py
   ```

4. **启动项目**
   ```bash
   python manage.py runserver
   ```

5. **访问系统**
   - 打开浏览器访问: http://127.0.0.1:8000/

---

### 方法2: 手动部署

1. **环境准备**
   ```bash
   # 创建项目目录
   mkdir ConstructionPM
   cd ConstructionPM
   
   # 创建虚拟环境
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

2. **安装依赖**
   ```bash
   pip install Django==4.2.7
   pip install Pillow==10.0.1
   pip install python-decouple==3.8
   ```

3. **复制项目文件**
   ```bash
   # 从解压的文件中复制
   # 复制 code/* 到当前目录
   # 复制 media/* 到当前目录
   # 复制 database_data.json 到当前目录
   ```

4. **数据库设置**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py loaddata database_data.json
   ```

5. **静态文件收集**
   ```bash
   python manage.py collectstatic --noinput
   ```

6. **创建管理员用户（可选）**
   ```bash
   python manage.py createsuperuser
   ```

7. **启动服务器**
   ```bash
   python manage.py runserver
   ```

---

## 🔧 配置说明

### 数据库配置
项目默认使用SQLite数据库，无需额外配置。如需使用其他数据库：

```python
# construction_pm/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # 或 mysql
        'NAME': 'construction_pm',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 媒体文件配置
```python
# construction_pm/settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

### 静态文件配置
```python
# construction_pm/settings.py
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
```

---

## ✅ 部署验证

部署完成后，请验证以下功能：

### 1. 基础功能
- [ ] 访问首页 http://127.0.0.1:8000/
- [ ] 查看项目列表
- [ ] 创建新项目
- [ ] 编辑现有项目

### 2. 图纸功能
- [ ] 上传图纸文件
- [ ] 查看图纸详情
- [ ] 图纸预览正常显示
- [ ] 图纸文件下载

### 3. 任务功能
- [ ] 创建任务
- [ ] 编辑任务
- [ ] 任务-图纸关联
- [ ] 任务状态管理

### 4. 标注功能
- [ ] 在任务页面添加标注
- [ ] 标注显示正确
- [ ] 标注颜色和类型正确
- [ ] 图纸页面显示所有标注

### 5. 数据完整性
- [ ] 所有导入的项目都存在
- [ ] 图纸文件正常显示
- [ ] 任务数据完整
- [ ] 标注数据正确

---

## 🐛 故障排除

### 常见问题及解决方案

**1. 图片不显示**
```bash
# 检查媒体文件路径
python manage.py shell
>>> from django.conf import settings
>>> print(settings.MEDIA_ROOT)
>>> print(settings.MEDIA_URL)

# 确保媒体文件已复制到正确位置
```

**2. 样式丢失**
```bash
# 重新收集静态文件
python manage.py collectstatic --clear --noinput
```

**3. 数据导入失败**
```bash
# 清空数据库重新导入
python manage.py flush
python manage.py migrate
python manage.py loaddata database_data.json
```

**4. 权限错误**
```bash
# Windows: 以管理员身份运行命令行
# Linux/Mac: 使用 sudo 或检查文件权限
chmod -R 755 media/
```

**5. 端口被占用**
```bash
# 使用其他端口
python manage.py runserver 8080
# 或
python manage.py runserver 0.0.0.0:8000
```

---

## 📞 技术支持

如果遇到部署问题，请检查：

1. **Python版本**: 确保使用Python 3.8+
2. **依赖安装**: 确保所有依赖都已正确安装
3. **文件权限**: 确保有读写权限
4. **路径问题**: 确保所有路径都正确
5. **防火墙**: 确保端口8000未被阻止

---

## 🎉 部署成功

部署成功后，您将拥有一个完整的建筑项目管理系统，包括：

- ✅ 项目管理功能
- ✅ 图纸上传和预览
- ✅ 任务创建和管理  
- ✅ 图纸标注功能
- ✅ 多图纸任务关联
- ✅ 标注高亮和交互
- ✅ 完整的用户界面

**访问地址**: http://127.0.0.1:8000/

祝您使用愉快！🎊
