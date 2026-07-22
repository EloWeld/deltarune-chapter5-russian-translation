using System;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Text.RegularExpressions;
using UndertaleModLib;
using UndertaleModLib.Models;
using UndertaleModLib.Util;
using UndertaleModLib.Decompiler;
using UndertaleModLib.Compiler;

// 1) кириллица в 4 оставшихся латинских шрифта
string workDir = "/Users/mtglitch/deltarune-ch5-ru/fontwork/lat2";
string[] fonts = { "fnt_8bit", "fnt_dotumche", "fnt_comicsans", "fnt_tinynoelle" };
foreach (var fontName in fonts)
{
    var f = Data.Fonts.FirstOrDefault(x => x.Name.Content == fontName);
    if (f == null) { Console.WriteLine($"{fontName}: НЕТ в игре, пропуск"); continue; }
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

    int grp = 0;
    foreach (var tgin in Data.TextureGroupInfo)
        if (tgin.TexturePages.Any(p => p.Resource == oldTex))
        {
            tgin.TexturePages.Add(new UndertaleResourceById<UndertaleEmbeddedTexture, UndertaleChunkTXTR>() { Resource = tex });
            grp++;
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
    Console.WriteLine($"{fontName}: {img.Width}x{img.Height}, глифов {n}, TGIN {grp}");
}

// 2) диалоги: кириллице шаг hspace/2 + 2 (было +1)
var gctx = new GlobalDecompileContext(Data);
var settings = Data.ToolInfo.DecompilerSettings;
var group = new CodeImportGroup(Data);

var wcode = Data.Code.FirstOrDefault(x => x.Name.Content == "gml_Object_obj_writer_Draw_0");
if (wcode == null) { Console.WriteLine("obj_writer: код отсутствует, пропуск"); }
else {
    string wsrc = new Underanalyzer.Decompiler.DecompileContext(gctx, wcode, settings).DecompileToString();
    var reW = new Regex(@"(else if \(ord\((\w+)\) < 8192\)\s*\{\s*\w+ -= \(\(\w+ / 2\) - )1(\);\s*\})");
    if (!reW.IsMatch(wsrc)) { Console.WriteLine("obj_writer: ПАТТЕРН НЕ НАЙДЕН"); }
    else { group.QueueReplace(wcode, reW.Replace(wsrc, "${1}2$3")); Console.WriteLine("obj_writer: -1 -> -2 ок"); }
}

// 3) battleblcon: замер ширины +1 -> +2
var bcode = Data.Code.FirstOrDefault(x => x.Name.Content == "gml_Object_obj_battleblcon_Draw_0");
if (bcode == null) { Console.WriteLine("battleblcon: код отсутствует, пропуск"); }
else {
    string bsrc = new Underanalyzer.Decompiler.DecompileContext(gctx, bcode, settings).DecompileToString();
    var reB = new Regex(@"(else if \(ord\((\w+)\) < 8192\)\s*\{\s*\w+ \+= \(\(\w+ \* 0\.5\) \+ )1(\);\s*\})");
    if (!reB.IsMatch(bsrc)) { Console.WriteLine("battleblcon: ПАТТЕРН НЕ НАЙДЕН"); }
    else { group.QueueReplace(bcode, reB.Replace(bsrc, "${1}2$3")); Console.WriteLine("battleblcon: +1 -> +2 ок"); }
}

group.Import();
Console.WriteLine("ROUND3 DONE");
