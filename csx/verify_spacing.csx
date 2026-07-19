using System;
using System.Linq;
using UndertaleModLib;
using UndertaleModLib.Models;
using UndertaleModLib.Decompiler;

var f = Data.Fonts.First(x => x.Name.Content == "fnt_ja_main");
var gН = f.Glyphs.First(g => g.Character == 0x41D);
var gH = f.Glyphs.First(g => g.Character == 'H');
Console.WriteLine($"fnt_ja_main: shift H={gH.Shift}, Н={gН.Shift}");

var gctx = new GlobalDecompileContext(Data);
var code = Data.Code.First(x => x.Name.Content == "gml_Object_obj_writer_Draw_0");
string src = new Underanalyzer.Decompiler.DecompileContext(gctx, code, Data.ToolInfo.DecompilerSettings).DecompileToString();
Console.WriteLine(src.Contains("< 8192") ? "код: порог 8192 на месте" : "код: ПАТЧ НЕ НАЙДЕН");
Console.WriteLine("VERIFY DONE");
