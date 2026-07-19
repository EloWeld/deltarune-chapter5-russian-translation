using System;
using System.Linq;
using UndertaleModLib;
using UndertaleModLib.Models;

foreach (var f in Data.Fonts.Where(x => x.Name.Content.StartsWith("fnt_ja")))
{
    int cyr = f.Glyphs.Count(g => g.Character >= 0x400 && g.Character <= 0x4FF);
    int cjk = f.Glyphs.Count(g => g.Character >= 0x3000);
    bool sorted = true;
    for (int i = 1; i < f.Glyphs.Count; i++)
        if (f.Glyphs[i].Character < f.Glyphs[i-1].Character) { sorted = false; break; }
    Console.WriteLine($"{f.Name.Content}: глифов {f.Glyphs.Count}, кир {cyr}, cjk {cjk}, сортировка {(sorted?"ok":"НАРУШЕНА")}, текстура {f.Texture.SourceWidth}x{f.Texture.SourceHeight} page={f.Texture.TexturePage.Name?.Content}");
}
Console.WriteLine("VERIFY DONE");
