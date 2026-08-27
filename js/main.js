/**
 * DOBN CAPITAL - Main JavaScript Control
 * Dự án học thuật - Nhóm 3 - L16 BUH
 */

document.addEventListener("DOMContentLoaded", function() {
    // 1. TỰ ĐỘNG XỬ LÝ KHÓA ĐĂNG NHẬP DÀNH RIÊNG CHO TRANG CUSTOMER.HTML
    if (window.location.pathname.includes("customer.html")) {
        // Kiểm tra trạng thái trong phiên làm việc (Session)
        if (sessionStorage.getItem("isLoggedIn") !== "true") {
            injectLoginModal();
        }
    }

    // 2. LOGIC ĐĂNG XUẤT (NẾU CẦN DÙNG CHO CÁC NÚT CHỨC NĂNG)
    const btnLogins = document.querySelectorAll(".btn-login");
    btnLogins.forEach(btn => {
        btn.addEventListener("click", function() {
            if (sessionStorage.getItem("isLoggedIn") === "true") {
                if (confirm("Bạn có muốn đăng xuất khỏi tài khoản định danh?")) {
                    sessionStorage.removeItem("isLoggedIn");
                    sessionStorage.removeItem("currentUser");
                    window.location.reload();
                }
            } else {
                // Nếu đang ở trang khác mà bấm nút đăng nhập, đẩy qua trang customer để kích hoạt form
                window.location.href = "customer.html";
            }
        });
    });
});

/**
 * Hàm khởi tạo và chèn giao diện khóa màn hình đăng nhập vào trang customer.html
 */
function injectLoginModal() {
    // Tạo phần tử overlay bao phủ toàn trang
    const overlay = document.createElement("div");
    overlay.id = "auth-overlay";
    overlay.className = "login-overlay";
    
    overlay.innerHTML = `
        <div class="login-modal">
            <div class="login-brand">
                DOBN <span class="gold-text">CAPITAL</span>
            </div>
            <h3>Yêu Cầu Đăng Nhập</h3>
            <p class="login-subtitle">Vui lòng đăng nhập tài khoản định danh để sử dụng dịch vụ thiết kế kế hoạch tài chính.</p>
            
            <div class="input-group">
                <label for="username"><i class="fas fa-user-shield text-gold"></i> Tên đăng nhập (Mã định danh):</label>
                <input type="text" id="username" placeholder="Ví dụ: DOBNC11123456" autocomplete="off" style="text-transform: uppercase;">
                <small class="input-help">Định dạng bắt buộc: DOBNC11 + 6 số bất kỳ</small>
            </div>

            <div class="input-group">
                <label for="password"><i class="fas fa-lock text-gold"></i> Mật khẩu:</label>
                <input type="password" id="password" placeholder="Nhập mật khẩu tài khoản">
            </div>

            <div id="login-error-msg" class="error-alert" style="display: none;">
                <i class="fas fa-exclamation-circle"></i> Tên đăng nhập sai định dạng! Hệ thống yêu cầu mã số dạng DOBNC11 + 6 số.
            </div>

            <button id="btn-submit-auth" class="btn-login-submit">Xác Nhận Đăng Nhập</button>
            
            <div class="login-footer">
                <a href="index.html"><i class="fas fa-arrow-left"></i> Quay lại Trang chủ</a>
            </div>
        </div>
    `;

    document.body.appendChild(overlay);

    // Xử lý sự kiện xác thực dữ liệu bên trong Modal
    const usernameInput = document.getElementById("username");
    const loginBtn = document.getElementById("btn-submit-auth");
    const errorMsg = document.getElementById("login-error-msg");

    loginBtn.addEventListener("click", function() {
        const usernameValue = usernameInput.value.trim().toUpperCase();
        // Regex kiểm tra chuỗi DOBNC11 kèm đúng 6 chữ số liên tiếp bên dưới
        const dobnRegex = /^DOBNC11\d{6}$/;

        if (dobnRegex.test(usernameValue)) {
            sessionStorage.setItem("isLoggedIn", "true");
            sessionStorage.setItem("currentUser", usernameValue);
            
            // Hiệu ứng mờ dần rồi biến mất
            overlay.style.opacity = "0";
            setTimeout(() => {
                overlay.remove();
            }, 300);
            
            alert("Đăng nhập tài khoản định danh thành công! Hệ thống mở khóa form lập danh mục.");
        } else {
            errorMsg.style.display = "block";
            usernameInput.style.borderColor = "#ef4444";
            usernameInput.focus();
        }
    });

    // Nhấn Enter để gửi nhanh form
    usernameInput.addEventListener("keypress", function(e) {
        if (e.key === "Enter") loginBtn.click();
    });
}
