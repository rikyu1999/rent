import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="一都三県・全駅網羅査定プロ", layout="wide")

# --- 1. データ読み込み（エラー対策付き） ---
@st.cache_data
def load_data():
    try:
        # アップロードしたCSVを読み込む
        return pd.read_csv("station_master.csv")
    except:
        # CSVがない場合に備えた、最低限のサンプルデータ
        return pd.DataFrame([
            {"route": "西武池袋線", "station": "池袋", "price": 4800},
            {"route": "西武池袋線", "station": "練馬", "price": 3800},
            {"route": "JR山手線", "station": "新宿", "price": 5200}
        ])

df = load_data()

st.title("🏘️ 一都三県・全駅網羅 賃料査定エンジン")

# --- 2. サイドバー：連動選択 ---
st.sidebar.header("【1】 所在地の選択")
all_routes = sorted(df["route"].unique())
sel_route = st.sidebar.selectbox("鉄道路線を選択", options=all_routes)

# その路線の駅だけに絞り込む
available_stations = sorted(df[df["route"] == sel_route]["station"].unique())
sel_station = st.sidebar.selectbox("対象駅を選択", options=available_stations)

# 単価取得
base_price = df[(df["route"] == sel_route) & (df["station"] == sel_station)]["price"].values[0]

st.sidebar.header("【2】 物件スペック")
b_type = st.sidebar.radio("建物種別", ["マンション", "アパート", "戸建て"])
sqm = st.sidebar.number_input("専有面積 (㎡)", value=25.0, step=0.5)
walk_min = st.sidebar.slider("駅徒歩 (分)", 1, 20, 5)
age = st.sidebar.slider("築年数 (年)", 0, 35, 5)

# --- 3. 査定ロジック ---
def calculate():
    type_map = {"マンション": 1.0, "アパート": 0.88, "戸建て": 1.12}
    w_factor = 1.0 - (walk_min * 0.012) if walk_min <= 10 else 0.88 - ((walk_min-10) * 0.025)
    a_factor = 1.0 - (age * 0.008) if age <= 10 else 0.92 - ((age-10) * 0.012)
    return int(base_price * sqm * w_factor * a_factor * type_map[b_type])

rent = calculate()

# --- 4. メイン画面 ---
st.subheader(f"📍 {sel_route} / {sel_station}駅")
st.metric("推定適正賃料（月額総額）", f"{rent:,} 円")
st.info(f"単価根拠: {base_price:,}円/㎡（支払総額ベース）")

prob = min(max(95 - (walk_min * 2.5) - (age * 1.2), 5), 98)
fig = go.Figure(go.Indicator(
    mode = "gauge+number", value = prob,
    gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#16a085"}},
    title = {'text': "成約期待値 (%)"}
))
st.plotly_chart(fig, use_container_width=True)
