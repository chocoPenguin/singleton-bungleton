<template>
  <Dialog
    v-model:visible="dialogVisible"
    :modal="true"
    :header="isEdit ? 'Edit Resource' : 'Create New Resource'"
    :style="{ width: '600px' }"
    :breakpoints="{ '960px': '75vw', '641px': '90vw' }"
    @hide="onHide"
  >
    <form @submit.prevent="handleSubmit" class="resource-form">
      <!-- Resource Name -->
      <div class="form-group">
        <label for="name" class="form-label">Resource Name <span class="required">*</span></label>
        <InputText
          id="name"
          v-model="formData.name"
          :class="{ 'p-invalid': errors.name }"
          placeholder="Enter resource name"
          required
        />
        <small v-if="errors.name" class="error-message">{{ errors.name }}</small>
      </div>

      <!-- Resource Type -->
      <div class="form-group">
        <label for="resourceType" class="form-label">Resource Type <span class="required">*</span></label>
        <Dropdown
          id="resourceType"
          v-model="formData.resource_type"
          :options="resourceTypeOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="Select resource type"
          :class="{ 'p-invalid': errors.resource_type }"
          required
        />
        <small v-if="errors.resource_type" class="error-message">{{ errors.resource_type }}</small>
      </div>

      <!-- Connection Key -->
      <div class="form-group">
        <label for="connectionKey" class="form-label">Connection Key <span class="required">*</span></label>
        <InputText
          id="connectionKey"
          v-model="formData.connection_key"
          :class="{ 'p-invalid': errors.connection_key }"
          placeholder="Enter connection key (Agent ID, API Key, etc.)"
          required
        />
        <small v-if="errors.connection_key" class="error-message">{{ errors.connection_key }}</small>
      </div>

      <!-- Description -->
      <div class="form-group">
        <label for="description" class="form-label">Description</label>
        <Textarea
          id="description"
          v-model="formData.description"
          rows="4"
          placeholder="Enter description (used in quiz generation prompts)"
          :class="{ 'p-invalid': errors.description }"
        />
        <small class="form-help">This description will be included in AI prompts when generating quizzes</small>
        <small v-if="errors.description" class="error-message">{{ errors.description }}</small>
      </div>

      <!-- File Path (Optional) -->
      <div class="form-group">
        <label for="filePath" class="form-label">File Path (Optional)</label>
        <InputText
          id="filePath"
          v-model="formData.file_path"
          :class="{ 'p-invalid': errors.file_path }"
          placeholder="Enter file path if applicable"
        />
        <small v-if="errors.file_path" class="error-message">{{ errors.file_path }}</small>
      </div>
    </form>

    <template #footer>
      <Button
        label="Cancel"
        severity="secondary"
        text
        @click="onCancel"
      />
      <Button
        :label="isEdit ? 'Update' : 'Create'"
        :loading="loading"
        @click="handleSubmit"
      />
    </template>
  </Dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Dropdown from 'primevue/dropdown';
import Button from 'primevue/button';
import { getResourceTypeOptions } from '../../api/resources.js';

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  resource: {
    type: Object,
    default: null
  }
});

// Emits
const emit = defineEmits(['update:visible', 'save']);

// State
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
});

const loading = ref(false);
const errors = reactive({});

const formData = reactive({
  name: '',
  resource_type: '',
  connection_key: '',
  description: '',
  file_path: '',
  type: 'external'
});

// Computed
const isEdit = computed(() => !!props.resource?.id);
const resourceTypeOptions = ref(getResourceTypeOptions());

// Methods
const resetForm = () => {
  formData.name = '';
  formData.resource_type = '';
  formData.connection_key = '';
  formData.description = '';
  formData.file_path = '';
  formData.type = 'external';
  Object.keys(errors).forEach(key => delete errors[key]);
};

const populateForm = (resource) => {
  if (resource) {
    formData.name = resource.name || '';
    formData.resource_type = resource.resource_type || '';
    formData.connection_key = resource.connection_key || '';
    formData.description = resource.description || '';
    formData.file_path = resource.file_path || '';
    formData.type = resource.type || 'external';
  }
};

const validateForm = () => {
  Object.keys(errors).forEach(key => delete errors[key]);

  if (!formData.name?.trim()) {
    errors.name = 'Resource name is required';
  }

  if (!formData.resource_type) {
    errors.resource_type = 'Resource type is required';
  }

  if (!formData.connection_key?.trim()) {
    errors.connection_key = 'Connection key is required';
  }

  return Object.keys(errors).length === 0;
};

const handleSubmit = async () => {
  if (!validateForm()) {
    return;
  }

  loading.value = true;
  try {
    const resourceData = {
      name: formData.name.trim(),
      resource_type: formData.resource_type,
      connection_key: formData.connection_key.trim(),
      description: formData.description?.trim() || null,
      file_path: formData.file_path?.trim() || null,
      type: formData.type
    };

    if (isEdit.value) {
      resourceData.id = props.resource.id;
    }

    emit('save', resourceData);
    dialogVisible.value = false;
  } catch (error) {
    console.error('Error submitting form:', error);
  } finally {
    loading.value = false;
  }
};

const onCancel = () => {
  dialogVisible.value = false;
};

const onHide = () => {
  resetForm();
};

// Watch for resource changes
watch(() => props.resource, (newResource) => {
  if (newResource) {
    populateForm(newResource);
  } else {
    resetForm();
  }
}, { immediate: true });

// Watch for dialog visibility changes
watch(dialogVisible, (visible) => {
  if (visible && !isEdit.value) {
    resetForm();
  }
});
</script>

<style scoped lang="scss">
.resource-form {
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
}

.required {
  color: #ef4444;
}

.error-message {
  color: #ef4444;
  font-size: 0.75rem;
  margin-top: 0.25rem;
}

.form-help {
  color: #6b7280;
  font-size: 0.75rem;
  font-style: italic;
}

:deep(.p-inputtext),
:deep(.p-dropdown),
:deep(.p-inputtextarea) {
  width: 100%;
}

:deep(.p-invalid) {
  border-color: #ef4444;
}

:deep(.p-dialog-footer) {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e5e7eb;
  margin: 1rem -1.5rem -1.5rem -1.5rem;
}
</style>