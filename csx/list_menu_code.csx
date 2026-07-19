using System;
using System.Linq;
using UndertaleModLib;
using UndertaleModLib.Models;

string[] keys = { "file", "chapter", "select", "launcher", "initializ", "title" };
foreach (var code in Data.Code)
{
    if (code == null || code.ParentEntry != null) continue;
    string nm = code.Name.Content.ToLower();
    if (keys.Any(k => nm.Contains(k)))
        Console.WriteLine(code.Name.Content);
}
Console.WriteLine("LIST DONE");
