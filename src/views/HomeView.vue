<script setup lang="ts">
import { ref, computed } from 'vue';
import type { DataManager } from '../utils/DataManager';
import WeaponCard from '../components/WeaponCard.vue';
import { FavoritesManager } from '../utils/favorites';

const props = defineProps<{
  dm: DataManager;
}>();

const emit = defineEmits<{
  (e: 'select', name: string): void;
}>();

const favorites = FavoritesManager.favorites;
const searchQuery = ref('');
const allWeapons = computed(() => props.dm.getWeaponNames());

const filteredWeapons = computed(() => {
  const q = searchQuery.value.toLowerCase();
  return allWeapons.value.filter(name => {
    if (!q) return true;
    return name.toLowerCase().includes(q);
  });
});

</script>

<template>
  <div class="flex flex-col h-full max-w-7xl mx-auto p-4">
    <!-- 头部 -->
    <div class="pt-5 pb-2 pl-2">
      <h1 class="text-3xl font-bold text-gray-900">武器列表</h1>
    </div>

    <!-- 搜索 -->
    <div class="p-2 sticky top-0 bg-gray-100 z-10">
      <div class="relative">
        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5 text-gray-400">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
          </svg>
        </div>
        <input 
          v-model="searchQuery"
          type="text" 
          class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          placeholder="搜索武器"
        />
      </div>
    </div>

    <!-- 列表 -->
    <div class="flex-1 overflow-y-auto p-2">
      <!-- 收藏列表 -->
      <div v-if="favorites.length > 0" class="mb-6">
        <h2 class="text-xl font-bold text-gray-800 mb-3 px-1 flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6 text-yellow-500 mr-2">
            <path fill-rule="evenodd" d="M10.788 3.21c.448-1.077 1.976-1.077 2.424 0l2.082 5.007 5.404.433c1.164.093 1.636 1.545.749 2.305l-4.117 3.527 1.257 5.273c.271 1.136-.964 2.033-1.96 1.425L12 18.354 7.373 21.18c-.996.608-2.231-.29-1.96-1.425l1.257-5.273-4.117-3.527c-.887-.76-.415-2.212.749-2.305l5.404-.433 2.082-5.006z" clip-rule="evenodd" />
          </svg>
          我的收藏
        </h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <div v-for="(fav, idx) in favorites" :key="idx" 
               class="bg-white rounded-lg shadow border border-yellow-200 p-4 cursor-pointer hover:shadow-md transition-shadow relative group"
               @click="emit('select', fav.weaponName)">
             <div class="font-bold text-gray-900 mb-1 flex justify-between">
               {{ fav.weaponName }}
               <button class="text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity" 
                  @click.stop="FavoritesManager.removeFavorite(fav.weaponName, fav as any)">
                 <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                   <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                 </svg>
               </button>
             </div>
             <div class="text-sm text-gray-600">
               <span class="font-bold text-teal-600">{{ fav.dungeon }}</span>
             </div>
             <div class="text-xs text-gray-500 mt-2">
               {{ fav.strategy }} ({{ fav.fixed_val }})
             </div>
          </div>
        </div>
        <hr class="border-gray-300 mt-6 mb-2" />
      </div>

      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3">
        <WeaponCard 
          v-for="name in filteredWeapons" 
          :key="name" 
          :weapon="dm.getWeaponDetails(name)!"
          @click="emit('select', name)"
        />
      </div>
      <div v-if="filteredWeapons.length === 0" class="text-center text-gray-500 mt-10">
        无匹配武器
      </div>
    </div>
  </div>
</template>
