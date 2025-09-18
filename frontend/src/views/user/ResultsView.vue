<template>
  <div class="results-view">
    <div class="page-header">
      <h1>Quiz Results</h1>
      <p>사용자별 퀴즈 결과를 확인하세요</p>
    </div>

    <Card class="results-card">
      <template #content>
        <div class="empty-state">
          <i class="pi pi-chart-line empty-icon"></i>
          <h3>결과 페이지</h3>
          <p>퀴즈 결과 기능은 현재 개발 중입니다.</p>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup>
import Card from 'primevue/card';
</script>

<style scoped>
.results-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

.page-header {
  text-align: center;
  margin-bottom: 2rem;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 1rem;
  color: white;
}

.page-header h1 {
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
  font-weight: 600;
}

.page-header p {
  margin: 0;
  opacity: 0.9;
  font-size: 1.1rem;
}

.results-card {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-radius: 1rem;
}

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
  margin: 0;
}
</style>