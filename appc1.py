import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(page_title="Tính Tiền Điện Phòng 307A", page_icon="⚡", layout="centered")

st.title("⚡ Tính Tiền Điện Phòng 307A")
st.write("Tự động lấy dữ liệu trực tiếp từ **Cột 1 (Tên)** và **Cột 32 (Số ngày)** trên Google Sheet.")

# Danh sách 6 thành viên cố định
danh_sach_thanh_vien = [
    "Hà Phương Anh",
    "Phương Ly",
    "Nguyễn Thị Phương Anh",
    "Loan",
    "Mến",
    "Nguyễn Phương Anh"
]

# 1. Nhập tổng số tiền điện
st.subheader("1. Tổng tiền điện")
tong_tien = st.number_input(
    "Nhập tổng tiền điện tháng này (VNĐ):",
    min_value=0,
    value=1500000,
    step=10000,
    format="%d"
)

st.markdown("---")

# 2. Đọc duy nhất Cột 1 và Cột 32 từ Google Sheet
st.subheader("2. Dữ liệu từ Google Sheet")

col_head1, col_head2 = st.columns([3, 1])
with col_head2:
    if st.button("🔄 Làm mới Sheet"):
        st.cache_data.clear()
        st.rerun()

SHEET_ID = "1lanmHwXOPIM_6KV0inZV2KFdP1Xmy3k7uUljA3yyvvM"
SHEET_NAME = "Sheet1"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

so_ngay_dict = {ten: 0.0 for ten in danh_sach_thanh_vien}

try:
    response = requests.get(CSV_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    
    if response.status_code == 200:
        # Đọc dữ liệu dạng thô (không tiêu đề)
        df_raw = pd.read_csv(io.StringIO(response.text), header=None, dtype=str)
        
        # Chỉ trích xuất đúng cột 1 và cột 32
        df_sub = df_raw[[1, 32]].dropna(subset=[1])
        df_sub.columns = ["Tên", "Số ngày (Cột 32)"]

        # Chuẩn hóa tên để đối chiếu
        df_sub["ten_clean"] = df_sub["Tên"].astype(str).str.strip().str.lower()

        for ten in danh_sach_thanh_vien:
            ten_clean = ten.strip().lower()
            khop = df_sub[df_sub["ten_clean"] == ten_clean]
            if not khop.empty:
                val = khop["Số ngày (Cột 32)"].values[0]
                try:
                    so_ngay_dict[ten] = float(str(val).replace(",", ".").strip())
                except (ValueError, TypeError):
                    so_ngay_dict[ten] = 0.0

        st.success("✅ Đã kết nối thành công! Chỉ đọc đúng Cột 1 và Cột 32.")
        with st.expander("👁️ Xem dữ liệu 2 cột trích xuất từ Sheet"):
            st.dataframe(df_sub[["Tên", "Số ngày (Cột 32)"]])
    else:
        st.error(f"❌ Không tải được Sheet (Mã lỗi {response.status_code}).")

except Exception as e:
    st.error(f"❌ Lỗi khi đọc dữ liệu: {e}")

st.markdown("---")

# 3. Điền tự động số ngày vào từng thành viên
st.subheader("3. Số ngày ở của từng thành viên")
danh_sach = []
cols_form = st.columns(2)

for i, ten in enumerate(danh_sach_thanh_vien):
    col_idx = i % 2
    with cols_form[col_idx]:
        ngay = st.number_input(
            f"Số ngày của **{ten}**:",
            min_value=0.0,
            max_value=31.0,
            value=float(so_ngay_dict[ten]),
            step=0.5,
            key=f"ngay_{i}"
        )
        danh_sach.append({"Họ và tên": ten, "Số ngày ở": ngay})

st.markdown("---")

# 4. Tính toán kết quả
if st.button("👉 Tính tiền điện", type="primary", use_container_width=True):
    tong_so_ngay = sum(item["Số ngày ở"] for item in danh_sach)
    
    if tong_so_ngay == 0:
        st.error("❌ Tổng số ngày ở của các bạn đang bằng 0. Vui lòng kiểm tra lại số ngày!")
    else:
        don_gia_ngay = tong_tien / tong_so_ngay
        
        ket_qua = []
        tong_tien_thuc_te = 0
        for item in danh_sach:
            tien_dong = round(item["Số ngày ở"] * don_gia_ngay)
            tong_tien_thuc_te += tien_dong
            ket_qua.append({
                "Họ và tên": item["Họ và tên"],
                "Số ngày ở (Cột 32)": f"{item['Số ngày ở']:g} ngày",
                "Tiền cần đóng": f"{tien_dong:,.0f} VNĐ"
            })
            
        st.subheader("4. Bảng phân bổ tiền điện")
        
        m1, m2 = st.columns(2)
        m1.metric("Tổng ngày-người", f"{tong_so_ngay:g} ngày")
        m2.metric("Đơn giá / ngày", f"{don_gia_ngay:,.0f} VNĐ")
        
        df_kq = pd.DataFrame(ket_qua)
        df_kq.index = range(1, len(df_kq) + 1)
        st.table(df_kq)
        
        chenh_lech = round(tong_tien - tong_tien_thuc_te)
        if chenh_lech != 0:
            st.caption(f"*(Chênh lệch do làm tròn số tiền: {chenh_lech:+,.0f} VNĐ)*")
