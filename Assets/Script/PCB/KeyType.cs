using UnityEngine;

namespace Pcb
{
    /// <summary>Pass colours (matching the Key_* / Key_Node_* / Key_Lock_* art). None = carrying nothing.</summary>
    public enum KeyType
    {
        None,
        Green,
        Red,
        Teal
    }

    public static class KeyTypeExtensions
    {
        /// <summary>Colour for placeholder shapes and editor handles.</summary>
        public static Color ToColor(this KeyType pass) => pass switch
        {
            KeyType.Green => new Color(0.25f, 0.85f, 0.35f),
            KeyType.Red => new Color(0.95f, 0.25f, 0.25f),
            KeyType.Teal => new Color(0.15f, 0.8f, 0.8f),
            _ => Color.gray
        };

        /// <summary>Green → Red → Teal → Green (Level Editor > Pass tool).</summary>
        public static KeyType NextPass(this KeyType pass) => pass switch
        {
            KeyType.Green => KeyType.Red,
            KeyType.Red => KeyType.Teal,
            _ => KeyType.Green
        };
    }
}
