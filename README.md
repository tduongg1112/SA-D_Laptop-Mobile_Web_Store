# kiemtra01_01.06_duongnt

Project Django microservices cho bai kiem tra:
- customer-service (MySQL)
- staff-service (MySQL)
- laptop-service (PostgreSQL)
- mobile-service (PostgreSQL)
- api-gateway (Nginx)

## Chuc nang
- Customer: dang nhap, tao gio hang, them san pham vao gio, tim kiem laptop/mobile.
- Staff: dang nhap, them mat hang, cap nhat item.
- 2 giao dien rieng: Customer va Staff.

## Chay bang Docker

Yeu cau: Docker Desktop.

```bash
cd kiemtra01_01.06_duongnt
docker compose up --build
```

Mo trinh duyet:
- API Gateway: http://localhost:8080/
- Customer UI: http://localhost:8080/customer/
- Staff UI: http://localhost:8080/staff/
- Laptop service: http://localhost:8080/laptop/
- Mobile service: http://localhost:8080/mobile/

## API tim kiem
- Laptop: http://localhost:8080/api/laptops/search/?q=dell
- Mobile: http://localhost:8080/api/mobiles/search/?q=iphone
- Customer tong hop: http://localhost:8080/customer/api/search/?q=apple

## Anh can chup de nop bai
1. Man hinh tao project va service.
2. Man hinh API gateway.
3. Man hinh docker (docker compose ps / logs).
4. Man hinh giao dien customer va staff.

Xem file checklist: docs/screenshot_checklist.md
