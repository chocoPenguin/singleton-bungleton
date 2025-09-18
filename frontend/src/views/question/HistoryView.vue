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
                <h3 class="card-title">{{ questionSet.description || 'Untitled Quiz Set' }}</h3>
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
            <p>퀴즈 세트: {{ selectedQuestionSet.description || 'Untitled' }}</p>
          </div>

          <Accordion :activeIndex="0">
            <AccordionTab
              v-for="(question, index) in questionDetails"
              :key="question.question_id"
              :header="`문제 ${index + 1}: ${truncateText(question.question, 50)}`"
            >
              <div class="question-detail">
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
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import Card from 'primevue/card';
import Button from 'primevue/button';
import Badge from 'primevue/badge';
import Tag from 'primevue/tag';
import ProgressSpinner from 'primevue/progressspinner';
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import { getAllQuestionSets, getQuestionSetDetails } from '../../api/questions.js';

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

// Initialize
onMounted(() => {
  fetchQuestionSets();
});
</script>

<style scoped>
.history-view {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
  text-align: center;
}

.page-title {
  font-size: 2rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.5rem 0;
}

.page-description {
  color: #6b7280;
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
  color: #374151;
  margin: 0 0 1rem 0;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
  color: #6b7280;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.question-sets-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.question-set-card {
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.question-set-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.question-set-card.selected {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
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
  margin: 0;
  line-height: 1.4;
}

.card-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.detail-item i {
  color: #9ca3af;
}

.question-details-section {
  background: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  max-height: 80vh;
  overflow-y: auto;
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.questions-summary {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
}

.questions-summary h3 {
  margin: 0 0 0.5rem 0;
  color: #1f2937;
}

.questions-summary p {
  margin: 0;
  color: #6b7280;
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
}

.choices-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.choices-list li {
  padding: 0.5rem 0;
  border-bottom: 1px solid #f3f4f6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.choices-list li.correct-answer {
  background: #f0f9ff;
  padding: 0.5rem;
  border-radius: 0.375rem;
  border-bottom: none;
  margin-bottom: 0.25rem;
}

.meta-info {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

/* Responsive design */
@media (max-width: 1024px) {
  .content-container {
    grid-template-columns: 1fr;
  }

  .question-details-section {
    max-height: 60vh;
  }
}

@media (max-width: 768px) {
  .history-view {
    padding: 1rem;
  }

  .page-title {
    font-size: 1.5rem;
  }

  .meta-info {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>