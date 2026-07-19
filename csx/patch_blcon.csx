using System;
using System.Linq;
using System.Text.RegularExpressions;
using UndertaleModLib;
using UndertaleModLib.Models;
using UndertaleModLib.Decompiler;
using UndertaleModLib.Compiler;

var gctx = new GlobalDecompileContext(Data);
var code = Data.Code.First(x => x.Name.Content == "gml_Object_obj_battleblcon_Draw_0");
string src = new Underanalyzer.Decompiler.DecompileContext(gctx, code, Data.ToolInfo.DecompilerSettings).DecompileToString();
var re = new Regex(@"else if \(ord\((\w+)\) < 8192 \|\| \(ord\(\1\) >= 65377 && ord\(\1\) <= 65439\)\)\s*\{\s*(\w+) \+= \((\w+) \* 0\.5\);\s*\}");
if (!re.IsMatch(src)) { Console.WriteLine("ПАТТЕРН НЕ НАЙДЕН"); return; }
string repl = "else if (ord($1) < 256 || (ord($1) >= 65377 && ord($1) <= 65439))\n" +
              "{\n    $2 += ($3 * 0.5);\n}\n" +
              "else if (ord($1) < 8192)\n" +
              "{\n    $2 += (($3 * 0.5) + 1);\n}";
var group = new CodeImportGroup(Data);
group.QueueReplace(code, re.Replace(src, repl));
group.Import();
Console.WriteLine("PATCH BLCON DONE");
