import streamlit as st
import pandas as pd
import os
from pathlib import Path
import random
import json

# 页面配置
st.set_page_config(page_title="英文单词学习工具", layout="wide", initial_sidebar_state="expanded")

# 自定义样式
st.markdown("""
    <style>
    .big-word {
        font-size: 48px;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 20px;
    }
    .word-meaning {
        font-size: 24px;
        color: #2ca02c;
        text-align: center;
        padding: 15px;
        background-color: #f0f0f0;
        border-radius: 10px;
    }
    .stats {
        font-size: 18px;
        text-align: center;
        padding: 10px;
        background-color: #e7f3ff;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# 标题
col1, col2 = st.columns([3, 1])
with col1:
    st.title("📚 英文单词学习工具")
with col2:
    st.markdown("**v1.0**")

# 初始化会话状态
if 'words' not in st.session_state:
    st.session_state.words = []
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'learned_count' not in st.session_state:
    st.session_state.learned_count = 0
if 'show_meaning' not in st.session_state:
    st.session_state.show_meaning = False
if 'studied_words' not in st.session_state:
    st.session_state.studied_words = set()

# 侧边栏 - 文件选择
st.sidebar.header("📖 选择学习资料")

# 获取可用的文本文件
vocab_dir = Path(__file__).parent / "english-vocabulary-master"
txt_files = sorted([f.name for f in vocab_dir.glob("*.txt") if f.is_file()])

if not txt_files:
    st.sidebar.warning("⚠️ 未找到单词文件，请确保文件在 english-vocabulary-master 文件夹中")
else:
    selected_file = st.sidebar.selectbox(
        "选择要学习的单词表：",
        txt_files,
        help="选择不同难度的单词表进行学习"
    )
    
    # 加载单词
    if st.sidebar.button("🔄 加载单词", use_container_width=True):
        file_path = vocab_dir / selected_file
        try:
            words = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and '\t' in line:
                        parts = line.split('\t', 1)
                        if len(parts) == 2:
                            word, meaning = parts
                            words.append({'word': word.strip(), 'meaning': meaning.strip()})
            
            st.session_state.words = words
            st.session_state.current_index = 0
            st.session_state.learned_count = 0
            st.session_state.show_meaning = False
            st.session_state.studied_words = set()
            st.sidebar.success(f"✅ 成功加载 {len(words)} 个单词！")
        except Exception as e:
            st.sidebar.error(f"❌ 加载文件失败: {e}")

# 学习统计
st.sidebar.markdown("---")
st.sidebar.header("📊 学习统计")
if st.session_state.words:
    total = len(st.session_state.words)
    learned = st.session_state.learned_count
    progress = learned / total if total > 0 else 0
    
    st.sidebar.metric("总单词数", total)
    st.sidebar.metric("已学习", learned)
    st.sidebar.progress(progress, text=f"{progress:.1%}")

# 学习控制
st.sidebar.markdown("---")
st.sidebar.header("⚙️ 学习设置")
study_mode = st.sidebar.radio(
    "学习模式：",
    ["📝 顺序学习", "🎲 随机学习"],
    help="选择学习方式"
)

if study_mode == "🎲 随机学习" and st.session_state.words:
    if st.sidebar.button("🔀 随机打乱", use_container_width=True):
        random.shuffle(st.session_state.words)
        st.session_state.current_index = 0
        st.sidebar.success("✅ 已随机打乱单词顺序！")

# 主要内容区域
if not st.session_state.words:
    st.info('👈 请先在左侧选择单词表并点击"加载单词"开始学习')
else:
    # 当前单词
    current_word = st.session_state.words[st.session_state.current_index]
    
    # 显示单词
    st.markdown(f'<div class="big-word">{current_word["word"]}</div>', unsafe_allow_html=True)
    
    # 显示中文含义（可点击按钮显示/隐藏）
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("👁️ 查看含义", use_container_width=True, key="show_meaning_btn"):
            st.session_state.show_meaning = not st.session_state.show_meaning
    
    with col2:
        if st.button("✅ 已掌握", use_container_width=True, key="learned_btn"):
            if current_word['word'] not in st.session_state.studied_words:
                st.session_state.studied_words.add(current_word['word'])
                st.session_state.learned_count += 1
            st.session_state.show_meaning = False
    
    with col3:
        if st.button("⏭️ 下一个", use_container_width=True, key="next_btn"):
            st.session_state.current_index = (st.session_state.current_index + 1) % len(st.session_state.words)
            st.session_state.show_meaning = False
    
    # 条件显示含义
    if st.session_state.show_meaning:
        st.markdown(f'<div class="word-meaning">{current_word["meaning"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="word-meaning">点击"查看含义"显示中文解释</div>', unsafe_allow_html=True)
    
    # 进度显示
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="stats">📍 当前: {st.session_state.current_index + 1} / {len(st.session_state.words)}</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stats">✅ 已掌握: {st.session_state.learned_count}</div>', unsafe_allow_html=True)
    with col3:
        progress_pct = (st.session_state.learned_count / len(st.session_state.words) * 100) if st.session_state.words else 0
        st.markdown(f'<div class="stats">🎯 进度: {progress_pct:.1f}%</div>', unsafe_allow_html=True)
    
    # 快速导航
    st.markdown("---")
    st.subheader("🔍 快速导航")
    col1, col2 = st.columns(2)
    with col1:
        jump_to = st.number_input("跳转到第几个单词：", min_value=1, max_value=len(st.session_state.words), value=st.session_state.current_index + 1)
        if st.button("跳转", use_container_width=True):
            st.session_state.current_index = jump_to - 1
            st.session_state.show_meaning = False
            st.rerun()
    
    with col2:
        search_word = st.text_input("搜索单词：", placeholder="输入英文单词")
        if search_word:
            matches = [i for i, w in enumerate(st.session_state.words) if w['word'].lower().startswith(search_word.lower())]
            if matches:
                st.session_state.current_index = matches[0]
                st.session_state.show_meaning = False
                st.success(f"✅ 找到 {len(matches)} 个匹配的单词")
                st.rerun()
            else:
                st.warning("❌ 未找到匹配的单词")

# 页脚
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("💡 提示：使用键盘快捷键可以更快速地学习")
with col2:
    st.caption("📚 单词来源: english-vocabulary-master")
with col3:
    st.caption("🎯 坚持学习，加油💪")
