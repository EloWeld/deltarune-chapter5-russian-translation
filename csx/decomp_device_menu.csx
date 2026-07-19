using System;
using System.IO;
using System.Linq;
using UndertaleModLib;
using UndertaleModLib.Models;
using UndertaleModLib.Decompiler;

string outDir = "/Users/mtglitch/deltarune-ch5-ru/fontwork/gml";
var gctx = new GlobalDecompileContext(Data);
var settings = Data.ToolInfo.DecompilerSettings;
int n = 0;
foreach (var code in Data.Code)
{
    if (code == null || code.ParentEntry != null) continue;
    string nm = code.Name.Content;
    if (!nm.Contains("DEVICE_MENU")) continue;
    string txt = new Underanalyzer.Decompiler.DecompileContext(gctx, code, settings).DecompileToString();
    File.WriteAllText(Path.Combine(outDir, nm + ".gml"), txt);
    Console.WriteLine($"{nm}: {txt.Length} байт");
    n++;
}
Console.WriteLine($"DONE {n}");
