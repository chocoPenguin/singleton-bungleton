<template>
  <div class="history-view">
    <div class="page-header">
      <h1 class="page-title">Question History</h1>
      <p class="page-description">생성된 퀴즈 세트 목록을 확인하고 상세 내용을 볼 수 있습니다</p>
    </div>

    <!-- Question Sets List -->
    <div class="content-container">
      <div class="question-sets-section">
        <h2 class="section-title">퀴즈 세트 목록</h2>

        <div v-if="loading" class="loading-container">
          <ProgressSpinner />
          <p>퀴즈 세트를 불러오는 중...</p>
        </div>

        <div v-else-if="questionSets.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="pi pi-file-o"></i>
          </div>
          <h3>생성된 퀴즈 세트가 없습니다</h3>
          <p>퀴즈 생성 페이지에서 새로운 퀴즈를 만들어보세요.</p>
          <Button label="퀴즈 생성하기" @click="$router.push('/questions/create')" />
        </div>

        <div v-else class="question-sets-grid">
          <Card
            v-for="questionSet in questionSets"
            :key="questionSet.id"
            class="question-set-card"
            @click="selectQuestionSet(questionSet)"
            :class="{ 'selected': selectedQuestionSet?.id === questionSet.id }"
          >
            <template #content>
              <div class="card-header">
                <h3 class="card-title">{{ questionSet.title || 'Untitled Quiz Set' }}</h3>
                <Badge :value="questionSet.num_questions + '문제'" severity="info" />
              </div>

              <div class="card-details">
                <div class="detail-item">
                  <i class="pi pi-users"></i>
                  <span>{{ questionSet.total_users }}명</span>
                </div>
                <div class="detail-item">
                  <i class="pi pi-calendar"></i>
                  <span>{{ formatDate(questionSet.created_at) }}</span>
                </div>
                <div class="detail-item">
                  <i class="pi pi-user"></i>
                  <span>{{ questionSet.author?.name || 'Unknown' }}</span>
                </div>
                <div v-if="questionSet.resource" class="detail-item">
                  <i class="pi pi-database"></i>
                  <span>{{ questionSet.resource.name }}</span>
                  <Tag
                    :value="getResourceTypeLabel(questionSet.resource.resource_type)"
                    :severity="getResourceTypeSeverity(questionSet.resource.resource_type)"
                    size="small"
                  />
                </div>
              </div>
            </template>
          </Card>
        </div>
      </div>

      <!-- Question Details Section -->
      <div v-if="selectedQuestionSet" class="question-details-section">
        <div class="details-header">
          <h2 class="section-title">문제 상세 내용</h2>
          <Button
            icon="pi pi-times"
            class="p-button-text p-button-plain"
            @click="selectedQuestionSet = null"
            aria-label="닫기"
          />
        </div>

        <div v-if="detailsLoading" class="loading-container">
          <ProgressSpinner />
          <p>문제 상세 정보를 불러오는 중...</p>
        </div>

        <div v-else-if="questionDetails.length === 0" class="empty-state">
          <p>이 퀴즈 세트에는 문제가 없습니다.</p>
        </div>

        <div v-else class="questions-container">
          <div class="questions-summary">
            <h3>총 {{ questionDetails.length }}개의 문제</h3>
            <p>퀴즈 세트: {{ selectedQuestionSet.title || 'Untitled' }}</p>
            <div v-if="selectedQuestionSet.resource" class="resource-info">
              <p class="resource-label">연결된 리소스:</p>
              <div class="resource-details">
                <span class="resource-name">{{ selectedQuestionSet.resource.name }}</span>
                <Tag
                  :value="getResourceTypeLabel(selectedQuestionSet.resource.resource_type)"
                  :severity="getResourceTypeSeverity(selectedQuestionSet.resource.resource_type)"
                  size="small"
                />
              </div>
              <p v-if="selectedQuestionSet.resource_description" class="resource-description">
                {{ selectedQuestionSet.resource_description }}
              </p>
            </div>
          </div>

          <Accordion :activeIndex="0" class="custom-accordion">
            <AccordionTab
              v-for="(question, index) in questionDetails"
              :key="question.question_id"
              :header="`문제 ${index + 1}: ${truncateText(question.question, 50)}`"
              class="custom-accordion-tab"
            >
              <div class="question-detail">
                <!-- 문제 내용 전체 표시 -->
                <div class="question-content">
                  <h4>문제</h4>
                  <p class="question-text">{{ question.question }}</p>
                </div>

                <div v-if="question.choices && question.choices.length > 0" class="choices-content">
                  <h4>선택지</h4>
                  <ul class="choices-list">
                    <li
                      v-for="(choice, choiceIndex) in question.choices"
                      :key="choiceIndex"
                      :class="{ 'correct-answer': choice === question.answer }"
                    >
                      {{ choiceIndex + 1 }}. {{ choice }}
                      <Tag v-if="choice === question.answer" value="정답" severity="success" />
                    </li>
                  </ul>
                </div>

                <div class="answer-content">
                  <h4>정답</h4>
                  <p class="answer-text">{{ question.answer }}</p>
                </div>

                <div class="meta-info">
                  <div class="meta-item">
                    <strong>문제 유형:</strong>
                    <Tag :value="getQuestionTypeLabel(question.type)" />
                  </div>
                  <div class="meta-item">
                    <strong>배점:</strong> {{ question.max_score }}점
                  </div>
                  <div class="meta-item">
                    <strong>할당 상태:</strong>
                    <Tag :value="question.status" :severity="getStatusSeverity(question.status)" />
                  </div>
                </div>
              </div>
            </AccordionTab>
          </Accordion>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue';
import { useToast } from 'primevue/usetoast';
import Card from 'primevue/card';
import Button from 'primevue/button';
import Badge from 'primevue/badge';
import Tag from 'primevue/tag';
import ProgressSpinner from 'primevue/progressspinner';
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import { getAllQuestionSets, getQuestionSetDetails } from '../../api/questions.js';
import { getResourceTypeLabel } from '../../api/resources.js';

const toast = useToast();

// State
const questionSets = ref([]);
const selectedQuestionSet = ref(null);
const questionDetails = ref([]);
const loading = ref(false);
const detailsLoading = ref(false);

// Load question sets
const fetchQuestionSets = async () => {
  loading.value = true;
  try {
    const response = await getAllQuestionSets();
    questionSets.value = response.data;
  } catch (error) {
    console.error('Failed to fetch question sets:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load question sets. Please try again.',
      life: 5000
    });
  } finally {
    loading.value = false;
  }
};

// Select question set and load details
const selectQuestionSet = async (questionSet) => {
  selectedQuestionSet.value = questionSet;
  questionDetails.value = [];

  detailsLoading.value = true;
  try {
    const response = await getQuestionSetDetails(questionSet.id);
    questionDetails.value = response.data.questions;
  } catch (error) {
    console.error('Failed to fetch question details:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load question details. Please try again.',
      life: 5000
    });
  } finally {
    detailsLoading.value = false;
  }
};

// Utility functions
const formatDate = (dateString) => {
  if (!dateString) return 'Unknown';
  const date = new Date(dateString);
  return date.toLocaleDateString('ko-KR') + ' ' + date.toLocaleTimeString('ko-KR', {
    hour: '2-digit',
    minute: '2-digit'
  });
};

const truncateText = (text, maxLength) => {
  if (!text) return '';
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
};

const getQuestionTypeLabel = (type) => {
  const typeMap = {
    'M': '객관식',
    'S': '주관식(단답)',
    'L': '주관식(서술)'
  };
  return typeMap[type] || '알 수 없음';
};

const getStatusSeverity = (status) => {
  const severityMap = {
    'assigned': 'info',
    'completed': 'success',
    'pending': 'warning'
  };
  return severityMap[status] || 'secondary';
};

const getResourceTypeSeverity = (type) => {
  switch (type) {
    case 'SP': return 'info';      // SharePoint
    case 'LS': return 'secondary'; // Local Storage
    case 'GC': return 'success';   // Google Cloud
    case 'S3': return 'warning';   // AWS S3
    default: return 'contrast';
  }
};

// 궁극의 아코디언 스타일링 솔루션 - MutationObserver 기반
const createUltimateAccordionSolution = () => {
  let observer = null;

  // 인라인 스타일 직접 적용 함수
  const applyInlineStyles = (element, styles) => {
    Object.entries(styles).forEach(([property, value]) => {
      element.style.setProperty(property, value, 'important');
    });
  };

  // 모든 텍스트 요소에 인라인 스타일 강제 적용
  const forceAccordionStyles = () => {
    const accordion = document.querySelector('.custom-accordion');
    if (!accordion) return;

    const headers = accordion.querySelectorAll('.p-accordion-header');

    headers.forEach(header => {
      // 모든 하위 텍스트 요소 찾기
      const textElements = header.querySelectorAll('*');
      const isActive = header.classList.contains('p-accordion-header-active');

      // 기본 스타일
      const baseStyles = {
        'text-shadow': 'none',
        'opacity': '1',
        'background-color': 'transparent',
        'border': 'none',
        'outline': 'none'
      };

      // 상태별 색상 스타일
      const colorStyles = isActive
        ? { 'color': '#2563eb', 'font-weight': '700' }  // 활성 상태 - 파란색
        : { 'color': '#374151', 'font-weight': '600' }; // 비활성 상태 - 진한 회색

      const finalStyles = { ...baseStyles, ...colorStyles };

      // 헤더 자체와 모든 하위 요소에 인라인 스타일 적용
      applyInlineStyles(header, finalStyles);
      textElements.forEach(el => applyInlineStyles(el, finalStyles));

      // 호버 이벤트 리스너 재설정
      header.onmouseenter = () => {
        const hoverStyles = isActive
          ? { 'color': '#1d4ed8', 'font-weight': '700' }  // 활성+호버 - 진한 파란색
          : { 'color': '#111827', 'font-weight': '700' }; // 비활성+호버 - 검은색

        const hoverFinalStyles = { ...baseStyles, ...hoverStyles };
        applyInlineStyles(header, hoverFinalStyles);
        textElements.forEach(el => applyInlineStyles(el, hoverFinalStyles));
      };

      header.onmouseleave = () => {
        const leaveStyles = isActive
          ? { 'color': '#2563eb', 'font-weight': '700' }
          : { 'color': '#374151', 'font-weight': '600' };

        const leaveFinalStyles = { ...baseStyles, ...leaveStyles };
        applyInlineStyles(header, leaveFinalStyles);
        textElements.forEach(el => applyInlineStyles(el, leaveFinalStyles));
      };
    });
  };

  // MutationObserver로 DOM 변화 감시
  const startObserver = () => {
    if (observer) observer.disconnect();

    observer = new MutationObserver((mutations) => {
      let shouldReapply = false;

      mutations.forEach((mutation) => {
        // 클래스 변화나 새 노드 추가 감지
        if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
          shouldReapply = true;
        } else if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
          shouldReapply = true;
        }
      });

      if (shouldReapply) {
        setTimeout(forceAccordionStyles, 50);
      }
    });

    const accordion = document.querySelector('.custom-accordion');
    if (accordion) {
      observer.observe(accordion, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['class']
      });
    }
  };

  // 초기 스타일 적용 및 관찰자 시작
  const initialize = () => {
    forceAccordionStyles();
    startObserver();

    // 추가 안전장치: 주기적으로 스타일 재적용
    const intervalId = setInterval(() => {
      if (document.querySelector('.custom-accordion')) {
        forceAccordionStyles();
      } else {
        clearInterval(intervalId);
      }
    }, 2000);
  };

  return { initialize, forceAccordionStyles };
};

// 궁극의 아코디언 솔루션 인스턴스 생성
let accordionSolution = null;

// Initialize
onMounted(() => {
  fetchQuestionSets();
});

// Watch for questionDetails changes and apply ultimate styling solution
watch(questionDetails, async () => {
  if (questionDetails.value.length > 0) {
    // DOM이 완전히 업데이트될 때까지 기다림
    await nextTick();

    // 잠시 후 궁극의 솔루션 적용
    setTimeout(() => {
      console.log('🚀 questionDetails 변화 감지 - 궁극의 아코디언 솔루션 시작');

      if (accordionSolution) {
        accordionSolution.forceAccordionStyles();
      } else {
        accordionSolution = createUltimateAccordionSolution();
        accordionSolution.initialize();
      }
    }, 300);
  }
}, { deep: true });
</script>

<style scoped lang="scss">
@use '@/assets/styles/datatable.scss';

.history-view {
  font-family: 'Inter', sans-serif;
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  background-color: #ffffff; // 흰색 배경
  color: #111827; // 검은색 텍스트
}

.page-header {
  margin-bottom: 2rem;
  text-align: center;
}

.page-title {
  font-size: 2rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 0.5rem 0;
}

.page-description {
  color: #4b5563;
  font-size: 1.1rem;
  margin: 0;
}

.content-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  align-items: start;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 1rem 0;
}

.loading-container, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
  color: #4b5563;
  background: #f9fafb;
  border-radius: 0.75rem;
}

.question-sets-section, .question-details-section {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.question-details-section {
  max-height: 80vh;
  overflow-y: auto;
}

.question-set-card {
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  border-radius: 0.5rem;

  &:hover {
    border-color: #d1d5db;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  }

  &.selected {
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.card-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1f2937;
}

.card-details {
  color: #6b7280;
}

.questions-summary {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #ffffff;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.resource-info {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.resource-label {
  font-weight: 600;
  color: #374151;
  margin: 0 0 0.5rem 0;
  font-size: 0.875rem;
}

.resource-details {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.resource-name {
  font-weight: 600;
  color: #1f2937;
}

.resource-description {
  color: #6b7280;
  font-size: 0.875rem;
  line-height: 1.4;
  margin: 0;
  font-style: italic;
}

.question-detail {
  padding: 1rem 0;
}

.question-content,
.choices-content,
.answer-content {
  margin-bottom: 1.5rem;
}

.question-content h4,
.choices-content h4,
.answer-content h4 {
  margin: 0 0 0.5rem 0;
  color: #374151;
  font-size: 1rem;
  font-weight: 600;
}

.question-text,
.answer-text {
  margin: 0;
  color: #1f2937;
  line-height: 1.6;
  background: #f9fafb;
  padding: 0.75rem;
  border-radius: 0.375rem;
  border-left: 4px solid #3b82f6;
}

.choices-list {
  list-style: none;
  padding: 0;
  margin: 0;
  background: #f9fafb;
  border-radius: 0.375rem;
  overflow: hidden;
}

.choices-list li {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  color: #374151;
  font-weight: 500;

  &:last-child {
    border-bottom: none;
  }

  &.correct-answer {
    background: #ecfdf5;
    border-left: 4px solid #10b981;
    font-weight: 600;
    color: #065f46;
  }
}

.meta-info {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #374151;
}

.meta-item strong {
  color: #374151;
}

// Accordion styles for light theme
::v-deep(.p-accordion-header-link) {
  background-color: #ffffff !important;
  border: 1px solid #e5e7eb !important;
  color: #374151 !important;
}

::v-deep(.p-accordion-header:not(.p-disabled).p-accordion-header-active > .p-accordion-header-link) {
  background-color: #eff6ff !important;
  border-color: #bfdbfe !important;
  color: #1e40af !important;
}

::v-deep(.p-accordion-content) {
  background-color: #ffffff !important;
  color: #374151 !important;
  border: 1px solid #e5e7eb !important;
  border-top: 0 !important;
}

/* 라이트 테마 강제 적용 */
.question-details-section {
  background-color: #ffffff !important; /* 흰색 배경 */
  color: #1f2937 !important; /* 어두운 글자색 */
}

.question-details-section .section-title,
.question-details-section h3,
.question-details-section h4,
.question-details-section p,
.question-details-section strong,
.question-details-section span,
.question-details-section li {
  color: #1f2937 !important; /* 모든 텍스트 어두운 색으로 */
}

.question-details-section .questions-summary,
.question-details-section .meta-info {
  background-color: #f9fafb !important; /* 약간 밝은 회색 배경 */
  border-color: #e5e7eb !important;
}

.question-details-section .choices-list li {
  background-color: #ffffff !important;
}

.question-details-section .choices-list li.correct-answer {
  background-color: #dbeafe !important; /* 정답 선택지 배경 */
  color: #1e40af !important;
}

/* ==============================================
   ACCORDION HEADER TEXT VISIBILITY - ULTIMATE FIX
   ============================================== */

/* 아코디언 헤더 텍스트 가시성을 위한 최강 우선순위 CSS */
.history-view .questions-container .custom-accordion .p-accordion-header,
.history-view .questions-container .custom-accordion .p-accordion-header *,
.history-view .questions-container .custom-accordion .p-accordion-header span,
.history-view .questions-container .custom-accordion .p-accordion-header div,
.history-view .questions-container .custom-accordion .p-accordion-header a,
.history-view .questions-container .custom-accordion .p-accordion-header button,
.history-view .questions-container .custom-accordion .p-accordion-header .p-accordion-header-link {
  color: #374151 !important; /* 기본 상태 - 진한 회색 */
  font-weight: 700 !important;
  opacity: 1 !important;
  text-shadow: none !important;
  background-color: transparent !important;
  border: none !important;
}

/* 호버 상태 */
.history-view .questions-container .custom-accordion .p-accordion-header:hover,
.history-view .questions-container .custom-accordion .p-accordion-header:hover *,
.history-view .questions-container .custom-accordion .p-accordion-header:hover span,
.history-view .questions-container .custom-accordion .p-accordion-header:hover div,
.history-view .questions-container .custom-accordion .p-accordion-header:hover a,
.history-view .questions-container .custom-accordion .p-accordion-header:hover button,
.history-view .questions-container .custom-accordion .p-accordion-header:hover .p-accordion-header-link {
  color: #1f2937 !important; /* 호버 상태 - 더 진한 회색 */
  font-weight: 700 !important;
  opacity: 1 !important;
  text-shadow: none !important;
  background-color: transparent !important;
}

/* 활성 상태 (열린 상태) */
.history-view .questions-container .custom-accordion .p-accordion-header-active,
.history-view .questions-container .custom-accordion .p-accordion-header-active *,
.history-view .questions-container .custom-accordion .p-accordion-header-active span,
.history-view .questions-container .custom-accordion .p-accordion-header-active div,
.history-view .questions-container .custom-accordion .p-accordion-header-active a,
.history-view .questions-container .custom-accordion .p-accordion-header-active button,
.history-view .questions-container .custom-accordion .p-accordion-header-active .p-accordion-header-link {
  color: #2563eb !important; /* 활성 상태 - 파란색 */
  font-weight: 700 !important;
  opacity: 1 !important;
  text-shadow: none !important;
  background-color: transparent !important;
}

/* 활성 + 호버 상태 */
.history-view .questions-container .custom-accordion .p-accordion-header-active:hover,
.history-view .questions-container .custom-accordion .p-accordion-header-active:hover *,
.history-view .questions-container .custom-accordion .p-accordion-header-active:hover span,
.history-view .questions-container .custom-accordion .p-accordion-header-active:hover div,
.history-view .questions-container .custom-accordion .p-accordion-header-active:hover a,
.history-view .questions-container .custom-accordion .p-accordion-header-active:hover button,
.history-view .questions-container .custom-accordion .p-accordion-header-active:hover .p-accordion-header-link {
  color: #1d4ed8 !important; /* 활성+호버 상태 - 진한 파란색 */
  font-weight: 700 !important;
  opacity: 1 !important;
  text-shadow: none !important;
  background-color: transparent !important;
}

/* 글로벌 백업 - 최후의 수단 */
:global(.custom-accordion .p-accordion-header *) {
  color: #374151 !important;
  font-weight: 700 !important;
  opacity: 1 !important;
  text-shadow: none !important;
}

:global(.custom-accordion .p-accordion-header:hover *) {
  color: #1f2937 !important;
}

:global(.custom-accordion .p-accordion-header-active *) {
  color: #2563eb !important;
}

:global(.custom-accordion .p-accordion-header-active:hover *) {
  color: #1d4ed8 !important;
}

</style>
