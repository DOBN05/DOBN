const SUPPORT_SCRIPT_URL =
  "https://script.google.com/macros/s/AKfycbzQdyf4tzwOH5y7P-GXs8QsnFX_UOM-RhyjS5nWH81-VdQ-4el_lKrur-paWekhfOJ8Hw/exec"; // URL từ Apps Script project mới

async function submitSupportForm() {
  const name     = document.getElementById('f-name').value.trim();
  const phone    = document.getElementById('f-phone').value.trim();
  const email    = document.getElementById('f-email').value.trim();
  const category = document.getElementById('f-category').value.trim();
  const priority = document.getElementById('f-priority').value.trim();
  const msg      = document.getElementById('f-message').value.trim();

  if (!name || !email || !msg) {
    alert('Vui lòng điền đầy đủ Họ tên, Email và Nội dung.');
    return;
  }

  const btn = document.querySelector('.btn-submit');
  btn.disabled = true;
  btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang gửi…';

  const formData = {
    timestamp:  new Date().toLocaleString('vi-VN', { timeZone: 'Asia/Ho_Chi_Minh' }),
    ho_ten:     name,
    dien_thoai: phone,
    email:      email,
    danh_muc:   category,
    uu_tien:    priority,
    noi_dung:   msg
  };

  try {
    await fetch(SUPPORT_SCRIPT_URL, {
      method: "POST",
      mode: "no-cors",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData)
    });
    console.log("Đã gửi support form:", formData);

    const toast = document.getElementById('toast');
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3500);

    ['f-name','f-phone','f-email','f-category','f-priority','f-message']
      .forEach(id => { const el = document.getElementById(id); if (el) el.value = ''; });

  } catch (error) {
    console.error("Lỗi gửi form:", error);
    alert('Có lỗi xảy ra. Vui lòng thử lại hoặc gọi hotline.');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-paper-plane"></i> Gửi Yêu Cầu';
  }
}
