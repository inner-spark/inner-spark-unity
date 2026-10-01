namespace Pcb
{
    public enum PcbLayer { Front = 0, Back = 1 }

    public enum NodeType
    {
        Capacitor, // stop point
        Via,       // stop point that exists on both sides; the spark can flip side here
        Start,     // where the spark spawns
        Goal,      // chip that ends the level
        Switch,    // toggle switch: each press flips every normal gate it's linked to
        AndSwitch, // toggle switch for AND gates: a gate opens only while all its AND switches are on
        PassHolder,// endless source of one pass colour: Space takes the pass (KeyNodeMechanic)
        PassLock   // can only be moved onto while carrying the matching pass (KeyLockMechanic)
    }

    /// <summary>Purely cosmetic PCB set-dressing. Never a stop point, never part of the movement graph.</summary>
    public enum DecorType
    {
        Resistor,
        IC,
        Diode,
        Transistor,
        ScrewHole,
        JumperWire,
        SilkscreenLabel,
        CopperPour
    }

    public static class PcbLayerExtensions
    {
        public static PcbLayer Other(this PcbLayer layer) =>
            layer == PcbLayer.Front ? PcbLayer.Back : PcbLayer.Front;
    }
}
