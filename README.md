# Fairytale Studio · Xưởng Phim Hoạt Hình Cổ Tích AI

Hệ thống sản xuất video hoạt hình truyện cổ tích bằng AI kết hợp kịch bản điện ảnh, bàn làm việc storyboard trực quan và mô hình Google Veo / Flow.

---

## Cấu trúc thư mục Workspace (`D:\Nghia\Truyen co tich\`)

```
D:\Nghia\Truyen co tich\
├── .agents/
│   └── skills/                         # Toàn bộ kỹ năng chuyên biệt cho AI Agent
│       ├── screenwriting/ (sw-*)       # Biên kịch, cấu trúc 3 hồi, đối kháng, thoại
│       ├── xianxia-cinematic-video-director/ # Đạo diễn góc máy điện ảnh cổ phong
│       ├── claude-animation-base/      # Kỹ năng diễn hoạt nét vẽ tay hoạt hình (p5.brush)
│       ├── lemo-opuscar/               # 66 phong cách nghệ thuật phim bằng code
│       ├── manage-storyboard-projects/ # Tạo và quản lý dự án storyboard
│       └── process-storyboard-tasks/   # Tự động điền ảnh/video/audio vào phân cảnh
├── tools/
│   ├── flow-mcp/                       # MCP Server điều khiển Google Flow Veo tự động
│   └── agent-storyboard/               # Bàn làm việc phân cảnh UI trực quan cục bộ
├── stories/                            # Lưu trữ các dự án truyện cổ tích, kịch bản, media
├── mcp_config.json                     # Cấu hình MCP Server tích hợp trực tiếp
└── README.md
```

---

## Khởi động & Đăng nhập nhanh

### 1. Đăng nhập Google Flow (chỉ làm 1 lần đầu tiên)
```bash
cd "D:\Nghia\Truyen co tich\tools\flow-mcp"
npm run login
```
Đăng nhập tài khoản Google trên cửa sổ Chrome vừa mở ra để lưu phiên làm việc cho `flow-mcp`.

### 2. Mở Bàn làm việc Storyboard
Chỉ cần yêu cầu Agent trong chat:
> *"Mở bàn làm việc Storyboard"*
Agent sẽ tự động gọi MCP khởi chạy và gửi đường link truy cập trực tiếp trên trình duyệt.
