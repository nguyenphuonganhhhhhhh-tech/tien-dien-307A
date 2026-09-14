import streamlit as st
import pandas as pd
import requests
import io
import re

st.set_page_config(page_title="Tính Tiền Điện Phòng 307A", page_icon="⚡", layout="centered")

st.title("⚡ Tính Tiền Điện Phòng 307A")
st.write("Tự động đọc số ngày ở từ **Google Sheet** để chia tiền điện.")

# 6 thành viên cố định
danh_sach_thanh_vien = [
    "Hà Phương Anh",
    "Phương Ly",
    "Nguyễn Thị Phương Anh",
    "Loan",
    "Mến",
    "Nguyễn Phương Anh"
]

# 1. Nhập tổng tiền điện
st.subheader("1. Tổng tiền điện")
tong_tien = st.number_input(
    "Nhập tổng tiền điện tháng này (VNĐ):",
    min_value=0,
    value=1500000,
    step=10000,
    format="%d"
)

st.markdown("---")

# 2. Đọc tự động từ Google Sheet
st.subheader("2. Dữ liệu từ Google Sheet")
SHEET_ID = "1lanmHwXOPIM_6KV0inZV2KFdP1Xmy3k7uUljA3yyvvM"
SHEET_NAME = "Sheet1"

# URL truy xuất dữ liệu CSV ổn định nhất của Google
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

so_ngay_dict = {ten: 0.0 for ten in danh_sach_thanh_vien}
sheet_loaded = False

try:
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(CSV_URL, headers=headers, timeout=10)
    
    if response.status_code == 200:
        # Tiêu đề bảng của bạn nằm ở dòng 2 (header=1)
        df_sheet = pd.read_csv(io.StringIO(response.text), header=1)
        
        # Tìm cột Họ và tên
        col_ten = None
        for c in df_sheet.columns:
            c_str = str(c).strip().lower()
            if any(kw in c_str for kw in ["họ", "tên", "thành viên", "name"]):
                col_ten = c
                break
        if col_ten is None:
            col_ten = df_sheet.columns[1]

        # Chuẩn hóa cột tên
        df_sheet['ten_clean'] = df_sheet[col_ten].astype(str).str.strip().str.lower()

        # Tìm cột Tổng
        col_tong = None
        for c in df_sheet.columns:
            c_str = str(c).strip().lower()
            if "tổng" in c_str or "tong" in c_str or "total" in c_str:
                col_tong = c
                break

        if col_tong is not None:
            st.success(f"✅ Đã tải dữ liệu! Lấy số ngày từ cột **'{col_tong}'**")
            for ten in danh_sach_thanh_vien:
                khop = df_sheet[df_sheet['ten_clean'] == ten.strip().lower()]
                if not khop.empty:
                    val = khop[col_tong].values[0]
                    try:
                        so_ngay_dict[ten] = float(str(val).replace(',', '.').strip())
                    except (ValueError, TypeError):
                        so_ngay_dict[ten] = 0.0
        else:
            st.info("ℹ️ Tự động cộng các ngày có đánh dấu **1** trong bảng.")
            cac_cot_ngay = [c for c in df_sheet.columns if c not in [df_sheet.columns[0], col_ten, 'ten_clean', 'STT']]
            
            for ten in danh_sach_thanh_vien:
                khop = df_sheet[df_sheet['ten_clean'] == ten.strip().lower()]
                if not khop.empty:
                    row_vals = khop[cac_cot_ngay].values[0]
                    tong_ngay = 0.0
                    for v in row_vals:
                        try:
                            v_num = float(str(v).replace(',', '.').strip())
                            if v_num > 0:
                                tong_ngay += v_num
                        except (ValueError, TypeError):
                            pass
                    so_ngay_dict[ten] = tong_ngay

        with st.expander("👁️ Xem bảng tính đọc từ Google Sheet"):
            st.dataframe(df_sheet)
        sheet_loaded = True
    else:
        st.error(f"❌ Google Sheet trả về mã lỗi: {response.status_code}. Hãy kiểm tra lại quyền Chia sẻ.")

except Exception as e:
    st.error(f"❌ Lỗi kết nối Google Sheet: {e}")
    st.warning("⚠️ Hãy kiểm tra quyền: Bấm nút **Chia sẻ** trên Google Sheet -> chọn **Bất kỳ ai có đường liên kết** (Người xem).")

st.markdown("---")

# 3. Form kiểm tra và nhập số ngày
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
        st.error("❌ Tổng số ngày ở của các thành viên phải lớn hơn 0!")
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
