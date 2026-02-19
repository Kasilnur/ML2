<script setup>
import { ref, computed } from 'vue';

const text = ref('');
const results = ref(null);

const analyze = async () => {
  if (!text.value) return;

  try {
    const response = await fetch('http://127.0.0.1:8000/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text.value })
    });
    const data = await response.json();
    results.value = data.predictions;
  } catch (e) {
    alert('Ошибка соединения с сервером');
  }
};

const translate = (label) => {
  const dict = {
    normal: 'Нормальный',
    insult: 'Оскорбление',
    threat: 'Угроза',
    obscenity: 'Непристойность'
  };
  return dict[label] || label;
};

const verdict = computed(() => {
  if (!results.value) return { text: '', type: '' };

  const isToxic =
    results.value.insult > 0.5 ||
    results.value.threat > 0.5 ||
    results.value.obscenity > 0.5;

  if (isToxic) {
    return { text: 'Комментарий отрицательный', type: 'bad' };
  }
  return { text: 'Комментарий положительный', type: 'good' };
});
</script>

<template>
  <div class="main-container">
    <h2>Анализ комментариев</h2>

    <textarea v-model="text" placeholder="Введите комментарий для анализа..."></textarea>
    <button @click="analyze">Проверить</button>

    <div v-if="results" class="results-box">
      <div class="verdict" :class="verdict.type">
        {{ verdict.text }}
      </div>
      <div class="classes">
        <div v-for="(prob, label) in results" :key="label" class="class-item">
          <span>{{ translate(label) }}:</span>
          <strong>{{ (prob * 100).toFixed(1) }}%</strong>
        </div>
      </div>
    </div>
  </div>
</template>


<style>
body {
  margin: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: white;
  color: #333;
  font-family:
    Inter,
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    Roboto,
    Oxygen,
    Ubuntu,
    Cantarell,
    'Fira Sans',
    'Droid Sans',
    'Helvetica Neue',
    sans-serif;
}

.main-container {
  background: #fff;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

h2 {
  margin-bottom: 10px;
  font-size: 20px;
  font-weight: 600;
  text-align: center;
}

textarea {
  width: 100%;
  height: 90px;
  padding: 12px;
  margin-bottom: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  resize: none;
  box-sizing: border-box;
  font-family: inherit;
  font-size: 14px;
  outline: none;
}

textarea:focus {
  border-color: #a0aec0;
}

button {
  width: 100%;
  padding: 12px;
  background: #1a202c;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.2s;
}

button:hover {
  background: #2d3748;
}

.results-box {
  margin-block: 20px;
}

.verdict {
  font-weight: bold;
  text-align: center;
  padding: 12px;
  margin-bottom: 10px;
  border-radius: 10px;
  font-size: 14px;
}

.verdict.good {
  background: #f0fdf4;
  color: #166534;
}

.verdict.bad {
  background: #fef2f2;
  color: #991b1b;
}

.class-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 14px;
  color: #4a5568;
}

.class-item strong {
  color: #1a202c;
}
</style>