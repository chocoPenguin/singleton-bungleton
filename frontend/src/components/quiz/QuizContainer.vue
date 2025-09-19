<template>
  <div class="quiz-container">
    <!-- 로딩 상태 -->
    <div v-if="loading" class="text-center p-4">
      <ProgressSpinner />
      <p class="mt-3">Loading...</p>
    </div>

    <!-- 문제 표시 -->
    <div v-else-if="questions.length > 0" class="quiz-wrapper">
      <!-- 전체 진행률 표시 -->
      <div class="progress-section mb-4">
        <div class="flex justify-content-between align-items-center mb-2">
          <span class="text-sm text-500">{{ Object.keys(answers).length }} / {{ questions.length }}</span>
        </div>
        <ProgressBar :value="progressPercentage" class="mb-2" />
      </div>

      <!-- 현재 페이지의 모든 문제 렌더링 -->
      <div class="questions-list">
        <div
          v-for="(question, index) in currentPageQuestions"
          :key="question.id"
          class="question-item mb-4"
        >
          <!-- 문제 번호 표시 -->
          <div class="question-header mb-3 p-2 bg-primary-50 border-round" style="display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
              <Badge :value="(currentPage * questionsPerPage) + index + 1" severity="info" />
              <!-- result 모드일 때만 점수 아이콘 표시 -->
              <div v-if="props.mode === 'result' && question.user_score !== undefined" class="score-icon" style="display: flex; align-items: center;">
                <!-- 만점 -->
                <i v-if="question.user_score === question.max_score"
                   class="pi pi-check-circle" style="color: #22c55e; font-size: 1.125rem;"></i>
                <!-- 50% 미만 -->
                <i v-else-if="question.user_score < (question.max_score * 0.5)"
                   class="pi pi-times-circle" style="color: #ef4444; font-size: 1.125rem;"></i>
                <!-- 50% 이상 -->
                <i v-else
                   class="pi pi-exclamation-triangle" style="color: #eab308; font-size: 1.125rem;"></i>
              </div>
            </div>
          </div>

          <!-- 객관식 문제 -->
          <MultipleChoiceQuestion
            v-if="question.Type === 'M'"
            :key="`mc-${question.id}`"
            :question="question"
            :choices="question.choices"
            :mode="props.mode"
            @answer="handleAnswer"
            @next="() => {}"
          />

          <!-- 단답형 문제 -->
          <SubjectiveQuestion
            v-else-if="question.Type === 'S'"
            :key="`sub-${question.id}`"
            :question="question"
            :answer-type="'short'"
            :mode="props.mode"
            @answer="handleAnswer"
            @next="() => {}"
          />

          <!-- 서술형 문제 -->
          <SubjectiveQuestion
            v-else-if="question.Type === 'L'"
            :key="`sub-${question.id}`"
            :question="question"
            :answer-type="'long'"
            :mode="props.mode"
            @answer="handleAnswer"
            @next="() => {}"
          />

          <!-- 알 수 없는 타입 -->
          <Card v-else>
            <template #content>
              <p class="text-center text-500">알 수 없는 문제 타입: {{ question.Type }}</p>
            </template>
          </Card>
        </div>
      </div>

      <!-- 네비게이션 버튼 -->
      <div class="navigation-controls mt-4">

        <!-- 페이지 네비게이션 -->
        <div class="page-nav flex justify-content-between align-items-center p-3 bg-gray-50 border-round">
          <Button
            label="Prev Page"
            severity="secondary"
            :disabled="currentPage === 0"
            @click="goToPreviousPage"
          />

          <div class="flex align-items-center gap-3">
            <div class="text-center">
              <div class="font-bold">{{ currentPage + 1 }} / {{ totalPages }}</div>
            </div>
          </div>

          <div class="flex gap-2">
            <Button
              v-if="currentPage < totalPages - 1"
              label="Next Page"
              severity="primary"
              @click="goToNextPage"
            />
            <Button
              v-if="currentPage === totalPages - 1"
              label="Finish"
              severity="success"
              @click="completeQuiz"
              :disabled="!allQuestionsAnswered"
            />
          </div>
        </div>
      </div>

      <!-- 총 점수 표시 (result 모드에서만) -->
      <div v-if="props.mode === 'result'" class="total-score-section mt-4 p-4" style="background-color: #f9fafb; border: 2px solid #e5e7eb; border-radius: 12px; text-align: center;">
        <h3 style="color: #1f2937; font-weight: 700; margin-bottom: 0.5rem; font-size: 1.5rem;">총 점수</h3>
        <div style="font-size: 2rem; font-weight: 800; color: #059669; margin-bottom: 0.5rem;">
          {{ totalUserScore }} / {{ totalMaxScore }}
        </div>
      </div>
    </div>

    <!-- 문제가 없는 경우 -->
    <div v-else class="text-center p-4">
      <i class="pi pi-exclamation-triangle text-4xl text-orange-500 mb-3"></i>
      <p>표시할 문제가 없습니다.</p>
      <Button label="다시 시도" @click="fetchQuestions" />
    </div>

    <!-- 퀴즈 완료 -->
    <div v-if="props.mode === 'quiz' && isCompleted" class="completion-screen text-center p-4">
      <i class="pi pi-check-circle text-6xl text-green-500 mb-4"></i>
      <h2>Completed!</h2>
      <p class="mb-4">모든 문제를 완료했습니다.</p>
      <Button
        :label="isSubmitting ? 'AI가 피드백을 생성하고 있습니다...' : '결과 보기'"
        :loading="isSubmitting"
        :disabled="isSubmitting"
        @click="showResults"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useRoute, useRouter } from 'vue-router';
import axios from '@/utils/axiosConfig';
import Card from 'primevue/card';
import Button from 'primevue/button';
import ProgressBar from 'primevue/progressbar';
import ProgressSpinner from 'primevue/progressspinner';
import Badge from 'primevue/badge';
import MultipleChoiceQuestion from './MultipleChoiceQuestion.vue';
import SubjectiveQuestion from './SubjectiveQuestion.vue';

const toast = useToast();
const route = useRoute();
const router = useRouter();

// Props 정의
const props = defineProps({
  mode: {
    type: String,
    default: 'quiz',
    validator: (value) => ['quiz', 'result'].includes(value)
  }
});

// 반응형 데이터
const questions = ref([]);
const currentQuestionIndex = ref(0);
const currentPage = ref(0); // 현재 페이지 (0부터 시작)
const questionsPerPage = ref(10); // 페이지당 문제 수
const answers = ref({});
const loading = ref(false);
const isCompleted = ref(false);
const isSubmitting = ref(false);

// 계산된 속성
const totalPages = computed(() => {
  return Math.ceil(questions.value.length / questionsPerPage.value);
});

const currentPageQuestions = computed(() => {
  const start = currentPage.value * questionsPerPage.value;
  const end = start + questionsPerPage.value;
  return questions.value.slice(start, end);
});

const currentQuestion = computed(() => {
  return currentPageQuestions.value[currentQuestionIndex.value] || {};
});

const progressPercentage = computed(() => {
  const totalAnswered = Object.keys(answers.value).length;
  return questions.value.length > 0
    ? Math.round((totalAnswered / questions.value.length) * 100)
    : 0;
});

const currentPageProgress = computed(() => {
  const answeredCount = currentPageQuestions.value.filter(q => answers.value[q.id]).length;
  return currentPageQuestions.value.length > 0
    ? Math.round((answeredCount / currentPageQuestions.value.length) * 100)
    : 0;
});

const allQuestionsAnswered = computed(() => {
  return questions.value.every(q => answers.value[q.id] !== undefined);
});

const currentPageAnswered = computed(() => {
  return currentPageQuestions.value.every(q => answers.value[q.id] !== undefined);
});

// result 모드에서 총 점수 계산
const totalUserScore = computed(() => {
  if (props.mode !== 'result') return 0;
  return questions.value.reduce((total, question) => {
    return total + (question.user_score || 0);
  }, 0);
});

const totalMaxScore = computed(() => {
  return questions.value.reduce((total, question) => {
    return total + (question.max_score || 0);
  }, 0);
});

// API 호출 함수
const fetchQuestions = async () => {
  loading.value = true;

  try {
    const userId = route.query.user_id;
    const questionSetId = route.query.question_set_id;

    const params = new URLSearchParams();
    if (userId) params.append('user_id', userId);
    if (questionSetId) params.append('question_set_id', questionSetId);

    // mode에 따라 다른 API 엔드포인트 호출
    const endpoint = props.mode === 'result' ? '/question_assignments/quiz/result' : '/question_assignments/quiz/list';
    const response = await axios.get(endpoint, {
      params: Object.fromEntries(params)
    });
    const data = response.data;

    // 백엔드 데이터를 프론트엔드 형식에 맞게 변환
    questions.value = data.map(q => ({
      id: q.id,
      Type: q.type, // 백엔드 'type' -> 프론트엔드 'Type'
      question: q.question,
      choices: q.choices,
      max_score: q.max_score,
      // result 모드일 때만 assignment 데이터 포함
      ...(props.mode === 'result' && {
        user_answer: q.user_answer,
        user_score: q.user_score,
        feedback: q.feedback,
        status: q.status
      })
    }));

  } catch (error) {
    console.error('문제 로딩 실패:', error);

    // 에러 발생 시에도 예제 데이터 표시
    questions.value = [
      {
        id: 1,
        Type: 'M',
        question: 'JavaScript에서 변수를 선언하는 키워드가 아닌 것은?',
        choices: [
          { value: 'A', label: 'var' },
          { value: 'B', label: 'let' },
          { value: 'C', label: 'const' },
          { value: 'D', label: 'define' }
        ]
      }
    ];

    toast.add({
      severity: 'warn',
      summary: '알림',
      detail: '예제 데이터를 표시합니다.',
      life: 3000
    });
  } finally {
    loading.value = false;
  }
};

// 이벤트 핸들러들
const handleAnswer = (data) => {
  const question = questions.value.find(q => q.id === data.questionId);
  answers.value[data.questionId] = {
    user_answer: data.answer,
    question: question?.question,
    max_score: question?.max_score
  };
};

// 페이지 네비게이션
const goToNextPage = () => {
  if (currentPage.value < totalPages.value - 1) {
    currentPage.value++;
  }
};

const goToPreviousPage = () => {
  if (currentPage.value > 0) {
    currentPage.value--;
  }
};

const completeQuiz = () => {
  isCompleted.value = true;

  // 서버에 답변 제출
  submitAnswers();

  toast.add({
    severity: 'success',
    summary: '완료',
    detail: '퀴즈가 완료되었습니다!',
    life: 3000
  });
};

const submitAnswers = async () => {
  try {
    isSubmitting.value = true;
    const response = await axios.post('/question_assignments/quiz/submit', {
      answers: answers.value
    });

  } catch (error) {
    console.error('Errors!', error);
  } finally {
    isSubmitting.value = false;
  }
};

const showResults = () => {
  const userId = route.query.user_id;
  const questionSetId = route.query.question_set_id;

  router.push({
    path: '/quiz/result',
    query: {
      user_id: userId,
      question_set_id: questionSetId
    }
  });
};

// 컴포넌트 마운트 시 데이터 로딩
onMounted(() => {
  fetchQuestions();
});
</script>

<style scoped>
.quiz-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 1rem;
}

.progress-section {
  background: var(--surface-50);
  padding: 1rem;
  border-radius: var(--border-radius);
  border: 1px solid var(--surface-border);
}

.navigation-controls {
  background: var(--surface-50);
  padding: 1rem;
  border-radius: var(--border-radius);
  border: 1px solid var(--surface-border);
}

.completion-screen {
  background: var(--surface-50);
  border-radius: var(--border-radius);
  border: 1px solid var(--surface-border);
}

.question-item {
  border: 1px solid var(--surface-border);
  border-radius: var(--border-radius);
  padding: 1rem;
  background: var(--surface-0);
  transition: box-shadow 0.2s;
}

.question-item:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.question-header {
  background: var(--primary-50) !important;
  border: 1px solid var(--primary-100);
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .quiz-container {
    padding: 0.5rem;
  }

  .navigation-controls {
    flex-direction: column;
    gap: 0.5rem;
  }
}

.page-nav{
  justify-content: center; /* 가로축 가운데 정렬 */
  align-items: center;     /* 세로축 가운데 정렬 */

  height: 10vh;           /* 세로 가운데 맞추려면 높이 필요 */
  display: flex;
  gap: 0.5rem;
}
</style>
