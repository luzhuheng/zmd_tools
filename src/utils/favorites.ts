import type { FarmingPlan } from './DataManager';
import { ref } from 'vue';

const COOKIE_NAME = 'zmd_farming_favorites';

export interface FavoritePlan {
  weaponName: string;
  dungeon: string;
  strategy: string;
  fixed_val: string;
  timestamp: number;
}

// Helper to set cookie
function setCookie(name: string, value: string, days: number) {
  let expires = "";
  if (days) {
    const date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    expires = "; expires=" + date.toUTCString();
  }
  document.cookie = name + "=" + (encodeURIComponent(value) || "") + expires + "; path=/";
}

// Helper to get cookie
function getCookie(name: string): string | null {
  const nameEQ = name + "=";
  const ca = document.cookie.split(';');
  for (let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) === ' ') c = c.substring(1, c.length);
    if (c.indexOf(nameEQ) === 0) return decodeURIComponent(c.substring(nameEQ.length, c.length));
  }
  return null;
}

// Internal load function
function loadFavorites(): FavoritePlan[] {
  const cookieVal = getCookie(COOKIE_NAME);
  if (!cookieVal) return [];
  try {
    return JSON.parse(cookieVal);
  } catch (e) {
    console.error('Failed to parse favorites cookie', e);
    return [];
  }
}

// Reactive state
const favorites = ref<FavoritePlan[]>(loadFavorites());

export const FavoritesManager = {
  getFavorites() {
    return favorites.value;
  },
  
  // Expose the reactive ref directly for components to use
  favorites,

  saveFavorites(newFavorites: FavoritePlan[]) {
    // Store for 365 days
    setCookie(COOKIE_NAME, JSON.stringify(newFavorites), 365);
    favorites.value = newFavorites;
  },

  addFavorite(weaponName: string, plan: FarmingPlan) {
    const current = favorites.value;
    const newFav: FavoritePlan = {
      weaponName,
      dungeon: plan.dungeon,
      strategy: plan.strategy,
      fixed_val: plan.fixed_val,
      timestamp: Date.now()
    };

    // Check if already exists
    const exists = current.some(f => 
      f.weaponName === newFav.weaponName &&
      f.dungeon === newFav.dungeon &&
      f.strategy === newFav.strategy &&
      f.fixed_val === newFav.fixed_val
    );

    if (!exists) {
      const updated = [newFav, ...current];
      this.saveFavorites(updated);
    }
  },

  removeFavorite(weaponName: string, plan: FarmingPlan) {
    const updated = favorites.value.filter(f => 
      !(f.weaponName === weaponName &&
        f.dungeon === plan.dungeon &&
        f.strategy === plan.strategy &&
        f.fixed_val === plan.fixed_val)
    );
    this.saveFavorites(updated);
  },

  isFavorite(weaponName: string, plan: FarmingPlan): boolean {
    return favorites.value.some(f => 
      f.weaponName === weaponName &&
      f.dungeon === plan.dungeon &&
      f.strategy === plan.strategy &&
      f.fixed_val === plan.fixed_val
    );
  }
};
