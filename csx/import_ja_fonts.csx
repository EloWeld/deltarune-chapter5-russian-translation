using System;
using System.IO;
using System.Linq;
using System.Text.Json;
using UndertaleModLib;
using UndertaleModLib.Models;
using UndertaleModLib.Util;

string workDir = "/Users/mtglitch/deltarune-ch5-ru/fontwork/ja";
string[] fonts = { "fnt_ja_main", "fnt_ja_mainbig", "fnt_ja_small", "fnt_ja_8bit",
                   "fnt_ja_8bit_mixed", "fnt_ja_comicsans", "fnt_ja_dotumche",
                   "fnt_ja_tinynoelle", "fnt_ja_kakugo" };

foreach (var fontName in fonts)
{
    var f = Data.Fonts.First(x => x.Name.Content == fontName);
    var oldTex = f.Texture.TexturePage;
    var oldFmt = oldTex.TextureData.Image.Format;

    byte[] png = File.ReadAllBytes($"{workDir}/{fontName}_new.png");
    GMImage img = GMImage.FromPng(png);
    if (oldFmt == GMImage.ImageFormat.Bz2Qoi) img = img.ConvertToBz2Qoi();
    else if (oldFmt == GMImage.ImageFormat.Qoi) img = img.ConvertToQoi();

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

    int addedToGroups = 0;
    foreach (var tgin in Data.TextureGroupInfo)
    {
        if (tgin.TexturePages.Any(p => p.Resource == oldTex))
        {
            tgin.TexturePages.Add(new UndertaleResourceById<UndertaleEmbeddedTexture, UndertaleChunkTXTR>() { Resource = tex });
            addedToGroups++;
        }
    }

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

    var doc = JsonDocument.Parse(File.ReadAllText($"{workDir}/{fontName}_glyphs.json"));
    f.Glyphs.Clear();
    int n = 0, cyr = 0;
    foreach (var g in doc.RootElement.GetProperty("glyphs").EnumerateArray())
    {
        int ch = g.GetProperty("char").GetInt32();
        f.Glyphs.Add(new UndertaleFont.Glyph
        {
            Character = (ushort)ch,
            SourceX = (ushort)g.GetProperty("x").GetInt32(),
            SourceY = (ushort)g.GetProperty("y").GetInt32(),
            SourceWidth = (ushort)g.GetProperty("w").GetInt32(),
            SourceHeight = (ushort)g.GetProperty("h").GetInt32(),
            Shift = (short)g.GetProperty("shift").GetInt32(),
            Offset = (short)g.GetProperty("offset").GetInt32(),
        });
        n++;
        if (ch >= 0x400 && ch <= 0x4FF) cyr++;
    }
    Console.WriteLine($"{fontName}: {img.Width}x{img.Height} {img.Format}, глифов {n} (кир. {cyr}), TGIN-групп {addedToGroups}");
}
Console.WriteLine("INJECT JA DONE");
