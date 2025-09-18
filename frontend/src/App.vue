<template>
  <div id="app" class="app-container">
    <!-- Sidebar -->
    <Sidebar
      ref="sidebarRef"
      @open-auth-modal="openAuthModal"
      @logout="logout"
      @toggle-collapse="handleSidebarToggle"
    />

    <!-- Main Content Area -->
    <div class="main-content" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <main class="content-area">
        <router-view />
      </main>
    </div>

    <!-- Auth Modal -->
    <AuthModal
      v-model:visible="showAuthModal"
      @login-success="onLoginSuccess"
    />

    <!-- Toast Messages -->
    <Toast />

    <!-- Confirm Dialog -->
    <ConfirmDialog />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import Toast from 'primevue/toast';
import ConfirmDialog from 'primevue/confirmdialog';
import Sidebar from './components/Sidebar.vue';
import AuthModal from './components/AuthModal.vue';

const router = useRouter();
const toast = useToast();

// Refs
const sidebarRef = ref(null);
const showAuthModal = ref(false);
const sidebarCollapsed = ref(false);

// Methods
const openAuthModal = () => {
  showAuthModal.value = true;
};

const logout = () => {
  localStorage.removeItem('token');

  toast.add({
    severity: 'info',
    summary: '로그아웃',
    detail: '성공적으로 로그아웃되었습니다.',
    life: 3000
  });

  // Update sidebar auth status
  if (sidebarRef.value) {
    sidebarRef.value.checkAuthStatus();
  }

  router.push('/');
};

const onLoginSuccess = () => {
  // Update sidebar auth status
  if (sidebarRef.value) {
    sidebarRef.value.checkAuthStatus();
  }
};

const handleSidebarToggle = (collapsed) => {
  sidebarCollapsed.value = collapsed;
};
</script>

<style scoped>
/* App Container */
.app-container {
  min-height: 100vh;
  display: flex;
  background-color: #f8fafc;
}

/* Main Content Area */
.main-content {
  flex: 1;
  margin-left: 280px; /* Sidebar width */
  min-height: 100vh;
  transition: margin-left 0.3s ease;
}

.main-content.sidebar-collapsed {
  margin-left: 80px; /* Collapsed sidebar width */
}

.content-area {
  padding: 2rem;
  min-height: calc(100vh - 4rem);
}

/* Responsive */
@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
    width: 100%;
  }

  .content-area {
    padding: 1rem;
  }
}

/* Global styles reset */
:deep(body) {
  margin: 0;
  padding: 0;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

:deep(*) {
  box-sizing: border-box;
}

/* Override PrimeVue component styles for consistent theming */
:deep(.p-component) {
  font-family: inherit;
}
</style>
