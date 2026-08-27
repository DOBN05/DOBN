# DOBN Capital — Backend AI (dữ liệu toàn thị trường + báo cáo AI)

Backend FastAPI bổ sung cho website tĩnh DOBN Capital:

1. **Khuyến nghị cổ phiếu AI** (`/api/recommend`) — sàng lọc rule-based
   trên dữ liệu **cache toàn thị trường** (SQLite, ~1.600+ mã HOSE/HNX/UPCOM),
   sau đó Claude API xếp hạng ra 5 mã + giải thích lý do.
2. **Báo cáo AI theo mã bất kỳ** (`/api/report/{code}`) — thay thế hoàn
   toàn file PDF tĩnh. Gọi `vnstock` SỐNG cho đúng 1 mã (vài giây), đưa
   cho Claude viết báo cáo phân tích có cấu trúc. Hoạt động với **TOÀN BỘ
   mã trên thị trường**, không giới hạn ở 39 mã pool cũ.
3. **Danh sách toàn thị trường** (`/api/stocks`) — phục vụ trang
   `stocks.html`/`stocks1.html` hiển thị lưới công ty full-market thay vì
   chỉ 39 mã.

## Vì sao cần cache SQLite thay vì gọi live 100%?

`vnstock` chỉ lấy chỉ số tài chính **từng mã một**, không có API bulk cho
toàn thị trường. Gọi tuần tự ~1.600 mã mỗi lần user nộp form sẽ mất nhiều
phút và dễ bị chặn IP. Giải pháp: `scripts/sync_market_data.py` chạy
**định kỳ (khuyến nghị 1 lần/ngày qua cron)**, quét toàn thị trường, lưu
vào `market_data.db` (SQLite). `/api/recommend` chỉ đọc từ cache này (nhanh).

Riêng `/api/report/{code}` xử lý **1 mã tại một thời điểm** nên vẫn gọi
`vnstock` sống, real-time, không cần cache.

## Cài đặt & chạy

```bash
cd backend
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Điền ANTHROPIC_API_KEY trong .env

uvicorn main:app --reload --port 8000
```

### Đồng bộ dữ liệu toàn thị trường (bắt buộc để có recommend full-market)

```bash
# Test nhanh trước với 20 mã:
python -m scripts.sync_market_data --limit 20

# Chạy full (mất khá lâu, vài chục phút - 1-2 tiếng tùy mạng):
python -m scripts.sync_market_data
```

**Nếu CHƯA chạy sync lần nào**: `/api/recommend` tự động fallback về pool
39 mã tĩnh cũ (không bị sập, chỉ là chưa "full market"). `/api/report/{code}`
vẫn hoạt động bình thường cho mọi mã vì nó không phụ thuộc cache.

Nên đặt cron chạy sync 1 lần/ngày:
```
0 1 * * * cd /path/to/backend && venv/bin/python -m scripts.sync_market_data >> sync.log 2>&1
```

## Các route

| Route | Method | Mô tả |
|---|---|---|
| `/api/health` | GET | Kiểm tra tình trạng + số mã đã cache |
| `/api/recommend` | POST | `{total_score, risk_type, horizon}` → 5 mã khuyến nghị |
| `/api/stocks?search=&exchange=&limit=` | GET | Danh sách mã từ cache (cho stocks.html) |
| `/api/stock/{code}` | GET | Dữ liệu thô: overview, price_history, chỉ số |
| `/api/report/{code}` | GET | Báo cáo AI đầy đủ cho 1 mã (real-time) |

## ⚠️ Lưu ý quan trọng

1. **Chưa test được với dữ liệu thật.** Môi trường mình dùng để viết code
   này không có internet ra ngoài tới nguồn dữ liệu vnstock. Mình đã xác
   nhận đúng cấu trúc API (`inspect.signature` trên `Quote`, `Finance`,
   `Company`, `Listing` trong `vnstock.api`), và test toàn bộ logic
   nghiệp vụ (cache SQLite, rule-based filter, fallback) bằng dữ liệu giả
   lập — nhưng **chưa chạy được sync script thật**. Hãy chạy
   `--limit 20` trước để kiểm tra, xem log lỗi nếu có và chỉnh tên cột
   trong `app/services/vnstock_data.py` nếu vnstock trả về khác tên.
2. **Không phải lời khuyên đầu tư** — đồ án học thuật.
3. `market_data.db` (SQLite) sẽ được tạo tự động, đã có trong `.gitignore`
   (không nên commit — mỗi máy tự sync riêng, hoặc bạn có thể bỏ dòng đó
   trong `.gitignore` nếu muốn ship kèm data đã sync sẵn).
4. Chi phí Claude API: mỗi lượt `/api/recommend` và mỗi lượt xem
   `/api/report/{code}` đều tốn 1 lần gọi Claude. Cân nhắc thêm cache cho
   báo cáo (ví dụ lưu báo cáo đã sinh vào DB, chỉ tạo lại nếu quá 24h) nếu
   traffic lớn.

## Việc cần làm tiếp theo (gợi ý)

- [ ] Chạy thử sync script với dữ liệu thật, sửa lỗi tên cột nếu cần
- [ ] Cache báo cáo AI đã sinh (tránh gọi lại Claude mỗi lần user xem lại)
- [ ] Deploy backend lên server, đổi `window.DOBN_API_BASE` trong các
      file HTML sang URL thật
- [ ] Đặt cron job chạy `sync_market_data.py` định kỳ trên server
- [ ] Thêm rate-limit cho `/api/recommend` và `/api/report/{code}`
