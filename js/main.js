/* =========================================================
   공통 스크립트 — 네비, D-day, 아코디언, 필터, 스크롤 애니메이션
   ========================================================= */

(function () {
  "use strict";

  /* ---- 모바일 네비 토글 ---- */
  const toggle = document.querySelector(".nav-toggle");
  const links = document.querySelector(".nav-links");
  if (toggle && links) {
    toggle.addEventListener("click", function () {
      links.classList.toggle("open");
    });
  }

  /* ---- 현재 페이지 nav 활성화 ---- */
  const path = location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll(".nav-links a").forEach(function (a) {
    const href = a.getAttribute("href");
    if (href === path || (path === "" && href === "index.html")) {
      a.classList.add("active");
    }
  });

  /* ---- D-day 계산 ---- */
  function daysUntil(dateStr) {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const target = new Date(dateStr + "T00:00:00");
    return Math.round((target - today) / 86400000);
  }

  const ddayNum = document.getElementById("dday-num");
  if (ddayNum && window.EXAM_DATE) {
    const d = daysUntil(window.EXAM_DATE);
    if (d > 0) ddayNum.innerHTML = "D-" + d + "<span>일</span>";
    else if (d === 0) ddayNum.innerHTML = "D-DAY";
    else ddayNum.innerHTML = "D+" + Math.abs(d) + "<span>일</span>";
    const dateEl = document.getElementById("dday-date");
    if (dateEl) {
      const dt = new Date(window.EXAM_DATE + "T00:00:00");
      dateEl.textContent =
        dt.getFullYear() + "년 " + (dt.getMonth() + 1) + "월 " + dt.getDate() + "일 시행 예정";
    }
  }

  /* ---- 주요 일정 리스트 ---- */
  const dlist = document.getElementById("dday-list");
  if (dlist && window.KEY_DATES) {
    window.KEY_DATES.forEach(function (item) {
      const d = daysUntil(item.date);
      const li = document.createElement("li");
      const tag = d > 0 ? "D-" + d : d === 0 ? "D-DAY" : "종료";
      li.innerHTML =
        '<span>' + item.label + "</span><span class='tag'>" + tag + "</span>";
      dlist.appendChild(li);
    });
  }

  /* ---- 아코디언 ---- */
  document.querySelectorAll(".acc-head").forEach(function (head) {
    head.addEventListener("click", function () {
      const item = head.parentElement;
      const body = item.querySelector(".acc-body");
      const isOpen = item.classList.contains("open");
      if (isOpen) {
        item.classList.remove("open");
        body.style.maxHeight = null;
      } else {
        item.classList.add("open");
        body.style.maxHeight = body.scrollHeight + "px";
      }
    });
  });

  /* ---- 체크리스트 토글 (localStorage 저장) ---- */
  document.querySelectorAll(".checklist").forEach(function (list) {
    const key = "checklist:" + (list.dataset.key || location.pathname);
    let saved = {};
    try { saved = JSON.parse(localStorage.getItem(key) || "{}"); } catch (e) {}
    list.querySelectorAll("li").forEach(function (li, i) {
      if (saved[i]) li.classList.add("done");
      li.addEventListener("click", function () {
        li.classList.toggle("done");
        saved[i] = li.classList.contains("done");
        try { localStorage.setItem(key, JSON.stringify(saved)); } catch (e) {}
      });
    });
  });

  /* ---- 공유 기능 (링크 복사 / 네이티브 공유 / SNS) ---- */
  (function () {
    var SITE = "https://daeip24.com";
    var urlEl = document.getElementById("share-url");
    if (!urlEl && !document.getElementById("copy-btn")) return;
    var url = (urlEl && urlEl.textContent.trim()) || SITE;
    var title = "입시나침반 | 수능·대학입시 정보";
    var copyBtn = document.getElementById("copy-btn");
    var shareBtn = document.getElementById("share-btn");
    var xa = document.getElementById("share-x");
    var fb = document.getElementById("share-fb");
    if (xa) xa.href = "https://twitter.com/intent/tweet?text=" + encodeURIComponent(title) + "&url=" + encodeURIComponent(url);
    if (fb) fb.href = "https://www.facebook.com/sharer/sharer.php?u=" + encodeURIComponent(url);

    function flash() {
      if (!copyBtn) return;
      var o = copyBtn.innerHTML;
      copyBtn.innerHTML = "✅ 복사됨!";
      setTimeout(function () { copyBtn.innerHTML = o; }, 1600);
    }
    function fallbackCopy() {
      try {
        var t = document.createElement("textarea");
        t.value = url; t.style.position = "fixed"; t.style.opacity = "0";
        document.body.appendChild(t); t.focus(); t.select();
        document.execCommand("copy"); document.body.removeChild(t); flash();
      } catch (e) { alert("공유 링크: " + url); }
    }
    function copy() {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(flash, fallbackCopy);
      } else { fallbackCopy(); }
    }
    if (copyBtn) copyBtn.addEventListener("click", copy);
    if (shareBtn) shareBtn.addEventListener("click", function () {
      if (navigator.share) {
        navigator.share({ title: title, text: title, url: url }).catch(function () {});
      } else { copy(); }
    });
  })();

  /* ---- 스크롤 등장 애니메이션 ---- */
  const reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && reveals.length) {
    const io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) {
            e.target.classList.add("in");
            io.unobserve(e.target);
          }
        });
      },
      { threshold: 0.12 }
    );
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("in"); });
  }
})();
