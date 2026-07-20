using System;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using UndertaleModLib;
using UndertaleModLib.Models;
using UndertaleModLib.Util;

// Вшивает PNG из sprites/ обратно в игру: <имя>_<кадр>.png -> кадр спрайта.
// Перерисовал PNG -> перезапустил скрипт -> в игре новая графика.
// ВАЖНО: запускать на файле, в который спрайты ещё НЕ вшивались (см. HOWTO).
string dir = "/Users/mtglitch/deltarune-ch5-ru/sprites";
var re = new Regex(@"^(.+)_(\d+)\.png$");
int done = 0, skipped = 0;

foreach (var path in Directory.GetFiles(dir, "*.png").OrderBy(x => x))
{
    var m = re.Match(Path.GetFileName(path));
    if (!m.Success) { skipped++; continue; }
    string name = m.Groups[1].Value;
    int frame = int.Parse(m.Groups[2].Value);

    var s = Data.Sprites.FirstOrDefault(x => x.Name.Content == name);
    if (s == null || frame >= s.Textures.Count || s.Textures[frame]?.Texture == null)
    {
        Console.WriteLine($"ПРОПУСК {Path.GetFileName(path)}: спрайт/кадр не найден");
        skipped++;
        continue;
    }

    var oldItem = s.Textures[frame].Texture;
    var oldTex = oldItem.TexturePage;
    var oldFmt = oldTex.TextureData.Image.Format;

    GMImage img = GMImage.FromPng(File.ReadAllBytes(path));
    if (img.Width != s.Width || img.Height != s.Height)
    {
        Console.WriteLine($"ПРОПУСК {Path.GetFileName(path)}: размер {img.Width}x{img.Height}, у спрайта {s.Width}x{s.Height}");
        skipped++;
        continue;
    }
    if (oldFmt == GMImage.ImageFormat.Bz2Qoi) img = img.ConvertToBz2Qoi();
    else if (oldFmt == GMImage.ImageFormat.Qoi) img = img.ConvertToQoi();

    var tex = new UndertaleEmbeddedTexture();
    tex.Name = Data.Strings.MakeString($"Texture_ru_{name}_{frame}");
    tex.Scaled = oldTex.Scaled;
    tex.GeneratedMips = oldTex.GeneratedMips;
    tex.TextureExternal = false;
    tex.TextureLoaded = true;
    tex.TextureData = new UndertaleEmbeddedTexture.TexData { Image = img };
    tex.TextureWidth = img.Width;
    tex.TextureHeight = img.Height;
    Data.EmbeddedTextures.Add(tex);

    foreach (var tgin in Data.TextureGroupInfo)
        if (tgin.TexturePages.Any(p => p.Resource == oldTex))
            tgin.TexturePages.Add(new UndertaleResourceById<UndertaleEmbeddedTexture, UndertaleChunkTXTR>() { Resource = tex });

    var page = new UndertaleTexturePageItem();
    page.Name = Data.Strings.MakeString($"PageItem_ru_{name}_{frame}");
    page.SourceX = 0; page.SourceY = 0;
    page.SourceWidth = (ushort)img.Width; page.SourceHeight = (ushort)img.Height;
    page.TargetX = 0; page.TargetY = 0;
    page.TargetWidth = (ushort)img.Width; page.TargetHeight = (ushort)img.Height;
    page.BoundingWidth = (ushort)s.Width; page.BoundingHeight = (ushort)s.Height;
    page.TexturePage = tex;
    Data.TexturePageItems.Add(page);

    s.Textures[frame].Texture = page;
    done++;
}
Console.WriteLine($"вшито кадров: {done}, пропущено: {skipped}");
Console.WriteLine("IMPORT SPRITES DONE");
