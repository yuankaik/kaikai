---
name: awesome-go-reference
description: Go 生态精选参考库——87 个分类、数千个库。来自 avelino/awesome-go (175K⭐)。搜索 Go 库时不靠猜测，从社区维护的权威列表中查找。
source: https://github.com/avelino/awesome-go
---

# Awesome Go 参考库

> Go 生态系统的权威精选列表，87 个分类，社区持续维护。
> 来源：avelino/awesome-go (175K ⭐)

## 使用场景

当用户问"Go 有什么好的 XXX 库？"时，不要凭记忆猜测。使用 awesome-go 查找社区验证的推荐。

触发词：Go 库、Go 框架、Go 工具、golang library、Go package

## 如何使用

### 方法 1：在线搜索（推荐）

直接在 GitHub 上搜索 README：

```
https://github.com/avelino/awesome-go
```

按分类浏览，或 Ctrl+F 搜索关键词。

### 方法 2：本地克隆

```bash
# 首次使用
git clone --depth 1 https://github.com/avelino/awesome-go.git /tmp/awesome-go

# 搜索某个分类
grep -i "关键词" /tmp/awesome-go/README.md

# 更新
cd /tmp/awesome-go && git pull
```

### 方法 3：结构化查询（有 Go 环境时）

```bash
cd /tmp/awesome-go
# 该仓库自带 Go 程序，可解析 README 为结构化数据
go run .  # 生成 HTML 站点到 out/ 目录
```

## 主要分类速查

| 分类 | 典型库 |
|------|--------|
| Web Frameworks | gin, echo, fiber, chi |
| Databases | gorm, sqlx, ent, pgx |
| CLI | cobra, urfave/cli, bubbletea |
| Testing | testify, ginkgo, go-sqlmock |
| Configuration | viper, koanf, envconfig |
| Logging | zap, zerolog, logrus |
| HTTP Clients | resty, grequests, heimdall |
| Auth & OAuth | casbin, go-oauth2, jwt-go |
| Message Queues | nats-go, sarama (Kafka), amqp |
| Caching | go-redis, bigcache, freecache |
| AI / ML | langchaingo, ollama, chromem-go |
| Microservices | go-kit, go-micro, kratos |
| DevOps | terraform, docker, kubernetes client-go |
| JSON | easyjson, jsoniter, gjson |
| Validation | validator, ozzo-validation |
| Job Scheduler | gocron, cron, go-flow |
| Serialization | protobuf, msgpack, avro |
| Security | age, acra, teler |

## 技巧

1. **不只找名字**：README 包含每个库的一句话描述，看完再推荐
2. **关注活跃度**：优先推荐有最近提交的库
3. **看许可证**：README 标注了许可证类型
4. **同类对比**：很多分类有多个选择，帮用户对比
