import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title= "TIỀN ĐIỆN NƯỚC P307A", page_icon="⚡", layout="centered")

st.title("TIỀN ĐIỆN NƯỚC P307A")
st.write("Tự động đọc số ngày ở từ **Google Sheets** để tính tiền điện.")

# 1. Nhập tổng tiền điện
st.subheader("1. Tổng tiền điện")
tong_tien = st.number_input(
    "Nhập tổng tiền điện tháng này (VNĐ):",
    min_value=0,
    value=3000000,
    step=1000,
    format="%d"
)

st.markdown("---")

# 2. Nhập link Google Sheet
st.subheader("2. Kết nối Google Sheet")
st.caption("📌 *Lưu ý: Bảng tính Google Sheet cần được bật chia sẻ quyền xem: **Chia sẻ -> Bất kỳ ai có đường liên kết đều có thể xem**.*")

# Bạn có thể điền sẵn link mặc định của phòng vào ô bên dưới
link_sheet_mac_dinh = "https://docs.google.com/spreadsheets/d/1lanmHwXOPIM_6KV0inZV2KFdP1Xmy3k7uUljA3yyvvM/edit?usp=sharing" 
url_sheet = st.text_input("https://docs.google.com/spreadsheets/d/1lanmHwXOPIM_6KV0inZV2KFdP1Xmy3k7uUljA3yyvvM/edit?usp=sharing", value=link_sheet_mac_dinh)

danh_sach_thanh_vien = [
    "Hà Phương Anh",
    "Phương Ly",
    "Nguyễn Thị Phương Anh",
    "Loan",
    "Mến",
    "Nguyễn Phương Anh"
]

so_ngay_dict = {ten: 30.0 for ten in danh_sach_thanh_vien}

def lay_csv_url(url):
    """Chuyển đổi URL Google Sheet thông thường sang link tải dữ liệu CSV"""
    sheet_id_match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
    if not sheet_id_match:
        return None
    sheet_id = sheet_id_match.group(1)
    
    gid_match = re.search(r'gid=([0-9]+)', url)
    gid = gid_match.group(1) if gid_match else "0"
    
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

if url_sheet.strip():
    csv_url = lay_csv_url(url_sheet)
    if not csv_url:
        st.error("⚠️ Link Google Sheet không đúng định dạng. Vui lòng kiểm tra lại.")
    else:
        try:
            df_sheet = pd.read_csv(csv_url)
            st.success("✅ Đã kết nối và tải dữ liệu từ Google Sheet thành công!")
            
            with st.expander("👁️ Xem bảng tính từ Google Sheet"):
                st.dataframe(df_sheet.head(10))

            cols = df_sheet.columns.tolist()
            col_select1, col_select2 = st.columns(2)
            
            with col_select1:
                col_ten = st.selectbox("Cột TÊN thành viên:", options=cols, index=0)
            
            with col_select2:
                # Gợi ý tự động cột ngày
                default_ngay_idx = 1 if len(cols) > 1 else 0
                for idx, c in enumerate(cols):
                    if any(kw in str(c).lower() for kw in ["ngày", "ngay", "tổng", "tong", "total", "ở", "o"]):
                        default_ngay_idx = idx
                        break
                col_ngay = st.selectbox("Cột SỐ NGÀY Ở:", options=cols, index=default_ngay_idx)

            # Chuẩn hóa tên để tự động khớp
            df_sheet['ten_clean'] = df_sheet[col_ten].astype(str).str.strip().str.lower()
            
            for ten in danh_sach_thanh_vien:
                khop = df_sheet[df_sheet['ten_clean'] == ten.strip().lower()]
                if not khop.empty:
                    val = khop[col_ngay].values[0]
                    try:
                        so_ngay_dict[ten] = float(val)
                    except (ValueError, TypeError):
                        so_ngay_dict[ten] = 0.0

        except Exception as e:
            st.error("❌ Không thể đọc Google Sheet. Hãy kiểm tra xem file đã bật **'Bất kỳ ai có đường liên kết'** chưa.")

st.markdown("---")

# 3. Hiển thị số ngày đã lấy được (có thể chỉnh lại nếu cần)
st.subheader("3. Số ngày ở của từng bạn")
danh_sach = []
cols = st.columns(2)

for i, ten in enumerate(danh_sach_thanh_vien):
    col_idx = i % 2
    with cols[col_idx]:
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
        st.error("❌ Tổng số ngày ở phải lớn hơn 0!")
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
            
        st.subheader("4. Kết quả phân bổ tiền điện")
        
        m1, m2 = st.columns(2)
        m1.metric("Tổng ngày-người", f"{tong_so_ngay:g} ngày")
        m2.metric("Đơn giá / ngày", f"{don_gia_ngay:,.0f} VNĐ")
        
        df_kq = pd.DataFrame(ket_qua)
        df_kq.index = range(1, len(df_kq) + 1)
        st.table(df_kq)
        
        chenh_lech = round(tong_tien - tong_tien_thuc_te)
        if chenh_lech != 0:
            st.caption(f"*(Chênh lệch do làm tròn số tiền: {chenh_lech:+,.0f} VNĐ)*")
