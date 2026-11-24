"""Build a mobile-first, PWA-ready personal podcast & TA learning web app in docs/."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from config import DOCS_DIR


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="theme-color" content="#0b1120" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
  <link rel="manifest" href="./manifest.json" />
  <title>Bản Tin &amp; Học TA Hàng Ngày</title>
  <style>
    :root {
      --bg: #0b1120;
      --surface: #111827;
      --surface-2: #1e293b;
      --border: #334155;
      --text: #f8fafc;
      --muted: #94a3b8;
      --accent: #38bdf8;
      --green: #22c55e;
      --red: #ef4444;
      --amber: #f59e0b;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
      padding-bottom: 48px;
    }
    .container { max-width: 960px; margin: 0 auto; padding: 16px; }
    header {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      padding: 14px 0 18px;
      border-bottom: 1px solid var(--border);
    }
    .brand h1 { margin: 0; font-size: 1.35rem; color: #f8fafc; }
    .brand p { margin: 4px 0 0; font-size: 0.88rem; color: var(--muted); }
    select.ep-select {
      background: var(--surface-2);
      color: var(--text);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 9px 12px;
      font-size: 0.92rem;
    }
    .card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 18px;
      margin-top: 18px;
    }
    .section-title {
      margin: 0 0 12px;
      font-size: 1.08rem;
      display: flex;
      align-items: center;
      gap: 8px;
      color: #e2e8f0;
    }
    /* Podcast Player */
    .player-card {
      background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
      border-color: #38bdf866;
    }
    .player-controls {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 10px;
      margin-top: 12px;
    }
    .btn {
      background: var(--surface-2);
      color: var(--text);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 8px 14px;
      font-size: 0.9rem;
      cursor: pointer;
      font-weight: 600;
    }
    .btn:hover { border-color: var(--accent); }
    .btn-primary {
      background: #0284c7;
      border-color: #38bdf8;
      color: #fff;
      padding: 10px 18px;
    }
    .progress-wrap {
      width: 100%;
      margin-top: 12px;
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 0.82rem;
      color: var(--muted);
    }
    input[type="range"] {
      flex: 1;
      accent-color: var(--accent);
      cursor: pointer;
    }
    .script-box {
      margin-top: 14px;
      padding: 14px;
      background: #0b1120;
      border-radius: 12px;
      border: 1px solid var(--border);
      font-size: 0.92rem;
      color: #cbd5e1;
      white-space: pre-line;
      display: none;
    }
    /* Macro strip */
    .macro-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(165px, 1fr));
      gap: 10px;
    }
    .macro-item {
      background: var(--surface-2);
      border-radius: 12px;
      padding: 12px;
      border: 1px solid #33415580;
    }
    .macro-label { font-size: 0.8rem; color: var(--muted); }
    .macro-val { font-size: 1.15rem; font-weight: 700; margin: 4px 0 2px; }
    .up { color: var(--green); }
    .down { color: var(--red); }
    .flat { color: var(--amber); }
    /* News */
    .news-item {
      padding: 14px;
      background: var(--surface-2);
      border-radius: 12px;
      margin-bottom: 10px;
      border-left: 4px solid var(--accent);
    }
    .news-item.positive { border-left-color: var(--green); }
    .news-item.caution { border-left-color: var(--amber); }
    .news-meta { font-size: 0.78rem; color: var(--muted); margin-bottom: 4px; }
    .news-title { font-weight: 700; font-size: 0.98rem; margin: 0 0 6px; }
    .news-title a { color: #f8fafc; text-decoration: none; }
    .news-title a:hover { text-decoration: underline; color: var(--accent); }
    .news-meaning {
      font-size: 0.88rem;
      color: #cbd5e1;
      background: #0f172a;
      padding: 8px 10px;
      border-radius: 8px;
    }
    /* Charts */
    .chart-img {
      width: 100%;
      height: auto;
      border-radius: 12px;
      border: 1px solid var(--border);
      margin-top: 8px;
      display: block;
    }
    /* Watchlist table */
    .table-wrap { overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
    th, td { padding: 10px 8px; text-align: left; border-bottom: 1px solid #1e293b; }
    th { color: var(--muted); font-size: 0.8rem; font-weight: 600; }
    .badge {
      display: inline-block;
      padding: 3px 9px;
      border-radius: 999px;
      font-size: 0.76rem;
      font-weight: 700;
    }
    .badge.bullish { background: #14532d; color: #86efac; }
    .badge.caution { background: #78350f; color: #fde68a; }
    .badge.bearish { background: #7f1d1d; color: #fca5a5; }
    .badge.neutral { background: #334155; color: #e2e8f0; }
    /* Quiz */
    .quiz-box {
      margin-top: 14px;
      padding: 14px;
      background: #0f172a;
      border-radius: 12px;
      border: 1px solid #38bdf844;
    }
    .quiz-opt {
      display: block;
      width: 100%;
      text-align: left;
      margin-top: 8px;
      padding: 10px 12px;
      background: var(--surface-2);
      color: var(--text);
      border: 1px solid var(--border);
      border-radius: 10px;
      cursor: pointer;
      font-size: 0.9rem;
    }
    .quiz-opt.correct { background: #14532d; border-color: var(--green); }
    .quiz-opt.wrong { background: #7f1d1d; border-color: var(--red); }
    .quiz-explain { margin-top: 10px; font-size: 0.88rem; color: #bae6fd; display: none; }
    .pill-note {
      display: inline-block;
      font-size: 0.8rem;
      background: #1e293b;
      color: #7dd3fc;
      padding: 4px 10px;
      border-radius: 999px;
      margin-top: 6px;
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="brand">
        <h1>📊 Bản Tin &amp; Học TA Hàng Ngày</h1>
        <p id="subHeader">Đang tải dữ liệu...</p>
      </div>
      <select id="episodeSelect" class="ep-select" aria-label="Chọn ngày bản tin"></select>
    </header>

    <!-- Audio Player -->
    <section class="card player-card">
      <h2 class="section-title">🎧 Nghe Podcast Gia Sư Hôm Nay</h2>
      <div id="introNote" style="font-size:0.93rem;color:#cbd5e1;"></div>
      <audio id="audioEl" preload="metadata"></audio>
      <div class="player-controls">
        <button id="playBtn" class="btn btn-primary">▶ Nghe bản tin</button>
        <button id="back15Btn" class="btn">-15s</button>
        <button id="fwd15Btn" class="btn">+15s</button>
        <button id="speedBtn" class="btn">Tốc độ: 1.0x</button>
        <button id="toggleScriptBtn" class="btn">📄 Đọc lời giảng</button>
      </div>
      <div class="progress-wrap">
        <span id="curTime">00:00</span>
        <input id="seekBar" type="range" min="0" max="100" value="0" />
        <span id="durTime">00:00</span>
      </div>
      <div id="scriptBox" class="script-box"></div>
      <div id="tiktokBox" style="margin-top:16px;display:none;">
        <div style="font-weight:700;font-size:0.95rem;color:#7dd3fc;margin-bottom:8px;">🎬 Video TikTok / Reels dọc (9:16) sẵn sàng đăng:</div>
        <video id="tiktokVideo" controls playsinline style="width:100%;max-width:340px;border-radius:14px;border:1px solid #334155;display:block;"></video>
      </div>
    </section>

    <!-- TA Lesson + Real Annotated Chart -->
    <section class="card" id="lessonSection">
      <h2 class="section-title">🎓 Mỗi Ngày 1 Chiêu TA (Thực chiến trên chart thật)</h2>
      <div id="lessonTitle" style="font-weight:700;font-size:1.05rem;color:#7dd3fc;"></div>
      <p id="lessonConcept" style="margin:8px 0;"></p>
      <div id="caseWalkthrough" style="background:#1e293b;padding:12px;border-radius:10px;font-size:0.92rem;"></div>
      <div id="lessonChartWrap" style="margin-top:12px;"></div>
      <div id="taFileWrap" style="margin-top:10px;display:none;">
        <a id="taFileLink" href="#" target="_blank" rel="noopener" class="btn" style="display:inline-block;text-decoration:none;background:#0f172a;border-color:#38bdf8;">📘 Mở / Tải File Bài Học TA (Song ngữ Việt–Anh)</a>
      </div>
      <div class="quiz-box">
        <div style="font-weight:700;font-size:0.94rem;">✅ Mini Quiz kiểm tra nhanh:</div>
        <div id="quizQuestion" style="margin-top:6px;font-size:0.93rem;"></div>
        <div id="quizOptions"></div>
        <div id="quizExplain" class="quiz-explain"></div>
      </div>
    </section>

    <!-- Macro & VN-Index -->
    <section class="card">
      <h2 class="section-title">📈 Bức Tranh Thị Trường &amp; Vĩ Mô</h2>
      <div id="macroGrid" class="macro-grid"></div>
      <div id="vniChartWrap" style="margin-top:14px;"></div>
    </section>

    <!-- Watchlist Table -->
    <section class="card">
      <h2 class="section-title">🔍 Soi Watchlist Bằng Ngôn Ngữ Bình Dân</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Mã</th>
              <th>Giá đóng cửa</th>
              <th>Thay đổi</th>
              <th>Khối lượng</th>
              <th>Trạng thái &amp; Giải thích</th>
            </tr>
          </thead>
          <tbody id="watchlistBody"></tbody>
        </table>
      </div>
    </section>

    <!-- News -->
    <section class="card">
      <h2 class="section-title">📰 Tin Kinh Tế – Chính Trị ("Tin gì? → Vậy thì sao?")</h2>
      <div id="newsList"></div>
    </section>

    <!-- Uni Exam Examples -->
    <section class="card" id="uniSection" style="display:none;border-color:#f59e0b55;">
      <h2 class="section-title">📚 Kho Ví Dụ Thi Tự Luận Cuối Kỳ (Liên hệ môn học)</h2>
      <div id="uniList"></div>
    </section>

    <!-- English Summary -->
    <section class="card" id="enSection" style="display:none;border-color:#3b82f655;">
      <h2 class="section-title">🇬🇧 English Recap &amp; Financial Vocabulary</h2>
      <div id="enContent"></div>
    </section>
  </div>

  <script>
    window.__ARCHIVE_DATA__ = __ARCHIVE_JSON__;
  </script>
  <script>
    const episodes = window.__ARCHIVE_DATA__ || [];
    const epSelect = document.getElementById("episodeSelect");
    const audioEl = document.getElementById("audioEl");
    const playBtn = document.getElementById("playBtn");
    const seekBar = document.getElementById("seekBar");
    const curTimeEl = document.getElementById("curTime");
    const durTimeEl = document.getElementById("durTime");
    const speedBtn = document.getElementById("speedBtn");
    const scriptBox = document.getElementById("scriptBox");
    const speeds = [1.0, 1.25, 1.5];
    let speedIdx = 0;

    function fmtTime(sec) {
      if (!isFinite(sec)) return "00:00";
      const m = Math.floor(sec / 60);
      const s = Math.floor(sec % 60);
      return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
    }

    function fmtVnd(val, isIndex) {
      if (val == null) return "-";
      return isIndex
        ? Number(val).toLocaleString("vi-VN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })
        : Number(val).toLocaleString("vi-VN", { maximumFractionDigits: 0 });
    }

    function clsPct(p) {
      if (p > 0) return "up";
      if (p < 0) return "down";
      return "flat";
    }

    function renderEpisode(ep) {
      if (!ep) return;
      document.getElementById("subHeader").innerHTML =
        `Cập nhật lúc ${ep.generated_time_vn} ngày ${ep.generated_date_vn} · ` +
        `<span class="pill-note">Dữ liệu phiên ${ep.market_trade_date_vn}</span>`;

      document.getElementById("introNote").textContent = ep.briefing.intro_note || "";
      scriptBox.textContent = ep.briefing.podcast_script || "";

      // Audio
      audioEl.pause();
      audioEl.src = ep.audio_rel_path;
      audioEl.load();
      playBtn.textContent = "▶ Nghe bản tin";
      seekBar.value = 0;
      curTimeEl.textContent = "00:00";

      // TikTok video preview
      const tiktokBox = document.getElementById("tiktokBox");
      const tiktokVideo = document.getElementById("tiktokVideo");
      if (ep.tiktok_rel_path) {
        tiktokVideo.src = ep.tiktok_rel_path;
        tiktokBox.style.display = "block";
      } else {
        tiktokBox.style.display = "none";
      }

      // Lesson
      const lesson = ep.lesson;
      document.getElementById("lessonTitle").textContent = lesson.title;
      document.getElementById("lessonConcept").textContent = lesson.concept_plain;
      document.getElementById("caseWalkthrough").innerHTML =
        `<strong>👀 Nhìn vào biểu đồ thật (${ep.case_stock_symbol || "VNINDEX"}):</strong> ${ep.briefing.case_walkthrough || ""}`;

      const lessonChartWrap = document.getElementById("lessonChartWrap");
      lessonChartWrap.innerHTML = ep.lesson_chart_rel_path
        ? `<img class="chart-img" src="${ep.lesson_chart_rel_path}" alt="Biểu đồ bài học TA" />`
        : "";
      const taFileWrap = document.getElementById("taFileWrap");
      const taFileLink = document.getElementById("taFileLink");
      if (ep.ta_file_rel_path) {
        taFileLink.href = ep.ta_file_rel_path;
        taFileWrap.style.display = "block";
      } else {
        taFileWrap.style.display = "none";
      }

      // Quiz
      const q = lesson.quiz;
      document.getElementById("quizQuestion").textContent = q.question;
      const optBox = document.getElementById("quizOptions");
      const expBox = document.getElementById("quizExplain");
      optBox.innerHTML = "";
      expBox.style.display = "none";
      expBox.textContent = "💡 Giải thích: " + q.explanation;

      q.options.forEach((optText, idx) => {
        const b = document.createElement("button");
        b.className = "quiz-opt";
        b.textContent = optText;
        b.onclick = () => {
          Array.from(optBox.children).forEach((child, cIdx) => {
            child.classList.remove("correct", "wrong");
            if (cIdx === q.answer_index) child.classList.add("correct");
            else if (cIdx === idx) child.classList.add("wrong");
          });
          expBox.style.display = "block";
        };
        optBox.appendChild(b);
      });

      // Macro grid
      const macroGrid = document.getElementById("macroGrid");
      const vni = ep.vnindex;
      let macroHtml = `
        <div class="macro-item">
          <div class="macro-label">VN-Index (${vni.trade_date_vn})</div>
          <div class="macro-val">${fmtVnd(vni.close, true)}</div>
          <div class="${clsPct(vni.change_pct)}">${vni.change_pct > 0 ? "+" : ""}${vni.change_pct.toFixed(2)}%</div>
        </div>
      `;
      (ep.macro || []).forEach(m => {
        if (m.close == null) return;
        macroHtml += `
          <div class="macro-item">
            <div class="macro-label">${m.label}</div>
            <div class="macro-val">${Number(m.close).toLocaleString("vi-VN")}</div>
            <div class="${clsPct(m.change_pct)}">${m.change_pct > 0 ? "+" : ""}${m.change_pct.toFixed(2)}%</div>
          </div>
        `;
      });
      macroGrid.innerHTML = macroHtml;

      document.getElementById("vniChartWrap").innerHTML = ep.vni_chart_rel_path
        ? `<img class="chart-img" src="${ep.vni_chart_rel_path}" alt="Biểu đồ VN-Index" />`
        : "";

      // Watchlist
      const tbody = document.getElementById("watchlistBody");
      tbody.innerHTML = (ep.stocks || []).map(s => `
        <tr>
          <td><strong>${s.symbol}</strong><br/><span style="font-size:0.75rem;color:#94a3b8;">${s.name}</span></td>
          <td>${fmtVnd(s.close, false)} đ</td>
          <td class="${clsPct(s.change_pct)}"><strong>${s.change_pct > 0 ? "+" : ""}${s.change_pct.toFixed(2)}%</strong></td>
          <td>${s.vol_ratio.toFixed(1)}x TB</td>
          <td>
            <span class="badge ${s.status_tone}">${s.status_label}</span>
            <div style="font-size:0.82rem;color:#cbd5e1;margin-top:4px;">${s.beginner_note}</div>
            <div style="font-size:0.76rem;color:#94a3b8;margin-top:2px;">${s.rsi_plain}</div>
          </td>
        </tr>
      `).join("");

      // News
      const newsList = document.getElementById("newsList");
      const insights = ep.briefing.news_insights;
      if (insights && insights.length) {
        newsList.innerHTML = insights.map(n => `
          <div class="news-item ${n.tone || 'neutral'}">
            <div class="news-title">${n.title}</div>
            <div class="news-meaning"><strong>Vậy thì sao?</strong> ${n.so_what}</div>
          </div>
        `).join("");
      } else {
        newsList.innerHTML = (ep.news || []).map(n => `
          <div class="news-item ${n.impact_tone || 'neutral'}">
            <div class="news-meta">${n.source} · ${n.category} · ${n.published_vn}</div>
            <div class="news-title"><a href="${n.link}" target="_blank" rel="noopener">${n.title}</a></div>
            <div class="news-meaning"><strong>Ý nghĩa cho người mới:</strong> ${n.beginner_meaning}</div>
          </div>
        `).join("");
      }

      // Uni exam examples
      const uniSection = document.getElementById("uniSection");
      const uniList = document.getElementById("uniList");
      const uniEx = ep.briefing.uni_exam_examples || [];
      if (uniEx.length) {
        uniSection.style.display = "block";
        uniList.innerHTML = uniEx.map(ex => `
          <div class="news-item caution">
            <div class="news-meta">${ex.subject} · ${ex.concept}</div>
            <div class="news-meaning"><strong>Ví dụ viết bài tự luận:</strong> ${ex.essay_example}</div>
          </div>
        `).join("");
      } else {
        uniSection.style.display = "none";
      }

      // English recap
      const enSection = document.getElementById("enSection");
      const enContent = document.getElementById("enContent");
      const en = ep.briefing.english_summary;
      if (en && (en.market_summary_en || en.ta_lesson_en)) {
        enSection.style.display = "block";
        const vocabHtml = (en.vocab || []).map(v =>
          `<li><strong>${v.term}</strong> (${v.vn}): ${v.meaning}</li>`
        ).join("");
        enContent.innerHTML = `
          <div style="font-weight:700;color:#7dd3fc;margin-bottom:6px;">${en.headline_en || ""}</div>
          <p style="margin:6px 0;">${en.market_summary_en || ""}</p>
          <p style="margin:6px 0;color:#cbd5e1;"><em>TA Focus:</em> ${en.ta_lesson_en || ""}</p>
          ${vocabHtml ? `<ul style="padding-left:18px;font-size:0.9rem;color:#e2e8f0;">${vocabHtml}</ul>` : ""}
        `;
      } else {
        enSection.style.display = "none";
      }
    }

    // Populate selector
    episodes.forEach((ep, idx) => {
      const opt = document.createElement("option");
      opt.value = idx;
      opt.textContent = `${ep.generated_date_vn} (${ep.generated_time_vn}) — ${ep.lesson.title.split(":")[0]}`;
      epSelect.appendChild(opt);
    });
    epSelect.onchange = () => renderEpisode(episodes[Number(epSelect.value)]);

    playBtn.onclick = () => {
      if (audioEl.paused) { audioEl.play(); playBtn.textContent = "⏸ Tạm dừng"; }
      else { audioEl.pause(); playBtn.textContent = "▶ Nghe bản tin"; }
    };
    document.getElementById("back15Btn").onclick = () => { audioEl.currentTime = Math.max(0, audioEl.currentTime - 15); };
    document.getElementById("fwd15Btn").onclick = () => { audioEl.currentTime = Math.min(audioEl.duration || 0, audioEl.currentTime + 15); };
    speedBtn.onclick = () => {
      speedIdx = (speedIdx + 1) % speeds.length;
      audioEl.playbackRate = speeds[speedIdx];
      speedBtn.textContent = `Tốc độ: ${speeds[speedIdx].toFixed(2).replace(".00", ".0")}x`;
    };
    document.getElementById("toggleScriptBtn").onclick = () => {
      scriptBox.style.display = scriptBox.style.display === "block" ? "none" : "block";
    };
    audioEl.ontimeupdate = () => {
      curTimeEl.textContent = fmtTime(audioEl.currentTime);
      durTimeEl.textContent = fmtTime(audioEl.duration);
      if (audioEl.duration) seekBar.value = (audioEl.currentTime / audioEl.duration) * 100;
    };
    audioEl.onloadedmetadata = () => { durTimeEl.textContent = fmtTime(audioEl.duration); };
    audioEl.onended = () => { playBtn.textContent = "▶ Nghe lại"; };
    seekBar.oninput = () => {
      if (audioEl.duration) audioEl.currentTime = (seekBar.value / 100) * audioEl.duration;
    };

    if (episodes.length > 0) renderEpisode(episodes[0]);
  </script>
</body>
</html>
"""


def write_pwa_manifest(docs_dir: Path = DOCS_DIR) -> None:
    manifest = {
        "name": "Bản Tin & Học TA Hàng Ngày",
        "short_name": "TA Podcast",
        "start_url": "./index.html",
        "display": "standalone",
        "background_color": "#0b1120",
        "theme_color": "#0b1120",
        "description": "Tổng hợp kinh tế chính trị, soi chứng khoán và học Phân tích kỹ thuật mỗi ngày.",
    }
    (docs_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def build_web_site(episodes: list[dict[str, Any]], docs_dir: Path = DOCS_DIR) -> Path:
    """Write data.json, manifest.json, and self-contained index.html in docs/."""
    docs_dir.mkdir(parents=True, exist_ok=True)
    write_pwa_manifest(docs_dir)

    archive_json = json.dumps(episodes, ensure_ascii=False)
    (docs_dir / "archive.json").write_text(archive_json, encoding="utf-8")

    html = HTML_TEMPLATE.replace("__ARCHIVE_JSON__", archive_json)
    index_path = docs_dir / "index.html"
    index_path.write_text(html, encoding="utf-8")
    return index_path
