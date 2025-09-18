<template>
  <div id="app">
    <!-- 헤더 -->
    <header class="app-header">
      <div class="header-container">
        <!-- 로고/브랜드 -->
        <div class="brand">
          <router-link to="/" class="brand-link">
            <h2 class="brand-title-1">Q</h2>
            <h2 class="brand-title-2">raft</h2>
          </router-link>
        </div>

        <!-- 네비게이션 메뉴 -->
        <nav class="main-nav">
          <ul class="nav-menu">
            <li class="nav-item">
              <router-link to="/" class="nav-link">Home</router-link>
            </li>
            <li class="nav-item">
              <router-link to="/quiz" class="nav-link">Quiz</router-link>
            </li>
            <li class="nav-item">
              <router-link to="/results" class="nav-link">Results</router-link>
            </li>
            <li class="nav-item">
              <router-link to="/about" class="nav-link">About</router-link>
            </li>
          </ul>
        </nav>

        <!-- 사용자 메뉴 -->
        <div class="user-menu">
          <Button
            icon="pi pi-user"
            severity="secondary"
            text
            rounded
            class="user-button"
            @click="handleUserButtonClick"
          />

          <!-- 드롭다운 메뉴 (로그인된 경우에만 표시) -->
          <div v-if="showUserMenu && isLoggedIn" class="user-dropdown">
            <ul>
              <li><a href="#" @click="goToProfile">Profile</a></li>
              <li><a href="#" @click="logout">Logout</a></li>
            </ul>
          </div>
        </div>

        <!-- 모바일 햄버거 메뉴 -->
        <button class="mobile-menu-toggle" @click="toggleMobileMenu">
          <i class="pi pi-bars"></i>
        </button>
      </div>

      <!-- 모바일 메뉴 (숨겨짐/보임) -->
      <nav v-if="showMobileMenu" class="mobile-nav">
        <ul class="mobile-menu">
          <li><router-link to="/" @click="closeMobileMenu">Home</router-link></li>
          <li><router-link to="/quiz" @click="closeMobileMenu">Quiz</router-link></li>
          <li><router-link to="/results" @click="closeMobileMenu">Results</router-link></li>
          <li><router-link to="/about" @click="closeMobileMenu">About</router-link></li>
        </ul>
      </nav>
    </header>

    <!-- 메인 콘텐츠 -->
    <main class="app-main">
      <router-view />
    </main>

    <!-- 푸터 (옵션) -->
    <footer class="app-footer">
      <p>&copy; 2024 Quiz App. All rights reserved.</p>
    </footer>

    <!-- 인증 모달 -->
    <AuthModal
      v-model:visible="showAuthModal"
      @login-success="onLoginSuccess"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import Button from 'primevue/button';
import AuthModal from './components/AuthModal.vue';

// 반응형 데이터
const showUserMenu = ref(false);
const showMobileMenu = ref(false);
const showAuthModal = ref(false);
const isLoggedIn = ref(false);

// 로그인 상태 체크
const checkAuthStatus = () => {
  const token = localStorage.getItem('token');
  isLoggedIn.value = !!token;
};

// 컴포넌트가 마운트될 때 로그인 상태 체크
onMounted(() => {
  checkAuthStatus();
});

// 사용자 버튼 클릭 핸들러
const handleUserButtonClick = () => {
  if (isLoggedIn.value) {
    toggleUserMenu();
  } else {
    showAuthModal.value = true;
  }
};

// 메서드들
const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value;
};

const toggleMobileMenu = () => {
  showMobileMenu.value = !showMobileMenu.value;
};

const closeMobileMenu = () => {
  showMobileMenu.value = false;
};

const goToProfile = () => {
  console.log('Go to profile');
  showUserMenu.value = false;
};

const logout = () => {
  localStorage.removeItem('token');
  isLoggedIn.value = false;
  showUserMenu.value = false;
  console.log('Logged out');
};

const onLoginSuccess = () => {
  checkAuthStatus();
  showUserMenu.value = false;
};
</script>

<style scoped>
/* 전체 앱 레이아웃 */
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 헤더 스타일 */
.app-header {
background: linear-gradient(135deg, #CDFADB 0%, #F6FDC3 2%, #FFCF96 5%, #FF8080 10%, #FF8080 97%, #FFCF96 100%);
  /* background: linear-gradient(135deg, #CCE0AC 0%, #F0EAAC 2%, #F4DEB3 5%, #FF8A8A 10%, #FF8A8A 97%, #F4DEB3 100%); */
    /* background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); */
  /* background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);  */
  /* background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);  */
  /* background: linear-gradient(135deg, #2196f3 0%, #21cbf3 100%);  */
  /* background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);  */
  /* background: #2563eb; */
  color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  position: sticky;
  top: 0;
  z-index: 1000;
  font-family: 'Inter';
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 64px;
}

/* 브랜드/로고 */
.brand {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  line-height: 1;
}

.brand-link {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-decoration: none;
  cursor: pointer;
  user-select: none;
  transition: all 0.3s ease;
  padding: 0.2rem;
  border-radius: 0.375rem;
}

.brand-link:hover {
  background: rgba(255, 255, 255, 0.0);
}

.brand-title-1 {
  margin: 0;
  font-size: 2rem;
  font-weight: 600;
  color: #1E293B;
  font-family: 'YeogiOttaeJalnan';
}

.brand-title-2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #1E293B;
  font-family: 'YeogiOttaeJalnan';
}

/* 네비게이션 메뉴 */
.main-nav {
  flex: 1;
  display: flex;
  justify-content: center;
}

.nav-menu {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 2rem;
}

.nav-item {
  display: flex;
  align-items: center;
}

.nav-link {
  color: #B91C1C;
  text-decoration: none;
  padding: 1rem 1rem;
  border-radius: 0.375rem;
  transition: all 0.2s;
  font-weight: 500;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: #7F1D1D;
}

.nav-link.router-link-active {
  background-color: rgba(255, 255, 255, 0.2);
  color: #7F1D1D;
}

/* 사용자 메뉴 */
.user-menu {
  position: relative;
}

.user-button {
  color: white !important;
}

.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border-radius: 0.375rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 150px;
  margin-top: 0.5rem;
}

.user-dropdown ul {
  list-style: none;
  margin: 0;
  padding: 0.5rem 0;
}

.user-dropdown li {
  padding: 0;
}

.user-dropdown a {
  display: block;
  padding: 0.5rem 1rem;
  color: #374151;
  text-decoration: none;
  transition: background-color 0.2s;
}

.user-dropdown a:hover {
  background-color: #f3f4f6;
}

/* 모바일 메뉴 토글 */
.mobile-menu-toggle {
  display: none;
  background: none;
  border: none;
  color: white;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0.5rem;
}

/* 모바일 네비게이션 */
.mobile-nav {
  background: rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.mobile-menu {
  list-style: none;
  margin: 0;
  padding: 1rem 0;
  text-align: center;
}

.mobile-menu li {
  margin: 0;
}

.mobile-menu a {
  display: block;
  color: white;
  text-decoration: none;
  padding: 0.75rem 1rem;
  font-weight: 500;
  transition: background-color 0.2s;
}

.mobile-menu a:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

/* 메인 콘텐츠 */
.app-main {
  flex: 1;
  padding: 2rem 1rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

/* 푸터 */
.app-footer {
  background: #f8fafc;
  border-top: 1px solid #e5e7eb;
  padding: 1rem;
  text-align: center;
  color: #6b7280;
  margin-top: auto;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .main-nav {
    display: none;
  }
  
  .mobile-menu-toggle {
    display: block;
  }
  
  .header-container {
    padding: 0 1rem;
  }
  
  .nav-menu {
    gap: 1rem;
  }
  
  .app-main {
    padding: 1rem 0.5rem;
  }
}

@media (max-width: 480px) {
  .brand-title {
    font-size: 1.25rem;
  }
  
  .header-container {
    min-height: 56px;
  }
}

/* 다양한 색상 옵션들 */
/* 
.app-header { background: #3b82f6; } // 파란색
.app-header { background: #10b981; } // 초록색  
.app-header { background: #f59e0b; } // 주황색
.app-header { background: #ef4444; } // 빨간색
.app-header { background: #8b5cf6; } // 보라색
*/
</style>