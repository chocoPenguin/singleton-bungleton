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
            :label="isSubmitting ? 'AI가 퀴즈를 생성하고 있습니다...' : 'Generate Questions'"
            icon="pi pi-plus"
            :loading="isSubmitting"
            :disabled="isSubmitting"
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
import { getAllGroups, getGroupsByAuthor } from '../../api/groups.js';
import { getAllAuthors } from '../../api/auth.js';
import { createQuestionSet, startQuestionGeneration, generateQuizWithAI } from '../../api/questions.js';
import { getCurrentUserFromToken } from '../../utils/auth.js';
import { getCurrentUser } from '../../api/users.js';

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
    let response;

    // 현재 사용자의 그룹만 조회
    const allAuthorsResponse = await getAllAuthors();
    const currentUserInfo = getCurrentUserFromToken();

    const currentAuthor = allAuthorsResponse.data.find(author => author.email === currentUserInfo.email);

    if (currentAuthor) {
      // 현재 author의 그룹만 조회
      response = await getGroupsByAuthor(currentAuthor.id);
      console.log('Groups for current author in CreateView:', response.data);
    } else {
      console.warn('Current author not found in CreateView, showing all groups');
      response = await getAllGroups();
    }

    groups.value = response.data.map(group => ({
      id: group.id,
      name: group.name,
      description: group.description || group.memo
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
    const userResponse = await getCurrentUser();
    const currentUser = userResponse.data;

    if (!currentUser || !currentUser.id) {
      throw new Error('User authentication required');
    }

    // Prepare quiz generation data for AI Foundry Agent
    const quizData = {
      group_id: form.value.selectedGroup,
      author_id: currentUser.id,
      num_questions: form.value.questionsPerPerson,
      language: form.value.language,
      difficulty: form.value.difficulty,
      description: form.value.instructions.trim(),
      title: generateAutoTitle(), // Add title here
      resource_id: null // Optional
    };

    // Generate quiz using AI Foundry Agent
    const response = await generateQuizWithAI(quizData);

    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: `Quiz generated successfully! Created ${response.data.questions_created} questions.`,
      life: 3000
    });

    // Navigate to history page
    router.push('/questions/history');

  } catch (error) {
    console.error('Failed to generate quiz:', error);

    let errorMessage = 'Failed to generate quiz. Please try again.';
    if (error.message === 'User authentication required') {
      errorMessage = 'User authentication required. Please log in again.';
    } else if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    } else if (error.response?.data?.message) {
      errorMessage = error.response.data.message;
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

.loading-message {
  display: block;
  text-align: center;
  color: #6b7280;
  margin-top: 0.75rem;
  font-style: italic;
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
