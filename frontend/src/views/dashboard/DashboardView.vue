<template>
  <div class="dashboard-container">
    <!-- 상단 텍스트 -->
    <p class="greeting">
      안녕하세요, <strong>{{ userName }}</strong> 님
    </p>

    <!-- 상단 차트 영역: 좌측 라인차트 / 우측 그룹별 퍼센트 bar -->
    <div class="top-section">
      <!-- 날짜별 문제 제출 라인 차트 -->
      <div class="card chart-card">
        <p class="section-title">전체 문제 출제 / 풀이 현황</p>
        <apexchart type="line" height="260" :options="lineOptions" :series="lineSeries" />
      </div>

      <!-- 그룹별 풀이 퍼센트 바 차트 -->
      <div class="card chart-card">
        <p class="section-title">그룹별 문제 풀이 퍼센트</p>
        <div class="group-bars">
          <div class="bar-row" v-for="(group, index) in groupProgress" :key="index">
            <span class="bar-label">{{ group.name }}</span>
            <div class="bar-container">
              <div class="bar-fill" :style="{ width: group.percent + '%' }"></div>
            </div>
            <span class="bar-percent">{{ group.percent }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 하단 유저 상위 랭킹 테이블 -->
    <div class="card table-card">
      <p class="section-title">TOP 5</p>
      <table class="ranking-table">
        <thead>
          <tr>
            <th>유저</th>
            <th>문제 풀이 수</th>
            <th>정답률</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(user, index) in topUsers" :key="index">
            <td>{{ user.name }}</td>
            <td>{{ user.solved }}</td>
            <td>{{ user.accuracy }}%</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import VueApexCharts from "vue3-apexcharts";

export default {
  name: "FinalDashboardView",
  components: {
    apexchart: VueApexCharts,
  },
  props: {
    userName: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      lineSeries: [
        { name: "출제된 문제 수", data: [5, 8, 6, 9, 10, 7, 11] },
        { name: "풀이된 문제 수", data: [3, 6, 5, 7, 9, 6, 10] },
      ],
      lineOptions: {
        chart: { toolbar: { show: false } },
        stroke: { curve: "smooth", width: 3 },
        colors: ["#94a3b8", "#64748B"],
        xaxis: {
          categories: ["9/13", "9/14", "9/15", "9/16", "9/17", "9/18", "9/19"],
          labels: {
            style: {
              colors: "#64748B",
              fontWeight: 500,
            },
          },
        },
        yaxis: {
          labels: {
            style: {
              colors: "#64748B",
              fontWeight: 500,
            },
          },
        },
        legend: {
          position: "top",
          horizontalAlign: "left",
        },
      },
      groupProgress: [
        { name: "Group1", percent: 92 },
        { name: "Group2", percent: 81 },
        { name: "Group3", percent: 68 },
        { name: "Group4", percent: 54 },
        { name: "Group5", percent: 49 },
      ],
      topUsers: [
        { name: "홍길동", solved: 52, accuracy: 94 },
        { name: "김개발", solved: 48, accuracy: 91 },
        { name: "이문제", solved: 44, accuracy: 89 },
        { name: "박풀이", solved: 42, accuracy: 87 },
        { name: "최정답", solved: 40, accuracy: 85 },
      ],
    };
  },
};
</script>

<style scoped lang="scss">
.dashboard-container {
  padding: 2rem;
  background-color: #f8f9fa;
  font-family: "Inter", sans-serif;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.greeting {
  font-size: 1.25rem;
  font-weight: 500;
  color: #111827;
}

.top-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
}

.card {
  background: #ffffff;
  border-radius: 14px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.chart-card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
}

.group-bars {
  display: flex;
  flex-direction: column;
  gap: 1rem;

  .bar-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;

    .bar-label {
      width: 60px;
      font-size: 0.9rem;
      color: #64748b;
    }

    .bar-container {
      flex: 1;
      background: #e5e7eb;
      height: 8px;
      border-radius: 4px;
      overflow: hidden;

      .bar-fill {
        height: 100%;
        background: #64748b;
      }
    }

    .bar-percent {
      width: 40px;
      text-align: right;
      font-size: 0.9rem;
      color: #374151;
    }
  }
}

.table-card {
  padding: 1.5rem;
}

.ranking-table {
  width: 100%;
  border-collapse: collapse;

  th,
  td {
    padding: 0.75rem;
    text-align: left;
    font-size: 0.9rem;
  }

  th {
    color: #6b7280;
    font-weight: 500;
    border-bottom: 1px solid #e5e7eb;
  }

  td {
    color: #374151;
    border-bottom: 1px solid #f1f5f9;
  }

  tr:last-child td {
    border-bottom: none;
  }
}
</style>
