using System;
using System.Linq;
using UndertaleModLib;
using UndertaleModLib.Models;

var f = Data.Fonts.First(x => x.Name.Content == "fnt_main");
int cyr = f.Glyphs.Count(g => g.Character >= 0x0410 && g.Character <= 0x044F);
var tp = f.Texture.TexturePage;
Console.WriteLine($"fnt_main: глифов={f.Glyphs.Count} кириллица={cyr} rangeEnd={f.RangeEnd}");
Console.WriteLine($"  текстура {tp.TextureData.Image.Width}x{tp.TextureData.Image.Height} формат={tp.TextureData.Image.Format} embIndex={Data.EmbeddedTextures.IndexOf(tp)}");

// проверка TGIN: входит ли новая текстура в какую-либо группу
if (Data.TextureGroupInfo != null && Data.TextureGroupInfo.Count > 0)
{
    int idx = Data.EmbeddedTextures.IndexOf(tp);
    bool inGroup = false;
    string groups = "";
    foreach (var tgin in Data.TextureGroupInfo)
    {
        if (tgin.TexturePages != null && tgin.TexturePages.Any(p => p.Resource == tp))
        { inGroup = true; groups += tgin.Name?.Content + " "; }
    }
    Console.WriteLine($"  TGIN групп всего={Data.TextureGroupInfo.Count}; новая текстура в группе: {inGroup} {groups}");
    // в какой группе была ОРИГИНАЛЬНАЯ текстура шрифта — покажем для сравнения на всякий
}
else Console.WriteLine("  TGIN отсутствует");
Console.WriteLine("VERIFY DONE");
