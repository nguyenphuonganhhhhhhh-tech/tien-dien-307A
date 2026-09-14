import streamlit as st
import pandas as pd
import requests
import io
import re

st.set_page_config(page_title="Tính Tiền Điện Phòng 307A", page_icon="⚡", layout="centered")

st.title("⚡ Tính Tiền Điện Phòng 307A")
st.write("Tự động đọc số ngày ở từ **Google Sheet** để chia tiền điện cho từng thành viên.")

# Danh sách 6 bạn trong phòng
danh_sach_thanh_vien = [
    "Hà Phương Anh",
    "Phương Ly",
    "Nguyễn Thị Phương Anh",
    "Loan",
    "Mến",
    "Nguyễn Phương Anh"
]

# 1. Tổng tiền điện
st.subheader("1. Tổng tiền điện")
tong_tien = st.number_input(
    "Nhập tổng tiền điện tháng này (VNĐ):",
    min_value=0,
    value=1500000,
    step=10000,
    format="%d"
)

st.markdown("---")

# 2. Đọc toàn diện Google Sheet
st.subheader("2. Dữ liệu từ Google Sheet")

col_btn1, col_btn2 = st.columns([3, 1])
with col_btn2:
    if st.button("🔄 Làm mới Sheet"):
        st.cache_data.clear()
        st.rerun()

SHEET_ID = "1lanmHwXOPIM_6KV0inZV2KFdP1Xmy3k7uUljA3yyvvM"
SHEET_NAME = "Sheet1"
# Đọc trực tiếp định dạng CSV sạch nhất
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

so_ngay_dict = {ten: 0.0 for ten in danh_sach_thanh_vien}

try:
    # Đọc thô toàn bộ bảng tính không ép header để không bị sót cột
    response = requests.get(CSV_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    
    if response.status_code == 200:
        # Đọc toàn bộ bảng dạng ma trận phẳng
        df_raw = pd.read_csv(io.StringIO(response.text), header=None, dtype=str)
        
        # Quét tìm vị trí hàng của từng thành viên
        for ten in danh_sach_thanh_vien:
            ten_chuan = ten.strip().lower()
            tim_thay = False
            
            for row_idx, row in df_raw.iterrows():
                # Kiểm tra xem tên có nằm trong hàng này không (thường ở cột 0, 1 hoặc 2)
                row_str_cells = [str(cell).strip().lower() for cell in row.values if pd.notna(cell)]
                if any(ten_chuan == cell or (ten_chuan in cell and len(cell) < len(ten_chuan) + 5) for cell in row_str_cells):
                    tim_thay = True
                    # Tìm tất cả các giá trị là số trong hàng của bạn này (bỏ qua STT ở đầu)
                    cac_so = []
                    for idx_col, val in enumerate(row.values):
                        if idx_col <= 1:  # Bỏ qua cột STT và cột Tên
                            continue
                        if pd.notna(val):
                            val_str = str(val).replace(',', '.').strip()
                            try:
                                num = float(val_str)
                                cac_so.append(num)
                            except ValueError:
                                pass
                    
                    if cac_so:
                        # Nếu ô cuối cùng lớn hơn tổng các ngày riêng lẻ hoặc bạn có cột Tổng ở cuối
                        # Thường cột "Tổng" là số cuối cùng trên hàng
                        # Nếu số cuối cùng chính là số tổng:
                        if len(cac_so) > 1 and cac_so[-1] == sum(cac_so[:-1]):
                            so_ngay_dict[ten] = float(cac_so[-1])
                        elif len(cac_so) > 1 and cac_so[-1] > 1: # Cột tổng thường có giá trị cộng dồn
                            so_ngay_dict[ten] = float(cac_so[-1])
                        else:
                            # Nếu bạn chỉ đánh dấu số 1 các ngày và chưa có cột tổng: cộng toàn bộ các số 1
                            so_ngay_dict[ten] = float(sum(cac_so))
                    break
                    
        st.success("✅ Đã kết nối và đọc toàn bộ dữ liệu Google Sheet thành công!")
        
        with st.expander("👁️ Bấm để xem toàn bộ bảng Google Sheet đã đọc"):
            st.dataframe(df_raw)
    else:
        st.error(f"❌ Không thể tải Google Sheet (Mã lỗi HTTP: {response.status_code}).")

except Exception as e:
    st.error(f"❌ Lỗi khi đọc dữ liệu: {e}")

st.markdown("---")

# 3. Form hiển thị số ngày tự động (vẫn cho phép sửa tay trực tiếp)
st.subheader("3. Số ngày ở của từng bạn")
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
        st.error("❌ Tổng số ngày ở của các bạn đang bằng 0. Vui lòng kiểm tra lại!")
    else:
        don_gia_ngay = tong_tien / tong_so_ngay
        
        ket_qua = []
        tong_tien_thuc_te = 0
        for item in danh_sach:
            tien_dong = round(item["Số ngày ở"] * don_gia_ngay)
            tong_tien_thuc_te += tien_dong
            ket_qua.append({
                "Họ và tên": item["Họ và tên"],
                "Số ngày ở": f"{item['Số ngày ở']:g} ngày",
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
