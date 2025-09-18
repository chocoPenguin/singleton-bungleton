<template>
  <div class="quiz-list-container">
    <!-- 페이지 헤더 -->
    <div class="page-header mb-6">
      <div class="flex justify-content-between align-items-center">
        <div>
          <h1 class="page-title">퀴즈 목록</h1>
          <p class="page-subtitle">다양한 주제의 퀴즈를 선택해서 도전해보세요!</p>
        </div>
      </div>
    </div>

    <!-- 필터 및 검색 -->
    <div class="filter-section mb-4">
      <div class="grid align-items-center">
        <div class="col-12 lg:col-6">
          <div class="search-box">
            <IconField iconPosition="left">
              <InputIcon class="pi pi-search" />
              <InputText 
                v-model="searchQuery" 
                placeholder="퀴즈 검색..." 
                class="w-full"
              />
            </IconField>
          </div>
        </div>
      </div>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="loading" class="text-center p-6">
      <ProgressSpinner />
      <p class="mt-3">퀴즈를 불러오는 중...</p>
    </div>

    <!-- 퀴즈 카드 목록 -->
    <div v-else-if="filteredQuizzes.length > 0" class="quiz-grid">
      <div class="grid">
        <div 
          v-for="quiz in paginatedQuizzes" 
          :key="quiz.id"
          class="col-12 md:col-6 lg:col-4"
        >
          <Card class="quiz-card h-full" @click="startQuiz(quiz)">
            <template #header>
              <div class="quiz-image">
                <img 
                  :src="quiz.thumbnail || '/images/default-quiz.jpg'" 
                  :alt="quiz.title"
                  class="quiz-thumbnail"
                />
                <div class="quiz-overlay">
                  <div class="quiz-stats">
                    <Badge :value="quiz.questionCount" severity="info" class="mr-2">
                      <i class="pi pi-question-circle mr-1"></i>
                      {{ quiz.questionCount }}문제
                    </Badge>
                    <Badge :value="quiz.difficulty" :severity="getDifficultyColor(quiz.difficulty)">
                      {{ quiz.difficulty }}
                    </Badge>
                  </div>
                </div>
              </div>
            </template>

            <template #title>
              <div class="quiz-title">{{ quiz.title }}</div>
            </template>

            <template #subtitle>
              <div class="quiz-category">
                <i class="pi pi-tag mr-1"></i>
                {{ quiz.category }}
              </div>
            </template>

            <template #content>
              <div class="quiz-description">
                <p class="text-600 mb-3">{{ quiz.description }}</p>
                
                <div class="quiz-meta">
                  <div class="flex justify-content-between align-items-center mb-2">
                    <small class="text-500">
                      <i class="pi pi-clock mr-1"></i>
                      약 {{ quiz.estimatedTime }}분
                    </small>
                    <small class="text-500">
                      <i class="pi pi-users mr-1"></i>
                      {{ quiz.participantCount }}명 참여
                    </small>
                  </div>
                  
                  <div class="quiz-rating flex align-items-center">
                    <Rating 
                      :modelValue="quiz.rating" 
                      readonly 
                      :cancel="false"
                      class="rating-small"
                    />
                    <small class="text-500 ml-2">({{ quiz.rating.toFixed(1) }})</small>
                  </div>
                </div>
              </div>
            </template>

            <template #footer>
              <div class="quiz-actions flex gap-2">
                <Button 
                  label="시작하기" 
                  icon="pi pi-play" 
                  class="flex-1"
                  @click.stop="startQuiz(quiz)"
                />
                <Button 
                  icon="pi pi-heart" 
                  severity="secondary" 
                  outlined
                  :class="{ 'liked': quiz.isLiked }"
                  @click.stop="toggleLike(quiz)"
                />
                <Button 
                  icon="pi pi-share-alt" 
                  severity="secondary" 
                  outlined
                  @click.stop="shareQuiz(quiz)"
                />
              </div>
            </template>
          </Card>
        </div>
      </div>
    </div>

    <!-- 퀴즈가 없는 경우 -->
    <div v-else class="empty-state text-center p-6">
      <i class="pi pi-inbox text-6xl text-400 mb-4"></i>
      <h3 class="text-700 mb-2">퀴즈가 없습니다</h3>
      <p class="text-600 mb-4">검색 조건에 맞는 퀴즈를 찾을 수 없습니다.</p>
      <Button label="필터 초기화" outlined @click="clearFilters" />
    </div>

    <!-- 페이지네이션 -->
    <div v-if="filteredQuizzes.length > itemsPerPage" class="pagination-section mt-6">
      <Paginator 
        v-model:first="first"
        :rows="itemsPerPage"
        :totalRecords="filteredQuizzes.length"
        :rowsPerPageOptions="[6, 12, 24]"
        template="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import Card from 'primevue/card';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Dropdown from 'primevue/dropdown';
import Badge from 'primevue/badge';
import Rating from 'primevue/rating';
import ProgressSpinner from 'primevue/progressspinner';
import Paginator from 'primevue/paginator';
import IconField from 'primevue/iconfield';
import InputIcon from 'primevue/inputicon';

const router = useRouter();
const toast = useToast();

// 반응형 데이터
const quizzes = ref([]);
const loading = ref(false);
const searchQuery = ref('');
const selectedCategory = ref(null);
const selectedDifficulty = ref(null);
const first = ref(0);
const itemsPerPage = ref(6);

// 필터 옵션
const categories = ref([
  { label: '전체', value: null },
  { label: 'JavaScript', value: 'javascript' },
  { label: 'Vue.js', value: 'vue' },
  { label: 'React', value: 'react' },
  { label: 'CSS', value: 'css' },
  { label: '데이터베이스', value: 'database' },
  { label: '알고리즘', value: 'algorithm' },
  { label: '네트워크', value: 'network' }
]);

const difficulties = ref([
  { label: '전체', value: null },
  { label: '초급', value: '초급' },
  { label: '중급', value: '중급' },
  { label: '고급', value: '고급' }
]);

// 계산된 속성
const filteredQuizzes = computed(() => {
  let filtered = quizzes.value;
  
  // 검색어 필터
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(quiz => 
      quiz.title.toLowerCase().includes(query) ||
      quiz.description.toLowerCase().includes(query) ||
      quiz.category.toLowerCase().includes(query)
    );
  }
  
  // 카테고리 필터
  if (selectedCategory.value) {
    filtered = filtered.filter(quiz => quiz.category === selectedCategory.value);
  }
  
  // 난이도 필터
  if (selectedDifficulty.value) {
    filtered = filtered.filter(quiz => quiz.difficulty === selectedDifficulty.value);
  }
  
  return filtered;
});

const paginatedQuizzes = computed(() => {
  const start = first.value;
  const end = start + itemsPerPage.value;
  return filteredQuizzes.value.slice(start, end);
});

// 메서드들
const fetchQuizzes = async () => {
  loading.value = true;
  
  try {
    // 실제 API 호출
    // const response = await fetch('/api/quizzes');
    // const data = await response.json();
    // quizzes.value = data.quizzes || [];
    
    // 예제 데이터
    quizzes.value = [
      {
        id: 1,
        title: 'JavaScript 기초 마스터',
        description: 'JavaScript의 기본 문법부터 고급 개념까지 체계적으로 학습할 수 있는 종합 퀴즈입니다.',
        category: 'JavaScript',
        difficulty: '초급',
        questionCount: 20,
        estimatedTime: 15,
        participantCount: 1250,
        rating: 4.8,
        isLiked: false,
        thumbnail: null
      },
      {
        id: 2,
        title: 'Vue.js 컴포넌트 심화',
        description: 'Vue.js의 컴포넌트 시스템을 깊이 있게 다루는 중급자를 위한 퀴즈입니다.',
        category: 'Vue.js',
        difficulty: '중급',
        questionCount: 15,
        estimatedTime: 12,
        participantCount: 890,
        rating: 4.6,
        isLiked: true,
        thumbnail: null
      },
      {
        id: 3,
        title: 'React Hooks 완전 정복',
        description: 'React Hooks의 모든 것을 다루는 실전 중심의 퀴즈입니다.',
        category: 'React',
        difficulty: '중급',
        questionCount: 25,
        estimatedTime: 20,
        participantCount: 2100,
        rating: 4.9,
        isLiked: false,
        thumbnail: null
      },
      {
        id: 4,
        title: 'CSS 레이아웃 마스터',
        description: 'Flexbox, Grid 등 모던 CSS 레이아웃 기법을 마스터하는 퀴즈입니다.',
        category: 'CSS',
        difficulty: '초급',
        questionCount: 18,
        estimatedTime: 10,
        participantCount: 756,
        rating: 4.4,
        isLiked: false,
        thumbnail: null
      },
      {
        id: 5,
        title: '데이터베이스 설계 원리',
        description: '관계형 데이터베이스의 설계 원리와 정규화를 다루는 고급 퀴즈입니다.',
        category: '데이터베이스',
        difficulty: '고급',
        questionCount: 30,
        estimatedTime: 25,
        participantCount: 445,
        rating: 4.7,
        isLiked: true,
        thumbnail: null
      },
      {
        id: 6,
        title: '알고리즘 문제 해결',
        description: '코딩 테스트에 자주 출제되는 알고리즘 문제들을 다루는 퀴즈입니다.',
        category: '알고리즘',
        difficulty: '고급',
        questionCount: 22,
        estimatedTime: 30,
        participantCount: 1678,
        rating: 4.5,
        isLiked: false,
        thumbnail: null
      }
    ];
    
  } catch (error) {
    console.error('퀴즈 로딩 실패:', error);
    toast.add({
      severity: 'error',
      summary: '오류',
      detail: '퀴즈를 불러오는데 실패했습니다.',
      life: 3000
    });
  } finally {
    loading.value = false;
  }
};

const startQuiz = (quiz) => {
  router.push(`/quiz/${quiz.id}`);
};

const toggleLike = (quiz) => {
  quiz.isLiked = !quiz.isLiked;
  toast.add({
    severity: quiz.isLiked ? 'success' : 'info',
    summary: quiz.isLiked ? '좋아요!' : '좋아요 취소',
    detail: `"${quiz.title}"를 ${quiz.isLiked ? '좋아요 목록에 추가' : '좋아요 목록에서 제거'}했습니다.`,
    life: 2000
  });
};

const shareQuiz = (quiz) => {
  // 공유 기능 구현
  navigator.clipboard.writeText(`${window.location.origin}/quiz/${quiz.id}`);
  toast.add({
    severity: 'success',
    summary: '공유 링크 복사됨',
    detail: '퀴즈 링크가 클립보드에 복사되었습니다.',
    life: 2000
  });
};

const clearFilters = () => {
  searchQuery.value = '';
  selectedCategory.value = null;
  selectedDifficulty.value = null;
  first.value = 0;
};

const getDifficultyColor = (difficulty) => {
  const colors = {
    '초급': 'success',
    '중급': 'warning', 
    '고급': 'danger'
  };
  return colors[difficulty] || 'info';
};

// 컴포넌트 마운트 시 데이터 로딩
onMounted(() => {
  fetchQuizzes();
});
</script>

<style scoped>
.quiz-list-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.page-header {
  text-align: left;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 0.5rem;
}

.page-subtitle {
  font-size: 1.1rem;
  color: var(--text-color-secondary);
  margin: 0;
}

.filter-section {
  background: var(--surface-50);
  padding: 1.5rem;
  border-radius: var(--border-radius);
  border: 1px solid var(--surface-border);
}

.quiz-card {
  cursor: pointer;
  transition: all 0.3s ease;
  height: 100%;
  border: 1px solid var(--surface-border);
}

.quiz-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  border-color: var(--primary-color);
}

.quiz-image {
  position: relative;
  height: 200px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.quiz-thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.quiz-overlay {
  position: absolute;
  top: 0;
  right: 0;
  padding: 1rem;
}

.quiz-stats {
  display: flex;
  gap: 0.5rem;
}

.quiz-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 0.5rem;
  line-height: 1.4;
}

.quiz-category {
  display: flex;
  align-items: center;
  color: var(--primary-color);
  font-weight: 500;
  font-size: 0.9rem;
}

.quiz-description {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.quiz-meta {
  margin-top: auto;
}

.quiz-actions {
  margin-top: 1rem;
}

.quiz-actions .liked {
  color: var(--pink-500) !important;
  border-color: var(--pink-500) !important;
}

.rating-small {
  font-size: 0.8rem;
}

.rating-small :deep(.p-rating-icon) {
  font-size: 0.8rem;
}

.empty-state {
  background: var(--surface-50);
  border-radius: var(--border-radius);
  border: 1px solid var(--surface-border);
}

.pagination-section {
  display: flex;
  justify-content: center;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .quiz-list-container {
    padding: 1rem 0.5rem;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .filter-section {
    padding: 1rem;
  }
  
  .page-header .flex {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
}

@media (max-width: 480px) {
  .quiz-image {
    height: 150px;
  }
  
  .quiz-actions {
    flex-direction: column;
  }
  
  .quiz-actions .flex-1 {
    flex: unset;
  }
}
</style>