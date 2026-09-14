"""
Chương trình: Chia tiền điện phòng trọ theo số ngày ở thực tế
Tác giả: [Tên của bạn]
GitHub: [Link repo của bạn]
"""

def nhap_so_duong(thong_bao, kieu_du_lieu=float):
    """Hàm phụ trợ để nhập số hợp lệ lớn hơn 0"""
    while True:
        try:
            gia_tri = kieu_du_lieu(input(thong_bao))
            if gia_tri <= 0:
                print("❌ Vui lòng nhập số lớn hơn 0.")
                continue
            return gia_tri
        except ValueError:
            print("❌ Dữ liệu không hợp lệ. Vui lòng nhập số.")

def main():
    print("=" * 45)
    print("   TIỆN ÍCH TÍNH TIỀN ĐIỆN THEO SỐ NGÀY Ở   ")
    print("=" * 45)

    # 1. Nhập tổng số tiền điện
    tong_tien_dien = nhap_so_duong("👉 Nhập tổng tiền điện tháng này (VNĐ): ", float)

    # 2. Nhập số lượng thành viên
    so_thanh_vien = nhap_so_duong("👉 Nhập số lượng thành viên trong phòng: ", int)

    thanh_vien = []
    print("\n--- NHẬP THÔNG TIN TỪNG THÀNH VIÊN ---")
    for i in range(1, so_thanh_vien + 1):
        ten = input(f"\nTên thành viên #{i}: ").strip()
        if not ten:
            ten = f"Thành viên {i}"
        
        while True:
            try:
                ngay = float(input(f"Số ngày ở của {ten} (0 - 31 ngày): "))
                if 0 <= ngay <= 31:
                    break
                print("❌ Số ngày phải từ 0 đến 31.")
            except ValueError:
                print("❌ Vui lòng nhập số ngày hợp lệ.")
        
        thanh_vien.append({"ten": ten, "so_ngay": ngay})

    # 3. Tính toán
    tong_so_ngay = sum(tv["so_ngay"] for tv in thanh_vien)

    if tong_so_ngay == 0:
        print("\n⚠️ Tổng số ngày ở của tất cả bằng 0, không thể phân bổ tiền điện.")
        return

    # Tính đơn giá điện trên 1 ngày người
    don_gia_ngay = tong_tien_dien / tong_so_ngay

    print("\n" + "=" * 55)
    print("                 KẾT QUẢ PHÂN BỔ                 ")
    print("=" * 55)
    print(f"Tổng tiền điện: {tong_tien_dien:,.0f} VNĐ")
    print(f"Tổng số ngày-người: {tong_so_ngay} ngày")
    print(f"Đơn giá: {don_gia_ngay:,.2f} VNĐ / người / ngày")
    print("-" * 55)
    print(f"{'STT':<5} | {'Họ và tên':<20} | {'Số ngày':<10} | {'Số tiền cần đóng'}")
    print("-" * 55)

    tong_tien_kiem_tra = 0
    for idx, tv in enumerate(thanh_vien, 1):
        tien_dong = round(tv["so_ngay"] * don_gia_ngay)
        tong_tien_kiem_tra += tien_dong
        print(f"{idx:<5} | {tv['ten']:<20} | {tv['so_ngay']:<10} | {tien_dong:,.0f} VNĐ")

    print("-" * 55)
    print(f"👉 Tổng tiền đã chia: {tong_tien_kiem_tra:,.0f} VNĐ")
    
    # Xử lý chênh lệch do làm tròn (nếu có)
    chenh_lech = round(tong_tien_dien - tong_tien_kiem_tra)
    if chenh_lech != 0:
        print(f"ℹ️ (Chênh lệch do làm tròn số: {chenh_lech:+,.0f} VNĐ)")
    print("=" * 55)

if __name__ == "__main__":
    main()