/**
 * Main JavaScript for PTIT Online Examination UI
 * Handles common functionality, mock data, and utilities
 */

// --- Utilities ---
const Utils = {
    // Show a toast message
    showToast: (message, type = 'info') => {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        const icon = type === 'success' ? 'check-circle' : (type === 'error' ? 'exclamation-circle' : 'info-circle');
        toast.innerHTML = `<i class="fas fa-${icon}"></i> <span>${message}</span>`;

        container.appendChild(toast);

        // Trigger animation
        setTimeout(() => toast.classList.add('show'), 10);

        // Auto remove
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    },

    // Check if user is logged in
    checkAuth: () => {
        const user = localStorage.getItem('ptit_user');
        return user ? JSON.parse(user) : null;
    },

    // Format time in seconds to MM:SS
    formatTime: (seconds) => {
        const m = Math.floor(seconds / 60).toString().padStart(2, '0');
        const s = (seconds % 60).toString().padStart(2, '0');
        return `${m}:${s}`;
    }
};

// --- Auth Module ---
// Xac thuc nguoi dung tu file data/users.json
const Auth = {
    // Doc danh sach nguoi dung tu file JSON vaf localStorage
    loadUsers: async () => {
        try {
            const response = await fetch('data/users.json');
            if (!response.ok) throw new Error('Khong the doc file du lieu nguoi dung');
            const data = await response.json();
            const localUsers = JSON.parse(localStorage.getItem('ptit_registered_users') || '[]');
            return [...data, ...localUsers];
        } catch (err) {
            console.error('Loi doc file users.json:', err);
            const localUsers = JSON.parse(localStorage.getItem('ptit_registered_users') || '[]');
            return localUsers;
        }
    },

    // Dang nhap sinh vien (role: student)
    loginStudent: async (username, password) => {
        const users = await Auth.loadUsers();
        const user = users.find(u =>
            u.username.toLowerCase() === username.trim().toLowerCase() &&
            u.password === password &&
            u.role === 'student'
        );
        return user || null;
    },

    // Dang nhap admin/giang vien (role: admin)
    loginAdmin: async (username, password) => {
        const users = await Auth.loadUsers();
        const user = users.find(u =>
            u.username.toLowerCase() === username.trim().toLowerCase() &&
            u.password === password &&
            u.role === 'admin'
        );
        return user || null;
    },

    // Luu thong tin phien dang nhap
    saveSession: (user) => {
        const sessionData = {
            id: user.id,
            name: user.name,
            role: user.role,
            email: user.email || '',
            class: user.class || ''
        };
        localStorage.setItem('ptit_user', JSON.stringify(sessionData));
    },

    // Dang xuat
    logout: () => {
        localStorage.removeItem('ptit_user');
        window.location.href = 'login.html';
    }
};

// --- Mock Data ---
const MockData = {
    exams: [
        { id: 1, title: 'Lập trình Web Cơ bản', type: 'practice', duration: 45, status: 'open', questions: 10, totalScore: 10 },
        { id: 2, title: 'Mạng Máy Tính - Giữa kỳ', type: 'midterm', duration: 60, status: 'upcoming', date: '2026-05-20 09:00', questions: 40, totalScore: 10 },
        { id: 3, title: 'Cơ sở dữ liệu - Cuối kỳ', type: 'final', duration: 90, status: 'open', questions: 60, totalScore: 10 },
        { id: 4, title: 'Trí tuệ nhân tạo', type: 'practice', duration: 30, status: 'open', questions: 20, totalScore: 10 },
        { id: 5, title: 'Cấu trúc dữ liệu và giải thuật', type: 'midterm', duration: 60, status: 'upcoming', date: '2026-05-25 14:00', questions: 50, totalScore: 10 },
        { id: 6, title: 'Kiến trúc máy tính', type: 'practice', duration: 45, status: 'open', questions: 30, totalScore: 10 },
        { id: 7, title: 'Hệ điều hành - Cuối kỳ', type: 'final', duration: 90, status: 'upcoming', date: '2026-06-10 08:30', questions: 60, totalScore: 10 },
        { id: 8, title: 'Công nghệ phần mềm', type: 'practice', duration: 20, status: 'open', questions: 15, totalScore: 10 },
        { id: 9, title: 'Mạng viễn thông', type: 'midterm', duration: 45, status: 'open', questions: 40, totalScore: 10 },
        { id: 10, title: 'An toàn thông tin', type: 'final', duration: 90, status: 'upcoming', date: '2026-06-15 13:30', questions: 70, totalScore: 10 }
    ],
    // Dummy questions for demo
    getQuestions: (examId) => {
        return [
            { id: 101, text: 'Trong CSS, thuoc tinh nao dung de doi mau chu?', options: ['text-color', 'color', 'font-color', 'text-style'], correct: 1 },
            { id: 102, text: 'The HTML nao dung de tao lien ket?', options: ['link', 'a', 'href', 'url'], correct: 1 },
            { id: 103, text: 'JavaScript la ngon ngu thuoc loai nao?', options: ['Compiled', 'Interpreted', 'Assembly', 'Machine Language'], correct: 1 },
        ];
    }
};

// Global Initialization
document.addEventListener('DOMContentLoaded', () => {
    // Inject FontAwesome if not present
    if (!document.querySelector('link[href*="font-awesome"]')) {
        const fa = document.createElement('link');
        fa.rel = 'stylesheet';
        fa.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css';
        document.head.appendChild(fa);
    }

    // Inject Google Fonts if not present
    if (!document.querySelector('link[href*="fonts.googleapis.com"]')) {
        const font = document.createElement('link');
        font.rel = 'stylesheet';
        font.href = 'https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;500;600;700&family=Libre+Baskerville:wght@400;700&display=swap';
        document.head.appendChild(font);
    }

    // Handle logout
    const logoutBtn = document.getElementById('btn-logout');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            Auth.logout();
        });
    }

    // Update user info in header if present
    const user = Utils.checkAuth();
    if (user && document.getElementById('user-name-display')) {
        document.getElementById('user-name-display').textContent = user.name;
        document.getElementById('user-avatar-initial').textContent = user.name.charAt(0).toUpperCase();
    }
});
