# 🚀 部署到 Streamlit Cloud（完全免费）

让任何人都可以访问你的"给你讲题的同桌"应用！

## 📋 前置准备

1. **GitHub 账号**：如果没有，先注册一个
2. **通义千问 API Key**：用户需要自己提供

## 🔧 部署步骤

### 步骤 1：上传代码到 GitHub

#### 方法 A：使用 Git 命令行

```bash
# 进入项目目录
cd c:\Users\王奕博\Desktop\minerU_API

# 初始化 git
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: 给你讲题的同桌"

# 在 GitHub 创建新仓库（不要勾选 README）
# 然后关联远程仓库
git remote add origin https://github.com/你的用户名/mineru-solver.git

# 推送代码
git branch -M main
git push -u origin main
```

#### 方法 B：使用 GitHub Desktop（推荐新手）

1. 下载并安装 [GitHub Desktop](https://desktop.github.com/)
2. 打开 GitHub Desktop
3. 点击 "Add an existing repository"
4. 选择 `c:\Users\王奕博\Desktop\minerU_API` 文件夹
5. 点击 "Publish repository"
6. 填写仓库名称（如 `mineru-solver`）
7. 点击 "Publish"

### 步骤 2：部署到 Streamlit Cloud

1. **访问 Streamlit Cloud**
   - 打开 [https://streamlit.io/cloud](https://streamlit.io/cloud)
   - 点击 "Sign in with GitHub"

2. **创建新应用**
   - 点击 "New app"
   - 选择你的 GitHub 仓库（如 `your-username/mineru-solver`）
   - Branch: `main`
   - Main file path: `app.py`

3. **配置高级设置（可选）**
   - App URL: 自定义你的应用网址
   - 点击 "Deploy!"

4. **等待部署完成**
   - 大约需要 2-5 分钟
   - 部署成功后会显示应用链接

### 步骤 3：分享你的应用

部署完成后，你会得到一个类似这样的链接：
```
https://your-app-name.streamlit.app
```

把这个链接分享给任何人，他们都可以：
- ✅ 访问应用
- ✅ 上传题目图片
- ✅ 输入自己的 API Key
- ✅ 获得 AI 解答

## 💡 重要提示

### 关于 API Key

**用户需要自己提供 API Key：**

1. **通义千问 API Key（必须）**
   - 访问：[https://dashscope.aliyun.com/](https://dashscope.aliyun.com/)
   - 注册阿里云账号
   - 创建 API Key
   - 新用户有免费额度

2. **MinerU API Token（仅两步模式需要）**
   - 访问：[https://openxlab.org.cn/](https://openxlab.org.cn/)
   - 注册 OpenXLab 账号
   - 获取 API Token

### 费用说明

- **Streamlit Cloud**: 完全免费
- **通义千问**: 按使用量付费，约 0.01-0.03 元/次
- **MinerU**: 按使用量付费，约 0.1-0.5 元/次

### 安全提示

✅ **API Key 不会被保存**：用户输入的 API Key 仅在会话期间使用，关闭页面后自动清除

✅ **HTTPS 加密**：Streamlit Cloud 自动启用 HTTPS，保证数据传输安全

❌ **不要硬编码 API Key**：已在 `.gitignore` 中排除 `.env` 文件

##  优化建议

### 1. 添加自定义域名（可选）

如果需要更专业的网址：
1. 购买域名（如 `tutor.example.com`）
2. 在 Streamlit Cloud 设置中添加自定义域名
3. 配置 DNS CNAME 记录

### 2. 添加分析统计（可选）

在 `app.py` 中添加 Google Analytics 或其他统计工具，了解使用情况。

### 3. 定期更新

当你的代码有更新时：
```bash
git add .
git commit -m "更新说明"
git push
```
Streamlit Cloud 会自动重新部署！

## ❓ 常见问题

### Q: 部署后无法访问？
A: 检查：
- GitHub 仓库是否公开
- Streamlit Cloud 部署状态是否为 "Running"
- 防火墙是否阻止访问

### Q: 用户上传的图片会保存吗？
A: 不会。图片仅在临时处理中使用，处理后立即删除。

### Q: 如何限制使用次数？
A: Streamlit Cloud 免费版有限制，如需更多资源可升级到付费计划。

### Q: 可以商用吗？
A: 可以，但需遵守：
- Streamlit Cloud 的使用条款
- 通义千问和 MinerU 的 API 使用协议

## 🎉 恭喜！

现在你已经拥有一个公开的 AI 题目解答助手，任何高中生都可以使用它来帮助学习！

分享链接给你的同学、老师，让更多人受益吧！📚✨
