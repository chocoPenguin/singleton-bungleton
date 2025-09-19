<template>
  <div class="resources-view">
    <div class="page-header">
      <h1 class="page-title">{{ userName }}'s Resource Management</h1>
    </div>

    <div class="resources-content">
      <div class="table-header">
        <Button
          label="New"
          icon="pi pi-plus"
          class="new-button"
          @click="openNewResource"
        />
      </div>
      <DataTable
        :value="resources"
        :paginator="true"
        :rows="10"
        :loading="loading"
        class="resources-table"
        responsiveLayout="scroll"
        stripedRows
      >
        <Column field="name" header="Resource Name" sortable>
          <template #body="slotProps">
            <span class="resource-name">
              {{ slotProps.data.name }}
            </span>
          </template>
        </Column>
        <Column field="resource_type" header="Type" sortable>
          <template #body="slotProps">
            <Tag
              :value="getResourceTypeLabel(slotProps.data.resource_type)"
              :severity="getResourceTypeSeverity(slotProps.data.resource_type)"
            />
          </template>
        </Column>
        <Column field="connection_key" header="Connection Key">
          <template #body="slotProps">
            <span class="connection-key">
              {{ truncateKey(slotProps.data.connection_key) }}
            </span>
          </template>
        </Column>
        <Column field="description" header="Description">
          <template #body="slotProps">
            <span
              class="description-text"
              :title="slotProps.data.description"
            >
              {{ truncateDescription(slotProps.data.description) }}
            </span>
          </template>
        </Column>
        <Column field="file_path" header="File Path">
          <template #body="slotProps">
            <span
              v-if="slotProps.data.file_path"
              class="file-path"
              :title="slotProps.data.file_path"
            >
              {{ truncateFilePath(slotProps.data.file_path) }}
            </span>
            <span v-else class="no-file">-</span>
          </template>
        </Column>
        <Column field="created_at" header="Created" sortable>
          <template #body="slotProps">
            {{ formatDate(slotProps.data.created_at) }}
          </template>
        </Column>
        <Column header="Actions">
          <template #body="slotProps">
            <div class="action-buttons">
              <Button
                icon="pi pi-pencil"
                severity="info"
                text
                @click="editResource(slotProps.data)"
                v-tooltip="'Edit'"
              />
              <Button
                icon="pi pi-trash"
                severity="danger"
                text
                @click="deleteResource(slotProps.data)"
                v-tooltip="'Delete'"
              />
            </div>
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Resource Modal -->
    <ResourceModal
      v-model:visible="showResourceModal"
      :resource="selectedResourceForEdit"
      @save="handleSaveResource"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Tag from 'primevue/tag';
import {
  getAllResources,
  createResource,
  updateResource,
  deleteResource as deleteResourceAPI,
  getResourcesByAuthor,
  getResourceTypeLabel
} from '../../api/resources.js';
import { getAllAuthors } from '../../api/auth.js';
import { getCurrentUserFromToken } from '../../utils/auth.js';
import ResourceModal from '../../components/admin/ResourceModal.vue';
import 'primeicons/primeicons.css'

// 반응형 데이터
const userName = ref('Loading...');
const resources = ref([]);
const loading = ref(true);

// Modal state
const showResourceModal = ref(false);
const selectedResourceForEdit = ref(null);

const toast = useToast();
const confirm = useConfirm();

// 사용자 정보 가져오기
const fetchCurrentUser = async () => {
  try {
    // JWT 토큰에서 사용자 정보 추출
    const userFromToken = getCurrentUserFromToken();
    if (userFromToken) {
      // 토큰에서 이메일 추출하여 이름으로 사용 (임시)
      const emailParts = userFromToken.email.split('@');
      userName.value = emailParts[0]; // 이메일의 @ 앞부분을 이름으로 사용
    }
  } catch (error) {
    console.error('사용자 정보 가져오기 실패:', error);
    userName.value = 'Guest';
  }
};

// 리소스 데이터 가져오기
const fetchResources = async () => {
  loading.value = true;
  try {
    let response;

    // 현재 사용자의 리소스만 조회
    const allAuthorsResponse = await getAllAuthors();
    const currentUserInfo = getCurrentUserFromToken();
    console.log('Current user info:', currentUserInfo);

    const currentAuthor = allAuthorsResponse.data.find(author => author.email === currentUserInfo.email);
    console.log('Found current author:', currentAuthor);

    if (currentAuthor) {
      // 현재 author의 리소스만 조회
      response = await getResourcesByAuthor(currentAuthor.id);
      console.log('Resources for current author:', response.data);
    } else {
      console.warn('Current author not found, showing all resources');
      response = await getAllResources();
    }

    console.log('Resources API response:', response.data); // 디버깅용

    // 백엔드에서 받은 데이터를 프론트엔드 형식에 맞게 변환
    resources.value = response.data.map((resource) => ({
      id: resource.id,
      name: resource.name,
      resource_type: resource.resource_type,
      connection_key: resource.connection_key,
      description: resource.description || 'No description',
      file_path: resource.file_path,
      type: resource.type,
      created_at: new Date(resource.created_at)
    }));
  } catch (error) {
    console.error('리소스 데이터 가져오기 실패:', error);

    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load resources. Please try again.',
      life: 5000
    });

    // 에러 시 빈 배열로 설정
    resources.value = [];
  } finally {
    loading.value = false;
  }
};

// 날짜 포맷팅
const formatDate = (value) => {
  if (!value) return "";
  const date = new Date(value);
  if (isNaN(date.getTime())) return value;
  return date.toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit"
  });
};

// 리소스 타입 severity 반환
const getResourceTypeSeverity = (type) => {
  switch (type) {
    case 'SP': return 'info';      // SharePoint
    case 'LS': return 'secondary'; // Local Storage
    case 'GC': return 'success';   // Google Cloud
    case 'S3': return 'warning';   // AWS S3
    default: return 'contrast';
  }
};

// 텍스트 자르기 함수들
const truncateKey = (key) => {
  if (!key) return '-';
  return key.length > 20 ? key.substring(0, 20) + '...' : key;
};

const truncateDescription = (description) => {
  if (!description) return '-';
  return description.length > 50 ? description.substring(0, 50) + '...' : description;
};

const truncateFilePath = (filePath) => {
  if (!filePath) return '-';
  return filePath.length > 30 ? '...' + filePath.substring(filePath.length - 30) : filePath;
};

// Modal handlers
const openNewResource = () => {
  selectedResourceForEdit.value = null;
  showResourceModal.value = true;
};

const handleSaveResource = async (resourceData) => {
  try {
    if (resourceData.id) {
      // Edit existing resource
      await updateResource(resourceData.id, resourceData);
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Resource updated successfully',
        life: 3000
      });
    } else {
      // Create new resource
      const userInfo = getCurrentUserFromToken();

      if (!userInfo?.email) {
        throw new Error('User authentication required');
      }

      // 현재 사용자의 이메일과 매칭되는 author ID 찾기
      console.log('User info for resource creation:', userInfo);

      const allAuthorsResponse = await getAllAuthors();
      console.log('All authors response:', allAuthorsResponse.data);

      const currentAuthor = allAuthorsResponse.data.find(author => {
        console.log('Comparing author email:', author.email, 'with user email:', userInfo.email);
        return author.email === userInfo.email;
      });

      console.log('Found current author:', currentAuthor);

      if (!currentAuthor) {
        throw new Error('Current author not found in database');
      }

      const payload = {
        name: resourceData.name,
        resource_type: resourceData.resource_type,
        connection_key: resourceData.connection_key,
        description: resourceData.description || null,
        file_path: resourceData.file_path || null,
        author_id: currentAuthor.id,
        type: resourceData.type || 'external'
      };

      console.log('Creating resource with payload:', payload);

      await createResource(payload);
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Resource created successfully',
        life: 3000
      });
    }

    // Refresh resources list
    await fetchResources();
  } catch (error) {
    console.error('Failed to save resource:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to save resource. Please try again.',
      life: 5000
    });
  }
};

// 리소스 편집
const editResource = (resource) => {
  selectedResourceForEdit.value = resource;
  showResourceModal.value = true;
};

// 리소스 삭제
const deleteResource = (resource) => {
  confirm.require({
    message: `Are you sure you want to delete the resource "${resource.name}"?`,
    header: 'Delete Confirmation',
    icon: 'pi pi-exclamation-triangle',
    rejectClass: 'p-button-secondary p-button-outlined',
    rejectLabel: 'Cancel',
    acceptLabel: 'Delete',
    accept: async () => {
      try {
        console.log('Deleting resource with ID:', resource.id);

        // 리소스 삭제 API 호출
        await deleteResourceAPI(resource.id);

        console.log('Resource deleted successfully');

        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Resource deleted successfully',
          life: 3000
        });

        // 리소스 목록 새로고침
        await fetchResources();
      } catch (error) {
        console.error('Failed to delete resource:', error);
        console.error('Error details:', error.response?.data);

        let errorMessage = 'Failed to delete resource. Please try again.';
        if (error.response?.data?.detail) {
          errorMessage = error.response.data.detail;
        }

        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: errorMessage,
          life: 5000
        });
      }
    }
  });
};

// 컴포넌트 마운트 시 데이터 로드
onMounted(() => {
  fetchCurrentUser();
  fetchResources();
});
</script>

<style scoped lang="scss">
@use '@/assets/styles/datatable.scss';

.page-header {
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.table-header {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-bottom: 1rem;
}

.new-button {
  background-color: #242b35ff !important;
  border-color: #242b35ff !important;
  color: white !important;
  font-weight: 500;
  transition: all 0.2s;
}

.new-button:hover {
  background-color: #475569 !important;
  border-color: #475569 !important;
}

.new-button:not(:disabled):hover {
  background-color: #475569 !important;
  border-color: #475569 !important;
}

.new-button:focus {
  box-shadow: 0 0 0 3px rgba(71, 85, 105, 0.2);
}

.new-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.resource-name {
  font-weight: 600;
  color: #374151;
}

.connection-key {
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
  color: #6b7280;
}

.description-text {
  color: #374151;
}

.file-path {
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
  color: #6b7280;
}

.no-file {
  color: #9ca3af;
  font-style: italic;
}

:deep(.resources-table) {
  .p-datatable-tbody > tr > td {
    padding: 0.75rem;
    vertical-align: middle;
  }
}

:deep(.p-tag) {
  font-size: 0.75rem;
  font-weight: 600;
}
</style>