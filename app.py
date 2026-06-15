"""
高中题目智能解答助手 - Streamlit 主界面
"""
import streamlit as st
import os
import tempfile
from dotenv import load_dotenv
from PIL import Image
from llm_client import get_answer_from_image

# 加载 .env 文件中的环境变量
load_dotenv()


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
    
    **1. MinerU API Token**
    - 访问 [MinerU](https://mineru.net/)
    - 注册/登录账号
    - 在控制台获取 API Token
    
    **2. 通义千问 API Key**
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
        help="用于图片识别的 API Token（可选）",
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
        ["🚀 快速模式", "✏️ 两步模式（可编辑）"],
        help="🚀 快速模式：MinerU识别后直接调用千问解答\n✏️ 两步模式：先展示MinerU识别结果，用户可编辑确认后再调用千问"
    )
    
    st.markdown("---")
    st.markdown("""
    ### 📖 快速开始
    
    1. **上传图片**：点击上传按钮，选择题目图片（JPG/PNG）
    2. **选择学科**：可手动选择或让系统自动检测
    3. **选择模式**：
       - 🚀 快速模式：MinerU识别后直接调用千问解答
       - ✏️ 两步模式：先查看并编辑MinerU识别结果，确认后再调用千问
    4. **开始处理**：点击“开始识别与解答”按钮
    5. **查看结果**：查看详细解答，可下载保存
    
    ### 💡 使用技巧
    
    - 📸 **图片质量**：确保图片清晰，光线充足，文字可读
    - 🎯 **单题效果**：单次上传一道题目效果最佳
    - 🔑 **API 配置**：首次使用需要在侧边栏配置 API Key（可在MinerU官网和阿里云官网免费申请）
    - 💰 **费用说明**：通义千问约 0.01-0.03 元/次，新用户有免费额度
    """)


# 主界面 - 文件上传
uploaded_file = st.file_uploader(
    "📤 上传题目图片",
    type=['jpg', 'jpeg', 'png'],
    help="支持 JPG、PNG 格式的图片"
)


def reset_two_step_state():
    """清空两步模式中依赖当前上传图片的状态。"""
    st.session_state.step2_markdown = None
    st.session_state.step2_edited_markdown = ""
    st.session_state.step2_manual_input = ""
    st.session_state.step2_submitted = False
    st.session_state.final_answer_result = None
    # 注意：不要在这里重置 uploaded_file_id，因为它用于检测文件是否变化


if 'step2_markdown' not in st.session_state:
    reset_two_step_state()


# 如果有上传的文件
if uploaded_file is not None:
    current_file_id = f"{uploaded_file.name}:{uploaded_file.size}"
    if st.session_state.get("uploaded_file_id") != current_file_id:
        st.session_state.uploaded_file_id = current_file_id
        reset_two_step_state()
    
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
            if not qwen_key:
                st.error("❌ 请在侧边栏配置通义千问 API Key（必须）")
                st.stop()
            
            if not mineru_token:
                st.error("❌ 请在侧边栏配置 MinerU API Token（必须）")
                st.stop()
            
            # 创建进度指示器
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # 步骤 1: 保存图片
                status_text.text("⏳ 正在保存图片...")
                progress_bar.progress(10)
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                    temp_path = tmp_file.name
                
                # 重新编码为标准 RGB JPEG，避免手机/微信图片的编码元信息导致 MinerU 读文件失败。
                image_for_upload = Image.open(uploaded_file)
                if image_for_upload.mode not in ("RGB", "L"):
                    image_for_upload = image_for_upload.convert("RGB")
                image_for_upload.save(temp_path, format="JPEG", quality=95)
                
                # 验证文件是否存在且有效
                if not os.path.exists(temp_path):
                    raise Exception(f"临时文件创建失败: {temp_path}")
                
                file_size = os.path.getsize(temp_path)
                print(f"临时文件已保存: {temp_path}, 大小: {file_size} bytes")
                
                # 步骤 2: 使用 MinerU 识别图片
                status_text.text("⏳ 步骤 1/3: 上传文件到 MinerU...")
                progress_bar.progress(20)
                
                # 导入 MinerU 客户端
                from mineru_client import parse_image_to_markdown
                
                markdown_text = parse_image_to_markdown(temp_path, mineru_token)
                progress_bar.progress(50)
                
                status_text.text("✅ MinerU 识别成功！")
                
                # 删除临时文件
                os.unlink(temp_path)
                
                # 根据模式进行不同处理
                if process_mode == "🚀 快速模式":
                    # 快速模式：直接调用千问生成解答
                    status_text.text("⏳ 步骤 2/2: 正在生成详细解答...")
                    progress_bar.progress(70)
                    
                    # 导入通义千问客户端
                    from llm_client import get_answer_from_qwen, detect_subject
                    
                    # 确定学科类型
                    if selected_subject == "自动检测":
                        subject = detect_subject(markdown_text)
                    else:
                        subject = selected_subject
                    
                    answer = get_answer_from_qwen(markdown_text, subject, qwen_key)
                    progress_bar.progress(100)
                    
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
                    # 两步模式：先保存识别结果。确认按钮会在按钮分支外渲染，
                    # 避免 Streamlit 重跑后外层按钮状态丢失。
                    progress_bar.progress(100)
                    status_text.text("✅ MinerU 识别完成，请确认识别内容")
                    st.session_state.step2_markdown = markdown_text
                    st.session_state.step2_edited_markdown = markdown_text
                    st.session_state.step2_manual_input = ""
                    st.session_state.step2_submitted = False
                    st.session_state.final_answer_result = None
                    st.rerun()

            except Exception as e:
                st.error(f"❌ 处理失败: {str(e)}")
                progress_bar.empty()
                status_text.empty()

        if process_mode == "✏️ 两步模式（可编辑）" and st.session_state.step2_markdown:
            st.markdown("---")
            
            if st.session_state.step2_submitted and st.session_state.final_answer_result:
                result = st.session_state.final_answer_result
                st.success("✅ 解答生成成功！")
                
                st.subheader("📚 详细解答")
                st.markdown(f"**学科类型**: {result['subject']}")
                st.markdown(result['answer'])
                
                st.download_button(
                    label="📥 下载解答文本",
                    data=result['answer'],
                    file_name=f"解答_{uploaded_file.name.split('.')[0]}.txt",
                    mime="text/plain"
                )
            else:
                st.success("✅ MinerU 识别成功！请查看并编辑识别结果")
                
                edited_markdown = st.text_area(
                    "✏️ 编辑识别结果（可直接修改）",
                    height=400,
                    help="如果识别有误，可以直接在这里修改。确认无误后点击下方按钮生成解答。",
                    key="step2_edited_markdown"
                )
                
                st.markdown("---")
                st.markdown("**💡 提示：** 如果识别结果完全错误，可以手动输入题目内容：")
                manual_input = st.text_area(
                    "📝 手动输入题目内容（可选）",
                    height=200,
                    placeholder="在此处手动输入题目内容...\n例如：\n已知函数 f(x) = x^2 + 2x + 1，求 f(3) 的值。",
                    key="step2_manual_input"
                )
                
                if manual_input.strip():
                    final_question = manual_input.strip()
                    st.info("ℹ️ 将使用手动输入的内容")
                else:
                    final_question = edited_markdown
                    st.info("ℹ️ 将使用编辑后的识别结果")
                
                confirm_button = st.button("✅ 确认无误，生成解答", type="primary", width='stretch', key="confirm_step2_btn")
                
                if confirm_button:
                    if not qwen_key:
                        st.error("❌ 请在侧边栏配置通义千问 API Key（必须）")
                        st.stop()
                    
                    if not final_question.strip():
                        st.error("❌ 题目内容为空，请先确认或手动输入题目内容")
                        st.stop()
                    
                    try:
                        with st.spinner('⏳ 正在生成详细解答，这可能需要 30秒-2分钟...'):
                            from llm_client import get_answer_from_qwen, detect_subject
                            
                            if selected_subject == "自动检测":
                                subject = detect_subject(final_question)
                            else:
                                subject = selected_subject
                            
                            answer = get_answer_from_qwen(final_question, subject, qwen_key)
                        
                        st.session_state.step2_submitted = True
                        st.session_state.final_answer_result = {
                            'subject': subject,
                            'answer': answer
                        }
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ 生成解答失败: {str(e)}")
                        st.markdown("**可能的原因：**")
                        st.markdown("- 通义千问 API Key 无效或过期")
                        st.markdown("- 网络连接问题")
                        st.markdown("- 题目内容过长")
                        st.markdown("\n**请检查侧边栏的 API 配置是否正确**")

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
