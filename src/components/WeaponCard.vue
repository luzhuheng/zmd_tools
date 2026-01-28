<script setup lang="ts">
import { computed } from 'vue';
import type { Weapon } from '../utils/DataManager';

const props = defineProps<{
  weapon: Weapon;
}>();

const emit = defineEmits<{
  (e: 'click', name: string): void;
}>();

const rarityDisplay = computed(() => {
  const r = props.weapon.rarity.replace('星', '');
  return `${r}★${props.weapon.name}`;
});
</script>

<template>
  <div 
    class="bg-white border border-gray-200 rounded-lg p-4 cursor-pointer hover:bg-gray-50 hover:shadow-md transition-all flex items-center justify-center h-24"
    @click="emit('click', weapon.name)"
  >
    <div class="text-center font-bold text-gray-800 line-clamp-2">
      {{ rarityDisplay }}
    </div>
  </div>
</template>
