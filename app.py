import streamlit as st
import plotly.graph_objects as go

# ページ設定
st.set_page_config(page_title="一都三県・プロ仕様査定", layout="wide")

st.title("🏘️ 一都三県・建物種別対応 賃料査定エンジン")
st.caption("マンション・アパート・戸建ての構造特性とエリアランクを反映した最新Ver.")

# --- サイドバー入力 ---
st.sidebar.header("【1】 物件属性")
# 建物種別の選択を追加
b_type = st.sidebar.radio("建物種別", ["マンション", "アパート", "戸建て"])

# エリアランクの定義（一都三県を想定）
area_rank = st.sidebar.selectbox("エリアランク", [
    "S: 都心5区・主要ターミナル駅直結", 
    "A: 23区人気住宅街・横浜/川崎中心部", 
    "B: 23区外縁・多摩・さいたま・千葉中心", 
    "C: 一都三県郊外・バス便エリア"
])

st.sidebar.header("【2】 形状・立地")
sqm = st.sidebar.number_input("専有面積 (㎡)", value=25.0, step=1.0)
walk_min = st.sidebar.slider("駅徒歩 (分)", 1, 20, 5)
age = st.sidebar.slider("築年数 (年)", 0, 30, 5)

st.sidebar.header("【3】 付加価値設備")
has_luxury = st.sidebar.checkbox("ハイグレード設備（床暖房・食洗機等）")
has_security = st.sidebar.checkbox("高度セキュリティ（内廊下・有人管理）")

# --- 凄腕査定ロジック ---
def calculate_advanced_rent():
    # 1. エリア別基本単価（平米単価）
    base_prices = {"S": 5500, "A": 4200, "B": 3200, "C": 2400}
    rank_key = area_rank[0] 
    price = base_prices[rank_key]

    # 2. 建物種別補正
    # マンションを1.0とし、アパートは管理・遮音性でマイナス、戸建ては希少性でプラス
    type_coeff = {"マンション": 1.0, "アパート": 0.88, "戸建て": 1.15}
    
    # 3. 駅徒歩補正（7分、10分を境に下落率を変化させる非線形ロジック）
    if walk_min <= 7:
        w_factor = 1.0 - (walk_min * 0.01)
    elif walk_min <= 10:
        w_factor = 0.93 - ((walk_min - 7) * 0.02)
    else:
        w_factor = 0.87 - ((walk_min - 10) * 0.04)
    
    # 4. 築年数補正（築5年までは「新築・築浅プレミアム」で維持）
    if age <= 5:
        a_factor = 1.0 - (age * 0.005)
    else:
        a_factor = 0.97 - ((age - 5) * 0.012)

    # 5. 基本計算
    core_rent = price * sqm * w_factor * a_factor * type_coeff[b_type]
    
    # 6. 設備加点
    if has_luxury: core_rent += (sqm * 200) # 平米あたり200円加算
    if has_security: core_rent += 5000       # 月額5,000円加算
    
    return int(core_rent)

rent = calculate_advanced_rent()

# --- 画面表示 ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("査定結果")
    st.metric("推定適正家賃", f"{rent:,} 円")
    
    # 成約確率の可視化
    prob = 90 - (walk_min * 2) - (age * 1)
    if b_type == "戸建て": prob += 5 # 戸建ては希少なため成約しやすい
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = min(max(prob, 10), 98),
        gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#1f77b4"}},
        title = {'text': "1ヶ月以内の成約期待値 (%)"}
    ))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("査定の根拠と戦略")
    st.write(f"● **建物種別補正**: {b_type}特有の需要を反映しました。")
    st.write(f"● **立地評価**: {area_rank}における駅徒歩{walk_min}分の希少性を算出。")
    
    if age <= 5:
        st.success("✨ **築浅プレミアム適用**: 建築費高騰により、この築年数は新築検討層を取り込める強い訴求力があります。")
    
    st.warning("⚠️ **現場からの助言**: この金額は「成約」を目的とした実利的な数値です。ポータルの見せかけの募集価格に合わせず、このラインで勝負することをお勧めします。")

st.markdown("---")
st.caption("※本システムは統計データに基づいた推計であり、物件の個別状態（眺望・リフォーム状況等）により変動します。")
