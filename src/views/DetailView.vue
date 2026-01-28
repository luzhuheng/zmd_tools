<script setup lang="ts">
import { computed, ref, onMounted } from 'vue';
import type { DataManager, FarmingPlan } from '../utils/DataManager';
import { FavoritesManager, type FavoritePlan } from '../utils/favorites';

const props = defineProps<{
  dm: DataManager;
  weaponName: string;
}>();

const emit = defineEmits<{
  (e: 'back'): void;
}>();

const weapon = computed(() => props.dm.getWeaponDetails(props.weaponName));
const plans = computed(() => props.dm.getFarmingPlans(props.weaponName));

const favorites = ref<FavoritePlan[]>([]);

onMounted(() => {
  favorites.value = FavoritesManager.getFavorites();
});

const isFav = (plan: FarmingPlan) => {
  return favorites.value.some(f => 
    f.weaponName === props.weaponName &&
    f.dungeon === plan.dungeon &&
    f.strategy === plan.strategy &&
    f.fixed_val === plan.fixed_val
  );
};

const toggleFavorite = (plan: FarmingPlan) => {
  if (isFav(plan)) {
    FavoritesManager.removeFavorite(props.weaponName, plan);
  } else {
    FavoritesManager.addFavorite(props.weaponName, plan);
  }
  favorites.value = FavoritesManager.getFavorites();
};

const rarityMap: Record<string, string> = {
  '一星': '1',
  '二星': '2',
  '三星': '3',
  '四星': '4',
  '五星': '5',
  '六星': '6'
};

const formatWeaponWithRarity = (name: string) => {
  const w = props.dm.getWeaponDetails(name);
  if (!w) return name;
  const r = rarityMap[w.rarity] || w.rarity.replace('星', '');
  return `${name} ${r}★`;
};

// 辅助函数：为特定方案排序副产物
const getSortedByProducts = (plan: FarmingPlan) => {
  if (!plan || !plan.by_products) return [];

  return Object.entries(plan.by_products)
    .sort(([, a], [, b]) => b.length - a.length)
    .map(([key, weapons]) => ({
      key,
      weapons: weapons.map(formatWeaponWithRarity).join(', ')
    }));
};
</script>

<template>
  <div class="flex flex-col h-full w-full mx-auto p-4 space-y-4 overflow-y-auto">
    <!-- 头部 -->
    <div class="flex items-center justify-between">
      <button @click="emit('back')"
        class="p-2 rounded hover:bg-gray-200 transition-colors flex items-center text-gray-700 font-bold">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"
          class="w-5 h-5 mr-1">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
        </svg>
        收起
      </button>
    </div>

    <div v-if="!weapon" class="text-red-500">Weapon not found</div>

    <template v-else>
      <!-- 信息卡片 -->
      <div class="bg-white rounded-lg shadow p-4 border border-gray-200">
        <div class="flex flex-col items-center text-center space-y-2">
          <!-- 第一行：图标 + 名称 + 稀有度 + 种类 -->
          <div class="flex flex-wrap items-center justify-center gap-2">
            <!-- 盾牌图标 -->
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"
              class="w-6 h-6 text-gray-700">
              <path fill-rule="evenodd"
                d="M12.516 2.17a.75.75 0 00-1.032 0 11.209 11.209 0 01-7.877 3.08.75.75 0 00-.722.515A12.74 12.74 0 002.25 12c0 5.542 2.98 10.533 7.918 13.027a.75.75 0 00.664 0C15.77 22.533 18.75 17.542 18.75 12a12.74 12.74 0 00-.635-6.235.75.75 0 00-.722-.515 11.208 11.208 0 01-7.877-3.08zM12 13.25a.75.75 0 000-1.5.75.75 0 000 1.5z"
                clip-rule="evenodd" />
            </svg>
            <span class="text-xl font-bold text-gray-900">{{ weapon.name }}</span>
            <span class="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full border border-gray-200">
              {{ weapon.rarity }}
            </span>
            <span class="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full border border-gray-200">
              {{ weapon.type }}
            </span>
          </div>
          
          <!-- 第二行：属性信息 -->
          <div class="flex flex-wrap justify-center gap-x-6 gap-y-1 text-sm pt-1">
            <div class="flex items-center space-x-1">
              <span class="font-bold text-blue-600">主词条:</span>
              <span class="text-gray-700">{{ weapon.main_stat }}</span>
            </div>
            <div class="flex items-center space-x-1">
              <span class="font-bold text-green-600">副词条:</span>
              <span class="text-gray-700">{{ weapon.sub_stat }}</span>
            </div>
            <div class="flex items-center space-x-1">
              <span class="font-bold text-orange-500">技能:</span>
              <span class="text-gray-700">{{ weapon.skill }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 方案列表 -->
      <div v-if="plans.length > 0" class="space-y-6">
        <h2 class="text-xl font-bold text-gray-800">推荐刷取方案 (共 {{ plans.length }} 种)</h2>

        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-6">
          <div v-for="(plan, idx) in plans" :key="idx" class="bg-white rounded-lg shadow p-6 border border-gray-200 h-full">
          <div class="flex justify-between items-start mb-2">
            <div class="flex items-center space-x-2">
              <h3 class="text-lg font-bold text-teal-600">方案 #{{ idx + 1 }}</h3>
              <button @click.stop="toggleFavorite(plan)" class="text-yellow-500 hover:text-yellow-600 transition-colors focus:outline-none" title="收藏/取消收藏">
                <svg v-if="isFav(plan)" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6">
                  <path fill-rule="evenodd" d="M10.788 3.21c.448-1.077 1.976-1.077 2.424 0l2.082 5.007 5.404.433c1.164.093 1.636 1.545.749 2.305l-4.117 3.527 1.257 5.273c.271 1.136-.964 2.033-1.96 1.425L12 18.354 7.373 21.18c-.996.608-2.231-.29-1.96-1.425l1.257-5.273-4.117-3.527c-.887-.76-.415-2.212.749-2.305l5.404-.433 2.082-5.006z" clip-rule="evenodd" />
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.563.045.797.77.362 1.127l-4.243 3.634a.563.563 0 00-.153.554l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.153-.554L3.016 10.513a.562.562 0 01.362-1.127l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" />
                </svg>
              </button>
            </div>
            <span class="text-xs px-2 py-1 bg-gray-100 rounded text-gray-600">
              {{ plan.strategy }}定向
            </span>
          </div>
          <hr class="border-gray-200 mb-4" />

          <div class="space-y-3">
            <div>
              <span class="font-bold text-gray-700">副本: </span>
              <span class="font-bold">{{ plan.dungeon }}</span>
            </div>

            <div>
              <div class="font-bold text-gray-700">定向主词条:</div>
              <div class="text-blue-600">{{ plan.selected_mains.join(', ') }}</div>
            </div>

            <div class="flex flex-wrap items-baseline gap-2">
              <span class="font-bold text-gray-700">定向策略: </span>
              <span class="text-blue-600">{{ plan.strategy }} ({{ plan.fixed_val }})</span>
            </div>

            <hr class="border-gray-200 my-4" />

            <div>
              <div class="font-bold text-gray-700 mb-2">
                可能产出的有用副产物 (共帮助 {{ plan.score }} 把其他武器):
              </div>

              <div class="border border-gray-300 rounded p-2 h-72 overflow-y-auto bg-gray-50 space-y-2">
                <div v-if="getSortedByProducts(plan).length === 0" class="italic text-gray-500 p-2">
                  无其他适用武器产生的副产物
                </div>
                <div v-for="(item, index) in getSortedByProducts(plan)" :key="index"
                  class="bg-white p-2 rounded border-b border-gray-200 last:border-0">
                  <div class="flex items-center text-sm font-bold text-blue-gray-600 mb-1">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"
                      class="w-4 h-4 mr-1 text-gray-500">
                      <path fill-rule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm.75-11.25a.75.75 0 00-1.5 0v2.5h-2.5a.75.75 0 000 1.5h2.5v2.5a.75.75 0 001.5 0v-2.5h2.5a.75.75 0 000-1.5h-2.5v-2.5z"
                        clip-rule="evenodd" />
                    </svg>
                    <span class="text-slate-600">[{{ item.key }}]</span>
                  </div>
                  <div class="text-xs text-gray-600 italic">
                    适用: {{ item.weapons }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        </div>
      </div>

      <div v-else class="bg-red-50 border border-red-200 text-red-600 p-4 rounded-lg">
        无可用刷取方案 (未找到同时满足条件的副本)
      </div>

    </template>
  </div>
</template>
