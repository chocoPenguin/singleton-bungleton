<template>
  <div class="about-view">
    <div class="page-header">
      <h1>About Qraft</h1>
      <p>AI 기반 교육 퀴즈 시스템</p>
    </div>

    <div class="content-grid">
      <Card class="about-card">
        <template #header>
          <div class="card-icon">
            <i class="pi pi-lightbulb"></i>
          </div>
        </template>
        <template #title>AI 기반 퀴즈 생성</template>
        <template #content>
          <p>Microsoft Copilot Studio를 활용하여 사용자별로 맞춤형 퀴즈를 자동 생성합니다.</p>
        </template>
      </Card>

      <Card class="about-card">
        <template #header>
          <div class="card-icon">
            <i class="pi pi-users"></i>
          </div>
        </template>
        <template #title>그룹 관리</template>
        <template #content>
          <p>그룹별로 사용자를 관리하고, 각 그룹에 적합한 교육 콘텐츠를 제공합니다.</p>
        </template>
      </Card>

      <Card class="about-card">
        <template #header>
          <div class="card-icon">
            <i class="pi pi-chart-bar"></i>
          </div>
        </template>
        <template #title>성과 분석</template>
        <template #content>
          <p>개인별, 그룹별 학습 성과를 분석하여 교육 효과를 극대화합니다.</p>
        </template>
      </Card>
    </div>

    <Card class="tech-stack-card">
      <template #title>기술 스택</template>
      <template #content>
        <div class="tech-grid">
          <div class="tech-item">
            <h4>Frontend</h4>
            <ul>
              <li>Vue 3 + TypeScript</li>
              <li>PrimeVue UI Library</li>
              <li>Vite Build Tool</li>
            </ul>
          </div>
          <div class="tech-item">
            <h4>Backend</h4>
            <ul>
              <li>FastAPI + Python</li>
              <li>SQLAlchemy ORM</li>
              <li>SQLite Database</li>
            </ul>
          </div>
          <div class="tech-item">
            <h4>AI Integration</h4>
            <ul>
              <li>Microsoft Copilot Studio</li>
              <li>자동 퀴즈 생성</li>
              <li>개인별 맞춤 문제</li>
            </ul>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup>
import Card from 'primevue/card';
</script>

<style scoped>
.about-view {
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

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.about-card {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-radius: 1rem;
  height: 100%;
}

.card-icon {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 80px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 2rem;
}

.tech-stack-card {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-radius: 1rem;
}

.tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.tech-item h4 {
  margin: 0 0 1rem 0;
  color: #374151;
  font-size: 1.1rem;
  font-weight: 600;
}

.tech-item ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.tech-item li {
  padding: 0.5rem 0;
  color: #6b7280;
  border-bottom: 1px solid #f3f4f6;
}

.tech-item li:last-child {
  border-bottom: none;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .about-view {
    padding: 0.5rem;
  }

  .content-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .tech-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}
</style>