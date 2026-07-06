/**
 * SD-ON Tool — Клиентская часть (JavaScript)
 * Радио-плеер на HTML5 <audio>, управление станциями, настройки.
 */

(function () {
    'use strict';

    const API = {
        getStations: () => fetch('/api/stations').then(r => r.json()),
        addStation: (name, url) => fetch('/api/stations', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, url })
        }).then(r => r.json()),
        updateStation: (index, name, url) => fetch('/api/stations/' + index, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, url })
        }).then(r => r.json()),
        deleteStation: (index) => fetch('/api/stations/' + index, {
            method: 'DELETE'
        }).then(r => r.json()),
        getConfig: () => fetch('/api/config').then(r => r.json()),
        saveConfig: (data) => fetch('/api/config', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
    };

    // ─── Состояние ──────────────────────────────────

    let stations = [];
    let activeUrl = '';
    let isPlaying = false;

    // ─── DOM-элементы ───────────────────────────────

    const audio = document.getElementById('radio-audio');
    const statusEl = document.getElementById('player-status');
    const btnPlay = document.getElementById('btn-play');
    const btnPause = document.getElementById('btn-pause');
    const btnStop = document.getElementById('btn-stop');
    const volumeSlider = document.getElementById('volume-slider');
    const volumeValue = document.getElementById('volume-value');
    const stationsList = document.getElementById('stations-list');
    const btnAddStation = document.getElementById('btn-add-station');
    const modalOverlay = document.getElementById('modal-overlay');
    const modalTitle = document.getElementById('modal-title');
    const inputName = document.getElementById('input-name');
    const inputUrl = document.getElementById('input-url');
    const btnModalCancel = document.getElementById('btn-modal-cancel');
    const btnModalSave = document.getElementById('btn-modal-save');

    let modalMode = 'add';
    let modalEditIndex = -1;

    // ─── Навигация ──────────────────────────────────

    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const page = btn.dataset.page;
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.getElementById('page-' + page).classList.add('active');
        });
    });

    // ─── Аудио-плеер ────────────────────────────────

    function playStation(url, name) {
        activeUrl = url;
        audio.src = url;
        audio.load();
        audio.play().then(() => {
            isPlaying = true;
            setStatus('▶ ' + name);
            btnPlay.style.display = 'none';
            btnPause.style.display = '';
            renderStations();
        }).catch(err => {
            setStatus('⚠ Ошибка: ' + err.message);
        });
        API.saveConfig({ lastStation: url });
    }

    function pausePlayback() {
        audio.pause();
        isPlaying = false;
        btnPlay.style.display = '';
        btnPause.style.display = 'none';
        setStatus('⏸ ' + getStationName(activeUrl));
    }

    function resumePlayback() {
        if (audio.src) {
            audio.play().then(() => {
                isPlaying = true;
                btnPlay.style.display = 'none';
                btnPause.style.display = '';
                setStatus('▶ ' + getStationName(activeUrl));
            });
        }
    }

    function stopPlayback() {
        audio.pause();
        audio.src = '';
        audio.load();
        isPlaying = false;
        btnPlay.style.display = '';
        btnPause.style.display = 'none';
        setStatus('⏹ Остановлено');
    }

    function setStatus(text) {
        statusEl.textContent = text;
    }

    function getStationName(url) {
        const s = stations.find(st => st.url === url);
        return s ? s.name : '';
    }

    // Автопереподключение
    audio.addEventListener('error', () => {
        if (activeUrl && isPlaying) {
            setStatus('🔄 Переподключение: ' + getStationName(activeUrl));
            setTimeout(() => {
                if (activeUrl && isPlaying) {
                    audio.src = activeUrl;
                    audio.load();
                    audio.play().catch(() => {});
                }
            }, 3000);
        }
    });

    audio.addEventListener('stalled', () => {
        if (activeUrl && isPlaying) {
            setStatus('🔄 Буферизация: ' + getStationName(activeUrl));
        }
    });

    audio.addEventListener('playing', () => {
        if (activeUrl) {
            setStatus('▶ ' + getStationName(activeUrl));
        }
    });

    // Кнопки
    btnPlay.addEventListener('click', () => {
        if (audio.paused && audio.src && activeUrl) {
            resumePlayback();
        } else if (activeUrl) {
            playStation(activeUrl, getStationName(activeUrl));
        }
    });

    btnPause.addEventListener('click', pausePlayback);
    btnStop.addEventListener('click', stopPlayback);

    // Громкость
    volumeSlider.addEventListener('input', () => {
        const v = parseInt(volumeSlider.value);
        audio.volume = v / 100;
        volumeValue.textContent = v + '%';
    });

    volumeSlider.addEventListener('change', () => {
        API.saveConfig({ volume: parseInt(volumeSlider.value) });
    });

    // ─── Станции ────────────────────────────────────

    function renderStations() {
        stationsList.innerHTML = '';
        const defaults = stations.filter(s => !s.custom);
        const customs = stations.filter(s => s.custom);

        if (defaults.length) {
            const label = document.createElement('div');
            label.className = 'section-label';
            label.textContent = 'Встроенные станции';
            stationsList.appendChild(label);
            defaults.forEach(s => stationsList.appendChild(createStationCard(s, false, -1)));
        }

        if (customs.length) {
            const label = document.createElement('div');
            label.className = 'section-label';
            label.textContent = 'Мои станции';
            stationsList.appendChild(label);
            customs.forEach((s, i) => stationsList.appendChild(createStationCard(s, true, i)));
        }
    }

    function createStationCard(station, isCustom, customIndex) {
        const card = document.createElement('div');
        card.className = 'station-card' + (station.url === activeUrl ? ' active' : '');

        const info = document.createElement('div');
        info.className = 'station-info';
        info.innerHTML = '<div class="station-name">' + escapeHtml(station.name) + '</div>' +
                         '<div class="station-url">' + escapeHtml(station.url) + '</div>';
        info.addEventListener('click', () => playStation(station.url, station.name));
        card.appendChild(info);

        if (isCustom) {
            const actions = document.createElement('div');
            actions.className = 'station-actions';

            const editBtn = document.createElement('button');
            editBtn.className = 'station-btn edit';
            editBtn.textContent = '✎';
            editBtn.title = 'Редактировать';
            editBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                openEditModal(customIndex, station.name, station.url);
            });
            actions.appendChild(editBtn);

            const delBtn = document.createElement('button');
            delBtn.className = 'station-btn delete';
            delBtn.textContent = '✕';
            delBtn.title = 'Удалить';
            delBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                if (confirm('Удалить «' + station.name + '»?')) {
                    API.deleteStation(customIndex).then(loadStations);
                }
            });
            actions.appendChild(delBtn);

            card.appendChild(actions);
        }

        return card;
    }

    async function loadStations() {
        try {
            stations = await API.getStations();
            renderStations();
        } catch (e) {
            console.error('Ошибка загрузки станций:', e);
        }
    }

    // ─── Модалка ────────────────────────────────────

    function openAddModal() {
        modalMode = 'add';
        modalEditIndex = -1;
        modalTitle.textContent = 'Добавить станцию';
        inputName.value = '';
        inputUrl.value = '';
        modalOverlay.classList.remove('hidden');
        inputName.focus();
    }

    function openEditModal(index, name, url) {
        modalMode = 'edit';
        modalEditIndex = index;
        modalTitle.textContent = 'Редактировать станцию';
        inputName.value = name;
        inputUrl.value = url;
        modalOverlay.classList.remove('hidden');
        inputName.focus();
    }

    function closeModal() {
        modalOverlay.classList.add('hidden');
    }

    async function saveModal() {
        const name = inputName.value.trim();
        const url = inputUrl.value.trim();

        if (!name) { inputName.style.borderColor = '#e94560'; return; }
        inputName.style.borderColor = '';

        if (!url || (!url.startsWith('http://') && !url.startsWith('https://'))) {
            inputUrl.style.borderColor = '#e94560'; return;
        }
        inputUrl.style.borderColor = '';

        if (modalMode === 'add') {
            await API.addStation(name, url);
        } else {
            await API.updateStation(modalEditIndex, name, url);
        }

        closeModal();
        loadStations();
    }

    btnAddStation.addEventListener('click', openAddModal);
    btnModalCancel.addEventListener('click', closeModal);
    btnModalSave.addEventListener('click', saveModal);

    modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) closeModal();
    });

    // Enter в полях модалки
    inputUrl.addEventListener('keydown', (e) => { if (e.key === 'Enter') saveModal(); });
    inputName.addEventListener('keydown', (e) => { if (e.key === 'Enter') inputUrl.focus(); });

    // ─── Инициализация ──────────────────────────────

    async function init() {
        try {
            const config = await API.getConfig();
            volumeSlider.value = config.volume || 70;
            volumeValue.textContent = volumeSlider.value + '%';
            audio.volume = parseInt(volumeSlider.value) / 100;
            activeUrl = config.lastStation || '';
        } catch (e) {
            console.error('Ошибка загрузки конфигурации:', e);
        }
        await loadStations();
    }

    function escapeHtml(text) {
        const d = document.createElement('div');
        d.textContent = text;
        return d.innerHTML;
    }

    init();
})();
