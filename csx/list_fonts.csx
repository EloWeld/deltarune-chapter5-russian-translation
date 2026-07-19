using System;
using System.IO;
using System.Linq;
using System.Text;
using UndertaleModLib;
using UndertaleModLib.Models;

var sb = new StringBuilder();
foreach (var f in Data.Fonts)
{
    int ascii = f.Glyphs.Count(g => g.Character >= 0x20 && g.Character < 0x7F);
    int cyr   = f.Glyphs.Count(g => g.Character >= 0x400 && g.Character <= 0x4FF);
    int cjk   = f.Glyphs.Count(g => g.Character >= 0x3000);
    var tp = f.Texture;
    string tex = tp == null ? "нет" : $"{tp.SourceWidth}x{tp.SourceHeight}@({tp.SourceX},{tp.SourceY}) page={tp.TexturePage?.Name?.Content}";
    sb.AppendLine($"{f.Name.Content}\tsize={f.EmSize}\trange={f.RangeStart}-{f.RangeEnd}\tglyphs={f.Glyphs.Count} (ascii={ascii} cyr={cyr} cjk={cjk})\ttex={tex}");
}
File.WriteAllText("/Users/mtglitch/deltarune-ch5-ru/fontwork/_fonts_list.txt", sb.ToString());
Console.WriteLine($"fonts: {Data.Fonts.Count} -> _fonts_list.txt");
