<template>
    <Card>
        <template #content>
            <div class="quiz-content">
                <p class="question-text mb-4">
                    {{ question.question || 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Inventore sed consequuntur error repudiandae numquam deserunt quisquam repellat libero asperiores earum nam nobis, culpa ratione quam perferendis esse, cupiditate neque quas!' }}
                </p>
                <div v-if="mode === 'result' && question.user_score !== undefined" class="question_max_score">
                  score: {{ question.user_score}} / {{ question.max_score }}
                </div>
                <div v-if="mode !== 'result'" class="question_max_score">
                  score: {{ question.max_score }}
                </div>
                
                <div class="answer-container mb-4">
                    
                    <!-- 짧은 답변용 InputText -->
                    <InputText
                        v-if="answerType === 'short'"
                        :id="`answer-${questionId}`"
                        v-model="userAnswer"
                        :placeholder="placeholder"
                        :disabled="mode === 'result'"
                        fluid
                        @input="handleAnswerChange"
                    />

                    <!-- 긴 답변용 Textarea -->
                    <Textarea
                        v-else
                        :id="`answer-${questionId}`"
                        v-model="userAnswer"
                        :placeholder="placeholder"
                        :disabled="mode === 'result'"
                        fluid
                        :rows="rows"
                        autoResize
                        @input="handleAnswerChange"
                    />
                    
                    <small v-if="maxLength" class="text-500 mt-1 block">
                        {{ userAnswer.length }} / 300 글자
                    </small>
                </div>

              <!-- 피드백 표시 (result 모드에서만) -->
              <div v-if="mode === 'result' && question.feedback" style="background-color: #f3f4f6; padding: 1rem; margin: 1rem 0; border-radius: 8px; border: 1px solid #e5e7eb;">
                <h4 style="color: #374151; font-weight: 600; margin-bottom: 0.5rem; font-size: 1.1rem;">AI Feedback</h4>
                <p style="color: #4b5563; line-height: 1.6; margin: 0;">{{ question.feedback }}</p>
              </div>
            </div>
        </template>
    </Card>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import Card from 'primevue/card';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Button from 'primevue/button';

// Props 정의
const props = defineProps({
    question: {
        type: Object,
        default: () => ({
            id: 1,
            title: 'Quiz 1',
            text: 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Inventore sed consequuntur error repudiandae numquam deserunt quisquam repellat libero asperiores earum nam nobis, culpa ratione quam perferendis esse, cupiditate neque quas!'
        })
    },
    answerType: {
        type: String,
        default: 'long', // 'short' | 'long'
        validator: (value) => ['short', 'long'].includes(value)
    },
    placeholder: {
        type: String,
        default: 'Enter here.'
    },
    maxLength: {
        type: Number,
        default: null
    },
    rows: {
        type: Number,
        default: 4
    },
    mode: {
      type: String,
      default: 'quiz'
    }
});

// Emits 정의
const emit = defineEmits(['answer', 'next']);

// 반응형 데이터
const userAnswer = ref('');

// 컴포넌트 고유 ID 생성
const questionId = computed(() => `question-${props.question.id || Date.now()}`);

// 메서드들
const handleAnswerChange = () => {
    emit('answer', {
        questionId: props.question.id,
        answer: userAnswer.value.trim()
    });
};

const clearAnswer = () => {
    userAnswer.value = '';
    emit('answer', {
        questionId: props.question.id,
        answer: null
    });
};

const submitAnswer = () => {
    const trimmedAnswer = userAnswer.value.trim();
    if (trimmedAnswer) {
        emit('next', {
            questionId: props.question.id,
            answer: trimmedAnswer
        });
    }
};

// result 모드에서 사용자 답변 설정
onMounted(() => {
    if (props.mode === 'result' && props.question.user_answer) {
        userAnswer.value = props.question.user_answer;
    }
});
</script>

<style scoped>
.question-text {
    line-height: 1.6;
    color: var(--text-color);
    font-family: 'Inter';
}

.answer-container {
    border: 1px solid var(--surface-border);
    border-radius: var(--border-radius);
    padding: 1rem;
    background-color: var(--surface-50);
}

/* InputText와 Textarea 커스텀 스타일 */
:deep(.p-inputtext),
:deep(.p-inputtextarea) {
    transition: all 0.2s;
}

:deep(.p-inputtext:focus),
:deep(.p-inputtextarea:focus) {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 0.2rem var(--primary-color-alpha-20);
}

/* 글자수 표시 스타일 */
.text-500 {
    color: var(--text-color-secondary);
    font-size: 0.875rem;
}

.question_max_score{
  text-align: right;
}
</style>