using System.Collections.Generic;
using UnityEngine;

namespace Pcb
{
    /// <summary>
    /// Ordered list of level prefabs. Managed from Tools > PCB > Level Editor.
    /// The first Main Stage Count levels are the main game (the ending plays after the last of them); any levels
    /// after that are Bonus stages, unlocked by finishing the main game.
    /// </summary>
    [CreateAssetMenu(menuName = "PCB/Level List", fileName = "LevelList")]
    public class LevelList : ScriptableObject
    {
        public List<Board> levels = new List<Board>();
        [Tooltip("How many levels make up the main game: the ending plays after the last of them, and the levels after " +
                 "it are Bonus stages (unlocked once the main game is finished). 0 = the whole list is the main game.")]
        [Min(0)] public int mainStageCount;

        public int Count => levels.Count;
        public Board this[int index] => levels[index];

        /// <summary>Number of main-game stages (the whole list when Main Stage Count is 0 or too big).</summary>
        public int MainCount => mainStageCount > 0 ? Mathf.Min(mainStageCount, levels.Count) : levels.Count;
        public bool HasBonus => MainCount < levels.Count;
        public bool IsBonus(int index) => index >= MainCount;
        /// <summary>1 for the first bonus stage.</summary>
        public int BonusNumber(int index) => index - MainCount + 1;

        public int IndexOf(string levelName)
        {
            for (int i = 0; i < levels.Count; i++)
                if (levels[i] && levels[i].levelName == levelName) return i;
            return -1;
        }
    }
}
