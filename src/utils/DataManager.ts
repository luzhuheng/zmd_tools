import Papa from 'papaparse';
// @ts-ignore
import weaponCsvContent from '../assets/数据/武器词条.CSV?raw';
// @ts-ignore
import dungeonCsvContent from '../assets/数据/副本.CSV?raw';

// 定义类型
export interface Weapon {
  name: string;
  rarity: string;
  type: string;
  main_stat: string;
  sub_stat: string;
  skill: string;
}

export interface Dungeon {
  name: string;
  main_stats: string[];
  sub_stats: string[];
  skills: string[];
}

export interface FarmingPlan {
  dungeon: string;
  strategy: string; // "主词条", "副词条", 或 "技能"
  fixed_val: string; // 目标特定值
  selected_mains: string[]; // 该副本的主词条列表（用于显示）
  by_products: Record<string, string[]>; // 键: "主|副|技", 值: 武器名称列表
  score: number;
  error?: string;
}

export class DataManager {
  weapons: Map<string, Weapon> = new Map();
  dungeons: Dungeon[] = [];
  isLoaded = false;

  constructor() {}

  async loadData() {
    if (this.isLoaded) return;

    try {
      // 加载武器数据
      this.parseWeapons(weaponCsvContent);

      // 加载副本数据
      this.parseDungeons(dungeonCsvContent);

      this.isLoaded = true;
    } catch (e) {
      console.error("Failed to load data:", e);
      throw e;
    }
  }

  private parseWeapons(csvText: string) {
    const results = Papa.parse(csvText, {
      header: true,
      skipEmptyLines: true,
    });

    for (const row of results.data as any[]) {
      // CSV 表头: 主词条,副词条,技能,稀有度,种类,名称
      if (row['名称']) {
        this.weapons.set(row['名称'], {
          name: row['名称'],
          rarity: row['稀有度'],
          type: row['种类'],
          main_stat: row['主词条'],
          sub_stat: row['副词条'],
          skill: row['技能'],
        });
      }
    }
  }

  private parseDungeons(csvText: string) {
    const results = Papa.parse(csvText, {
      header: false,
      skipEmptyLines: false, // 我们需要手动处理结构
    });

    const data = results.data as string[][];
    const rows = data.length;

    // 遍历行以查找表头
    for (let r = 0; r < rows; r++) {
      const row = data[r];
      if (!row) continue;

      for (let c = 0; c < row.length; c++) {
        if (row[c] === '主词条') {
          // 发现一个数据块。
          // 副本名称位于上一行的同一列（或附近）
          // 实际上，基于 CSV：
          // 第一行：名称, 列2, 列3, 列4, 名称2...
          // 第二行：主词条, 副词条, 技能, 空, 主词条, 副词条, 技能...
          // 所以如果 row[c] == '主词条', 名称位于 data[r-1][c]
          
          if (r === 0) continue; // 基于文件结构不应该发生
          const prevRow = data[r-1];
          if (!prevRow) continue;

          const dungeonName = prevRow[c];
          if (!dungeonName) continue;

          const mainStats: string[] = [];
          const subStats: string[] = [];
          const skills: string[] = [];

          // 读取下方的数据行
          let currentR = r + 1;
          while (currentR < rows) {
            const dRow = data[currentR];
            if (!dRow) {
                currentR++;
                continue;
            }
            // 如果遇到空行或新块的开始则停止（虽然新块通常之前有表头）
            // 文件在块之间有空行。
            // 此外，如果该列的项目较少，单元格可能为空。
            // 但如果所有 3 列都为空，我们停止。
            
            const cellM = dRow[c];
            const cellS = dRow[c+1];
            const cellK = dRow[c+2];

            const m = cellM ? cellM.trim() : '';
            const s = cellS ? cellS.trim() : '';
            const k = cellK ? cellK.trim() : '';

            if (!m && !s && !k) {
              // 检查是真正的块结束还是仅仅是间隔？
              // 假设数据块是连续的。
              // 但我们应该检查是否遇到了新的标题行？
              // 如果 dRow 包含 "主词条"，我们走得太远了（但我们在外层循环中扫描 "主词条"，所以我们应该跳过已处理的行？不，外层循环会处理下一个块）。
              // 我们只需要停止读取 *当前* 副本。
              // 如果下一行是标题行，我们停止。
              if (dRow.some(cell => cell === '主词条')) break; 
              
              // 如果仅仅是空行分隔符
              break;
            }
            
            if (m) mainStats.push(m);
            if (s) subStats.push(s);
            if (k) skills.push(k);

            currentR++;
          }

          this.dungeons.push({
            name: dungeonName,
            main_stats: mainStats,
            sub_stats: subStats,
            skills: skills
          });
          
          // 优化：在外层循环中跳过本行的 c, c+1, c+2 列？
          // 外层循环将 c 增加 1。我们可以让它继续，它不会在 c+1/c+2 匹配 "主词条"。
        }
      }
    }
  }

  getWeaponNames(): string[] {
    return Array.from(this.weapons.keys());
  }

  getWeaponDetails(name: string): Weapon | undefined {
    return this.weapons.get(name);
  }

  getFarmingPlans(weaponName: string): FarmingPlan[] {
    const weapon = this.weapons.get(weaponName);
    if (!weapon) return [];

    const allPlans: FarmingPlan[] = [];

    // 策略：目标副词条，目标技能（主词条不能单独作为目标）
    const strategies = [
      { type: "副词条", val: weapon.sub_stat },
      { type: "技能", val: weapon.skill }
    ];

    for (const dungeon of this.dungeons) {
      // 检查副本是否包含目标主词条
      if (!dungeon.main_stats.includes(weapon.main_stat)) continue;

      for (const strat of strategies) {
        // 检查副本是否支持该策略（包含特定值）
        // 并检查副本是否包含其他所需的随机部分
        if (strat.type === "副词条") {
            if (!dungeon.sub_stats.includes(strat.val)) continue;
            if (!dungeon.skills.includes(weapon.skill)) continue;
        } else { // 技能
            if (!dungeon.skills.includes(strat.val)) continue;
            if (!dungeon.sub_stats.includes(weapon.sub_stat)) continue;
        }

        // 优化：选择最好的 3 个主词条
        // 我们必须包含 weapon.main_stat。
        // 我们需要从 dungeon.main_stats 中挑选另外 2 个（排除 weapon.main_stat）。
        const otherMains = dungeon.main_stats.filter(m => m !== weapon.main_stat);
        
        // 从 otherMains 中生成 2 个的组合
        const combinations: string[][] = [];
        if (otherMains.length < 2) {
            // 如果少于 2 个其他词条，则全部选取（总数 < 3）
            combinations.push(otherMains); 
        } else {
            for (let i = 0; i < otherMains.length; i++) {
                for (let j = i + 1; j < otherMains.length; j++) {
                    const m1 = otherMains[i];
                    const m2 = otherMains[j];
                    if (m1 && m2) {
                        combinations.push([m1, m2]);
                    }
                }
            }
        }

        // 评估每个组合
        for (const combo of combinations) {
            const currentMains = [weapon.main_stat, ...combo];
            
            // 计算此配置的分数
            const byProducts: Record<string, string[]> = {};
            let score = 0;

            const s_list = (strat.type === "副词条") ? [strat.val] : dungeon.sub_stats;
            const k_list = (strat.type === "技能") ? [strat.val] : dungeon.skills;

            for (const m of currentMains) {
                for (const s of s_list) {
                    for (const k of k_list) {
                        // 检查匹配
                         const matchedWeapons: string[] = [];
                         for (const [wName, w] of this.weapons.entries()) {
                            if (wName === weaponName) continue; 
                            if (w.main_stat === m && w.sub_stat === s && w.skill === k) {
                                matchedWeapons.push(wName);
                            }
                         }

                         if (matchedWeapons.length > 0) {
                            const key = `${m} | ${s} | ${k}`;
                            byProducts[key] = matchedWeapons;
                            score += matchedWeapons.length;
                         }
                    }
                }
            }
            
            if (score > 0) {
                 allPlans.push({
                     dungeon: dungeon.name,
                     strategy: strat.type,
                     fixed_val: strat.val,
                     selected_mains: currentMains,
                     by_products: byProducts,
                     score: score
                 });
            }
        }
      }
    }

    // 按分数降序排列方案
    allPlans.sort((a, b) => b.score - a.score);

    // 过滤掉次优方案
    const finalPlans: FarmingPlan[] = [];
    
    // 辅助函数：从副产物中获取所有武器名称
    const getWeaponSet = (plan: FarmingPlan) => {
        const set = new Set<string>();
        for (const list of Object.values(plan.by_products)) {
            list.forEach(w => set.add(w));
        }
        return set;
    };

    // 辅助函数：检查集合 A 是否是集合 B 的子集
    const isSubset = (setA: Set<string>, setB: Set<string>) => {
        for (const elem of setA) {
            if (!setB.has(elem)) return false;
        }
        return true;
    };

    for (let i = 0; i < allPlans.length; i++) {
        const currentPlan = allPlans[i];
        if (!currentPlan) continue;
        const currentSet = getWeaponSet(currentPlan);
        let isSuboptimal = false;

        for (let j = 0; j < allPlans.length; j++) {
            if (i === j) continue;
            const otherPlan = allPlans[j];
            if (!otherPlan) continue;
            const otherSet = getWeaponSet(otherPlan);

            // 如果当前方案的产物是其他方案产物的子集
            if (isSubset(currentSet, otherSet)) {
                // 如果是严格更小的子集（或者相同的集合但分数较低？），移除当前
                if (otherSet.size > currentSet.size) {
                    isSuboptimal = true;
                    break;
                }
                // 如果集合相等
                if (otherSet.size === currentSet.size) {
                    // 如果分数也相等（如果集合相等，分数应该也相等）
                    // 我们需要一个决胜局来避免同时移除两者或同时保留两者（如果我们想去重）
                    // 如果它们来自同一个副本，我们绝对应该移除一个（重复项）
                    // 如果它们来自不同的副本，也许保留两者？
                    
                    if (currentPlan.dungeon === otherPlan.dungeon) {
                         // 它们来自同一个副本，但也许是不同的策略？
                         // 例如，一个目标副词条，一个目标技能。
                         // 由于输出完全相同，对于该副本显示两者是多余的。
                         // 移除索引较低的一个（保留后来的？还是保留较早的？）
                         // 让我们保留索引较小的一个（最先遇到的）
                         if (j < i) {
                             isSuboptimal = true;
                             break;
                         }
                    } else {
                        // 不同的副本。保留两者。
                        // 除非用户真的想移除所有冗余。
                        // 用户说：“这两把武器已经包含在……这个方案中了”
                        // 这意味着冗余是不好的。
                        // 但是不同的副本有不同的可刷性。
                        // 让我们坚持：如果是严格子集则移除。
                        // 如果集合相等：如果是同一个副本则移除。
                    }
                }
            }
        }

        if (!isSuboptimal) {
            finalPlans.push(currentPlan);
        }
    }

    return finalPlans;
  }
}
