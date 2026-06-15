"""
简化版测试应用 - 用于演示基本功能
暂时使用模拟数据，后续可以接入真实的 MinerU API
"""
import streamlit as st
from PIL import Image
import time


# 页面配置
st.set_page_config(
    page_title="🎓 给你讲题的同桌",
    page_icon="🎓",
    layout="wide"
)

# 标题
st.title("🎓 给你讲题的同桌")
st.markdown("### 🌟 演示版本 - 展示基本功能")

# 文件上传
uploaded_file = st.file_uploader("📤 上传题目图片", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    # 显示图片
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📷 原图")
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
    
    with col2:
        st.subheader("⚙️ 处理选项")
        subject = st.selectbox("选择学科", ["数学", "语文", "英语", "物理", "化学"])
        
        if st.button("🚀 开始处理", type="primary"):
            # 模拟处理过程
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 步骤 1: 模拟识别
            status_text.text("⏳ 正在识别题目...")
            for i in range(30):
                progress_bar.progress((i + 1) * 2)
                time.sleep(0.05)
            
            # 模拟识别结果
            mock_markdown = """
### 识别结果

**第8题（多选题）** 设等差数列 {aₙ} 的前 n 项和为 Sₙ，若 a₂ < -a₁₃ < a₁，则（）

A. a₇ > 0  
B. a₈ < 0  
C. S₁₅ > 0  
D. 数列 {Sₙ/n} 是递减数列
            """
            
            with st.expander("📝 查看识别结果", expanded=True):
                st.markdown(mock_markdown)
            
            # 步骤 2: 模拟生成解答
            status_text.text("⏳ 正在生成解答...")
            for i in range(30, 60):
                progress_bar.progress((i + 1) * 2)
                time.sleep(0.05)
            
            # 模拟解答
            mock_answer = """
### 📚 详细解答

**考点分析：**
本题考查等差数列的性质和前 n 项和公式的应用。

**解题思路：**
1. 利用等差数列通项公式表示各项
2. 根据给定条件推导公差 d 的符号
3. 逐项判断各选项的正确性

**详细步骤：**

由已知条件 a₂ < -a₁₃ < a₁，可得：
- a₂ = a₁ + d
- a₁₃ = a₁ + 12d

代入得：a₁ + d < -(a₁ + 12d) < a₁

由此可推出：
1. 2a₁ + 13d < 0
2. a₁ > -6d

**逐项分析：**

✅ **A. a₇ > 0**
   - a₇ = a₁ + 6d
   - 由 a₁ > -6d 可得 a₇ > 0 ✓

✅ **B. a₈ < 0**
   - 经推导可知 d < 0
   - 因此 a₈ < 0 ✓

❌ **C. S₁₅ > 0**
   - S₁₅ = 15(a₁ + 7d)
   - 由于 a₈ < 0，所以 S₁₅ < 0 ✗

✅ **D. 数列 {Sₙ/n} 是递减数列**
   - Sₙ/n = a₁ + (n-1)d/2
   - 由于 d < 0，数列递减 ✓

**答案：ABD**

---

💡 **学习建议：**
掌握等差数列的基本公式和性质，注意不等式的灵活运用。
            """
            
            progress_bar.progress(100)
            status_text.text("✅ 完成！")
            
            st.markdown("---")
            st.subheader("✅ 解答结果")
            st.markdown(f"**学科**: {subject}")
            st.markdown(mock_answer)
            
            # 下载按钮
            st.download_button(
                label="📥 下载解答",
                data=mock_answer,
                file_name=f"解答.txt",
                mime="text/plain"
            )

# 使用说明
st.markdown("---")
st.markdown("""
### 💡 使用说明

这是一个**演示版本**，展示了应用的基本功能。

**完整版本需要：**
1. ✅ MinerU API Token（用于图片识别）
2. ✅ 通义千问 API Key（用于生成解答）

**下一步：**
- 获取 API Key 后，运行 `app.py` 即可使用完整功能
- 详见 README.md 文档
""")
