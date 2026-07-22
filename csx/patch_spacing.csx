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

// 1) новые Shift для кириллицы (зазор как у латиницы)
foreach (var fontName in fonts)
{
    var f = Data.Fonts.FirstOrDefault(x => x.Name.Content == fontName);
    if (f == null) { Console.WriteLine($"{fontName}: НЕТ в игре, пропуск"); continue; }
    if (!File.Exists($"{workDir}/{fontName}_shift.json")) { Console.WriteLine($"{fontName}: нет shift.json, пропуск"); continue; }
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
    Console.WriteLine($"{fontName}: shift обновлён у {changed} глифов");
}

// 2) патч кода: кириллица должна получать половинный шаг, как латиница
string[] targets = { "gml_Object_obj_writer_Draw_0", "gml_Object_obj_battleblcon_Draw_0",
                     "gml_Object_obj_dw_cliff_verticalwind_post_Step_0", "gml_Object_obj_aqua_enemy_Step_0" };
var gctx = new GlobalDecompileContext(Data);
var settings = Data.ToolInfo.DecompilerSettings;
var group = new CodeImportGroup(Data);
var re = new Regex(@"ord\((\w+)\) < 256 \|\| \(ord\(\1\) >= 65377");
int patched = 0;
foreach (var name in targets)
{
    var code = Data.Code.FirstOrDefault(x => x.Name.Content == name);
    if (code == null) { Console.WriteLine($"{name}: код отсутствует, пропуск"); continue; }
    string src = new Underanalyzer.Decompiler.DecompileContext(gctx, code, settings).DecompileToString();
    if (!re.IsMatch(src))
    {
        Console.WriteLine($"{name}: паттерн НЕ найден, пропуск");
        continue;
    }
    string fixedSrc = re.Replace(src, "ord($1) < 8192 || (ord($1) >= 65377");
    group.QueueReplace(code, fixedSrc);
    patched++;
    Console.WriteLine($"{name}: заменено вхождений {re.Matches(src).Count}");
}
group.Import();
Console.WriteLine($"PATCH SPACING DONE (код: {patched})");
