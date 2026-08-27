// ═══════════════════════════════════════════════════════════
//  DOBN Capital — Frontend: Gửi PDF qua Email
//
//  Thay thế hàm downloadPDFFile() hiện tại trong customer.html
//  bằng hàm downloadPDFFile() bên dưới.
//
//  Đổi EMAIL_SERVER_URL thành URL thật của Node server của bạn.
// ═══════════════════════════════════════════════════════════

const EMAIL_SERVER_URL = 'http://localhost:3000/send-report';
// Khi deploy đổi thành: 'https://your-server.com/send-report'

async function downloadPDFFile() {
  const { jsPDF } = window.jspdf;

  const page1 = document.getElementById('pdfPage1');
  const page2 = document.getElementById('pdfPage2');
  page1.classList.remove('hidden');
  page2.classList.remove('hidden');

  // Hiện trạng thái loading
  const btn = document.querySelector('.btn-download');
  const originalHTML = btn.innerHTML;
  btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang xử lý...';
  btn.disabled = true;

  try {
    // 1. Generate PDF
    await new Promise(r => setTimeout(r, 800));
    const pdf = new jsPDF('p', 'mm', 'a4');
    const W = pdf.internal.pageSize.getWidth();
    const H = pdf.internal.pageSize.getHeight();

    const c1 = await html2canvas(page1, { scale: 2, useCORS: true, backgroundColor: '#ffffff' });
    pdf.addImage(c1.toDataURL('image/png'), 'PNG', 0, 0, W, H);
    pdf.addPage();
    const c2 = await html2canvas(page2, { scale: 2, useCORS: true, backgroundColor: '#ffffff' });
    pdf.addImage(c2.toDataURL('image/png'), 'PNG', 0, 0, W, H);

    // 2. Tải xuống cho người dùng (vẫn giữ tính năng download local)
    pdf.save('DOBN_Capital_Report.pdf');

    // 3. Lấy base64 để gửi email (KHÔNG có prefix "data:application/pdf;base64,")
    const pdfBase64 = pdf.output('datauristring').split(',')[1];

    // 4. Lấy thông tin từ form
    const clientName    = document.getElementById('custName').value;
    const recipientEmail = document.getElementById('custEmail').value;

    // Lấy risk info đã tính sẵn từ DOM PDF
    const riskLevel      = document.getElementById('pdfRisk')?.innerText     || '';
    const investmentType = document.getElementById('pdfType')?.innerText     || '';
    const timeHorizon    = document.getElementById('pdfType')?.innerText     || '';

    // Nếu người dùng chưa điền email thì skip gửi mail
    if (!recipientEmail) {
      showToast('Không có email để gửi. Báo cáo đã được tải xuống.', 'warning');
      return;
    }

    // 5. Gọi API backend
    btn.innerHTML = '<i class="fas fa-paper-plane fa-spin"></i> Đang gửi email...';

    const response = await fetch(EMAIL_SERVER_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        pdfBase64,
        recipientEmail,
        clientName,
        riskLevel,
        investmentType,
        timeHorizon,
      }),
    });

    const result = await response.json();

    if (result.success) {
      showToast(`✅ Báo cáo đã được gửi tới ${recipientEmail}`, 'success');
    } else {
      showToast('⚠️ Tải xuống thành công nhưng không gửi được email.', 'warning');
      console.error(result);
    }

  } catch (err) {
    console.error('Lỗi gửi email:', err);
    showToast('⚠️ Đã tải xuống, nhưng gửi email thất bại.', 'warning');
  } finally {
    btn.innerHTML = originalHTML;
    btn.disabled = false;
  }
}

// ── Toast notification nhỏ gọn ──────────────────
function showToast(message, type = 'success') {
  const existing = document.getElementById('dobn-toast');
  if (existing) existing.remove();

  const colors = {
    success: { bg: '#04045d', border: '#c4922a', text: '#fff' },
    warning: { bg: '#7c5a10', border: '#e0b55a', text: '#fff' },
  };
  const c = colors[type] || colors.success;

  const toast = document.createElement('div');
  toast.id = 'dobn-toast';
  toast.style.cssText = `
    position:fixed;bottom:32px;right:32px;z-index:9999;
    background:${c.bg};border:1px solid ${c.border};color:${c.text};
    padding:14px 22px;border-radius:10px;font-size:.85rem;font-weight:500;
    box-shadow:0 8px 32px rgba(0,0,0,.25);
    animation:slideUp .3s ease forwards;
    max-width:340px;line-height:1.5;
  `;
  toast.innerHTML = message;

  // inject keyframe nếu chưa có
  if (!document.getElementById('toast-style')) {
    const s = document.createElement('style');
    s.id = 'toast-style';
    s.textContent = '@keyframes slideUp{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}';
    document.head.appendChild(s);
  }

  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 5000);
}
