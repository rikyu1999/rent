import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ページ設定
st.set_page_config(page_title="一都三県・路線駅連動査定", layout="wide")

# --- 1. データ準備（本来はCSVから読み込みますが、コード内に主要サンプルを配置） ---
@st.cache_data
def get_data():
    # 路線名、駅名、平米単価のマスター
    data = [
        {"route": "西武新宿線", "station": "西武新宿", "price": 4100},
        {"route": "西武新宿線", "station": "高田馬場", "price": 4300},
        {"route": "西武新宿線", "station": "鷺ノ宮", "price": 3400},
        {"route": "西武新宿線", "station": "上石神井", "price": 3200},
        {"route": "西武新宿線", "station": "所沢", "price": 2800},
        {"route": "西武池袋線", "station": "池袋", "price": 4800},
        {"route": "西武池袋線", "station": "練馬", "price": 3800},
        {"route": "西武池袋線", "station": "石神井公園", "price": 3400},
        {"route": "JR山手線", "station": "新宿", "price": 5200},
        {"route": "JR山手線", "station": "恵比寿", "price": 5800},
        {"route": "JR山手線", "station": "目黒", "price": 5300},
        {"route": "JR中央線", "station": "中野", "price": 4200},
        {"route": "JR中央線", "station": "吉祥寺", "price": 4500},
        {"route": "JR中央線", "station": "立川", "price": 3200},
    ]
    return pd.DataFrame(data)

df = get_data()

st.title("🚉 首都圏 路線・駅連動 賃料査定プロ")

# --- 2. サイドバー：連動プルダウン ---
st.sidebar.header("【1】 所在設定")

# ① 路線を選択
selected_route = st.sidebar.selectbox("鉄道路線を選択", options=df["route"].unique())

# ② 選択された路線の駅だけに絞り込む
available_stations = df[df["route"] == selected_route]["station"].unique()
selected_station = st.sidebar.selectbox("対象駅を選択", options=available_stations)

# 選択された駅の単価を取得
base_unit_price = df[(df["route"] == selected_route) & (df["station"] == selected_station)].iloc[0]["price"]

st.sidebar.header("【2】 物件詳細")
b_type = st.sidebar.radio("建物種別", ["マンション", "アパート", "戸建て"])
sqm = st.sidebar.number_input("専有面積 (㎡)", value=25.0, step=1.0)
walk_min = st.sidebar.slider("駅徒歩 (分)", 1, 20, 5)
age = st.sidebar.slider("築年数 (年)", 0, 30, 5)

# --- 3. 査定ロジック ---
def calculate_rent():
    type_coeff = {"マンション": 1.0, "アパート": 0.88, "戸建て": 1.15}
    w_factor = 1.0 - (walk_min * 0.015) if walk_min <= 10 else 0.85 - ((walk_min-10) * 0.03)
    a_factor = 1.0 if age <= 2 else 0.98 - ((age-2) * 0.01)
    
    res = base_unit_price * sqm * w_factor * a_factor * type_coeff[b_type]
    return int(res)

rent = calculate_rent()

# --- 4. メイン表示 ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader(f"📍 {selected_route} / {selected_station}駅")
    st.metric("推定適正賃料（支払総額）", f"{rent:,} 円")
    
    # ゲージ表示
    prob = min(max(92 - (walk_min * 2) - (age * 1), 10), 98)
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = prob,
        gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#2ecc71"}},
        title = {'text': "成約期待値 (%)"}
    ))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("分析アドバイス")
    st.success(f"**マーケット状況:**\n{selected_route}沿線は安定した需要があり、特に{selected_station}駅周辺の{b_type}は、{sqm}㎡前後の広さで最も高い成約率を記録しています。")
    st.info(f"単価根拠: {base_unit_price:,}円/㎡")

    # PDFダウンロードボタン（枠だけ再配置）
    st.button("📄 査定報告書(PDF)をダウンロード")
