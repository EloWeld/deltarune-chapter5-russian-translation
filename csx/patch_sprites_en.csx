using System;
using System.Linq;
using System.Text.RegularExpressions;
using UndertaleModLib;
using UndertaleModLib.Models;
using UndertaleModLib.Decompiler;
using UndertaleModLib.Compiler;

// В японском режиме игра подменяет ~40 спрайтов (кнопки боя, таблички, имена)
// и голосовые клипы на японские версии. Возвращаем английские: в карте
// значение всегда становится равным ключу (как в en-ветке).
var gctx = new GlobalDecompileContext(Data);
var code = Data.Code.First(x => x.Name.Content == "gml_GlobalScript_scr_84_init_localization");
string src = new Underanalyzer.Decompiler.DecompileContext(gctx, code, Data.ToolInfo.DecompilerSettings).DecompileToString();

var re = new Regex("ds_map_add\\((sm|sndm), \"([A-Za-z0-9_]+)\", [A-Za-z0-9_]+\\);");
int before = re.Matches(src).Count;
string fixedSrc = re.Replace(src, "ds_map_add($1, \"$2\", $2);");
int changed = 0;
foreach (Match m in re.Matches(src))
    if (!m.Value.Contains($"\"{m.Groups[2].Value}\", {m.Groups[2].Value});")) changed++;

var group = new CodeImportGroup(Data);
group.QueueReplace(code, fixedSrc);
group.Import();
Console.WriteLine($"записей в картах: {before}, японских подмен убрано: {changed}");
Console.WriteLine("PATCH SPRITES DONE");
