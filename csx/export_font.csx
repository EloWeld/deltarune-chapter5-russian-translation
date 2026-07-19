using System;
using System.IO;
using System.Linq;
using System.Text;
using UndertaleModLib;
using UndertaleModLib.Models;
using UndertaleModLib.Util;

string outDir = "/Users/mtglitch/deltarune-ch5-ru/fontwork";
Directory.CreateDirectory(outDir);

string[] targets = {"fnt_main","fnt_mainbig","fnt_small"};

using (var tw = new TextureWorker())
{
    foreach (var name in targets)
    {
        var f = Data.Fonts.First(x => x.Name.Content == name);
        var t = f.Texture;

        // экспорт региона шрифта в PNG
        var img = tw.GetTextureFor(t, name);
        img.Write($"{outDir}/{name}.png");

        // метрики глифов относительно левого-верхнего угла региона шрифта
        var sb = new StringBuilder();
        sb.Append("{\n");
        sb.Append($"  \"font\": \"{name}\",\n");
        sb.Append($"  \"pageSrcX\": {t.SourceX}, \"pageSrcY\": {t.SourceY}, \"pageW\": {t.SourceWidth}, \"pageH\": {t.SourceHeight},\n");
        sb.Append($"  \"rangeStart\": {f.RangeStart}, \"rangeEnd\": {f.RangeEnd},\n");
        sb.Append("  \"glyphs\": [\n");
        var lines = new System.Collections.Generic.List<string>();
        foreach (var g in f.Glyphs)
        {
            lines.Add($"    {{\"char\": {(int)g.Character}, \"x\": {g.SourceX}, \"y\": {g.SourceY}, \"w\": {g.SourceWidth}, \"h\": {g.SourceHeight}, \"shift\": {g.Shift}, \"offset\": {g.Offset}}}");
        }
        sb.Append(string.Join(",\n", lines));
        sb.Append("\n  ]\n}\n");
        File.WriteAllText($"{outDir}/{name}.json", sb.ToString());

        Console.WriteLine($"{name}: экспортирован PNG {t.SourceWidth}x{t.SourceHeight}, глифов {f.Glyphs.Count}");
    }
}
Console.WriteLine("DONE");
