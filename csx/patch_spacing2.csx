using System;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Text.RegularExpressions;
using UndertaleModLib;
using UndertaleModLib.Models;
using UndertaleModLib.Decompiler;
using UndertaleModLib.Compiler;

string workDir = "/Users/mtglitch/deltarune-ch5-ru/fontwork/ja";
string[] fonts = { "fnt_ja_main", "fnt_ja_mainbig", "fnt_ja_small", "fnt_ja_8bit",
                   "fnt_ja_8bit_mixed", "fnt_ja_comicsans", "fnt_ja_dotumche",
                   "fnt_ja_tinynoelle", "fnt_ja_kakugo" };

// 1) Shift кириллицы = чернила + латинский зазор + 1
foreach (var fontName in fonts)
{
    var f = Data.Fonts.First(x => x.Name.Content == fontName);
    var doc = JsonDocument.Parse(File.ReadAllText($"{workDir}/{fontName}_shift.json"));
    int changed = 0;
    foreach (var g in f.Glyphs)
    {
        if (doc.RootElement.TryGetProperty(g.Character.ToString(), out var s))
        {
            g.Shift = (short)s.GetInt32();
            changed++;
        }
    }
    Console.WriteLine($"{fontName}: shift обновлён у {changed}");
}

// 2) врайтеры: кириллице шаг hspace/2 + 1 (латинице/катакане — как было hspace/2)
string[] targets = { "gml_Object_obj_writer_Draw_0", "gml_Object_obj_battleblcon_Draw_0" };
var gctx = new GlobalDecompileContext(Data);
var settings = Data.ToolInfo.DecompilerSettings;
var group = new CodeImportGroup(Data);
var re = new Regex(@"if \(ord\((\w+)\) < 8192 \|\| \(ord\(\1\) >= 65377 && ord\(\1\) <= 65439\)\)\s*\{\s*(\w+) -= \((\w+) / 2\);\s*\}");
foreach (var name in targets)
{
    var code = Data.Code.First(x => x.Name.Content == name);
    string src = new Underanalyzer.Decompiler.DecompileContext(gctx, code, settings).DecompileToString();
    var m = re.Match(src);
    if (!m.Success)
    {
        Console.WriteLine($"{name}: паттерн НЕ найден!");
        continue;
    }
    string repl = "if (ord($1) < 256 || (ord($1) >= 65377 && ord($1) <= 65439))\n" +
                  "{\n    $2 -= ($3 / 2);\n}\n" +
                  "else if (ord($1) < 8192)\n" +
                  "{\n    $2 -= (($3 / 2) - 1);\n}";
    group.QueueReplace(code, re.Replace(src, repl));
    Console.WriteLine($"{name}: патч ок (переменные {m.Groups[1].Value}/{m.Groups[2].Value}/{m.Groups[3].Value})");
}
group.Import();
Console.WriteLine("PATCH SPACING2 DONE");
