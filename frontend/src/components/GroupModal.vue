<template>
  <Dialog
    v-model:visible="visible"
    modal
    :header="isEdit ? 'Edit Group' : 'New Group'"
    :style="{ width: '32rem' }"
    :breakpoints="{ '1199px': '75vw', '575px': '90vw' }"
    class="custom-dialog"
  >
    <div class="modal-content">
      <div class="form-field">
        <label for="name" class="field-label">Group Name *</label>
        <InputText
          id="name"
          v-model.trim="groupData.name"
          required="true"
          autofocus
          :invalid="submitted && !groupData.name"
          placeholder="Enter group name"
          class="field-input"
        />
        <small v-if="submitted && !groupData.name" class="field-error">
          Group name is required.
        </small>
      </div>

      <div class="form-field">
        <label for="language" class="field-label">Language *</label>
        <Dropdown
          id="language"
          v-model="groupData.language"
          :options="languages"
          optionLabel="label"
          optionValue="value"
          placeholder="Select language"
          required="true"
          :invalid="submitted && !groupData.language"
          class="field-input"
        />
        <small v-if="submitted && !groupData.language" class="field-error">
          Language is required.
        </small>
      </div>

      <div class="form-field">
        <label for="memo" class="field-label">Memo</label>
        <Textarea
          id="memo"
          v-model="groupData.memo"
          rows="4"
          cols="30"
          placeholder="Enter memo (optional)"
          class="field-input"
        />
      </div>
    </div>

    <template #footer>
      <div class="modal-footer">
        <Button
          label="Cancel"
          icon="pi pi-times"
          class="cancel-button"
          @click="hideDialog"
        />
        <Button
          :label="isEdit ? 'Update' : 'Save'"
          icon="pi pi-check"
          class="save-button"
          @click="saveGroup"
          :loading="saving"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed } from 'vue';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Dropdown from 'primevue/dropdown';
import Button from 'primevue/button';

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  group: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['update:visible', 'save']);

const visible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
});

const submitted = ref(false);
const saving = ref(false);

const groupData = ref({
  name: '',
  language: '',
  memo: ''
});

const languages = ref([
  { label: '한국어', value: 'ko' },
  { label: 'English', value: 'en' },
  { label: 'Tiếng Việt', value: 'vi' },
  { label: '日本語', value: 'ja' }
]);

const isEdit = computed(() => !!props.group?.id);

const resetForm = () => {
  groupData.value = {
    name: props.group?.name || '',
    language: props.group?.language || '',
    memo: props.group?.memo || ''
  };
  submitted.value = false;
};

const hideDialog = () => {
  visible.value = false;
  setTimeout(resetForm, 100);
};

const saveGroup = async () => {
  submitted.value = true;

  if (!groupData.value.name?.trim() || !groupData.value.language) {
    return;
  }

  saving.value = true;

  try {
    const payload = {
      ...groupData.value,
      name: groupData.value.name.trim()
    };

    if (isEdit.value) {
      payload.id = props.group.id;
    }

    emit('save', payload);
    hideDialog();
  } finally {
    saving.value = false;
  }
};

// Watch for prop changes to reset form
import { watch } from 'vue';
watch(() => props.visible, (newVal) => {
  if (newVal) {
    resetForm();
  }
});
</script>

<style scoped>
/* Modal Content */
.modal-content {
  padding: 1rem 0;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.field-label {
  font-weight: 600;
  color: #111827;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.field-input {
  width: 100% !important;
}

.field-error {
  color: #dc2626 !important;
  font-size: 0.75rem;
  margin-top: 0.25rem;
}

/* Modal Footer */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 1rem;
}

.cancel-button {
  background-color: transparent !important;
  border-color: #d1d5db !important;
  color: #6b7280 !important;
}

.cancel-button:hover {
  background-color: #f9fafb !important;
  border-color: #9ca3af !important;
  color: #374151 !important;
}

.save-button {
  background-color: #475569 !important;
  border-color: #475569 !important;
  color: white !important;
}

.save-button:hover {
  background-color: #334155 !important;
  border-color: #334155 !important;
}

/* Dialog Customization */
:deep(.p-dialog) {
  background-color: #ffffff;
  border-radius: 0.75rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

:deep(.p-dialog-header) {
  background-color: #ffffff;
  border-bottom: 1px solid #e2e8f0;
  padding: 1.5rem;
  border-radius: 0.75rem 0.75rem 0 0;
}

:deep(.p-dialog-title) {
  font-weight: 600;
  color: #111827;
}

:deep(.p-dialog-content) {
  background-color: #ffffff;
  padding: 0 1.5rem;
}

:deep(.p-dialog-footer) {
  background-color: #ffffff;
  border-top: 1px solid #e2e8f0;
  padding: 1.5rem;
  border-radius: 0 0 0.75rem 0.75rem;
}

/* Input Field Styling */
:deep(.p-inputtext) {
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  padding: 0.75rem;
  background-color: white;
  color: #111827;
  transition: border-color 0.2s, box-shadow 0.2s;
}

:deep(.p-inputtext:focus) {
  border-color: #475569;
  box-shadow: 0 0 0 3px rgba(71, 85, 105, 0.1);
}

:deep(.p-inputtext::placeholder) {
  color: #9ca3af;
}

:deep(.p-dropdown) {
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  background-color: white;
  color: #111827;
}

:deep(.p-dropdown:focus-within) {
  border-color: #475569;
  box-shadow: 0 0 0 3px rgba(71, 85, 105, 0.1);
}

:deep(.p-dropdown-label) {
  color: #111827;
}

:deep(.p-inputtextarea) {
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  padding: 0.75rem;
  background-color: white;
  color: #111827;
  font-family: inherit;
  resize: vertical;
}

:deep(.p-inputtextarea:focus) {
  border-color: #475569;
  box-shadow: 0 0 0 3px rgba(71, 85, 105, 0.1);
}

:deep(.p-inputtextarea::placeholder) {
  color: #9ca3af;
}
</style>