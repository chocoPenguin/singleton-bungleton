<template>
  <div class="quiz-container">
    <!-- 로딩 상태 -->
    <div v-if="loading" class="text-center p-4">
      <ProgressSpinner />
      <p class="mt-3">문제를 불러오는 중...</p>
    </div>

    <!-- 문제 표시 -->
    <div v-else-if="questions.length > 0" class="quiz-wrapper">
      <!-- 전체 진행률 표시 -->
      <div class="progress-section mb-4">
        <div class="flex justify-content-between align-items-center mb-2">
          <h3>전체 진행률</h3>
          <span class="text-sm text-500">{{ Object.keys(answers).length }} / {{ questions.length }} 완료</span>
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
          <div class="question-header mb-3 p-2 bg-primary-50 border-round flex align-items-center">
            <Badge :value="(currentPage * questionsPerPage) + index + 1" severity="info" class="mr-2" />
            <span class="font-semibold text-primary">{{ question.title }}</span>
            <div class="ml-auto">
              <i v-if="answers[question.id]" class="pi pi-check-circle text-green-500 text-xl"></i>
              <i v-else class="pi pi-circle text-gray-300 text-xl"></i>
            </div>
          </div>

          <!-- 객관식 문제 -->
          <MultipleChoiceQuestion
            v-if="question.type === 'multiple_choice'"
            :key="`mc-${question.id}`"
            :question="question"
            :choices="question.choices"
            @answer="handleAnswer"
            @next="() => {}"
          />

          <!-- 주관식 문제 -->
          <SubjectiveQuestion
            v-else-if="question.type === 'subjective'"
            :key="`sub-${question.id}`"
            :question="question"
            :answer-type="question.answerType || 'long'"
            :max-length="question.maxLength"
            :placeholder="question.placeholder"
            @answer="handleAnswer"
            @next="() => {}"
          />

          <!-- 알 수 없는 타입 -->
          <Card v-else>
            <template #content>
              <p class="text-center text-500">알 수 없는 문제 타입: {{ question.type }}</p>
            </template>
          </Card>
        </div>
      </div>

      <!-- 네비게이션 버튼 -->
      <div class="navigation-controls mt-4">
        <!-- 페이지 완료 확인 -->
        <div class="page-summary mb-4 p-3 bg-blue-50 border-round">
          <div class="flex justify-content-between align-items-center">
            <div>
              <h5 class="m-0 text-blue-900">페이지 {{ currentPage + 1 }} 완료 상태</h5>
              <small class="text-blue-600">
                {{ currentPageQuestions.filter(q => answers[q.id]).length }} / {{ currentPageQuestions.length }} 문제 완료
              </small>
            </div>
            <div>
              <i v-if="currentPageAnswered" class="pi pi-check-circle text-green-500 text-2xl"></i>
              <i v-else class="pi pi-clock text-orange-500 text-2xl"></i>
            </div>
          </div>
        </div>

        <!-- 페이지 네비게이션 -->
        <div class="page-nav flex justify-content-between align-items-center p-3 bg-gray-50 border-round">
          <Button
            label="이전 페이지"
            severity="secondary"
            icon="pi pi-chevron-left"
            :disabled="currentPage === 0"
            @click="goToPreviousPage"
          />

          <div class="flex align-items-center gap-3">
            <div class="text-center">
              <div class="text-sm text-500">페이지</div>
              <div class="font-bold">{{ currentPage + 1 }} / {{ totalPages }}</div>
            </div>
          </div>

          <div class="flex gap-2">
            <Button
              v-if="currentPage < totalPages - 1"
              label="다음 페이지"
              severity="primary"
              icon="pi pi-chevron-right"
              iconPos="right"
              @click="goToNextPage"
            />
            <Button
              v-if="currentPage === totalPages - 1"
              label="퀴즈 완료"
              severity="success"
              icon="pi pi-check"
              @click="completeQuiz"
              :disabled="!allQuestionsAnswered"
            />
          </div>
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
    <div v-if="isCompleted" class="completion-screen text-center p-4">
      <i class="pi pi-check-circle text-6xl text-green-500 mb-4"></i>
      <h2>퀴즈 완료!</h2>
      <p class="mb-4">모든 문제를 완료했습니다.</p>
      <Button label="결과 보기" @click="showResults" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import Card from 'primevue/card';
import Button from 'primevue/button';
import ProgressBar from 'primevue/progressbar';
import ProgressSpinner from 'primevue/progressspinner';
import Badge from 'primevue/badge';
import MultipleChoiceQuestion from './MultipleChoiceQuestion.vue';
import SubjectiveQuestion from './SubjectiveQuestion.vue';

const toast = useToast();

// 반응형 데이터
const questions = ref([]);
const currentQuestionIndex = ref(0);
const currentPage = ref(0); // 현재 페이지 (0부터 시작)
const questionsPerPage = ref(10); // 페이지당 문제 수
const answers = ref({});
const loading = ref(false);
const isCompleted = ref(false);

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

// API 호출 함수
const fetchQuestions = async () => {
  loading.value = true;
  
  try {
    // 개발용 예제 데이터 (20개)
    questions.value = [
      // 1-5번 문제
      { id: 1, type: 'multiple_choice', title: 'JavaScript 기초', text: 'JavaScript에서 변수를 선언하는 키워드가 아닌 것은?', choices: [{ value: 'A', label: 'var' }, { value: 'B', label: 'let' }, { value: 'C', label: 'const' }, { value: 'D', label: 'define' }] },
      { id: 2, type: 'subjective', title: '서술형 문제', text: 'Vue.js의 주요 장점 3가지를 설명하세요.', answerType: 'long', maxLength: 500, placeholder: 'Vue.js의 장점을 자세히 설명해주세요...' },
      { id: 3, type: 'subjective', title: '간단 답변', text: 'HTML의 약자는 무엇인가요?', answerType: 'short', maxLength: 50, placeholder: '약자를 입력하세요' },
      { id: 4, type: 'multiple_choice', title: 'CSS 기초', text: 'CSS에서 박스 모델에 포함되지 않는 것은?', choices: [{ value: 'A', label: 'margin' }, { value: 'B', label: 'padding' }, { value: 'C', label: 'border' }, { value: 'D', label: 'display' }] },
      { id: 5, type: 'subjective', title: 'React 개념', text: 'React의 Virtual DOM에 대해 간단히 설명하세요.', answerType: 'long', maxLength: 300, placeholder: 'Virtual DOM의 개념을 설명해주세요...' },
      
      // 6-10번 문제
      { id: 6, type: 'multiple_choice', title: 'HTTP 프로토콜', text: 'HTTP 상태 코드 중 "Not Found"를 나타내는 코드는?', choices: [{ value: 'A', label: '200' }, { value: 'B', label: '404' }, { value: 'C', label: '500' }, { value: 'D', label: '302' }] },
      { id: 7, type: 'subjective', title: 'Git 개념', text: 'Git의 브랜치(branch)란 무엇인가요?', answerType: 'short', maxLength: 100, placeholder: '브랜치의 개념을 간단히...' },
      { id: 8, type: 'multiple_choice', title: 'Database', text: 'SQL에서 테이블의 모든 데이터를 조회하는 명령어는?', choices: [{ value: 'A', label: 'SELECT ALL' }, { value: 'B', label: 'SELECT *' }, { value: 'C', label: 'GET ALL' }, { value: 'D', label: 'SHOW ALL' }] },
      { id: 9, type: 'subjective', title: 'API 설계', text: 'RESTful API의 특징 2가지를 설명하세요.', answerType: 'long', maxLength: 400, placeholder: 'RESTful API의 특징을 설명해주세요...' },
      { id: 10, type: 'multiple_choice', title: 'Node.js', text: 'Node.js의 특징이 아닌 것은?', choices: [{ value: 'A', label: '비동기 처리' }, { value: 'B', label: '이벤트 기반' }, { value: 'C', label: '멀티스레드' }, { value: 'D', label: '서버사이드' }] },
      
      // 11-15번 문제
      { id: 11, type: 'multiple_choice', title: 'TypeScript', text: 'TypeScript의 장점이 아닌 것은?', choices: [{ value: 'A', label: '정적 타입 검사' }, { value: 'B', label: '컴파일 타임 에러 검출' }, { value: 'C', label: '런타임 성능 향상' }, { value: 'D', label: 'IDE 지원 향상' }] },
      { id: 12, type: 'subjective', title: '웹 보안', text: 'XSS 공격이란 무엇인가요?', answerType: 'long', maxLength: 300, placeholder: 'XSS 공격에 대해 설명해주세요...' },
      { id: 13, type: 'multiple_choice', title: '알고리즘', text: '시간 복잡도가 O(1)인 연산은?', choices: [{ value: 'A', label: '배열 순회' }, { value: 'B', label: '이진 탐색' }, { value: 'C', label: '해시 테이블 조회' }, { value: 'D', label: '정렬' }] },
      { id: 14, type: 'subjective', title: '디자인 패턴', text: 'MVC 패턴의 각 구성요소 역할을 설명하세요.', answerType: 'long', maxLength: 400, placeholder: 'Model, View, Controller의 역할을...' },
      { id: 15, type: 'multiple_choice', title: '네트워크', text: 'OSI 7계층 모델에서 HTTP는 몇 번째 계층에 속하나요?', choices: [{ value: 'A', label: '5계층' }, { value: 'B', label: '6계층' }, { value: 'C', label: '7계층' }, { value: 'D', label: '4계층' }] },
      
      // 16-20번 문제
      { id: 16, type: 'subjective', title: '클라우드', text: 'AWS와 같은 클라우드 서비스의 장점은?', answerType: 'short', maxLength: 150, placeholder: '클라우드의 주요 장점을...' },
      { id: 17, type: 'multiple_choice', title: 'DevOps', text: 'CI/CD에서 CI는 무엇의 약자인가요?', choices: [{ value: 'A', label: 'Continuous Integration' }, { value: 'B', label: 'Code Integration' }, { value: 'C', label: 'Complete Integration' }, { value: 'D', label: 'Custom Integration' }] },
      { id: 18, type: 'subjective', title: '성능 최적화', text: '웹사이트 로딩 속도를 개선하는 방법 3가지를 나열하세요.', answerType: 'long', maxLength: 350, placeholder: '성능 최적화 방법을 설명해주세요...' },
      { id: 19, type: 'multiple_choice', title: 'Docker', text: 'Docker 컨테이너의 특징이 아닌 것은?', choices: [{ value: 'A', label: '가상화' }, { value: 'B', label: '격리' }, { value: 'C', label: '이식성' }, { value: 'D', label: '하드웨어 에뮬레이션' }] },
      { id: 20, type: 'subjective', title: '프로젝트 관리', text: '애자일 개발 방법론의 핵심 원칙을 설명하세요.', answerType: 'long', maxLength: 400, placeholder: '애자일의 핵심 원칙을 설명해주세요...' }
    ];

    // 실제 API 호출은 주석 처리 (나중에 사용)
    /*
    const response = await fetch('/api/quiz/questions');
    const data = await response.json();
    questions.value = data.questions || [];
    */
    
  } catch (error) {
    console.error('문제 로딩 실패:', error);
    
    // 에러 발생 시에도 예제 데이터 표시
    questions.value = [
      {
        id: 1,
        type: 'multiple_choice',
        title: 'JavaScript 기초',
        text: 'JavaScript에서 변수를 선언하는 키워드가 아닌 것은?',
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
  answers.value[data.questionId] = data.answer;
  console.log('답변 저장:', data);
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
    const response = await fetch('/api/quiz/submit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        answers: answers.value
      })
    });
    
    const result = await response.json();
    console.log('제출 결과:', result);
    
  } catch (error) {
    console.error('답변 제출 실패:', error);
  }
};

const showResults = () => {
  // 결과 페이지로 이동하거나 결과 표시
  console.log('최종 답변:', answers.value);
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
</style>