using System;
using System.Linq;
using UndertaleModLib;
using UndertaleModLib.Models;
using UndertaleModLib.Util;

using (var tw = new TextureWorker())
{
    var f = Data.Fonts.First(x => x.Name.Content == "fnt_main");
    var img = tw.GetTextureFor(f.Texture, "check");
    img.Write("/Users/mtglitch/deltarune-ch5-ru/fontwork/_patched_fnt_main.png");
    int cyr = f.Glyphs.Count(g => g.Character >= 0x0410 && g.Character <= 0x044F);
    Console.WriteLine($"fnt_main в игре: глифов {f.Glyphs.Count}, кириллица {cyr}, текстура {f.Texture.SourceWidth}x{f.Texture.SourceHeight}");
}
Console.WriteLine("CHECK DONE");
