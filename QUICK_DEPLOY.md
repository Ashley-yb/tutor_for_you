# 🚀 5分钟快速部署指南

## 第一步：上传到 GitHub（2分钟）

### 最简单的方法 - 使用 GitHub Desktop

1. **下载 GitHub Desktop**
   - 访问：https://desktop.github.com/
   - 下载并安装

2. **发布仓库**
   - 打开 GitHub Desktop
   - 点击 "Add an existing repository"
   - 选择文件夹：`c:\Users\王奕博\Desktop\minerU_API`
   - 填写仓库名称：`tutor-app`（或你喜欢的名字）
   - 点击 "Publish repository"

✅ 完成！代码已上传到 GitHub

---

## 第二步：部署到 Streamlit Cloud（3分钟）

1. **访问 Streamlit Cloud**
   - 打开：https://streamlit.io/cloud
   - 点击 "Sign in with GitHub"
   - 授权访问你的 GitHub

2. **创建应用**
   - 点击 "New app"
   - Repository: 选择你刚创建的仓库（如 `your-username/tutor-app`）
   - Branch: `main`
   - Main file path: `app.py`
   - 点击 "Deploy!"

3. **等待部署**
   - 大约 2-3 分钟
   - 看到 "Running" 状态就成功了！

4. **获取链接**
   - 复制应用链接，类似：`https://tutor-app.streamlit.app`

✅ 完成！应用已公开部署

---

## 第三步：分享给用户

把链接发给任何人，他们就可以：

1. 打开链接
2. 上传题目图片
3. 输入自己的 API Key（首次使用需要）
4. 获得 AI 解答

### 用户如何获取 API Key？

**通义千问 API Key（必须）：**
1. 访问：https://dashscope.aliyun.com/
2. 注册阿里云账号
3. 创建 API Key
4. 新用户有免费额度

**MinerU API Token（可选，仅两步模式需要）：**
1. 访问：https://openxlab.org.cn/
2. 注册账号
3. 获取 Token

---

## 🎉 大功告成！

现在任何人都可以通过这个链接使用你的应用了！

### 后续更新

当你修改代码后：
1. 在 GitHub Desktop 中提交更改
2. 点击 "Push origin"
3. Streamlit Cloud 会自动重新部署（约1分钟）

---

## 💡 小贴士

- ✅ 完全免费
- ✅ HTTPS 加密，安全可靠
- ✅ API Key 不会被保存
- ✅ 自动处理高并发

有任何问题随时问我！😊
