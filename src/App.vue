<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { DataManager } from './utils/DataManager';
import HomeView from './views/HomeView.vue';
import DetailView from './views/DetailView.vue';

const dm = new DataManager();
const loading = ref(true);
const error = ref<string | null>(null);

const showDetail = ref(false);
const selectedWeapon = ref<string>('');

onMounted(async () => {
  try {
    await dm.loadData();
    loading.value = false;
  } catch (e) {
    error.value = `Failed to load data: ${e}`;
    loading.value = false;
  }
});

function handleWeaponSelect(name: string) {
  selectedWeapon.value = name;
  showDetail.value = true;
}

function handleBack() {
  showDetail.value = false;
}
</script>

<template>
  <div class="min-h-screen bg-gray-100 font-sans text-gray-900">
    <div v-if="loading" class="flex items-center justify-center min-h-screen">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
    </div>
    
    <div v-else-if="error" class="flex items-center justify-center min-h-screen text-red-500 p-4">
      {{ error }}
    </div>

    <div v-else class="h-screen flex flex-col relative overflow-hidden">
      <!-- 主页始终显示 -->
      <HomeView 
        :dm="dm" 
        @select="handleWeaponSelect"
      />
      
      <!-- 遮罩层 -->
      <div 
        class="absolute inset-0 bg-black/50 z-20 transition-opacity duration-300"
        :class="showDetail ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'"
        @click="handleBack"
      ></div>

      <!-- 详情页 - 底部升起 -->
      <div 
        class="absolute bottom-0 left-0 right-0 bg-gray-100 rounded-t-2xl shadow-2xl z-30 transform transition-transform duration-300 ease-in-out flex flex-col h-[90vh]"
        :class="showDetail ? 'translate-y-0' : 'translate-y-full'"
      >
        <DetailView 
          v-if="selectedWeapon"
          :dm="dm" 
          :weapon-name="selectedWeapon"
          @back="handleBack"
          class="h-full rounded-t-2xl"
        />
      </div>
    </div>
  </div>
</template>

<style>
/* 如果需要，全局样式 */
html, body {
  height: 100%;
  margin: 0;
}
</style>
