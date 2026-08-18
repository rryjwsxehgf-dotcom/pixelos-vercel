// ============================================
// GALLERY — Удаление изображений
// ============================================

/**
 * Отрисовывает галерею с кнопками удаления
 */
function renderGallery(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    let gallery = JSON.parse(localStorage.getItem('pixelGallery') || '[]');

    if (gallery.length === 0) {
        container.innerHTML = `
            <div style="display:flex;align-items:center;justify-content:center;height:100%;color:var(--text-dim);flex-direction:column;gap:8px">
                <span style="font-size:40px">🖼️</span>
                <span>GALLERY EMPTY</span>
                <span style="font-size:10px">Draw something and click SAVE</span>
            </div>`;
        return;
    }

    let html = '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(100px,1fr));gap:6px;padding:8px;flex:1;overflow:auto;align-content:start">';
    
    gallery.forEach((item, index) => {
        html += `
            <div class="gallery-card" id="gallery-item-${index}" style="position:relative;aspect-ratio:1;background:#000;border-radius:2px;overflow:hidden;cursor:pointer;border:1px solid var(--border-subtle);transition:all 0.2s">
                <img src="${item.data}" style="width:100%;height:100%;object-fit:contain" loading="lazy" onclick="viewFullscreen(${index})">
                <button class="gallery-delete-btn" onclick="deleteImage(${index}, event)" title="Delete">
                    ✕
                </button>
                <div style="position:absolute;bottom:0;left:0;right:0;background:rgba(0,0,0,0.8);color:var(--text-dim);font-size:8px;padding:2px 6px;text-align:center;font-family:var(--font-mono)">
                    ${item.time || 'unknown'}
                </div>
            </div>`;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

/**
 * Удаление изображения по индексу
 */
async function deleteImage(index, event) {
    // Останавливаем всплытие (чтобы не открылся полноэкранный просмотр)
    if (event) {
        event.stopPropagation();
        event.preventDefault();
    }

    // Запрашиваем подтверждение
    if (!confirm(`[!] Delete image #${index + 1}?\nThis action cannot be undone.`)) {
        return;
    }

    // Отправляем запрос на сервер (для логирования)
    try {
        const response = await fetch(`/api/gallery/delete/${index}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            // Удаляем из localStorage
            let gallery = JSON.parse(localStorage.getItem('pixelGallery') || '[]');
            if (index >= 0 && index < gallery.length) {
                gallery.splice(index, 1);
                localStorage.setItem('pixelGallery', JSON.stringify(gallery));
                
                // Анимируем удаление из DOM
                const itemEl = document.getElementById(`gallery-item-${index}`);
                if (itemEl) {
                    itemEl.style.transition = 'all 0.3s ease';
                    itemEl.style.opacity = '0';
                    itemEl.style.transform = 'scale(0.8)';
                    setTimeout(() => {
                        // Перерисовываем всю галерею
                        renderGallery('galleryBody');
                    }, 300);
                } else {
                    // Если элемент не найден — просто перерисовываем
                    renderGallery('galleryBody');
                }
                
                showToast(`🗑️ Image deleted`);
            }
        } else {
            showToast(`❌ ${data.message}`);
        }
    } catch (error) {
        // Если сервер недоступен — всё равно удаляем локально
        let gallery = JSON.parse(localStorage.getItem('pixelGallery') || '[]');
        if (index >= 0 && index < gallery.length) {
            gallery.splice(index, 1);
            localStorage.setItem('pixelGallery', JSON.stringify(gallery));
            renderGallery('galleryBody');
            showToast('🗑️ Deleted (offline)');
        }
    }
}

/**
 * Полноэкранный просмотр
 */
function viewFullscreen(index) {
    let gallery = JSON.parse(localStorage.getItem('pixelGallery') || '[]');
    if (!gallery[index]) return;
    
    const overlay = document.createElement('div');
    overlay.style.cssText = 'position:fixed;inset:0;z-index:99999;background:rgba(0,0,0,0.95);display:flex;align-items:center;justify-content:center;cursor:pointer;flex-direction:column;gap:12px';
    
    const img = document.createElement('img');
    img.src = gallery[index].data;
    img.style.cssText = 'max-width:95vw;max-height:85vh;object-fit:contain;border:1px solid var(--border-glow)';
    
    const info = document.createElement('div');
    info.textContent = `${gallery[index].time || ''} | ${index + 1}/${gallery.length}`;
    info.style.cssText = 'color:var(--text-dim);font-family:var(--font-mono);font-size:11px';
    
    overlay.appendChild(img);
    overlay.appendChild(info);
    overlay.addEventListener('click', () => overlay.remove());
    document.body.appendChild(overlay);
}

// Экспорт для глобального доступа
window.deleteImage = deleteImage;
window.viewFullscreen = viewFullscreen;
window.renderGallery = renderGallery;

console.log('[GALLERY] Module loaded — deleteImage(), viewFullscreen(), renderGallery()');
