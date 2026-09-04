let selectedWork = null;
const searchInput = document.getElementById('work-search');
const categorySelect = document.getElementById('category');
const resultsBox = document.getElementById('work-results');
const workIdInput = document.getElementById('work_item_id');
const btnAdd = document.getElementById('btn-add');
const selectedBox = document.getElementById('selected-work');
const selectedLabel = document.getElementById('selected-label');
const selectedMeta = document.getElementById('selected-meta');

let debounceTimer = null;

function clearSelection() {
  selectedWork = null;
  workIdInput.value = '';
  selectedBox.classList.add('hidden');
  btnAdd.disabled = true;
}

function highlightMatch(text, query) {
  if (!query) return text;
  const tokens = query.trim().split(/\s+/).filter(Boolean);
  let result = text;
  for (const token of tokens) {
    const re = new RegExp(`(${token.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    result = result.replace(re, '<mark>$1</mark>');
  }
  return result;
}

function selectWork(item) {
  selectedWork = item;
  workIdInput.value = item.id;
  selectedLabel.textContent = `${item.code} — ${item.name}`;
  selectedMeta.textContent = `${item.price} ₽ / ${item.unit}`;
  selectedBox.classList.remove('hidden');
  resultsBox.classList.remove('visible');
  searchInput.value = item.name;
  btnAdd.disabled = false;
}

async function searchWorks() {
  const q = searchInput.value.trim();
  const category = categorySelect.value;

  if (selectedWork && q !== selectedWork.name) {
    clearSelection();
  }

  const params = new URLSearchParams();
  if (q) params.set('q', q);
  if (category) params.set('category', category);

  const res = await fetch('/api/works?' + params.toString());
  const items = await res.json();

  resultsBox.innerHTML = '';
  if (!items.length) {
    const empty = document.createElement('div');
    empty.className = 'work-item muted';
    empty.textContent = q ? 'Ничего не найдено. Попробуйте часть слова: «заяв», «обжим», «стояк»' : 'Нет работ в выбранной категории';
    resultsBox.appendChild(empty);
  } else {
    items.forEach((item) => {
      const div = document.createElement('div');
      div.className = 'work-item';
      div.innerHTML =
        `<span class="wi-code">${item.code}</span> ` +
        `${highlightMatch(item.name, q)}<br>` +
        `<small class="muted">${item.price} ₽ / ${item.unit} · ${item.category}</small>`;
      div.onclick = () => selectWork(item);
      resultsBox.appendChild(div);
    });
  }
  resultsBox.classList.add('visible');
}

searchInput.addEventListener('input', () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(searchWorks, 200);
});

categorySelect.addEventListener('change', () => {
  clearSelection();
  searchInput.value = '';
  searchWorks();
});

searchInput.addEventListener('focus', () => {
  searchWorks();
});

// Показать работы категории при загрузке страницы
if (categorySelect.value) {
  searchWorks();
}
