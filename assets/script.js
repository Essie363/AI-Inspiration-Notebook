// ==================== Theme ====================
(function() {
  var saved = localStorage.getItem("ai-inspiration-theme");
  if (saved === "dark") {
    document.documentElement.setAttribute("data-theme", "dark");
  }
})();

function toggleTheme() {
  var isDark = document.documentElement.getAttribute("data-theme") === "dark";
  if (isDark) {
    document.documentElement.removeAttribute("data-theme");
    localStorage.setItem("ai-inspiration-theme", "light");
  } else {
    document.documentElement.setAttribute("data-theme", "dark");
    localStorage.setItem("ai-inspiration-theme", "dark");
  }
}

// ==================== Favorites ====================
function loadFavorites() {
  try { return JSON.parse(localStorage.getItem("ai-inspiration-favs")) || []; }
  catch(e) { return []; }
}

function saveFavorites(f) { localStorage.setItem("ai-inspiration-favs", JSON.stringify(f)); }

function isFavorited(pid) {
  var favs = loadFavorites();
  for (var i = 0; i < favs.length; i++) {
    if (favs[i].id === pid || favs[i] === pid) return true;
  }
  return false;
}

function toggleFavorite(btn) {
  var card = btn.closest(".card");
  var pid = card.getAttribute("data-pid");
  if (!pid) return;
  var favs = loadFavorites();
  var found = false;
  for (var i = 0; i < favs.length; i++) {
    var id = (typeof favs[i] === "string") ? favs[i] : favs[i].id;
    if (id === pid) { favs.splice(i, 1); found = true; break; }
  }
  if (!found) { favs.push({ id: pid, addedAt: new Date().toISOString().slice(0,10) }); }
  saveFavorites(favs);
  updateCardUI(card, !found);
}

function updateCardUI(card, isFav) {
  var btn = card.querySelector(".fav-btn");
  if (!btn) return;
  if (isFav) {
    btn.classList.add("active"); card.classList.add("favorited");
  } else {
    btn.classList.remove("active"); card.classList.remove("favorited");
  }
}

function restoreFavorites() {
  var favs = loadFavorites();
  document.querySelectorAll(".card").forEach(function(card) {
    var pid = card.getAttribute("data-pid");
    if (pid) updateCardUI(card, isFavorited(pid));
  });
}

// ==================== Card Expand/Collapse ====================
function expandCard(card) {
  card.classList.add("expanded");
  setTimeout(function() { card.scrollIntoView({ behavior: "smooth", block: "nearest" }); }, 50);
}

function collapseCard(card) {
  var full = card.querySelector(".card-full");
  if (full) { full.style.opacity = "0"; full.style.transform = "translateY(-8px)"; }
  setTimeout(function() {
    card.classList.remove("expanded");
    if (full) { full.style.opacity = ""; full.style.transform = ""; }
  }, 150);
}

// ==================== Category Filter ====================
function filterCategory(btn, category) {
  document.querySelectorAll(".tab").forEach(function(t) { t.classList.remove("active"); });
  btn.classList.add("active");
  document.querySelectorAll(".card").forEach(function(c) {
    if (category === "all" || c.getAttribute("data-category") === category) {
      c.style.display = "";
    } else {
      c.style.display = "none";
    }
  });
  var expanded = document.querySelector(".card.expanded");
  if (expanded) collapseCard(expanded);
}

// ==================== Favorites Modal ====================
function openFavModal() {
  var favs = loadFavorites();
  var body = document.getElementById("favModalBody");
  var modal = document.getElementById("favModal");
  if (!body || !modal) return;
  if (favs.length === 0) {
    body.innerHTML = "<div class=\"fav-empty\">No favorites yet.</div>";
    modal.style.display = ""; return;
  }
  var groups = {};
  for (var f of favs) {
    var card = document.querySelector('.card[data-pid="' + f.id + '"]');
    if (!card) continue;
    if (!groups[f.addedAt]) groups[f.addedAt] = [];
    var title = (card.querySelector(".card-title") || {}).textContent || f.id;
    var link = (card.querySelector(".ext-link") || {}).getAttribute("href") || "#";
    groups[f.addedAt].push({ id: f.id, title: title, link: link });
  }
  var sortedDates = Object.keys(groups).sort().reverse();
  var html = "";
  for (var d of sortedDates) {
    html += "<div class=\"fav-group\">";
    html += "  <div class=\"fav-group-title\">" + d + "</div>";
    for (var item of groups[d]) {
      html += "  <div class=\"fav-item\">";
      html += "    <div class=\"fav-item-info\">";
      html += "      <span class=\"fav-item-title\">" + item.title + "</span>";
      html += "    </div>";
      html += '    <a href="' + item.link + '" target="_blank" class="fav-item-link">Open</a>';
      html += '    <button class="fav-item-unfav" title="Remove" data-pid="' + item.id + '">♥</button>';
      html += "  </div>";
    }
    html += "</div>";
  }
  body.innerHTML = html;
  modal.style.display = "";
}

function closeFavModal() {
  var modal = document.getElementById("favModal");
  if (modal) modal.style.display = "none";
}

function unfavFromModal(pid) {
  var favs = loadFavorites();
  for (var i = 0; i < favs.length; i++) {
    var id = (typeof favs[i] === "string") ? favs[i] : favs[i].id;
    if (id === pid) { favs.splice(i, 1); break; }
  }
  saveFavorites(favs);
  var card = document.querySelector('.card[data-pid="' + pid + '"]');
  if (card) updateCardUI(card, false);
  openFavModal();
}

document.addEventListener("keydown", function(e) { if (e.key === "Escape") closeFavModal(); });
// ==================== Modal unfav button delegation ====================
document.addEventListener("click", function(e) {
  var btn = e.target.closest(".fav-item-unfav");
  if (!btn) return;
  var pid = btn.getAttribute("data-pid");
  if (pid) unfavFromModal(pid);
});


// ==================== Main Click Handler ====================
document.addEventListener("click", function(e) {
  var favBtn = e.target.closest(".fav-btn");
  if (favBtn) { e.stopPropagation(); toggleFavorite(favBtn); return; }
  var card = e.target.closest(".card");
  if (!card) return;
  if (e.target.closest(".close-btn") || e.target.closest(".ext-link") || e.target.closest(".tab")) return;
  if (card.classList.contains("expanded")) { collapseCard(card); }
  else {
    var expanded = document.querySelector(".card.expanded");
    if (expanded) collapseCard(expanded);
    expandCard(card);
  }
});

document.addEventListener("click", function(e) {
  var cb = e.target.closest(".close-btn");
  if (cb) { e.stopPropagation(); collapseCard(cb.closest(".card")); }
});

// ==================== Sticky Tabs ====================
(function() {
  var sentinel = document.createElement("div");
  sentinel.className = "tabs-scroll-sentinel";
  var tabs = document.querySelector(".tabs");
  if (tabs && tabs.parentNode) {
    tabs.parentNode.insertBefore(sentinel, tabs.nextSibling);
  }
  new IntersectionObserver(function(entries) {
    for (var e of entries) {
      tabs.classList.toggle("tabs--stuck", !e.isIntersecting);
    }
  }, { threshold: 0 }).observe(sentinel);
})();

restoreFavorites();



// ==================== Channel Switcher (PRD 4.1) ====================
var currentChannel = 'notebook';

function switchChannel(btn, channel) {
  if (currentChannel === channel) return;
  setChannel(channel, btn);
}

var _channelScrollY = { notebook: 0, digest: 0 };

function setChannel(channel, btn) {
  // Save current scroll position before switching
  _channelScrollY[currentChannel] = window.scrollY;
  localStorage.setItem('ai-inspiration-channel', channel);

  // Update button states
  document.querySelectorAll('.channel-btn').forEach(function(b) { b.classList.remove('active'); });
  if (btn) btn.classList.add('active');
  else {
    var targetBtn = document.querySelector('.channel-btn[onclick*="' + channel + '"]');
    if (targetBtn) targetBtn.classList.add('active');
  }

  var tabsRow = document.getElementById('tabsRow');
  var cardGrid = document.querySelector('.card-grid');
  var digest = document.getElementById('digestSection');
  var main = document.querySelector('main');
  var footer = document.querySelector('.footer');

  if (channel === 'notebook') {
    if (tabsRow) tabsRow.style.display = '';
    if (cardGrid) cardGrid.style.display = '';
    if (digest) digest.style.display = 'none';
    if (main) main.style.display = '';
    if (footer) footer.style.display = '';
    var allTab = document.querySelector('.tab[onclick*="all"]');
    if (allTab && !allTab.classList.contains('active')) {
      allTab.click();
    }
  } else {
    if (tabsRow) tabsRow.style.display = 'none';
    if (cardGrid) cardGrid.style.display = 'none';
    if (digest) digest.style.display = '';
    if (main) main.style.display = 'none';
    if (footer) footer.style.display = 'none';
  }

  // Restore scroll position for the new channel
  currentChannel = channel;
  window.scrollTo(0, _channelScrollY[channel] || 0);
}





// ==================== Builder Digest Timeline (PRD 4.7) ====================
function switchToTimeline(btn) {
  // Deactivate all tabs, activate clicked one
  document.querySelectorAll(".tab").forEach(function(t) { t.classList.remove("active"); });
  if (btn) btn.classList.add("active");

  // Hide cards, show timeline
  var grid = document.querySelector(".card-grid");
  var digest = document.getElementById("digestSection");
  var main = document.querySelector("main");
  var footer = document.querySelector(".footer");

  if (grid) grid.style.display = "none";
  if (digest) digest.style.display = "";
  if (main) main.style.display = "none";
  if (footer) footer.style.display = "none";
}

// Hook into existing filterCategory to restore card view
var origFilterCategory = filterCategory;
filterCategory = function(btn, category) {
  // Restore card view
  var grid = document.querySelector(".card-grid");
  var digest = document.getElementById("digestSection");
  var main = document.querySelector("main");
  var footer = document.querySelector(".footer");

  if (grid) grid.style.display = "";
  if (digest) digest.style.display = "none";
  if (main) main.style.display = "";
  if (footer) footer.style.display = "";

  // Call original
  origFilterCategory(btn, category);
};

// ==================== Restore channel on load (PRD 4.1) ====================
(function() {
  var savedChannel = localStorage.getItem('ai-inspiration-channel');
  if (savedChannel === 'digest') {
    setChannel('digest');
  }
})();


// ==================== Timeline Sidebar Nav (left sidebar + right content) ====================
(function() {
  var sidebar = document.getElementById('timelineSidebar');
  if (!sidebar) return;

  var items = sidebar.querySelectorAll('.timeline-nav-item');
  var builders = document.querySelectorAll('.timeline-builder');
  if (!items.length || !builders.length) return;

  var builderIds = [];
  builders.forEach(function(b) { if (b.id) builderIds.push(b.id); });

  var observer = new IntersectionObserver(function(entries) {
    var lastVisible = null;
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        lastVisible = entry.target.id;
      }
    });
    if (lastVisible) {
      items.forEach(function(item) {
        if (item.getAttribute('data-builder') === lastVisible) {
          item.classList.add('active');
        } else {
          item.classList.remove('active');
        }
      });
    }
  }, {
    root: null,
    rootMargin: '-60px 0px -60% 0px',
    threshold: 0,
  });

  builders.forEach(function(b) { observer.observe(b); });

  // Smooth scroll on sidebar click
  items.forEach(function(item) {
    item.addEventListener('click', function(e) {
      e.preventDefault();
      var targetId = item.getAttribute('data-builder');
      var target = document.getElementById(targetId);
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
})();
