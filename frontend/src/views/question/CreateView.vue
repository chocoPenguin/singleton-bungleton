<template>
  <div class="create-view">
    <div class="page-header">
      <h1 class="page-title">Create Question Set</h1>
      <p class="page-description">Generate questions for your group members</p>
    </div>

    <div class="form-container">
      <form @submit.prevent="handleSubmit" class="create-form">
        <!-- Quiz Set Title -->
        <div class="form-group">
          <label for="title" class="form-label">
            Quiz Set Title
            <span class="optional-label">(Optional)</span>
          </label>
          <InputText
            id="title"
            v-model="form.title"
            placeholder="Enter quiz set title (auto-generated if empty)"
            class="form-input"
          />
          <small class="form-help">
            If empty, title will be auto-generated with current date and time
          </small>
        </div>

        <!-- Group Selection -->
        <div class="form-group">
          <label for="group" class="form-label required">
            Select Group
          </label>
          <Dropdown
            id="group"
            v-model="form.selectedGroup"
            :options="groups"
            optionLabel="name"
            optionValue="id"
            placeholder="Search and select a group"
            filter
            filterPlaceholder="Search groups..."
            :loading="groupsLoading"
            class="form-input"
            emptyMessage="No groups found"
            emptyFilterMessage="No groups match your search"
          />
        </div>

        <!-- Questions per Person -->
        <div class="form-group">
          <label for="questionsPerPerson" class="form-label required">
            Questions per Person
          </label>
          <InputNumber
            id="questionsPerPerson"
            v-model="form.questionsPerPerson"
            :min="1"
            :max="50"
            placeholder="Enter number of questions"
            class="form-input"
          />
        </div>

        <!-- Language Selection -->
        <div class="form-group">
          <label for="language" class="form-label required">
            Language
          </label>
          <Dropdown
            id="language"
            v-model="form.language"
            :options="languages"
            optionLabel="label"
            optionValue="value"
            placeholder="Select language"
            class="form-input"
          />
        </div>

        <!-- Difficulty Level -->
        <div class="form-group">
          <label for="difficulty" class="form-label required">
            Difficulty Level
          </label>
          <Dropdown
            id="difficulty"
            v-model="form.difficulty"
            :options="difficulties"
            optionLabel="label"
            optionValue="value"
            placeholder="Select difficulty"
            class="form-input"
          />
        </div>

        <!-- Question Scope / Instructions -->
        <div class="form-group">
          <label for="instructions" class="form-label">
            Question Scope & Instructions
            <span class="optional-label">(Optional)</span>
          </label>
          <Textarea
            id="instructions"
            v-model="form.instructions"
            placeholder="Enter question scope, topics to focus on, specific requirements, or any special instructions for question generation..."
            :rows="5"
            class="form-input"
          />
          <small class="form-help">
            Provide specific topics, question types, or any constraints for question generation
          </small>
        </div>

        <!-- Submit Button -->
        <div class="form-actions">
          <Button
            type="submit"
            label="Generate Questions"
            icon="pi pi-plus"
            :loading="isSubmitting"
            class="submit-button"
            size="large"
          />
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import Dropdown from 'primevue/dropdown';
import Textarea from 'primevue/textarea';
import Button from 'primevue/button';
import { getAllGroups } from '../../api/groups.js';
import { createQuestionSet, startQuestionGeneration } from '../../api/questions.js';
import { getCurrentUserFromToken } from '../../utils/auth.js';

const router = useRouter();
const toast = useToast();

// Form data
const form = ref({
  title: '',
  selectedGroup: null,
  questionsPerPerson: 5,
  language: 'ko',
  difficulty: 'medium',
  instructions: ''
});

// Options
const languages = ref([
  { label: '한국어', value: 'ko' },
  { label: 'English', value: 'en' },
  { label: 'Tiếng Việt', value: 'vi' },
  { label: '日本語', value: 'ja' }
]);

const difficulties = ref([
  { label: '쉬움', value: 'easy' },
  { label: '보통', value: 'medium' },
  { label: '어려움', value: 'hard' }
]);

// State
const groups = ref([]);
const groupsLoading = ref(false);
const isSubmitting = ref(false);

// Load groups
const fetchGroups = async () => {
  groupsLoading.value = true;
  try {
    const response = await getAllGroups();
    groups.value = response.data.map(group => ({
      id: group.id,
      name: group.name,
      description: group.description
    }));
  } catch (error) {
    console.error('Failed to fetch groups:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load groups. Please try again.',
      life: 5000
    });
  } finally {
    groupsLoading.value = false;
  }
};

// Form validation
const validateForm = () => {
  if (!form.value.selectedGroup) {
    toast.add({
      severity: 'warn',
      summary: 'Validation Error',
      detail: 'Please select a group.',
      life: 3000
    });
    return false;
  }

  if (!form.value.questionsPerPerson || form.value.questionsPerPerson < 1) {
    toast.add({
      severity: 'warn',
      summary: 'Validation Error',
      detail: 'Please enter a valid number of questions per person.',
      life: 3000
    });
    return false;
  }

  if (!form.value.language) {
    toast.add({
      severity: 'warn',
      summary: 'Validation Error',
      detail: 'Please select a language.',
      life: 3000
    });
    return false;
  }

  if (!form.value.difficulty) {
    toast.add({
      severity: 'warn',
      summary: 'Validation Error',
      detail: 'Please select a difficulty level.',
      life: 3000
    });
    return false;
  }

  return true;
};

// Generate auto title if empty
const generateAutoTitle = () => {
  if (!form.value.title.trim()) {
    const now = new Date();
    const dateStr = now.toLocaleDateString('ko-KR');
    const timeStr = now.toLocaleTimeString('ko-KR', {
      hour: '2-digit',
      minute: '2-digit'
    });
    return `Quiz Set ${dateStr} ${timeStr}`;
  }
  return form.value.title.trim();
};

// Handle form submission
const handleSubmit = async () => {
  if (!validateForm()) return;

  isSubmitting.value = true;
  try {
    // Get current user info
    const userInfo = getCurrentUserFromToken();
    const authorEmail = userInfo?.email;

    if (!authorEmail) {
      throw new Error('User authentication required');
    }

    // Prepare question set data
    const questionSetData = {
      title: generateAutoTitle(),
      group_id: form.value.selectedGroup,
      questions_per_person: form.value.questionsPerPerson,
      language: form.value.language,
      difficulty: form.value.difficulty,
      instructions: form.value.instructions.trim() || null,
      author_email: authorEmail,
      status: 'pending' // Will be updated when generation starts
    };

    // Create question set
    const response = await createQuestionSet(questionSetData);
    const questionSetId = response.data.id;

    // TODO: Start question generation (when LLM is ready)
    // await startQuestionGeneration(questionSetId);

    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Question set created successfully!',
      life: 3000
    });

    // Navigate to history page
    router.push('/questions/history');

  } catch (error) {
    console.error('Failed to create question set:', error);

    let errorMessage = 'Failed to create question set. Please try again.';
    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    }

    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: errorMessage,
      life: 5000
    });
  } finally {
    isSubmitting.value = false;
  }
};

// Initialize component
onMounted(() => {
  fetchGroups();
});
</script>

<style scoped>
.create-view {
  padding: 2rem;
  max-width: 800px;
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

.form-container {
  background: white;
  border-radius: 0.75rem;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.create-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-label.required::after {
  content: '*';
  color: #dc2626;
}

.optional-label {
  font-weight: 400;
  color: #6b7280;
  font-size: 0.75rem;
}

.form-input {
  width: 100%;
}

.form-help {
  color: #6b7280;
  font-size: 0.75rem;
}

.form-actions {
  margin-top: 1rem;
  display: flex;
  justify-content: center;
}

.submit-button {
  padding: 0.75rem 2rem;
}

/* PrimeVue component overrides */
:deep(.p-inputtext) {
  width: 100%;
}

:deep(.p-dropdown) {
  width: 100%;
}

:deep(.p-inputnumber) {
  width: 100%;
}

:deep(.p-inputnumber-input) {
  width: 100%;
}

:deep(.p-inputtextarea) {
  width: 100%;
  resize: vertical;
  min-height: 120px;
}
</style>