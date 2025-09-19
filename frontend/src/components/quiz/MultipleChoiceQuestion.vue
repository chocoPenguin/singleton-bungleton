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
                <div class="choices-container">
                    <div 
                        v-for="(choice, index) in choices" 
                        :key="index"
                        class="choice-item mb-3"
                        style="margin: 0.5rem"
                    >
                        <div class="flex align-items-center">
                            <RadioButton
                                :inputId="`choice-${index}`"
                                :name="questionId"
                                :value="choice"
                                v-model="selectedAnswer"
                                :disabled="mode === 'result'"
                                @change="handleAnswerChange"
                            />
                            <label
                                :for="`choice-${index}`"
                                :class="[
                                    'ml-2 flex-1 p-2 border-round transition-colors',
                                    mode === 'result' ? 'cursor-default' : 'cursor-pointer hover:bg-gray-50'
                                ]"
                            >
                                {{ choice }}
                            </label>
                        </div>
                    </div>
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
import RadioButton from 'primevue/radiobutton';

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
    choices: {
        type: Array,
        default: () => [
            '첫 번째 선택지입니다.',
            '두 번째 선택지입니다.',
            '세 번째 선택지입니다.',
            '네 번째 선택지입니다.'
        ]
    },
    mode: {
        type: String,
        default: 'quiz'
    }
});

// Emits 정의
const emit = defineEmits(['answer', 'next']);

// 반응형 데이터
const selectedAnswer = ref('');

// 컴포넌트 고유 ID 생성
const questionId = computed(() => `question-${props.question.id || Date.now()}`);

// 메서드들
const handleAnswerChange = () => {
    emit('answer', {
        questionId: props.question.id,
        answer: selectedAnswer
    });
};

// result 모드에서 사용자 답변 설정
onMounted(() => {
    if (props.mode === 'result' && props.question.user_answer) {
        selectedAnswer.value = props.question.user_answer;
    }
});

</script>

<style scoped>
.question-text {
    line-height: 1.6;
    color: var(--text-color);
}

.choice-item {
    border: 1px solid var(--surface-border);
    border-radius: var(--border-radius);
    transition: all 0.2s;
    padding: 0 0.5rem;
}

.choice-item:hover {
    border-color: var(--primary-color);
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.choice-item label {
    user-select: none;
    padding: 0 0.5rem;
}

.question_max_score{
    text-align: right;
}
</style>