// ============================================
// BOOT SCREEN — анимация загрузки системы
// ============================================
(function() {
    // Проверяем, был ли уже boot-screen на этой сессии
    if (sessionStorage.getItem('booted')) return;
    
    const bootHTML = `
        <div class="boot-screen" id="bootScreen">
            <div class="boot-logo glitch-text" data-text="PIXEL_OS">PIXEL_OS</div>
            <div class="boot-log">
                <div class="boot-log-line">[  <span class="ok">OK</span>  ] Initializing kernel...</div>
                <div class="boot-log-line">[  <span class="ok">OK</span>  ] Loading Erika Engine v3.1...</div>
                <div class="boot-log-line">[  <span class="ok">OK</span>  ] Mounting file systems...</div>
                <div class="boot-log-line">[  <span class="warn">??</span>  ] Establishing neural link...</div>
            </div>
            <div class="boot-progress-wrap">
                <div class="boot-progress-fill" id="bootProgress"></div>
            </div>
            <div class="boot-status" id="bootStatus">BOOTING...</div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('afterbegin', bootHTML);
    
    const bootScreen = document.getElementById('bootScreen');
    const bootProgress = document.getElementById('bootProgress');
    const bootStatus = document.getElementById('bootStatus');
    
    let progress = 0;
    const steps = [
        { p: 15, t: 'Loading drivers...' },
        { p: 35, t: 'Initializing GPU...' },
        { p: 55, t: 'Starting Erika daemon...' },
        { p: 75, t: 'Connecting to neural core...' },
        { p: 90, t: 'Almost ready...' },
        { p: 100, t: 'SYSTEM READY' }
    ];
    
    let stepIndex = 0;
    const interval = setInterval(() => {
        if (stepIndex < steps.length) {
            progress = steps[stepIndex].p;
            bootProgress.style.width = progress + '%';
            bootStatus.textContent = steps[stepIndex].t;
            stepIndex++;
        } else {
            clearInterval(interval);
            bootStatus.textContent = 'WELCOME, USER';
            setTimeout(() => {
                bootScreen.classList.add('fade-out');
                sessionStorage.setItem('booted', 'true');
                setTimeout(() => {
                    bootScreen.remove();
                }, 800);
            }, 600);
        }
    }, 400);
})();
