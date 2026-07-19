using System;
using System.IO;
using System.Linq;
using System.Text.Json;
using UndertaleModLib;
using UndertaleModLib.Models;
using UndertaleModLib.Util;

string workDir = "/Users/mtglitch/deltarune-ch5-ru/fontwork";
string[] fonts = { "fnt_main", "fnt_mainbig", "fnt_small" };

foreach (var fontName in fonts)
{
    var f = Data.Fonts.First(x => x.Name.Content == fontName);
    var oldTex = f.Texture.TexturePage;
    var oldFmt = oldTex.TextureData.Image.Format;

    // новый атлас -> GMImage, конверт под формат игры
    byte[] png = File.ReadAllBytes($"{workDir}/{fontName}_new.png");
    GMImage img = GMImage.FromPng(png);
    if (oldFmt == GMImage.ImageFormat.Bz2Qoi) img = img.ConvertToBz2Qoi();
    else if (oldFmt == GMImage.ImageFormat.Qoi) img = img.ConvertToQoi();

    // встроенная текстура
    var tex = new UndertaleEmbeddedTexture();
    tex.Name = Data.Strings.MakeString($"Texture_ru_{fontName}");
    tex.Scaled = oldTex.Scaled;
    tex.GeneratedMips = oldTex.GeneratedMips;
    tex.TextureExternal = false;
    tex.TextureLoaded = true;
    tex.TextureData = new UndertaleEmbeddedTexture.TexData { Image = img };
    tex.TextureWidth = img.Width;
    tex.TextureHeight = img.Height;
    Data.EmbeddedTextures.Add(tex);

    // включаем новую текстуру в те же TGIN-группы, что и оригинальную (иначе движок не подхватит)
    int addedToGroups = 0;
    foreach (var tgin in Data.TextureGroupInfo)
    {
        if (tgin.TexturePages.Any(p => p.Resource == oldTex))
        {
            tgin.TexturePages.Add(new UndertaleResourceById<UndertaleEmbeddedTexture, UndertaleChunkTXTR>() { Resource = tex });
            addedToGroups++;
        }
    }
    Console.WriteLine($"  {fontName}: добавлено в TGIN-групп: {addedToGroups}");

    // texture page item на всю текстуру
    var page = new UndertaleTexturePageItem();
    page.Name = Data.Strings.MakeString($"PageItem_ru_{fontName}");
    page.SourceX = 0; page.SourceY = 0;
    page.SourceWidth = (ushort)img.Width; page.SourceHeight = (ushort)img.Height;
    page.TargetX = 0; page.TargetY = 0;
    page.TargetWidth = (ushort)img.Width; page.TargetHeight = (ushort)img.Height;
    page.BoundingWidth = (ushort)img.Width; page.BoundingHeight = (ushort)img.Height;
    page.TexturePage = tex;
    Data.TexturePageItems.Add(page);

    f.Texture = page;

    // глифы из JSON (латиница без изменений + кириллица)
    var doc = JsonDocument.Parse(File.ReadAllText($"{workDir}/{fontName}_glyphs.json"));
    f.Glyphs.Clear();
    int n = 0;
    foreach (var g in doc.RootElement.GetProperty("glyphs").EnumerateArray())
    {
        f.Glyphs.Add(new UndertaleFont.Glyph
        {
            Character = (ushort)g.GetProperty("char").GetInt32(),
            SourceX = (ushort)g.GetProperty("x").GetInt32(),
            SourceY = (ushort)g.GetProperty("y").GetInt32(),
            SourceWidth = (ushort)g.GetProperty("w").GetInt32(),
            SourceHeight = (ushort)g.GetProperty("h").GetInt32(),
            Shift = (short)g.GetProperty("shift").GetInt32(),
            Offset = (short)g.GetProperty("offset").GetInt32(),
        });
        n++;
    }
    if (f.RangeEnd < 0x451) f.RangeEnd = 0x451;

    Console.WriteLine($"{fontName}: текстура {img.Width}x{img.Height} формат {img.Format}, глифов {n}");
}
Console.WriteLine("INJECT DONE");
