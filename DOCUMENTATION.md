# 建筑项目管理系统 - 完整文档

## 📋 目录
1. [系统概述](#系统概述)
2. [功能特性](#功能特性)
3. [技术架构](#技术架构)
4. [安装部署](#安装部署)
5. [使用指南](#使用指南)
6. [API文档](#api文档)
7. [开发指南](#开发指南)
8. [性能优化](#性能优化)
9. [故障排除](#故障排除)

## 系统概述

建筑项目管理系统是一个功能完整的Web应用，专为建筑行业设计，提供项目管理、任务跟踪、图纸标注、甘特图可视化等核心功能。

### 核心价值
- **提高效率**: 数字化管理减少人工成本
- **精确跟踪**: 实时进度监控和报告
- **协作增强**: 多用户协作和权限管理
- **数据安全**: 基于公司的数据隔离

## 功能特性

### 🏗️ 项目管理
- **项目创建**: 支持项目基本信息、时间计划设置
- **工地管理**: 多工地支持，每个工地独立管理
- **进度跟踪**: 基于时间和任务完成情况的智能进度计算
- **状态管理**: 项目状态流转（规划中→进行中→已完成）

### 📋 任务管理
- **层级结构**: 主任务和子任务的完整层级管理
- **任务类型**: 新建施工、整改修复、检查验收、维护保养
- **状态跟踪**: 开放→进行中→待处理→已完成
- **依赖管理**: 四种依赖类型（FS、SS、FF、SF）
- **循环检测**: 自动检测和防止循环依赖

### 📊 甘特图可视化
- **时间轴显示**: 横向展示项目全周期
- **工地分组**: 按工作地点分组显示任务
- **任务层级**: 清晰的主任务→子任务结构
- **进度可视化**: 颜色编码和进度条显示
- **PDF导出**: 专业的甘特图PDF报告

### 📐 图纸管理
- **PDF上传**: 支持拖拽上传，文件验证
- **在线预览**: PDF.js支持的在线查看
- **标注功能**: 点、线、矩形、文本标注
- **标注管理**: 标注编辑、删除、批量操作

### 👥 用户管理
- **公司隔离**: 基于公司的数据完全隔离
- **权限控制**: 用户只能访问自己公司的数据
- **安全认证**: 完整的登录、注册、注销流程

## 技术架构

### 后端架构
```
Django 4.2.7
├── Core Module (核心模块)
│   ├── Mixins (混入类)
│   ├── Utils (工具函数)
│   └── Base Views (基础视图)
├── Accounts (用户认证)
├── Projects (项目管理)
├── Tasks (任务管理)
├── Drawings (图纸管理)
└── Gantt (甘特图)
```

### 前端技术栈
- **HTML5 + CSS3**: 现代Web标准
- **Bootstrap 5**: 响应式UI框架
- **JavaScript ES6+**: 现代JavaScript特性
- **PDF.js**: PDF文件处理
- **Canvas API**: 图纸标注功能

### 数据库设计
```sql
-- 核心实体关系
User (用户)
├── Project (项目) 1:N
    ├── WorkSite (工地) 1:N
        ├── Task (任务) 1:N
        │   ├── SubTask (子任务) 1:N
        │   └── TaskDependency (依赖) N:N
        └── Drawing (图纸) 1:N
            └── Annotation (标注) 1:N
```

## 安装部署

### 开发环境
```bash
# 1. 克隆项目
git clone <repository-url>
cd ConstructionPMProject

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 5. 创建超级用户
python manage.py createsuperuser

# 6. 启动服务
python manage.py runserver
```

### 生产环境
```bash
# 1. 安装生产依赖
pip install gunicorn whitenoise

# 2. 配置环境变量
export DEBUG=False
export ALLOWED_HOSTS=your-domain.com
export SECRET_KEY=your-secret-key

# 3. 收集静态文件
python manage.py collectstatic

# 4. 启动Gunicorn
gunicorn construction_pm.wsgi:application --bind 0.0.0.0:8000
```

### Docker部署
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "construction_pm.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## 使用指南

### 快速开始
1. **注册账户**: 填写公司信息和用户信息
2. **创建项目**: 设置项目基本信息和时间计划
3. **添加工地**: 为项目添加施工工地
4. **创建任务**: 添加主任务和子任务
5. **上传图纸**: 上传PDF图纸并添加标注
6. **查看甘特图**: 可视化项目进度

### 核心工作流程
```
项目创建 → 工地设置 → 任务规划 → 图纸上传 → 标注添加 → 进度跟踪 → 甘特图查看 → PDF导出
```

### 任务依赖设置
- **完成-开始 (FS)**: A任务完成后B任务才能开始
- **开始-开始 (SS)**: A任务开始后B任务才能开始
- **完成-完成 (FF)**: A任务完成后B任务才能完成
- **开始-完成 (SF)**: A任务开始后B任务才能完成

## API文档

### 甘特图API
```http
GET /gantt/api/project/{project_id}/data/
Content-Type: application/json

Response:
{
  "project": {...},
  "worksites": [...],
  "tasks": [...],
  "dependencies": [...]
}
```

### 任务依赖API
```http
POST /tasks/{task_id}/dependency/add/
Content-Type: application/json

{
  "predecessor_id": 1,
  "dependency_type": "FS",
  "lag_days": 0
}
```

### 子任务API
```http
POST /tasks/{parent_task_id}/subtask/create/
Content-Type: application/json

{
  "name": "子任务名称",
  "responsible_person": "负责人",
  "start_date": "2025-01-01",
  "end_date": "2025-01-10",
  "deadline": "2025-01-15"
}
```

## 开发指南

### 代码结构
```
core/
├── mixins.py          # 通用混入类
├── utils.py           # 工具函数
└── views.py           # 基础视图类

apps/
├── accounts/          # 用户认证
├── projects/          # 项目管理
├── tasks/            # 任务管理
├── drawings/         # 图纸管理
└── gantt/           # 甘特图
```

### 核心混入类
- **UserOwnedMixin**: 用户数据隔离
- **OptimizedQueryMixin**: 查询优化
- **DateValidationMixin**: 日期验证
- **CacheMixin**: 缓存支持
- **APIResponseMixin**: API响应格式化

### 开发规范
```python
# 视图继承示例
class ProjectListView(BaseListView):
    model = Project
    template_name = 'projects/list.html'
    search_fields = ['name', 'description']
    
# 表单验证示例
class ProjectForm(forms.ModelForm, FormValidationMixin):
    def clean(self):
        return self.validate_date_fields()
```

## 性能优化

### 数据库优化
- **查询优化**: 使用select_related和prefetch_related
- **索引优化**: 为常用查询字段添加索引
- **批量操作**: 使用bulk_create和bulk_update

### 缓存策略
```python
# 视图缓存
@cache_page(300)
def project_list(request):
    pass

# 模板片段缓存
{% cache 300 project_stats project.id %}
    <!-- 项目统计信息 -->
{% endcache %}

# 查询结果缓存
@cache_model_method(timeout=300)
def get_progress_percentage(self):
    pass
```

### 前端优化
- **静态文件压缩**: 使用WhiteNoise
- **图片优化**: 自动生成缩略图
- **懒加载**: 大列表分页加载
- **CDN**: 静态资源CDN加速

## 故障排除

### 常见问题

**1. 数据库迁移失败**
```bash
# 重置迁移
python manage.py migrate --fake-initial
python manage.py migrate
```

**2. 静态文件404**
```python
# settings.py
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

**3. PDF上传失败**
```python
# 检查文件大小限制
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
```

**4. 甘特图显示异常**
- 检查任务日期是否设置
- 验证项目时间范围
- 确认浏览器JavaScript支持

### 日志分析
```bash
# 查看应用日志
tail -f logs/construction_pm.log

# 查看错误日志
grep ERROR logs/construction_pm.log

# 性能分析
grep "executed in" logs/construction_pm.log
```

### 性能监控
```python
# 数据库查询监控
from django.db import connection
print(f"Queries: {len(connection.queries)}")

# 内存使用监控
import psutil
print(f"Memory: {psutil.virtual_memory().percent}%")
```

---

**文档版本**: 2.0.0  
**最后更新**: 2025年9月6日  
**维护团队**: Construction PM Development Team
