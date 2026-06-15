# ✅ 部署前检查清单

在部署到 Streamlit Cloud 之前，请确认以下事项：

## 📋 代码准备

- [ ] 所有 Python 文件已创建
  - [x] app.py（主应用）
  - [x] mineru_client.py
  - [x] llm_client.py
  - [x] demo_app.py（可选）

- [ ] 配置文件已创建
  - [x] requirements.txt
  - [x] .gitignore
  - [x] .streamlit/config.toml

- [ ] 文档已完善
  - [x] README.md
  - [x] DEPLOY.md
  - [x] QUICK_DEPLOY.md
  - [x] PROJECT_SUMMARY.md

## 🔐 安全配置

- [ ] `.env` 文件已添加到 `.gitignore`
- [ ] API Key 已从代码中移除（使用用户输入）
- [ ] 敏感信息不会上传到 GitHub

## 🧪 本地测试

- [ ] 应用可以正常运行
  ```bash
  streamlit run app.py
  ```
- [ ] 上传图片功能正常
- [ ] API 调用功能正常
- [ ] 错误处理正常

## 📦 Git 准备

- [ ] 已安装 Git 或 GitHub Desktop
- [ ] 已注册 GitHub 账号
- [ ] 已创建新仓库（公开）

##  部署步骤

### 1. 上传到 GitHub

```bash
# 初始化 git（如果还没有）
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: 给你讲题的同桌"

# 关联远程仓库
git remote add origin https://github.com/你的用户名/仓库名.git

# 推送
git branch -M main
git push -u origin main
```

或使用 GitHub Desktop：
1. 打开 GitHub Desktop
2. Add existing repository → 选择项目文件夹
3. Publish repository

### 2. 部署到 Streamlit Cloud

1. 访问：https://streamlit.io/cloud
2. Sign in with GitHub
3. New app
4. 选择仓库
5. Branch: main
6. Main file path: app.py
7. 点击 Deploy!

### 3. 验证部署

- [ ] 应用状态为 "Running"
- [ ] 可以访问应用链接
- [ ] 页面正常显示
- [ ] 可以上传图片
- [ ] 可以输入 API Key
- [ ] 可以获得解答

## 🎯 上线后检查

- [ ] 分享链接给朋友测试
- [ ] 确认不同浏览器都能访问
- [ ] 确认移动端显示正常
- [ ] 收集用户反馈

## 💡 常见问题

### Q: 部署后看不到图片？
A: 检查图片路径是否正确，确保使用相对路径。

### Q: API 调用失败？
A: 确认用户输入的 API Key 正确，检查网络连接。

### Q: 应用加载很慢？
A: Streamlit Cloud 免费版有一定限制，考虑优化代码或升级计划。

### Q: 如何更新代码？
A: 
```bash
git add .
git commit -m "更新说明"
git push
```
Streamlit Cloud 会自动重新部署。

##  完成！

如果以上所有项都已完成，恭喜你！应用已成功部署！

现在可以：
- 分享链接给用户
- 收集使用反馈
- 持续优化改进

---

**提示**：保存此清单，每次更新部署时都可以参考！
