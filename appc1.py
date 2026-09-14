import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Tính Tiền Điện Phòng 307A", page_icon="⚡", layout="centered")

st.title("⚡ Tính Tiền Điện Phòng 307A")
st.write("Tự động đọc số ngày ở từ cột **Tổng** trên Google Sheet.")

# Danh sách 6 thành viên cố định
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
DEFAULT_URL = "https://docs.google.com/spreadsheets/d/1lanmHwXOPIM_6KV0inZV2KFdP1Xmy3k7uUljA3yyvvM/edit?usp=sharing"

def lay_csv_url(url):
    sheet_id_match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
    if not sheet_id_match:
        return None
    sheet_id = sheet_id_match.group(1)
    
    gid_match = re.search(r'gid=([0-9]+)', url)
    gid = gid_match.group(1) if gid_match else "0"
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

so_ngay_dict = {ten: 30.0 for ten in danh_sach_thanh_vien}

try:
    csv_url = lay_csv_url(DEFAULT_URL)
    df_sheet = pd.read_csv(csv_url)
    
    # 1. Tự động xác định cột Tên (tìm cột đầu tiên hoặc cột có chữ 'tên'/'họ và tên')
    col_ten = df_sheet.columns[0]
    for c in df_sheet.columns:
        if any(kw in str(c).strip().lower() for kw in ["tên", "ten", "họ tên", "thành viên"]):
            col_ten = c
            break

    # 2. Tự động xác định cột 'Tổng'
    col_tong = None
    for c in df_sheet.columns:
        if "tổng" in str(c).strip().lower() or "tong" in str(c).strip().lower():
            col_tong = c
            break
            
    if col_tong is None:
        # Nếu không thấy chữ 'Tổng', mặc định lấy cột cuối cùng
        col_tong = df_sheet.columns[-1]

    st.success(f"✅ Đã kết nối Sheet! Tự động lấy số ngày từ cột: **'{col_tong}'**")

    # Chuẩn hóa để so khớp tên chính xác
    df_sheet['ten_clean'] = df_sheet[col_ten].astype(str).str.strip().str.lower()

    for ten in danh_sach_thanh_vien:
        khop = df_sheet[df_sheet['ten_clean'] == ten.strip().lower()]
        if not khop.empty:
            val = khop[col_tong].values[0]
            try:
                # Làm sạch và chuyển đổi sang số thực
                val_clean = str(val).replace(',', '.').strip()
                so_ngay_dict[ten] = float(val_clean)
            except (ValueError, TypeError):
                so_ngay_dict[ten] = 0.0

    with st.expander("👁️ Xem trước bảng tính từ Google Sheet"):
        st.dataframe(df_sheet)

except Exception as e:
    st.error(
        "❌ Chưa đọc được Google Sheet. Bạn nhớ kiểm tra xem file đã bật "
        "**Chia sẻ -> Bất kỳ ai có đường liên kết đều có thể xem (Viewer)** chưa nhé!"
    )

st.markdown("---")

# 3. Hiển thị số ngày tương ứng của từng bạn
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
                "Số ngày ở (từ cột Tổng)": f"{item['Số ngày ở']:g} ngày",
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
