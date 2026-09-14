import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(page_title="Tính Tiền Điện Phòng 307A", page_icon="⚡", layout="centered")

st.title("⚡ Tính Tiền Điện Phòng 307A")
st.write("Tự động lấy số ngày ở từ cột **Tổng** trên Google Sheet để phân bổ tiền điện.")

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

# 2. Đọc tự động số ngày từ cột "Tổng" trên Google Sheet
st.subheader("2. Dữ liệu từ Google Sheet")
SHEET_ID = "1lanmHwXOPIM_6KV0inZV2KFdP1Xmy3k7uUljA3yyvvM"
SHEET_NAME = "Sheet1"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

so_ngay_dict = {ten: 0.0 for ten in danh_sach_thanh_vien}

try:
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(CSV_URL, headers=headers, timeout=10)
    
    if response.status_code == 200:
        # Bảng tính có tiêu đề ở hàng 2 (header=1)
        df_sheet = pd.read_csv(io.StringIO(response.text), header=1)
        
        # 1. Xác định cột chứa Họ và Tên (thường là cột B)
        col_ten = None
        for c in df_sheet.columns:
            c_str = str(c).strip().lower()
            if any(kw in c_str for kw in ["họ", "tên", "thành viên", "name"]):
                col_ten = c
                break
        if col_ten is None:
            col_ten = df_sheet.columns[1]

        # 2. Xác định chính xác cột "Tổng"
        col_tong = None
        for c in df_sheet.columns:
            c_str = str(c).strip().lower()
            if "tổng" in c_str or "tong" in c_str or "total" in c_str:
                col_tong = c
                break

        if col_tong is not None:
            st.success(f"✅ Đã kết nối Sheet! Tự động trích xuất số ngày từ cột: **'{col_tong}'**")
            
            # Chuẩn hóa cột tên để so khớp không phân biệt hoa thường, dấu cách thừa
            df_sheet["ten_clean"] = df_sheet[col_ten].astype(str).str.strip().str.lower()
            
            for ten in danh_sach_thanh_vien:
                khop = df_sheet[df_sheet["ten_clean"] == ten.strip().lower()]
                if not khop.empty:
                    val = khop[col_tong].values[0]
                    try:
                        # Chuyển đổi định dạng số (xử lý cả dấu phẩy thập phân nếu có)
                        val_num = float(str(val).replace(",", ".").strip())
                        so_ngay_dict[ten] = max(0.0, val_num)
                    except (ValueError, TypeError):
                        so_ngay_dict[ten] = 0.0
        else:
            st.warning("⚠️ Không tìm thấy cột nào tên là **'Tổng'** trên Google Sheet. Bạn hãy kiểm tra lại tiêu đề cột.")

        with st.expander("👁️ Xem bảng tính đọc từ Google Sheet"):
            st.dataframe(df_sheet)
    else:
        st.error(f"❌ Không tải được Sheet (Mã lỗi {response.status_code}).")

except Exception as e:
    st.error(f"❌ Lỗi kết nối Google Sheet: {e}")

st.markdown("---")

# 3. Hiển thị số ngày đã được tự động điền (vẫn cho phép sửa tay nếu cần)
st.subheader("3. Số ngày ở thực tế của từng thành viên")
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

# 4. Tính toán và phân bổ tiền điện
if st.button("👉 Tính tiền điện", type="primary", use_container_width=True):
    tong_so_ngay = sum(item["Số ngày ở"] for item in danh_sach)
    
    if tong_so_ngay == 0:
        st.error("❌ Tổng số ngày ở của cả phòng bằng 0! Vui lòng kiểm tra lại số ngày.")
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
