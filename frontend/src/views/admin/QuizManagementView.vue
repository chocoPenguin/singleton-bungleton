<template>
  <div class="quiz-management">
    <!-- 페이지 헤더 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">Quiz Management</h1>
        <p class="page-description">AI 기반 퀴즈 생성 및 관리</p>
      </div>
      <Button
        label="퀴즈 생성"
        icon="pi pi-plus"
        @click="showCreateDialog = true"
        class="create-btn"
      />
    </div>

    <!-- 로딩 상태 -->
    <div v-if="loading" class="text-center p-4">
      <ProgressSpinner />
      <p class="mt-3">퀴즈 목록을 불러오는 중...</p>
    </div>

    <!-- 퀴즈 목록 테이블 -->
    <Card v-else class="quiz-table-card">
      <template #content>
        <DataTable
          :value="questionSets"
          :paginator="true"
          :rows="10"
          :rowsPerPageOptions="[5, 10, 20]"
          dataKey="id"
          v-model:selection="selectedQuestionSets"
          selectionMode="multiple"
          :loading="loading"
          filterDisplay="menu"
          :globalFilterFields="['id', 'description', 'group.name']"
          class="quiz-datatable"
          @row-click="onRowClick"
        >
          <template #header>
            <div class="table-header">
              <div class="table-title">
                <h3>퀴즈 목록</h3>
                <Badge :value="questionSets.length" severity="info" />
              </div>
              <div class="table-actions">
                <IconField iconPosition="left">
                  <InputIcon class="pi pi-search" />
                  <InputText
                    v-model="globalFilter"
                    placeholder="검색..."
                    class="search-input"
                  />
                </IconField>
                <Button
                  icon="pi pi-refresh"
                  severity="secondary"
                  @click="fetchQuestionSets"
                  :loading="loading"
                  text
                />
              </div>
            </div>
          </template>

          <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>

          <Column field="id" header="ID" sortable style="width: 5rem">
            <template #body="{ data }">
              <Badge :value="data.id" severity="info" />
            </template>
          </Column>

          <Column field="group.name" header="그룹" sortable>
            <template #body="{ data }">
              <Tag :value="data.group?.name || '그룹 없음'" severity="secondary" />
            </template>
          </Column>

          <Column field="num_questions" header="문제 수" sortable style="width: 8rem">
            <template #body="{ data }">
              <div class="flex align-items-center gap-2">
                <i class="pi pi-question-circle text-blue-500"></i>
                <span>{{ data.num_questions || 0 }}개</span>
              </div>
            </template>
          </Column>

          <Column field="description" header="설명" style="min-width: 200px">
            <template #body="{ data }">
              <div class="description-cell">
                <span v-if="data.description" class="description-text">
                  {{ data.description.length > 50 ? data.description.substring(0, 50) + '...' : data.description }}
                </span>
                <span v-else class="no-description">설명 없음</span>
              </div>
            </template>
          </Column>

          <Column field="total_users" header="할당 사용자" sortable style="width: 10rem">
            <template #body="{ data }">
              <div class="flex align-items-center gap-2">
                <i class="pi pi-users text-green-500"></i>
                <span>{{ data.total_users || 0 }}명</span>
              </div>
            </template>
          </Column>

          <Column field="created_at" header="생성일" sortable style="width: 10rem">
            <template #body="{ data }">
              <span class="created-date">
                {{ formatDate(data.created_at) }}
              </span>
            </template>
          </Column>

          <Column header="액션" style="width: 8rem">
            <template #body="{ data }">
              <div class="action-buttons">
                <Button
                  icon="pi pi-eye"
                  severity="info"
                  text
                  rounded
                  @click.stop="viewDetails(data.id)"
                  v-tooltip.top="'상세 보기'"
                />
                <Button
                  icon="pi pi-trash"
                  severity="danger"
                  text
                  rounded
                  @click.stop="confirmDelete(data)"
                  v-tooltip.top="'삭제'"
                />
              </div>
            </template>
          </Column>

          <template #empty>
            <div class="empty-state">
              <i class="pi pi-inbox empty-icon"></i>
              <h3>퀴즈가 없습니다</h3>
              <p>새로운 퀴즈를 생성해보세요.</p>
              <Button
                label="퀴즈 생성하기"
                icon="pi pi-plus"
                @click="showCreateDialog = true"
              />
            </div>
          </template>
        </DataTable>
      </template>
    </Card>

    <!-- 퀴즈 생성 다이얼로그 -->
    <QuizCreateDialog
      v-model:visible="showCreateDialog"
      @quiz-created="onQuizCreated"
    />

    <!-- 삭제 확인 다이얼로그 -->
    <ConfirmDialog />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';

// PrimeVue Components
import Card from 'primevue/card';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import IconField from 'primevue/iconfield';
import InputIcon from 'primevue/inputicon';
import Badge from 'primevue/badge';
import Tag from 'primevue/tag';
import ProgressSpinner from 'primevue/progressspinner';
import ConfirmDialog from 'primevue/confirmdialog';

// Custom Components
import QuizCreateDialog from '@/components/admin/QuizCreateDialog.vue';

// Composables
const router = useRouter();
const toast = useToast();
const confirm = useConfirm();

// 반응형 데이터
const questionSets = ref([]);
const selectedQuestionSets = ref([]);
const loading = ref(false);
const showCreateDialog = ref(false);
const globalFilter = ref('');

// 계산된 속성
const filteredQuestionSets = computed(() => {
  if (!globalFilter.value) return questionSets.value;

  const searchTerm = globalFilter.value.toLowerCase();
  return questionSets.value.filter(qs =>
    qs.id.toString().includes(searchTerm) ||
    qs.description?.toLowerCase().includes(searchTerm) ||
    qs.group?.name?.toLowerCase().includes(searchTerm)
  );
});

// API 호출 함수들
const fetchQuestionSets = async () => {
  console.log('fetchQuestionSets called');
  loading.value = true;
  try {
    const response = await fetch('http://localhost:8000/api/question_sets');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    questionSets.value = data;

  } catch (error) {
    console.error('퀴즈 목록 조회 실패:', error);
    toast.add({
      severity: 'error',
      summary: '오류',
      detail: '퀴즈 목록을 불러오는데 실패했습니다.',
      life: 3000
    });
  } finally {
    loading.value = false;
  }
};

// 이벤트 핸들러들
const onRowClick = (event) => {
  viewDetails(event.data.id);
};

const viewDetails = (id) => {
  router.push(`/admin/quiz/${id}`);
};

const confirmDelete = (questionSet) => {
  confirm.require({
    message: `퀴즈 "${questionSet.description || `ID: ${questionSet.id}`}"를 삭제하시겠습니까?`,
    header: '삭제 확인',
    icon: 'pi pi-exclamation-triangle',
    rejectClass: 'p-button-secondary p-button-outlined',
    rejectLabel: '취소',
    acceptLabel: '삭제',
    accept: () => deleteQuestionSet(questionSet.id)
  });
};

const deleteQuestionSet = async (id) => {
  try {
    const response = await fetch(`http://localhost:8000/api/question_sets/${id}`, {
      method: 'DELETE'
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || '퀴즈 삭제 실패');
    }

    // Remove from local list after successful deletion
    questionSets.value = questionSets.value.filter(qs => qs.id !== id);

    toast.add({
      severity: 'success',
      summary: '성공',
      detail: '퀴즈가 삭제되었습니다.',
      life: 3000
    });
  } catch (error) {
    console.error('퀴즈 삭제 실패:', error);
    toast.add({
      severity: 'error',
      summary: '오류',
      detail: '퀴즈 삭제에 실패했습니다.',
      life: 3000
    });
  }
};

const onQuizCreated = (newQuiz) => {
  // 새로 생성된 퀴즈를 목록에 추가
  questionSets.value.unshift(newQuiz);

  toast.add({
    severity: 'success',
    summary: '성공',
    detail: '퀴즈가 성공적으로 생성되었습니다.',
    life: 3000
  });
};

// 유틸리티 함수들
const formatDate = (dateString) => {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
};

// 컴포넌트 마운트 시 데이터 로딩
onMounted(async () => {
  console.log('QuizManagementView mounted');
  try {
    await fetchQuestionSets();
    console.log('QuestionSets loaded successfully:', questionSets.value);
  } catch (error) {
    console.error('Error in onMounted:', error);
  }
});
</script>

<style scoped>
.quiz-management {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

/* 페이지 헤더 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 1rem;
  color: white;
}

.header-content h1 {
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
  font-weight: 600;
}

.header-content p {
  margin: 0;
  opacity: 0.9;
  font-size: 1.1rem;
}

.create-btn {
  background: rgba(255, 255, 255, 0.2) !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  color: white !important;
}

.create-btn:hover {
  background: rgba(255, 255, 255, 0.3) !important;
}

/* 테이블 카드 */
.quiz-table-card {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-radius: 1rem;
  overflow: hidden;
}

/* 테이블 헤더 */
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.table-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.table-title h3 {
  margin: 0;
  color: #374151;
}

.table-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.search-input {
  min-width: 250px;
}

/* 테이블 스타일 */
.quiz-datatable {
  border-radius: 0.5rem;
  overflow: hidden;
}

.quiz-datatable .p-datatable-header {
  background: #f8fafc;
  border-bottom: 1px solid #e5e7eb;
}

.quiz-datatable .p-datatable-tbody > tr {
  cursor: pointer;
  transition: background-color 0.2s;
}

.quiz-datatable .p-datatable-tbody > tr:hover {
  background-color: #f3f4f6;
}

/* 셀 스타일 */
.description-cell {
  max-width: 200px;
}

.description-text {
  color: #374151;
  line-height: 1.4;
}

.no-description {
  color: #9ca3af;
  font-style: italic;
}

.created-date {
  color: #6b7280;
  font-size: 0.875rem;
}

/* 액션 버튼 */
.action-buttons {
  display: flex;
  gap: 0.25rem;
}

/* 빈 상태 */
.empty-state {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.empty-icon {
  font-size: 3rem;
  color: #d1d5db;
  margin-bottom: 1rem;
}

.empty-state h3 {
  margin: 0 0 0.5rem 0;
  color: #374151;
}

.empty-state p {
  margin: 0 0 1.5rem 0;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .quiz-management {
    padding: 0.5rem;
  }

  .page-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }

  .table-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .table-actions {
    justify-content: center;
  }

  .search-input {
    min-width: auto;
    width: 100%;
  }
}
</style>