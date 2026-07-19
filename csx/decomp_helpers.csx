using System;
using System.IO;
using System.Linq;
using UndertaleModLib;
using UndertaleModLib.Models;
using UndertaleModLib.Decompiler;

string outDir = "/Users/mtglitch/deltarune-ch5-ru/fontwork/gml";
string[] keys = { "draw_text_shadow", "set_draw_font", "scr_84", "mojigrid", "draw_shadow" };
var gctx = new GlobalDecompileContext(Data);
var settings = Data.ToolInfo.DecompilerSettings;
foreach (var code in Data.Code)
{
    if (code == null || code.ParentEntry != null) continue;
    string nm = code.Name.Content;
    if (!keys.Any(k => nm.ToLower().Contains(k))) continue;
    try
    {
        string txt = new Underanalyzer.Decompiler.DecompileContext(gctx, code, settings).DecompileToString();
        File.WriteAllText(Path.Combine(outDir, nm + ".gml"), txt);
        Console.WriteLine($"{nm}: {txt.Length}");
    }
    catch (Exception e) { Console.WriteLine($"FAIL {nm}: {e.Message}"); }
}
Console.WriteLine("DONE");
