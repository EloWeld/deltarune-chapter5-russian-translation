using System;
using System.IO;
using System.Linq;
using System.Text;
using UndertaleModLib;
using UndertaleModLib.Models;
using UndertaleModLib.Util;

string outDir = "/Users/mtglitch/deltarune-ch5-ru/fontwork/ja";
Directory.CreateDirectory(outDir);
string[] fonts = { "fnt_ja_main", "fnt_ja_mainbig", "fnt_ja_small", "fnt_ja_8bit",
                   "fnt_ja_8bit_mixed", "fnt_ja_comicsans", "fnt_ja_dotumche",
                   "fnt_ja_tinynoelle", "fnt_ja_kakugo" };

using (var tw = new TextureWorker())
{
    foreach (var name in fonts)
    {
        var f = Data.Fonts.First(x => x.Name.Content == name);
        var img = tw.GetTextureFor(f.Texture, name);
        img.Write($"{outDir}/{name}.png");

        var sb = new StringBuilder();
        sb.Append("{\"font\":\"").Append(name).Append("\",\"emSize\":").Append((int)f.EmSize)
          .Append(",\"regionW\":").Append(f.Texture.SourceWidth)
          .Append(",\"regionH\":").Append(f.Texture.SourceHeight)
          .Append(",\"glyphs\":[");
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
Console.WriteLine("EXPORT JA DONE");
