using System;
using System.IO;
using System.Linq;
using UndertaleModLib;
using UndertaleModLib.Models;

void DumpAll(UndertaleData d, string label){
    Console.WriteLine($"=== {label}: fonts={d.Fonts.Count} ===");
    foreach(var f in d.Fonts){
        int cyr = f.Glyphs.Count(g => g.Character >= 0x0400 && g.Character <= 0x04FF);
        Console.WriteLine($"  {f.Name?.Content,-22} глифов={f.Glyphs.Count,-5} КИРИЛЛИЦА={cyr,-4} rangeEnd={f.RangeEnd}");
    }
}

DumpAll(Data, "CH5");
UndertaleData ch4;
using(var fs = new FileStream("/Users/mtglitch/Library/Application Support/Steam/steamapps/common/DELTARUNE/DELTARUNE.app/Contents/Resources/chapter4_mac/game.ios", FileMode.Open, FileAccess.Read))
    ch4 = UndertaleIO.Read(fs);
DumpAll(ch4, "CH4");
