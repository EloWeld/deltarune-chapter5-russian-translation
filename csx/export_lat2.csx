using System;
using System.IO;
using System.Linq;
using System.Text;
using UndertaleModLib;
using UndertaleModLib.Models;
using UndertaleModLib.Util;

string outDir = "/Users/mtglitch/deltarune-ch5-ru/fontwork/lat2";
Directory.CreateDirectory(outDir);
string[] fonts = { "fnt_8bit", "fnt_dotumche", "fnt_comicsans", "fnt_tinynoelle" };

using (var tw = new TextureWorker())
{
    foreach (var name in fonts)
    {
        var f = Data.Fonts.First(x => x.Name.Content == name);
        var img = tw.GetTextureFor(f.Texture, name);
        img.Write($"{outDir}/{name}.png");
        var sb = new StringBuilder();
        sb.Append("{\"font\":\"").Append(name).Append("\",\"glyphs\":[");
        bool first = true;
        foreach (var g in f.Glyphs)
        {
            if (!first) sb.Append(",");
            first = false;
            sb.Append("{\"char\":").Append(g.Character)
              .Append(",\"x\":").Append(g.SourceX).Append(",\"y\":").Append(g.SourceY)
              .Append(",\"w\":").Append(g.SourceWidth).Append(",\"h\":").Append(g.SourceHeight)
              .Append(",\"shift\":").Append(g.Shift).Append(",\"offset\":").Append(g.Offset).Append("}");
        }
        sb.Append("]}");
        File.WriteAllText($"{outDir}/{name}.json", sb.ToString());
        Console.WriteLine($"{name}: {f.Texture.SourceWidth}x{f.Texture.SourceHeight}, глифов {f.Glyphs.Count}");
    }
}
Console.WriteLine("EXPORT LAT2 DONE");
