// ===== Theme Toggle =====
const ThemeManager = {
  KEY: 'culinary_theme',
  init() {
    const saved = localStorage.getItem(this.KEY);
    if (saved === 'light') document.body.classList.add('light');
    document.getElementById('themeToggle').addEventListener('click', () => {
      document.body.classList.toggle('light');
      localStorage.setItem(this.KEY, document.body.classList.contains('light') ? 'light' : 'dark');
    });
  }
};

// ===== Bookmark Manager =====
const BookmarkManager = {
  KEY: 'culinary_bookmarks',

  getAll() {
    try { return JSON.parse(localStorage.getItem(this.KEY)) || []; }
    catch { return []; }
  },

  save(bookmarks) {
    try { localStorage.setItem(this.KEY, JSON.stringify(bookmarks)); }
    catch (e) { console.warn('localStorage write failed:', e); }
  },

  isBookmarked(url) {
    return this.getAll().some(b => b.url === url);
  },

  toggle(recipe) {
    const bookmarks = this.getAll();
    const index = bookmarks.findIndex(b => b.url === recipe.url);
    if (index === -1) {
      bookmarks.push({ ...recipe, saved_at: new Date().toISOString() });
      this.save(bookmarks);
      return true;
    } else {
      bookmarks.splice(index, 1);
      this.save(bookmarks);
      return false;
    }
  },

  count() { return this.getAll().length; }
};

// ===== Init Bookmarks =====
function initBookmarks() {
  document.querySelectorAll('.btn-bookmark').forEach(btn => {
    const card = btn.closest('.result-card');
    if (!card) return;
    const url = card.dataset.url;

    if (BookmarkManager.isBookmarked(url)) {
      btn.classList.add('active');
      btn.innerHTML = '&#9733;';
    }

    btn.addEventListener('click', () => {
      const recipe = {
        title: card.dataset.title,
        source: card.dataset.source,
        url: card.dataset.url,
        prep_time: card.dataset.prepTime || ''
      };
      const nowBookmarked = BookmarkManager.toggle(recipe);
      btn.classList.toggle('active', nowBookmarked);
      btn.innerHTML = nowBookmarked ? '&#9733;' : '&#9734;';
      updateBookmarkCount();
      // If bookmarks tab is visible, refresh it
      if (document.getElementById('bookmarks-list')) showBookmarks();
    });
  });
}

function updateBookmarkCount() {
  const els = document.querySelectorAll('#bookmark-count, #bm-count-inline');
  els.forEach(el => { if (el) el.textContent = BookmarkManager.count(); });
}

function showBookmarks() {
  const container = document.getElementById('bookmarks-list');
  if (!container) return;
  const bookmarks = BookmarkManager.getAll();

  if (bookmarks.length === 0) {
    container.innerHTML = '<p class="no-results">No bookmarks saved yet. Click &#9734; on a recipe to save it.</p>';
    return;
  }

  container.innerHTML = bookmarks.map(b => `
    <div class="result-card" data-url="${escHtml(b.url)}" data-title="${escHtml(b.title)}"
         data-source="${escHtml(b.source)}" data-prep-time="${escHtml(b.prep_time || '')}">
      <h3>${escHtml(b.title)}</h3>
      <p class="meta">${escHtml(b.source)}${b.prep_time ? ' &middot; ' + escHtml(b.prep_time) : ''}</p>
      <p class="url-preview">${escHtml(b.url)}</p>
      <div class="card-actions">
        <a href="${escHtml(b.url)}" target="_blank" rel="noopener" class="btn-open">Open Recipe</a>
        <button class="btn-bookmark active" type="button" onclick="removeBookmark('${escHtml(b.url)}')">&#9733; Remove</button>
      </div>
    </div>
  `).join('');
}

function removeBookmark(url) {
  const bookmarks = BookmarkManager.getAll().filter(b => b.url !== url);
  BookmarkManager.save(bookmarks);
  showBookmarks();
  updateBookmarkCount();
}

function escHtml(str) {
  const d = document.createElement('div');
  d.textContent = str;
  return d.innerHTML;
}

// ===== Speech Recognition =====
const SpeechManager = {
  recognition: null,
  init() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
      const btn = document.getElementById('micBtn');
      if (btn) {
        btn.title = 'Voice search not supported in this browser';
        btn.style.opacity = '0.4';
        btn.style.cursor = 'not-allowed';
        btn.onclick = () => alert('Voice search requires Chrome on Android. Please use Chrome to search by voice.');
      }
      return;
    }
    this.recognition = new SR();
    this.recognition.lang = 'en-US';
    this.recognition.interimResults = false;
    this.recognition.continuous = false;
    this.recognition.maxAlternatives = 1;

    this.recognition.onresult = (e) => {
      const text = e.results[0][0].transcript;
      const input = document.querySelector('.search-bar input[name="q"]');
      if (input) { input.value = text; input.form?.submit(); }
    };

    this.recognition.onend = () => {
      document.getElementById('micBtn')?.classList.remove('listening');
    };

    this.recognition.onerror = (e) => {
      document.getElementById('micBtn')?.classList.remove('listening');
      if (e.error === 'not-allowed') {
        alert('Microphone permission denied. Please allow microphone access in your browser settings.');
      } else if (e.error === 'no-speech') {
        // Silently retry - user didn't speak
      } else if (e.error === 'network') {
        alert('Voice search requires an internet connection.');
      }
    };

    document.getElementById('micBtn')?.addEventListener('click', () => {
      if (!this.recognition) return;
      try {
        this.recognition.start();
        document.getElementById('micBtn').classList.add('listening');
      } catch(e) {
        document.getElementById('micBtn')?.classList.remove('listening');
      }
    });
  }
};

// ===== Install Banner =====
function dismissInstall() {
  const dontShow = document.getElementById('dontShowAgain');
  if (dontShow && dontShow.checked) {
    localStorage.setItem('install_permanently_dismissed', '1');
  }
  document.getElementById('installBanner').style.display = 'none';
}

// ===== Init =====
document.addEventListener('DOMContentLoaded', () => {
  ThemeManager.init();
  SpeechManager.init();
  initBookmarks();
  updateBookmarkCount();
  const bmLabel = document.querySelector('label[for="tab-bookmarks"]');
  if (bmLabel) bmLabel.addEventListener('click', () => setTimeout(showBookmarks, 50));
  // Show install banner on mobile unless permanently dismissed
  if (!localStorage.getItem('install_permanently_dismissed') && /Android|iPhone|iPad|iPod/i.test(navigator.userAgent)) {
    document.getElementById('installBanner').style.display = 'block';
  }
  // Show back button on search/results pages
  const backBtn = document.getElementById('backBtn');
  if (backBtn && window.location.pathname !== '/') {
    backBtn.style.display = 'flex';
  }
});
