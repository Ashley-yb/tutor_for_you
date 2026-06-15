"""
高中题目智能解答助手 - Streamlit 主界面
"""
import streamlit as st
import os
import tempfile
from PIL import Image
from mineru_client import parse_image_to_markdown
from llm_client import get_answer_from_qwen, get_answer_from_image, detect_subject


# 页面配置
st.set_page_config(
    page_title="🎓 给你讲题的同桌",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# 自定义 CSS 样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
    }
    .step-indicator {
        display: flex;
        justify-content: space-around;
        margin: 2rem 0;
    }
    .step {
        text-align: center;
        padding: 0.5rem;
    }
    .step-number {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: #1E88E5;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 0.5rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# 标题
st.markdown('<div class="main-header">🎓 给你讲题的同桌</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">上传题目图片，AI 自动识别并生成详细解答</div>', unsafe_allow_html=True)


# 侧边栏 - API 配置
with st.sidebar:
    st.header("⚙️ API 配置")
    
    st.markdown("""
    ### 🔑 获取 API Key
    
    本应用需要您提供自己的 API Key：
    
    **1. MinerU API Token**（两步模式需要）
    - 访问 [MinerU](https://mineru.net/)
    - 注册/登录账号
    - 在控制台获取 API Token
    
    **2. 通义千问 API Key**（必须）
    - 访问 [阿里云 DashScope](https://dashscope.aliyun.com/)
    - 注册/登录阿里云账号
    - 创建 API Key
    - 新用户有免费额度可用
    
    💡 **提示**：您的 API Key 仅用于本次会话，不会被保存
    """)
    
    st.markdown("---")
    
    # MinerU API Token
    mineru_token = st.text_input(
        "MinerU API Token",
        value="",
        type="password",
        help="用于图片识别的 API Token（仅两步模式需要）",
        key="mineru_token_input"
    )
    
    # 通义千问 API Key
    qwen_key = st.text_input(
        "通义千问 API Key",
        value="",
        type="password",
        help="用于生成解答的 API Key（必须）",
        key="qwen_key_input"
    )
    
    # 处理模式选择
    process_mode = st.radio(
        "处理模式",
        ["🚀 快速模式（推荐）", "📝 两步模式"],
        help=" 快速模式：使用视觉模型直接识别并解答（更快、更简单）\n 两步模式：先OCR识别为文本，再生成解答（可查看中间结果）"
    )
    
    st.markdown("---")
    st.markdown("""
    ### 📖 快速开始
    
    1. **上传图片**：点击上传按钮，选择题目图片（JPG/PNG）
    2. **选择学科**：可手动选择或让系统自动检测
    3. **选择模式**：
       - 🚀 快速模式：一步到位，直接识别并解答（推荐）
       - 📝 两步模式：先查看识别结果，再生成解答
    4. **开始处理**：点击“开始识别与解答”按钮
    5. **查看结果**：查看详细解答，可下载保存
    
    ### 💡 使用技巧
    
    - 📸 **图片质量**：确保图片清晰，光线充足，文字可读
    - 🎯 **单题效果**：单次上传一道题目效果最佳
    -  **API 配置**：首次使用需要在侧边栏配置 API Key（可在MinerU官网和阿里云官网免费申请）
    -  **费用说明**：通义千问 VL 约 0.01-0.03 元/次，新用户有免费额度
    """)


# 主界面 - 文件上传
uploaded_file = st.file_uploader(
    "📤 上传题目图片",
    type=['jpg', 'jpeg', 'png'],
    help="支持 JPG、PNG 格式的图片"
)


# 如果有上传的文件
if uploaded_file is not None:
    # 显示上传的图片
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📷 原图预览")
        image = Image.open(uploaded_file)
        st.image(image, width='stretch')
    
    with col2:
        st.subheader("⚙️ 处理选项")
        
        # 学科选择（自动检测或手动选择）
        subject_options = ["自动检测", "数学", "语文", "英语", "物理", "化学", "生物", "政治", "历史", "地理"]
        selected_subject = st.selectbox("选择学科类型", subject_options)
        
        # 开始处理按钮
        process_button = st.button(" 开始识别与解答", type="primary", width='stretch')
        
        if process_button:
            # 检查 API 配置
            if not mineru_token:
                st.error("❌ 请在侧边栏配置 MinerU API Token")
                st.stop()
            
            if not qwen_key:
                st.error("❌ 请在侧边栏配置通义千问 API Key")
                st.stop()
            
            # 创建进度指示器
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # 步骤 1: 保存图片
                status_text.text("⏳ 步骤 1/3: 正在保存图片...")
                progress_bar.progress(10)
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    temp_path = tmp_file.name
                
                # 步骤 2: 根据模式处理
                if process_mode == "🚀 快速模式（推荐）":
                    # 快速模式：直接使用 VL 模型识别并解答
                    status_text.text("⏳ 正在识别题目并生成解答...")
                    progress_bar.progress(40)
                    
                    # 确定学科类型
                    if selected_subject == "自动检测":
                        subject = "综合"  # VL 模型会自动识别
                    else:
                        subject = selected_subject
                    
                    answer = get_answer_from_image(temp_path, subject, qwen_key)
                    progress_bar.progress(100)
                    
                    # 删除临时文件
                    os.unlink(temp_path)
                    
                    status_text.text("✅ 完成！")
                    
                    # 显示结果
                    st.success("✅ 识别与解答成功！")
                    
                    st.markdown("---")
                    st.subheader("📚 详细解答")
                    st.markdown(f"**学科类型**: {subject}")
                    st.markdown(answer)
                    
                    # 添加下载按钮
                    st.download_button(
                        label="📥 下载解答文本",
                        data=answer,
                        file_name=f"解答_{uploaded_file.name.split('.')[0]}.txt",
                        mime="text/plain"
                    )
                    
                else:
                    # 两步模式：先识别，再解答
                    status_text.text("⏳ 步骤 2/3: 正在识别题目内容...")
                    progress_bar.progress(40)
                    
                    markdown_text = parse_image_to_markdown(temp_path, mineru_token)
                    progress_bar.progress(70)
                    
                    # 删除临时文件
                    os.unlink(temp_path)
                    
                    # 显示识别结果
                    st.success("✅ 图片识别成功！")
                    
                    with st.expander("📝 查看识别结果（点击展开）", expanded=False):
                        st.markdown(markdown_text)
                    
                    # 步骤 3: 调用大模型生成解答
                    status_text.text("⏳ 步骤 3/3: 正在生成详细解答...")
                    progress_bar.progress(85)
                    
                    # 确定学科类型
                    if selected_subject == "自动检测":
                        subject = detect_subject(markdown_text)
                    else:
                        subject = selected_subject
                    
                    answer = get_answer_from_qwen(markdown_text, subject, qwen_key)
                    progress_bar.progress(100)
                    
                    status_text.text("✅ 完成！")
                    
                    # 显示最终结果
                    st.markdown("---")
                    st.subheader("📚 详细解答")
                    st.markdown(f"**学科类型**: {subject}")
                    st.markdown(answer)
                    
                    # 添加复制按钮
                    st.download_button(
                        label="📥 下载解答文本",
                        data=answer,
                        file_name=f"解答_{uploaded_file.name.split('.')[0]}.txt",
                        mime="text/plain"
                    )
                
            except Exception as e:
                st.error(f"❌ 处理失败: {str(e)}")
                progress_bar.empty()
                status_text.empty()


# 示例展示区
else:
    st.markdown("---")
    st.subheader("💡 使用示例")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **1️⃣ 上传题目图片**
        
        点击上传按钮，选择包含题目的图片文件
        """)
    
    with col2:
        st.markdown("""
        **2️⃣ AI 自动识别**
        
        系统自动识别图片中的文字和公式
        """)
    
    with col3:
        st.markdown("""
        **3️⃣ 获取详细解答**
        
        AI 教师生成专业的解题步骤和答案
        """)
    
    # 注意事项
    st.markdown("""
    ### ⚠️ 注意事项
    
    - 📸 **图片质量**：请确保图片清晰，光线充足，文字可读
    - 📐 **公式识别**：复杂的数学公式可能需要手动校对
    - 🔑 **API 配置**：首次使用需要在侧边栏配置 API Token（可在MinerU官网和阿里云官网免费申请）
    - 💰 **费用说明**：MinerU 和通义千问均按使用量计费
    """)


# 页脚
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #999; font-size: 0.9rem;'>
        Made with ❤️ for High School Students | Powered by MinerU & Qwen
    </div>
    """,
    unsafe_allow_html=True
)
