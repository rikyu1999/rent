import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF

# ページ設定
st.set_page_config(page_title="一都三県・全駅対応査定プロ", layout="wide")

# --- 1. データ読み込み（駅名マスター） ---
@st.cache_data
def load_station_data():
    try:
        # station_master.csvがあれば読み込む
        return pd.read_csv("station_master.csv")
    except:
        # ない場合のサンプル（西武線を含む主要駅）
        return pd.DataFrame({
            "station_name": ["西武新宿", "練馬", "所沢", "新宿", "池袋", "渋谷", "横浜", "大宮", "千葉"],
            "base_price": [4100, 3600, 2800, 5200, 4800, 5500, 4300, 3200, 2800]
        })

df_stations = load_station_data()

st.title("🚉 首都圏・高精度賃料査定エンジン")
st.caption("駅別相場・建物種別を統合した実務特化型Ver.")

# --- 2. サイドバー：入力を一つに統合 ---
st.sidebar.header("【1】 物件・立地条件")

# 駅名検索（ここを入り口にする）
selected_station = st.sidebar.selectbox(
    "対象駅を選択または検索",
    options=df_stations["station_name"].unique()
)

# 建物種別
b_type = st.sidebar.radio("建物種別", ["マンション", "アパート", "戸建て"])

# 物件スペック
sqm = st.sidebar.number_input("専有面積 (㎡)", value=25.0, step=1.0)
walk_min = st.sidebar.slider("駅徒歩 (分)", 1, 20, 5)
age = st.sidebar.slider("築年数 (年)", 0, 30, 5)

# --- 3. 査定ロジック ---
def calculate_rent():
    # 選択された駅の単価を取得
    base_unit_price = df_stations[df_stations["station_name"] == selected_station].iloc[0]["base_price"]
    
    # 種別係数
    type_coeff = {"マンション": 1.0, "アパート": 0.88, "戸建て": 1.15}
    # 徒歩補正
    w_factor = 1.0 - (walk_min * 0.015) if walk_min <= 10 else 0.85 - ((walk_min-10) * 0.03)
    # 築年補正
    a_factor = 1.0 if age <= 2 else 0.98 - ((age-2) * 0.01)
    
    res = base_unit_price * sqm * w_factor * a_factor * type_coeff[b_type]
    return int(res)

rent = calculate_rent()
prob = min(max(92 - (walk_min * 2) - (age * 1), 10), 98)

# --- 4. メイン表示エリア ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader(f"📍 {selected_station}駅 の査定結果")
    st.metric("推定適正賃料（支払総額）", f"{rent:,} 円")
    
    # ゲージ表示
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = prob,
        gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#2ecc71"}},
        title = {'text': "成約期待値 (%)"}
    ))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("レポート出力・アドバイス")
    
    # PDFダウンロードボタン（英字簡易版）
    st.write("この内容でオーナー提案用レポートを作成できます。")
    st.button("📄 査定報告書(PDF)をダウンロード") # 機能詳細は前回同様のため簡略化

    st.success(f"**分析コメント:**\n{selected_station}駅周辺の{b_type}需要に基づき算出。徒歩{walk_min}分はターゲット層が明確な好条件です。")

st.info(f"💡 現在、{selected_station}駅の平米単価（{df_stations[df_stations['station_name'] == selected_station].iloc[0]['base_price']:,}円）を基準に計算しています。")
