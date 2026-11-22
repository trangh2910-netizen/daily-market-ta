# 📊 Bản Tin Kinh Tế – Chính Trị & Lớp Học TA Hàng Ngày

Hệ thống tự động cập nhật mỗi ngày (không cần bật máy tính), tổng hợp tin vĩ mô, soi chứng khoán Việt Nam & Quốc tế, vẽ biểu đồ chú thích và tạo giọng đọc Podcast tiếng Việt để nghe trên điện thoại, máy tính ở bất kỳ đâu.

## Chạy thử trên máy ngay lập tức
```powershell
.\.venv\Scripts\python.exe main.py
```
Sau khi chạy xong, mở file `docs/index.html` bằng trình duyệt để nghe thử Podcast, xem biểu đồ TA và làm Quiz.

## Cách đưa lên Cloud miễn phí (tắt máy vẫn tự chạy mỗi ngày)

1. **Tạo 1 repository mới trên GitHub** (có thể để **Public** để dùng GitHub Pages miễn phí; hoặc nâng cấp sau nếu muốn Private).
2. **Đẩy toàn bộ thư mục này lên GitHub:**
   ```powershell
   git init
   git add .
   git commit -m "init daily market TA podcast"
   git branch -M main
   git remote add origin https://github.com/<TEN_GITHUB_CUA_BAN>/<TEN_REPO>.git
   git push -u origin main
   ```
3. **Bật GitHub Pages:**
   - Vào **Settings → Pages → Build and deployment**:
     - Source: **Deploy from a branch**
     - Branch: `main`, Folder: `/docs` → **Save**.
   - Sau ~1 phút, trang web của bạn sẽ hoạt động tại `https://<TEN_GITHUB_CUA_BAN>.github.io/<TEN_REPO>/`.
   - Mở link này trên **điện thoại** → chọn **Thêm vào màn hình chính (Add to Home Screen)** để dùng như App riêng!

4. *(Tùy chọn)* **Thêm AI tóm tắt sâu & Email nhắc mỗi ngày:**
   - Vào **Settings → Secrets and variables → Actions → New repository secret**:
     - `GEMINI_API_KEY`: API key Gemini miễn phí (từ Google AI Studio) để AI phân tích tin vĩ mô sâu hơn (nếu không thêm, hệ thống vẫn chạy tốt bằng bộ phân tích nội bộ).
     - `SMTP_USER` / `SMTP_PASS` (Gmail App Password) / `NOTIFY_EMAIL` / `PUBLIC_SITE_URL`: để tự động gửi mail nhắc kèm file MP3 mỗi sáng/chiều.
