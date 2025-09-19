<!-- QuizView.vue -->
<template>
  <QuizContainer :key="$route.path" :mode="computedMode" />
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import QuizContainer from '@/components/quiz/QuizContainer.vue'

const route = useRoute()

// Props 정의
const props = defineProps({
  mode: {
    type: String,
    default: 'quiz'
  }
})

// 라우트 경로에 따라 mode 결정
const computedMode = computed(() => {
  if (route.path === '/quiz/result') {
    return 'result'
  } else if (route.path === '/quiz/list') {
    return 'quiz'
  }
  return props.mode || 'quiz'
})

</script>