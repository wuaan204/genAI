/**
 * Fashion Finder - Frontend JavaScript
 * Sử dụng LeafletJS (miễn phí, không cần API key)
 */

// ===== Configuration =====
const CONFIG = {
    API_BASE_URL: 'http://localhost:8000',
    DEFAULT_LOCATION: { lat: 21.0285, lon: 105.8542 },
    MAP_ZOOM: 14
};

// ===== State Management =====
const state = {
    map: null,
    userMarker: null,
    shopMarkers: [],
    userLocation: null
};

// ===== DOM Elements =====
const elements = {
    map: document.getElementById('map'),
    chatHistory: document.getElementById('chat-history'),
    chatInput: document.getElementById('chat-input'),
    sendBtn: document.getElementById('send-btn'),
    locateBtn: document.getElementById('locate-btn'),
    searchShopsBtn: document.getElementById('search-shops-btn'),
    themeToggle: document.getElementById('theme-toggle'),
    locationStatus: document.getElementById('location-status'),
    shopsList: document.getElementById('shops-list'),
    shopsContainer: document.getElementById('shops-container')
};

// ===== Initialize Application =====
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initMap();
    setupEventListeners();
});

/**
 * Khởi tạo theme từ localStorage
 */
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    if (savedTheme === 'light') {
        document.body.classList.add('light-mode');
        elements.themeToggle.querySelector('.theme-icon').textContent = '☀️';
    }
}

/**
 * Toggle dark/light mode
 */
function toggleTheme() {
    const isLight = document.body.classList.toggle('light-mode');
    const themeIcon = elements.themeToggle.querySelector('.theme-icon');
    
    if (isLight) {
        themeIcon.textContent = '☀️';
        localStorage.setItem('theme', 'light');
    } else {
        themeIcon.textContent = '🌙';
        localStorage.setItem('theme', 'dark');
    }
}

/**
 * Khởi tạo bản đồ Leaflet
 */
function initMap() {
    state.map = L.map('map').setView(
        [CONFIG.DEFAULT_LOCATION.lat, CONFIG.DEFAULT_LOCATION.lon],
        CONFIG.MAP_ZOOM
    );

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap',
        maxZoom: 19
    }).addTo(state.map);
    
    requestUserLocation();
}

/**
 * Thiết lập event listeners
 */
function setupEventListeners() {
    elements.locateBtn.addEventListener('click', requestUserLocation);
    elements.sendBtn.addEventListener('click', sendMessage);
    elements.searchShopsBtn.addEventListener('click', searchNearbyShops);
    elements.themeToggle.addEventListener('click', toggleTheme);
    
    elements.chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    elements.chatInput.addEventListener('input', () => {
        elements.sendBtn.disabled = !elements.chatInput.value.trim() || !state.userLocation;
    });
}

/**
 * Yêu cầu quyền truy cập vị trí GPS
 */
function requestUserLocation() {
    if (!navigator.geolocation) {
        updateLocationStatus('Trình duyệt không hỗ trợ GPS', 'error');
        useDefaultLocation();
        return;
    }

    updateLocationStatus('Đang lấy vị trí...', 'loading');
    elements.locateBtn.disabled = true;

    navigator.geolocation.getCurrentPosition(
        (position) => {
            const { latitude, longitude } = position.coords;
            state.userLocation = { lat: latitude, lon: longitude };
            
            updateUserMarker(latitude, longitude);
            state.map.setView([latitude, longitude], CONFIG.MAP_ZOOM);
            
            updateLocationStatus(`Vị trí: ${latitude.toFixed(4)}, ${longitude.toFixed(4)}`, 'success');
            elements.sendBtn.disabled = !elements.chatInput.value.trim();
            elements.searchShopsBtn.disabled = false;
            elements.locateBtn.disabled = false;
            
            updateWelcomeMessage(true);
        },
        (error) => {
            console.error('Lỗi lấy vị trí:', error);
            handleLocationError(error);
            elements.locateBtn.disabled = false;
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }
    );
}

/**
 * Xử lý lỗi khi lấy vị trí
 */
function handleLocationError(error) {
    let message = '';
    switch (error.code) {
        case error.PERMISSION_DENIED:
            message = 'Bạn đã từ chối quyền truy cập vị trí';
            break;
        case error.POSITION_UNAVAILABLE:
            message = 'Không thể xác định vị trí';
            break;
        case error.TIMEOUT:
            message = 'Hết thời gian chờ lấy vị trí';
            break;
        default:
            message = 'Lỗi không xác định';
    }
    
    updateLocationStatus(message, 'error');
    useDefaultLocation();
}

/**
 * Sử dụng vị trí mặc định khi không lấy được GPS
 */
function useDefaultLocation() {
    state.userLocation = CONFIG.DEFAULT_LOCATION;
    updateUserMarker(CONFIG.DEFAULT_LOCATION.lat, CONFIG.DEFAULT_LOCATION.lon);
    state.map.setView([CONFIG.DEFAULT_LOCATION.lat, CONFIG.DEFAULT_LOCATION.lon], CONFIG.MAP_ZOOM);
    
    elements.sendBtn.disabled = !elements.chatInput.value.trim();
    elements.searchShopsBtn.disabled = false;
    
    updateWelcomeMessage(false);
}

/**
 * Cập nhật marker vị trí người dùng
 */
function updateUserMarker(lat, lon) {
    if (state.userMarker) {
        state.map.removeLayer(state.userMarker);
    }

    const userIcon = L.divIcon({
        html: `<div class="user-marker-icon"></div>`,
        className: 'user-marker',
        iconSize: [24, 24],
        iconAnchor: [12, 12]
    });

    state.userMarker = L.marker([lat, lon], { icon: userIcon })
        .addTo(state.map)
        .bindPopup('<strong>📍 Vị trí của bạn</strong>');
}

/**
 * Cập nhật trạng thái vị trí
 */
function updateLocationStatus(message, type = 'info') {
    elements.locationStatus.textContent = message;
    
    const colors = {
        success: '#10B981',
        error: '#EF4444',
        loading: '#F59E0B',
        info: '#94A3B8'
    };
    
    elements.locationStatus.style.color = colors[type] || colors.info;
}

/**
 * Cập nhật tin nhắn chào mừng
 */
function updateWelcomeMessage(hasLocation) {
    const welcomeMsg = elements.chatHistory.querySelector('.bot-message .message-content p');
    if (welcomeMsg) {
        if (hasLocation) {
            welcomeMsg.innerHTML = 'Xin chào! 👋 Tôi là trợ lý thời trang AI. Bạn có thể hỏi tôi về xu hướng, cách phối đồ, hoặc tìm cửa hàng gần đây!';
        } else {
            welcomeMsg.innerHTML = 'Xin chào! 👋 Đang sử dụng vị trí mặc định (Hà Nội). Bạn có thể hỏi tôi về thời trang hoặc tìm cửa hàng!';
        }
    }
}

/**
 * Gửi tin nhắn đến backend
 */
async function sendMessage() {
    const message = elements.chatInput.value.trim();
    
    if (!message || !state.userLocation) {
        return;
    }

    addUserMessage(message);
    elements.chatInput.value = '';
    elements.sendBtn.disabled = true;

    showTypingIndicator();

    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                lat: state.userLocation.lat,
                lon: state.userLocation.lon,
                message: message
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        hideTypingIndicator();
        addBotMessage(data.ai_message);

    } catch (error) {
        console.error('Lỗi gửi tin nhắn:', error);
        hideTypingIndicator();
        addBotMessage('Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu. Vui lòng thử lại sau.');
    }
}

/**
 * Tìm kiếm cửa hàng gần đây (nút riêng)
 */
async function searchNearbyShops() {
    if (!state.userLocation) {
        return;
    }

    elements.searchShopsBtn.disabled = true;
    elements.searchShopsBtn.innerHTML = '<span class="btn-icon">⏳</span> Đang tìm...';

    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                lat: state.userLocation.lat,
                lon: state.userLocation.lon,
                message: 'Tìm cửa hàng gần đây'
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        displayShopsOnMap(data.shops);
        displayShopsList(data.shops);
        
        updateLocationStatus(`Tìm thấy ${data.shops.length} cửa hàng`, 'success');

    } catch (error) {
        console.error('Lỗi tìm kiếm:', error);
        updateLocationStatus('Lỗi tìm kiếm cửa hàng', 'error');
    } finally {
        elements.searchShopsBtn.disabled = false;
        elements.searchShopsBtn.innerHTML = '<span class="btn-icon">🔍</span> Tìm cửa hàng';
    }
}

/**
 * Hiển thị các cửa hàng trên bản đồ
 */
function displayShopsOnMap(shops) {
    state.shopMarkers.forEach(marker => state.map.removeLayer(marker));
    state.shopMarkers = [];

    if (!shops || shops.length === 0) {
        return;
    }

    const bounds = [];
    
    if (state.userLocation) {
        bounds.push([state.userLocation.lat, state.userLocation.lon]);
    }

    shops.forEach((shop, index) => {
        const shopIcon = L.divIcon({
            html: `<div class="shop-marker-icon">${index + 1}</div>`,
            className: 'shop-marker',
            iconSize: [36, 36],
            iconAnchor: [18, 18]
        });

        const marker = L.marker([shop.lat, shop.lon], { icon: shopIcon })
            .addTo(state.map)
            .bindPopup(`
                <div class="map-popup">
                    <h4>🏪 ${shop.name}</h4>
                    <p>📍 ${shop.address}</p>
                    <p>📏 ${shop.distance_km} km</p>
                    <p>🏷️ ${shop.category}</p>
                    <p>💰 ${shop.price_range}</p>
                    ${shop.promo_text ? `<p class="promo">🎁 ${shop.promo_text}</p>` : ''}
                    <button onclick="openInGoogleMaps('${shop.name.replace(/'/g, "\\'")}', '${shop.address.replace(/'/g, "\\'")}')" class="popup-btn">
                        🗺️ Mở Google Maps
                    </button>
                </div>
            `);

        state.shopMarkers.push(marker);
        bounds.push([shop.lat, shop.lon]);
    });

    if (bounds.length > 1) {
        state.map.fitBounds(bounds, { padding: [50, 50] });
    }
}

/**
 * Hiển thị danh sách cửa hàng trong sidebar
 */
function displayShopsList(shops) {
    if (!shops || shops.length === 0) {
        elements.shopsList.classList.add('hidden');
        return;
    }

    elements.shopsContainer.innerHTML = '';
    
    shops.forEach((shop, index) => {
        const shopCard = document.createElement('div');
        shopCard.className = 'shop-card';
        shopCard.innerHTML = `
            <div class="shop-header">
                <div class="shop-name">
                    ${index + 1}. ${shop.name}
                    <span class="shop-distance">${shop.distance_km} km</span>
                </div>
                <button class="btn-open-maps" title="Mở trong Google Maps">
                    🗺️
                </button>
            </div>
            <div class="shop-info">
                📍 ${shop.address}<br>
                🏷️ ${shop.category} | 💰 ${shop.price_range}
            </div>
            ${shop.promo_text ? `<div class="shop-promo">🎁 ${shop.promo_text}</div>` : ''}
        `;

        const openMapsBtn = shopCard.querySelector('.btn-open-maps');
        openMapsBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            openInGoogleMaps(shop.name, shop.address);
        });

        shopCard.addEventListener('click', () => {
            state.map.setView([shop.lat, shop.lon], 17);
            state.shopMarkers[index]?.openPopup();
        });

        elements.shopsContainer.appendChild(shopCard);
    });

    elements.shopsList.classList.remove('hidden');
}

/**
 * Mở vị trí trong Google Maps (tab mới)
 */
function openInGoogleMaps(name, address) {
    const searchQuery = encodeURIComponent(`${name}, ${address}`);
    const url = `https://www.google.com/maps/search/?api=1&query=${searchQuery}`;
    window.open(url, '_blank');
}

/**
 * Thêm tin nhắn của người dùng
 */
function addUserMessage(message) {
    const messageEl = document.createElement('div');
    messageEl.className = 'chat-message user-message';
    messageEl.innerHTML = `
        <div class="message-avatar">👤</div>
        <div class="message-content">
            <p>${escapeHtml(message)}</p>
            <span class="message-time">${getCurrentTime()}</span>
        </div>
    `;
    
    elements.chatHistory.appendChild(messageEl);
    scrollToBottom();
}

/**
 * Thêm tin nhắn của bot
 */
function addBotMessage(message) {
    const messageEl = document.createElement('div');
    messageEl.className = 'chat-message bot-message';
    messageEl.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <p>${formatBotMessage(message)}</p>
            <span class="message-time">${getCurrentTime()}</span>
        </div>
    `;
    
    elements.chatHistory.appendChild(messageEl);
    scrollToBottom();
}

/**
 * Format tin nhắn bot
 */
function formatBotMessage(message) {
    return message
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>');
}

/**
 * Escape HTML
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Lấy thời gian hiện tại
 */
function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString('vi-VN', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

/**
 * Cuộn chat history xuống cuối
 */
function scrollToBottom() {
    elements.chatHistory.scrollTop = elements.chatHistory.scrollHeight;
}

/**
 * Hiển thị typing indicator trong chat
 */
function showTypingIndicator() {
    const typingEl = document.createElement('div');
    typingEl.id = 'typing-indicator';
    typingEl.className = 'chat-message bot-message';
    typingEl.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content typing-content">
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    elements.chatHistory.appendChild(typingEl);
    scrollToBottom();
}

/**
 * Ẩn typing indicator
 */
function hideTypingIndicator() {
    const typingEl = document.getElementById('typing-indicator');
    if (typingEl) {
        typingEl.remove();
    }
}
