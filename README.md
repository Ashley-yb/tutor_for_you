# 📚 高中题目智能解答助手

一个基于 AI 的高中题目识别与解答系统，帮助学生快速获取题目解析。

## ✨ 功能特点

- 📸 **图片识别**：自动识别题目图片中的文字和公式
- 🤖 **智能解答**：AI 教师生成详细的解题步骤
- 🎯 **多学科支持**：支持数学、语文、英语、物理、化学等科目
- 💻 **简单易用**：上传即用，无需复杂配置

## 🚀 快速开始

### 本地运行

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 运行应用

```bash
streamlit run app.py
```

浏览器会自动打开 http://localhost:8501

### 🌐 公开部署（推荐）

想让任何人都能访问？查看 [QUICK_DEPLOY.md](QUICK_DEPLOY.md) 或 [DEPLOY.md](DEPLOY.md)

**只需 5 分钟，完全免费！**

1. 上传代码到 GitHub
2. 部署到 Streamlit Cloud
3. 分享链接给用户

用户使用时需要自己提供 API Key。

## 📖 使用流程

1. **上传图片**：点击上传按钮，选择题目图片（JPG/PNG）
2. **选择学科**：可手动选择或让系统自动检测
3. **开始处理**：点击"开始识别与解答"按钮
4. **查看结果**：查看识别内容和详细解答

## 🔑 获取 API Key

### MinerU API Token

1. 访问 [OpenXLab](https://openxlab.org.cn/)
2. 注册/登录账号
3. 在控制台获取 API Token

### 通义千问 API Key

1. 访问 [阿里云 DashScope](https://dashscope.aliyun.com/)
2. 注册/登录阿里云账号
3. 创建 API Key
4. 新用户有免费额度可用

## 💰 费用说明

- **MinerU**: 按图片数量计费，约 0.1-0.5 元/次
- **通义千问**: qwen-turbo 模型价格低廉，新用户有免费额度

## 🛠️ 技术栈

- **前端**: Streamlit
- **图片识别**: MinerU (OCR)
- **大模型**: 通义千问 (Qwen)
- **语言**: Python 3.8+

## 📝 注意事项

- 确保图片清晰，文字可读
- 复杂公式可能需要手动校对
- 解答仅供参考，请独立思考
- 遵守 API 使用规范

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License
