<template>
  <Dialog
    v-model:visible="dialogVisible"
    modal
    header="새 퀴즈 생성"
    :style="{ width: '500px' }"
    :closable="true"
    :draggable="false"
    class="quiz-create-dialog"
  >
    <template #header>
      <div class="dialog-header">
        <i class="pi pi-plus-circle mr-2"></i>
        <span>AI 기반 퀴즈 생성</span>
      </div>
    </template>

    <div class="dialog-content">
      <Form
        v-slot="$form"
        :resolver="resolver"
        :initialValues="initialValues"
        @submit="onSubmit"
        class="quiz-form"
      >
        <!-- 그룹 선택 -->
        <div class="form-field">
          <label for="group_id" class="field-label">
            <i class="pi pi-users mr-1"></i>
            대상 그룹 *
          </label>
          <Dropdown
            name="group_id"
            v-model="formData.group_id"
            :options="groups"
            optionLabel="name"
            optionValue="id"
            placeholder="그룹을 선택하세요"
            fluid
            :loading="loadingGroups"
            class="group-dropdown"
          />
          <Message
            v-if="$form.group_id?.invalid"
            severity="error"
            size="small"
            variant="simple"
          >
            {{ $form.group_id.error?.message }}
          </Message>
        </div>

        <!-- 작성자 ID (임시) -->
        <div class="form-field">
          <label for="author_id" class="field-label">
            <i class="pi pi-user mr-1"></i>
            작성자 ID *
          </label>
          <InputNumber
            name="author_id"
            v-model="formData.author_id"
            placeholder="작성자 ID를 입력하세요"
            fluid
            :min="1"
          />
          <Message
            v-if="$form.author_id?.invalid"
            severity="error"
            size="small"
            variant="simple"
          >
            {{ $form.author_id.error?.message }}
          </Message>
        </div>

        <!-- 문제 수 -->
        <div class="form-field">
          <label for="num_questions" class="field-label">
            <i class="pi pi-question-circle mr-1"></i>
            문제 수 *
          </label>
          <InputNumber
            name="num_questions"
            v-model="formData.num_questions"
            placeholder="생성할 문제 수"
            fluid
            :min="1"
            :max="50"
            showButtons
            buttonLayout="horizontal"
            incrementButtonIcon="pi pi-plus"
            decrementButtonIcon="pi pi-minus"
          />
          <small class="field-help">
            사용자별로 다른 문제가 생성됩니다 (1-50개)
          </small>
          <Message
            v-if="$form.num_questions?.invalid"
            severity="error"
            size="small"
            variant="simple"
          >
            {{ $form.num_questions.error?.message }}
          </Message>
        </div>

        <!-- 언어 선택 -->
        <div class="form-field">
          <label for="language" class="field-label">
            <i class="pi pi-globe mr-1"></i>
            언어 *
          </label>
          <Dropdown
            name="language"
            v-model="formData.language"
            :options="['ko', 'en']"
            placeholder="언어를 선택하세요"
            fluid
          />
          <Message
            v-if="$form.language?.invalid"
            severity="error"
            size="small"
            variant="simple"
          >
            {{ $form.language.error?.message }}
          </Message>
        </div>

        <!-- 난이도 선택 -->
        <div class="form-field">
          <label for="difficulty" class="field-label">
            <i class="pi pi-sliders-h mr-1"></i>
            난이도 *
          </label>
          <Dropdown
            name="difficulty"
            v-model="formData.difficulty"
            :options="['상', '중', '하']"
            placeholder="난이도를 선택하세요"
            fluid
          />
          <Message
            v-if="$form.difficulty?.invalid"
            severity="error"
            size="small"
            variant="simple"
          >
            {{ $form.difficulty.error?.message }}
          </Message>
        </div>

        <!-- 퀴즈 세트 제목 -->
        <div class="form-field">
          <label for="title" class="field-label">
            <i class="pi pi-tag mr-1"></i>
            퀴즈 세트 제목 *
          </label>
          <InputText
            name="title"
            v-model="formData.title"
            placeholder="예: 신입사원 온보딩 퀴즈"
            fluid
          />
          <Message
            v-if="$form.title?.invalid"
            severity="error"
            size="small"
            variant="simple"
          >
            {{ $form.title.error?.message }}
          </Message>
        </div>

        <!-- 설명/요구사항 -->
        <div class="form-field">
          <label for="description" class="field-label">
            <i class="pi pi-file-text mr-1"></i>
            퀴즈 설명 및 요구사항 *
          </label>
          <Textarea
            name="description"
            v-model="formData.description"
            rows="4"
            placeholder="예: 중급 난이도의 객관식 문제, 업무 프로세스 중심"
            fluid
            class="description-textarea"
          />
          <small class="field-help">
            난이도, 문제 유형(객관식/주관식), 주제 범위 등을 상세히 입력하세요
          </small>
          <Message
            v-if="$form.description?.invalid"
            severity="error"
            size="small"
            variant="simple"
          >
            {{ $form.description.error?.message }}
          </Message>
        </div>

        <!-- 리소스 ID (선택사항) -->
        <div class="form-field">
          <label for="resource_id" class="field-label">
            <i class="pi pi-book mr-1"></i>
            참고 자료 (선택사항)
          </label>
          <InputNumber
            name="resource_id"
            v-model="formData.resource_id"
            placeholder="참고할 자료 ID (선택사항)"
            fluid
            :min="1"
          />
          <small class="field-help">
            특정 교육 자료를 기반으로 퀴즈를 생성하려면 입력하세요
          </small>
        </div>

        <!-- 예상 생성 정보 -->
        <div v-if="selectedGroup" class="generation-info">
          <h4><i class="pi pi-info-circle mr-1"></i>생성 예정 정보</h4>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">선택된 그룹:</span>
              <Tag :value="selectedGroup.name" severity="info" />
            </div>
            <div class="info-item">
              <span class="info-label">그룹 사용자 수:</span>
              <Badge :value="`${selectedGroup.user_count || 0}명`" severity="secondary" />
            </div>
            <div class="info-item">
              <span class="info-label">총 생성될 문제 수:</span>
              <Badge
                :value="`${(formData.num_questions || 0) * (selectedGroup.user_count || 0)}개`"
                severity="success"
              />
            </div>
          </div>
        </div>

        <!-- 버튼 영역 -->
        <div class="dialog-actions">
          <Button
            type="button"
            label="취소"
            severity="secondary"
            @click="closeDialog"
            :disabled="submitting"
          />
          <Button
            type="submit"
            label="퀴즈 생성"
            icon="pi pi-cog"
            :loading="submitting"
            loadingIcon="pi pi-spin pi-cog"
          />
        </div>
      </Form>
    </div>
  </Dialog>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { zodResolver } from '@primevue/forms/resolvers/zod';
import { useToast } from 'primevue/usetoast';
import { z } from 'zod';

// PrimeVue Components
import Dialog from 'primevue/dialog';
import Form from '@primevue/forms/form';
import Dropdown from 'primevue/dropdown';
import InputNumber from 'primevue/inputnumber';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Button from 'primevue/button';
import Message from 'primevue/message';
import Tag from 'primevue/tag';
import Badge from 'primevue/badge';

// Props & Emits
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: ''
  }
});

const emit = defineEmits(['update:visible', 'quiz-created']);

// Composables
const toast = useToast();

// 반응형 데이터
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
});

const groups = ref([]);
const loadingGroups = ref(false);
const submitting = ref(false);
const formData = ref({});

// 폼 초기값
const initialValues = ref({
  group_id: null,
  author_id: 1, // 임시 기본값
  num_questions: 5,
  language: 'ko',
  difficulty: '중',
  title: props.title, // Initialize title from prop
  description: '',
  resource_id: null
});

// 폼 검증 스키마
const resolver = ref(zodResolver(
  z.object({
    group_id: z.number().min(1, { message: '그룹을 선택해주세요.' }),
    author_id: z.number().min(1, { message: '작성자 ID를 입력해주세요.' }),
    num_questions: z.number()
      .min(1, { message: '최소 1개의 문제가 필요합니다.' })
      .max(50, { message: '최대 50개까지 생성 가능합니다.' }),
    language: z.string(),
    difficulty: z.string(),
    title: z.string().min(1, { message: '퀴즈 세트 제목을 입력해주세요.' }).max(255, { message: '최대 255자까지 입력 가능합니다.' }), // Add title validation
    description: z.string()
      .min(10, { message: '최소 10자 이상 입력해주세요.' })
      .max(1000, { message: '최대 1000자까지 입력 가능합니다.' }),
    resource_id: z.number().min(1).optional().nullable()
  })
));

// 계산된 속성
const selectedGroup = computed(() => {
  if (!formData.value.group_id) return null;
  return groups.value.find(g => g.id === formData.value.group_id);
});

// API 호출 함수들
const fetchGroups = async () => {
  loadingGroups.value = true;
  try {
    const response = await fetch('http://localhost:8000/api/groups/with-users');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    groups.value = data;

  } catch (error) {
    console.error('그룹 목록 조회 실패:', error);
    toast.add({
      severity: 'error',
      summary: '오류',
      detail: '그룹 목록을 불러오는데 실패했습니다.',
      life: 3000
    });
  } finally {
    loadingGroups.value = false;
  }
};

const createQuiz = async (formData) => {
  try {
    const requestData = {
      group_id: formData.group_id,
      author_id: formData.author_id,
      num_questions: formData.num_questions,
      language: formData.language,
      difficulty: formData.difficulty,
      title: formData.title, // Include title here
      description: formData.description,
      resource_id: formData.resource_id || undefined
    };

    // 디버깅을 위해 콘솔에 전송될 데이터 출력
    console.log("API 요청 데이터:", JSON.stringify(requestData, null, 2));

    const response = await fetch('http://localhost:8000/api/question_sets/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || '퀴즈 생성 실패');
    }

    const result = await response.json();
    return result;

  } catch (error) {
    console.error('퀴즈 생성 실패:', error);
    throw error;
  }
};

// 이벤트 핸들러들
const onSubmit = async ({ valid }) => {
  if (!valid) return;

  submitting.value = true;
  try {
    const result = await createQuiz(formData.value);

    toast.add({
      severity: 'success',
      summary: '생성 완료',
      detail: `퀴즈가 성공적으로 생성되었습니다. (${result.questions_created}개 문제)`,
      life: 5000
    });

    // 부모 컴포넌트에 새로 생성된 퀴즈 정보 전달
    emit('quiz-created', result.data.question_set);

    closeDialog();

  } catch (error) {
    toast.add({
      severity: 'error',
      summary: '생성 실패',
      detail: '퀴즈 생성 중 오류가 발생했습니다.',
      life: 3000
    });
  } finally {
    submitting.value = false;
  }
};

const closeDialog = () => {
  dialogVisible.value = false;
  // 폼 리셋
  formData.value = { ...initialValues.value };
};

// 감시자
watch(dialogVisible, (newValue) => {
  if (newValue) {
    fetchGroups();
  }
});

// 컴포넌트 마운트 시
onMounted(() => {
  formData.value = { ...initialValues.value };
});
</script>

<style scoped>
.quiz-create-dialog {
  border-radius: 1rem;
  overflow: hidden;
}

.dialog-header {
  display: flex;
  align-items: center;
  font-size: 1.1rem;
  font-weight: 600;
  color: #374151;
}

.dialog-content {
  padding: 0;
}

.quiz-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* 폼 필드 스타일 */
.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.field-label {
  display: flex;
  align-items: center;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.25rem;
}

.field-help {
  color: #6b7280;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.group-dropdown {
  min-height: 2.5rem;
}

.description-textarea {
  resize: vertical;
  min-height: 100px;
}

/* 생성 정보 섹션 */
.generation-info {
  background: #f8fafc;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
  margin-top: 0.5rem;
}

.generation-info h4 {
  margin: 0 0 1rem 0;
  color: #374151;
  font-size: 1rem;
  display: flex;
  align-items: center;
}

.info-grid {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-label {
  color: #6b7280;
  font-size: 0.875rem;
}

/* 액션 버튼 */
.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

/* 반응형 디자인 */
@media (max-width: 640px) {
  .quiz-create-dialog {
    width: 95vw !important;
    margin: 1rem;
  }

  .info-grid {
    gap: 0.5rem;
  }

  .info-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }

  .dialog-actions {
    flex-direction: column;
  }

  .dialog-actions button {
    width: 100%;
  }
}

/* 폼 에러 메시지 스타일 */
.p-message.p-message-error {
  margin-top: 0.25rem;
}

/* 로딩 상태 스타일 */
.p-button[loading] {
  pointer-events: none;
}
</style>