# OpenPulse - 开源社区生命力智能诊断与预警平台

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)

**基于时序图分析的开源社区健康度实时监测与关键贡献者流失预警系统**

## 📖 项目简介

OpenPulse 是一个创新的开源社区健康监测平台，融合四大开源工具（OpenDigger、Apache IoTDB、EasyGraph、DataEase），提供：

- 🔮 **预测式洞察**：提前3-6个月预警关键贡献者流失风险
- 🌐 **全息图谱**：构建开发者协作网络，识别社区"结构洞"与"桥接者"
- 📊 **实时脉搏**：分钟级社区健康状态监测
- 🎯 **决策赋能**：为OSPO提供可视化风险评估报告

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      OpenPulse 技术架构                          │
├─────────────────────────────────────────────────────────────────┤
│  [OpenDigger]        [Apache IoTDB]      [EasyGraph]            │
│   数据采集层     →     时序存储层    →     图分析层              │
│  ·OpenRank指标        ·高效压缩存储       ·结构洞检测            │
│  ·活跃度数据          ·实时流处理         ·社区检测              │
│  ·贡献者画像          ·降采样分析         ·影响力传播            │
│                                                                  │
│                    ↓                                             │
│              [Web Dashboard] 可视化决策层                         │
│              ·健康度仪表盘  ·预警大屏  ·趋势报告                  │
└─────────────────────────────────────────────────────────────────┘
```

## ✨ 核心功能

### 1. 六维健康度评估
- **活跃度** (Activity): 提交、PR、Issue活动水平
- **多样性** (Diversity): 贡献者数量和分布
- **响应速度** (Response Time): Issue/PR响应时间
- **代码质量** (Code Quality): PR审查率、测试覆盖率
- **文档完整度** (Documentation): README、Wiki质量
- **社区氛围** (Community): Issue关闭率、互动质量

### 2. 三级预警机制
- 🟢 **绿色**: 健康状态，持续监控
- 🟡 **黄色**: 贡献频率下降30%（提前1-2个月预警）
- 🟠 **橙色**: 社交网络连接减少50% + 活跃度骤降
- 🔴 **红色**: 核心贡献者即将离开（准确率>85%）

### 3. 协作网络分析
- 结构洞检测：识别关键"桥接者"
- 社区检测：发现协作子群
- 巴士因子计算：评估项目风险
- 影响力传播分析

### 4. 生命周期识别
- **Embryonic**: 萌芽期（<3个核心贡献者）
- **Growth**: 成长期（活跃度快速上升）
- **Mature**: 成熟期（稳定发展）
- **Decline**: 衰退期（活跃度下降>30%）

## 🚀 快速开始

### 前置要求

- Python 3.9+
- Docker & Docker Compose (推荐)
- 或手动安装：PostgreSQL 13+, Redis 6+, Apache IoTDB 1.3+

### 方式一：Docker Compose（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/hwk603/openPulse.git
cd openRank

# 2. 启动所有服务
docker-compose up -d

# 3. 等待服务启动（约30秒）
docker-compose ps

# 4. 访问服务
# API文档: http://localhost:8000/docs
# Web Dashboard: 打开 web-dashboard/index.html
```

### 方式二：本地开发

```bash
# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库连接

# 4. 启动PostgreSQL、Redis、IoTDB
# 使用Docker快速启动依赖服务：
docker-compose up -d postgres redis iotdb

# 5. 初始化数据库
python -c "from src.database import init_db; init_db()"

# 6. 启动API服务
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# 7. 启动Celery Worker（新终端）
celery -A src.tasks.celery_app worker --loglevel=info

# 8. 启动Celery Beat（新终端，可选）
celery -A src.tasks.celery_app beat --loglevel=info
```

## 📱 使用方式

### 1. Web Dashboard

打开 `web-dashboard/index.html` 在浏览器中：

```bash
# 使用Python简单HTTP服务器
cd web-dashboard
python -m http.server 8080
# 访问 http://localhost:8080
```

输入GitHub仓库（如 `apache/iotdb`）即可查看健康度分析。

### 2. Chrome浏览器插件

```bash
# 1. 打开Chrome扩展管理页面
chrome://extensions/

# 2. 启用"开发者模式"

# 3. 点击"加载已解压的扩展程序"

# 4. 选择 chrome-extension 目录

# 5. 访问任意GitHub仓库页面，查看健康度指标
```

### 3. API调用

#### 添加监控仓库

```bash
curl -X POST "http://localhost:8000/api/v1/repositories" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "github",
    "owner": "apache",
    "repo": "iotdb"
  }'
```

#### 评估社区健康度

```bash
curl -X POST "http://localhost:8000/api/v1/health-assessment" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "github",
    "owner": "apache",
    "repo": "iotdb"
  }'
```

#### 预测贡献者流失

```bash
curl -X POST "http://localhost:8000/api/v1/churn-prediction" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "github",
    "owner": "apache",
    "repo": "iotdb",
    "contributor_username": "example_user"
  }'
```

#### 分析协作网络

```bash
curl -X POST "http://localhost:8000/api/v1/network-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "github",
    "owner": "apache",
    "repo": "iotdb"
  }'
```

## 📊 API 文档

启动服务后访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 测试

### 测试套件概览

项目包含 **130+ 个测试用例**，覆盖所有核心功能模块：

| 测试模块 | 测试数量 | 覆盖范围 |
|---------|---------|---------|
| 数据采集 (OpenDigger) | 10 | API调用、错误处理、超时处理 |
| 存储层 (IoTDB) | 15 | CRUD操作、查询、批处理 |
| 图分析 (EasyGraph) | 15 | 网络构建、中心性、社区检测 |
| 业务服务 | 22 | 健康度评估、流失预测 |
| API接口 | 24 | REST端点、错误处理、CORS |
| 数据模型 | 17 | Pydantic & SQLAlchemy模型 |
| 异步任务 | 12 | Celery任务、调度、重试 |
| 集成测试 | 15 | 端到端工作流、性能测试 |

### 运行测试

```bash
# 安装测试依赖
pip install pytest pytest-cov pytest-asyncio pytest-xdist

# 运行所有测试
pytest tests/ -v

# 运行测试并生成覆盖率报告
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# 查看覆盖率报告
open htmlcov/index.html  # macOS/Linux
start htmlcov/index.html  # Windows

# 运行特定类型的测试
pytest -m unit          # 仅运行单元测试
pytest -m integration   # 仅运行集成测试
pytest -m performance   # 仅运行性能测试

# 并行运行测试（更快）
pytest tests/ -n auto

# 运行特定测试文件
pytest tests/test_api.py -v
pytest tests/test_services.py::TestHealthAssessmentService -v
```

### 测试覆盖率目标

- **目标覆盖率**: >80%
- **当前覆盖率**: 查看 `htmlcov/index.html` 获取详细报告
- **测试文档**: 详见 [tests/README.md](tests/README.md)

### 持续集成

项目配置了完整的 CI/CD 测试流程，每次提交都会自动运行测试套件。

## 📁 项目结构

```
openRank/
├── src/                          # 源代码
│   ├── api/                      # FastAPI应用
│   │   ├── main.py              # 主应用入口
│   │   └── routes/              # API路由
│   │       ├── health.py        # 健康检查
│   │       ├── analysis.py      # 健康度分析
│   │       ├── repositories.py  # 仓库管理
│   │       └── network.py       # 网络分析
│   ├── data_collection/         # 数据采集
│   │   └── opendigger_client.py # OpenDigger客户端
│   ├── storage/                 # 存储层
│   │   └── iotdb_client.py     # IoTDB客户端
│   ├── graph_analysis/          # 图分析
│   │   └── network_analyzer.py  # 网络分析器
│   ├── services/                # 业务服务
│   │   ├── health_assessment.py # 健康度评估
│   │   └── churn_prediction.py  # 流失预测
│   ├── tasks/                   # Celery任务
│   │   ├── celery_app.py       # Celery配置
│   │   ├── data_collection.py  # 数据采集任务
│   │   └── analysis.py         # 分析任务
│   ├── models/                  # 数据模型
│   │   ├── schemas.py          # Pydantic模型
│   │   └── database.py         # SQLAlchemy模型
│   ├── database.py              # 数据库连接
│   └── utils/                   # 工具函数
├── config/                      # 配置文件
│   └── settings.py             # 应用配置
├── tests/                       # 测试文件 (130+ 测试用例)
│   ├── conftest.py             # 测试配置和fixtures
│   ├── test_api.py             # API端点测试 (24个测试)
│   ├── test_models.py          # 数据模型测试 (17个测试)
│   ├── test_data_collection.py # OpenDigger客户端测试 (10个测试)
│   ├── test_storage.py         # IoTDB存储测试 (15个测试)
│   ├── test_graph_analysis.py  # 图分析测试 (15个测试)
│   ├── test_services.py        # 业务服务测试 (22个测试)
│   ├── test_tasks.py           # Celery任务测试 (12个测试)
│   ├── test_integration.py     # 集成测试 (15个测试)
│   └── README.md               # 测试文档
├── chrome-extension/            # Chrome浏览器插件
│   ├── manifest.json           # 插件配置
│   ├── popup.html              # 弹窗UI
│   ├── popup.js                # 弹窗逻辑
│   ├── content.js              # 内容脚本
│   ├── content.css             # 样式
│   └── background.js           # 后台脚本
├── web-dashboard/               # Web仪表盘
│   └── index.html              # 单页应用
├── docker-compose.yml           # Docker编排
├── Dockerfile                   # Docker镜像
├── requirements.txt             # Python依赖
├── pytest.ini                   # pytest配置
├── .env.example                # 环境变量示例
└── README.md                   # 项目文档
```

## 🎯 应用场景

### 1. 开源基金会项目健康管理
- 管理数百个孵化项目
- 提前3-6个月预警项目衰退风险
- 科学分配导师资源

### 2. 企业OSPO开源选型决策
- 构建"开源组件健康评分卡"
- 识别高风险依赖（巴士因子≤2）
- 为技术选型会议提供数据支撑

### 3. 开源项目Maintainer自助诊断
- 免费健康度评估
- 了解项目健康状况
- 优化社区运营策略

## 🔧 配置说明

### 环境变量

编辑 `.env` 文件配置：

```bash
# API配置
DEBUG=True
API_HOST=0.0.0.0
API_PORT=8000

# OpenDigger API
OPENDIGGER_API_URL=https://oss.x-lab.info/open_digger
OPENDIGGER_TIMEOUT=30

# Apache IoTDB
IOTDB_HOST=localhost
IOTDB_PORT=6667
IOTDB_USER=root
IOTDB_PASSWORD=root

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=openpulse
POSTGRES_PASSWORD=openpulse
POSTGRES_DB=openpulse

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 健康度评分权重

在 `config/settings.py` 中调整：

```python
HEALTH_SCORE_WEIGHTS = {
    "activity": 0.25,           # 活跃度权重
    "diversity": 0.15,          # 多样性权重
    "response_time": 0.15,      # 响应速度权重
    "code_quality": 0.15,       # 代码质量权重
    "documentation": 0.15,      # 文档完整度权重
    "community_atmosphere": 0.15 # 社区氛围权重
}
```

## 🐛 故障排查

### 问题1: IoTDB连接失败

```bash
# 检查IoTDB是否运行
docker-compose ps iotdb

# 查看IoTDB日志
docker-compose logs iotdb

# 重启IoTDB
docker-compose restart iotdb
```

### 问题2: API返回500错误

```bash
# 查看API日志
docker-compose logs api

# 检查数据库连接
docker-compose exec postgres psql -U openpulse -d openpulse -c "\dt"
```

### 问题3: Chrome插件无法加载

- 确保API服务运行在 `http://localhost:8000`
- 检查浏览器控制台错误信息
- 验证CORS配置（API已配置允许所有来源）

### 问题4: 数据采集失败

```bash
# 测试OpenDigger API连接
curl https://oss.x-lab.info/open_digger/github/apache/iotdb/openrank.json

# 检查Celery Worker状态
docker-compose logs celery-worker
```

### 问题5: 测试失败

```bash
# 确保安装了测试依赖
pip install pytest pytest-cov pytest-asyncio pytest-xdist

# 运行测试查看详细错误
pytest tests/ -v --tb=short

# 检查特定测试
pytest tests/test_api.py::TestHealthEndpoints::test_root_endpoint -v

# 查看测试覆盖率
pytest tests/ --cov=src --cov-report=term-missing
```

## 📝 开发指南

### 代码规范

```bash
# 格式化代码
black src/

# 代码检查
flake8 src/

# 类型检查
mypy src/
```

### 开发流程（TDD）

1. **编写测试** - 在 `tests/` 目录下编写测试用例
2. **运行测试** - 确保测试失败（红灯）
3. **实现功能** - 编写最小可行代码
4. **运行测试** - 确保测试通过（绿灯）
5. **重构代码** - 优化代码质量
6. **再次测试** - 确保重构后测试仍然通过

### 添加新的分析指标

1. 在 `src/models/schemas.py` 添加数据模型
2. 在 `tests/test_models.py` 添加模型测试
3. 在 `src/services/` 实现分析逻辑
4. 在 `tests/test_services.py` 添加服务测试
5. 在 `src/api/routes/` 添加API端点
6. 在 `tests/test_api.py` 添加API测试
7. 运行完整测试套件确保无回归

### 测试最佳实践

- ✅ 每个新功能都要有对应的测试
- ✅ 保持测试独立性，不依赖其他测试
- ✅ 使用 fixtures 复用测试数据
- ✅ Mock 外部依赖（API、数据库）
- ✅ 测试边界条件和异常情况
- ✅ 保持测试覆盖率 >80%

### 提交规范

遵循 Conventional Commits：

- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具相关

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 Apache 2.0 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

感谢以下开源项目：

- [OpenDigger](https://github.com/X-lab2017/open-digger) - 开源数据分析平台
- [Apache IoTDB](https://iotdb.apache.org/) - 时序数据库
- [EasyGraph](https://github.com/easy-graph/Easy-Graph) - 图分析库
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Web框架

## 📮 联系我们

- 项目主页: https://github.com/hwk603/openPulse
- 问题反馈: https://github.com/hwk603/openPulse/issues

## 🌟 Star History

如果这个项目对你有帮助，请给我们一个 Star ⭐️

---

**Let's keep open source alive and thriving!** 🚀
