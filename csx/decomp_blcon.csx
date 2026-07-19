using System;
using System.IO;
using System.Linq;
using UndertaleModLib;
using UndertaleModLib.Models;
using UndertaleModLib.Decompiler;

var gctx = new GlobalDecompileContext(Data);
var code = Data.Code.First(x => x.Name.Content == "gml_Object_obj_battleblcon_Draw_0");
string src = new Underanalyzer.Decompiler.DecompileContext(gctx, code, Data.ToolInfo.DecompilerSettings).DecompileToString();
File.WriteAllText("/Users/mtglitch/deltarune-ch5-ru/fontwork/gml/gml_Object_obj_battleblcon_Draw_0.gml", src);
int i = src.IndexOf("8192");
Console.WriteLine(src.Substring(Math.Max(0, i - 400), Math.Min(700, src.Length - Math.Max(0, i - 400))));
