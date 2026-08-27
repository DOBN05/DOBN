// ======================================================
// STOCK POOL — GẮN NGÀNH (sector) CHO MỖI MÃ
// ======================================================

const EXPANDED_STOCK_POOL = [

    // ── CONSERVATIVE + LONG TERM ──────────────────────
    { code:"VCB", name:"Ngân hàng TMCP Ngoại thương Việt Nam",       type:"Conservative", horizon:"Long-term",   sector:"Banking",   fundamentalscore:12, expectedReturn:"8-10%",  volatility:"Low",       exchange:"HOSE", logo:"logo/VCB.png" },
    { code:"BID", name:"Ngân hàng TMCP Đầu tư và Phát triển VN",    type:"Conservative", horizon:"Long-term",   sector:"Banking",   fundamentalscore:14, expectedReturn:"8-11%",  volatility:"Low",       exchange:"HOSE", logo:"logo/BID.png" },
    { code:"GAS", name:"Tổng Công ty Khí Việt Nam - CTCP",           type:"Conservative", horizon:"Long-term",   sector:"Energy",    fundamentalscore:14, expectedReturn:"9-11%",  volatility:"Low",       exchange:"HOSE", logo:"logo/GAS.png" },
    { code:"REE", name:"Công ty Cổ phần Cơ Điện Lạnh",               type:"Conservative", horizon:"Long-term",   sector:"Utilities", fundamentalscore:15, expectedReturn:"9-12%",  volatility:"Low",       exchange:"HOSE", logo:"logo/REE.png" },
    { code:"MBB", name:"Ngân hàng TMCP Quân đội",                    type:"Conservative", horizon:"Long-term",   sector:"Banking",   fundamentalscore:16, expectedReturn:"10-12%", volatility:"Low",       exchange:"HOSE", logo:"logo/MBB.png" },
    { code:"CTG", name:"Ngân hàng TMCP Công Thương Việt Nam",        type:"Conservative", horizon:"Long-term",   sector:"Banking",   fundamentalscore:16, expectedReturn:"10-12%", volatility:"Low",       exchange:"HOSE", logo:"logo/CTG.png" },
    { code:"VGI", name:"Tổng Công ty CP Đầu tư Quốc tế Viettel",    type:"Conservative", horizon:"Long-term",   sector:"Telecom",   fundamentalscore:17, expectedReturn:"10-14%", volatility:"Low",       exchange:"UPCOM", logo:"logo/VGI.png" },
    { code:"PLX", name:"Tập đoàn Xăng dầu Việt Nam",                 type:"Conservative", horizon:"Long-term",   sector:"Energy",    fundamentalscore:18, expectedReturn:"10-13%", volatility:"Low",       exchange:"HOSE", logo:"logo/PLX.png" },
    { code:"BVH", name:"Tập đoàn Bảo Việt",                          type:"Conservative", horizon:"Long-term",   sector:"Insurance", fundamentalscore:19, expectedReturn:"10-13%", volatility:"Low",       exchange:"HOSE", logo:"logo/BVH.png" },
    { code:"VNM", name:"Công ty Cổ phần Sữa Việt Nam",               type:"Conservative", horizon:"Long-term",   sector:"Consumer",  fundamentalscore:20, expectedReturn:"8-11%",  volatility:"Low",       exchange:"HOSE", logo:"logo/VNM.png" },

    // ── BALANCED + MEDIUM TERM ────────────────────────
    { code:"FPT", name:"Công ty Cổ phần FPT",                        type:"Balanced", horizon:"Medium-term", sector:"Technology",   fundamentalscore:22, expectedReturn:"12-15%", volatility:"Medium", exchange:"HOSE", logo:"logo/FPT.png" },
    { code:"CTR", name:"Tổng Công ty CP Công trình Viettel",         type:"Balanced", horizon:"Medium-term", sector:"Telecom",      fundamentalscore:24, expectedReturn:"12-15%", volatility:"Medium", exchange:"HOSE", logo:"logo/CTR.png" },
    { code:"GMD", name:"Công ty Cổ phần Gemadept",                   type:"Balanced", horizon:"Medium-term", sector:"Logistics",    fundamentalscore:24, expectedReturn:"12-15%", volatility:"Medium", exchange:"HOSE", logo:"logo/GMD.png" },
    { code:"HPG", name:"Công ty Cổ phần Tập đoàn Hòa Phát",         type:"Balanced", horizon:"Medium-term", sector:"Materials",    fundamentalscore:25, expectedReturn:"13-16%", volatility:"Medium", exchange:"HOSE", logo:"logo/HPG.png" },
    { code:"TCB", name:"Ngân hàng TMCP Kỹ thương Việt Nam",          type:"Balanced", horizon:"Medium-term", sector:"Banking",      fundamentalscore:26, expectedReturn:"13-16%", volatility:"Medium", exchange:"HOSE", logo:"logo/TCB.png" },
    { code:"MWG", name:"Công ty Cổ phần Đầu tư Thế Giới Di Động",   type:"Balanced", horizon:"Medium-term", sector:"Retail",       fundamentalscore:26, expectedReturn:"13-17%", volatility:"Medium", exchange:"HOSE", logo:"logo/MWG.png" },
    { code:"VTP", name:"Tổng Công ty CP Bưu chính Viettel",          type:"Balanced", horizon:"Medium-term", sector:"Logistics",    fundamentalscore:27, expectedReturn:"13-17%", volatility:"Medium", exchange:"HOSE", logo:"logo/VTP.png" },
    { code:"DCM", name:"Công ty Cổ phần Phân bón Dầu khí Cà Mau",   type:"Balanced", horizon:"Medium-term", sector:"Agriculture",  fundamentalscore:28, expectedReturn:"14-18%", volatility:"Medium", exchange:"HOSE", logo:"logo/DCM.png" },
    { code:"DPM", name:"Tổng Công ty Phân bón và Hóa chất Dầu khí", type:"Balanced", horizon:"Medium-term", sector:"Agriculture",  fundamentalscore:28, expectedReturn:"14-18%", volatility:"Medium", exchange:"HOSE", logo:"logo/DPM.png" },
    { code:"MSN", name:"Công ty Cổ phần Tập đoàn Masan",             type:"Balanced", horizon:"Medium-term", sector:"Consumer",     fundamentalscore:29, expectedReturn:"14-18%", volatility:"Medium", exchange:"HOSE", logo:"logo/MSN.png" },
    { code:"KDH", name:"Công ty CP Đầu tư và Kinh doanh Nhà Khang Điền", type:"Balanced", horizon:"Medium-term", sector:"RealEstate", fundamentalscore:30, expectedReturn:"14-18%", volatility:"Medium", exchange:"HOSE", logo:"logo/KDH.png" },
    { code:"HDB", name:"Ngân hàng TMCP Phát triển TP.HCM",           type:"Balanced", horizon:"Medium-term", sector:"Banking",      fundamentalscore:31, expectedReturn:"15-18%", volatility:"Medium", exchange:"HOSE", logo:"logo/HDB.png" },
    { code:"IDC", name:"Tổng Công ty IDICO - CTCP",                  type:"Balanced", horizon:"Medium-term", sector:"Infrastructure", fundamentalscore:25, expectedReturn:"13-16%", volatility:"Medium", exchange:"HNX",  logo:"logo/IDC.png" },
    { code:"OIL", name:"Tổng Công ty Dầu Việt Nam - CTCP",           type:"Balanced", horizon:"Medium-term", sector:"Energy",       fundamentalscore:27, expectedReturn:"12-15%", volatility:"Medium", exchange:"UPCOM", logo:"logo/OIL.png" },

    // ── AGGRESSIVE + SHORT TERM ───────────────────────
    { code:"SSI", name:"Công ty Cổ phần Chứng khoán SSI",            type:"Aggressive", horizon:"Short-term", sector:"Securities",  fundamentalscore:33, expectedReturn:"18-22%", volatility:"High",      exchange:"HOSE", logo:"logo/SSI.png" },
    { code:"VCI", name:"Công ty Cổ phần Chứng khoán Vietcap",        type:"Aggressive", horizon:"Short-term", sector:"Securities",  fundamentalscore:33, expectedReturn:"18-22%", volatility:"High",      exchange:"HOSE", logo:"logo/VCI.png" },
    { code:"HCM", name:"Công ty CP Chứng khoán TP.HCM",              type:"Aggressive", horizon:"Short-term", sector:"Securities",  fundamentalscore:34, expectedReturn:"18-22%", volatility:"High",      exchange:"HOSE", logo:"logo/HCM.png" },
    { code:"DGW", name:"Công ty Cổ phần Thế Giới Số",                type:"Aggressive", horizon:"Short-term", sector:"Technology",  fundamentalscore:34, expectedReturn:"18-24%", volatility:"High",      exchange:"HOSE", logo:"logo/DGW.png" },
    { code:"GEX", name:"Công ty Cổ phần Tập đoàn GELEX",             type:"Aggressive", horizon:"Short-term", sector:"Industrial",  fundamentalscore:35, expectedReturn:"18-24%", volatility:"High",      exchange:"HOSE", logo:"logo/GEX.png" },
    { code:"VRE", name:"Công ty Cổ phần Vincom Retail",               type:"Aggressive", horizon:"Short-term", sector:"RealEstate",  fundamentalscore:36, expectedReturn:"19-24%", volatility:"High",      exchange:"HOSE", logo:"logo/VRE.png" },
    { code:"VHM", name:"Công ty Cổ phần Vinhomes",                   type:"Aggressive", horizon:"Short-term", sector:"RealEstate",  fundamentalscore:37, expectedReturn:"20-25%", volatility:"High",      exchange:"HOSE", logo:"logo/VHM.png" },
    { code:"DXG", name:"Công ty Cổ phần Tập đoàn Đất Xanh",          type:"Aggressive", horizon:"Short-term", sector:"RealEstate",  fundamentalscore:38, expectedReturn:"20-25%", volatility:"High",      exchange:"HOSE", logo:"logo/DXG.png" },
    { code:"VIC", name:"Tập đoàn Vingroup - CTCP",                   type:"Aggressive", horizon:"Short-term", sector:"Conglomerate", fundamentalscore:39, expectedReturn:"20-25%", volatility:"High",      exchange:"HOSE", logo:"logo/VIC.png" },
    { code:"VJC", name:"Công ty Cổ phần Hàng không Vietjet",         type:"Aggressive", horizon:"Short-term", sector:"Aviation",    fundamentalscore:39, expectedReturn:"20-25%", volatility:"High",      exchange:"HOSE", logo:"logo/VJC.png" },
    { code:"NVL", name:"Công ty CP Tập đoàn Đầu tư Địa ốc No Va",   type:"Aggressive", horizon:"Short-term", sector:"RealEstate",  fundamentalscore:40, expectedReturn:"25%+",   volatility:"Very High", exchange:"HOSE", logo:"logo/NVL.png" },
    { code:"YEG", name:"Công ty Cổ phần Tập đoàn Yeah1",             type:"Aggressive", horizon:"Short-term", sector:"Media",       fundamentalscore:40, expectedReturn:"25%+",   volatility:"Very High", exchange:"HOSE", logo:"logo/YEG.png" },
    { code:"SHS", name:"Công ty CP Chứng khoán Sài Gòn - Hà Nội",   type:"Aggressive", horizon:"Short-term", sector:"Securities",  fundamentalscore:34, expectedReturn:"18-23%", volatility:"High",      exchange:"HNX",  logo:"logo/SHS.png" },
    { code:"MSR", name:"Công ty Cổ phần Masan High-Tech Materials",  type:"Aggressive", horizon:"Short-term", sector:"Materials",   fundamentalscore:36, expectedReturn:"20-25%", volatility:"High",      exchange:"UPCOM", logo:"logo/MSR.png" },
    { code:"EVF", name:"Công ty Cổ phần Tài chính Điện lực",         type:"Aggressive", horizon:"Short-term", sector:"Finance",     fundamentalscore:38, expectedReturn:"20-26%", volatility:"High",      exchange:"HOSE", logo:"logo/EVF.png" },
];

// ======================================================
// DOBN CAPITAL — DIVERSIFIED RECOMMENDATION ENGINE (LOCAL FALLBACK)
// Mỗi ngành tối đa MAX_PER_SECTOR mã, tổng 5 mã
// Giữ lại thuật toán cũ để dùng khi KHÔNG gọi được backend AI
// (ví dụ: chưa bật server, mất mạng, hoặc đang demo offline).
// ======================================================

const MAX_PER_SECTOR = 2; // tối đa 2 mã/ngành trong danh mục cuối

function getRecommendationsLocal(score, riskType, horizon) {

    // ── Bước 1: lọc theo horizon ──────────────────────
    let pool = EXPANDED_STOCK_POOL.filter(s => s.horizon === horizon);

    // ── Bước 2: nếu không đủ 5, bổ sung cùng riskType ─
    if (pool.length < 5) {
        const extra = EXPANDED_STOCK_POOL.filter(s => s.type === riskType);
        pool = [...pool, ...extra];
    }

    // ── Bước 3: loại trùng ───────────────────────────
    pool = [...new Map(pool.map(s => [s.code, s])).values()];

    // ── Bước 4: sắp xếp theo độ gần score ───────────
    pool.sort((a, b) =>
        Math.abs(a.fundamentalscore - score) - Math.abs(b.fundamentalscore - score)
    );

    // ── Bước 5: chọn đa dạng ngành ──────────────────
    // Duyệt từ trên xuống (gần score nhất), chọn mã nếu ngành
    // chưa đạt MAX_PER_SECTOR. Dừng khi đủ 5 mã.
    const sectorCount = {};
    const result = [];

    for (const stock of pool) {
        if (result.length >= 5) break;

        const sector = stock.sector;
        const count = sectorCount[sector] || 0;

        if (count < MAX_PER_SECTOR) {
            result.push(stock);
            sectorCount[sector] = count + 1;
        }
    }

    // ── Bước 6: fallback nếu vẫn chưa đủ 5 ──────────
    // (trường hợp pool quá ít sector) — nới lỏng giới hạn
    if (result.length < 5) {
        for (const stock of pool) {
            if (result.length >= 5) break;
            if (!result.find(r => r.code === stock.code)) {
                result.push(stock);
            }
        }
    }

    return result;
}

// ======================================================
// DOBN CAPITAL — AI RECOMMENDATION (LIVE DATA + CLAUDE)
// Gọi backend FastAPI (backend/) để lấy khuyến nghị dựa trên
// dữ liệu tài chính SỐNG từ vnstock + AI xếp hạng/giải thích.
// Nếu backend không phản hồi (chưa bật server, lỗi mạng...),
// tự động rơi về thuật toán tĩnh cũ (getRecommendationsLocal)
// để tính năng không bị sập khi demo.
// ======================================================

const RECOMMEND_API_URL =
    (window.DOBN_API_BASE || "http://localhost:8000") + "/api/recommend";

async function getRecommendations(score, riskType, horizon) {
    try {
        const res = await fetch(RECOMMEND_API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                total_score: score,
                risk_type: riskType,
                horizon: horizon,
            }),
        });

        if (!res.ok) throw new Error(`Backend trả lỗi ${res.status}`);

        const data = await res.json();

        // Chuẩn hoá field cho khớp với chỗ render (stock.code, stock.name)
        return data.recommendations.map(r => ({
            code: r.code,
            name: r.name,
            sector: r.sector,
            matchScore: r.match_score,
            reason: r.reason,
            keyMetrics: r.key_metrics,
        }));
    } catch (err) {
        console.warn(
            "[DOBN] Không gọi được backend AI, dùng fallback tĩnh:",
            err.message
        );
        return getRecommendationsLocal(score, riskType, horizon);
    }
}
