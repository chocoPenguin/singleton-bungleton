<template>
  <div class="groups-view">
    <!-- 그룹 목록 뷰 -->
    <div v-if="currentView === 'list'">
      <div class="page-header">
        <h1 class="page-title">{{ userName }}'s Group List</h1>
      </div>

      <div class="groups-content">
        <div class="table-header">
          <Button
            label="New"
            icon="pi pi-plus"
            class="new-button"
            @click="openNewGroup"
          />
        </div>
        <DataTable
          :value="groups"
          :paginator="true"
          :rows="10"
          :loading="loading"
          class="groups-table"
          responsiveLayout="scroll"
          stripedRows
        >
          <Column field="name" header="Group Name" sortable>
            <template #body="slotProps">
              <span
                class="clickable-group-name"
                @click="viewGroupDetails(slotProps.data)"
              >
                {{ slotProps.data.name }}
              </span>
            </template>
          </Column>
          <Column field="description" header="Description"></Column>
          <Column field="memberCount" header="Members" sortable>
            <template #body="slotProps">
              {{ slotProps.data.memberCount }}
            </template>
          </Column>
          <Column field="createdAt" header="Created" sortable>
            <template #body="slotProps">
              {{ formatDate(slotProps.data.createdAt) }}
            </template>
          </Column>
          <Column header="Actions">
            <template #body="slotProps">
              <div class="action-buttons">
                <Button
                  icon="pi pi-pencil"
                  severity="info"
                  text
                  @click="editGroup(slotProps.data)"
                  v-tooltip="'Edit'"
                />
                <Button
                  icon="pi pi-trash"
                  severity="danger"
                  text
                  @click="deleteGroup(slotProps.data)"
                  v-tooltip="'Delete'"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>
    </div>

    <!-- 그룹 상세 뷰 -->
    <div v-if="currentView === 'detail'">
      <div class="page-header">
        <div class="detail-header">
          <Button
            icon="pi pi-angle-left"
            text
            @click="backToGroupList"
            class="back-button"
            v-tooltip="'Back to Group List'"
          />
          <h1 class="page-title">{{ selectedGroup?.name }}</h1>
        </div>
      </div>

      <div class="groups-content">
        <div class="table-header">
          <Button
            label="New"
            icon="pi pi-plus"
            class="new-button"
            @click="openAddMember"
          />
        </div>
        <DataTable
          :value="groupMembers"
          :paginator="true"
          :rows="10"
          :loading="membersLoading"
          class="members-table groups-table"
          responsiveLayout="scroll"
          stripedRows
        >
          <Column field="name" header="Name" sortable></Column>
          <Column field="email" header="Email" sortable></Column>
          <Column header="Actions">
            <template #body="slotProps">
              <div class="action-buttons">
                <Button
                  icon="pi pi-pencil"
                  severity="info"
                  text
                  @click="editMember(slotProps.data)"
                  v-tooltip="'Edit Member'"
                />
                <Button
                  icon="pi pi-user-minus"
                  severity="danger"
                  text
                  @click="removeMember(slotProps.data)"
                  v-tooltip="'Remove from Group'"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>
    </div>

    <!-- Group Modal -->
    <GroupModal
      v-model:visible="showGroupModal"
      :group="selectedGroupForEdit"
      @save="handleSaveGroup"
    />

    <!-- Member Modal -->
    <MemberModal
      v-model:visible="showMemberModal"
      :member="selectedMemberForEdit"
      @save="handleSaveMember"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import ColumnGroup from 'primevue/columngroup';
import Row from 'primevue/row';
import Button from 'primevue/button';
import Tag from 'primevue/tag';
import { getAllGroups, createGroup, updateGroup } from '../../api/groups.js';
import { getUsersByGroup, getCurrentUser, createUser, addUserToGroup, getAllUsers } from '../../api/users.js';
import { getAllAuthors } from '../../api/auth.js';
import { getCurrentUserFromToken, getUserIdFromToken } from '../../utils/auth.js';
import GroupModal from '../../components/GroupModal.vue';
import MemberModal from '../../components/MemberModal.vue';
import 'primeicons/primeicons.css'

// 반응형 데이터
const userName = ref('Loading...');
const groups = ref([]);
const loading = ref(true);

// 뷰 상태 관리
const currentView = ref('list'); // 'list' | 'detail'
const selectedGroup = ref(null);
const groupMembers = ref([]);
const membersLoading = ref(false);

// Modal state
const showGroupModal = ref(false);
const showMemberModal = ref(false);
const selectedGroupForEdit = ref(null);
const selectedMemberForEdit = ref(null);

const toast = useToast();

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

    // 실제 사용자 정보 API 호출 (옵션)
    // const response = await getCurrentUser();
    // userName.value = response.data.name;
  } catch (error) {
    console.error('사용자 정보 가져오기 실패:', error);
    userName.value = 'Guest';
  }
};

// 그룹 데이터 가져오기
const fetchGroups = async () => {
  loading.value = true;
  try {
    // 실제 API 호출
    const response = await getAllGroups();

    console.log('Groups API response:', response.data); // 디버깅용

    // 백엔드에서 받은 데이터를 프론트엔드 형식에 맞게 변환
    groups.value = await Promise.all(response.data.map(async (group) => {
      let memberCount = group.member_count || group.memberCount || 0;

      // member_count가 없으면 별도로 멤버 수를 가져오기
      if (memberCount === 0) {
        try {
          const membersResponse = await getUsersByGroup(group.id);
          memberCount = membersResponse.data.length;
        } catch (memberError) {
          console.warn(`Failed to get member count for group ${group.id}:`, memberError);
          memberCount = 0;
        }
      }

      return {
        id: group.id,
        name: group.name,
        description: group.description || 'No description',
        memberCount: memberCount,
        createdAt: new Date(group.created_at),
        status: group.is_active ? 'Active' : 'Inactive'
      };
    }));
  } catch (error) {
    console.error('그룹 데이터 가져오기 실패:', error);

    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load groups. Please try again.',
      life: 5000
    });

    // 에러 시 빈 배열로 설정
    groups.value = [];
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

// 상태 severity 반환
const getStatusSeverity = (status) => {
  switch (status.toLowerCase()) {
    case 'active': return 'success';
    case 'inactive': return 'warning';
    default: return 'info';
  }
};

// 그룹 상세 보기
const viewGroupDetails = async (group) => {
  selectedGroup.value = group;
  currentView.value = 'detail';
  await fetchGroupMembers(group.id);
};

// 그룹 멤버 데이터 가져오기
const fetchGroupMembers = async (groupId) => {
  membersLoading.value = true;
  try {
    // 실제 API 호출
    const response = await getUsersByGroup(groupId);

    // 백엔드에서 받은 데이터를 프론트엔드 형식에 맞게 변환
    groupMembers.value = response.data.map(user => ({
      id: user.id,
      name: user.name,
      email: user.email,
      role: user.role || 'Member',
      joinedAt: new Date(user.created_at || user.joined_at),
      status: user.is_active ? 'Active' : 'Inactive'
    }));
  } catch (error) {
    console.error('그룹 멤버 데이터 가져오기 실패:', error);

    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load group members. Please try again.',
      life: 5000
    });

    // 에러 시 빈 배열로 설정
    groupMembers.value = [];
  } finally {
    membersLoading.value = false;
  }
};

// 그룹 목록으로 돌아가기
const backToGroupList = () => {
  currentView.value = 'list';
  selectedGroup.value = null;
  groupMembers.value = [];
};

// 역할 severity 반환
const getRoleSeverity = (role) => {
  switch (role.toLowerCase()) {
    case 'admin': return 'danger';
    case 'moderator': return 'warning';
    case 'member': return 'info';
    default: return 'secondary';
  }
};

// Modal handlers
const openNewGroup = () => {
  selectedGroupForEdit.value = null;
  showGroupModal.value = true;
};

const openAddMember = () => {
  selectedMemberForEdit.value = null;
  showMemberModal.value = true;
};

const handleSaveGroup = async (groupData) => {
  try {
    if (groupData.id) {
      // Edit existing group
      await updateGroup(groupData.id, groupData);
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Group updated successfully',
        life: 3000
      });
    } else {
      // Create new group
      const userInfo = getCurrentUserFromToken();

      if (!userInfo?.email) {
        throw new Error('User authentication required');
      }

      // 현재 사용자의 이메일과 매칭되는 author ID 찾기
      const allAuthorsResponse = await getAllAuthors();
      const currentAuthor = allAuthorsResponse.data.find(author => author.email === userInfo.email);

      if (!currentAuthor) {
        throw new Error('Current author not found in database');
      }

      const authorId = currentAuthor.id;

      const payload = {
        name: groupData.name,
        language: groupData.language,
        memo: groupData.memo || '',
        author_id: authorId
      };

      console.log('Creating group with payload:', payload); // 디버깅용
      await createGroup(payload);
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Group created successfully',
        life: 3000
      });
    }

    // Refresh groups list
    await fetchGroups();
  } catch (error) {
    console.error('Failed to save group:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to save group. Please try again.',
      life: 5000
    });
  }
};

const handleSaveMember = async (memberData) => {
  try {
    if (memberData.id) {
      // Edit existing member - not implemented yet
      toast.add({
        severity: 'info',
        summary: 'Info',
        detail: 'Member editing not implemented yet',
        life: 3000
      });
    } else {
      // Create new user and add to group
      const newUser = await createUser({
        name: memberData.name,
        email: memberData.email,
        role: memberData.role
      });

      // Add user to current group
      await addUserToGroup(selectedGroup.value.id, newUser.data.id);

      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Member added successfully',
        life: 3000
      });
    }

    // Refresh members list
    if (selectedGroup.value) {
      await fetchGroupMembers(selectedGroup.value.id);
    }
  } catch (error) {
    console.error('Failed to save member:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to save member. Please try again.',
      life: 5000
    });
  }
};

// 그룹 편집
const editGroup = (group) => {
  selectedGroupForEdit.value = group;
  showGroupModal.value = true;
};

// 그룹 삭제
const deleteGroup = (group) => {
  console.log('Delete group:', group);
  // TODO: 삭제 확인 다이얼로그 표시
};

// 멤버 편집
const editMember = (member) => {
  selectedMemberForEdit.value = member;
  showMemberModal.value = true;
};

// 멤버 제거
const removeMember = (member) => {
  console.log('Remove member:', member);
  // TODO: 멤버 제거 확인 다이얼로그 표시
};

// 컴포넌트 마운트 시 데이터 로드
onMounted(() => {
  fetchCurrentUser();
  fetchGroups();
});
</script>

<style scoped lang="scss">
@import '@/assets/styles/datatable.scss';

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

/* 그룹명 클릭 가능 스타일 */
.clickable-group-name {
  color: #374151;
  cursor: pointer;
  font-weight: 600;
  text-decoration: none;
  transition: color 0.2s;
}

.clickable-group-name:hover {
  color: #374151;
  text-decoration: underline;
}

/* 상세 페이지 헤더 */
.detail-header {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.back-button {
  flex-shrink: 0;
  padding: 0.5rem;
  color: #6b7280;
  border-radius: 0.5rem;
  transition: all 0.2s;
}

.back-button:hover {
  background-color: #f3f4f6;
  color: #374151;
}
</style>