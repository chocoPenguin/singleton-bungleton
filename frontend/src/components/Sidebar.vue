<template>
  <div class="sidebar" :class="{ 'collapsed': collapsed }">
    <!-- Brand Section -->
    <div class="brand-section">
      <router-link to="/" class="brand-link">
        <div class="brand-content">
          <h2 class="brand-title">Qraft!</h2>
        </div>
      </router-link>
    </div>

    <!-- Navigation Menu -->
    <nav class="sidebar-nav">
      <ul class="nav-menu">
        <!-- Questions Section -->
        <li class="nav-item">
          <div class="nav-section-title">Questions</div>
        </li>
        <li class="nav-item">
          <router-link to="/questions/create" class="nav-link nav-link-indent">
            <span class="nav-label">Create Questions</span>
          </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/questions/history" class="nav-link nav-link-indent">
            <span class="nav-label">Question History</span>
          </router-link>
        </li>

        <!-- Groups Section -->
        <li class="nav-item">
          <div class="nav-section-title">Groups</div>
        </li>
        <li class="nav-item">
          <router-link to="/groups" class="nav-link nav-link-indent">
            <span class="nav-label">Group Management</span>
          </router-link>
        </li>
      </ul>
    </nav>

    <!-- Profile Section (Bottom) -->
    <div class="profile-section">
      <div class="profile-content" @click="toggleProfileMenu">
        <Avatar
          :label="userInitial"
          class="profile-avatar"
          shape="circle"
          size="normal"
        />
        <div class="profile-info" v-if="!collapsed">
          <div class="profile-name">{{ userName }}</div>
          <div class="profile-status">{{ isLoggedIn ? 'Online' : 'Offline' }}</div>
        </div>
        <Button
          v-if="!collapsed"
          icon="pi pi-ellipsis-v"
          text
          class="profile-menu-button"
          @click.stop="toggleProfileMenu"
        />
      </div>

      <!-- Profile Dropdown -->
      <div v-if="showProfileMenu" class="profile-dropdown" @click="closeProfileMenu">
        <ul>
          <li v-if="!isLoggedIn">
            <a href="#" @click="openAuthModal">
              <i class="pi pi-sign-in"></i>
              Login
            </a>
          </li>
          <template v-else>
            <li>
              <a href="#" @click="goToProfile">
                <i class="pi pi-user"></i>
                Profile
              </a>
            </li>
            <li>
              <a href="#" @click="logout">
                <i class="pi pi-sign-out"></i>
                Logout
              </a>
            </li>
          </template>
        </ul>
      </div>
    </div>

    <!-- Collapse Button -->
    <Button
      :icon="collapsed ? 'pi pi-angle-right' : 'pi pi-angle-left'"
      class="collapse-button"
      text
      @click="toggleCollapse"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import Button from 'primevue/button';
import Avatar from 'primevue/avatar';
import { getCurrentUserFromToken } from '../utils/auth.js';

const router = useRouter();
const toast = useToast();

// Emits
const emit = defineEmits(['open-auth-modal', 'logout', 'toggle-collapse']);

// State
const collapsed = ref(false);
const showProfileMenu = ref(false);
const userName = ref('Guest');
const isLoggedIn = ref(false);

// Computed
const userInitial = computed(() => {
  return userName.value.charAt(0).toUpperCase();
});

// Methods
const toggleCollapse = () => {
  collapsed.value = !collapsed.value;
  emit('toggle-collapse', collapsed.value);
};

const toggleProfileMenu = () => {
  showProfileMenu.value = !showProfileMenu.value;
};

const closeProfileMenu = () => {
  showProfileMenu.value = false;
};

const openAuthModal = () => {
  emit('open-auth-modal');
  closeProfileMenu();
};

const goToProfile = () => {
  console.log('Go to profile');
  closeProfileMenu();
};

const logout = () => {
  emit('logout');
  closeProfileMenu();
};

const checkAuthStatus = () => {
  const token = localStorage.getItem('token');
  isLoggedIn.value = !!token;

  if (token) {
    const userInfo = getCurrentUserFromToken();
    if (userInfo) {
      const emailParts = userInfo.email.split('@');
      userName.value = emailParts[0];
    }
  } else {
    userName.value = 'Guest';
  }
};

// Initialize
onMounted(() => {
  checkAuthStatus();
});

// Expose methods for parent component
defineExpose({
  checkAuthStatus
});
</script>

<style scoped>
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  width: 230px;
  background: #ffffff;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  z-index: 1000;
}

.sidebar.collapsed {
  width: 80px;
}

/* Brand Section */
.brand-section {
  padding: 1.5rem 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.brand-link {
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  transition: none;
}

.brand-link:hover {
  background: none;
}

.brand-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  font-family: 'YeogiOttaeJalnan', sans-serif;
}

/* Navigation */
.sidebar-nav {
  flex: 1;
  padding: 1rem 0;
  overflow-y: auto;
}

.nav-menu {
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-item {
  margin: 0;
}

.nav-section-title {
  padding: 0.75rem 1rem 0.5rem 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: #475569;
  text-decoration: none;
  transition: all 0.2s;
  border-radius: 0;
}

.nav-link:hover {
  background-color: #f1f5f9;
  color: #0f172a;
}

.nav-link.router-link-active {
  background-color: color-mix(in srgb,var(--p-surface-50) calc(100%*var(--tw-bg-opacity, 1)),transparent);
  color: #475569;
  border-right: 3px solid #475569;
}

.nav-link-indent {
  padding-left: 2.5rem; /* 아이콘 + gap 만큼 들여쓰기 (1rem + 0.75rem + 0.75rem) */
}

.sidebar.collapsed .nav-link-indent {
  padding-left: 0.75rem; /* collapsed 상태에서는 일반 padding */
}

.nav-icon {
  font-size: 1rem;
  width: 1rem;
}

.nav-label {
  font-weight: 500;
}

/* Profile Section */
.profile-section {
  position: relative;
  padding: 1rem;
  border-top: 1px solid #e2e8f0;
}

.profile-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.profile-content:hover {
  background-color: #f1f5f9;
}

.profile-avatar {
  flex-shrink: 0;
}

.profile-info {
  flex: 1;
  min-width: 0;
}

.profile-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 0.875rem;
  line-height: 1.25;
}

.profile-status {
  font-size: 0.75rem;
  color: #64748b;
}

.profile-menu-button {
  flex-shrink: 0;
  width: 1.5rem;
  height: 1.5rem;
  padding: 0;
}

.profile-dropdown {
  position: absolute;
  bottom: 100%;
  left: 1rem;
  right: 1rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  margin-bottom: 0.5rem;
  z-index: 50;
}

.profile-dropdown ul {
  list-style: none;
  margin: 0;
  padding: 0.5rem 0;
}

.profile-dropdown li {
  margin: 0;
}

.profile-dropdown a {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  color: #374151;
  text-decoration: none;
  font-size: 0.875rem;
  transition: background-color 0.2s;
}

.profile-dropdown a:hover {
  background-color: #f3f4f6;
}

.profile-dropdown i {
  width: 1rem;
  font-size: 0.875rem;
}

/* Collapse Button */
.collapse-button {
  position: absolute;
  top: 50%;
  right: -1rem;
  transform: translateY(-50%);
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: white;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
}

.collapse-button:hover {
  background-color: #f8fafc;
  border-color: #cbd5e1;
}

/* Collapsed State */
.sidebar.collapsed .nav-label,
.sidebar.collapsed .nav-section-title,
.sidebar.collapsed .profile-info {
  display: none;
}

.sidebar.collapsed .brand-title {
  display: none;
}

.sidebar.collapsed .nav-link {
  justify-content: center;
  padding: 0.75rem;
}

.sidebar.collapsed .profile-content {
  justify-content: center;
}

.sidebar.collapsed .profile-menu-button {
  display: none;
}

/* Responsive */
@media (max-width: 768px) {
  .sidebar {
    width: 100%;
    transform: translateX(-100%);
  }

  .sidebar.mobile-open {
    transform: translateX(0);
  }
}
</style>