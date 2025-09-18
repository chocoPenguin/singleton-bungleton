<template>
  <div class="quiz-detail">
    <!-- 로딩 상태 -->
    <div v-if="loading" class="text-center p-4">
      <ProgressSpinner />
      <p class="mt-3">퀴즈 정보를 불러오는 중...</p>
    </div>

    <!-- 에러 상태 -->
    <div v-else-if="error" class="error-state">
      <Card>
        <template #content>
          <div class="text-center p-4">
            <i class="pi pi-exclamation-triangle text-red-500 text-4xl mb-3"></i>
            <h3>오류 발생</h3>
            <p>{{ error }}</p>
            <div class="mt-4">
              <Button
                label="다시 시도"
                icon="pi pi-refresh"
                @click="fetchQuizDetail"
                class="mr-2"
              />
              <Button
                label="목록으로"
                icon="pi pi-arrow-left"
                severity="secondary"
                @click="goBack"
              />
            </div>
          </div>
        </template>
      </Card>
    </div>

    <!-- 퀴즈 상세 정보 -->
    <div v-else-if="questionSet" class="quiz-detail-content">
      <!-- 헤더 -->
      <div class="detail-header">
        <div class="header-content">
          <div class="breadcrumb">
            <Button
              icon="pi pi-arrow-left"
              label="목록으로"
              text
              @click="goBack"
              class="back-btn"
            />
          </div>
          <h1 class="page-title">퀴즈 상세 정보</h1>
          <div class="header-actions">
            <Button
              icon="pi pi-trash"
              label="삭제"
              severity="danger"
              outlined
              @click="confirmDelete"
            />
          </div>
        </div>
      </div>

      <!-- 기본 정보 카드 -->
      <Card class="info-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-info-circle mr-2"></i>
            기본 정보
          </div>
        </template>
        <template #content>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">퀴즈 ID</span>
              <Badge :value="questionSet.id" severity="info" />
            </div>
            <div class="info-item">
              <span class="info-label">대상 그룹</span>
              <Tag :value="questionSet.group?.name || '그룹 없음'" severity="secondary" />
            </div>
            <div class="info-item">
              <span class="info-label">사용자당 문제 수</span>
              <div class="flex align-items-center gap-2">
                <i class="pi pi-question-circle text-blue-500"></i>
                <span>{{ questionSet.num_questions }}개</span>
              </div>
            </div>
            <div class="info-item">
              <span class="info-label">할당된 사용자</span>
              <div class="flex align-items-center gap-2">
                <i class="pi pi-users text-green-500"></i>
                <span>{{ questionSet.total_users }}명</span>
              </div>
            </div>
            <div class="info-item">
              <span class="info-label">총 생성된 문제</span>
              <Badge :value="`${totalQuestions}개`" severity="success" />
            </div>
            <div class="info-item">
              <span class="info-label">생성일</span>
              <span class="created-date">{{ formatDate(questionSet.created_at) }}</span>
            </div>
          </div>

          <div v-if="questionSet.description" class="description-section">
            <h4>설명 및 요구사항</h4>
            <div class="description-content">
              {{ questionSet.description }}
            </div>
          </div>
        </template>
      </Card>

      <!-- 사용자별 할당 정보 -->
      <Card class="assignments-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-users mr-2"></i>
            사용자별 문제 할당 ({{ userAssignments.length }}명)
          </div>
        </template>
        <template #content>
          <div class="user-assignments">
            <div
              v-for="assignment in userAssignments"
              :key="assignment.user_id"
              class="user-assignment-card"
            >
              <div class="user-header">
                <div class="user-info">
                  <Avatar
                    :label="assignment.user_name.charAt(0)"
                    class="user-avatar"
                    shape="circle"
                    size="large"
                  />
                  <div class="user-details">
                    <h4>{{ assignment.user_name }}</h4>
                    <span class="user-id">ID: {{ assignment.user_id }}</span>
                  </div>
                </div>
                <div class="assignment-stats">
                  <Badge :value="`${assignment.question_count}개 문제`" severity="info" />
                </div>
              </div>

              <div class="assigned-questions">
                <h5>할당된 문제들</h5>
                <div class="questions-list">
                  <div
                    v-for="(question, index) in assignment.assigned_questions"
                    :key="question.question_id"
                    class="question-item"
                  >
                    <div class="question-number">
                      <Badge :value="index + 1" />
                    </div>
                    <div class="question-content">
                      <p class="question-text">{{ question.question }}</p>
                      <div class="question-meta">
                        <small class="question-id">ID: {{ question.question_id }}</small>
                        <small class="answer-preview">정답: {{ question.answer }}</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </Card>

      <!-- 전체 문제 목록 -->
      <Card class="questions-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-list mr-2"></i>
            전체 문제 목록 ({{ allQuestions.length }}개)
          </div>
        </template>
        <template #content>
          <Accordion :multiple="true" class="questions-accordion">
            <AccordionTab
              v-for="(question, index) in allQuestions"
              :key="question.id"
              :header="`문제 ${index + 1}: ${question.question.substring(0, 50)}...`"
            >
              <div class="question-detail">
                <div class="question-header-info">
                  <div class="question-meta-info">
                    <Badge :value="`ID: ${question.id}`" severity="info" class="mr-2" />
                    <Tag value="객관식" severity="secondary" />
                  </div>
                </div>

                <div class="question-full-text">
                  <h4>문제</h4>
                  <p>{{ question.question }}</p>
                </div>

                <div v-if="question.choices" class="question-choices">
                  <h4>선택지</h4>
                  <div class="choices-list">
                    <div
                      v-for="(choice, choiceIndex) in parseChoices(question.choices)"
                      :key="choiceIndex"
                      class="choice-item"
                      :class="{ 'correct-choice': choice === question.answer }"
                    >
                      <span class="choice-label">{{ String.fromCharCode(65 + choiceIndex) }}.</span>
                      <span class="choice-text">{{ choice }}</span>
                      <Tag v-if="choice === question.answer" value="정답" severity="success" class="ml-2" />
                    </div>
                  </div>
                </div>

                <div class="question-answer">
                  <h4>정답</h4>
                  <Tag :value="question.answer" severity="success" />
                </div>
              </div>
            </AccordionTab>
          </Accordion>
        </template>
      </Card>
    </div>

    <!-- 삭제 확인 다이얼로그 -->
    <ConfirmDialog />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';

// PrimeVue Components
import Card from 'primevue/card';
import Button from 'primevue/button';
import Badge from 'primevue/badge';
import Tag from 'primevue/tag';
import Avatar from 'primevue/avatar';
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import ProgressSpinner from 'primevue/progressspinner';
import ConfirmDialog from 'primevue/confirmdialog';

// Composables
const route = useRoute();
const router = useRouter();
const toast = useToast();
const confirm = useConfirm();

// 반응형 데이터
const questionSet = ref(null);
const userAssignments = ref([]);
const allQuestions = ref([]);
const loading = ref(false);
const error = ref(null);

// Props에서 ID 가져오기
const quizId = computed(() => route.params.id);

// 계산된 속성
const totalQuestions = computed(() => {
  return allQuestions.value.length;
});

// API 호출 함수들
const fetchQuizDetail = async () => {
  loading.value = true;
  error.value = null;

  try {
    // 개발용 예제 데이터
    const mockQuestionSet = {
      id: parseInt(quizId.value),
      group: { id: 1, name: '신규 입사자' },
      num_questions: 5,
      description: '기본 업무 프로세스에 대한 이해도를 측정하는 퀴즈입니다. 중급 난이도의 객관식 문제로 구성되어 있습니다.',
      total_users: 3,
      created_at: '2024-01-15T09:00:00Z',
      author_id: 1
    };

    const mockUserAssignments = [
      {
        user_id: 1,
        user_name: '김철수',
        assigned_questions: [
          {
            question_id: 1,
            question: '회사의 핵심 가치 중 하나가 아닌 것은?',
            answer: 'D'
          },
          {
            question_id: 2,
            question: '신규 입사자가 첫 주에 완료해야 하는 필수 교육은?',
            answer: 'B'
          },
          {
            question_id: 3,
            question: '업무 시작 전 안전 점검 사항은?',
            answer: 'A'
          },
          {
            question_id: 4,
            question: '고객 응대 시 가장 중요한 원칙은?',
            answer: 'C'
          },
          {
            question_id: 5,
            question: '비상 상황 발생 시 첫 번째 연락처는?',
            answer: 'A'
          }
        ],
        question_count: 5
      },
      {
        user_id: 2,
        user_name: '이영희',
        assigned_questions: [
          {
            question_id: 6,
            question: '회사의 조직도에서 직접 보고 라인은?',
            answer: 'B'
          },
          {
            question_id: 7,
            question: '연차 신청 시 최소 사전 통보 기간은?',
            answer: 'C'
          },
          {
            question_id: 8,
            question: '회사 내부 커뮤니케이션 도구는?',
            answer: 'D'
          },
          {
            question_id: 9,
            question: '프로젝트 진행 시 우선순위 결정 기준은?',
            answer: 'A'
          },
          {
            question_id: 10,
            question: '팀 회의 참석 시 준비해야 할 자료는?',
            answer: 'B'
          }
        ],
        question_count: 5
      },
      {
        user_id: 3,
        user_name: '박민수',
        assigned_questions: [
          {
            question_id: 11,
            question: '업무 문서 작성 시 필수 포함 사항은?',
            answer: 'C'
          },
          {
            question_id: 12,
            question: '외부 미팅 참석 시 준수사항은?',
            answer: 'A'
          },
          {
            question_id: 13,
            question: '업무 개선 제안 시 절차는?',
            answer: 'D'
          },
          {
            question_id: 14,
            question: '정보 보안 규정 중 가장 중요한 것은?',
            answer: 'B'
          },
          {
            question_id: 15,
            question: '업무 인수인계 시 체크리스트 항목은?',
            answer: 'C'
          }
        ],
        question_count: 5
      }
    ];

    const mockAllQuestions = [
      {
        id: 1,
        question: '회사의 핵심 가치 중 하나가 아닌 것은?',
        choices: '["고객 중심", "혁신", "협력", "이익 추구"]',
        answer: 'D'
      },
      {
        id: 2,
        question: '신규 입사자가 첫 주에 완료해야 하는 필수 교육은?',
        choices: '["업무 매뉴얼 숙지", "안전 교육", "시스템 교육", "모든 항목"]',
        answer: 'D'
      },
      // ... 나머지 문제들 (실제로는 15개 모두)
    ];

    // 실제 API 호출로 대체 예정
    // const response = await fetch(`/api/question_sets/${quizId.value}`);
    // const data = await response.json();

    questionSet.value = mockQuestionSet;
    userAssignments.value = mockUserAssignments;
    allQuestions.value = mockAllQuestions;

  } catch (err) {
    console.error('퀴즈 상세 정보 조회 실패:', err);
    error.value = '퀴즈 정보를 불러오는데 실패했습니다.';
  } finally {
    loading.value = false;
  }
};

// 이벤트 핸들러들
const goBack = () => {
  router.push('/admin/quiz');
};

const confirmDelete = () => {
  confirm.require({
    message: '이 퀴즈를 삭제하시겠습니까? 삭제된 데이터는 복구할 수 없습니다.',
    header: '삭제 확인',
    icon: 'pi pi-exclamation-triangle',
    rejectClass: 'p-button-secondary p-button-outlined',
    rejectLabel: '취소',
    acceptLabel: '삭제',
    accept: deleteQuiz
  });
};

const deleteQuiz = async () => {
  try {
    // 실제 API 호출로 대체 예정
    // await fetch(`/api/question_sets/${quizId.value}`, { method: 'DELETE' });

    toast.add({
      severity: 'success',
      summary: '삭제 완료',
      detail: '퀴즈가 성공적으로 삭제되었습니다.',
      life: 3000
    });

    // 목록 페이지로 이동
    router.push('/admin/quiz');

  } catch (error) {
    console.error('퀴즈 삭제 실패:', error);
    toast.add({
      severity: 'error',
      summary: '삭제 실패',
      detail: '퀴즈 삭제 중 오류가 발생했습니다.',
      life: 3000
    });
  }
};

// 유틸리티 함수들
const formatDate = (dateString) => {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const parseChoices = (choicesJson) => {
  try {
    return JSON.parse(choicesJson);
  } catch (error) {
    return [];
  }
};

// 컴포넌트 마운트 시
onMounted(() => {
  fetchQuizDetail();
});
</script>

<style scoped>
.quiz-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

/* 헤더 */
.detail-header {
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.breadcrumb {
  display: flex;
  align-items: center;
}

.back-btn {
  color: #6b7280 !important;
}

.page-title {
  margin: 0;
  font-size: 1.875rem;
  font-weight: 600;
  color: #374151;
  flex: 1;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

/* 카드 공통 스타일 */
.info-card,
.assignments-card,
.questions-card {
  margin-bottom: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-radius: 1rem;
}

.card-title {
  display: flex;
  align-items: center;
  font-size: 1.25rem;
  font-weight: 600;
  color: #374151;
}

/* 기본 정보 그리드 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.info-label {
  font-weight: 500;
  color: #6b7280;
}

.created-date {
  color: #374151;
  font-size: 0.875rem;
}

/* 설명 섹션 */
.description-section {
  border-top: 1px solid #e5e7eb;
  padding-top: 1.5rem;
  margin-top: 1.5rem;
}

.description-section h4 {
  margin: 0 0 0.75rem 0;
  color: #374151;
  font-size: 1rem;
}

.description-content {
  background: #f8fafc;
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
  line-height: 1.6;
  color: #374151;
}

/* 사용자 할당 */
.user-assignments {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.user-assignment-card {
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1.5rem;
  background: #f8fafc;
}

.user-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-avatar {
  background: #3b82f6 !important;
  color: white !important;
}

.user-details h4 {
  margin: 0;
  color: #374151;
  font-size: 1.125rem;
}

.user-id {
  color: #6b7280;
  font-size: 0.875rem;
}

.assigned-questions h5 {
  margin: 0 0 1rem 0;
  color: #374151;
  font-size: 1rem;
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.question-item {
  display: flex;
  gap: 0.75rem;
  padding: 0.75rem;
  background: white;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.question-number {
  flex-shrink: 0;
}

.question-content {
  flex: 1;
}

.question-text {
  margin: 0 0 0.5rem 0;
  color: #374151;
  line-height: 1.5;
}

.question-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: #6b7280;
}

/* 전체 문제 목록 */
.questions-accordion {
  border-radius: 0.5rem;
  overflow: hidden;
}

.question-detail {
  padding: 1rem 0;
}

.question-header-info {
  margin-bottom: 1rem;
}

.question-meta-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.question-full-text h4,
.question-choices h4,
.question-answer h4 {
  margin: 0 0 0.75rem 0;
  color: #374151;
  font-size: 1rem;
}

.question-full-text p {
  color: #374151;
  line-height: 1.6;
  margin: 0;
}

.choices-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.choice-item {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  background: #f8fafc;
  border-radius: 0.375rem;
  border: 1px solid #e5e7eb;
}

.choice-item.correct-choice {
  background: #ecfdf5;
  border-color: #10b981;
}

.choice-label {
  font-weight: 600;
  color: #374151;
  margin-right: 0.5rem;
  min-width: 1.5rem;
}

.choice-text {
  color: #374151;
  flex: 1;
}

/* 에러 상태 */
.error-state {
  margin: 2rem 0;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .quiz-detail {
    padding: 0.5rem;
  }

  .header-content {
    flex-direction: column;
    align-items: stretch;
  }

  .page-title {
    text-align: center;
    margin: 1rem 0;
  }

  .info-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .info-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .user-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .question-meta {
    flex-direction: column;
    gap: 0.25rem;
  }
}
</style>