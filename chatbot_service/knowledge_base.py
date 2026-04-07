"""
Knowledge Base - Product catalog & policies for RAG context.
This replaces ChromaDB with a simple in-memory search for reliability.
"""

PRODUCTS = [
    # === LAPTOPS ===
    {"id": 1, "type": "laptop", "name": "Dell XPS 15", "brand": "Dell", "price": 1499, "category": "ultrabook",
     "specs": "Intel Core i7-13700H, 16GB RAM, 512GB SSD, 15.6\" OLED 3.5K, NVIDIA RTX 4050",
     "description": "Laptop cao cấp cho dân sáng tạo nội dung và lập trình viên, màn hình OLED sắc nét."},
    {"id": 2, "type": "laptop", "name": "MacBook Air M3", "brand": "Apple", "price": 1099, "category": "ultrabook",
     "specs": "Apple M3, 8GB RAM, 256GB SSD, 13.6\" Liquid Retina, Pin 18h",
     "description": "Laptop mỏng nhẹ nhất của Apple, hiệu năng mạnh mẽ với chip M3, pin cả ngày."},
    {"id": 3, "type": "laptop", "name": "ASUS ROG Strix G16", "brand": "ASUS", "price": 1799, "category": "gaming",
     "specs": "Intel Core i9-13980HX, 32GB RAM, 1TB SSD, RTX 4070, 16\" QHD 240Hz",
     "description": "Laptop gaming đỉnh cao, tản nhiệt tốt, màn hình 240Hz mượt mà cho game thủ."},
    {"id": 4, "type": "laptop", "name": "Lenovo ThinkPad X1 Carbon", "brand": "Lenovo", "price": 1349, "category": "business",
     "specs": "Intel Core i7-1365U, 16GB RAM, 512GB SSD, 14\" 2.8K OLED, 1.12kg",
     "description": "Laptop doanh nhân hàng đầu, siêu nhẹ, bàn phím tuyệt vời, bảo mật doanh nghiệp."},
    {"id": 5, "type": "laptop", "name": "Acer Nitro 5", "brand": "Acer", "price": 899, "category": "gaming",
     "specs": "AMD Ryzen 7 7735HS, 16GB RAM, 512GB SSD, RTX 4060, 15.6\" FHD 144Hz",
     "description": "Laptop gaming giá rẻ nhất phân khúc, hiệu năng tốt cho sinh viên chơi game."},
    {"id": 6, "type": "laptop", "name": "HP Pavilion 15", "brand": "HP", "price": 649, "category": "student",
     "specs": "Intel Core i5-1335U, 8GB RAM, 256GB SSD, 15.6\" FHD IPS",
     "description": "Laptop sinh viên giá tốt, đủ dùng cho học tập và làm việc văn phòng."},

    # === MOBILES ===
    {"id": 7, "type": "mobile", "name": "iPhone 15 Pro Max", "brand": "Apple", "price": 1199, "category": "flagship",
     "specs": "A17 Pro, 256GB, 6.7\" Super Retina XDR, Camera 48MP, Titanium",
     "description": "Flagship đỉnh của Apple, khung titanium, camera chuyên nghiệp, chip mạnh nhất."},
    {"id": 8, "type": "mobile", "name": "Samsung Galaxy S24 Ultra", "brand": "Samsung", "price": 1299, "category": "flagship",
     "specs": "Snapdragon 8 Gen 3, 256GB, 6.8\" Dynamic AMOLED, Camera 200MP, S Pen",
     "description": "Smartphone Android cao cấp nhất, camera 200MP, kèm bút S Pen, AI tích hợp."},
    {"id": 9, "type": "mobile", "name": "Xiaomi 14", "brand": "Xiaomi", "price": 599, "category": "mid-range",
     "specs": "Snapdragon 8 Gen 3, 256GB, 6.36\" LTPO AMOLED, Camera Leica 50MP",
     "description": "Flagship killer giá cực tốt, camera Leica, hiệu năng ngang hàng flagship."},
    {"id": 10, "type": "mobile", "name": "Samsung Galaxy A55", "brand": "Samsung", "price": 399, "category": "mid-range",
     "specs": "Exynos 1480, 128GB, 6.6\" Super AMOLED, Camera 50MP, IP67",
     "description": "Điện thoại tầm trung tốt nhất Samsung, chống nước IP67, màn hình đẹp."},
    {"id": 11, "type": "mobile", "name": "OPPO Reno 11", "brand": "OPPO", "price": 449, "category": "mid-range",
     "specs": "Dimensity 7050, 256GB, 6.7\" AMOLED 120Hz, Camera 64MP, Sạc 67W",
     "description": "Điện thoại tầm trung OPPO, thiết kế đẹp, sạc siêu nhanh 67W."},
    {"id": 12, "type": "mobile", "name": "Realme C67", "brand": "Realme", "price": 179, "category": "budget",
     "specs": "Snapdragon 685, 128GB, 6.72\" IPS 90Hz, Camera 108MP, Pin 5000mAh",
     "description": "Điện thoại giá rẻ nhất cửa hàng, pin trâu, camera 108MP ấn tượng."},
]

POLICIES = """
=== CHÍNH SÁCH CỬA HÀNG NOVA ELECTRONICS ===

1. BẢO HÀNH:
- Laptop: Bảo hành chính hãng 24 tháng + 6 tháng bảo hành cửa hàng
- Điện thoại: Bảo hành chính hãng 12 tháng + 3 tháng bảo hành cửa hàng
- Phụ kiện kèm theo: 6 tháng

2. ĐỔI TRẢ:
- Đổi trả miễn phí trong 15 ngày đầu nếu lỗi phần cứng từ nhà sản xuất
- Hoàn tiền 100% trong 7 ngày nếu sản phẩm chưa kích hoạt bảo hành
- Không áp dụng đổi trả với sản phẩm đã qua sử dụng trên 15 ngày

3. KHUYẾN MÃI HIỆN TẠI:
- Giảm 10% cho sinh viên có thẻ sinh viên (áp dụng laptop)
- Mua laptop tặng balo + chuột không dây
- Mua điện thoại flagship tặng ốp lưng + dán màn hình
- Trả góp 0% lãi suất qua thẻ tín dụng trong 12 tháng

4. GIAO HÀNG:
- Miễn phí giao hàng nội thành HCM và Hà Nội
- Giao hàng toàn quốc: Phí 30.000đ - 50.000đ tùy khu vực
- Thời gian giao: 1-2 ngày (nội thành), 3-5 ngày (tỉnh)
"""


def search_products(query: str, top_k: int = 5):
    """Simple keyword-based product search for RAG context."""
    query_lower = query.lower()
    scored = []
    for p in PRODUCTS:
        score = 0
        searchable = f"{p['name']} {p['brand']} {p['category']} {p['specs']} {p['description']} {p['type']}".lower()
        # Score by keyword match
        for word in query_lower.split():
            if word in searchable:
                score += 1
        # Boost if type matches
        if "laptop" in query_lower and p["type"] == "laptop":
            score += 2
        if any(w in query_lower for w in ["điện thoại", "phone", "mobile", "dt"]) and p["type"] == "mobile":
            score += 2
        if any(w in query_lower for w in ["rẻ", "giá rẻ", "budget", "sinh viên", "tiết kiệm"]):
            if p["price"] < 700:
                score += 3
        if any(w in query_lower for w in ["gaming", "game", "chơi game"]):
            if p["category"] == "gaming":
                score += 3
        if any(w in query_lower for w in ["cao cấp", "flagship", "tốt nhất", "đắt"]):
            if p["category"] in ("flagship", "ultrabook"):
                score += 3
        scored.append((score, p))

    scored.sort(key=lambda x: -x[0])
    return [p for _, p in scored[:top_k] if _ > 0] or PRODUCTS[:top_k]


def build_context(query: str) -> str:
    """Build RAG context from knowledge base."""
    results = search_products(query)
    parts = ["=== SẢN PHẨM LIÊN QUAN ==="]
    for p in results:
        parts.append(
            f"- {p['name']} ({p['brand']}) | Giá: ${p['price']} | Loại: {p['type']}\n"
            f"  Thông số: {p['specs']}\n"
            f"  Mô tả: {p['description']}"
        )
    parts.append(f"\n{POLICIES}")
    return "\n".join(parts)
