<template>
  <Dialog
    v-model:visible="isVisible"
    modal
    :closable="true"
    :draggable="false"
    class="auth-modal"
    style="width: 400px"
  >
    <template #header>
      <div class="auth-modal-header">
        <h3>{{ activeTab === 'login' ? '로그인' : '회원가입' }}</h3>
      </div>
    </template>

    <div class="auth-modal-content">
      <!-- 탭 버튼 -->
      <div class="tab-buttons">
        <Button
          :class="{ 'active': activeTab === 'login' }"
          @click="activeTab = 'login'"
          text
          class="tab-button"
        >
          로그인
        </Button>
        <Button
          :class="{ 'active': activeTab === 'register' }"
          @click="activeTab = 'register'"
          text
          class="tab-button"
        >
          회원가입
        </Button>
      </div>

      <!-- 로그인 폼 -->
      <form v-if="activeTab === 'login'" @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <label for="email">이메일</label>
          <InputText v-model="loginForm.email" id="email" type="email" required />
        </div>
        <div class="form-group">
          <label for="password">비밀번호</label>
          <Password v-model="loginForm.password" id="password" :feedback="false" toggleMask />
        </div>
        <Button type="submit" label="로그인" class="submit-button" :loading="isLoading" />
      </form>

      <!-- 회원가입 폼 -->
      <form v-if="activeTab === 'register'" @submit.prevent="handleRegister" class="auth-form">
        <div class="form-group">
          <label for="name">이름</label>
          <InputText v-model="registerForm.name" id="name" type="text" required />
        </div>
        <div class="form-group">
          <label for="registerEmail">이메일</label>
          <InputText v-model="registerForm.email" id="registerEmail" type="email" required />
        </div>
        <div class="form-group">
          <label for="registerPassword">비밀번호</label>
          <Password v-model="registerForm.password" id="registerPassword" :feedback="false" toggleMask />
        </div>
        <Button type="submit" label="회원가입" class="submit-button" :loading="isLoading" />
      </form>
    </div>
  </Dialog>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import Dialog from 'primevue/dialog';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import { useToast } from 'primevue/usetoast';
import { registerAuthor, loginAuthor } from '../api/auth.js';

const router = useRouter();
const toast = useToast();

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
});

// Emits
const emit = defineEmits(['update:visible', 'login-success']);

// Reactive data
const isVisible = ref(props.visible);
const activeTab = ref('login');
const isLoading = ref(false);

const loginForm = ref({
  email: '',
  password: ''
});

const registerForm = ref({
  name: '',
  email: '',
  password: ''
});

// Watch for prop changes
watch(() => props.visible, (newVal) => {
  isVisible.value = newVal;
});

// Watch for dialog visibility changes
watch(isVisible, (newVal) => {
  emit('update:visible', newVal);
  if (!newVal) {
    // Reset forms when closing
    loginForm.value = { email: '', password: '' };
    registerForm.value = { name: '', email: '', password: '' };
    activeTab.value = 'login';
  }
});

// Methods
const handleLogin = async () => {
  isLoading.value = true;
  try {
    const response = await loginAuthor({
      username: loginForm.value.email,
      password: loginForm.value.password,
    });

    localStorage.setItem("token", response.data.access_token);
    toast.add({
      severity: 'success',
      summary: '성공',
      detail: '로그인 성공!',
      life: 3000
    });

    emit('login-success');
    isVisible.value = false;

    // Navigate to quiz page after login
    router.push("/quiz");
  } catch (err) {
    console.error(err);
    toast.add({
      severity: 'error',
      summary: '로그인 실패',
      detail: err.response?.data?.detail || err.message,
      life: 5000
    });
  } finally {
    isLoading.value = false;
  }
};

const handleRegister = async () => {
  isLoading.value = true;
  try {
    const response = await registerAuthor({
      name: registerForm.value.name,
      email: registerForm.value.email,
      password: registerForm.value.password,
    });

    toast.add({
      severity: 'success',
      summary: '회원가입 성공',
      detail: '계정이 생성되었습니다!',
      life: 3000
    });

    // Close modal after successful registration
    setTimeout(() => {
      isVisible.value = false;
    }, 1500);
  } catch (err) {
    console.error(err);

    let errorMessage = '회원가입에 실패했습니다.';
    if (err.response?.data?.detail) {
      const detail = err.response.data.detail;
      if (detail.includes('Email already registered') || detail.includes('already registered')) {
        errorMessage = '이미 사용중인 이메일입니다.';
      } else {
        errorMessage = detail;
      }
    }

    toast.add({
      severity: 'error',
      summary: '회원가입 실패',
      detail: errorMessage,
      life: 5000
    });
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.auth-modal-header {
  text-align: center;
  width: 100%;
}

.auth-modal-header h3 {
  margin: 0;
  color: #374151;
}

.auth-modal-content {
  padding: 0;
}

.tab-buttons {
  display: flex;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 1.5rem;
}

.tab-button {
  flex: 1;
  padding: 0.75rem 1rem;
  border-radius: 0;
  color: #6b7280;
  font-weight: 500;
  transition: all 0.2s;
}

.tab-button.active {
  color: #2563eb;
  border-bottom: 2px solid #2563eb;
}

.tab-button:hover {
  color: #2563eb;
  background-color: #f8fafc;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

.submit-button {
  margin-top: 0.5rem;
  width: 100%;
}

/* PrimeVue 컴포넌트 스타일 조정 */
:deep(.p-inputtext) {
  width: 100%;
}

:deep(.p-password) {
  width: 100%;
}

:deep(.p-password-input) {
  width: 100%;
}

:deep(.p-dialog .p-dialog-header) {
  padding: 1rem 1.5rem 0.5rem 1.5rem;
}

:deep(.p-dialog .p-dialog-content) {
  padding: 0 1.5rem 1.5rem 1.5rem;
}
</style>