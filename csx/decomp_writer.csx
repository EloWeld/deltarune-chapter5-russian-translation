using System;
using System.IO;
using System.Linq;
using UndertaleModLib;
using UndertaleModLib.Models;
using UndertaleModLib.Decompiler;

string outDir = "/Users/mtglitch/deltarune-ch5-ru/fontwork/gml";
Directory.CreateDirectory(outDir);
string[] keys = { "writer", "textsetup", "text_setup", "fileselect", "filemenu", "spacing", "darkcontroller" };

var gctx = new GlobalDecompileContext(Data);
var settings = Data.ToolInfo.DecompilerSettings;
int n = 0;
foreach (var code in Data.Code)
{
    if (code == null || code.Name == null) continue;
    string nm = code.Name.Content.ToLower();
    if (!keys.Any(k => nm.Contains(k))) continue;
    if (code.ParentEntry != null) continue;
    try
    {
        string txt = new Underanalyzer.Decompiler.DecompileContext(gctx, code, settings).DecompileToString();
        File.WriteAllText(Path.Combine(outDir, code.Name.Content + ".gml"), txt);
        n++;
    }
    catch (Exception e)
    {
        Console.WriteLine($"FAIL {code.Name.Content}: {e.Message}");
    }
}
Console.WriteLine($"декомпилировано: {n}");
