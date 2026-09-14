import streamlit as st
import pandas as pd

st.set_page_config(page_title="Tính Tiền Điện Phòng Trọ", page_icon="⚡", layout="centered")

st.title("⚡ Tính Tiền Điện Theo Số Ngày Ở")
st.write("Công cụ phân bổ tiền điện công bằng dựa trên số ngày thực tế mỗi người ở trong tháng.")

# Khung nhập thông tin chung
with st.container():
    st.subheader("1. Thông tin chung")
    tong_tien = st.number_input(
        "Tổng tiền điện cần thanh toán (VNĐ):",
        min_value=0,
        value=1200000,
        step=10000,
        format="%d"
    )
    so_nguoi = st.number_input(
        "Số lượng thành viên trong phòng:",
        min_value=1,
        max_value=30,
        value=3,
        step=1
    )

st.markdown("---")

# Khung nhập số ngày từng người
st.subheader("2. Thông tin từng thành viên")
danh_sach = []

cols = st.columns(2)
for i in range(int(so_nguoi)):
    with cols[0]:
        ten = st.text_input(f"Tên thành viên #{i+1}", value=f"Thành viên {i+1}", key=f"ten_{i}")
    with cols[1]:
        ngay = st.number_input(f"Số ngày ở (0 - 31)", min_value=0.0, max_value=31.0, value=30.0, step=0.5, key=f"ngay_{i}")
    danh_sach.append({"Họ và tên": ten, "Số ngày ở": ngay})

# Nút tính tiền
st.markdown("---")
if st.button("👉 Tính toán kết quả", type="primary"):
    tong_so_ngay = sum(item["Số ngày ở"] for item in danh_sach)
    
    if tong_so_ngay == 0:
        st.error("Tổng số ngày ở của tất cả mọi người phải lớn hơn 0!")
    else:
        don_gia_ngay = tong_tien / tong_so_ngay
        
        # Tạo bảng kết quả
        ket_qua = []
        tong_tien_thuc_te = 0
        for item in danh_sach:
            tien_dong = round(item["Số ngày ở"] * don_gia_ngay)
            tong_tien_thuc_te += tien_dong
            ket_qua.append({
                "Họ và tên": item["Họ và tên"],
                "Số ngày ở": f"{item['Số ngày ở']} ngày",
                "Số tiền phải đóng (VNĐ)": f"{tien_dong:,.0f} đ"
            })
            
        st.subheader("3. Bảng phân bổ tiền điện")
        
        col_metric1, col_metric2 = st.columns(2)
        col_metric1.metric("Tổng ngày-người", f"{tong_so_ngay} ngày")
        col_metric2.metric("Đơn giá", f"{don_gia_ngay:,.0f} đ / người / ngày")
        
        df = pd.DataFrame(ket_qua)
        st.table(df)
        
        chenh_lech = round(tong_tien - tong_tien_thuc_te)
        if chenh_lech != 0:
            st.caption(f"*(Chênh lệch do làm tròn số: {chenh_lech:+,.0f} VNĐ)*")
