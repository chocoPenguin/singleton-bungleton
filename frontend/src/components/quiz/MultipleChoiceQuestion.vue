<template>
    <Card>
        <template #content>
            <div class="quiz-content">
                <p class="question-text mb-4">
                    {{ question.question || 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Inventore sed consequuntur error repudiandae numquam deserunt quisquam repellat libero asperiores earum nam nobis, culpa ratione quam perferendis esse, cupiditate neque quas!' }}
                </p>
              <div class="question_max_score">
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
                                :value="choice.value"
                                v-model="selectedAnswer"
                                @change="handleAnswerChange"
                            />
                            <label 
                                :for="`choice-${index}`" 
                                class="ml-2 cursor-pointer flex-1 p-2 hover:bg-gray-50 border-round transition-colors"
                            >
                                {{ choice.label }}
                            </label>
                        </div>
                    </div>
                </div>
            </div>
        </template>
    </Card>
</template>

<script setup>
import { ref, computed } from 'vue';
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
            { value: 'A', label: '첫 번째 선택지입니다.' },
            { value: 'B', label: '두 번째 선택지입니다.' },
            { value: 'C', label: '세 번째 선택지입니다.' },
            { value: 'D', label: '네 번째 선택지입니다.' }
        ]
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
        answer: selectedAnswer.value
    });
};

const clearAnswer = () => {
    selectedAnswer.value = '';
    emit('answer', {
        questionId: props.question.id,
        answer: null
    });
};

const submitAnswer = () => {
    if (selectedAnswer.value) {
        emit('next', {
            questionId: props.question.id,
            answer: selectedAnswer.value
        });
    }
};
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