import streamlit as st
import pandas as pd

st.set_page_config(page_title="Tính Tiền Điện Phòng 307A", page_icon="⚡", layout="centered")

st.title("⚡ Tính Tiền Điện Phòng Trọ")
st.write("Công cụ phân bổ tiền điện công bằng theo số ngày ở thực tế của từng thành viên.")

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

# 2. Danh sách thành viên mặc định
st.subheader("2. Điền số ngày ở trong tháng")
danh_sach_mac_dinh = [
    "Hà Phương Anh",
    "Phương Ly",
    "Nguyễn Thị Phương Anh",
    "Loan",
    "Mến",
    "Nguyễn Phương Anh"
]

danh_sach = []

# Hiển thị form nhập cho từng thành viên
for i, ten_mac_dinh in enumerate(danh_sach_mac_dinh):
    col1, col2 = st.columns([3, 2])
    with col1:
        ten = st.text_input(f"Thành viên #{i+1}", value=ten_mac_dinh, key=f"ten_{i}")
    with col2:
        ngay = st.number_input(
            f"Số ngày ở",
            min_value=0.0,
            max_value=31.0,
            value=30.0,
            step=0.5,
            key=f"ngay_{i}"
        )
    danh_sach.append({"Họ và tên": ten, "Số ngày ở": ngay})

st.markdown("---")

# 3. Nút tính kết quả
if st.button("👉 Tính tiền điện", type="primary", use_container_width=True):
    tong_so_ngay = sum(item["Số ngày ở"] for item in danh_sach)
    
    if tong_so_ngay == 0:
        st.error("❌ Tổng số ngày ở của cả phòng phải lớn hơn 0!")
    else:
        don_gia_ngay = tong_tien / tong_so_ngay
        
        ket_qua = []
        tong_tien_thuc_te = 0
        for item in danh_sach:
            tien_dong = round(item["Số ngày ở"] * don_gia_ngay)
            tong_tien_thuc_te += tien_dong
            ket_qua.append({
                "Họ và tên": item["Họ và tên"],
                "Số ngày ở": f"{item['Số ngày ở']} ngày",
                "Tiền cần đóng": f"{tien_dong:,.0f} VNĐ"
            })
            
        st.subheader("3. Kết quả chi tiết")
        
        m1, m2 = st.columns(2)
        m1.metric("Tổng ngày-người", f"{tong_so_ngay:g} ngày")
        m2.metric("Đơn giá / ngày", f"{don_gia_ngay:,.0f} VNĐ")
        
        df = pd.DataFrame(ket_qua)
        df.index = range(1, len(df) + 1)  # Đánh số thứ tự từ 1
        st.table(df)
        
        chenh_lech = round(tong_tien - tong_tien_thuc_te)
        if chenh_lech != 0:
            st.caption(f"*(Chênh lệch do làm tròn số tiền: {chenh_lech:+,.0f} VNĐ)*")
