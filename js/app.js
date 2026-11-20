/**
 * BBQ House - Frontend Application Controller
 * Single-link, synchronized interactive store & admin dashboard.
 */

const API_BASE = "";

// Global State
const State = {
    user: null,
    cart: [],
    categories: [],
    products: [],
    activeCategory: "all",
    searchQuery: "",
    activeView: "home",
    adminView: "orders",
    currentTrackOrderId: null
};

// Initialize App
document.addEventListener("DOMContentLoaded", () => {
    initAuth();
    initCart();
    loadCategories();
    loadProducts();
    checkHealth();
    setupEventListeners();
    handleUrlHash();
});

// =====================================================================
// UTILS & TOASTS
// =====================================================================

function showToast(message, type = "success") {
    let container = document.getElementById("toastContainer");
    if (!container) {
        container = document.createElement("div");
        container.id = "toastContainer";
        container.className = "toast-container";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    const icon = type === "success" ? "✅" : (type === "error" ? "❌" : "ℹ️");
    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => toast.classList.add("show"), 10);
    setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

function formatPrice(val) {
    return "₱" + Number(val || 0).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// =====================================================================
// SYSTEM HEALTH & DB STATUS
// =====================================================================

async function checkHealth() {
    try {
        const res = await fetch(`${API_BASE}/api/health`);
        const data = await res.json();
        const el = document.getElementById("dbStatusIndicator");
        if (el) {
            el.innerHTML = `<span>⚡ DB Mode: <strong>${data.database}</strong></span> <span>${data.supabase_configured ? "Supabase Configured" : "Local Mode"}</span>`;
        }
    } catch (e) {
        console.error("Health check error:", e);
    }
}

// =====================================================================
// AUTHENTICATION
// =====================================================================

function initAuth() {
    const saved = localStorage.getItem("bbq_user");
    if (saved) {
        try {
            State.user = JSON.parse(saved);
        } catch (e) {
            State.user = null;
        }
    }
    renderAuthUI();
}

function renderAuthUI() {
    const authContainer = document.getElementById("navAuthContainer");
    const adminLink = document.getElementById("adminNavLink");

    if (!authContainer) return;

    if (State.user) {
        authContainer.innerHTML = `
            <a href="#orders" onclick="switchView('orders')" class="nav-item">📋 My Orders</a>
            <span class="user-greeting" style="color: #ff8a00; font-weight:700;">👋 ${State.user.name.split(' ')[0]}</span>
            <button onclick="handleLogout()" class="login-btn" style="border:none; cursor:pointer;">Logout</button>
        `;
        if (adminLink) {
            adminLink.style.display = "inline-flex";
        }
    } else {
        authContainer.innerHTML = `
            <button onclick="openModal('authModal')" class="login-btn" style="border:none; cursor:pointer;">Login / Sign Up</button>
        `;
        if (adminLink) {
            // Keep admin link visible for demo testing convenience
            adminLink.style.display = "inline-flex";
        }
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById("loginEmail").value.trim();
    const password = document.getElementById("loginPassword").value;

    try {
        const res = await fetch(`${API_BASE}/api/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json();

        if (!res.ok) throw new Error(data.detail || "Login failed");

        State.user = data.user;
        localStorage.setItem("bbq_user", JSON.stringify(State.user));
        renderAuthUI();
        closeModal("authModal");
        showToast(`Welcome back, ${State.user.name}!`);

        if (State.user.role === "admin") {
            switchView("admin");
        }
    } catch (err) {
        showToast(err.message, "error");
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const name = document.getElementById("regName").value.trim();
    const email = document.getElementById("regEmail").value.trim();
    const phone = document.getElementById("regPhone").value.trim();
    const address = document.getElementById("regAddress").value.trim();
    const password = document.getElementById("regPassword").value;
    const role = document.getElementById("regRole").value;

    try {
        const res = await fetch(`${API_BASE}/api/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, email, phone, address, password, role })
        });
        const data = await res.json();

        if (!res.ok) throw new Error(data.detail || "Registration failed");

        State.user = data.user;
        localStorage.setItem("bbq_user", JSON.stringify(State.user));
        renderAuthUI();
        closeModal("authModal");
        showToast("Registration successful! Welcome to BBQ House.");

        if (State.user.role === "admin") {
            switchView("admin");
        }
    } catch (err) {
        showToast(err.message, "error");
    }
}

function handleLogout() {
    State.user = null;
    localStorage.removeItem("bbq_user");
    renderAuthUI();
    showToast("Logged out successfully.");
    switchView("home");
}

function quickFillLogin(role) {
    if (role === "admin") {
        document.getElementById("loginEmail").value = "admin@bbqhouse.com";
        document.getElementById("loginPassword").value = "admin123";
    } else {
        document.getElementById("loginEmail").value = "customer@bbqhouse.com";
        document.getElementById("loginPassword").value = "customer123";
    }
}

// =====================================================================
// DATA FETCHING & SYNCHRONIZATION
// =====================================================================

async function loadCategories() {
    try {
        const res = await fetch(`${API_BASE}/api/categories`);
        State.categories = await res.json();
        renderCategories();
    } catch (e) {
        console.error("Failed to load categories:", e);
    }
}

async function loadProducts() {
    try {
        const url = State.activeCategory !== "all" 
            ? `${API_BASE}/api/products?category_id=${State.activeCategory}` 
            : `${API_BASE}/api/products`;
        
        const res = await fetch(url);
        State.products = await res.json();
        renderProducts();
        renderFeatured();
    } catch (e) {
        console.error("Failed to load products:", e);
    }
}

function renderCategories() {
    // Render filter tabs on menu page
    const filterContainer = document.getElementById("categoryFilterTabs");
    if (filterContainer) {
        let html = `<button class="filter-tab ${State.activeCategory === 'all' ? 'active' : ''}" onclick="setCategory('all')">All BBQ Items</button>`;
        State.categories.forEach(cat => {
            html += `<button class="filter-tab ${State.activeCategory == cat.id ? 'active' : ''}" onclick="setCategory(${cat.id})">${cat.name}</button>`;
        });
        filterContainer.innerHTML = html;
    }

    // Also populate Admin Add/Edit Product category select
    const catSelect = document.getElementById("adminProductCategory");
    if (catSelect) {
        catSelect.innerHTML = State.categories.map(c => `<option value="${c.id}">${c.name}</option>`).join("");
    }
}

function setCategory(catId) {
    State.activeCategory = catId;
    renderCategories();
    loadProducts();
}

function handleSearch(query) {
    State.searchQuery = query.toLowerCase();
    renderProducts();
}

function renderFeatured() {
    const featuredContainer = document.getElementById("featuredContainer");
    if (!featuredContainer) return;

    const featured = State.products.slice(0, 3);
    featuredContainer.innerHTML = featured.map(p => `
        <div class="product-card">
            <div class="product-image">
                <img src="${p.image || 'images/products/pork-bbq.jpg'}" alt="${p.name}" onerror="this.src='images/products/pork-bbq.jpg'">
            </div>
            <div class="product-info">
                <h3>${p.name}</h3>
                <p>${p.description || ''}</p>
                <div class="product-bottom">
                    <span class="price">${formatPrice(p.price)}</span>
                    <button class="order-btn" onclick="addToCart(${p.id})">Order</button>
                </div>
            </div>
        </div>
    `).join("");
}

function renderProducts() {
    const container = document.getElementById("productsCatalogContainer");
    if (!container) return;

    let filtered = State.products;
    if (State.searchQuery) {
        filtered = filtered.filter(p => 
            p.name.toLowerCase().includes(State.searchQuery) || 
            (p.description && p.description.toLowerCase().includes(State.searchQuery))
        );
    }

    if (filtered.length === 0) {
        container.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 50px 20px;">
                <p style="font-size: 18px; color: #888;">No BBQ items found matching your selection.</p>
                <button onclick="setCategory('all')" class="btn-primary" style="margin-top: 15px; border:none; cursor:pointer;">Show All Items</button>
            </div>
        `;
        return;
    }

    container.innerHTML = filtered.map(p => `
        <div class="product-card">
            <div class="product-image">
                <img src="${p.image || 'images/products/pork-bbq.jpg'}" alt="${p.name}" onerror="this.src='images/products/pork-bbq.jpg'">
            </div>
            <div class="product-info">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 6px;">
                    <span style="font-size:12px; font-weight:800; color:#ff6b00; text-transform:uppercase;">${p.category_name || 'BBQ'}</span>
                    <span style="font-size:11px; font-weight:700; color:${p.stock > 0 ? '#10b981' : '#ef4444'};">${p.stock > 0 ? `Stock: ${p.stock}` : 'Out of Stock'}</span>
                </div>
                <h3>${p.name}</h3>
                <p>${p.description || ''}</p>
                <div class="product-bottom">
                    <span class="price">${formatPrice(p.price)}</span>
                    <div style="display:flex; gap:6px;">
                        <button class="order-btn" onclick="openProductQuickView(${p.id})" style="background:#444;">👁️</button>
                        <button class="order-btn" onclick="addToCart(${p.id})" ${p.stock <= 0 ? 'disabled style="opacity:0.5; cursor:not-allowed;"' : ''}>+ Add</button>
                    </div>
                </div>
            </div>
        </div>
    `).join("");
}

function openProductQuickView(id) {
    const p = State.products.find(x => x.id === id);
    if (!p) return;

    document.getElementById("quickViewImg").src = p.image || 'images/products/pork-bbq.jpg';
    document.getElementById("quickViewTitle").innerText = p.name;
    document.getElementById("quickViewCategory").innerText = p.category_name || 'BBQ Specialty';
    document.getElementById("quickViewPrice").innerText = formatPrice(p.price);
    document.getElementById("quickViewStock").innerText = `Available: ${p.stock} units`;
    document.getElementById("quickViewDesc").innerText = p.description || 'Delicious freshly grilled barbecue recipe.';
    document.getElementById("quickViewAddBtn").onclick = () => {
        addToCart(p.id);
        closeModal('productQuickViewModal');
    };

    openModal("productQuickViewModal");
}

// =====================================================================
// SHOPPING CART & CHECKOUT
// =====================================================================

function initCart() {
    const saved = localStorage.getItem("bbq_cart");
    if (saved) {
        try {
            State.cart = JSON.parse(saved);
        } catch (e) {
            State.cart = [];
        }
    }
    updateCartUI();
}

function saveCart() {
    localStorage.setItem("bbq_cart", JSON.stringify(State.cart));
    updateCartUI();
}

function addToCart(productId, qty = 1) {
    const product = State.products.find(p => p.id === productId);
    if (!product) return;

    if (product.stock <= 0) {
        showToast("Item is currently out of stock.", "error");
        return;
    }

    const existing = State.cart.find(item => item.id === productId);
    if (existing) {
        if (existing.quantity + qty > product.stock) {
            showToast(`Cannot add more than ${product.stock} items available in stock.`, "warning");
            return;
        }
        existing.quantity += qty;
    } else {
        State.cart.push({
            id: product.id,
            name: product.name,
            price: Number(product.price),
            image: product.image,
            quantity: qty
        });
    }

    saveCart();
    showToast(`Added "${product.name}" to your cart!`);
}

function updateCartQty(productId, delta) {
    const item = State.cart.find(i => i.id === productId);
    if (!item) return;

    const prod = State.products.find(p => p.id === productId);
    const maxStock = prod ? prod.stock : 999;

    const newQty = item.quantity + delta;
    if (newQty <= 0) {
        removeCartItem(productId);
        return;
    }
    if (newQty > maxStock) {
        showToast(`Maximum stock limit reached (${maxStock}).`, "warning");
        return;
    }

    item.quantity = newQty;
    saveCart();
}

function removeCartItem(productId) {
    State.cart = State.cart.filter(i => i.id !== productId);
    saveCart();
    showToast("Item removed from cart.", "info");
}

function clearCart() {
    State.cart = [];
    saveCart();
}

function updateCartUI() {
    const totalCount = State.cart.reduce((sum, item) => sum + item.quantity, 0);
    const badge = document.getElementById("cartCountBadge");
    if (badge) {
        badge.innerText = totalCount;
        badge.style.display = totalCount > 0 ? "inline-block" : "none";
    }

    renderCartDrawer();
}

function renderCartDrawer() {
    const container = document.getElementById("cartItemsContainer");
    const subtotalEl = document.getElementById("cartSubtotal");
    const totalEl = document.getElementById("cartTotal");
    const checkoutBtn = document.getElementById("cartCheckoutBtn");

    if (!container) return;

    if (State.cart.length === 0) {
        container.innerHTML = `
            <div style="text-align:center; padding: 60px 20px; color:#999;">
                <p style="font-size:42px; margin-bottom:10px;">🛒</p>
                <p style="font-weight:700; font-size:16px;">Your cart is empty</p>
                <p style="font-size:13px; margin-top:5px;">Check out our menu to add sizzling BBQ!</p>
            </div>
        `;
        if (subtotalEl) subtotalEl.innerText = formatPrice(0);
        if (totalEl) totalEl.innerText = formatPrice(0);
        if (checkoutBtn) checkoutBtn.disabled = true;
        return;
    }

    let subtotal = 0;
    container.innerHTML = State.cart.map(item => {
        const itemTotal = item.price * item.quantity;
        subtotal += itemTotal;
        return `
            <div class="cart-item">
                <img src="${item.image || 'images/products/pork-bbq.jpg'}" class="cart-item-img" onerror="this.src='images/products/pork-bbq.jpg'">
                <div class="cart-item-info">
                    <div class="cart-item-title">${item.name}</div>
                    <div class="cart-item-price">${formatPrice(item.price)}</div>
                    <div class="cart-qty-ctrl">
                        <button class="qty-btn" onclick="updateCartQty(${item.id}, -1)">-</button>
                        <span class="qty-val">${item.quantity}</span>
                        <button class="qty-btn" onclick="updateCartQty(${item.id}, 1)">+</button>
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-weight:800; font-size:14px; color:#222; margin-bottom:8px;">${formatPrice(itemTotal)}</div>
                    <button class="cart-remove-btn" onclick="removeCartItem(${item.id})">🗑️</button>
                </div>
            </div>
        `;
    }).join("");

    const deliveryFee = 49.00;
    const grandTotal = subtotal + deliveryFee;

    if (subtotalEl) subtotalEl.innerText = formatPrice(subtotal);
    if (totalEl) totalEl.innerText = formatPrice(grandTotal);
    if (checkoutBtn) checkoutBtn.disabled = false;
}

function openCartDrawer() {
    document.getElementById("cartDrawerOverlay").classList.add("active");
    document.getElementById("cartDrawer").classList.add("active");
}

function closeCartDrawer() {
    document.getElementById("cartDrawerOverlay").classList.remove("active");
    document.getElementById("cartDrawer").classList.remove("active");
}

function proceedToCheckout() {
    closeCartDrawer();
    if (State.cart.length === 0) {
        showToast("Your cart is empty!", "warning");
        return;
    }

    // Pre-populate user details if logged in
    if (State.user) {
        const nameField = document.getElementById("checkoutName");
        const emailField = document.getElementById("checkoutEmail");
        const phoneField = document.getElementById("checkoutPhone");
        const addrField = document.getElementById("checkoutAddress");

        if (nameField && State.user.name) nameField.value = State.user.name;
        if (emailField && State.user.email) emailField.value = State.user.email;
        if (phoneField && State.user.phone) phoneField.value = State.user.phone;
        if (addrField && State.user.address) addrField.value = State.user.address;
    }

    // Render checkout items breakdown
    const checkoutItemsContainer = document.getElementById("checkoutItemsSummary");
    const subtotal = State.cart.reduce((sum, it) => sum + (it.price * it.quantity), 0);
    const grandTotal = subtotal + 49.00;

    if (checkoutItemsContainer) {
        checkoutItemsContainer.innerHTML = State.cart.map(it => `
            <div style="display:flex; justify-content:space-between; margin-bottom:8px; font-size:14px;">
                <span>${it.name} <strong>x${it.quantity}</strong></span>
                <span>${formatPrice(it.price * it.quantity)}</span>
            </div>
        `).join("") + `
            <div style="border-top:1px dashed #ccc; padding-top:8px; margin-top:8px;">
                <div style="display:flex; justify-content:space-between; font-size:13px; color:#666;">
                    <span>Delivery Fee:</span>
                    <span>₱49.00</span>
                </div>
                <div style="display:flex; justify-content:space-between; font-size:16px; font-weight:800; color:#ff6b00; margin-top:5px;">
                    <span>Total Amount:</span>
                    <span>${formatPrice(grandTotal)}</span>
                </div>
            </div>
        `;
    }

    openModal("checkoutModal");
}

async function handlePlaceOrder(e) {
    e.preventDefault();
    if (State.cart.length === 0) return;

    const subtotal = State.cart.reduce((sum, it) => sum + (it.price * it.quantity), 0);
    const totalAmount = subtotal + 49.00;

    const orderPayload = {
        user_id: State.user ? State.user.id : null,
        customer_name: document.getElementById("checkoutName").value.trim(),
        customer_email: document.getElementById("checkoutEmail").value.trim(),
        customer_phone: document.getElementById("checkoutPhone").value.trim(),
        delivery_address: document.getElementById("checkoutAddress").value.trim(),
        order_notes: document.getElementById("checkoutNotes").value.trim(),
        total_amount: totalAmount,
        payment_method: document.getElementById("checkoutPaymentMethod").value,
        items: State.cart.map(i => ({
            product_id: i.id,
            product_name: i.name,
            quantity: i.quantity,
            price: i.price,
            subtotal: i.price * i.quantity
        }))
    };

    try {
        const res = await fetch(`${API_BASE}/api/orders`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(orderPayload)
        });
        const order = await res.json();

        if (!res.ok) throw new Error(order.detail || "Failed to place order.");

        clearCart();
        closeModal("checkoutModal");
        showToast("🎉 Order placed successfully! Tracking your delivery now.");

        // Reload products so local stock updates
        loadProducts();

        // Switch to order tracking view
        State.currentTrackOrderId = order.id;
        switchView("orders");
        loadOrderTracking(order.id);
    } catch (err) {
        showToast(err.message, "error");
    }
}

// =====================================================================
// ORDER TRACKING & "MY ORDERS"
// =====================================================================

async function loadOrderTracking(orderId) {
    try {
        const res = await fetch(`${API_BASE}/api/orders/${orderId}`);
        if (!res.ok) throw new Error("Order not found");
        const order = await res.json();
        renderOrderTracker(order);
    } catch (e) {
        console.error("Tracker error:", e);
    }
}

function renderOrderTracker(order) {
    const container = document.getElementById("activeOrderTracker");
    if (!container) return;

    const steps = [
        { key: "pending", label: "Placed", icon: "🕒" },
        { key: "confirmed", label: "Confirmed", icon: "✅" },
        { key: "preparing", label: "Grilling", icon: "🔥" },
        { key: "ready", label: "Ready", icon: "📦" },
        { key: "out_for_delivery", label: "Rider Out", icon: "🚴" },
        { key: "completed", label: "Delivered", icon: "🎉" }
    ];

    const currentIdx = steps.findIndex(s => s.key === order.order_status);

    container.innerHTML = `
        <div style="background:#fff; border-radius:14px; padding:25px; box-shadow:0 8px 30px rgba(0,0,0,0.06); border:1px solid #f0e6de; margin-bottom:30px;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; border-bottom:1px solid #f2ede8; padding-bottom:15px;">
                <div>
                    <h3 style="font-size:20px; font-weight:800; color:#222;">Order #${order.id}</h3>
                    <p style="font-size:13px; color:#888;">Placed on ${new Date(order.created_at).toLocaleString()}</p>
                </div>
                <div style="text-align:right;">
                    <span class="status-pill status-${order.order_status}">${order.order_status.replace(/_/g, ' ')}</span>
                    <p style="font-size:16px; font-weight:800; color:#ff6b00; margin-top:4px;">${formatPrice(order.total_amount)}</p>
                </div>
            </div>

            <!-- Visual Stepper -->
            <div class="order-stepper">
                ${steps.map((st, i) => {
                    const isCompleted = i < currentIdx;
                    const isActive = i === currentIdx;
                    const cls = isCompleted ? 'completed' : (isActive ? 'active' : '');
                    return `
                        <div class="step-item ${cls}">
                            <div class="step-circle">${st.icon}</div>
                            <div class="step-label">${st.label}</div>
                        </div>
                    `;
                }).join("")}
            </div>

            <!-- Items Details -->
            <div style="background:#faf7f5; border-radius:8px; padding:15px; margin-top:20px;">
                <h4 style="font-size:14px; font-weight:800; margin-bottom:10px;">Items Ordered:</h4>
                ${(order.items || []).map(it => `
                    <div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:6px;">
                        <span>${it.product_name} <strong>x${it.quantity}</strong></span>
                        <span>${formatPrice(it.subtotal)}</span>
                    </div>
                `).join("")}
                <div style="border-top:1px dashed #e0d4ca; padding-top:8px; margin-top:8px; font-size:13px; color:#555;">
                    <p>📍 Delivery to: <strong>${order.delivery_address}</strong></p>
                    <p>💳 Payment: <strong>${order.payment_method.replace(/_/g, ' ').toUpperCase()}</strong> (${order.payment_status.toUpperCase()})</p>
                </div>
            </div>
            
            <div style="text-align:right; margin-top:15px;">
                <button onclick="loadOrderTracking(${order.id})" class="btn-secondary" style="padding:6px 14px; font-size:13px;">🔄 Refresh Status</button>
            </div>
        </div>
    `;
}

async function loadAllOrders() {
    try {
        const url = State.user && State.user.role !== 'admin'
            ? `${API_BASE}/api/orders?user_id=${State.user.id}`
            : `${API_BASE}/api/orders`;

        const res = await fetch(url);
        const orders = await res.json();
        renderOrdersList(orders);
    } catch (e) {
        console.error("Failed to load orders list:", e);
    }
}

function renderOrdersList(orders) {
    const container = document.getElementById("ordersHistoryContainer");
    if (!container) return;

    if (orders.length === 0) {
        container.innerHTML = `<p style="text-align:center; color:#999; padding:30px;">No previous orders found.</p>`;
        return;
    }

    container.innerHTML = orders.map(ord => `
        <div style="background:#fff; border-radius:10px; padding:18px; margin-bottom:12px; border:1px solid #f0e6de; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div>
                <span style="font-weight:800; font-size:16px;">Order #${ord.id}</span>
                <span class="status-pill status-${ord.order_status}" style="margin-left:8px;">${ord.order_status.replace(/_/g, ' ')}</span>
                <p style="font-size:13px; color:#777; margin-top:4px;">${new Date(ord.created_at).toLocaleDateString()} • ${(ord.items || []).length} items</p>
            </div>
            <div style="text-align:right;">
                <div style="font-weight:800; font-size:16px; color:#ff6b00;">${formatPrice(ord.total_amount)}</div>
                <button onclick="loadOrderTracking(${ord.id})" class="btn-primary" style="padding:6px 12px; font-size:12px; margin-top:6px; border:none; cursor:pointer;">Track Live</button>
            </div>
        </div>
    `).join("");
}

// =====================================================================
// ADMIN DASHBOARD & LIVE MANAGEMENT
// =====================================================================

async function adminLoadDashboard() {
    await adminLoadStats();
    if (State.adminView === "orders") {
        await adminLoadOrders();
    } else if (State.adminView === "products") {
        await adminLoadProducts();
    } else if (State.adminView === "customers") {
        await adminLoadCustomers();
    }
}

async function adminLoadStats() {
    try {
        const res = await fetch(`${API_BASE}/api/stats`);
        const stats = await res.json();

        document.getElementById("kpiRevenue").innerText = formatPrice(stats.total_revenue);
        document.getElementById("kpiOrders").innerText = stats.total_orders;
        document.getElementById("kpiActive").innerText = stats.active_orders;
        document.getElementById("kpiProducts").innerText = stats.total_products;
        document.getElementById("kpiCustomers").innerText = stats.total_customers;
    } catch (e) {
        console.error("Stats error:", e);
    }
}

async function adminLoadOrders(statusFilter = "all") {
    try {
        const url = statusFilter !== "all" ? `${API_BASE}/api/orders?status=${statusFilter}` : `${API_BASE}/api/orders`;
        const res = await fetch(url);
        const orders = await res.json();

        const tbody = document.getElementById("adminOrdersTableBody");
        if (!tbody) return;

        if (orders.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:30px; color:#999;">No orders found.</td></tr>`;
            return;
        }

        tbody.innerHTML = orders.map(ord => `
            <tr>
                <td><strong>#${ord.id}</strong></td>
                <td>
                    <div style="font-weight:700;">${ord.customer_name}</div>
                    <div style="font-size:12px; color:#777;">${ord.customer_phone}</div>
                </td>
                <td>
                    <div style="font-size:13px; max-width:220px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                        ${(ord.items || []).map(i => `${i.product_name} (x${i.quantity})`).join(", ")}
                    </div>
                </td>
                <td><strong>${formatPrice(ord.total_amount)}</strong></td>
                <td>
                    <span class="status-pill status-${ord.order_status}">${ord.order_status.replace(/_/g, ' ')}</span>
                </td>
                <td>
                    <span style="font-size:12px; font-weight:700; color:${ord.payment_status === 'paid' ? '#10b981' : '#f59e0b'};">
                        ${ord.payment_status.toUpperCase()}
                    </span>
                </td>
                <td>
                    <select onchange="adminUpdateOrderStatus(${ord.id}, this.value)" style="padding:6px; border-radius:6px; border:1px solid #ccc; font-size:12px;">
                        <option value="pending" ${ord.order_status === 'pending' ? 'selected' : ''}>Pending</option>
                        <option value="confirmed" ${ord.order_status === 'confirmed' ? 'selected' : ''}>Confirmed</option>
                        <option value="preparing" ${ord.order_status === 'preparing' ? 'selected' : ''}>Preparing</option>
                        <option value="ready" ${ord.order_status === 'ready' ? 'selected' : ''}>Ready</option>
                        <option value="out_for_delivery" ${ord.order_status === 'out_for_delivery' ? 'selected' : ''}>Out for Delivery</option>
                        <option value="completed" ${ord.order_status === 'completed' ? 'selected' : ''}>Completed</option>
                        <option value="cancelled" ${ord.order_status === 'cancelled' ? 'selected' : ''}>Cancelled</option>
                    </select>
                </td>
            </tr>
        `).join("");
    } catch (e) {
        console.error("Admin orders error:", e);
    }
}

async function adminUpdateOrderStatus(orderId, newStatus) {
    try {
        const paymentStatus = newStatus === "completed" ? "paid" : undefined;
        const res = await fetch(`${API_BASE}/api/orders/${orderId}/status`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ order_status: newStatus, payment_status: paymentStatus })
        });
        if (!res.ok) throw new Error("Failed to update status");

        showToast(`Order #${orderId} updated to "${newStatus.replace(/_/g, ' ')}"!`);
        adminLoadStats();
        adminLoadOrders();

        // If tracking active order, update tracker view as well
        if (State.currentTrackOrderId === orderId) {
            loadOrderTracking(orderId);
        }
    } catch (err) {
        showToast(err.message, "error");
    }
}

async function adminLoadProducts() {
    try {
        const res = await fetch(`${API_BASE}/api/products`);
        const products = await res.json();

        const tbody = document.getElementById("adminProductsTableBody");
        if (!tbody) return;

        tbody.innerHTML = products.map(p => `
            <tr>
                <td><strong>#${p.id}</strong></td>
                <td>
                    <div style="display:flex; align-items:center; gap:10px;">
                        <img src="${p.image || 'images/products/pork-bbq.jpg'}" style="width:40px; height:40px; border-radius:6px; object-fit:cover;" onerror="this.src='images/products/pork-bbq.jpg'">
                        <div>
                            <div style="font-weight:700;">${p.name}</div>
                            <div style="font-size:12px; color:#777;">${p.category_name || 'BBQ'}</div>
                        </div>
                    </div>
                </td>
                <td><strong>${formatPrice(p.price)}</strong></td>
                <td>
                    <span style="font-weight:700; color:${p.stock > 10 ? '#10b981' : '#ef4444'};">${p.stock}</span>
                </td>
                <td>
                    <span class="status-pill status-${p.status === 'available' ? 'completed' : 'cancelled'}">${p.status}</span>
                </td>
                <td>
                    <button onclick="adminEditProduct(${p.id})" style="background:#f0f0f0; border:none; padding:6px 10px; border-radius:4px; cursor:pointer;">✏️ Edit</button>
                    <button onclick="adminDeleteProduct(${p.id})" style="background:#fee2e2; color:#ef4444; border:none; padding:6px 10px; border-radius:4px; cursor:pointer; margin-left:4px;">🗑️ Delete</button>
                </td>
            </tr>
        `).join("");
    } catch (e) {
        console.error("Admin products error:", e);
    }
}

async function adminLoadCustomers() {
    try {
        const res = await fetch(`${API_BASE}/api/customers`);
        const customers = await res.json();

        const tbody = document.getElementById("adminCustomersTableBody");
        if (!tbody) return;

        tbody.innerHTML = customers.map(c => `
            <tr>
                <td><strong>#${c.id}</strong></td>
                <td><strong>${c.name}</strong></td>
                <td>${c.email}</td>
                <td>${c.phone || 'N/A'}</td>
                <td><span class="status-pill status-${c.role === 'admin' ? 'confirmed' : 'completed'}">${c.role}</span></td>
                <td>${c.created_at ? new Date(c.created_at).toLocaleDateString() : 'Recent'}</td>
            </tr>
        `).join("");
    } catch (e) {
        console.error("Admin customers error:", e);
    }
}

function adminOpenAddProduct() {
    document.getElementById("adminProductModalTitle").innerText = "Add New BBQ Product";
    document.getElementById("adminProductId").value = "";
    document.getElementById("adminProductName").value = "";
    document.getElementById("adminProductPrice").value = "";
    document.getElementById("adminProductStock").value = "50";
    document.getElementById("adminProductDesc").value = "";
    document.getElementById("adminProductImage").value = "images/products/pork-bbq.jpg";
    document.getElementById("adminProductStatus").value = "available";
    openModal("adminProductModal");
}

function adminEditProduct(id) {
    const p = State.products.find(x => x.id === id);
    if (!p) return;

    document.getElementById("adminProductModalTitle").innerText = `Edit Product #${p.id}`;
    document.getElementById("adminProductId").value = p.id;
    document.getElementById("adminProductName").value = p.name;
    document.getElementById("adminProductCategory").value = p.category_id || "";
    document.getElementById("adminProductPrice").value = p.price;
    document.getElementById("adminProductStock").value = p.stock;
    document.getElementById("adminProductDesc").value = p.description || "";
    document.getElementById("adminProductImage").value = p.image || "images/products/pork-bbq.jpg";
    document.getElementById("adminProductStatus").value = p.status || "available";

    openModal("adminProductModal");
}

async function handleAdminSaveProduct(e) {
    e.preventDefault();
    const id = document.getElementById("adminProductId").value;
    const payload = {
        name: document.getElementById("adminProductName").value.trim(),
        category_id: parseInt(document.getElementById("adminProductCategory").value) || null,
        price: parseFloat(document.getElementById("adminProductPrice").value),
        stock: parseInt(document.getElementById("adminProductStock").value),
        description: document.getElementById("adminProductDesc").value.trim(),
        image: document.getElementById("adminProductImage").value.trim() || "images/products/pork-bbq.jpg",
        status: document.getElementById("adminProductStatus").value
    };

    try {
        let res;
        if (id) {
            res = await fetch(`${API_BASE}/api/products/${id}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
        } else {
            res = await fetch(`${API_BASE}/api/products`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
        }

        if (!res.ok) throw new Error("Failed to save product");

        closeModal("adminProductModal");
        showToast(id ? "Product updated successfully!" : "New BBQ product created!");
        loadProducts();
        adminLoadProducts();
        adminLoadStats();
    } catch (err) {
        showToast(err.message, "error");
    }
}

async function adminDeleteProduct(id) {
    if (!confirm("Are you sure you want to delete this product?")) return;
    try {
        const res = await fetch(`${API_BASE}/api/products/${id}`, { method: "DELETE" });
        if (!res.ok) throw new Error("Failed to delete product");
        showToast("Product deleted.");
        loadProducts();
        adminLoadProducts();
        adminLoadStats();
    } catch (err) {
        showToast(err.message, "error");
    }
}

function setAdminTab(tab) {
    State.adminView = tab;
    document.querySelectorAll(".admin-tab-btn").forEach(b => b.classList.remove("active"));
    const activeBtn = document.getElementById(`tabBtn_${tab}`);
    if (activeBtn) activeBtn.classList.add("active");

    document.getElementById("adminSection_orders").style.display = tab === "orders" ? "block" : "none";
    document.getElementById("adminSection_products").style.display = tab === "products" ? "block" : "none";
    document.getElementById("adminSection_customers").style.display = tab === "customers" ? "block" : "none";

    adminLoadDashboard();
}

// =====================================================================
// VIEW SWITCHING (SINGLE LINK ARCHITECTURE)
// =====================================================================

function switchView(viewName) {
    State.activeView = viewName;
    window.location.hash = viewName;

    // Sections
    const homeSection = document.getElementById("homeView");
    const menuSection = document.getElementById("menuView");
    const ordersSection = document.getElementById("ordersView");
    const adminSection = document.getElementById("adminView");

    if (homeSection) homeSection.style.display = viewName === "home" ? "block" : "none";
    if (menuSection) menuSection.style.display = viewName === "menu" ? "block" : "none";
    if (ordersSection) ordersSection.style.display = viewName === "orders" ? "block" : "none";
    if (adminSection) adminSection.style.display = viewName === "admin" ? "block" : "none";

    window.scrollTo({ top: 0, behavior: "smooth" });

    if (viewName === "menu") {
        renderProducts();
    } else if (viewName === "orders") {
        loadAllOrders();
        if (State.currentTrackOrderId) {
            loadOrderTracking(State.currentTrackOrderId);
        }
    } else if (viewName === "admin") {
        adminLoadDashboard();
    }
}

function handleUrlHash() {
    const hash = window.location.hash.replace("#", "");
    if (["home", "menu", "orders", "admin"].includes(hash)) {
        switchView(hash);
    } else {
        switchView("home");
    }
}

// =====================================================================
// MODAL CONTROLLER & EVENT LISTENERS
// =====================================================================

function openModal(id) {
    const el = document.getElementById(id);
    if (el) el.classList.add("active");
}

function closeModal(id) {
    const el = document.getElementById(id);
    if (el) el.classList.remove("active");
}

function setupEventListeners() {
    window.addEventListener("hashchange", handleUrlHash);

    // Close modals on clicking overlay background
    document.querySelectorAll(".modal-overlay").forEach(overlay => {
        overlay.addEventListener("click", (e) => {
            if (e.target === overlay) {
                overlay.classList.remove("active");
            }
        });
    });

    // Close cart drawer on backdrop click
    const cartOverlay = document.getElementById("cartDrawerOverlay");
    if (cartOverlay) {
        cartOverlay.addEventListener("click", closeCartDrawer);
    }
}
