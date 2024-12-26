import re
import requests
import jieba
from collections import Counter
import streamlit as st
from pyecharts.charts import WordCloud, Bar, Pie, Line, Scatter, Radar, Funnel
from pyecharts import options as opts
from streamlit.components.v1 import html
from bs4 import BeautifulSoup

st.title("文本分析与词频可视化")
st.sidebar.title("功能选项")

url = st.sidebar.text_input("请输入文章的 URL:")
min_freq = st.sidebar.slider("最低词频筛选", 1, 10, 2)
chart_type = st.sidebar.selectbox(
    "选择可视化图表类型:",
    ["词云图", "柱状图", "饼图", "折线图", "散点图", "雷达图", "漏斗图"]
)

stopwords = set([
    "的", "了", "是", "在", "和", "有", "我", "他", "它", "这", "不", "人", "也", "都", "一个", "我们", "对", "为",
    "着", "要", "就"
])


# 抓取网页内容
def fetch_text(url):
    try:
        response = requests.get(url)
        response.encoding = "utf-8"
        return response.text
    except Exception as e:
        st.error(f"无法抓取 URL 内容: {e}")
        return None


# 清理文本内容（去除HTML标签和非中文字符）
def clean_text(text):
    # 去除HTML标签
    soup = BeautifulSoup(text, "html.parser")
    text = soup.get_text()
    # 正则去除非中文字符
    text = "".join(re.findall(r"[\u4e00-\u9fa5]", text))
    return text


# 分词与词频统计
def analyze_text(text, min_freq=1):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("输入的文本内容无效（为空或非字符串）。")

    # 清理文本
    cleaned_text = clean_text(text)
    # 分词
    words = jieba.lcut(cleaned_text)
    # 去除停用词
    words = [word for word in words if word not in stopwords and len(word) > 1]
    # 统计词频
    word_counts = Counter(words)
    # 筛选最低频
    word_counts = {word: count for word, count in word_counts.items() if count >= min_freq}
    return word_counts


# 生成词云图
def create_wordcloud(word_counts):
    wordcloud = (
        WordCloud()
        .add("", list(word_counts.items()), word_size_range=[20, 100])
        .set_global_opts(title_opts=opts.TitleOpts(title="词云图"))
    )
    return wordcloud


def render_chart(chart):
    html_content = chart.render_embed()
    html(html_content, height=600)


# 生成其他图表
def create_chart(word_counts, chart_type):
    data = list(word_counts.items())[:20]
    labels, values = zip(*data)

    if chart_type == "柱状图":
        chart = (
            Bar()
            .add_xaxis(list(labels))
            .add_yaxis("词频", list(values))
            .set_global_opts(title_opts=opts.TitleOpts(title="柱状图"))
        )
    elif chart_type == "饼图":
        chart = (
            Pie()
            .add("", data)
            .set_global_opts(title_opts=opts.TitleOpts(title="饼图"))
        )
    elif chart_type == "折线图":
        chart = (
            Line()
            .add_xaxis(list(labels))
            .add_yaxis("词频", list(values))
            .set_global_opts(title_opts=opts.TitleOpts(title="折线图"))
        )
    elif chart_type == "散点图":
        chart = (
            Scatter()
            .add_xaxis(list(labels))
            .add_yaxis("词频", list(values))
            .set_global_opts(title_opts=opts.TitleOpts(title="散点图"))
        )
    elif chart_type == "雷达图":
        max_value = max(values)
        radar = Radar()
        radar.add_schema(
            schema=[{"name": labels[i], "max": max_value} for i in range(len(labels))]
        )
        radar.add("词频", [list(values)])
        radar.set_global_opts(title_opts=opts.TitleOpts(title="雷达图"))
        chart = radar
    elif chart_type == "漏斗图":
        chart = (
            Funnel()
            .add("词频", data)
            .set_global_opts(title_opts=opts.TitleOpts(title="漏斗图"))
        )
    else:
        chart = create_wordcloud(word_counts)  # 默认词云图

    return chart

if url:
    text = fetch_text(url)

    if text:
        try:
            cleaned_text = clean_text(text)

            st.subheader("抓取的文章内容：")
            st.text_area("文章内容", cleaned_text, height=400)

            word_counts = analyze_text(text, min_freq=min_freq)
            st.subheader("分词结果：")
            top_words = Counter(word_counts).most_common(20)
            for word, freq in top_words:
                st.write(f"{word}: {freq}")

            chart = create_chart(word_counts, chart_type)
            render_chart(chart)

        except Exception as e:
            st.error(f"文本分析时出错: {e}")
    else:
        st.error("抓取的文本内容为空，请检查输入的 URL 是否有效。")
