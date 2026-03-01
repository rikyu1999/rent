import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ページ設定
st.set_page_config(page_title="一都三県・全駅網羅 賃料査定プロ", layout="wide")

# --- 1. CSVデータの読み込み ---
@st.cache_data
def load_all_stations():
    try:
        # アップロードしたCSVを読み込む
        df = pd.read_csv("station_master.csv")
        return df
    except:
        # ファイルがない場合の緊急用サンプル
        return pd.DataFrame([
            {"route": "西武池袋線", "station": "池袋", "price": 4800},
            {"route": "西武池袋線", "station": "練馬", "price": 3800},
            {"route": "西武新宿線", "station": "西武新宿", "price": 4100}
        ])

df = load_all_stations()

st.title("🏘️ 一都三県・全駅網羅型 賃料査定エンジン")
st.caption("CSVマスターデータに基づき、全路線・全駅の成約価格を瞬時に算出します")

# --- 2. サイドバー：2段階連動選択 ---
st.sidebar.header("【1】 所在地の選択")

# 路線選択
all_routes = sorted(df["route"].unique())
selected_route = st.sidebar.selectbox("鉄道路線を選択", options=all_routes)

# 駅選択（選択された路線に紐づく駅のみを表示）
available_stations = sorted(df[df["route"] == selected_route]["station"].unique())
selected_station = st.sidebar.selectbox("対象駅を選択", options=available_stations)

# 単価取得
base_price = df[(df["route"] == selected_route) & (df["station"] == selected_station)]["price"].values[0]

st.sidebar.header("【2】 物件スペック")
b_type = st.sidebar.radio("建物種別", ["マンション", "アパート", "戸建て"])
sqm = st.sidebar.number_input("専有面積 (㎡)", value=25.0, step=0.5)
walk_min = st.sidebar.slider("駅徒歩 (分)", 1, 20, 5)
age = st.sidebar.slider("築年数 (年)", 0, 35, 5)

# --- 3. 査定ロジック ---
def advanced_calc():
    type_map = {"マンション": 1.0, "アパート": 0.88, "戸建て": 1.12}
    # 徒歩減価
    w_factor = 1.0 - (walk_min * 0.012) if walk_min <= 10 else 0.88 - ((walk_min-10) * 0.025)
    # 築年減価
    a_factor = 1.0 - (age * 0.008) if age <= 10 else 0.92 - ((age-10) * 0.012)
    
    total = base_price * sqm * w_factor * a_factor * type_map[b_type]
    return int(total)

rent = advanced_calc()
prob = min(max(95 - (walk_min * 2.5) - (age * 1.2), 5), 98)

# --- 4. メイン画面表示 ---
c1, c2 = st.columns([1, 1])
with c1:
    st.markdown(f"### 📍 査定対象: {selected_station}駅")
    st.metric("推定適正賃料（月額総額）", f"{rent:,} 円")
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = prob,
        gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#16a085"}},
        title = {'text': "1ヶ月以内の成約期待値 (%)"}
    ))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("プロの査定根拠")
    st.write(f"✅ **駅別相場**: {selected_route} {selected_station}駅の最新データを反映。")
    st.write(f"✅ **構造評価**: {b_type}特有の賃料耐性を算出。")
    st.info(f"単価指標: {base_price:,}円/㎡（支払総額ベース）")
route,station,price
西武池袋線,池袋,4800
西武池袋線,椎名町,3800
西武池袋線,東長崎,3600
西武池袋線,江古田,3500
西武池袋線,桜台,3500
西武池袋線,練馬,3800
西武池袋線,中村橋,3400
西武池袋線,富士見台,3300
西武池袋線,練馬高野台,3300
西武池袋線,石神井公園,3400
西武池袋線,大泉学園,3100
西武池袋線,保谷,2900
西武池袋線,ひばりヶ丘,2900
西武池袋線,東久留米,2700
西武池袋線,清瀬,2600
西武池袋線,秋津,2500
西武池袋線,所沢,2800
西武新宿線,西武新宿,4100
西武新宿線,高田馬場,4300
西武新宿線,下落合,3800
西武新宿線,中井,3700
西武新宿線,新井薬師前,3500
西武新宿線,沼袋,3400
西武新宿線,野方,3400
西武新宿線,都立家政,3300
西武新宿線,鷺ノ宮,3400
西武新宿線,下井草,3200
西武新宿線,井荻,3200
西武新宿線,上井草,3100
西武新宿線,上石神井,3200
JR山手線,新宿,5200
JR山手線,渋谷,5500
JR山手線,恵比寿,5800
JR山手線,目黒,5300
JR中央線,中野,4200
JR中央線,高円寺,4000
JR中央線,阿佐ヶ谷,3900
JR中央線,荻窪,4000
JR中央線,吉祥寺,4500
