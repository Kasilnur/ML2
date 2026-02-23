<script setup>
import { ref, computed } from 'vue';

const text = ref('');
const results = ref(null);
const rows = ref([]);

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
    rows.value = data.rows;
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
          <strong>{{ (prob * 100).toFixed(2) }}%</strong>
        </div>
      </div>
    </div>
    <div class="comments-section">
      <h3>Комментарии ({{ Object.keys(rows).length }})</h3>
      <div v-if="Object.keys(rows).length" class="comments-list">
        <div v-for="(item, id) in rows" :key="id" class="comment-card">
          <div class="comment-header">
            <span class="comment-id">№ {{ id }}</span>
          </div>
          <p class="comment-text">{{ item.comment }}</p>

          <div class="prediction-box">
            <div v-for="(prob, label) in item.prediction" :key="label" class="prediction-item">
              <span>{{ translate(label) }}:</span>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: (prob * 100) + '%' }"></div>
              </div>
              <span class="prediction-value">{{ (prob * 100).toFixed(2) }}%</span>
            </div>
          </div>
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
  min-width: 70vw;
  background: #fff;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.main-container h2 {
  margin: 0 0 10px 0;
  font-size: 20px;
  font-weight: 600;
  text-align: center;
}

textarea {
  width: 100%;
  height: 90px;
  padding: 10px;
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
  padding: 10px;
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

button:active {
  background: #404b5f;
}

.results-box {
  margin-block: 10px;
}

.verdict {
  font-weight: bold;
  text-align: center;
  padding: 10px;
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
  justify-self: center;
  width: 15%;
  margin-bottom: 10px;
  font-size: 14px;
  color: #4a5568;
}

.class-item strong {
  color: #1a202c;
}

.comments-section {
  margin-top: 30px;
  border-top: 1px solid #e2e8f0;
  padding-top: 20px;
}

.comments-section h3 {
  margin: 0 0 15px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a202c;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 200px;
  overflow-y: auto;
  padding-right: 5px;
}

.comment-card {
  background: #f7fafc;
  border-radius: 8px;
  padding: 12px;
  border: 1px solid #edf2f7;
}

.comment-header {
  display: flex;
  gap: 10px;
  margin-bottom: 5px;
  font-size: 13px;
  color: #718096;
}

.comment-id {
  font-weight: 600;
  color: #2d3748;
}

.comment-text {
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
  color: #1a202c;
}

.prediction-box {
  background: white;
  border-radius: 8px;
  padding: 10px;
  margin-top: 10px;
  border: 1px solid #e2e8f0;
}

.prediction-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
  font-size: 13px;
}

.prediction-item span:first-child {
  width: 100px;
  color: #4a5568;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #1a202c;
}

.prediction-value {
  min-width: 50px;
  text-align: right;
  font-weight: 600;
  color: #2d3748;
}
</style>