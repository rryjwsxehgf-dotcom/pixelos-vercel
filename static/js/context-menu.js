// ============================================
// CYBERPUNK CONTEXT MENU
// ============================================
(function() {
    const menuHTML = `
        <div class="cyber-context-menu" id="cyberContextMenu" style="display:none">
            <div class="cyber-menu-item" data-action="refresh">
                <span class="cyber-menu-icon">🔄</span> Refresh
            </div>
            <div class="cyber-menu-item" data-action="logs">
                <span class="cyber-menu-icon">📋</span> System Log
            </div>
            <div class="cyber-menu-divider"></div>
            <div class="cyber-menu-item" data-action="clear-chat">
                <span class="cyber-menu-icon">🗑️</span> Clear Chat
            </div>
            <div class="cyber-menu-item" data-action="terminal">
                <span class="cyber-menu-icon">⬛</span> Terminal
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', menuHTML);
    
    const contextMenu = document.getElementById('cyberContextMenu');
    
    // Показываем меню при правом клике
    document.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        
        const x = e.clientX;
        const y = e.clientY;
        
        // Позиционируем меню
        contextMenu.style.display = 'block';
        contextMenu.style.left = Math.min(x, window.innerWidth - 220) + 'px';
        contextMenu.style.top = Math.min(y, window.innerHeight - 200) + 'px';
    });
    
    // Скрываем меню при клике вне его
    document.addEventListener('click', function(e) {
        if (!contextMenu.contains(e.target)) {
            contextMenu.style.display = 'none';
        }
    });
    
    // Обработчики пунктов меню
    contextMenu.addEventListener('click', function(e) {
        const item = e.target.closest('.cyber-menu-item');
        if (!item) return;
        
        const action = item.dataset.action;
        contextMenu.style.display = 'none';
        
        switch(action) {
            case 'refresh':
                window.location.reload();
                break;
            case 'logs':
                if (typeof openApp === 'function') {
                    openApp('admin');
                }
                break;
            case 'clear-chat':
                if (typeof clearChat === 'function') {
                    clearChat();
                } else {
                    // Очистка localStorage чата
                    localStorage.removeItem('erik_chat_history');
                    // Перезагрузка iframe с чатом
                    const chatFrame = document.querySelector('iframe[src*="erik"]');
                    if (chatFrame) chatFrame.src = chatFrame.src;
                }
                break;
            case 'terminal':
                if (typeof openApp === 'function') {
                    openApp('erik');
                }
                break;
        }
    });
})();
